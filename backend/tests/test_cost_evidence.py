"""Synthetic fixtures test matching rules; they are not empirical validation data."""

import json
from copy import deepcopy

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.core.cost_evidence import assess_actual_cost, summarize_observations
from backend.database import get_session
from backend.models.estimate import Estimate
from backend.routers.cost_evidence import router
from backend.schemas.cost_evidence import PurchaseEvidence


@pytest.fixture
def matching_records():
    request = {
        "catalyst_domain": "thermal", "order_size_tons": 2, "template_id": "test_route",
        "components": [
            {"name": "Pt", "wt_pct": 2, "price_per_lb": 100, "purchase_evidence": {
                "quote_date": "2026-05-04", "grade": "Synthetic test grade A",
            }},
            {"name": "C", "wt_pct": 98, "price_per_lb": 1, "purchase_evidence": {
                "quote_date": "2026-05-07", "grade": "Synthetic test grade B",
            }},
        ],
    }
    result = {
        "step_method": {
            "production_rate_ton_per_day": 1, "pre_margin_per_lb": 8,
            "step_details": [{"step": "mixer_slurry"}, {"step": "dryer_rotary_100_300C"}],
        },
        "summary": {"estimated_price_per_lb": 10, "net_cost_per_lb": 9},
        "costing_scope": {
            "status": "modeled_steps", "uncosted_operations": [], "dropped_steps": [],
            "costed_steps": [
                {"step": "mixer_slurry", "status": "costed"},
                {"step": "dryer_rotary_100_300C", "status": "costed"},
            ],
        },
    }
    actual = {
        "observed_price": 12.5, "currency": "USD", "price_unit": "lb",
        "observation_date": "2026-05-21", "price_period": "2026-05",
        "order_size_tons": 2, "production_rate_ton_per_day": 1, "template_id": "test_route",
        "components": [
            {"name": "Pt", "wt_pct": 2, "grade": "Synthetic test grade A"},
            {"name": "C", "wt_pct": 98, "grade": "Synthetic test grade B"},
        ],
        "steps": ["mixer_slurry", "dryer_rotary_100_300C"],
        "cost_boundary": "full_selling_price", "evidence_type": "invoice",
        "cost_scope_note": "Synthetic test: all modeled operations, overhead and selling margin; no recovery credit.",
        "production_conditions_note": "Synthetic test: 2 short tons at 1 short ton/day.",
        "source": "Synthetic unit-test invoice, not real evidence", "verified_by_user": True,
    }
    return request, result, actual


def test_eligible_synthetic_comparison_reports_signed_error(matching_records):
    assessment = assess_actual_cost(*matching_records)
    assert assessment["eligible"] is True
    assert assessment["signed_error_pct"] == -20
    assert assessment["absolute_percentage_error"] == 20
    assert assessment["verification"] == "user_supplied_not_independently_verified"


@pytest.mark.parametrize("changes,reason", [
    ({"verified_by_user": False}, "confirmed by the user"),
    ({"evidence_type": "supplier_quote"}, "quote"),
    ({"cost_boundary": "material_purchase"}, "not a full cost"),
    ({"price_period": "2026-04"}, "price month"),
    ({"observation_date": "2026-04-01"}, "date and stated price month"),
    ({"order_size_tons": 20}, "Production quantity"),
    ({"production_rate_ton_per_day": None}, "Effective production rate"),
    ({"steps": ["mixer_slurry"]}, "manufacturing steps"),
    ({"template_id": "different"}, "manufacturing template"),
    ({"currency": "EUR"}, "currency conversion"),
    ({"cost_scope_note": ""}, "inclusions"),
    ({"production_conditions_note": ""}, "production conditions"),
])
def test_incomparable_conditions_have_no_error(matching_records, changes, reason):
    request, result, observation = matching_records
    observation.update(changes)
    assessment = assess_actual_cost(request, result, observation)
    assert assessment["eligible"] is False
    assert assessment["signed_error_pct"] is None
    assert assessment["absolute_percentage_error"] is None
    assert any(reason in item for item in assessment["exclusion_reasons"])


def test_unknown_grade_and_component_month_block_comparison(matching_records):
    request, result, observation = matching_records
    request["components"][0].pop("purchase_evidence")
    assessment = assess_actual_cost(request, result, observation)
    assert not assessment["eligible"]
    assert any("Grade is unknown" in reason for reason in assessment["exclusion_reasons"])
    assert any("price month" in reason for reason in assessment["exclusion_reasons"])


def test_actual_composition_is_not_silently_normalized(matching_records):
    request, result, observation = matching_records
    observation["components"][1]["wt_pct"] = 95
    assessment = assess_actual_cost(request, result, observation)
    assert not assessment["eligible"]
    assert any("100 wt%" in reason for reason in assessment["exclusion_reasons"])


def test_step_multiplicity_is_preserved(matching_records):
    request, result, observation = matching_records
    observation["steps"].append("mixer_slurry")
    assert not assess_actual_cost(request, result, observation)["eligible"]


def test_uncosted_operation_prevents_full_cost_error(matching_records):
    request, result, observation = matching_records
    result["costing_scope"]["uncosted_operations"] = ["reduction_furnace"]
    assessment = assess_actual_cost(request, result, observation)
    assert not assessment["eligible"]
    assert any("omits manufacturing" in reason for reason in assessment["exclusion_reasons"])


def test_unknown_legacy_scope_prevents_full_cost_error(matching_records):
    request, result, observation = matching_records
    result.pop("costing_scope")
    assert not assess_actual_cost(request, result, observation)["eligible"]


@pytest.mark.parametrize("scope", [
    {"status": "unknown"},
    {"status": "modeled_steps", "costed_steps": []},
    {"status": "modeled_steps", "costed_steps": [{"step": "mixer_slurry", "status": "costed"}]},
])
def test_unknown_or_inconsistent_scope_is_not_treated_as_full_cost(matching_records, scope):
    request, result, observation = matching_records
    result["costing_scope"] = scope
    assert not assess_actual_cost(request, result, observation)["eligible"]


def test_library_resolution_overrules_misleading_request_name(matching_records):
    request, result, observation = matching_records
    request["components"][0]["material_key"] = "test_nickel"
    result["materials"] = {"components": [{"name": "Ni"}, {"name": "C"}]}
    result["resolved_materials"] = [{
        "material_key": "test_nickel", "used_for": "component:active_metal",
        "pricing_basis": "reference_monthly:Ni:2026-05",
    }]
    assessment = assess_actual_cost(request, result, observation)
    assert not assessment["eligible"]
    assert any("composition" in reason for reason in assessment["exclusion_reasons"])
    observation["components"][0]["name"] = "Ni"
    assert assess_actual_cost(request, result, observation)["eligible"]


def test_missing_resolved_library_name_never_uses_request_alias(matching_records):
    request, result, observation = matching_records
    request["components"][0]["material_key"] = "test_nickel"
    assert not assess_actual_cost(request, result, observation)["eligible"]


@pytest.mark.parametrize("field", ["omitted_template_steps", "dropped_steps"])
def test_scale_or_template_omissions_prevent_full_cost_error(matching_records, field):
    request, result, observation = matching_records
    result["costing_scope"][field] = ["unmodeled_operation"]
    assert not assess_actual_cost(request, result, observation)["eligible"]


def test_recipe_without_observed_consumption_is_excluded(matching_records):
    request, result, observation = matching_records
    request["components"][0]["recipe_consumption"] = {"precursor_name": "Synthetic precursor"}
    assert not assess_actual_cost(request, result, observation)["eligible"]
    request["components"][0].pop("recipe_consumption")
    request["consumables"] = [{"name": "Synthetic solvent"}]
    assert not assess_actual_cost(request, result, observation)["eligible"]


def test_boundary_selects_margin_and_recovery_without_mixing(matching_records):
    request, result, observation = matching_records
    observation["cost_boundary"] = "full_manufacturing_cost"
    assert assess_actual_cost(request, result, observation)["predicted_price"] == 8
    observation["cost_boundary"] = "full_net_after_recovery"
    assert assess_actual_cost(request, result, observation)["predicted_price"] == 9


def test_kg_comparison_uses_mass_conversion(matching_records):
    request, result, observation = matching_records
    observation["price_unit"] = "kg"
    observation["observed_price"] = 10 * 2.20462
    assessment = assess_actual_cost(request, result, observation)
    assert assessment["eligible"]
    assert abs(assessment["signed_error_pct"]) < 0.001


def test_mape_is_null_without_eligible_observations(matching_records):
    request, result, observation = matching_records
    assert summarize_observations(request, result)["mape_pct"] is None
    observation["evidence_type"] = "supplier_quote"
    result["local_cost_observations"] = [{"id": "synthetic", "observation": observation}]
    summary = summarize_observations(request, result)
    assert summary["eligible_count"] == 0
    assert summary["mape_pct"] is None


def test_local_observation_round_trip_preserves_snapshot(session, matching_records):
    request, result, observation = matching_records
    record = Estimate(name="Synthetic evidence fixture", input_json=json.dumps(request), result_json=json.dumps(result))
    session.add(record)
    session.commit()
    session.refresh(record)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        response = client.post(f"/api/estimates/{record.id}/observations", json=observation)
        assert response.status_code == 201
        saved = response.json()
        assert saved["eligible_count"] == 1
        assert saved["mape_pct"] == 20
        assert client.get(f"/api/estimates/{record.id}/observations").json() == saved
        assert client.get("/api/estimates/99999/observations").status_code == 404
    session.refresh(record)
    assert record.get_input() == request
    stored_result = deepcopy(record.get_result())
    stored_result.pop("local_cost_observations")
    assert stored_result == result


def test_purchase_evidence_is_optional_and_rejects_invalid_numbers_and_dates():
    assert PurchaseEvidence().model_dump()["supplier"] is None
    assert PurchaseEvidence(quote_date="2026-05-01").quote_date == "2026-05-01"
    for payload in ({"quantity": -1}, {"quantity": float("nan")}, {"quote_date": "2026-02-31"}):
        with pytest.raises(ValidationError):
            PurchaseEvidence(**payload)


def test_purchase_metadata_survives_real_calculate_and_save_without_changing_cost(client):
    payload = {
        "components": [
            {"role": "active_metal", "name": "Pt", "wt_pct": 2, "price_per_lb": 100},
            {"role": "support", "name": "C", "wt_pct": 98, "price_per_lb": 1},
        ],
        "steps": ["mixer_slurry", "dryer_rotary_100_300C"], "order_size_tons": 2,
    }
    original = client.post("/api/calculate", json=payload)
    assert original.status_code == 200
    evidence = {
        "supplier": "Synthetic test supplier", "quote_date": "2026-05-04", "quantity": 5,
        "quantity_unit": "kg", "grade": "Synthetic test grade", "cost_boundary": "Material only",
        "reference": "Synthetic local invoice", "notes": "Not an empirical data point",
    }
    payload["components"][0]["purchase_evidence"] = evidence
    saved = client.post("/api/calculate/save?name=Synthetic%20purchase%20evidence", json=payload)
    assert saved.status_code == 200
    assert saved.json()["result"]["summary"] == original.json()["summary"]
    estimate_id = saved.json()["id"]
    detail = client.get(f"/api/estimates/{estimate_id}").json()
    assert detail["input"]["components"][0]["purchase_evidence"] == evidence
    response = client.get(f"/api/estimates/{estimate_id}/observations")
    assert response.status_code == 200
    assert response.json()["eligible_count"] == 0
    assert response.json()["mape_pct"] is None
