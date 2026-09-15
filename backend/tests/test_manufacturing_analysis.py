"""Traceable perturbations use absolute units and the same batch cost calculation."""

from copy import deepcopy

import pytest

from backend.tests.test_manufacturing_intermediates import nested_protocol
from backend.tests.test_manufacturing_protocol import payload


def case():
    return {**payload(), "manufacturing_protocol": nested_protocol()}


def test_input_listing_excludes_record_only_and_inactive_values(client):
    data = case()
    data["manufacturing_protocol"]["operations"][0]["ph"] = 7
    r = client.post("/api/uncertainty/manufacturing-inputs", json=data)
    assert r.status_code == 200, r.text
    options = {v["path"]: v for v in r.json()["variables"]}
    assert "operations.0.ph" not in options
    assert "operations.0.gases.0.duration_h" not in options
    assert options["intermediate_batches.0.produced_mass_kg"]["evidence"]["recorded_value"] == .01
    assert options["operations.0.duration_h"]["unit"] == "h"


def test_absolute_duration_sensitivity_matches_independent_batch_arithmetic(client):
    r = client.post("/api/uncertainty/manufacturing-sensitivity", json={"calculation_input": case(),
        "manufacturing_ranges": [{"path": "operations.0.duration_h", "low": 2, "high": 3}]})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["baseline_usd_kg"] == pytest.approx(5666.85)
    # Extra upstream hour: 2 kW*.1 + equipment3 + gas1 L/min*60/1000*10 =3.8 USD.
    # Effective upstream allocation .05; dry product .002 kg; two 5% overheads.
    assert d["rows"][0]["high_usd_kg"] - d["rows"][0]["low_usd_kg"] == pytest.approx(3.8*.05/.002*1.05**2)
    assert d["rows"][0]["low_error"] is None


def test_seeded_manufacturing_monte_carlo_preserves_input_and_reports_bounds(client):
    original = case()
    before = deepcopy(original)
    args = {"calculation_input": original, "uncertainties": {}, "n_simulations": 100, "seed": 15,
            "manufacturing_ranges": [{"path": "finished_batch_mass_kg", "low": .002, "high": .004}]}
    first = client.post("/api/uncertainty", json=args)
    assert first.status_code == 200, first.text
    d = first.json()
    assert d == client.post("/api/uncertainty", json=args).json()
    assert original == before
    assert d["baseline_price_per_kg"] == pytest.approx(5666.85)
    assert d["n_failed"] == 0 and d["std"] > 0
    assert sum(bin["count"] for bin in d["histogram"]) == 100
    assert sum(bin["percent"] for bin in d["histogram"]) == pytest.approx(100)
    widths = [bin["high"] - bin["low"] for bin in d["histogram"]]
    assert max(widths) == pytest.approx(min(widths))
    assert d["manufacturing_analysis"]["variables"][0]["low"] == .002
    assert "fixed_manufacturing_assumptions" not in d


@pytest.mark.parametrize("change", ["missing", "record_only", "inactive", "duplicate", "reversed", "fractional_count"])
def test_invalid_or_noncausal_variations_are_rejected(client, change):
    args = {"calculation_input": case(), "uncertainties": {}, "n_simulations": 100,
            "manufacturing_ranges": [{"path": "operations.0.duration_h", "low": 1, "high": 2}]}
    row = args["manufacturing_ranges"][0]
    if change == "missing":
        row["path"] = "operations.99.duration_h"
    elif change == "record_only":
        args["calculation_input"]["manufacturing_protocol"]["mode"] = "record_only"
    elif change == "inactive":
        row["path"] = "operations.0.gases.0.duration_h"
    elif change == "duplicate":
        args["manufacturing_ranges"].append(dict(row))
    elif change == "reversed":
        row.update(low=3, high=2)
    else:
        row.update(path="operations.0.repetitions", low=1.5, high=2)
    r = client.post("/api/uncertainty", json=args)
    assert r.status_code == 422, r.text


def test_infeasible_mass_samples_are_counted_instead_of_clamped(client):
    args = {"calculation_input": case(), "uncertainties": {}, "n_simulations": 100, "seed": 15,
            "manufacturing_ranges": [{"path": "intermediate_batches.0.used_mass_kg", "low": .005, "high": .02}]}
    r = client.post("/api/uncertainty", json=args)
    assert r.status_code == 200, r.text
    d = r.json()
    assert 0 < d["n_failed"] < 100
    assert sum(d["failure_reasons"].values()) == d["n_failed"]
    assert d["n_failed"] + d["n_successful"] == 100


def test_sensitivity_reports_invalid_endpoint_without_losing_valid_endpoint(client):
    r = client.post("/api/uncertainty/manufacturing-sensitivity", json={"calculation_input": case(),
        "manufacturing_ranges": [{"path": "intermediate_batches.0.used_mass_kg", "low": .005, "high": .02}]})
    assert r.status_code == 200, r.text
    row = r.json()["rows"][0]
    assert row["low_usd_kg"] > 0
    assert row["high_usd_kg"] is None
    assert "exceed recovered mass" in row["high_error"]


def test_no_variation_histogram_does_not_invent_a_cost_range(client):
    r = client.post("/api/uncertainty", json={"calculation_input": case(), "uncertainties": {}, "n_simulations": 100, "seed": 15})
    assert r.status_code == 200, r.text
    bins = r.json()["histogram"]
    assert len(bins) == 1 and bins[0]["count"] == 100
    assert bins[0]["low"] == bins[0]["high"]
