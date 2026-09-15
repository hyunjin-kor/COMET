"""Synthetic aliquot balances: allocated catalyst cost differs from batch expenditure."""

from copy import deepcopy

import pytest

from backend.core.cost_engine import estimate_catalyst_cost
from backend.core.manufacturing import evaluate_protocol
from backend.schemas.manufacturing import ManufacturingProtocol
from backend.tests.test_manufacturing_protocol import payload


def intermediate_protocol():
    # Explicit synthetic assumptions. No claim of measured catalyst costs or yield.
    upstream = dict(name="Synthetic support batch", intermediate_batch_id="support", duration_h=2,
        additional_time_h=0, average_power_kw=2, equipment_usd_h=3, attended_labor_h=.5, other_cost_usd=1,
        gases=[dict(name="Synthetic gas", flow_l_per_min=1, duration_basis="operation",
                    price_usd_per_m3=10, volume_basis="25 C, 1 bar for both flow and price")],
        purchases=[dict(name="Synthetic precursor", quantity=10, unit="g", price_usd_per_unit=2)])
    final = dict(name="Final impregnation", duration_h=1, additional_time_h=0,
        average_power_kw=1, equipment_usd_h=2, attended_labor_h=.25, other_cost_usd=0,
        purchases=[dict(name="Synthetic active precursor", quantity=1, unit="g", price_usd_per_unit=3)])
    return dict(mode="batch_cost", materials_basis="purchases", finished_batch_mass_kg=.002,
        electricity_usd_kwh=.1, labor_usd_h=10, source_note="Synthetic intermediate allocation fixture",
        intermediate_batches=[dict(id="support", name="Support", produced_mass_kg=.01, used_mass_kg=.001,
            input_evidence={"produced_mass_kg": dict(kind="assumption", citation="Synthetic recovery", recorded_value=.01)})],
        operations=[upstream, final])


def test_all_charges_are_allocated_once_and_whole_expenditure_is_retained():
    p = intermediate_protocol()
    result = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    report = result["manufacturing"]
    # Upstream: electricity .4 + equipment 6 + labor 5 + gas 1.2 + other 1 = 13.6.
    # Final: electricity .1 + equipment 2 + labor 2.5 = 4.6.
    assert report["operations"][0]["incurred_cost_usd"] == pytest.approx(13.6)
    assert report["operations"][0]["cost_usd"] == pytest.approx(1.36)
    assert report["operations"][0]["gases"][0]["volume_m3"] == pytest.approx(.12)
    assert report["batch_processing_cost_usd"] == pytest.approx(5.96)
    assert report["batch_materials_cost_usd"] == 5  # 20*.1 + 3
    assert report["purchases"][0]["incurred_cost_usd"] == 20
    assert report["purchases"][0]["quantity"] == 10
    assert report["electricity_kwh_per_kg"] == pytest.approx((4*.1 + 1)/.002)
    assert report["serial_operation_hours"] == 3
    assert report["allocated_operation_hours"] == pytest.approx(1.2)
    expected = (5 + 5.96) / .002 * 1.05**2
    assert result["summary"]["estimated_price_per_kg"] == pytest.approx(expected, abs=.0001)
    calc = {row["id"]: row for row in report["trace"]["calculations"]}
    assert calc["intermediate_batches.0.allocation_fraction"]["value"] == .1
    assert "intermediate_batches.0.allocation_fraction" in calc["operations.0.gas"]["input_paths"]
    assert calc["total.selling_price"]["value"] == pytest.approx(expected)
    assert report["trace"]["cost_ledger"]
    assert intermediate_protocol() == p


def test_recovered_mass_and_used_mass_affect_only_allocated_upstream_charges():
    p = intermediate_protocol()
    p["intermediate_batches"][0]["produced_mass_kg"] = .02
    r = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert r["batch_materials_cost_usd"] == 4
    assert r["batch_processing_cost_usd"] == pytest.approx(.68 + 4.6)
    p["intermediate_batches"][0]["used_mass_kg"] *= 2
    r = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert r["batch_materials_cost_usd"] == 5
    p["operations"][0]["repetitions"] = 2
    # Recovery input refers to the whole declared intermediate batch, including repetitions.
    r = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert r["batch_materials_cost_usd"] == 7
    assert r["batch_processing_cost_usd"] == pytest.approx(2.72 + 4.6)


def test_whole_batch_charge_does_not_assume_reusable_inventory_or_an_unknown_yield():
    p = intermediate_protocol()
    p["intermediate_batches"][0].update(allocation_basis="whole_batch", produced_mass_kg=None)
    r = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert r["batch_materials_cost_usd"] == 23
    assert r["batch_processing_cost_usd"] == pytest.approx(13.6 + 4.6)
    assert r["allocated_operation_hours"] == 3
    row = next(x for x in r["trace"]["inputs"] if x["path"] == "intermediate_batches.0.produced_mass_kg")
    assert row["value"] is None and row["effect"] == "record_only"


def nested_protocol():
    p = intermediate_protocol()
    p["intermediate_batches"][0]["destination_batch_id"] = "pellets"
    p["intermediate_batches"].append(dict(id="pellets", name="Pellets", produced_mass_kg=.02, used_mass_kg=.01))
    p["operations"].insert(1, dict(name="Pellet forming", intermediate_batch_id="pellets", duration_h=1,
        additional_time_h=0, average_power_kw=0, equipment_usd_h=0, attended_labor_h=0, other_cost_usd=2))
    return p


def test_successive_aliquots_multiply_fractions_without_repeating_upstream_charges():
    p = nested_protocol()
    result = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    r = result["manufacturing"]
    assert r["intermediate_batches"][0]["transfer_fraction"] == .1
    assert r["intermediate_batches"][0]["allocation_fraction"] == .05
    assert r["batch_materials_cost_usd"] == 4  # 20*.1*.5 + 3
    assert r["batch_processing_cost_usd"] == pytest.approx(13.6*.1*.5 + 2*.5 + 4.6)
    assert result["summary"]["estimated_price_per_kg"] == pytest.approx(5666.85, abs=.0001)
    assert r["serial_operation_hours"] == 4
    assert r["allocated_operation_hours"] == pytest.approx(2*.05 + 1*.5 + 1)
    calc = {row["id"]: row for row in r["trace"]["calculations"]}
    assert "intermediate_batches.1.allocation_fraction" in calc["intermediate_batches.0.allocation_fraction"]["input_paths"]
    p["intermediate_batches"].reverse()
    reversed_order = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert reversed_order["batch_processing_cost_usd"] == r["batch_processing_cost_usd"]


@pytest.mark.parametrize("destination", ["support", "missing", "cycle"])
def test_invalid_transfer_destinations_and_cycles_are_rejected(destination):
    p = nested_protocol()
    if destination == "cycle":
        p["intermediate_batches"][1]["destination_batch_id"] = "support"
    else:
        p["intermediate_batches"][0]["destination_batch_id"] = destination
    with pytest.raises(ValueError):
        ManufacturingProtocol.model_validate(p)


def test_unknown_downstream_recovery_cannot_leave_an_upstream_cost_looking_complete():
    p = nested_protocol()
    p["mode"] = "record_only"
    p["intermediate_batches"][1]["produced_mass_kg"] = None
    r = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert all(row["allocation_fraction"] is None for row in r["intermediate_batches"])
    assert r["operations"][0]["cost_usd"] is None
    assert r["batch_materials_cost_usd"] is None


@pytest.mark.parametrize("field", ["produced_mass_kg", "used_mass_kg"])
def test_unknown_intermediate_mass_blocks_cost_and_remains_unknown_in_record_mode(field):
    p = intermediate_protocol()
    p["intermediate_batches"][0][field] = None
    with pytest.raises(ValueError, match="intermediate mass"):
        estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    p["mode"] = "record_only"
    r = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert not r["complete"]
    assert r["batch_materials_cost_usd"] is None
    assert r["batch_processing_cost_usd"] is None
    assert r["intermediate_batches"][0]["allocation_fraction"] is None
    assert r["operations"][0]["cost_usd"] is None


@pytest.mark.parametrize("error", ["too_much", "duplicate", "undefined", "unassigned", "no_final", "zero"])
def test_ambiguous_batch_boundaries_are_rejected(error):
    p = intermediate_protocol()
    if error == "too_much":
        p["intermediate_batches"][0]["used_mass_kg"] = 1
    elif error == "duplicate":
        p["intermediate_batches"].append(deepcopy(p["intermediate_batches"][0]))
    elif error == "undefined":
        p["operations"][0]["intermediate_batch_id"] = "missing"
    elif error == "unassigned":
        p["operations"][0]["intermediate_batch_id"] = ""
    elif error == "no_final":
        p["operations"][1]["intermediate_batch_id"] = "support"
    else:
        p["intermediate_batches"][0]["produced_mass_kg"] = 0
    with pytest.raises(ValueError):
        ManufacturingProtocol.model_validate(p)


@pytest.mark.parametrize("make_protocol", [intermediate_protocol, nested_protocol])
def test_api_save_reload_retains_allocation_source_and_modified_recovery(client, make_protocol):
    p = make_protocol()
    p["intermediate_batches"][0]["produced_mass_kg"] = .02
    saved = client.post("/api/calculate/save?name=synthetic-aliquot", json={**payload(), "manufacturing_protocol": p})
    assert saved.status_code == 200, saved.text
    loaded = client.get(f"/api/estimates/{saved.json()['id']}").json()
    result = loaded["result"]["manufacturing"]
    rows = {row["path"]: row for row in result["trace"]["inputs"]}
    assert rows["intermediate_batches.0.produced_mass_kg"]["source_status"] == "modified"
    assert rows["intermediate_batches.0.produced_mass_kg"]["evidence"]["recorded_value"] == .01
    recalculated = client.post("/api/calculate", json=loaded["input"])
    assert recalculated.status_code == 200, recalculated.text
    assert recalculated.json()["manufacturing"] == result
