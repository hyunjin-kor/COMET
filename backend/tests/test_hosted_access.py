"""Hosted account boundaries use disposable storage and synthetic identities."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from backend.config import settings
from backend.main import app
from backend.models.hosted import HostedAccount, HostedLoginSession
from backend.services import hosted_access as hosted

HEADERS = {"Origin": "https://testserver", "X-Comet-Request": "1"}
PASSWORD = "synthetic-fixture-password-only"


@pytest.fixture
def hosted_client(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "hosted_mode", True)
    monkeypatch.setattr(settings, "hosted_origin", "https://testserver")
    monkeypatch.setattr(settings, "hosted_storage_dir", str(tmp_path))
    # Test identities/storage only. Never mark the real rights manifest approved.
    monkeypatch.setattr(hosted, "check_data_rights", lambda *args: [])
    app.dependency_overrides.clear()
    with TestClient(app, base_url="https://testserver") as client:
        organization = hosted.create_organization("Synthetic organization")
        first = hosted.create_account(organization.id, "fixture.first", PASSWORD)
        second = hosted.create_account(organization.id, "fixture.second", PASSWORD)
        yield client, first, second


def login(client, username="fixture.first", password=PASSWORD):
    return client.post("/api/auth/login", json={"username": username, "password": password}, headers=HEADERS)


def test_hosted_defaults_off_and_local_session_has_no_login_requirement(client):
    assert client.get("/api/auth/session").json() == {"mode": "desktop", "authenticated": False, "account": None}
    assert client.get("/api/estimates").status_code == 200


@pytest.mark.parametrize("path", ["/api/estimates", "/api/materials", "/api/equipment", "/api/prices", "/api/templates/costs"])
def test_every_private_api_requires_authentication(hosted_client, path):
    client, _, _ = hosted_client
    assert client.get(path).status_code == 401


def test_session_cookie_rotation_logout_and_hash_only_storage(hosted_client):
    client, first, _ = hosted_client
    response = login(client)
    assert response.status_code == 200
    cookie = response.headers["set-cookie"]
    assert all(flag in cookie.lower() for flag in ("httponly", "secure", "samesite=strict"))
    token = client.cookies.get(hosted.COOKIE_NAME)
    with hosted.control_session() as session:
        stored = session.exec(select(HostedLoginSession)).one()
        assert stored.token_hash != token
        assert stored.account_id == first.id
        assert session.get(HostedAccount, first.id).password_hash != PASSWORD
    assert "password" not in response.text
    assert login(client).status_code == 200
    assert client.cookies.get(hosted.COOKIE_NAME) != token
    client.cookies.set(hosted.COOKIE_NAME, token, domain="testserver.local", path="/")
    assert client.get("/api/estimates").status_code == 401
    client.cookies.clear()
    assert login(client).status_code == 200
    assert client.post("/api/auth/logout", headers=HEADERS).status_code == 200
    assert client.get("/api/estimates").status_code == 401


@pytest.mark.parametrize("headers", [{}, {"Origin": "https://testserver"}, {"Origin": "https://evil.example", "X-Comet-Request": "1"}])
def test_login_csrf_rejected(hosted_client, headers):
    client, _, _ = hosted_client
    assert client.post("/api/auth/login", json={"username": "fixture.first", "password": PASSWORD}, headers=headers).status_code == 403


def test_authenticated_mutation_also_requires_origin_and_custom_header(hosted_client):
    client, _, _ = hosted_client
    assert login(client).status_code == 200
    assert client.post("/api/materials", json={"name": "private", "category": "custom"}).status_code == 403


def test_company_colleagues_do_not_implicitly_share_private_materials(hosted_client):
    client, _, _ = hosted_client
    assert login(client).status_code == 200
    saved = client.post("/api/materials", headers=HEADERS, json={"name": "Private first formula", "category": "PrivateCategory", "price": 10}).json()
    assert saved["is_custom"]
    client.post("/api/auth/logout", headers=HEADERS)
    assert login(client, "fixture.second").status_code == 200
    assert "Private first formula" not in client.get("/api/materials").text
    assert "PrivateCategory" not in client.get("/api/materials/categories").text
    for method in ("get", "patch", "delete"):
        response = getattr(client, method)(f"/api/materials/{saved['id']}", headers=HEADERS, **({"json": {"name": "attacker"}} if method == "patch" else {}))
        assert response.status_code == 404


def test_disabled_account_and_expired_session_are_rejected(hosted_client):
    client, first, _ = hosted_client
    assert login(client).status_code == 200
    with hosted.control_session() as session:
        record = session.exec(select(HostedLoginSession)).one()
        record.expires_at = 1
        session.add(record)
        session.commit()
    assert client.get("/api/estimates").status_code == 401
    assert login(client).status_code == 200
    hosted.set_account_enabled(first.id, False)
    assert client.get("/api/estimates").status_code == 401
    assert login(client).status_code == 401


def test_login_failure_does_not_reveal_account_existence_and_is_throttled(hosted_client, monkeypatch):
    from types import SimpleNamespace

    monkeypatch.setattr(hosted, "time", SimpleNamespace(time=lambda: 2_000_000_000.0))
    client, _, _ = hosted_client
    known = login(client, password="incorrect-synthetic-password")
    unknown = login(client, "fixture.unknown", "incorrect-synthetic-password")
    assert known.status_code == unknown.status_code == 401
    assert known.json() == unknown.json()
    for _ in range(4):
        assert login(client, password="incorrect-synthetic-password").status_code == 401
    assert login(client).status_code == 429


def test_unreviewed_commercial_data_prevents_hosted_start(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "hosted_mode", True)
    monkeypatch.setattr(settings, "hosted_origin", "https://testserver")
    monkeypatch.setattr(settings, "hosted_storage_dir", str(tmp_path))
    with pytest.raises(RuntimeError, match="data rights"):
        with TestClient(app):
            pass


def test_hosted_never_collects_live_prices(hosted_client, monkeypatch):
    client, _, _ = hosted_client
    assert login(client).status_code == 200
    assert client.post("/api/prices/refresh", headers=HEADERS).status_code == 403
    assert client.get("/api/health").json()["scheduler_running"] is False


def test_private_path_rejects_non_server_identifier(hosted_client):
    with pytest.raises(ValueError):
        hosted.account_database_path("../../comet")


def test_other_company_cannot_read_export_compare_or_change_saved_estimates(hosted_client):
    client, _, _ = hosted_client
    from backend.tests.test_api import _save_estimate

    assert login(client).status_code == 200
    client.headers.update(HEADERS)
    first = _save_estimate(client, "Private first estimate").json()["id"]
    second = _save_estimate(client, "Private second estimate").json()["id"]
    equipment = client.post("/api/equipment", json={"name": "Private first equipment", "category": "custom",
                                                  "size_units": "kg", "function_type": "power"}).json()["id"]
    client.post("/api/auth/logout")
    organization = hosted.create_organization("Synthetic other company")
    hosted.create_account(organization.id, "fixture.other", PASSWORD)
    assert login(client, "fixture.other").status_code == 200
    assert client.get("/api/estimates").json() == []
    assert "Private first equipment" not in client.get("/api/equipment").text
    for path in (f"/api/estimates/{first}", f"/api/export/{first}", f"/api/export/{first}?format=csv",
                 f"/api/estimates/{first}/observations", f"/api/equipment/{equipment}", f"/api/materials/equipment/{equipment}"):
        assert client.get(path).status_code == 404
    assert client.delete(f"/api/estimates/{first}").status_code == 404
    assert client.patch(f"/api/equipment/{equipment}", json={"name": "changed"}).status_code == 404
    assert client.delete(f"/api/equipment/{equipment}").status_code == 404
    assert client.post("/api/estimates/compare", json={"estimate_ids": [first, second], "reference_estimate_id": first,
                                                    "price_basis": "reference", "order_size_tons": 10}).status_code == 404
    assert client.post(f"/api/estimates/{first}/observations", json={"observed_price": 1, "observation_date": "2026-09-07",
                                                                                "source": "synthetic test only"}).status_code == 404


def test_auth_errors_never_echo_invalid_password(hosted_client):
    client, _, _ = hosted_client
    invalid = "synthetic-value-" * 30
    response = login(client, password=invalid)
    assert response.status_code == 422
    assert invalid not in response.text


def test_body_limit_applies_without_content_length(hosted_client):
    client, _, _ = hosted_client
    response = client.post("/api/auth/login", headers=HEADERS, content=iter([b"x" * (1024 * 1024)] * 3))
    assert response.status_code == 413


def test_password_salts_and_invalid_hash_fail_closed():
    first, second = hosted.hash_password(PASSWORD), hosted.hash_password(PASSWORD)
    assert first != second
    assert hosted.verify_password(PASSWORD, first)
    assert not hosted.verify_password(PASSWORD, "invalid")
    assert not hosted.verify_password(PASSWORD, None)


@pytest.mark.parametrize("identifier", ["../step_library", "..\\step_library", "C:\\private", "..%2fprivate"])
def test_template_inputs_cannot_access_files_outside_catalog(identifier):
    from fastapi import HTTPException

    from backend.routers.calculator import _load_template
    from backend.routers.materials import get_template

    with pytest.raises(ValueError):
        _load_template(identifier)
    with pytest.raises(HTTPException) as exc:
        get_template(identifier)
    assert exc.value.status_code == 404


def test_desktop_schema_creation_excludes_hosted_control_tables(monkeypatch, tmp_path):
    from sqlalchemy import inspect
    from sqlmodel import create_engine

    from backend import database

    engine = create_engine(f"sqlite:///{(tmp_path / 'local.db').as_posix()}")
    monkeypatch.setattr(database, "engine", engine)
    try:
        database.create_db_and_tables()
        tables = inspect(engine).get_table_names()
        assert "estimates" in tables
        assert not any(name.startswith("hosted_") for name in tables)
    finally:
        engine.dispose()


def test_missing_private_database_never_falls_back_to_desktop(hosted_client, monkeypatch, tmp_path):
    client, _, _ = hosted_client
    assert login(client).status_code == 200
    monkeypatch.setattr(hosted, "account_database_path", lambda _: tmp_path / "missing.db")
    assert client.get("/api/estimates").status_code == 503
    assert not (tmp_path / "missing.db").exists()
