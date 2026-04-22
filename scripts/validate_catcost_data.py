"""Validate checked-in CatCost-derived JSON against the workbook."""

from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from catcost_excel import (
    CatCostWorkbook,
    extract_cepci,
    extract_chemppi,
    extract_equipment_library,
    extract_materials_library,
    extract_process_templates,
    extract_spent_catalyst_library,
    extract_step_library,
    slugify,
)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "backend" / "data"
PROCESS_TEMPLATES_DIR = DATA_DIR / "process_templates"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_equal(label: str, left, right, failures: list[str]) -> None:
    if left != right:
        failures.append(f"{label}: expected {left!r}, got {right!r}")


def _material_workbook_view(item: dict) -> dict:
    """Compare only fields populated directly from the workbook rows."""
    return {
        "name": item["name"],
        "mw_g_mol": item["mw_g_mol"],
        "density_g_ml": item["density_g_ml"],
        "concentration_pct": item["concentration_pct"],
        "bulk_price_usd": item["bulk_price_usd"],
        "bulk_qty": item["bulk_qty"],
        "bulk_units": item["bulk_units"],
        "quote_year": item["quote_year"],
        "quote_source": item["quote_source"],
        "notes": item["notes"],
    }


def main() -> int:
    workbook = CatCostWorkbook()
    failures: list[str] = []
    try:
        materials = extract_materials_library(workbook)
        checked_materials = _load_json(DATA_DIR / "materials_library.json")
        _assert_equal("materials.total_count", materials["total_count"], checked_materials["total_count"], failures)
        _assert_equal(
            "materials.first",
            _material_workbook_view(materials["materials"][0]),
            _material_workbook_view(checked_materials["materials"][0]),
            failures,
        )
        _assert_equal(
            "materials.last",
            _material_workbook_view(materials["materials"][-1]),
            _material_workbook_view(checked_materials["materials"][-1]),
            failures,
        )

        steps = extract_step_library(workbook)
        checked_steps = _load_json(DATA_DIR / "step_library.json")
        _assert_equal("step_library", steps, checked_steps, failures)

        equipment = extract_equipment_library(workbook)
        checked_equipment = _load_json(DATA_DIR / "equipment_library.json")
        _assert_equal("equipment.total_count", equipment["total_count"], checked_equipment["total_count"], failures)
        _assert_equal("equipment.first", equipment["equipment"][0], checked_equipment["equipment"][0], failures)
        _assert_equal("equipment.last", equipment["equipment"][-1], checked_equipment["equipment"][-1], failures)

        chemppi = extract_chemppi(workbook)
        checked_chemppi = _load_json(DATA_DIR / "chemppi.json")
        _assert_equal("chemppi.annual", chemppi["annual"], checked_chemppi["annual"], failures)

        cepci = extract_cepci(workbook)
        checked_cepci = _load_json(DATA_DIR / "cepci.json")
        _assert_equal("cepci.annual", cepci["annual"], checked_cepci["annual"], failures)

        spent = extract_spent_catalyst_library(workbook)
        checked_spent = _load_json(DATA_DIR / "spent_catalyst.json")
        _assert_equal("spent.supports", spent["supports"], checked_spent["supports"], failures)
        _assert_equal("spent.metals", spent["metals"], checked_spent["metals"], failures)
        _assert_equal("spent.landfill_classes", spent["landfill_classes"], checked_spent["landfill_classes"], failures)
        _assert_equal("spent.bulk_densities", spent["bulk_densities"], checked_spent["bulk_densities"], failures)
        _assert_equal("spent.rcra_metals", spent["rcra_metals"], checked_spent["rcra_metals"], failures)

        workbook_templates = {slugify(item["name"]): item for item in extract_process_templates(workbook)}
        for template_id, template in workbook_templates.items():
            checked_path = PROCESS_TEMPLATES_DIR / f"{template_id}.json"
            if not checked_path.exists():
                failures.append(f"process template missing: {template_id}")
                continue
            checked = _load_json(checked_path)
            _assert_equal(f"template.{template_id}", template, checked, failures)
    finally:
        workbook.close()

    if failures:
        print("CatCost workbook validation failed:")
        for failure in failures:
            print(f"  * {failure}")
        return 1

    print("CatCost workbook validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
