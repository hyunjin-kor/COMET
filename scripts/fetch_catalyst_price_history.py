"""Fetch monthly traded unit values for finished catalysts from the free, keyless preview API.

Heading 3815 of the Harmonized System covers catalytic preparations, and its four
subheadings separate them by active substance. United States import unit values for those
subheadings are the only free public series found that price finished catalysts rather than
their raw materials, so they give an external reference for the estimator that is not
derived from the same cost method.

A unit value aggregates every grade, loading, formulation and order size traded under one
code in one month, so it is a market level for a category, not a quote for a formulation.
It is used in the paper as a range to compare against, never as a target to fit.

No credentials are used or sent and no subscription endpoint is called, matching
scripts/fetch_support_history.py. HTTP 429 stops the run without retrying, every response
or failure is retained beside its status, and an existing output file is resumed rather
than refetched. Run:

    python scripts/fetch_catalyst_price_history.py --start 2019-01 --end 2026-05 --out docs/paper/catalyst_market_2026-09-10.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, date, datetime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.core.comtrade_snapshot import PREVIEW_API, parse_preview, preview_params  # noqa: E402
from backend.services.price_scheduler import _months_between  # noqa: E402

REPORTER = "842"
CATALOG = [
    {"id": "HS381511", "hs": "381511", "active": "nickel",
     "name": "Supported catalysts with nickel or nickel compounds as the active substance",
     "note": "Covers reforming, methanation, hydrogenation and ammonia-related nickel catalysts of every "
             "loading and support."},
    {"id": "HS381512", "hs": "381512", "active": "precious metal",
     "name": "Supported catalysts with precious metal or precious metal compounds as the active substance",
     "note": "Mixes automotive, refining and chemical platinum-group and silver catalysts, so the unit value "
             "follows the metal content of whatever traded that month."},
    {"id": "HS381519", "hs": "381519", "active": "other",
     "name": "Supported catalysts with an active substance other than nickel or precious metals",
     "note": "Copper, iron, cobalt, chromium, molybdenum and zeolite-supported catalysts."},
    {"id": "HS381590", "hs": "381590", "active": "unsupported",
     "name": "Unsupported reaction initiators, accelerators and catalytic preparations",
     "note": "Bulk oxides and unsupported preparations; the cheapest category and the least like a finished "
             "supported catalyst."},
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="YYYY-MM, inclusive")
    parser.add_argument("--end", required=True, help="YYYY-MM, inclusive")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--sleep", type=float, default=12.0, help="seconds between requests")
    args = parser.parse_args()
    start, end = date.fromisoformat(args.start + "-01"), date.fromisoformat(args.end + "-01")
    periods = _months_between(start, end)
    if not periods or end >= date.today().replace(day=1):
        parser.error("request completed calendar months")

    output = {"generated_at": datetime.now(UTC).isoformat(), "endpoint": PREVIEW_API,
              "access": "free public preview; no credentials", "source": "UN Comtrade",
              "policy_url": "https://uncomtrade.org/docs/policy-on-use-and-re-dissemination/",
              "reporter_code": REPORTER, "flow_code": "M", "unit": "$/kg",
              "scope": "United States import unit values for the four subheadings of HS 3815, customs value "
                       "divided by net weight. All grades, loadings and partners are combined, so a series is a "
                       "category market level, not a catalyst-grade quote.",
              "requested_months": periods, "catalog": CATALOG, "series": {}, "requests": []}
    if args.out.is_file():
        previous = json.loads(args.out.read_text(encoding="utf-8"))
        if previous.get("endpoint") == PREVIEW_API and previous.get("catalog") == CATALOG:
            output["requests"] = previous.get("requests", [])
            output["series"] = previous.get("series", {})
            output["generated_at"] = previous.get("generated_at", output["generated_at"])
    done = {(r["symbol"], r["period"]) for r in output["requests"] if r["status"] != "unverified"}

    args.out.parent.mkdir(parents=True, exist_ok=True)
    stopped = False
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        for entry in CATALOG:
            points = {p["date"]: p for p in output["series"].get(entry["id"], {}).get("points", [])}
            for period in periods:
                if (entry["id"], period) in done:
                    continue
                params = preview_params(entry["hs"], period, REPORTER)
                record = {"symbol": entry["id"], "period": period, "status": "unverified"}
                try:
                    response = client.get(PREVIEW_API, params=params)
                    record.update(url=str(response.url), http_status=response.status_code)
                    stopped = response.status_code == 429
                    response.raise_for_status()
                    payload = response.json()
                    record["response"] = payload
                    point = parse_preview(payload, entry["hs"], period, REPORTER)
                    record["status"] = "accepted" if point else "not_published"
                    if point:
                        points[point["date"]] = point
                except (httpx.HTTPError, ValueError, TypeError) as exc:
                    record["reason"] = str(exc)
                output["requests"].append(record)
                ordered = [points[k] for k in sorted(points)]
                if ordered:
                    output["series"][entry["id"]] = {
                        "name": entry["name"], "active_substance": entry["active"], "hs": entry["hs"],
                        "unit": "$/kg", "source": "UN Comtrade (monthly import unit value)",
                        "cadence": "monthly_unit_value", "grade_note": entry["note"],
                        "points": ordered, "first": ordered[0]["date"], "last": ordered[-1]["date"],
                        "n": len(ordered)}
                args.out.write_text(json.dumps(output, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
                print(f"{entry['id']} {period}: {record['status']}", flush=True)
                if stopped:
                    break
                time.sleep(args.sleep)
            if stopped:
                break
    accepted = sum(1 for r in output["requests"] if r["status"] == "accepted")
    print(f"Saved {len(output['series'])} series, {accepted} accepted observations, "
          f"{len(output['requests'])} requests to {args.out}")
    if stopped:
        sys.exit(1)


if __name__ == "__main__":
    main()
