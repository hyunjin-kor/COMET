"""Manually recorded B2B entitlements; no payment processor or client grants."""

import json
import math
import time

from fastapi import HTTPException, Request
from sqlalchemy import func, text
from sqlmodel import Session, select

from backend.models.hosted import HostedAccount, HostedAuditEvent, HostedOrganization
from backend.services.hosted_access import control_session

_REASONS = {"contract_recorded", "contract_renewed", "customer_request", "security_review", "correction"}
_READ_PREFIXES = ("/api/estimates", "/api/export", "/api/materials", "/api/equipment", "/api/prices", "/api/indices", "/api/templates", "/api/account")


def subscription_state(organization: HostedOrganization, *, now: float | None = None) -> str:
    now = time.time() if now is None else now
    if organization.status == "revoked":
        return "revoked"
    if (organization.status != "active" or organization.starts_at is None or organization.ends_at is None
            or not all(math.isfinite(value) for value in (organization.starts_at, organization.ends_at))):
        return "pending"
    if now >= organization.ends_at:
        return "expired"
    return "pending" if now < organization.starts_at else "active"


def audit_event(session: Session, actor: str, action: str, target_id: str, details: dict | None = None):
    if not actor.strip() or len(actor) > 128:
        raise ValueError("An operator or account identifier is required")
    session.add(HostedAuditEvent(at=time.time(), actor=actor, action=action, target_id=target_id,
                                details_json=json.dumps(details or {}, sort_keys=True, allow_nan=False)))


def enabled_seats(session: Session, organization_id: str) -> int:
    return session.exec(select(func.count()).select_from(HostedAccount).where(
        HostedAccount.organization_id == organization_id, HostedAccount.enabled == True)).one()  # noqa: E712


def require_available_seat(session: Session, organization_id: str):
    organization = session.get(HostedOrganization, organization_id)
    if not organization:
        raise ValueError("Organization not found")
    if enabled_seats(session, organization_id) >= organization.seat_limit:
        raise ValueError("No available subscription seat")


def set_subscription(organization_id: str, *, status: str, starts_at: float | None, ends_at: float | None,
                     seat_limit: int, actor: str, reason: str) -> HostedOrganization:
    if status not in {"pending", "active", "revoked"} or reason not in _REASONS:
        raise ValueError("Invalid subscription status or reason")
    if isinstance(seat_limit, bool) or not isinstance(seat_limit, int) or not 1 <= seat_limit <= 1000:
        raise ValueError("Subscription seat limit must be between1 and1000")
    if ((starts_at is None) != (ends_at is None) or (status == "active" and starts_at is None)
            or (starts_at is not None and (not all(math.isfinite(v) for v in (starts_at, ends_at)) or ends_at <= starts_at))):
        raise ValueError("Subscription requires a valid explicit start/end period")
    with control_session() as session:
        session.exec(text("BEGIN IMMEDIATE"))
        organization = session.get(HostedOrganization, organization_id)
        if not organization:
            raise ValueError("Organization not found")
        if enabled_seats(session, organization_id) > seat_limit:
            raise ValueError("Seat limit is below currently enabled accounts; review seats explicitly")
        before = {key: getattr(organization, key) for key in ("status", "starts_at", "ends_at", "seat_limit")}
        organization.status, organization.starts_at, organization.ends_at, organization.seat_limit = status, starts_at, ends_at, seat_limit
        session.add(organization)
        after = {key: getattr(organization, key) for key in before}
        audit_event(session, actor, "subscription_updated", organization.id, {"reason": reason, "before": before, "after": after})
        session.commit()
        session.refresh(organization)
        return organization


def subscription_view(organization_id: str) -> dict:
    with control_session() as session:
        organization = session.get(HostedOrganization, organization_id)
        if not organization:
            raise HTTPException(401, "Sign in required")
        status = subscription_state(organization)
        return {"status": status, "can_start_work": status == "active", "starts_at": organization.starts_at,
                "ends_at": organization.ends_at, "seat_limit": organization.seat_limit}


def enforce_subscription(request: Request, account: HostedAccount) -> None:
    path = request.url.path
    if request.method == "POST" and path in {"/api/auth/logout", "/api/auth/password"}:
        return
    if request.method in {"GET", "HEAD"}:
        if path in {"/api/decision/benchmarks", "/api/lca/factors"}:
            return
        if path != "/api/templates/costs" and any(path == prefix or path.startswith(prefix + "/") for prefix in _READ_PREFIXES):
            return
    if not subscription_view(account.organization_id)["can_start_work"]:
        raise HTTPException(403, "Subscription is inactive; saved data can still be viewed and exported")
