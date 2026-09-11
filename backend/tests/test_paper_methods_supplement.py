"""Check the supplemental scientific claims against the actual calculators."""

import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from scripts.paper_methods_text import extend_methods
from scripts.reproduce_paper_methods import (
    ROOT,
    SEED,
    STUDY,
    build_study,
    normalization_examples,
    recipe_example,
    uncertainty_examples,
)


def test_removal_replay_preserves_inputs_and_fixed_reference_order():
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    original = deepcopy(study)
    result = normalization_examples(study)
    assert study == original
    assert result["cases"] == study["summary"]["candidate_removal_cases"]
    assert result["changed"] == study["summary"]["candidate_removal_winner_changes"]
    assert result["fixed_changed"] == 0
    row = next(row for row in result["example"]["rows"] if row["slug"] == "co-mgo-la2o3")
    assert row["cost"] == 4.7411
    assert row["total_before"] == 89.3
    assert row["total_after"] == 77.4


def test_removal_replay_rejects_a_false_saved_winner():
    study = json.loads(STUDY.read_text(encoding="utf-8"))
    study["families"][0]["reference_winner"] = "not-the-recomputed-winner"
    with pytest.raises(ValueError, match="reference winner"):
        normalization_examples(study)


def test_recipe_and_area_scenarios_keep_correct_functional_units():
    recipe = recipe_example()
    assert recipe["purchased_precursor_kg_per_kg"] == 2
    assert recipe["total_usd_per_kg"] == pytest.approx(13.1)
    thermal, electrode = uncertainty_examples(recipe)
    assert thermal["result"]["unit"] == "$/lb"
    assert electrode["result"]["unit"] == "$/cm2"
    assert "baseline_price_per_lb" not in electrode["result"]
    assert "yield" in thermal["result"]["fixed_recipe_assumptions"]
    assert all(row["same_seed_equal"] and row["fixed_input_point_equal"] for row in (thermal, electrode))


def test_published_yield_is_not_used_as_an_industrial_cost_validation():
    result = build_study()
    baseline, low_yield, improved = result["published_yield_case"]
    assert low_yield["charged_ni_per_recovered_ni"] == pytest.approx(100 / 1.3)
    assert improved["charged_ni_per_recovered_ni"] < baseline["charged_ni_per_recovered_ni"]
    assert low_yield["fixed_input_yield_cost_ratio_to_gen1"] != pytest.approx(
        low_yield["reported_materials_cost_usd_per_kg"] / baseline["reported_materials_cost_usd_per_kg"])
    assert "does not reproduce" in result["yield_case_note"]


@pytest.mark.parametrize('seed,expected', [(SEED + 1, 'seed differs'), (SEED, 'matching robustness')])
def test_manuscript_rejects_unrelated_supplement(seed, expected):
    run = SimpleNamespace(manifest={'seed': seed}, data={})
    with pytest.raises(ValueError, match=expected):
        extend_methods('', '', run, ROOT / 'docs/paper/methods-2026-09-09/methods_study.json')
