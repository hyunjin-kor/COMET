"""Synthetic batch purchase balances; no external prices or measurements."""

from copy import deepcopy

import pytest

from backend.core.cost_engine import estimate_catalyst_cost
from backend.tests.test_manufacturing_protocol import payload, protocol


def purchased_protocol():
    p = protocol()
    p['materials_basis'] = 'purchases'
    p['operations'][0].update(solvent='Synthetic solvent', solvent_volume_ml=100, purchases=[
        {'name': 'Synthetic precursor', 'quantity': 2, 'unit': 'g', 'price_usd_per_unit': 2},
        {'name': 'Synthetic solvent', 'quantity_basis': 'solvent_volume', 'unit': 'mL', 'price_usd_per_unit': .01},
    ])
    return p


def test_batch_purchases_replace_composition_cost_without_double_counting():
    p = purchased_protocol()
    result = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    m = result['materials']
    assert sum(r['cost_usd_kg'] for r in m['batch_purchases']) == pytest.approx(5 / .03)
    assert result['manufacturing']['batch_materials_cost_usd'] == 5
    changed = payload()
    changed['components'][0]['price_per_lb'] *= 1000
    changed['consumables'] = [{'name': 'Ignored old solvent', 'kg_per_kg_catalyst': 1000, 'price_per_kg': 999, 'source_note': 'Synthetic'}]
    other = estimate_catalyst_cost(**changed, manufacturing_protocol=p)
    assert result['summary']['estimated_price_per_kg'] == other['summary']['estimated_price_per_kg']
    assert any('replace' in w.lower() and 'purchases' in w.lower() for w in result['warnings'])


def test_solvent_quantity_link_and_dry_yield_change_final_cost():
    p = purchased_protocol()
    base = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    p['operations'][0]['solvent_volume_ml'] = 200
    changed = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    assert changed['manufacturing']['batch_materials_cost_usd'] == 6
    assert changed['step_method']['estimated_price_per_kg'] - base['step_method']['estimated_price_per_kg'] == pytest.approx(1 / .03 * 1.05**2, abs=.0001)
    p['finished_batch_mass_kg'] *= 2
    doubled_yield = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    assert doubled_yield['step_method']['estimated_price_per_kg'] == pytest.approx(changed['step_method']['estimated_price_per_kg'] / 2, abs=.0001)


def test_purchases_count_repetitions_and_trace_sources():
    p = purchased_protocol()
    p['operations'][0]['repetitions'] = 3
    source = {'kind': 'assumption', 'citation': 'Synthetic purchase', 'recorded_value': 2}
    p['operations'][0]['purchases'][0]['input_evidence'] = {'quantity': source}
    result = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    assert result['manufacturing']['batch_materials_cost_usd'] == 15
    trace = result['manufacturing']['trace']
    rows = {r['path']: r for r in trace['inputs']}
    assert rows['operations.0.purchases.0.quantity']['evidence']['citation'] == 'Synthetic purchase'
    assert rows['operations.0.solvent_volume_ml']['effect'] == 'cost_input'
    assert sum(r['value'] for r in trace['cost_ledger']) == pytest.approx(result['step_method']['estimated_price_per_kg'], abs=.0001)


def test_record_mode_does_not_replace_selected_material_or_processing_model():
    p = purchased_protocol()
    p['mode'] = 'record_only'
    result = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    base = estimate_catalyst_cost(**payload())
    assert result['summary']['estimated_price_per_kg'] == base['summary']['estimated_price_per_kg']
    assert result['manufacturing']['batch_materials_cost_usd'] == 5


@pytest.mark.parametrize('change', ['empty', 'price', 'solvent', 'two_quantities', 'wrong_unit'])
def test_incomplete_or_ambiguous_purchases_cannot_produce_batch_price(change):
    p = purchased_protocol()
    if change == 'empty':
        p['operations'][0]['purchases'] = []
    elif change == 'price':
        p['operations'][0]['purchases'][0]['price_usd_per_unit'] = None
    elif change == 'solvent':
        p['operations'][0]['solvent_volume_ml'] = None
    elif change == 'two_quantities':
        p['operations'][0]['purchases'][1]['quantity'] = 100
    else:
        p['operations'][0]['purchases'][1]['unit'] = 'kg'
    with pytest.raises(ValueError):
        estimate_catalyst_cost(**payload(), manufacturing_protocol=p)


def test_source_default_classification_survives_round_trip():
    from backend.core.manufacturing import evaluate_protocol
    from backend.schemas.manufacturing import ManufacturingProtocol
    p = ManufacturingProtocol.model_validate(protocol())
    original = deepcopy(p.model_dump())
    first = evaluate_protocol(p)['trace']
    second = evaluate_protocol(ManufacturingProtocol.model_validate(original))['trace']
    assert first == second


def test_batch_purchase_api_save_compare_and_fixed_uncertainty(client):
    p = {**payload(), 'manufacturing_protocol': purchased_protocol()}
    p['manufacturing_protocol']['operations'][0]['purchases'][0]['input_evidence'] = {
        'price_usd_per_unit': {'kind': 'assumption', 'citation': 'Synthetic purchase price', 'recorded_value': 2}}
    saved = client.post('/api/calculate/save?name=synthetic-batch-purchases', json=p)
    assert saved.status_code == 200, saved.text
    first = saved.json()['id']
    loaded = client.get(f'/api/estimates/{first}').json()
    assert loaded['input']['manufacturing_protocol']['operations'][0]['purchases'][0]['input_evidence']
    assert loaded['result']['manufacturing']['batch_materials_cost_usd'] == 5
    p['manufacturing_protocol']['operations'][0]['solvent_volume_ml'] = 200
    second = client.post('/api/calculate/save?name=synthetic-more-solvent', json=p)
    assert second.status_code == 200, second.text
    comp = client.post('/api/estimates/compare', json={'estimate_ids': [first, second.json()['id']],
        'reference_estimate_id': first, 'order_size_tons': 2, 'price_basis': 'reference'})
    assert comp.status_code == 200, comp.text
    a, b = comp.json()['estimates']
    assert a['common_conditions']['manufacturing']['batch_materials_cost_usd'] == 5
    assert b['common_conditions']['manufacturing']['batch_materials_cost_usd'] == 6
    req = {'calculation_input': p, 'n_simulations': 100, 'seed': 10,
           'uncertainties': {key: [1, 1] for key in ['active_component_price', 'promoter_price', 'support_price',
                                                   'electrode_adjunct_price', 'order_size_tons']}}
    mc = client.post('/api/uncertainty', json=req)
    assert mc.status_code == 200, mc.text
    assert mc.json()['mean'] == pytest.approx(second.json()['result']['summary']['estimated_price_per_lb'])
    assert 'fixed_manufacturing_assumptions' in mc.json()


def test_post_use_recovery_is_separate_from_manufacturing_ledger():
    args = {**payload(), 'include_spent_value': True, 'manufacturing_protocol': purchased_protocol()}
    result = estimate_catalyst_cost(**args)
    trace = result['manufacturing']['trace']
    assert sum(r['value'] for r in trace['cost_ledger']) == pytest.approx(result['step_method']['estimated_price_per_kg'], abs=.0001)
    recovery = trace['recovery_adjustment']
    assert recovery['net_cost_usd_kg'] == pytest.approx(result['summary']['net_cost_per_kg'], abs=.0001)
    assert recovery['gross_selling_price_usd_kg'] - recovery['applied_credit_usd_kg'] == pytest.approx(recovery['net_cost_usd_kg'])
