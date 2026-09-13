"""Observed-date replay, score controls, and an independent cost-effect check."""

from copy import deepcopy

import pytest

from scripts.analyze_price_crossover_cases import bisect_bracket
from scripts.fetch_crossover_prices import parse_daily_csv
from scripts.run_price_crossovers import (
    ROOT,
    continuous_scores,
    cost_values,
    daily_states,
    pair_crossings,
    read,
    strict_winner,
    transitions,
)


def test_daily_intersection_excludes_missing_quotes_and_preserves_annotations():
    baseline = {s: {"price": 5, "unit": "$/lb", "source": "fixed annotations"} for s in ("Ni", "Co", "Fe")}
    snapshot = {"series": {
        "Ni": {"unit": "$/lb", "cadence": "daily", "points": [{"date": "2026-01-02", "price": 7}, {"date": "2026-01-05", "price": 8}]},
        "Co": {"unit": "$/lb", "cadence": "daily", "points": [{"date": "2026-01-05", "price": 20}]}}}
    states, varying = daily_states(snapshot, baseline)
    assert varying == ["Co", "Ni"]
    assert [day for day, _ in states] == ["2026-01-05"]
    assert states[0][1]["Ni"] == {"price": 8, "unit": "$/lb", "source": "fixed annotations"}
    assert states[0][1]["Fe"] == baseline["Fe"]
    assert baseline["Ni"]["price"] == 5
    for key, value in [("cadence", "monthly_average"), ("unit", "$/troy_oz")]:
        changed = deepcopy(snapshot)
        changed["series"]["Ni"][key] = value
        with pytest.raises(ValueError):
            daily_states(changed, baseline)
    snapshot["series"]["Co"]["points"] *= 2
    with pytest.raises(ValueError, match="duplicate"):
        daily_states(snapshot, baseline)


def test_daily_export_rejects_ambiguous_region_and_metal_header_order():
    raw = "Daily PGM prices for New York\nDate,Platinum,Palladium,Rhodium,Iridium,Ruthenium\n11-Sep-2026,1815,1330,9725,7850,1675\n"
    assert parse_daily_csv(raw)["Pt"] == [{"date": "2026-09-11", "price": 1815.0}]
    assert parse_daily_csv(raw)["Ru"][0]["price"] == 1675
    with pytest.raises(ValueError):
        parse_daily_csv(raw.replace("New York", "London"))
    with pytest.raises(ValueError, match="column"):
        parse_daily_csv(raw.replace("Platinum,Palladium", "Palladium,Platinum"))


def test_crossings_require_opposite_cost_signs_and_bracket_ties():
    rows = [{"date": str(i), "costs": {"a": a, "b": 10}} for i, a in enumerate([9, 10, 9, 10, 11])]
    pair = pair_crossings(rows, ["a", "b"], 0.001)
    assert pair[0]["events"] == [{"from": "2", "to": "4"}]
    assert pair[0]["exceeds_one_percent_both_sides"]
    assert not pair_crossings(rows[:4], ["a", "b"], 0.001)
    assert strict_winner({"a": 10, "b": 10.0001}, lower=True, tolerance=0.0002) is None
    assert transitions([{"date": "1", "winner": "a"}, {"date": "2", "winner": None},
                        {"date": "3", "winner": "b"}], "winner") == [{"from": "1", "to": "3", "before": "a", "after": "b"}]


def test_unrounded_fixed_scores_do_not_import_dynamic_evidence_or_cost_tie_breaks():
    ref = [{"slug": s, "summary": {"economics_basis_value": c, "economics_basis_unit": "$/lb"},
            "scores": {"evidence": e, "route": 50, "performance": 50}}
           for s, c, e in [("a", 10, 80), ("b", 20, 40), ("c", 30, 50)]]
    weights = {"economics": 0.5, "evidence": 0.5, "route": 0, "performance": 0}
    scores = continuous_scores({"a": 22.0001, "b": 10, "c": 30}, ref, weights)
    assert scores["a"] == pytest.approx(59.99975)
    assert scores["b"] == 70
    assert strict_winner(scores) == "b"
    ref[-1]["summary"]["economics_basis_unit"] = "$/cm2"
    with pytest.raises(ValueError, match="Mixed"):
        cost_values(ref)


def test_ammonia_cobalt_effect_matches_independent_adopted_method_arithmetic():
    mechanisms = read(ROOT / "docs/paper/price-crossovers-2026-09-13/crossover_mechanisms.json")
    case = next(c for c in mechanisms["cases"] if c["family"] == "ammonia-cracking")
    effect = case["metal_effects"]["Co"]
    # 5 wt% Co, 1.10 precursor factor; G&A then SARD, both 5%;
    # adopted selling-price margin correlation for the fixed 20 short-ton order.
    margin = 39.192 * 20 ** -0.23360 / 100
    independent = 0.05 * 1.10 * (19.5706 - 15.1872) * 1.05**2 / (1 - margin)
    assert effect["gap_change_usd_lb"] == pytest.approx(independent, abs=0.0002)
    assert case["gap_before"] < 0 < case["gap_after"]
    assert case["costs_before"]["co-mgo-la2o3"] == min(case["costs_before"].values())
    assert case["costs_after"]["ni-alumina-baseline"] == min(case["costs_after"].values())


def test_threshold_bracket_and_study_coverage():
    bracket = bisect_bracket(lambda x: 2 * x - 7, 1, 10)
    assert bracket["low"] <= 3.5 <= bracket["high"]
    assert bracket["gap_low"] <= 0 <= bracket["gap_high"]
    with pytest.raises(ValueError, match="not bracketed"):
        bisect_bracket(lambda x: x + 1, 1, 10)
    study = read(ROOT / "docs/paper/price-crossovers-2026-09-13/price_crossovers.json")
    assert len(study["families"]) == 30
    assert sum(len(f["candidates"]) for f in study["families"]) == 116
    assert study["monthly_ledgers_verified"] == 30 * 89
    for family in study["families"]:
        for period in family["periods"].values():
            assert all(set(row["costs"]) == set(family["candidates"]) for row in period["records"])
