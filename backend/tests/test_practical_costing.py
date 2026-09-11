"""Synthetic mass-balance/throughput fixtures, not observed industrial prices."""

from copy import deepcopy

import pytest

from backend.core.constants import LB_PER_KG
from backend.core.cost_engine import estimate_catalyst_cost
from backend.core.materials_calc import calculate_materials_cost_multi
from backend.core.recipe_costing import calculate_recipe_materials


def payload():
    return {
        "components": [
            {"role": "active_metal", "name": "Ni", "wt_pct": 20, "price_per_lb": 10},
            {"role": "support", "name": "Al2O3", "wt_pct": 80, "price_per_lb": 1},
        ],
        "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
        "order_size_tons": 20,
        "basis_year": 2017, "target_year": 2017,
    }


def recipe():
    return {"precursor_name": "Synthetic Ni precursor", "retained_component_fraction": .25,
            "purity_fraction": .8, "yield_fraction": .5, "price_per_kg": 5,
            "source_note": "Synthetic arithmetic fixture, not a measured purchase"}


def test_default_materials_are_exactly_unchanged():
    components = payload()["components"]
    assert calculate_recipe_materials(components) == calculate_materials_cost_multi(components)
    implicit = estimate_catalyst_cost(**payload())
    explicit = estimate_catalyst_cost(**payload(), production_rate_ton_per_day=10)
    assert implicit["materials"] == explicit["materials"]
    assert implicit["summary"] == explicit["summary"]
    assert implicit["step_method"] == explicit["step_method"]


def test_precursor_mass_and_consumables_close_without_double_counting():
    p = payload()
    p["components"][0]["recipe_consumption"] = recipe()
    additions = [{"name": "Synthetic wash", "kg_per_kg_catalyst": 3, "price_per_kg": .5,
                  "source_note": "Synthetic net purchase fixture"}]
    before = deepcopy(p)
    result = estimate_catalyst_cost(**p, consumables=additions)
    materials = result["materials"]
    # 0.2 kg finished Ni / (0.25 * 0.8 * 0.5) = 2 kg purchased precursor.
    row = materials["components"][0]
    assert row["recipe_consumption"]["purchased_kg_per_kg_catalyst"] == 2
    assert row["recipe_consumption"]["cost_per_kg_catalyst"] == 10
    expected_per_lb = 10 / LB_PER_KG + .8 + 1.5 / LB_PER_KG
    assert materials["total_materials_cost_per_lb"] == pytest.approx(expected_per_lb, abs=1e-6)
    assert p == before
    baseline = estimate_catalyst_cost(**payload())
    assert result["lca"] == baseline["lca"]
    assert any("not added to LCA" in w for w in result["warnings"])


def test_rate_changes_processing_not_materials_or_margin():
    base = estimate_catalyst_cost(**payload())
    slower = estimate_catalyst_cost(**payload(), production_rate_ton_per_day=5)
    assert base["step_method"]["campaign_days"] == 3
    assert slower["step_method"]["campaign_days"] == 5
    assert slower["step_method"]["processing_cost_per_lb"] == pytest.approx(
        base["step_method"]["processing_cost_per_lb"] * 5 / 3, abs=1e-4)
    assert slower["materials"] == base["materials"]
    assert slower["step_method"]["margin_pct"] == base["step_method"]["margin_pct"]


def test_zero_price_warning_uses_charged_precursor_instead_of_reference_metal():
    p = payload()
    p['components'][0].update(price_per_lb=0, recipe_consumption=recipe())
    assert not any('zero charged purchase' in w for w in estimate_catalyst_cost(**p)['warnings'])
    p['components'][0]['price_per_lb'] = 10
    p['components'][0]['recipe_consumption']['price_per_kg'] = 0
    assert any('zero charged purchase' in w for w in estimate_catalyst_cost(**p)['warnings'])


def test_save_load_recipe_rate_evidence_and_scope(client):
    p = payload()
    p["components"][0]["recipe_consumption"] = recipe()
    p["components"][0]["purchase_evidence"] = {"quote_date": "2026-05-01", "supplier": "Synthetic fixture", "grade": "test"}
    p.update(template_id="hydrothermal", production_rate_ton_per_day=5,
             production_rate_note="Synthetic measured-rate fixture")
    # Select a real declared template; the fixture's actual steps are intentionally customized.
    templates = client.get('/api/templates?catalyst_domain=thermal').json()
    p["template_id"] = next(t["id"] for t in templates if t.get("uncosted_operations"))
    calc = client.post('/api/calculate', json=p)
    assert calc.status_code == 200, calc.text
    saved = client.post('/api/calculate/save?name=synthetic-practical', json=p)
    assert saved.status_code == 200, saved.text
    loaded = client.get(f'/api/estimates/{saved.json()["id"]}').json()
    assert loaded["result"] == calc.json()
    assert loaded["input"]["production_rate_ton_per_day"] == 5
    assert loaded["input"]["components"][0]["recipe_consumption"] == recipe()
    assert loaded["result"]["purchase_evidence"][0]["evidence"]["quote_date"] == "2026-05-01"
    assert loaded["result"]["costing_scope"]["status"] == "partial"
    assert loaded["result"]["costing_scope"]["uncosted_operations"]


@pytest.mark.parametrize('field,value', [('retained_component_fraction', 0), ('purity_fraction', 1.1), ('yield_fraction', -1), ('price_per_kg', -2), ('source_note', '')])
def test_invalid_recipe_is_rejected(client, field, value):
    p = payload()
    p['components'][0]['recipe_consumption'] = {**recipe(), field: value}
    assert client.post('/api/calculate', json=p).status_code == 422


def test_no_markup_double_count_or_thermal_inputs_in_electrode(client):
    p = payload()
    p['components'][0].update(recipe_consumption=recipe(), precursor_markup=2)
    assert client.post('/api/calculate', json=p).status_code == 422
    p['components'][0]['precursor_markup'] = 1
    p['catalyst_domain'] = 'electrocatalyst'
    assert client.post('/api/calculate', json=p).status_code == 422


def test_rate_requires_positive_value_and_provenance(client):
    for fields in [{'production_rate_ton_per_day': 0, 'production_rate_note': 'fixture'},
                   {'production_rate_ton_per_day': 5}]:
        assert client.post('/api/calculate', json={**payload(), **fields}).status_code == 422


def test_fixed_uncertainty_matches_new_recipe_rate_and_does_not_mutate(client):
    p = payload()
    p['components'][0]['recipe_consumption'] = recipe()
    p.update(production_rate_ton_per_day=5, production_rate_note='Synthetic fixture',
             consumables=[{'name': 'Water', 'kg_per_kg_catalyst': 2, 'price_per_kg': .5, 'source_note': 'Synthetic'}])
    baseline = client.post('/api/calculate', json=p).json()
    req = {'calculation_input': p, 'n_simulations': 100, 'seed': 20260906,
           'uncertainties': {key: [1, 1] for key in ['active_component_price', 'promoter_price', 'support_price', 'electrode_adjunct_price', 'order_size_tons']}}
    first = client.post('/api/uncertainty', json=req)
    assert first.status_code == 200, first.text
    assert first.json() == client.post('/api/uncertainty', json=req).json()
    assert first.json()['mean'] == first.json()['min'] == first.json()['max'] == baseline['summary']['estimated_price_per_lb']
    assert client.post('/api/calculate', json=p).json() == baseline
