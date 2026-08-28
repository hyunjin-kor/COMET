"""The MEA manufacturing adder: derived values, provenance, and default-off behavior."""

import json
from pathlib import Path

import pytest

from backend.core.electrocatalyst import calculate_electrode_layer_cost, load_mea_manufacturing

DATA = Path(__file__).resolve().parents[1] / "data" / "mea_manufacturing.json"

BASE = dict(
    catalyst_price_per_lb=15000.0,
    active_area_cm2=250.0,
    catalyst_loading_mg_cm2=0.4,
    membrane_cost_per_cm2=0.02,
)


def test_default_is_materials_only():
    """No scenario -> identical totals to the pre-existing model."""
    r = calculate_electrode_layer_cost(**BASE)
    assert r["manufacturing_cost_usd"] == 0.0
    assert r["manufacturing"] is None
    assert r["total_cost_usd"] == pytest.approx(
        r["catalyst_cost_usd"] + r["ionomer_cost_usd"] + r["substrate_cost_usd"] + r["membrane_cost_usd"]
    )


@pytest.mark.parametrize("scenario", ["rnd_batch", "pilot_roll_to_roll"])
def test_scenario_adds_area_proportional_cost(scenario):
    data = json.loads(DATA.read_text(encoding="utf-8"))
    per_cm2 = data["scenarios"][scenario]["manufacturing_usd_per_cm2"]
    r = calculate_electrode_layer_cost(**BASE, manufacturing_scenario=scenario)
    assert r["manufacturing_cost_usd"] == pytest.approx(per_cm2 * BASE["active_area_cm2"], rel=1e-6)
    base = calculate_electrode_layer_cost(**BASE)
    assert r["total_cost_usd"] == pytest.approx(base["total_cost_usd"] + r["manufacturing_cost_usd"], rel=1e-6)


def test_unknown_scenario_is_rejected():
    with pytest.raises(ValueError, match="unknown manufacturing_scenario"):
        calculate_electrode_layer_cost(**BASE, manufacturing_scenario="bogus")


def test_derivation_chain_is_internally_consistent():
    """Each stored figure must reproduce from the one before it, so a hand edit
    to any single number breaks loudly instead of silently shipping."""
    data = json.loads(DATA.read_text(encoding="utf-8"))
    fx = data["currency_conversion"]["eur_to_usd"]
    for name, s in data["scenarios"].items():
        eur = s["total_eur_per_m2_active"] * (1 - s["consumable_share"])
        assert s["manufacturing_eur_per_m2"] == pytest.approx(eur, rel=1e-3), name
        assert s["manufacturing_usd_per_m2"] == pytest.approx(eur * fx, rel=1e-3), name
        assert s["manufacturing_usd_per_cm2"] == pytest.approx(eur * fx / 10_000, rel=1e-3), name


def test_provenance_travels_with_the_result():
    r = calculate_electrode_layer_cost(**BASE, manufacturing_scenario="rnd_batch")
    m = r["manufacturing"]
    assert m["reference_url"].startswith("https://doi.org/")
    assert m["eur_to_usd"] == 1.1306
    assert m["confidence"] == "derived"


def test_data_file_declares_its_conversions():
    data = load_mea_manufacturing()
    cc = data["currency_conversion"]
    assert cc["eur_to_usd"] > 0 and cc["basis"] and cc["source_url"].startswith("http")
    assert data["reference_url"].startswith("https://doi.org/")
