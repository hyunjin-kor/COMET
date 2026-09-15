"""Shared batch prices require explicit specification keys and matching units."""

from copy import deepcopy

from backend.tests.test_manufacturing_intermediates import nested_protocol
from backend.tests.test_manufacturing_protocol import payload


def save(client, protocol, name):
    r = client.post('/api/calculate/save', params={'name': name}, json={**payload(), 'manufacturing_protocol': protocol})
    assert r.status_code == 200, r.text
    return r.json()['id']


def keyed_protocol():
    p = nested_protocol()
    p['operations'][0]['equipment_comparison_key'] = 'Synthetic furnace A, equipment only'
    p['operations'][0]['gases'][0]['comparison_key'] = 'Synthetic gas purity A'
    p['operations'][0]['purchases'][0]['comparison_key'] = 'Synthetic precursor grade A'
    p['operations'][0]['purchases'][0]['input_evidence'] = {'price_usd_per_unit': {
        'kind': 'assumption', 'citation': 'Reference synthetic price', 'recorded_value': 2}}
    p['input_evidence'] = {'electricity_usd_kwh': {'kind': 'assumption', 'citation': 'Reference tariff', 'recorded_value': .1}}
    return p


def compare(client, first, second):
    return client.post('/api/estimates/compare', json={'estimate_ids': [first, second], 'reference_estimate_id': first,
        'price_basis': 'reference', 'order_size_tons': 2})


def test_common_keyed_prices_preserve_quantities_and_copy_reference_evidence(client):
    p = keyed_protocol()
    first = save(client, p, 'Synthetic price reference')
    p['operations'][0]['equipment_usd_h'] = 9
    p['operations'][0]['gases'][0]['price_usd_per_m3'] = 30
    p['operations'][0]['purchases'][0]['price_usd_per_unit'] = 6
    p['electricity_usd_kwh'] = .3
    p['input_evidence']['electricity_usd_kwh']['citation'] = 'Original alternative tariff'
    second = save(client, p, 'Synthetic price alternative')
    before = client.get(f'/api/estimates/{second}').json()
    response = compare(client, first, second)
    assert response.status_code == 200, response.text
    rows = response.json()['estimates']
    assert rows[0]['values']['common_conditions'] == rows[1]['values']['common_conditions']
    report = rows[1]['common_conditions']['manufacturing']
    protocol = report['protocol']
    assert protocol['operations'][0]['purchases'][0]['quantity'] == 10
    assert protocol['operations'][0]['purchases'][0]['price_usd_per_unit'] == 2
    assert protocol['input_evidence']['electricity_usd_kwh']['citation'] == 'Reference tariff'
    assert client.get(f'/api/estimates/{second}').json() == before
    prices = [r for r in response.json()['price_snapshot'] if r['key'].startswith('batch:')]
    assert len(prices) == 3 and all(r['overridden_estimate_ids'] == [second] for r in prices)
    assert len(response.json()['price_snapshot']) == 3
    assert all(row['scale_adjustment'] == {'substitutions': [], 'uncosted_steps': []} for row in rows)
    assert protocol['operations'][0]['purchases'][0]['input_evidence']['price_usd_per_unit']['citation'] == 'Reference synthetic price'


def test_same_name_without_key_does_not_assert_equivalent_purchasing_specifications(client):
    p = nested_protocol()
    first = save(client, p, 'Unkeyed reference')
    p['operations'][0]['purchases'][0]['price_usd_per_unit'] = 6
    second = save(client, p, 'Unkeyed alternative')
    d = compare(client, first, second).json()
    assert d['estimates'][0]['values']['common_conditions'] != d['estimates'][1]['values']['common_conditions']
    assert any('without a comparison key' in w for w in d['warnings'])


def test_shared_key_with_different_price_units_or_gas_reference_conditions_is_rejected(client):
    p = keyed_protocol()
    first = save(client, p, 'Reference units')
    for key in ('unit', 'volume_basis'):
        changed = deepcopy(p)
        if key == 'unit':
            changed['operations'][0]['purchases'][0]['unit'] = 'kg'
        else:
            changed['operations'][0]['gases'][0]['volume_basis'] = 'Different standard state'
        second = save(client, changed, 'Incompatible units')
        response = compare(client, first, second)
        assert response.status_code == 422, response.text


def test_conflicting_prices_for_one_key_within_a_saved_case_are_not_silently_selected(client):
    p = keyed_protocol()
    first = save(client, p, 'Unique price')
    item = deepcopy(p['operations'][0]['purchases'][0])
    item['price_usd_per_unit'] = 3
    p['operations'][0]['purchases'].append(item)
    second = save(client, p, 'Conflicting same-key price')
    response = compare(client, first, second)
    assert response.status_code == 422, response.text
