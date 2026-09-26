"""Local operator commands for reviewed B2B accounts; never a public admin API."""

import argparse
import getpass
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlmodel import select  # noqa: E402

from backend.config import settings  # noqa: E402
from backend.models.hosted import HostedAccount, HostedAuditEvent, HostedOrganization  # noqa: E402
from backend.services import hosted_access as hosted  # noqa: E402
from backend.services.hosted_subscription import set_subscription, subscription_state  # noqa: E402


def instant(value):
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("Use an ISO timestamp with an explicit UTC offset")
    return parsed.timestamp()


def private_password():
    # Do not silently fall back to echoed/redirected input on an unattended host.
    if not sys.stdin.isatty():
        raise ValueError("Password provisioning requires an interactive private terminal")
    password = getpass.getpass("New password: ")
    if password != getpass.getpass("Confirm new password: "):
        raise ValueError("Passwords do not match")
    return password


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--actor", help="Operator identifier recorded for each administrative change")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("initialize", help="Validate commercial data review and initialize/migrate the private control store")
    organization = commands.add_parser("organization", help="Create a pending organization; does not activate a subscription")
    organization.add_argument("name")
    account = commands.add_parser("account", help="Provision one account within the recorded seat limit")
    account.add_argument("--organization", required=True)
    account.add_argument("--username", required=True)
    contract = commands.add_parser("subscription", help="Record an already authorized contract period and seat limit")
    contract.add_argument("--organization", required=True)
    contract.add_argument("--status", choices=["pending", "active", "revoked"], required=True)
    contract.add_argument("--starts-at", type=instant)
    contract.add_argument("--ends-at", type=instant)
    contract.add_argument("--seats", type=int, required=True)
    contract.add_argument("--reason", choices=["contract_recorded", "contract_renewed", "customer_request", "security_review", "correction"], required=True)
    for name in ("enable-account", "disable-account", "reset-password"):
        commands.add_parser(name).add_argument("account_id")
    commands.add_parser("status", help="Show contract/account metadata only")
    audit = commands.add_parser("audit", help="Show bounded administrative/security events without research content")
    audit.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    if not settings.hosted_mode:
        parser.error("HOSTED_MODE must be explicitly enabled")
    hosted.validate_hosted_configuration()
    if args.command not in {"status", "audit"} and (not args.actor or not args.actor.strip() or len(args.actor) > 128):
        parser.error("A nonempty --actor of at most128 characters is required")
    try:
        if args.command == "initialize":
            hosted.initialize_hosted_store()
            result = {"status": "initialized"}
        elif args.command == "organization":
            item = hosted.create_organization(args.name, actor=args.actor)
            result = {"organization_id": item.id, "status": item.status}
        elif args.command == "account":
            item = hosted.create_account(args.organization, args.username, private_password(), actor=args.actor)
            result = {"account_id": item.id, "organization_id": item.organization_id}
        elif args.command == "subscription":
            item = set_subscription(args.organization, status=args.status, starts_at=args.starts_at,
                                    ends_at=args.ends_at, seat_limit=args.seats, actor=args.actor, reason=args.reason)
            result = {"organization_id": item.id, "status": subscription_state(item), "seat_limit": item.seat_limit}
        elif args.command in {"enable-account", "disable-account"}:
            hosted.set_account_enabled(args.account_id, args.command == "enable-account", actor=args.actor)
            result = {"account_id": args.account_id, "enabled": args.command == "enable-account"}
        elif args.command == "reset-password":
            hosted.reset_account_password(args.account_id, private_password(), actor=args.actor)
            result = {"account_id": args.account_id, "status": "password_reset_sessions_revoked"}
        else:
            with hosted.control_session() as session:
                if args.command == "status":
                    organizations = session.exec(select(HostedOrganization).order_by(HostedOrganization.name, HostedOrganization.id)).all()
                    accounts = session.exec(select(HostedAccount).order_by(HostedAccount.username)).all()
                    result = {"organizations": [dict(id=o.id, name=o.name, status=subscription_state(o), starts_at=o.starts_at,
                                                     ends_at=o.ends_at, seats=o.seat_limit) for o in organizations],
                              "accounts": [dict(id=a.id, username=a.username, organization_id=a.organization_id, enabled=a.enabled) for a in accounts]}
                else:
                    if not 1 <= args.limit <= 500:
                        raise ValueError("Audit limit must be between1 and500")
                    events = session.exec(select(HostedAuditEvent).order_by(HostedAuditEvent.at.desc(), HostedAuditEvent.id).limit(args.limit)).all()
                    result = {"events": [event.model_dump() for event in events]}
        print(json.dumps(result, ensure_ascii=True, indent=2))
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
