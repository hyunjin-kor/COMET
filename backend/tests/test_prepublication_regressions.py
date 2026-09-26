"""User-visible failures found in the prepublication review; synthetic inputs only."""

import json
from copy import deepcopy

import pytest

THERMAL = {
    "components": [
        {"role": "active_metal", "name": "Ni", "wt_pct": 20, "price_per_lb": 7.5},
        {"role": "support", "name": "Al2O3", "wt_pct": 80, "price_per_lb": 0.5},
    ],
    "steps": ["mixer_slurry", "kiln_batch"], "order_size_tons": 4.99,
}
ELECTRODE = {
    "catalyst_domain": "electrocatalyst", "application_family": "fuel_cell",
    "components": [{"role": "active_catalyst", "name": "Pt/C", "wt_pct": 100, "price_per_lb": 100}],
    "steps": ["membrane_pretreatment"], "order_size_tons": 2,
    "electrode_input": {"active_area_cm2": 25, "catalyst_loading_mg_cm2": 0.5,
                        "substrate_cost_per_cm2": 0.10, "membrane_cost_per_cm2": 0.20},
}


def test_electrode_range_uses_the_displayed_assembly_and_varies_adjunct_prices(client):
    point = client.post('/api/calculate', json=ELECTRODE).json()['electrode_model']
    response = client.post('/api/uncertainty', json={
        'calculation_input': ELECTRODE, 'n_simulations': 100, 'seed': 20260906,
        'uncertainties': {'electrode_adjunct_price': [2, 2]},
    })
    assert response.status_code == 200
    value = response.json()
    assert value['unit'] == '$/cm2'
    assert value['baseline'] == point['cost_per_cm2_usd']
    assert value['mean'] == pytest.approx(point['cost_per_cm2_usd'] + 0.30, abs=1e-6)
    assert 'baseline_price_per_lb' not in value
    assert value['metric'] == 'electrode_assembly_cost'


def test_range_keeps_all_draws_when_order_crosses_a_scale_boundary(client):
    response = client.post('/api/uncertainty', json={
        'calculation_input': THERMAL, 'n_simulations': 100, 'seed': 20260906,
        'uncertainties': {'order_size_tons': [0.8, 1.2]},
    })
    assert response.status_code == 200
    assert response.json()['n_successful'] == 100


def test_recovery_range_matches_the_net_headline(client):
    payload = deepcopy(THERMAL)
    payload.update(include_spent_value=True, order_size_tons=2)
    payload['components'][0].update(name='Pt', wt_pct=2, price_per_lb=15000)
    payload['components'][1].update(name='C', wt_pct=98)
    calculated = client.post('/api/calculate', json=payload).json()
    assert calculated['summary']['net_cost_per_lb'] < calculated['summary']['estimated_price_per_lb']
    response = client.post('/api/uncertainty', json={
        'calculation_input': payload, 'n_simulations': 100,
        'uncertainties': {'active_component_price': [1, 1]},
    })
    assert response.status_code == 200
    value = response.json()
    assert value['mean'] == calculated['summary']['net_cost_per_lb']
    assert value['baseline_price_per_lb'] == calculated['summary']['net_cost_per_lb']


@pytest.mark.parametrize('structured', [False, True])
def test_unknown_uncertainty_parameters_are_rejected_instead_of_reported_as_applied(client, structured):
    legacy = {'metal_symbol': 'Ni', 'metal_price': 7.5, 'metal_loading_wt_pct': 20}
    payload = {'calculation_input': THERMAL} if structured else legacy
    response = client.post('/api/uncertainty', json={**payload, 'n_simulations': 100,
                                                   'uncertainties': {'typo_price': [0.1, 10]}})
    assert response.status_code == 422


def test_template_without_explicit_steps_uses_its_scale_fitted_operations(client):
    payload = {**THERMAL, 'template_id': 'coprecipitation_metal_oxide', 'order_size_tons': 20}
    del payload['steps']
    card = next(item for item in client.get('/api/templates/costs?order_size_tons=20&catalyst_domain=thermal').json()['templates']
                if item['id'] == payload['template_id'])
    response = client.post('/api/calculate', json=payload)
    assert response.status_code == 200
    value = response.json()
    assert [s['step'] for s in value['step_method']['step_details']] == card['steps_fitted']
    assert value['step_method']['processing_cost_per_lb'] == pytest.approx(card['processing_cost_per_lb'], abs=0.0001)


def test_thermal_calculation_rejects_an_electrode_template(client):
    response = client.post('/api/calculate', json={**THERMAL, 'template_id': 'pem_fuel_cell_ccm'})
    assert response.status_code == 422


@pytest.mark.parametrize('value', ['Infinity', '-Infinity', 'NaN'])
def test_nonfinite_numbers_are_client_errors_and_do_not_poison_material_catalog(client, value):
    response = client.post('/api/materials', content=json.dumps({'name': 'Invalid fixture', 'category': 'custom', 'price': value}),
                           headers={'Content-Type': 'application/json'})
    assert response.status_code == 422
    assert not client.get('/api/materials?q=Invalid%20fixture').json()


@pytest.mark.parametrize('path,payload', [
    ('/api/calculate', {**THERMAL, 'order_size_tons': 'Infinity'}),
    ('/api/calculate/quick', {'metal_symbol': 'Ni', 'metal_price': 'Infinity', 'metal_loading_wt_pct': 20}),
    ('/api/capex', {'purchased_equipment_cost_usd': 'Infinity'}),
    ('/api/uncertainty', {'metal_symbol': 'Ni', 'metal_price': 7.5, 'metal_loading_wt_pct': 20, 'order_size_tons': 0}),
    ('/api/compare', {'compositions': [{'metal_symbol': 'Ni', 'metal_price': 7.5, 'metal_loading_wt_pct': 20, 'order_size_tons': 0}] * 2}),
])
def test_invalid_numeric_requests_return_422(client, path, payload):
    response = client.post(path, json=payload)
    assert response.status_code == 422


def test_literal_nonfinite_json_gets_a_serializable_validation_error(client):
    payload = {**THERMAL, 'order_size_tons': float('nan')}
    response = client.post('/api/calculate', content=json.dumps(payload), headers={'Content-Type': 'application/json'})
    assert response.status_code == 422


def test_tiny_order_outside_the_margin_correlation_does_not_return_a_negative_price(client):
    response = client.post('/api/calculate', json={**THERMAL, 'order_size_tons': 0.001})
    assert response.status_code == 422
    assert 'margin' in response.text.lower()


def test_saved_template_defaults_replay_the_actual_calculated_steps(client):
    payload = {**THERMAL, 'template_id': 'coprecipitation_metal_oxide', 'order_size_tons': 20}
    del payload['steps']
    saved = client.post('/api/calculate/save?name=Synthetic%20template', json=payload).json()
    stored = client.get(f"/api/estimates/{saved['id']}").json()
    replay = client.post('/api/calculate', json=stored['input']).json()
    assert stored['input']['steps'] == saved['result']['costing_scope']['actual_steps']
    assert replay['step_method'] == saved['result']['step_method']


def test_explicit_empty_uncertainty_mapping_keeps_the_case_fixed(client):
    response = client.post('/api/uncertainty', json={
        'calculation_input': THERMAL, 'n_simulations': 100, 'uncertainties': {},
    })
    assert response.status_code == 200
    value = response.json()
    assert value['std'] == 0
    assert value['uncertainties_applied'] == {}
    assert value['mean'] == value['baseline']


@pytest.mark.parametrize('quantity', ['nan', 'inf', '0.001'])
def test_template_costs_reject_invalid_production_quantities(client, quantity):
    assert client.get('/api/templates/costs', params={'order_size_tons': quantity}).status_code == 422
