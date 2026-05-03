"""Cradle-to-gate Life Cycle Assessment (LCA) for catalyst formulations.

Computes Global Warming Potential (kg CO2-eq) and Cumulative Energy Demand (MJ)
per kg of finished catalyst, as a wt%-weighted sum of per-element impact factors.

All seed values come from a single, peer-reviewed open-access source:
    Nuss P, Eckelman MJ (2014). PLOS ONE 9(7): e101298.
    doi:10.1371/journal.pone.0101298  (CC BY 4.0)

The engine never invents factors. Components without a verified factor in
backend/data/lca_factors.json contribute their wt% to a `data_gap_pct`
field that the response surfaces to the user.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from backend.paths import data_dir

_DATA_DIR = data_dir()
_LCA_FILE = _DATA_DIR / "lca_factors.json"


@lru_cache(maxsize=1)
def _load_lca_dataset() -> dict:
    """Read and cache the LCA seed JSON.

    Cached at module level — the dataset is small and read-only at runtime.
    """
    with open(_LCA_FILE, encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_element_key(component: dict, aliases: dict[str, str]) -> str | None:
    """Find the LCA dataset key for a component.

    Resolution order:
      1. Direct hit on `name` (e.g. "Pt", "TiO2", "ZrO2")
      2. Form-alias hit (e.g. "Al2O3" -> "Al")
      3. Symbol of the chemical formula stripped of digits (e.g. "Pt2O" -> "Pt")
      4. None — caller treats this as a data gap
    """
    name = (component.get("name") or "").strip()
    if not name:
        return None

    factors = _load_lca_dataset()["factors"]
    if name in factors:
        return name
    if name in aliases:
        target = aliases[name]
        if target in factors:
            return target

    # Last-resort: drop trailing digits and try again ("Pt3" -> "Pt").
    stripped = "".join(ch for ch in name if not ch.isdigit())
    if stripped in factors:
        return stripped
    if stripped in aliases and aliases[stripped] in factors:
        return aliases[stripped]
    return None


def compute_catalyst_lca(components: list[dict]) -> dict[str, Any]:
    """Compute cradle-to-gate impact per kg of finished catalyst.

    Parameters
    ----------
    components:
        List of resolved component dicts containing at least:
          - "name" (str): element symbol or material name
          - "wt_pct" (float): weight percent in the finished catalyst (0-100)
        Extra keys are ignored.

    Returns
    -------
    dict with:
        gwp_kg_co2eq_per_kg_catalyst (float | None)
        ced_mj_per_kg_catalyst (float | None)
        per_component (list[dict]) — per-component contribution + matched factor
        data_gap_pct (float) — total wt% with no verified factor
        coverage_pct (float) — total wt% with verified factors
        warnings (list[str])
        reference (dict) — citation metadata for the result
    """
    dataset = _load_lca_dataset()
    factors: dict[str, dict] = dataset["factors"]
    aliases: dict[str, str] = dataset.get("form_aliases", {})
    unsupported: set[str] = set(dataset.get("unsupported_supports", []))

    total_wt = sum(max(0.0, float(c.get("wt_pct", 0.0))) for c in components)
    if total_wt <= 0:
        return {
            "gwp_kg_co2eq_per_kg_catalyst": None,
            "ced_mj_per_kg_catalyst": None,
            "per_component": [],
            "data_gap_pct": 0.0,
            "coverage_pct": 0.0,
            "warnings": ["No components with positive wt_pct — LCA cannot be computed."],
            "reference": _reference_block(),
        }

    per_component: list[dict[str, Any]] = []
    gwp_total = 0.0
    ced_total = 0.0
    gap_wt = 0.0
    warnings: list[str] = []

    for component in components:
        wt = max(0.0, float(component.get("wt_pct", 0.0)))
        if wt == 0:
            continue
        share = wt / total_wt  # mass fraction of finished catalyst
        name = (component.get("name") or "").strip() or "(unnamed)"

        key = _resolve_element_key(component, aliases)
        if key is None:
            gap_wt += wt
            reason = "explicitly_unsupported" if name in unsupported else "no_factor_in_dataset"
            per_component.append({
                "name": name,
                "role": component.get("role"),
                "wt_pct": wt,
                "matched_key": None,
                "factor_status": reason,
                "gwp_contribution_kg_co2eq_per_kg_catalyst": None,
                "ced_contribution_mj_per_kg_catalyst": None,
            })
            if name in unsupported:
                warnings.append(
                    f"{name}: support material not in {dataset['primary_reference']['citation']}; "
                    "treated as data gap. Add a verified LCI source to backend/data/lca_factors.json to fill in."
                )
            else:
                warnings.append(
                    f"{name}: no verified LCA factor — contributes {wt:.2f} wt% to the data gap."
                )
            continue

        factor = factors[key]
        gwp_per_kg = float(factor["gwp_kg_co2eq_per_kg"])
        ced_per_kg = float(factor["ced_mj_per_kg"])
        gwp_contrib = share * gwp_per_kg
        ced_contrib = share * ced_per_kg

        gwp_total += gwp_contrib
        ced_total += ced_contrib
        per_component.append({
            "name": name,
            "role": component.get("role"),
            "wt_pct": wt,
            "matched_key": key,
            "factor_status": "matched_alias" if key != name else "matched",
            "gwp_kg_co2eq_per_kg_material": gwp_per_kg,
            "ced_mj_per_kg_material": ced_per_kg,
            "gwp_contribution_kg_co2eq_per_kg_catalyst": round(gwp_contrib, 4),
            "ced_contribution_mj_per_kg_catalyst": round(ced_contrib, 4),
            "process_name": factor.get("process_name"),
            "data_origin": factor.get("data_origin"),
        })

    data_gap_pct = round(100.0 * gap_wt / total_wt, 2) if total_wt > 0 else 0.0
    coverage_pct = round(100.0 - data_gap_pct, 2)

    if data_gap_pct >= 50.0:
        warnings.append(
            f"Coverage is only {coverage_pct:.1f}% of catalyst mass — "
            "the reported impact is a partial estimate."
        )

    has_any_match = any(c["factor_status"] not in {"explicitly_unsupported", "no_factor_in_dataset"} for c in per_component)
    return {
        "gwp_kg_co2eq_per_kg_catalyst": round(gwp_total, 4) if has_any_match else None,
        "ced_mj_per_kg_catalyst": round(ced_total, 4) if has_any_match else None,
        "per_component": per_component,
        "data_gap_pct": data_gap_pct,
        "coverage_pct": coverage_pct,
        "warnings": warnings,
        "reference": _reference_block(),
        "impact_categories": dataset["impact_categories"],
    }


def _reference_block() -> dict:
    """Return citation metadata to attach to every LCA result."""
    dataset = _load_lca_dataset()
    return dataset["primary_reference"]


def list_factors() -> dict:
    """Return the full LCA dataset (used by GET /api/lca/factors)."""
    dataset = _load_lca_dataset()
    return {
        "schema_version": dataset["schema_version"],
        "description": dataset["description"],
        "impact_categories": dataset["impact_categories"],
        "primary_reference": dataset["primary_reference"],
        "factors": dataset["factors"],
        "form_aliases": dataset.get("form_aliases", {}),
        "form_alias_note": dataset.get("form_alias_note", ""),
        "unsupported_supports": dataset.get("unsupported_supports", []),
        "unsupported_note": dataset.get("unsupported_note", ""),
    }
