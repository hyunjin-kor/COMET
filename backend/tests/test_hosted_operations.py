"""Browser account confirmation and hosted resource budgets."""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from backend.services import hosted_usage as usage
from backend.tests.test_hosted_access import HEADERS, login
from backend.tests.test_hosted_access import hosted_client as _hosted_client_fixture

hosted_client = _hosted_client_fixture


def test_changed_cookie_cannot_write_previous_tabs_draft(hosted_client):
    client, first, second = hosted_client
    login(client)
    login(client, second.username)
    response = client.post('/api/materials', json={'name': 'Previous tab private formula', 'category': 'private'},
                           headers={**HEADERS, 'X-Comet-Account': first.id})
    assert response.status_code == 409
    assert 'Previous tab private formula' not in client.get('/api/materials').text
    del client.headers['X-Comet-Account']
    assert client.get('/api/materials').status_code == 409
    assert client.get('/api/auth/session').json()['account']['id'] == second.id


def test_persistent_per_account_budget_keeps_saved_reads_available(hosted_client, monkeypatch):
    client, first, second = hosted_client
    monkeypatch.setattr(usage, 'time', SimpleNamespace(time=lambda: 2_000_000_001.0))
    for _ in range(60):
        usage.consume_budget(first)
    login(client)
    blocked = client.post('/api/calculate', json={}, headers=HEADERS)
    assert blocked.status_code == 429
    assert 1 <= int(blocked.headers['Retry-After']) <= 60
    assert client.get('/api/estimates').status_code == 200
    usage.consume_budget(second)
    monkeypatch.setattr(usage, 'time', SimpleNamespace(time=lambda: 2_000_000_061.0))
    usage.consume_budget(first)


def test_uncertainty_has_separate_bounded_budget(hosted_client, monkeypatch):
    _, first, _ = hosted_client
    monkeypatch.setattr(usage, 'time', SimpleNamespace(time=lambda: 2_000_000_001.0))
    for _ in range(10):
        usage.consume_budget(first, uncertainty=True)
    with pytest.raises(HTTPException) as exc:
        usage.consume_budget(first, uncertainty=True)
    assert exc.value.status_code == 429
    usage.consume_budget(first)


def test_work_slots_release_on_failure_and_never_block_reads(hosted_client):
    _, first, _ = hosted_client
    request = SimpleNamespace(url=SimpleNamespace(path='/api/calculate'), method='POST')
    read = SimpleNamespace(url=SimpleNamespace(path='/api/estimates'), method='GET')
    with usage.work_slot(request, first), usage.work_slot(request, first):
        with pytest.raises(HTTPException):
            with usage.work_slot(request, first):
                pytest.fail('third work request entered')
        with usage.work_slot(read, first):
            pass
    with pytest.raises(ValueError), usage.work_slot(request, first):
        raise ValueError('synthetic calculation failure')
    with usage.work_slot(request, first), usage.work_slot(request, first):
        pass


def test_company_budget_is_shared_but_data_is_not(hosted_client, monkeypatch):
    _, first, second = hosted_client
    monkeypatch.setattr(usage, 'time', SimpleNamespace(time=lambda: 2_000_000_001.0))
    from backend.models.hosted import HostedUsageCounter
    from backend.services.hosted_access import control_session

    with control_session() as session:
        session.add(HostedUsageCounter(key=f'company:{first.organization_id}', window=int(2_000_000_001 // 60), attempts=240))
        session.commit()
    for account in (first, second):
        with pytest.raises(HTTPException):
            usage.consume_budget(account)
