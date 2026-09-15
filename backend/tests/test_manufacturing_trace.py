"""Input provenance and linked operating-time checks using synthetic data."""

from copy import deepcopy

import pytest

from backend.core.cost_engine import estimate_catalyst_cost
from backend.core.manufacturing import evaluate_protocol
from backend.schemas.manufacturing import ManufacturingProtocol
from backend.tests.test_manufacturing_protocol import payload, protocol


def run(value):
    return evaluate_protocol(ManufacturingProtocol.model_validate(value))


def gas(basis="operation"):
    return {"name": "N2", "flow_l_per_min": 1, "duration_basis": basis,
            "price_usd_per_m3": 10, "volume_basis": "Flow and price at 20 C, 1 atm"}


def test_linked_gas_time_reaches_final_selling_price():
    p = protocol()
    p["operations"][0]["gases"] = [gas()]
    base = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    p["operations"][0]["temperature_profile"][-1]["hold_h"] += 1
    changed = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    # One extra hour: 0.1 electricity + 3 equipment + 0.6 gas USD/batch.
    assert changed["manufacturing"]["batch_processing_cost_usd"] - base["manufacturing"]["batch_processing_cost_usd"] == pytest.approx(3.7)
    assert changed["step_method"]["estimated_price_per_kg"] - base["step_method"]["estimated_price_per_kg"] == pytest.approx(3.7 / .03 * 1.05 * 1.05, abs=.0001)


def test_hold_link_excludes_ramps_and_extra_time_and_counts_repetitions():
    p = protocol()
    p["operations"][0].update(gases=[gas("holds")], repetitions=2)
    r = run(p)
    assert r["operations"][0]["gases"][0]["duration_h"] == 12
    assert r["operations"][0]["gases"][0]["volume_m3"] == pytest.approx(.72)
    assert r["operations"][0]["costs_usd"]["gas"] == pytest.approx(7.2)


def test_linked_gas_rejects_a_second_independent_duration():
    p = protocol()
    p["operations"][0]["gases"] = [{**gas(), "duration_h": 2}]
    with pytest.raises(ValueError, match="linked"):
        run(p)


def test_unknown_operation_time_cannot_become_known_linked_gas_cost():
    p = protocol()
    p["operations"][0].update(gases=[gas()], additional_time_h=None)
    with pytest.raises(ValueError, match="Complete batch"):
        run(p)
    p["mode"] = "record_only"
    result = run(p)
    assert result["operations"][0]["gases"][0]["volume_m3"] is None
    assert result["operations"][0]["gases"][0]["duration_h"] is None


def test_input_source_snapshot_detects_user_edits_without_changing_cost():
    p = protocol()
    segment = p["operations"][0]["temperature_profile"][-1]
    segment["input_evidence"] = {"hold_h": {"kind": "assumption", "citation": "Synthetic five-hour scenario",
                                               "locator": "Test fixture", "recorded_value": 5}}
    original = deepcopy(p)
    result = run(p)
    row = next(r for r in result["trace"]["inputs"] if r["path"] == "operations.0.temperature_profile.2.hold_h")
    assert row["source_status"] == "matches_record"
    assert row["unit"] == "h" and row["value"] == 5
    assert result["batch_processing_cost_usd"] == pytest.approx(run(protocol())["batch_processing_cost_usd"])
    assert p == original
    segment["hold_h"] = 6
    changed = run(p)
    row = next(r for r in changed["trace"]["inputs"] if r["path"] == "operations.0.temperature_profile.2.hold_h")
    assert row["source_status"] == "modified"
    assert row["evidence"]["recorded_value"] == 5
    assert changed["trace"]["protocol_sha256"] != result["trace"]["protocol_sha256"]


def test_context_conditions_are_visible_but_not_false_cost_dependencies():
    p = protocol()
    p["operations"][0].update(ph=9, stirring_rpm=400, pressure_bar_abs=3)
    r = run(p)
    rows = {row["path"]: row for row in r["trace"]["inputs"]}
    for field in ("ph", "stirring_rpm", "pressure_bar_abs"):
        assert rows[f"operations.0.{field}"]["effect"] == "record_only"
    assert r["batch_processing_cost_usd"] == pytest.approx(run(protocol())["batch_processing_cost_usd"])
    assert r["trace"]["coverage"]["unattributed"] > 0


def test_trace_cost_ledger_reconciles_to_price_and_incomplete_cost_is_not_zero():
    result = estimate_catalyst_cost(**payload(), manufacturing_protocol=protocol())
    ledger = result["manufacturing"]["trace"]["cost_ledger"]
    assert sum(row["value"] for row in ledger) == pytest.approx(result["step_method"]["estimated_price_per_kg"], abs=.0001)
    assert {r["category"] for r in ledger} == {"materials", "electricity", "equipment", "labor", "gas", "other", "ga", "sard", "margin"}
    p = {"mode": "record_only", "operations": [{"name": "Unknown drying"}]}
    trace = run(p)["trace"]
    assert all(row["value"] is None for row in trace["calculations"] if row["unit"] == "USD")


def test_source_pointer_must_name_an_existing_input():
    p = protocol()
    p["input_evidence"] = {"invented_cost": {"kind": "assumption", "citation": "fixture", "recorded_value": 1}}
    with pytest.raises(ValueError, match="input_evidence"):
        run(p)


def test_provenance_survives_api_save_load(client):
    p = protocol()
    p["input_evidence"] = {"finished_batch_mass_kg": {"kind": "measured", "citation": "Synthetic balance record",
                                                    "locator": "Fixture only, not a real measurement", "recorded_value": .03}}
    saved = client.post("/api/calculate/save?name=synthetic-provenance-test", json={**payload(), "manufacturing_protocol": p})
    assert saved.status_code == 200, saved.text
    loaded = client.get(f"/api/estimates/{saved.json()['id']}").json()
    assert loaded["input"]["manufacturing_protocol"]["input_evidence"] == ManufacturingProtocol.model_validate(p).model_dump()["input_evidence"]
    assert loaded["result"]["manufacturing"]["trace"]["protocol_sha256"]
