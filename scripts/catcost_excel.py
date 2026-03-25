"""Helpers for reading CatCost workbook data without openpyxl.

The CatCost workbook bundled for local development has invalid stylesheet XML,
so ``openpyxl`` cannot load it reliably. These helpers read the workbook
directly from the XLSX zip structure and expose small extraction utilities for
the data that CatPrice consumes.
"""

from __future__ import annotations

import json
import re
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
SHEETS_DIR = "xl/"

WORKBOOK_PATH = Path(__file__).resolve().parent.parent / "CatCost_v1-1-1" / "CatCost_v1-1-1.xlsx"
DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data"
PROCESS_TEMPLATES_DIR = DATA_DIR / "process_templates"

TEXT_OVERRIDES = {
    "Phosphoric acid, comÃªl and tech., 75% tanks, delivered": "Phosphoric acid, com'l and tech., 75% tanks, delivered",
}

STEP_NAME_TO_KEY = {
    "Ball forming unit": "ball_forming",
    "Crystallizer": "crystallizer",
    "Dryer, batch vacuum tray": "dryer_batch_vacuum_tray",
    "Dryer, rotary (40\u2013100 \u00b0C)": "dryer_rotary_40_100C",
    "Dryer, rotary (100\u2013300 \u00b0C)": "dryer_rotary_100_300C",
    "Dryer, spray": "dryer_spray",
    "Extruder, with feeder": "extruder_with_feeder",
    "Filter, belt vacuum": "filter_belt_vacuum",
    "Filter, plate and frame": "filter_plate_frame",
    "Filter, rotary vacuum": "filter_rotary_vacuum",
    "Flare": "flare",
    "Incipient wetness (impregnation)": "incipient_wetness",
    "Kiln, batch (300\u20131290 \u00b0C)": "kiln_batch",
    "Kiln, continuous direct (300\u20131290 \u00b0C)": "kiln_continuous_direct",
    "Kiln, continuous indirect (300\u20131290 \u00b0C)": "kiln_continuous_indirect",
    "Mill": "mill",
    "Mixer, dry blender": "mixer_dry_blender",
    "Mixer, slurry": "mixer_slurry",
    "Reactor, simple (mixing)": "reactor_simple",
    "Reactor, multistep": "reactor_multistep",
    "Scrubber, NOx": "scrubber_nox",
}

TEMPLATE_METADATA = {
    "FCC Catalyst (USY w/ RE)": {
        "category": "FCC/Zeolite",
        "example_catalysts": ["USY FCC catalyst", "REY FCC catalyst"],
    },
    "Magnesia/Alumina": {
        "category": "Mixed Oxide",
        "example_catalysts": ["MgO/Al2O3"],
    },
    "Metal Carbide (Bulk)": {
        "category": "Bulk Carbide",
        "example_catalysts": ["Mo2C", "WC"],
    },
    "Metal Carbide on Metal Oxide": {
        "category": "Supported Carbide",
        "example_catalysts": ["Mo2C/Al2O3", "WC/ZrO2"],
    },
    "Metal (Earth Abundant) on Metal Oxide": {
        "category": "Supported Metal",
        "example_catalysts": ["Ni/Al2O3", "Co/TiO2", "Cu/SiO2"],
    },
    "Metal (PGM) on Carbon": {
        "category": "Supported PGM",
        "example_catalysts": ["Pt/C", "Pd/C", "Ru/C"],
    },
    "Metal (PGM) on Metal Oxide": {
        "category": "Supported PGM",
        "example_catalysts": ["Pt/Al2O3", "Pd/TiO2", "Rh/SiO2"],
    },
    "Zeolite Beta (Bulk)": {
        "category": "Zeolite",
        "example_catalysts": ["Beta zeolite"],
    },
    "Zeolite Beta with Metal Active Site": {
        "category": "Zeolite",
        "example_catalysts": ["Pd/Beta", "Pt/Beta"],
    },
    "Zeolite ZSM-5 (Bulk)": {
        "category": "Zeolite",
        "example_catalysts": ["ZSM-5"],
    },
    "Zeolite ZSM-5 (20\u201325%)": {
        "category": "Zeolite",
        "example_catalysts": ["ZSM-5/Al2O3", "ZSM-5/SiO2-Al2O3"],
    },
}


def slugify(value: str) -> str:
    """Create a stable filesystem-safe identifier."""
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    ascii_value = ascii_value.replace("%", " pct ")
    return re.sub(r"[^a-z0-9]+", "_", ascii_value.lower()).strip("_")


def _to_float(value: str | None) -> float | None:
    if value in (None, "", "-", "n/a", "#N/A"):
        return None
    return float(value)


def _to_int(value: str | None) -> int | None:
    number = _to_float(value)
    if number is None:
        return None
    return int(round(number))


def _clean_text(value: str | None) -> str:
    cleaned = (value or "").strip()
    return TEXT_OVERRIDES.get(cleaned, cleaned)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class CatCostWorkbook:
    """Thin XLSX reader for the CatCost workbook."""

    def __init__(self, path: Path = WORKBOOK_PATH) -> None:
        self.path = path
        self._archive = zipfile.ZipFile(path)
        self._shared_strings = self._load_shared_strings()
        self._sheet_targets = self._load_sheet_targets()

    def close(self) -> None:
        self._archive.close()

    def _load_shared_strings(self) -> list[str]:
        root = ET.fromstring(self._archive.read("xl/sharedStrings.xml"))
        values: list[str] = []
        for item in root:
            parts = [node.text or "" for node in item.iter(f"{{{NS_MAIN}}}t")]
            values.append("".join(parts))
        return values

    def _load_sheet_targets(self) -> dict[str, str]:
        workbook = ET.fromstring(self._archive.read("xl/workbook.xml"))
        rels = ET.fromstring(self._archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
        targets: dict[str, str] = {}
        sheets = workbook.find(f"{{{NS_MAIN}}}sheets")
        assert sheets is not None
        for sheet in sheets:
            name = sheet.attrib["name"]
            rel_id = sheet.attrib[f"{{{NS_REL}}}id"]
            targets[name] = f"{SHEETS_DIR}{rel_map[rel_id]}"
        return targets

    def _cell_value(self, cell: ET.Element) -> str:
        value_node = cell.find(f"{{{NS_MAIN}}}v")
        if value_node is None:
            return ""
        value = value_node.text or ""
        cell_type = cell.get("t", "")
        if cell_type == "s":
            return self._shared_strings[int(value)]
        return value

    def sheet_rows(self, sheet_name: str) -> list[dict[str, str]]:
        target = self._sheet_targets[sheet_name]
        root = ET.fromstring(self._archive.read(target))
        sheet_data = root.find(f"{{{NS_MAIN}}}sheetData")
        if sheet_data is None:
            return []

        rows: list[dict[str, str]] = []
        for row in sheet_data:
            row_data: dict[str, str] = {}
            for cell in row:
                ref = cell.get("r", "")
                column = "".join(ch for ch in ref if ch.isalpha())
                row_data[column] = self._cell_value(cell)
            rows.append(row_data)
        return rows


def extract_materials_library(workbook: CatCostWorkbook) -> dict[str, Any]:
    rows = workbook.sheet_rows("Materials Library")
    materials = []
    for idx, row in enumerate(rows, start=1):
        if idx < 16:
            continue
        name = _clean_text(row.get("A"))
        if not name:
            continue
        materials.append(
            {
                "name": name,
                "material_type": _clean_text(row.get("B")) or "Chemical",
                "mw_g_mol": _to_float(row.get("C")),
                "density_g_ml": _to_float(row.get("D")),
                "concentration_pct": _to_float(row.get("E")),
                "bulk_price_usd": _to_float(row.get("P")),
                "bulk_qty": _to_float(row.get("Q")),
                "bulk_units": _clean_text(row.get("R")) or None,
                "quote_year": _to_int(row.get("S")),
                "quote_source": _clean_text(row.get("T")),
                "notes": _clean_text(row.get("V")),
            }
        )

    return {
        "version": "1.1.1",
        "basis": "CatCost v1.1.1 Materials Library",
        "source": "CatCost_v1-1-1.xlsx, Materials Library sheet",
        "total_count": len(materials),
        "materials": materials,
    }


def extract_step_library(workbook: CatCostWorkbook) -> dict[str, Any]:
    rows = workbook.sheet_rows("Step Library")
    steps = []
    for idx, row in enumerate(rows, start=1):
        if idx < 4:
            continue
        name = _clean_text(row.get("A"))
        if not name:
            continue
        steps.append(
            {
                "name": name,
                "key": STEP_NAME_TO_KEY[name],
                "cost_small": _to_float(row.get("B")),
                "cost_medium": _to_float(row.get("C")),
                "cost_large": _to_float(row.get("D")),
                "note": _clean_text(row.get("E")) or "-",
                "basis": "$/hr, mid-2017",
            }
        )

    return {
        "version": "1.1.1",
        "source": "CatCost_v1-1-1.xlsx, Step Library sheet",
        "basis_year": 2017,
        "basis_currency": "USD",
        "scale_thresholds": {
            "small_tons_per_day": 1,
            "medium_tons_per_day": 10,
            "large_tons_per_day": 150,
        },
        "total_count": len(steps),
        "steps": steps,
    }


def extract_equipment_library(workbook: CatCostWorkbook) -> dict[str, Any]:
    rows = workbook.sheet_rows("Equip. Library")
    equipment = []
    for idx, row in enumerate(rows, start=1):
        if idx < 3:
            continue
        category = _clean_text(row.get("A"))
        name = _clean_text(row.get("B"))
        if not (category and name):
            continue

        materials = [_clean_text(row.get(col)) for col in ("Q", "R", "S", "T", "U", "V", "W")]
        materials = [value for value in materials if value]
        material_factors = [_to_float(row.get(col)) for col in ("AA", "AB", "AC", "AD", "AE", "AF", "AG")]
        material_factors = [value for value in material_factors if value is not None]

        equipment.append(
            {
                "category": category,
                "name": name,
                "size_units": _clean_text(row.get("C")),
                "s_lower": _to_float(row.get("D")),
                "s_upper": _to_float(row.get("E")),
                "a": _to_float(row.get("F")) or 0.0,
                "b": _to_float(row.get("G")) or 0.0,
                "n": _to_float(row.get("H")) or 0.0,
                "c": _to_float(row.get("I")),
                "d": _to_float(row.get("J")),
                "function_type": _clean_text(row.get("K")),
                "source": _clean_text(row.get("L")),
                "cepci_basis": _to_float(row.get("M")),
                "nf_refinery_basis": _to_float(row.get("N")),
                "year": _to_int(row.get("O")),
                "pricing_basis": _clean_text(row.get("P")),
                "installation_factor": _to_float(row.get("AH")) or 1.0,
                "labor_factor": _to_float(row.get("AI")) or 0.0,
                "note": _clean_text(row.get("AJ")),
                "materials": materials,
                "material_factors": material_factors,
            }
        )

    return {
        "version": "1.1.1",
        "source": "CatCost_v1-1-1.xlsx, Equip. Library sheet",
        "total_count": len(equipment),
        "equipment": equipment,
    }


def extract_chemppi(workbook: CatCostWorkbook) -> dict[str, Any]:
    rows = workbook.sheet_rows("ChemPPI")
    annual: dict[str, float] = {}
    for row in rows:
        year = _clean_text(row.get("A"))
        if year.isdigit() and len(year) == 4:
            avg = row.get("N") or row.get("M")
            if avg:
                annual[year] = float(avg)

    return {
        "version": "1.1.1",
        "source": "CatCost_v1-1-1.xlsx, ChemPPI sheet",
        "series_id": "PCU325---325---",
        "description": "Producer Price Index - Chemical Manufacturing (Base Dec 1984 = 100)",
        "annual": annual,
    }


def extract_cepci(workbook: CatCostWorkbook) -> dict[str, Any]:
    rows = workbook.sheet_rows("CEPCI")
    annual: dict[str, dict[str, float | None]] = {}
    for row in rows:
        year = _clean_text(row.get("A"))
        if year.isdigit() and len(year) == 4 and int(year) <= 2025:
            annual[year] = {
                "CEPCI": _to_float(row.get("B")),
                "MS": _to_float(row.get("C")),
                "NF": _to_float(row.get("D")),
                "ENR": _to_float(row.get("E")),
                "CEPCI_equip": _to_float(row.get("F")),
            }

    return {
        "version": "1.1.1",
        "source": "CatCost_v1-1-1.xlsx, CEPCI sheet",
        "description": "Chemical Engineering Plant Cost Index and related indices",
        "annual": annual,
    }


def extract_capex_factors(workbook: CatCostWorkbook) -> dict[str, Any]:
    rows = workbook.sheet_rows("3d CapEx")
    direct: dict[str, Any] = {}
    indirect: dict[str, Any] = {}
    totals: dict[str, Any] = {}

    key_map = {
        "Purchased Equipment": "purchased_equipment",
        "Installation": "installation",
        "Instrumentation and Controls": "instrumentation_controls",
        "Piping": "piping",
        "Electrical": "electrical",
        "Buildings": "buildings",
        "Yard Improvements": "yard_improvements",
        "Service Facilities": "service_facilities",
        "Waste Treatment": "waste_treatment",
        "Land": "land",
        "Engineering and Supervision": "engineering_supervision",
        "Construction Expenses": "construction_expenses",
        "Legal Expenses": "legal_expenses",
        "Contractor's Fee": "contractors_fee",
        "Contingency": "contingency",
        "Total Direct": "total_direct",
        "Total Indirect": "total_indirect",
        "Total Fixed Capital Investment (FCI)": "total_fci",
        "Working Capital": "working_capital",
        "Total Capital Investment (TCI)": "total_tci",
    }

    for row in rows:
        name = _clean_text(row.get("C"))
        if not name or name.endswith("Capital") or name == "Cost Item":
            continue
        key = key_map.get(name)
        if key is None:
            continue
        payload = {
            "name": name,
            "units": _clean_text(row.get("G")),
            "base": _to_float(row.get("D")),
            "low": _to_float(row.get("E")),
            "high": _to_float(row.get("F")),
        }
        if key in {"total_direct", "total_indirect", "total_fci", "working_capital", "total_tci"}:
            totals[key] = payload
        elif name in {
            "Engineering and Supervision",
            "Construction Expenses",
            "Legal Expenses",
            "Contractor's Fee",
            "Contingency",
        }:
            indirect[key] = payload
        else:
            direct[key] = payload

    return {
        "metadata": {
            "version": "1.1.1",
            "source": "CatCost v1.1.1, 3d CapEx sheet",
            "note": "All values as % of purchased equipment cost unless noted",
        },
        "direct_capital": direct,
        "indirect_capital": indirect,
        "totals": totals,
    }


def extract_opex_factors(workbook: CatCostWorkbook) -> dict[str, Any]:
    rows = workbook.sheet_rows("3e OpEx")
    direct_operating: dict[str, Any] = {}
    fixed_operating: dict[str, Any] = {}
    general_expenses: dict[str, Any] = {}
    direct_labor: dict[str, Any] = {}

    key_map = {
        "Direct Labor Rate": ("direct_labor", "labor_rate"),
        "Supervisory and Clerical Labor": ("direct_operating", "supervisory_clerical"),
        "Laboratory Charges": ("direct_operating", "laboratory_charges"),
        "Maintenance and Repair (M&R)": ("direct_operating", "maintenance_repair"),
        "Operating Supplies": ("direct_operating", "operating_supplies"),
        "Local Taxes": ("fixed_operating", "local_taxes"),
        "Insurance": ("fixed_operating", "insurance"),
        "Rent": ("fixed_operating", "rent"),
        "Plant Overhead": ("fixed_operating", "plant_overhead"),
        "Administration": ("general_expenses", "administration"),
        "Distribution and Marketing": ("general_expenses", "distribution_marketing"),
        "Research and Development": ("general_expenses", "research_development"),
    }

    for row in rows:
        name = _clean_text(row.get("C"))
        if name not in key_map:
            continue
        section, key = key_map[name]
        payload = {
            "name": name,
            "base": _to_float(row.get("D")),
            "low": _to_float(row.get("E")),
            "high": _to_float(row.get("F")),
            "units": _clean_text(row.get("G")),
        }
        if section == "direct_labor":
            direct_labor[key] = payload
        elif section == "direct_operating":
            direct_operating[key] = payload
        elif section == "fixed_operating":
            fixed_operating[key] = payload
        else:
            general_expenses[key] = payload

    return {
        "metadata": {
            "version": "1.1.1",
            "source": "CatCost v1.1.1, 3e OpEx sheet",
        },
        "direct_labor": direct_labor,
        "direct_operating": direct_operating,
        "fixed_operating": fixed_operating,
        "general_expenses": general_expenses,
    }


def extract_spent_catalyst_library(workbook: CatCostWorkbook) -> dict[str, Any]:
    rows = workbook.sheet_rows("Spent Cat Library")
    supports: dict[str, Any] = {}
    metals: dict[str, Any] = {}
    landfill_classes: dict[str, Any] = {}
    bulk_densities: dict[str, Any] = {}
    rcra_metals: dict[str, Any] = {}
    section: str | None = None

    for row in rows:
        key = _clean_text(row.get("A"))
        if not key:
            continue

        if key == "Table 1 - Support-specific data":
            section = "supports"
            continue
        if key == "Table 2 - Metal-specific data":
            section = "metals"
            continue
        if key == "Table 3 - Landfill Fees and Sale Values":
            section = "landfill"
            continue
        if key == "Table 4 - Catalyst Bulk Densities (or specified by user)":
            section = "bulk_densities"
            continue
        if key == "Table 5 - RCRA metals and Toxicity Characteristic Leaching Prodedure Limits. Estimated minimum concentrations of RCRA metals as wt. % in catalyst that would pass the TCLP threshold are provided; no warranty is given as to the accuracy or usefulness of these estimates.":
            section = "rcra"
            continue

        if key in {"Support", "Metal", "Catalyst Hazard Class", "Catalyst"}:
            continue

        if section == "supports":
            supports[key] = {
                "fixed_bed_loss_support_pct": {
                    "low": _to_float(row.get("B")),
                    "high": _to_float(row.get("C")),
                    "avg": _to_float(row.get("D")),
                },
                "fixed_bed_loss_metal_pct": {
                    "low": _to_float(row.get("E")),
                    "high": _to_float(row.get("F")),
                    "avg": _to_float(row.get("G")),
                },
                "slurry_loss_support_pct": {
                    "low": _to_float(row.get("H")),
                    "high": _to_float(row.get("I")),
                    "avg": _to_float(row.get("J")),
                },
                "slurry_loss_metal_pct": {
                    "low": _to_float(row.get("K")),
                    "high": _to_float(row.get("L")),
                    "avg": _to_float(row.get("M")),
                },
                "thermal_ox_fee_per_lb": {
                    "low": _to_float(row.get("N")),
                    "high": _to_float(row.get("O")),
                    "avg": _to_float(row.get("P")),
                },
                "incoming_fee_per_ft3": {
                    "low": _to_float(row.get("Q")),
                    "high": _to_float(row.get("R")),
                    "avg": _to_float(row.get("S")),
                },
                "metal_contaminant_fee_per_ft3": {
                    "low": _to_float(row.get("T")),
                    "high": _to_float(row.get("U")),
                    "avg": _to_float(row.get("V")),
                },
            }
            continue

        if section == "metals":
            metals[key] = {
                "loss_refining_pct": {
                    "low": _to_float(row.get("B")),
                    "high": _to_float(row.get("C")),
                    "avg": _to_float(row.get("D")),
                },
                "refining_charge_per_troy_oz": _to_float(row.get("E")),
                "is_precious_metal": _clean_text(row.get("F")).lower() == "yes",
                "spot_price": _to_float(row.get("H")),
                "spot_unit": _clean_text(row.get("I")),
                "spot_year": _to_int(row.get("J")),
                "spot_source": _clean_text(row.get("K")),
                "note": _clean_text(row.get("G")),
            }
            continue

        if section == "landfill":
            landfill_classes[key] = {
                "landfill_fee_per_lb": {
                    "low": _to_float(row.get("B")),
                    "high": _to_float(row.get("C")),
                    "avg": _to_float(row.get("D")),
                },
                "sale_value_per_lb": {
                    "low": _to_float(row.get("E")),
                    "high": _to_float(row.get("F")),
                    "avg": _to_float(row.get("G")),
                },
                "note": _clean_text(row.get("H")),
            }
            continue

        if section == "bulk_densities":
            bulk_densities[key] = {
                "lb_per_ft3": _to_float(row.get("B")),
                "kg_per_m3": _to_float(row.get("C")),
                "note": _clean_text(row.get("D")),
            }
            continue

        if section == "rcra":
            rcra_metals[key] = {
                "tclp_limit_mg_per_l": _to_float(row.get("B")),
                "estimated_concentration_wt_pct": _to_float(row.get("C")),
            }

    return {
        "version": "1.1.1",
        "source": "CatCost_v1-1-1.xlsx, Spent Cat Library sheet",
        "basis_year": 2016,
        "supports": supports,
        "metals": metals,
        "landfill_classes": landfill_classes,
        "bulk_densities": bulk_densities,
        "rcra_metals": rcra_metals,
    }


def extract_process_templates(workbook: CatCostWorkbook) -> list[dict[str, Any]]:
    rows = workbook.sheet_rows("3a Step Method")
    templates: list[dict[str, Any]] = []
    idx = 0
    while idx < len(rows):
        row = rows[idx]
        if _clean_text(row.get("C")) != "Step Method Template Name":
            idx += 1
            continue

        name = _clean_text(rows[idx + 1].get("C"))
        if not name:
            idx += 1
            continue

        description = ""
        note = ""
        step_header_idx = idx + 1
        cursor = idx + 2
        while cursor < len(rows):
            current = _clean_text(rows[cursor].get("C"))
            if current == "Description" and cursor + 1 < len(rows):
                description = _clean_text(rows[cursor + 1].get("C"))
            elif current.startswith("Note that"):
                note = current
            elif current == "Step Name":
                step_header_idx = cursor
                break
            cursor += 1

        step_quantities = []
        cursor = step_header_idx + 1
        while cursor < len(rows):
            current_name = _clean_text(rows[cursor].get("C"))
            if current_name == "Step Method Template Name":
                break
            quantity = _to_float(rows[cursor].get("D"))
            if current_name in STEP_NAME_TO_KEY and quantity and quantity > 0:
                step_quantities.append(
                    {
                        "step": STEP_NAME_TO_KEY[current_name],
                        "template_step_name": current_name,
                        "quantity": quantity,
                        "note": _clean_text(rows[cursor].get("I")),
                    }
                )
            cursor += 1

        metadata = TEMPLATE_METADATA.get(name, {"category": "CatCost Template", "example_catalysts": []})
        expanded_steps: list[str] = []
        for item in step_quantities:
            expanded_steps.extend([item["step"]] * int(round(item["quantity"])))

        templates.append(
            {
                "id": slugify(name),
                "name": name,
                "description": description or note,
                "category": metadata["category"],
                "example_catalysts": metadata["example_catalysts"],
                "steps": expanded_steps,
                "step_quantities": step_quantities,
                "source": "CatCost_v1-1-1.xlsx, 3a Step Method sheet",
            }
        )
        idx = cursor

    return templates


def sync_spent_catalyst_json(workbook: CatCostWorkbook) -> Path:
    path = DATA_DIR / "spent_catalyst.json"
    _write_json(path, extract_spent_catalyst_library(workbook))
    return path


def sync_process_templates(workbook: CatCostWorkbook) -> list[Path]:
    written: list[Path] = []
    for template in extract_process_templates(workbook):
        path = PROCESS_TEMPLATES_DIR / f"{template['id']}.json"
        _write_json(path, template)
        written.append(path)
    return written
