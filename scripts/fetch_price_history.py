"""Fetch and freeze the reference price history for the paper analysis.

The desktop app prices day to day from live feeds (Yahoo Finance futures,
Johnson Matthey daily base prices, Westmetall's LME settlements). The paper
does not: it prices from institutional monthly averages, which can be cited
and re-costed from without depending on the day the tool was run. This script
pulls those series and writes one file that `price_volatility_screen.py`,
`active_metal_breakeven.py` and `build_reference_basis.py` read without a
network round trip.

  IMF PCPS          Al Cu Ni Zn Sn Co Mo Au Ag   monthly averages as published
  Johnson Matthey   Pt Pd Rh Ru Ir               daily base prices averaged by month

Every series is cut at the latest month all of them cover (IMF publishes a
month early in the next one), so the file is rectangular and the running,
incomplete month never enters a replay. W, Re, V and Fe have no published
series and take their USGS or CatCost anchors in `build_reference_basis.py`.

Run:  python scripts/fetch_price_history.py --out docs/paper/price_history_<date>.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.core.price_fetcher import fetch_reference_series  # noqa: E402


def _series(entry: dict[str, Any]) -> dict[str, Any]:
    points = sorted(entry["points"], key=lambda p: p["date"])
    return {
        "source": entry["source"],
        "unit": entry["unit"],
        "cadence": "monthly_average",
        "points": points,
        "first": points[0]["date"] if points else None,
        "last": points[-1]["date"] if points else None,
        "n": len(points),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--start", default="2019-01-01", help="first month to keep, as a date")
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end = date.today()
    raw, failures = asyncio.run(fetch_reference_series(start, end))
    if not raw:
        raise SystemExit(f"no series fetched: {failures}")

    series = {symbol: _series(entry) for symbol, entry in raw.items()}
    last_month = max(entry["last"][:7] for entry in series.values())

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "requested": {"start": args.start, "end": end.isoformat()},
        "cadence": "monthly_average",
        "last_month": last_month,
        "failures": failures,
        "series": series,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=1), encoding="utf-8")

    print(f"{'symbol':<8}{'source':<36}{'n':>6}  {'first':<12}{'last':<12}")
    for symbol, entry in sorted(series.items()):
        print(f"{symbol:<8}{entry['source']:<36}{entry['n']:>6}  "
              f"{entry['first'] or '-':<12}{entry['last'] or '-':<12}")
    print(f"all series cut at {last_month}")
    if failures:
        print("failures:")
        for key, message in sorted(failures.items()):
            print(f"  {key}: {message}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
