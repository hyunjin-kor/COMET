"""Contract entitlements are server-controlled and distinct from account security."""

import time

import pytest
from sqlmodel import select

from backend.models.hosted import HostedAccount, HostedAuditEvent, HostedOrganization
from backend.services import hosted_access as hosted
from backend.services.hosted_subscription import set_subscription, subscription_state
from backend.tests.test_api import _save_estimate
from backend.tests.test_hosted_access import HEADERS, PASSWORD, login
from backend.tests.test_hosted_access import hosted_client as _hosted_client_fixture

hosted_client = _hosted_client_fixture


def contract(org_id, *, status="active", seats=2, starts=None, ends=None):
    now = time.time()
    return set_subscription(org_id, status=status, starts_at=now - 10 if starts is None else starts,
                            ends_at=now + 3600 if ends is None else ends, seat_limit=seats,
                            actor="synthetic-test-operator", reason="contract_recorded")


@pytest.mark.parametrize("state", ["expired", "revoked", "pending"])
def test_inactive_contract_keeps_saved_read_export_but_blocks_new_work(hosted_client, state):
    client, account, _ = hosted_client
    assert login(client).status_code == 200
    client.headers.update(HEADERS)
    estimate_id = _save_estimate(client, "Private retained result").json()["id"]
    now = time.time()
    contract(account.organization_id, status="active" if state == "expired" else state,
             starts=now - 3600, ends=now - 1 if state == "expired" else now + 3600)
    view = client.get("/api/auth/session").json()["account"]["subscription"]
    assert view["status"] == state and not view["can_start_work"]
    assert client.get(f"/api/estimates/{estimate_id}").status_code == 200
    assert client.get(f"/api/export/{estimate_id}").status_code == 200
    assert client.get(f"/api/estimates/{estimate_id}/observations").status_code == 200
    assert _save_estimate(client, "Not allowed").status_code == 403
    assert client.get("/api/templates/costs").status_code == 403
    assert client.get("/api/decision/benchmarks/ammonia-synthesis").status_code == 403
    assert client.post("/api/materials", json={"name": "Not allowed", "category": "custom"}).status_code == 403
    assert client.post("/api/auth/logout").status_code == 200
    assert login(client).status_code == 200


def test_contract_renewal_takes_effect_for_existing_session(hosted_client):
    client, account, _ = hosted_client
    assert login(client).status_code == 200
    client.headers.update(HEADERS)
    contract(account.organization_id, status="revoked")
    assert _save_estimate(client, "Inactive").status_code == 403
    contract(account.organization_id)
    assert _save_estimate(client, "Renewed").status_code == 200


def test_seat_limit_applies_to_creation_reactivation_and_reduction(hosted_client):
    _, account, second = hosted_client
    with pytest.raises(ValueError, match="seat"):
        hosted.create_account(account.organization_id, "fixture.third", PASSWORD)
    hosted.set_account_enabled(second.id, False)
    third = hosted.create_account(account.organization_id, "fixture.third", PASSWORD)
    with pytest.raises(ValueError, match="seat"):
        hosted.set_account_enabled(second.id, True)
    with pytest.raises(ValueError, match="seat"):
        contract(account.organization_id, seats=1)
    with hosted.control_session() as session:
        assert session.get(HostedAccount, third.id).enabled
        assert session.get(HostedOrganization, account.organization_id).seat_limit == 2


def test_pending_is_default_and_contract_boundaries_are_exact(hosted_client):
    organization = hosted.create_organization("Synthetic pending company")
    assert subscription_state(organization, now=1000) == "pending"
    organization.status, organization.starts_at, organization.ends_at = "active", 1000, 2000
    assert subscription_state(organization, now=999) == "pending"
    assert subscription_state(organization, now=1000) == "active"
    assert subscription_state(organization, now=2000) == "expired"
    organization.status = "revoked"
    assert subscription_state(organization, now=1500) == "revoked"


def test_contract_updates_reject_invalid_period_seats_and_unrecorded_actor(hosted_client):
    _, account, _ = hosted_client
    for change in ({"ends_at": 1, "starts_at": 2}, {"seat_limit": 0}, {"actor": ""}, {"status": "invented"}):
        values = dict(status="active", starts_at=1, ends_at=2, seat_limit=2, actor="test-operator", reason="contract_recorded")
        values.update(change)
        with pytest.raises(ValueError):
            set_subscription(account.organization_id, **values)


def test_contract_audit_contains_changes_without_credentials_or_research_values(hosted_client):
    _, account, _ = hosted_client
    contract(account.organization_id, status="revoked")
    with hosted.control_session() as session:
        events = session.exec(select(HostedAuditEvent).where(HostedAuditEvent.action == "subscription_updated")
                              .order_by(HostedAuditEvent.at, HostedAuditEvent.id)).all()
        assert events[-1].target_id == account.organization_id
        assert events[-1].actor == "synthetic-test-operator"
        assert "revoked" in events[-1].details_json
        assert all(PASSWORD not in event.model_dump_json() for event in events)


def test_password_change_after_expiry_invalidates_all_other_sessions(hosted_client):
    client, account, _ = hosted_client
    assert login(client).status_code == 200
    token = client.cookies.get(hosted.COOKIE_NAME)
    contract(account.organization_id, starts=time.time() - 100, ends=time.time() - 1)
    response = client.post("/api/auth/password", headers=HEADERS,
                           json={"current_password": PASSWORD, "new_password": PASSWORD + "-changed"})
    assert response.status_code == 200
    assert client.get("/api/estimates").status_code == 401
    assert login(client, password=PASSWORD).status_code == 401
    assert login(client, password=PASSWORD + "-changed").status_code == 200
    assert token != client.cookies.get(hosted.COOKIE_NAME)


def test_simultaneous_account_creation_cannot_claim_the_same_last_seat(hosted_client):
    from concurrent.futures import ThreadPoolExecutor

    _, account, second = hosted_client
    hosted.set_account_enabled(second.id, False)

    def create(username):
        try:
            return hosted.create_account(account.organization_id, username, PASSWORD).id
        except ValueError as exc:
            assert "seat" in str(exc)
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(create, ["fixture.concurrent1", "fixture.concurrent2"]))
    assert sum(result is not None for result in results) == 1


def test_operator_password_reset_revokes_sessions(hosted_client):
    client, account, _ = hosted_client
    assert login(client).status_code == 200
    hosted.reset_account_password(account.id, PASSWORD + "-reset", actor="synthetic-test-operator")
    assert client.get("/api/estimates").status_code == 401
    assert login(client, password=PASSWORD + "-reset").status_code == 200


def test_legacy_control_schema_is_extended_without_activating_old_organization(hosted_client, monkeypatch, tmp_path):
    import sqlite3

    from backend.config import settings

    root = tmp_path / "legacy"
    root.mkdir()
    with sqlite3.connect(root / "control.db") as connection:
        connection.execute("CREATE TABLE hosted_organizations (id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL)")
        connection.execute("INSERT INTO hosted_organizations VALUES (?, ?)", ("a" * 32, "Synthetic legacy"))
    monkeypatch.setattr(settings, "hosted_storage_dir", str(root))
    hosted.initialize_hosted_store()
    with hosted.control_session() as session:
        organization = session.get(HostedOrganization, "a" * 32)
        assert organization.name == "Synthetic legacy"
        assert subscription_state(organization) == "pending"
        assert organization.starts_at is None and organization.ends_at is None


def test_operator_cli_never_accepts_password_in_arguments(monkeypatch):
    from scripts.manage_hosted import main, private_password

    monkeypatch.setattr("sys.argv", ["manage_hosted", "account", "--organization", "test", "--username", "test", "--password", "synthetic"])
    with pytest.raises(SystemExit):
        main()
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    with pytest.raises(ValueError, match="private terminal"):
        private_password()


def test_client_cannot_grant_itself_a_contract_or_change_company(hosted_client):
    client, account, _ = hosted_client
    contract(account.organization_id, status="pending")
    response = client.post("/api/auth/login", headers=HEADERS, json={"username": "fixture.first", "password": PASSWORD,
                                                                  "subscription": "active", "organization_id": "other"})
    assert response.status_code == 422
    assert login(client).status_code == 200
    assert client.get("/api/auth/session").json()["account"]["subscription"]["status"] == "pending"
