"""The published illustrative cases must agree with the live calculator API."""

import json

import pytest

from backend.core.constants import LB_PER_KG
from scripts.reproduce_manufacturing_study import OUTPUT, independent_balance


def test_frozen_baseline_matches_hand_balance_and_calculator_api(client):
    data = json.loads((OUTPUT / "manufacturing_study.json").read_text(encoding="utf-8"))
    response = client.post("/api/calculate", json=data["request"])
    assert response.status_code == 200, response.text
    result = response.json()
    expected = independent_balance()["selling_price_usd_kg"]
    assert result["summary"]["estimated_price_per_kg"] == pytest.approx(expected, abs=.0001)
    assert result["manufacturing"]["trace"]["protocol_sha256"] == data["baseline"]["manufacturing"]["trace"]["protocol_sha256"]
    assert all(row["source_status"] != "unattributed" for row in result["manufacturing"]["trace"]["inputs"]
               if row["effect"] == "cost_input" and isinstance(row["value"], (float, int)))


def test_frozen_sensitivity_and_sampling_agree_with_api(client):
    data = json.loads((OUTPUT / "manufacturing_study.json").read_text(encoding="utf-8"))
    ranges = [{key: row[key] for key in ("path", "low", "high")} for row in data["sensitivity"]]
    response = client.post("/api/uncertainty/manufacturing-sensitivity", json={"calculation_input": data["request"], "manufacturing_ranges": ranges})
    assert response.status_code == 200, response.text
    for actual, expected in zip(response.json()["rows"], data["sensitivity"]):
        for end in ("low_usd_kg", "high_usd_kg"):
            assert actual[end] == expected[end]
    mc = data["monte_carlo"]
    ranges = [{key: row[key] for key in ("path", "low", "high")} for row in mc["variables"]]
    response = client.post("/api/uncertainty", json={"calculation_input": data["request"], "manufacturing_ranges": ranges,
        "uncertainties": {}, "n_simulations": mc["n_simulations"], "seed": mc["seed"]})
    assert response.status_code == 200, response.text
    actual = response.json()
    assert actual["n_failed"] == 0
    for key in ("mean", "p5", "p95"):
        assert actual[key] * LB_PER_KG == pytest.approx(mc[key + "_usd_kg"], abs=.0003)
    assert [row["count"] for row in actual["histogram"]] == [row["count"] for row in mc["histogram"]]
