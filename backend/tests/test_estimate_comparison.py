"""Saved estimates retain their evidence while comparisons harmonize prices."""

import json
from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.database import get_session
from backend.models.estimate import Estimate
from backend.models.metal_price import MetalPrice
from backend.routers.calculator import _prepare_calculation
from backend.routers.estimate_comparison import router
from backend.schemas.cost_input import CostCalculationRequest


@pytest.fixture
def comparison_client(session):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        yield client


def _thermal(price=20.0, order=2.0):
    return {
        "components": [
            {"role": "active_metal", "name": "Ni", "wt_pct": 20, "price_per_lb": price},
            {"role": "support", "name": "Al2O3", "wt_pct": 80, "price_per_lb": 1.0},
        ],
        "order_size_tons": order, "target_year": 2017,
        "steps": ["mixer_slurry", "dryer_rotary_100_300C"],
    }


def _save(session, payload, name="Synthetic test estimate"):
    req = CostCalculationRequest.model_validate(payload)
    result, _, family = _prepare_calculation(req, session)
    row = Estimate(name=name, catalyst_domain=req.catalyst_domain,
                   application_family=family, input_json=json.dumps(req.model_dump(mode="json")),
                   result_json=json.dumps(result))
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def _request(first, second, **updates):
    return {"estimate_ids": [first.id, second.id], "reference_estimate_id": first.id,
            "price_basis": "reference", "order_size_tons": 20, **updates}


def test_price_and_scale_are_separated_without_mutating_saved_snapshots(session, comparison_client):
    first = _save(session, _thermal(20, 2), "Reference")
    second = _save(session, _thermal(40, 200), "Alternative")
    before = [(row.input_json, row.result_json) for row in (first, second)]
    response = comparison_client.post("/api/estimates/compare", json=_request(first, second))
    assert response.status_code == 200, response.text
    data = response.json()
    one, two = data["estimates"]
    assert one["values"]["common_conditions"] == two["values"]["common_conditions"]
    assert one["values"]["repriced_original_conditions"] != two["values"]["repriced_original_conditions"]
    assert two["values"]["saved"] != two["values"]["repriced_original_conditions"]
    assert data["common_conditions"]["order_size_tons"] == 20
    nickel = next(item for item in data["price_snapshot"] if item["key"] == "manual:ni:")
    assert nickel["values"]["price_per_lb"] == 20
    assert nickel["overridden_estimate_ids"] == [second.id]
    for row in (first, second):
        session.refresh(row)
    assert before == [(row.input_json, row.result_json) for row in (first, second)]


def test_selection_order_never_changes_reference_price_priority(session, comparison_client):
    first = _save(session, _thermal(20))
    second = _save(session, _thermal(40))
    forward = comparison_client.post("/api/estimates/compare", json=_request(first, second)).json()
    reverse = comparison_client.post("/api/estimates/compare", json=_request(
        first, second, estimate_ids=[second.id, first.id],
    )).json()
    assert forward["price_snapshot"] == reverse["price_snapshot"]
    assert {row["estimate_id"]: row["values"] for row in forward["estimates"]} == {
        row["estimate_id"]: row["values"] for row in reverse["estimates"]
    }


@pytest.mark.parametrize("updates", [
    {"estimate_ids": [1, 1]}, {"estimate_ids": [1]},
    {"reference_estimate_id": 999999}, {"order_size_tons": 0},
])
def test_invalid_selection_is_rejected(session, comparison_client, updates):
    first = _save(session, _thermal())
    second = _save(session, _thermal())
    response = comparison_client.post("/api/estimates/compare", json=_request(first, second, **updates))
    assert response.status_code == 422


def test_unknown_saved_estimate_is_not_silently_omitted(session, comparison_client):
    first = _save(session, _thermal())
    response = comparison_client.post("/api/estimates/compare", json={
        "estimate_ids": [first.id, 999999], "reference_estimate_id": first.id,
        "order_size_tons": 20, "price_basis": "reference",
    })
    assert response.status_code == 404


def _electrode(area=25.0, loading=0.5, price=1000.0):
    return {
        "components": [{"role": "active_catalyst", "name": "Pt/C", "wt_pct": 100,
                        "price_per_lb": price}],
        "catalyst_domain": "electrocatalyst", "application_family": "fuel_cell",
        "target_year": 2017, "steps": ["mixer_slurry"],
        "electrode_input": {"active_area_cm2": area,
                            "catalyst_loading_mg_cm2": loading,
                            "substrate_cost_per_cm2": 0.001},
    }


def test_electrode_comparison_uses_area_headline_and_shared_loading(session, comparison_client):
    first = _save(session, _electrode())
    second = _save(session, _electrode(100, 2.0, 2000))
    response = comparison_client.post("/api/estimates/compare", json=_request(first, second))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["unit"] == "USD/cm2"
    one, two = data["estimates"]
    assert one["values"]["common_conditions"] == two["values"]["common_conditions"]
    assert one["values"]["repriced_original_conditions"] != two["values"]["repriced_original_conditions"]
    assert one["values"]["common_conditions"] == one["common_conditions"]["electrode_model"]["cost_per_cm2_usd"]
    assert two["common_conditions"]["electrode_model"]["active_area_cm2"] == 25
    assert two["common_conditions"]["electrode_model"]["catalyst_loading_mg_cm2"] == 0.5


def test_mixed_domains_and_applications_are_rejected(session, comparison_client):
    first = _save(session, _thermal())
    second = _save(session, _electrode())
    response = comparison_client.post("/api/estimates/compare", json=_request(first, second))
    assert response.status_code == 422
    third_payload = _electrode()
    third_payload["application_family"] = "electrolyzer"
    third = _save(session, third_payload)
    response = comparison_client.post("/api/estimates/compare", json=_request(second, third))
    assert response.status_code == 422


def test_complete_multimetal_compositions_are_preserved(session, comparison_client):
    payload = _thermal()
    payload["components"] = [
        {"role": "active_metal", "name": "Ni", "wt_pct": 20, "price_per_lb": 20},
        {"role": "active_metal", "name": "Cu", "wt_pct": 10, "price_per_lb": 5},
        {"role": "promoter", "name": "Co", "wt_pct": 5, "price_per_lb": 15},
        {"role": "support", "name": "Al2O3", "wt_pct": 65, "price_per_lb": 1},
    ]
    first = _save(session, payload)
    second = _save(session, _thermal())
    data = comparison_client.post("/api/estimates/compare", json=_request(first, second)).json()
    common = data["estimates"][0]["common_conditions"]
    assert common["input_summary"]["n_components"] == 4
    assert [row["name"] for row in common["materials"]["components"]] == ["Ni", "Cu", "Co", "Al2O3"]


def test_reference_library_snapshot_uses_requested_price_tier(session, comparison_client):
    session.add(MetalPrice(symbol="Ni", name="Nickel", price=17, unit="$/lb",
                          source="Synthetic reference test quote", basis="reference"))
    session.add(MetalPrice(symbol="Ni", name="Nickel", price=29, unit="$/lb",
                          source="Synthetic live test quote", basis="live"))
    session.commit()
    payload = _thermal()
    payload["components"][0] = {"role": "active_metal", "material_key": "lit:usgs-nickel-cathode-2025", "wt_pct": 20}
    first = _save(session, payload)
    second = _save(session, payload)
    data = comparison_client.post("/api/estimates/compare", json=_request(first, second)).json()
    snapshot = next(row for row in data["price_snapshot"] if row["key"].startswith("library:"))
    assert snapshot["values"]["price_per_lb"] == 17
    assert snapshot["evidence"]["quote_source"] == "Synthetic reference test quote"
    assert data["estimates"][0]["common_conditions"]["resolved_materials"][0]["normalized_price_per_lb"] == 17


def test_recipe_and_consumable_prices_harmonize_but_consumption_is_preserved(session, comparison_client):
    payload = _thermal()
    payload["components"][0]["recipe_consumption"] = {
        "precursor_name": "Synthetic nickel precursor, grade A",
        "retained_component_fraction": 0.2, "purity_fraction": 1, "yield_fraction": 0.5,
        "price_per_kg": 10, "source_note": "Synthetic test input; not a market observation",
    }
    payload["consumables"] = [{"name": "Synthetic wash liquid, grade A", "kg_per_kg_catalyst": 2,
                               "price_per_kg": 3, "source_note": "Synthetic test input"}]
    first = _save(session, payload)
    alternative = deepcopy(payload)
    alternative["components"][0]["recipe_consumption"].update(price_per_kg=100, yield_fraction=1)
    alternative["consumables"][0].update(price_per_kg=30, kg_per_kg_catalyst=4)
    second = _save(session, alternative)
    data = comparison_client.post("/api/estimates/compare", json=_request(first, second)).json()
    assert any(row["key"].startswith("precursor:") for row in data["price_snapshot"])
    assert any(row["key"].startswith("consumable:") for row in data["price_snapshot"])
    assert data["estimates"][0]["values"]["common_conditions"] != data["estimates"][1]["values"]["common_conditions"]
    assert data["estimates"][1]["values"]["common_conditions"] < data["estimates"][1]["values"]["saved"]


def test_scale_specific_equipment_is_substituted_and_disclosed(session, comparison_client):
    payload = _thermal(order=20)
    payload["steps"] = ["kiln_continuous_indirect", "filter_rotary_vacuum"]
    first = _save(session, payload)
    second = _save(session, payload)
    response = comparison_client.post("/api/estimates/compare", json=_request(first, second, order_size_tons=2))
    assert response.status_code == 200, response.text
    common = response.json()["estimates"][0]["common_conditions"]
    assert [step["step"] for step in common["step_method"]["step_details"]] == ["kiln_batch", "filter_plate_frame"]
    assert common["costing_scope"]["substitutions"] == [
        {"from": "kiln_continuous_indirect", "to": "kiln_batch"},
        {"from": "filter_rotary_vacuum", "to": "filter_plate_frame"},
    ]
    assert common["costing_scope"]["status"] == "proxy"


def test_shared_effective_rate_and_overhead_follow_named_reference(session, comparison_client):
    payload = _thermal()
    payload.update(production_rate_ton_per_day=1, production_rate_note="Synthetic test rate",
                   ga_overhead_pct=0.1, sard_pct=0.12)
    first = _save(session, payload)
    alternative = _thermal()
    alternative.update(production_rate_ton_per_day=2, production_rate_note="Synthetic alternate rate")
    second = _save(session, alternative)
    data = comparison_client.post("/api/estimates/compare", json=_request(first, second)).json()
    assert data["common_conditions"]["production_rate_ton_per_day"] == 1
    assert data["common_conditions"]["ga_overhead_pct"] == 0.1
    assert data["common_conditions"]["sard_pct"] == 0.12
    assert data["estimates"][1]["common_conditions"]["step_method"]["production_rate_ton_per_day"] == 1
    assert data["estimates"][1]["repriced_original_conditions"]["step_method"]["production_rate_ton_per_day"] == 2


def test_harmonized_manual_price_carries_its_actual_source_evidence(session, comparison_client):
    payload = _thermal(20)
    payload["components"][0]["purchase_evidence"] = {
        "supplier": "Synthetic supplier A", "grade": "Synthetic grade A", "quote_date": "2026-05-01",
    }
    first = _save(session, payload)
    alternative = deepcopy(payload)
    alternative["components"][0]["price_per_lb"] = 30
    alternative["components"][0]["purchase_evidence"]["supplier"] = "Synthetic supplier B"
    second = _save(session, alternative)
    data = comparison_client.post("/api/estimates/compare", json=_request(first, second)).json()
    evidence = data["estimates"][1]["common_conditions"]["purchase_evidence"]
    assert evidence[0]["evidence"]["supplier"] == "Synthetic supplier A"
    assert second.get_input()["components"][0]["purchase_evidence"]["supplier"] == "Synthetic supplier B"


def test_unknown_manual_grade_is_not_assumed_equal_to_known_library_material(session, comparison_client):
    session.add(MetalPrice(symbol="Ni", name="Nickel", price=17, unit="$/lb",
                          source="Synthetic test quote", basis="reference"))
    session.commit()
    payload = _thermal()
    payload["components"][0] = {"role": "active_metal", "material_key": "lit:usgs-nickel-cathode-2025", "wt_pct": 20}
    first = _save(session, payload)
    second = _save(session, _thermal(29))
    data = comparison_client.post("/api/estimates/compare", json=_request(first, second)).json()
    prices = {row["key"]: row["values"] for row in data["price_snapshot"]}
    assert prices["library:lit:usgs-nickel-cathode-2025"]["price_per_lb"] == 17
    assert prices["manual:ni:"]["price_per_lb"] == 29
    assert any("equivalent purchasing specifications" in warning for warning in data["warnings"])


def test_manual_ionomer_concentrations_are_not_silently_replaced(session, comparison_client):
    payload = _electrode()
    payload["electrode_input"].update(ionomer_to_catalyst_ratio=1, ionomer_price_per_ml=1,
                                     ionomer_solids_fraction=0.05)
    first = _save(session, payload)
    alternative = deepcopy(payload)
    alternative["electrode_input"]["ionomer_solids_fraction"] = 0.1
    second = _save(session, alternative)
    data = comparison_client.post("/api/estimates/compare", json=_request(first, second)).json()
    ionomers = [row for row in data["price_snapshot"] if row["key"].startswith("electrode:ionomer:")]
    assert len(ionomers) == 2
    one, two = [row["common_conditions"]["electrode_model"] for row in data["estimates"]]
    assert one["ionomer_dispersion_volume_ml"] == pytest.approx(two["ionomer_dispersion_volume_ml"] * 2, abs=1e-4)
    assert one["ionomer_cost_usd"] > two["ionomer_cost_usd"]
