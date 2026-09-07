"""Counterfactual analysis separates price levels from evidence annotations."""

from copy import deepcopy

import pytest

from scripts.run_controlled_cases import cross_price_evidence, electrode_cases, manufacturing_cases


def synthetic_family(confidence=50):
    candidates = []
    for slug, cost, economic in [("a", 10, 100), ("b", 20, 0)]:
        candidates.append({
            "slug": slug,
            "summary": {"landed_cost_per_lb": cost, "economics_basis_value": cost,
                        "economics_basis_unit": "$/lb"},
            "scores": {"economics": economic, "evidence": confidence, "route": 60,
                       "performance": 40, "total": round(0.5 * economic + 0.5 * confidence, 1)},
            "components": [{"name": slug, "role": "active_metal", "wt_pct": 100,
                            "cost_per_lb_cat": cost, "evidence": {"confidence_score": confidence}}],
        })
    return {"family": "synthetic", "decision_profile": {"weights": {
        "economics": 0.5, "evidence": 0.5, "route": 0, "performance": 0}},
        "candidates": candidates}


def test_evidence_only_change_has_zero_price_contribution():
    result = cross_price_evidence(synthetic_family(50), synthetic_family(80))
    for row in result["contributions"]:
        assert row["price_effect_score_points"] == 0
        assert row["evidence_effect_score_points"] == 15
        assert row["total_change_score_points"] == 15


def test_identical_endpoints_have_identical_rankings_and_no_effect():
    baseline = synthetic_family()
    result = cross_price_evidence(baseline, deepcopy(baseline))
    assert all(state["ranking"] == ["a", "b"] for state in result["states"].values())
    assert all(row["total_change_score_points"] == 0 for row in result["contributions"])
    assert baseline == synthetic_family()


def test_candidate_order_does_not_change_matching():
    live = synthetic_family(80)
    live["candidates"].reverse()
    assert cross_price_evidence(synthetic_family(), live) == cross_price_evidence(synthetic_family(), synthetic_family(80))


@pytest.mark.parametrize("change", ["composition", "candidate", "unit", "route"])
def test_non_price_differences_cannot_be_silently_attributed(change):
    live = synthetic_family()
    if change == "composition":
        live["candidates"][0]["components"][0]["wt_pct"] = 99
    elif change == "candidate":
        live["candidates"].pop()
    elif change == "unit":
        live["candidates"][0]["summary"]["economics_basis_unit"] = "$/cm2"
    else:
        live["candidates"][0]["scores"]["route"] = 80
    with pytest.raises(ValueError):
        cross_price_evidence(synthetic_family(), live)


def test_scale_sweep_holds_finished_material_cost_fixed():
    import json
    from pathlib import Path

    basis = json.loads((Path(__file__).resolve().parents[2] / "docs/paper/submission-2026-09-07/reference_basis_2026-09-07.json").read_text(encoding="utf-8"))["price_basis"]
    result = manufacturing_cases(basis)
    assert len(result["rows"]) == 21
    assert len({row["materials_usd_per_lb"] for row in result["rows"]}) == 1
    assert {row["scale"] for row in result["rows"]} == {"small", "medium", "large"}
    assert all(not row["dropped_steps"] for row in result["rows"])


def test_electrode_center_case_matches_the_native_material_stack(session):
    from backend.core.decision_engine import evaluate_benchmark_family

    native = evaluate_benchmark_family(session=session, family="pem-electrolyzer-oer")
    expected = next(c for c in native["candidates"] if c["slug"] == "pem-irox-baseline")
    result = electrode_cases(session)
    center = next(row for row in result["rows"] if row["powder_price_multiplier"] == 1 and row["loading_mg_cm2"] == 1.5)
    assert center["cost_usd_per_m2"] == expected["summary"]["electrode_cost_per_m2"]
    assert center["total_usd"] == expected["estimate"]["electrode_model"]["total_cost_usd"]


def test_unrecorded_data_directory_override_is_rejected(monkeypatch, tmp_path):
    from scripts.run_controlled_cases import main

    monkeypatch.setenv("COMET_DATA_DIR", str(tmp_path))
    monkeypatch.setattr("sys.argv", ["controlled", "--reference-basis", "missing.json",
                                   "--live-basis", "missing.json", "--out-dir", str(tmp_path)])
    with pytest.raises(ValueError, match="repository data directory"):
        main()
