"""Independent, hand-computable checks for paper/app decision consistency."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from backend.core.decision_engine import evaluate_benchmark_family
from scripts.build_submission_manuscript import reference_snapshot_equivalent
from scripts.run_all_families import DIMS, rank
from scripts.run_controlled_cases import _rank
from scripts.run_decision_robustness import (
    historical_states,
    joint_grid,
    removal_audit,
    rubric_audit,
)


def candidate(slug, economics, evidence, cost, *, area_cost=None, route=0, performance=0):
    return {
        "slug": slug,
        "scores": dict(economics=economics, evidence=evidence, route=route,
                       performance=performance, total=0),
        "summary": {"landed_cost_per_lb": cost,
                    "economics_basis_value": cost if area_cost is None else area_cost,
                    "economics_basis_unit": "$/lb" if area_cost is None else "$/cm2"},
    }


def test_paper_uses_displayed_composite_before_cost_tie():
    # Both scores round to 50.0; lower cost must win despite 0.01 raw deficit.
    rows = [candidate("raw-score-leader", 50.04, 0, 2),
            candidate("lower-cost", 50.03, 0, 1)]
    before = deepcopy(rows)
    assert rank(rows, dict(economics=1, evidence=0, route=0, performance=0))[0] == "lower-cost"
    assert rows == before


def test_electrode_tie_uses_area_cost_not_powder_price():
    rows = [candidate("cheap-powder", 50, 50, 1, area_cost=2),
            candidate("cheap-area", 50, 50, 100, area_cost=1)]
    assert _rank(rows)[0]["slug"] == "cheap-area"
    assert rank(rows, dict(economics=1, evidence=0, route=0, performance=0))[0] == "cheap-area"


def test_joint_enumeration_counts_and_regret_hand_oracle():
    rows = [candidate("a", 100, 0, 1), candidate("b", 0, 100, 2)]
    grid = [dict(economics=1, evidence=0, route=0, performance=0),
            dict(economics=0, evidence=1, route=0, performance=0)]
    result = joint_grid([rows, rows], grid)
    assert result["scenarios"] == 4
    for c in result["candidates"].values():
        assert c["rank_counts"] == [2, 2]
        assert c["first_rank_share_pct"] == 50
        assert c["mean_rank"] == 1.5
        assert c["mean_regret_score_points"] == 50
        assert c["worst_regret_score_points"] == 100
    assert result == joint_grid([list(reversed(rows))] * 2, grid)


def test_removing_loser_can_change_minmax_normalization():
    rows = [candidate("a", 100, 0, 1), candidate("b", 90, 20, 2), candidate("c", 0, 0, 11)]
    audit = removal_audit(rows, dict(economics=0.5, evidence=0.5, route=0, performance=0))
    removed_c = next(r for r in audit if r["removed"] == "c")
    assert removed_c["fixed_scale_winner"] == "b"
    assert removed_c["renormalized_winner"] == "a"
    assert removed_c["winner_changed"]
    assert rows[1]["scores"]["economics"] == 90


def test_removal_audit_after_ledger_totals_use_recomputed_economics():
    rows = [candidate("a", 100, 0, 1), candidate("b", 90, 20, 2), candidate("c", 0, 0, 11)]
    weights = dict(economics=0.5, evidence=0.5, route=0, performance=0)
    for row in removal_audit(rows, weights):
        for entry in row["after"]:
            assert entry["scores"]["total"] == round(sum(entry["scores"][d] * weights[d] for d in DIMS), 1)


def test_rubric_bounds_and_cost_tie_are_exact():
    rows = [candidate("a", 0, 0, 1, route=60, performance=60),
            candidate("b", 0, 0, 2, route=50, performance=50)]
    weights = dict(economics=0, evidence=0, route=0.5, performance=0.5)
    assert rubric_audit(rows, weights, 2)["survives_all_box_perturbations"]
    assert rubric_audit(rows, weights, 5)["survives_all_box_perturbations"]
    assert not rubric_audit(rows, weights, 6)["survives_all_box_perturbations"]


def test_history_intersection_holds_annotations_and_fixed_prices():
    baseline = {"Ni": dict(price=8, unit="$/kg", source="reference", reference_url="retained"),
                "Cu": dict(price=9, unit="$/kg"), "support": dict(price=7)}
    history = {"basis_month": "2026-02", "cadence": "monthly_average", "series": {
        "HS123456": {"cadence": "monthly_unit_value", "points": []},
        "Ni": {"unit": "$/kg", "points": [dict(date="2026-01-31", price=1), dict(date="2026-02-28", price=2)]},
        "Cu": {"unit": "$/kg", "points": [dict(date="2026-02-28", price=3), dict(date="2026-03-31", price=4)]}}}
    states, symbols = historical_states(history, baseline)
    assert symbols == ["Cu", "Ni"]
    assert len(states) == 1 and states[0][0] == "2026-02"
    assert states[0][1]["Ni"] == dict(price=2, unit="$/kg", source="reference", reference_url="retained")
    assert states[0][1]["support"] == baseline["support"]
    assert baseline["Ni"]["price"] == 8


@pytest.mark.parametrize("price", [0, -1, float("nan"), float("inf")])
def test_history_rejects_invalid_prices(price):
    with pytest.raises(ValueError, match="finite positive"):
        historical_states({"basis_month": "2026-01", "cadence": "monthly_average", "series": {
            "Ni": {"unit": "$/kg", "points": [dict(date="2026-01-31", price=price)]}}},
            {"Ni": dict(price=1, unit="$/kg")})


def test_joint_rejects_mixed_units_and_changed_candidate_set():
    rows = [candidate("a", 100, 0, 1), candidate("b", 0, 100, 2, area_cost=3)]
    with pytest.raises(ValueError, match="Mixed functional"):
        joint_grid([rows], [dict(economics=1, evidence=0, route=0, performance=0)])


@pytest.mark.parametrize("family", ["co2-electroreduction", "glycerol-electrooxidation",
                                   "hydrogen-evolution-reaction", "nitrogen-reduction-reaction"])
def test_incomplete_electrode_family_displays_actual_powder_ranking_basis(session, family):
    result = evaluate_benchmark_family(session=session, family=family)
    assert {c["summary"]["economics_basis_unit"] for c in result["candidates"]} == {"$/lb"}
    assert {c["summary"]["economics_basis_label"] for c in result["candidates"]} == {"Catalyst powder screening"}
    for c in result["candidates"]:
        assert c["summary"]["economics_basis_value"] == c["summary"]["landed_cost_per_lb"]


def test_reference_equivalence_ignores_only_run_metadata():
    a = dict(price_basis={"Ni": dict(price=12, unit="$/kg", source="IMF")}, history_file="a", generated_at="old")
    b = {**a, "history_file": "b", "generated_at": "new"}
    assert reference_snapshot_equivalent(a, b)
    for key, value in (("price", 13), ("unit", "$/lb"), ("source", "unverified")):
        c = deepcopy(b)
        c["price_basis"]["Ni"][key] = value
        assert not reference_snapshot_equivalent(a, c)


def test_frozen_joint_study_conserves_ranks_and_matches_application(session):
    path = Path(__file__).resolve().parents[2] / "docs/paper/robustness-2026-09-08/decision_robustness.json"
    study = json.loads(path.read_text(encoding="utf-8"))
    basis_path = path.parent.parent / "submission-2026-09-07/reference_basis_2026-09-07.json"
    basis = json.loads(basis_path.read_text(encoding="utf-8"))["price_basis"]
    for family in study["families"]:
        reference = family["reference_candidates"]
        assert rank(reference, family["balanced_weights"])[0] == family["reference_winner"]
        app = evaluate_benchmark_family(session=session, family=family["family"], prices=basis, basis="reference")
        assert app["winner"]["slug"] == family["reference_winner"]
        assert [c["scores"] for c in app["candidates"]] == [c["scores"] for c in reference]
        for grid in family["joint_grids"].values():
            assert sum(c["first_rank_count"] for c in grid["candidates"].values()) == grid["scenarios"]
            for c in grid["candidates"].values():
                assert sum(c["rank_counts"]) == grid["scenarios"]
                assert 0 <= c["mean_regret_score_points"] <= c["worst_regret_score_points"] <= 100
        assert all(r["fixed_scale_winner"] == family["reference_winner"] for r in family["candidate_removal"])
