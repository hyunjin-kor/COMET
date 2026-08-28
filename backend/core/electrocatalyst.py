"""Area-based adjunct model for electrocatalyst coating workflows."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

GRAMS_PER_LB = 453.59237
CM2_PER_M2 = 10_000

_MEA_MANUFACTURING_PATH = Path(__file__).resolve().parents[1] / "data" / "mea_manufacturing.json"


@lru_cache(maxsize=1)
def load_mea_manufacturing() -> dict:
    """MEA manufacturing scenarios derived from Hog et al. 2026 (see the data file)."""
    return json.loads(_MEA_MANUFACTURING_PATH.read_text(encoding="utf-8"))


def calculate_electrode_layer_cost(
    *,
    catalyst_price_per_lb: float,
    active_area_cm2: float,
    catalyst_loading_mg_cm2: float,
    ionomer_to_catalyst_ratio: float = 0.0,
    ionomer_price_per_ml: float = 0.0,
    ionomer_price_per_kg_solids: float = 0.0,
    ionomer_density_g_ml: float = 0.94,
    ionomer_solids_fraction: float = 0.05,
    substrate_cost_per_cm2: float = 0.0,
    membrane_cost_per_cm2: float = 0.0,
    application_family: str = "general",
    manufacturing_scenario: str | None = None,
) -> dict:
    """Estimate area-based coating cost for a single electrocatalyst layer."""

    if active_area_cm2 <= 0:
        raise ValueError("active_area_cm2 must be positive")
    if catalyst_loading_mg_cm2 <= 0:
        raise ValueError("catalyst_loading_mg_cm2 must be positive")
    if ionomer_to_catalyst_ratio < 0:
        raise ValueError("ionomer_to_catalyst_ratio must be non-negative")
    if ionomer_density_g_ml <= 0:
        raise ValueError("ionomer_density_g_ml must be positive")
    if not 0 < ionomer_solids_fraction <= 1:
        raise ValueError("ionomer_solids_fraction must be between 0 and 1")

    catalyst_mass_g = active_area_cm2 * catalyst_loading_mg_cm2 / 1000.0
    catalyst_cost_usd = catalyst_mass_g / GRAMS_PER_LB * catalyst_price_per_lb

    ionomer_solids_mass_g = catalyst_mass_g * ionomer_to_catalyst_ratio
    ionomer_dispersion_mass_g = 0.0
    ionomer_dispersion_volume_ml = 0.0
    ionomer_cost_usd = 0.0
    ionomer_pricing_mode = "none"
    if ionomer_solids_mass_g > 0 and ionomer_price_per_kg_solids > 0:
        ionomer_cost_usd = ionomer_solids_mass_g / 1000.0 * ionomer_price_per_kg_solids
        ionomer_pricing_mode = "dry_solids"
    elif ionomer_solids_mass_g > 0:
        ionomer_dispersion_mass_g = ionomer_solids_mass_g / ionomer_solids_fraction
        ionomer_dispersion_volume_ml = ionomer_dispersion_mass_g / ionomer_density_g_ml
        ionomer_cost_usd = ionomer_dispersion_volume_ml * ionomer_price_per_ml
        ionomer_pricing_mode = "dispersion_volume"

    substrate_cost_usd = substrate_cost_per_cm2 * active_area_cm2
    membrane_cost_usd = membrane_cost_per_cm2 * active_area_cm2

    manufacturing_cost_usd = 0.0
    manufacturing_detail = None
    if manufacturing_scenario:
        data = load_mea_manufacturing()
        scenario = data["scenarios"].get(manufacturing_scenario)
        if scenario is None:
            raise ValueError(
                f"unknown manufacturing_scenario {manufacturing_scenario!r}; "
                f"expected one of {sorted(data['scenarios'])}"
            )
        manufacturing_cost_usd = scenario["manufacturing_usd_per_cm2"] * active_area_cm2
        manufacturing_detail = {
            "scenario": manufacturing_scenario,
            "label": scenario["label"],
            "usd_per_cm2": scenario["manufacturing_usd_per_cm2"],
            "eur_per_m2": scenario["manufacturing_eur_per_m2"],
            "eur_to_usd": data["currency_conversion"]["eur_to_usd"],
            "fx_basis": data["currency_conversion"]["basis"],
            "source": data["source"],
            "reference_url": data["reference_url"],
            "confidence": data["confidence"],
        }

    total_cost_usd = (
        catalyst_cost_usd + ionomer_cost_usd + substrate_cost_usd + membrane_cost_usd
        + manufacturing_cost_usd
    )
    cost_per_cm2_usd = total_cost_usd / active_area_cm2

    return {
        "application_family": application_family,
        "active_area_cm2": round(active_area_cm2, 4),
        "catalyst_loading_mg_cm2": round(catalyst_loading_mg_cm2, 4),
        "catalyst_mass_g": round(catalyst_mass_g, 6),
        "catalyst_cost_usd": round(catalyst_cost_usd, 6),
        "ionomer_to_catalyst_ratio": round(ionomer_to_catalyst_ratio, 4),
        "ionomer_pricing_mode": ionomer_pricing_mode,
        "ionomer_solids_mass_g": round(ionomer_solids_mass_g, 6),
        "ionomer_dispersion_volume_ml": round(ionomer_dispersion_volume_ml, 6),
        "ionomer_cost_usd": round(ionomer_cost_usd, 6),
        "substrate_cost_usd": round(substrate_cost_usd, 6),
        "membrane_cost_usd": round(membrane_cost_usd, 6),
        "manufacturing_cost_usd": round(manufacturing_cost_usd, 6),
        "manufacturing": manufacturing_detail,
        "total_cost_usd": round(total_cost_usd, 6),
        "cost_per_cm2_usd": round(cost_per_cm2_usd, 6),
        "cost_per_m2_usd": round(cost_per_cm2_usd * CM2_PER_M2, 2),
        "breakdown": [
            {"label": "Catalyst powder", "cost_usd": round(catalyst_cost_usd, 6)},
            {"label": "Ionomer", "cost_usd": round(ionomer_cost_usd, 6)},
            {"label": "Substrate / GDL", "cost_usd": round(substrate_cost_usd, 6)},
            {"label": "Membrane", "cost_usd": round(membrane_cost_usd, 6)},
            {"label": "Manufacturing (equipment, labor, facility)", "cost_usd": round(manufacturing_cost_usd, 6)},
        ],
    }
