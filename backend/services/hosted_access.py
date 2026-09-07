"""Server-side identity and account-private SQLite sessions for hosted mode."""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import time
from contextlib import contextmanager
from pathlib import Path
from threading import BoundedSemaphore
from urllib.parse import urlsplit

from fastapi import HTTPException, Request
from sqlalchemy import delete, inspect, text
from sqlmodel import Session, SQLModel, create_engine, select

from backend.config import settings
from backend.core.data_rights import check_data_rights
from backend.models import Equipment, Estimate, Material, MetalPrice
from backend.models.hosted import (
    HostedAccount,
    HostedAuditEvent,
    HostedLoginSession,
    HostedLoginThrottle,
    HostedOrganization,
)
from backend.paths import data_dir

COOKIE_NAME = "__Host-comet_session"
SESSION_SECONDS = 12 * 60 * 60
_PASSWORD_SLOTS = BoundedSemaphore(2)
_CONTROL_TABLES = [model.__table__ for model in (HostedAccount, HostedOrganization, HostedLoginSession, HostedLoginThrottle, HostedAuditEvent)]
_DATA_TABLES = [model.__table__ for model in (Equipment, Estimate, Material, MetalPrice)]
_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
_PUBLIC_API = {("GET", "/api/health"), ("GET", "/api/auth/session"), ("POST", "/api/auth/login")}


def cookie_name() -> str:
    return COOKIE_NAME if settings.hosted_origin.startswith("https:") else "comet_session_local"


def storage_root() -> Path:
    root = Path(settings.hosted_storage_dir)
    if not settings.hosted_storage_dir or not root.is_absolute():
        raise RuntimeError("Hosted storage requires an absolute private directory")
    root = root.resolve()
    source = Path(__file__).resolve().parents[2]
    if root == Path(root.anchor) or root.is_relative_to(source) or source.is_relative_to(root):
        raise RuntimeError("Hosted storage must be outside the source and static-file directories")
    return root


def validate_hosted_configuration() -> None:
    origin = urlsplit(settings.hosted_origin)
    local_http = (settings.hosted_allow_local_http and origin.scheme == "http"
                  and origin.hostname in {"127.0.0.1", "localhost", "::1"})
    if (not origin.hostname or origin.path or origin.query or origin.fragment or origin.username
            or origin.password or (origin.scheme != "https" and not local_http)):
        raise RuntimeError("Hosted origin must be one explicit HTTPS origin (local HTTP is opt-in)")
    if settings.debug or "*" in settings.allowed_hosts_list or origin.hostname not in settings.allowed_hosts_list:
        raise RuntimeError("Hosted mode requires debug off and an explicit matching allowed host")
    storage_root()


def _sqlite_engine(path: Path):
    return create_engine(f"sqlite:///{path.as_posix()}", connect_args={"check_same_thread": False, "timeout": 10})


def initialize_hosted_store() -> None:
    validate_hosted_configuration()
    if check_data_rights(data_dir(), Path(settings.hosted_rights_manifest), "commercial_use"):
        raise RuntimeError("Commercial data rights review has not passed; hosted service is disabled")
    root = storage_root()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    (root / "accounts").mkdir(exist_ok=True, mode=0o700)
    engine = _sqlite_engine(root / "control.db")
    try:
        SQLModel.metadata.create_all(engine, tables=_CONTROL_TABLES)
        existing = {column["name"] for column in inspect(engine).get_columns("hosted_organizations")}
        additions = {"status": "VARCHAR NOT NULL DEFAULT 'pending'", "starts_at": "FLOAT",
                     "ends_at": "FLOAT", "seat_limit": "INTEGER NOT NULL DEFAULT 1"}
        with engine.begin() as connection:
            for name, ddl in additions.items():
                if name not in existing:
                    connection.exec_driver_sql(f"ALTER TABLE hosted_organizations ADD COLUMN {name} {ddl}")
    finally:
        engine.dispose()


@contextmanager
def control_session():
    path = storage_root() / "control.db"
    if not path.is_file():
        raise RuntimeError("Hosted store has not been initialized")
    engine = _sqlite_engine(path)
    try:
        with Session(engine) as session:
            yield session
    finally:
        engine.dispose()


def account_database_path(account_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{32}", account_id):
        raise ValueError("Invalid server account identifier")
    root = storage_root()
    path = root / "accounts" / f"{account_id}.db"
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        raise RuntimeError("Redirected private database path")
    return path


def normalize_username(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9._@+-]{3,128}", value):
        raise ValueError("Account name must have 3–128 letters, digits or ._@+-")
    return value.casefold()


def hash_password(password: str) -> str:
    if not 15 <= len(password) <= 128:
        raise ValueError("Password must contain 15–128 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**17, r=8, p=1, maxmem=256 * 1024**2)
    return f"scrypt-17-8-1${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str | None) -> bool:
    if not 1 <= len(password) <= 128:
        return False
    try:
        method, salt, expected = encoded.split("$") if encoded else ("scrypt-17-8-1", "00" * 16, "00" * 64)
        if method != "scrypt-17-8-1" or len(salt) != 32 or len(expected) != 128:
            return False
        digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**17, r=8, p=1, maxmem=256 * 1024**2)
        return hmac.compare_digest(digest.hex(), expected) and encoded is not None
    except ValueError:
        return False


def create_organization(name: str, *, actor: str = "operator") -> HostedOrganization:
    from backend.services.hosted_subscription import audit_event

    if not name.strip() or len(name) > 200:
        raise ValueError("Organization name must have 1–200 characters")
    with control_session() as session:
        organization = HostedOrganization(name=name.strip())
        session.add(organization)
        audit_event(session, actor, "organization_created", organization.id)
        session.commit()
        session.refresh(organization)
        return organization


def create_account(organization_id: str, username: str, password: str, *, actor: str = "operator") -> HostedAccount:
    from backend.database import sync_material_library
    from backend.services.hosted_subscription import audit_event, require_available_seat

    username = normalize_username(username)
    password_hash = hash_password(password)
    with control_session() as session:
        session.exec(text("BEGIN IMMEDIATE"))
        if session.get(HostedOrganization, organization_id) is None:
            raise ValueError("Organization not found")
        require_available_seat(session, organization_id)
        if session.exec(select(HostedAccount).where(HostedAccount.username == username)).first():
            raise ValueError("Account already exists")
        account = HostedAccount(organization_id=organization_id, username=username, password_hash=password_hash)
        engine = _sqlite_engine(account_database_path(account.id))
        try:
            SQLModel.metadata.create_all(engine, tables=_DATA_TABLES)
            with Session(engine) as private:
                sync_material_library(private, force=True)
        finally:
            engine.dispose()
        session.add(account)
        audit_event(session, actor, "account_created", account.id, {"organization_id": organization_id})
        session.commit()
        session.refresh(account)
        return account


def set_account_enabled(account_id: str, enabled: bool, *, actor: str = "operator") -> None:
    from backend.services.hosted_subscription import audit_event, require_available_seat

    with control_session() as session:
        session.exec(text("BEGIN IMMEDIATE"))
        account = session.get(HostedAccount, account_id)
        if account is None:
            raise ValueError("Account not found")
        if enabled and not account.enabled:
            require_available_seat(session, account.organization_id)
        account.enabled = enabled
        session.add(account)
        if not enabled:
            session.exec(delete(HostedLoginSession).where(HostedLoginSession.account_id == account_id))
        audit_event(session, actor, "account_enabled" if enabled else "account_disabled", account.id)
        session.commit()


def _limit_login(username: str, client_host: str) -> None:
    window = int(time.time() // 60)
    keys = [("global", 60), ("account:" + username, 5), ("client:" + client_host, 20)]
    with control_session() as session:
        session.exec(text("BEGIN IMMEDIATE"))
        session.exec(delete(HostedLoginThrottle).where(HostedLoginThrottle.window < window - 10))
        for key, limit in keys:
            key = hashlib.sha256(key.encode()).hexdigest()
            row = session.get(HostedLoginThrottle, key)
            if row is None:
                row = HostedLoginThrottle(key=key, window=window)
            if row.window != window:
                row.window, row.attempts = window, 0
            if row.attempts >= limit:
                raise HTTPException(429, "Too many login attempts; try again later", headers={"Retry-After": "60"})
            row.attempts += 1
            session.add(row)
        session.commit()


def sign_in(username: str, password: str, client_host: str, previous_token: str | None):
    from backend.services.hosted_subscription import audit_event

    username = normalize_username(username)
    _limit_login(username, client_host)
    if not _PASSWORD_SLOTS.acquire(blocking=False):
        raise HTTPException(429, "Login service is busy; try again later", headers={"Retry-After": "5"})
    try:
        with control_session() as session:
            account = session.exec(select(HostedAccount).where(HostedAccount.username == username)).first()
            valid = verify_password(password, account.password_hash if account else None)
            if not valid or not account or not account.enabled:
                raise HTTPException(401, "Invalid account or password")
            now = time.time()
            session.exec(delete(HostedLoginSession).where(HostedLoginSession.expires_at <= now))
            if previous_token:
                previous = session.get(HostedLoginSession, hashlib.sha256(previous_token.encode()).hexdigest())
                if previous:
                    session.delete(previous)
            # Bound active session storage even after repeated valid logins.
            old = session.exec(select(HostedLoginSession).where(HostedLoginSession.account_id == account.id)
                               .order_by(HostedLoginSession.expires_at.desc())).all()
            for record in old[4:]:
                session.delete(record)
            token = secrets.token_urlsafe(32)
            session.add(HostedLoginSession(token_hash=hashlib.sha256(token.encode()).hexdigest(),
                                          account_id=account.id, expires_at=now + SESSION_SECONDS))
            audit_event(session, account.id, "signed_in", account.id)
            session.commit()
            session.refresh(account)
            return account, token
    finally:
        _PASSWORD_SLOTS.release()


def account_for_request(request: Request) -> HostedAccount | None:
    token = request.cookies.get(cookie_name(), "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
        return None
    with control_session() as session:
        login = session.get(HostedLoginSession, hashlib.sha256(token.encode()).hexdigest())
        if login is None or login.expires_at <= time.time():
            return None
        account = session.get(HostedAccount, login.account_id)
        if not account or not account.enabled or session.get(HostedOrganization, account.organization_id) is None:
            return None
        return account


def authorize_hosted_request(request: Request) -> None:
    if not settings.hosted_mode or not request.url.path.startswith("/api/"):
        return
    if settings.hosted_allow_local_http and settings.hosted_origin.startswith("http:"):
        if not request.client or request.client.host not in {"127.0.0.1", "::1", "testclient"}:
            raise HTTPException(403, "Local HTTP testing accepts loopback clients only")
    if request.method not in _SAFE_METHODS:
        if (request.headers.get("Origin") != settings.hosted_origin
                or request.headers.get("X-Comet-Request") != "1"):
            raise HTTPException(403, "Same-origin application request required")
    if (request.method, request.url.path) in _PUBLIC_API:
        return
    account = account_for_request(request)
    if account is None:
        raise HTTPException(401, "Sign in required")
    request.state.hosted_account = account
    from backend.services.hosted_subscription import enforce_subscription

    enforce_subscription(request, account)


@contextmanager
def private_session(request: Request):
    # Resolve identity again if invoked independently of the app dependency.
    account = getattr(request.state, "hosted_account", None) or account_for_request(request)
    if account is None:
        raise HTTPException(401, "Sign in required")
    path = account_database_path(account.id)
    if not path.is_file():
        raise HTTPException(503, "Private storage is unavailable")
    engine = _sqlite_engine(path)
    try:
        with Session(engine) as session:
            yield session
    finally:
        engine.dispose()


def sign_out(request: Request) -> None:
    from backend.services.hosted_subscription import audit_event

    token = request.cookies.get(cookie_name(), "")
    with control_session() as session:
        record = session.get(HostedLoginSession, hashlib.sha256(token.encode()).hexdigest())
        if record:
            audit_event(session, record.account_id, "signed_out", record.account_id)
            session.delete(record)
            session.commit()


def reset_account_password(account_id: str, password: str, *, actor: str) -> None:
    from backend.services.hosted_subscription import audit_event

    encoded = hash_password(password)
    with control_session() as session:
        session.exec(text("BEGIN IMMEDIATE"))
        account = session.get(HostedAccount, account_id)
        if not account:
            raise ValueError("Account not found")
        account.password_hash = encoded
        session.add(account)
        session.exec(delete(HostedLoginSession).where(HostedLoginSession.account_id == account_id))
        audit_event(session, actor, "password_reset", account_id)
        session.commit()


def change_password(account_id: str, current_password: str, new_password: str, client_host: str) -> None:
    from backend.services.hosted_subscription import audit_event

    _limit_login(account_id, client_host)
    if not _PASSWORD_SLOTS.acquire(blocking=False):
        raise HTTPException(429, "Login service is busy; try again later")
    try:
        with control_session() as session:
            session.exec(text("BEGIN IMMEDIATE"))
            account = session.get(HostedAccount, account_id)
            if not account or not account.enabled or not verify_password(current_password, account.password_hash):
                raise HTTPException(401, "Invalid account or password")
            account.password_hash = hash_password(new_password)
            session.add(account)
            session.exec(delete(HostedLoginSession).where(HostedLoginSession.account_id == account_id))
            audit_event(session, account_id, "password_changed", account_id)
            session.commit()
    finally:
        _PASSWORD_SLOTS.release()
