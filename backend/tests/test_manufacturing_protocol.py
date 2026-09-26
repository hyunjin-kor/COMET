"""Synthetic operating inputs; no measured catalyst cost or power is implied."""

from copy import deepcopy

import pytest

from backend.core.constants import LB_PER_KG
from backend.core.cost_engine import estimate_catalyst_cost
from backend.core.manufacturing import evaluate_protocol
from backend.schemas.manufacturing import ManufacturingProtocol


def payload():
    return {"components": [{"role": "active_metal", "name": "Ni", "wt_pct": 20, "price_per_lb": 10},
                           {"role": "support", "name": "Al2O3", "wt_pct": 80, "price_per_lb": 1}],
            "steps": ["mixer_slurry"], "order_size_tons": 2, "basis_year": 2017, "target_year": 2017}


def protocol():
    return {"mode": "batch_cost", "finished_batch_mass_kg": 0.03, "electricity_usd_kwh": .1,
            "labor_usd_h": 10, "source_note": "Synthetic arithmetic fixture, not a measured experiment",
            "operations": [{"name": "Multistage thermal treatment", "start_temperature_c": 20,
                            "temperature_profile": [
                                {"target_c": 200, "ramp_c_per_min": 5, "hold_h": .5, "ramp_power_kw": 2, "hold_power_kw": 1},
                                {"target_c": 300, "ramp_c_per_min": 5, "hold_h": .5, "ramp_power_kw": 2, "hold_power_kw": 1},
                                {"target_c": 500, "ramp_c_per_min": 5, "hold_h": 5, "ramp_power_kw": 2, "hold_power_kw": 1}],
                            "additional_time_h": 1, "additional_power_kw": 0,
                            "equipment_usd_h": 3, "attended_labor_h": .5, "other_cost_usd": 0}]}


def test_multistage_heat_time_energy_and_kg_cost():
    p = protocol()
    r = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    # Ramp = (500 - 20)/5/60 = 1.6 h; holds 6 h; extra time 1 h.
    assert r['serial_operation_hours'] == pytest.approx(8.6)
    assert r['operations'][0]['electricity_kwh'] == pytest.approx(9.2)
    cost = .92 + 8.6 * 3 + .5 * 10
    assert r['batch_processing_cost_usd'] == pytest.approx(cost)
    assert r['processing_cost_usd_kg'] == pytest.approx(cost / .03)
    result = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    assert result['step_method']['processing_cost_per_lb'] == pytest.approx(cost / .03 / LB_PER_KG)
    assert result['step_method']['margin_pct'] == 0
    assert result['lca']['process'] is None
    assert result['costing_scope']['costed_steps'] == []
    assert p == protocol()


def test_hold_temperature_ramp_yield_and_repetition_sensitivity():
    base = protocol()
    def run(p):
        return evaluate_protocol(ManufacturingProtocol.model_validate(p))
    r = run(base)
    p = deepcopy(base)
    p['operations'][0]['temperature_profile'][-1]['hold_h'] += 1
    assert run(p)['batch_processing_cost_usd'] - r['batch_processing_cost_usd'] == pytest.approx(3.1)
    p = deepcopy(base)
    p['operations'][0]['temperature_profile'][-1]['target_c'] = 800
    assert run(p)['serial_operation_hours'] - r['serial_operation_hours'] == pytest.approx(1)
    p['operations'][0]['temperature_profile'][-1]['ramp_c_per_min'] = 10
    assert run(p)['serial_operation_hours'] < r['serial_operation_hours'] + 1
    p = deepcopy(base)
    p['finished_batch_mass_kg'] /= 2
    assert run(p)['processing_cost_usd_kg'] == pytest.approx(r['processing_cost_usd_kg'] * 2)
    p = deepcopy(base)
    p['operations'][0]['repetitions'] = 2
    assert run(p)['batch_processing_cost_usd'] == pytest.approx(r['batch_processing_cost_usd'] * 2)


def test_reduction_gas_has_its_own_duration_and_volume_basis():
    p = protocol()
    p['operations'][0]['gases'] = [{'name': 'H2/N2 mixture', 'flow_l_per_min': .1, 'duration_h': 2,
                                  'price_usd_per_m3': 10, 'volume_basis': 'Both at 0 C and 1 atm'}]
    r = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert r['operations'][0]['gases'][0]['volume_m3'] == pytest.approx(.012)
    assert r['operations'][0]['costs_usd']['gas'] == pytest.approx(.12)


def test_record_only_preserves_legacy_results_and_reports_missing_not_zero():
    p = {'mode': 'record_only', 'operations': [{'name': 'Drying', 'start_temperature_c': 110,
                                             'duration_h': 10, 'additional_time_h': 0}]}
    base = estimate_catalyst_cost(**payload())
    recorded = estimate_catalyst_cost(**payload(), manufacturing_protocol=p)
    assert base['summary'] == recorded['summary']
    assert base['step_method'] == recorded['step_method']
    assert recorded['manufacturing']['processing_cost_usd_kg'] is None
    assert recorded['manufacturing']['operations'][0]['duration_h'] == 10
    assert recorded['manufacturing']['operations'][0]['cost_usd'] is None


def test_measured_energy_replaces_power_and_small_batch_avoids_industrial_margin():
    p = protocol()
    op = p['operations'][0]
    op['energy_basis'] = 'measured'
    op['measured_energy_kwh'] = 7
    op['additional_power_kw'] = None
    for segment in op['temperature_profile']:
        segment['ramp_power_kw'] = segment['hold_power_kw'] = None
    result = estimate_catalyst_cost(**{**payload(), 'order_size_tons': .00001}, manufacturing_protocol=p)
    assert result['manufacturing']['operations'][0]['electricity_kwh'] == 7
    assert result['step_method']['margin_pct'] == 0
    op['temperature_profile'][-1]['hold_h'] += 1
    changed = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert changed['operations'][0]['electricity_kwh'] == 7
    assert changed['batch_processing_cost_usd'] == pytest.approx(result['manufacturing']['batch_processing_cost_usd'] + 3)
    op['measured_energy_kwh'] = None
    with pytest.raises(ValueError, match='measured electricity'):
        evaluate_protocol(ManufacturingProtocol.model_validate(p))


def test_cooling_profile_and_missing_gas_basis(client):
    p = protocol()
    p['operations'][0]['temperature_profile'].append(
        {'target_c': 20, 'ramp_c_per_min': 10, 'hold_h': 0, 'ramp_power_kw': 0})
    report = evaluate_protocol(ManufacturingProtocol.model_validate(p))
    assert report['serial_operation_hours'] == pytest.approx(9.4)
    p['operations'][0]['gases'] = [{'name': 'N2', 'flow_l_per_min': .1,
                                  'duration_h': 2, 'price_usd_per_m3': 10}]
    assert client.post('/api/calculate', json={**payload(), 'manufacturing_protocol': p}).status_code == 422


def test_mixed_models_and_electrode_protocols_are_rejected(client):
    p = {**payload(), 'manufacturing_protocol': protocol()}
    assert client.post('/api/calculate', json={**p, 'catalyst_domain': 'electrocatalyst'}).status_code == 422
    assert client.post('/api/calculate', json={**p, 'production_rate_ton_per_day': 1,
                                              'production_rate_note': 'fixture'}).status_code == 422
    ids = [client.post('/api/calculate/save', json=x).json()['id'] for x in (p, payload())]
    response = client.post('/api/estimates/compare', json={'estimate_ids': ids, 'reference_estimate_id': ids[0],
                                                         'order_size_tons': 2, 'price_basis': 'reference'})
    assert response.status_code == 422


@pytest.mark.parametrize('mutate', [
    lambda p: p.update(finished_batch_mass_kg=0),
    lambda p: p.update(electricity_usd_kwh=None),
    lambda p: p.update(source_note=' '),
    lambda p: p['operations'][0].update(start_temperature_c=None),
    lambda p: p['operations'][0].update(duration_h=10),
    lambda p: p['operations'][0].update(measured_energy_kwh=10),
    lambda p: p['operations'][0]['temperature_profile'][0].update(ramp_c_per_min=0),
    lambda p: p['operations'][0]['temperature_profile'][0].update(hold_power_kw=None),
    lambda p: p['operations'][0].update(pressure_bar_abs=-1),
    lambda p: p['operations'][0].update(repetitions=1.5),
])
def test_invalid_or_incomplete_inputs_rejected(client, mutate):
    p = protocol()
    mutate(p)
    response = client.post('/api/calculate', json={**payload(), 'manufacturing_protocol': p})
    assert response.status_code == 422, response.text


def test_save_reload_compare_and_fixed_uncertainty(client):
    p = {**payload(), 'manufacturing_protocol': protocol()}
    calc = client.post('/api/calculate', json=p)
    assert calc.status_code == 200, calc.text
    saved = client.post('/api/calculate/save?name=synthetic-protocol', json=p)
    assert saved.status_code == 200, saved.text
    first_id = saved.json()['id']
    loaded = client.get(f'/api/estimates/{first_id}').json()
    assert loaded['input']['manufacturing_protocol']['operations'][0]['temperature_profile'][2]['hold_h'] == 5
    assert loaded['result'] == calc.json()
    p['manufacturing_protocol']['operations'][0]['temperature_profile'][2]['hold_h'] = 10
    second = client.post('/api/calculate/save?name=synthetic-longer', json=p)
    assert second.status_code == 200, second.text
    comp = client.post('/api/estimates/compare', json={'estimate_ids': [first_id, second.json()['id']],
                                                     'reference_estimate_id': first_id, 'order_size_tons': 2,
                                                     'price_basis': 'reference'})
    assert comp.status_code == 200, comp.text
    a, b = comp.json()['estimates']
    assert a['common_conditions']['manufacturing']['protocol']['operations'][0]['temperature_profile'][2]['hold_h'] == 5
    assert b['values']['common_conditions'] > a['values']['common_conditions']
    req = {'calculation_input': p, 'n_simulations': 100, 'seed': 10,
           'uncertainties': {key: [1, 1] for key in ['active_component_price', 'promoter_price', 'support_price',
                                                   'electrode_adjunct_price', 'order_size_tons']}}
    mc = client.post('/api/uncertainty', json=req)
    assert mc.status_code == 200, mc.text
    longer = client.post('/api/calculate', json=p).json()
    assert mc.json()['mean'] == pytest.approx(longer['summary']['estimated_price_per_lb'])
