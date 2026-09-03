"""Fetch and freeze long-run metal price history for the paper analysis.

The recorded prices in the application database only start when the app was
first run, which is too short a window to say anything about price sensitivity.
This pulls the published history from the three feeds COMET already uses and
writes it to one file so `price_volatility_screen.py` can replay it without a
network round trip and the numbers stay reproducible.

Coverage differs by feed, and the analysis has to respect that rather than
paper over it:

  Johnson Matthey   Ru Rh Pt Pd Ir     monthly, 2019 onward
  Yahoo Finance     Pt Pd Au Ag Cu Al  daily, five years
  Westmetall (LME)  Ni Zn Sn           daily, current year only
  IMF PCPS          Co                 monthly average, from --start (series begins 1992)

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

from backend.core.price_fetcher import (  # noqa: E402
    IMF_PCPS_SERIES,
    JM_HISTORY_SYMBOLS,
    WESTMETALL_FIELDS,
    YAHOO_METALS,
    fetch_history,
    fetch_imf_pcps_history,
    fetch_johnson_matthey_history,
    fetch_westmetall_history,
)

YAHOO_UNITS = {symbol: unit for symbol, _ticker, _name, unit, _factor in YAHOO_METALS}
JM_UNIT = "$/troy_oz"
WESTMETALL_UNIT = "$/lb"
IMF_UNIT = "$/lb"


def _series(rows: list[dict], unit: str, source: str) -> dict[str, Any]:
    points = [
        {"date": row["date"], "price": float(row["price"])}
        for row in rows
        if row.get("price") is not None
    ]
    points.sort(key=lambda p: p["date"])
    return {
        "source": source,
        "unit": unit,
        "points": points,
        "first": points[0]["date"] if points else None,
        "last": points[-1]["date"] if points else None,
        "n": len(points),
    }


async def collect(start: date, end: date, yahoo_period: str, pause_s: float) -> dict[str, Any]:
    """Fetch every feed, one symbol at a time, tolerating individual failures."""
    series: dict[str, dict[str, Any]] = {}
    failures: dict[str, str] = {}

    try:
        jm = await fetch_johnson_matthey_history(start, end)
        for symbol in JM_HISTORY_SYMBOLS:
            rows = (jm or {}).get(symbol) or []
            if rows:
                series[symbol] = _series(rows, JM_UNIT, "Johnson Matthey (live)")
            else:
                failures[symbol] = "johnson matthey returned no rows"
    except Exception as exc:  # noqa: BLE001 - one dead feed must not lose the others
        failures["_johnson_matthey"] = f"{type(exc).__name__}: {exc}"

    for symbol in YAHOO_UNITS:
        # Yahoo rate-limits bursts; a short pause keeps the whole run under one quota.
        await asyncio.sleep(pause_s)
        try:
            rows = await fetch_history(symbol, yahoo_period)
        except Exception as exc:  # noqa: BLE001
            failures[f"yahoo:{symbol}"] = f"{type(exc).__name__}: {exc}"
            continue
        if not rows:
            failures[f"yahoo:{symbol}"] = "empty response (rate limited?)"
            continue
        # Johnson Matthey is the settlement reference for PGMs; keep it where both exist.
        if symbol not in series:
            series[symbol] = _series(rows, YAHOO_UNITS[symbol], "Yahoo Finance (live)")
        else:
            series[symbol]["alternate_yahoo"] = _series(
                rows, YAHOO_UNITS[symbol], "Yahoo Finance (live)"
            )

    for symbol in WESTMETALL_FIELDS:
        try:
            rows = await fetch_westmetall_history(symbol)
        except Exception as exc:  # noqa: BLE001
            failures[f"westmetall:{symbol}"] = f"{type(exc).__name__}: {exc}"
            continue
        if rows:
            series[symbol] = _series(rows, WESTMETALL_UNIT, "Westmetall (LME settlement)")
        else:
            failures[f"westmetall:{symbol}"] = "empty response"

    for symbol in IMF_PCPS_SERIES:
        try:
            rows = await fetch_imf_pcps_history(symbol, start)
        except Exception as exc:  # noqa: BLE001
            failures[f"imf:{symbol}"] = f"{type(exc).__name__}: {exc}"
            continue
        if rows:
            series[symbol] = _series(rows, IMF_UNIT, "IMF PCPS (monthly average)")
        else:
            failures[f"imf:{symbol}"] = "empty response"

    return {"series": series, "failures": failures}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--start", default="2019-01-01", help="Johnson Matthey and IMF history start")
    parser.add_argument("--yahoo-period", default="5y")
    parser.add_argument("--pause", type=float, default=3.0, help="seconds between Yahoo calls")
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end = date.today()
    result = asyncio.run(collect(start, end, args.yahoo_period, args.pause))

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "requested": {
            "johnson_matthey_start": args.start,
            "yahoo_period": args.yahoo_period,
            "end": end.isoformat(),
        },
        "failures": result["failures"],
        "series": result["series"],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=1), encoding="utf-8")

    print(f"{'symbol':<8}{'source':<32}{'n':>6}  {'first':<12}{'last':<12}")
    for symbol, entry in sorted(result["series"].items()):
        print(f"{symbol:<8}{entry['source']:<32}{entry['n']:>6}  "
              f"{entry['first'] or '-':<12}{entry['last'] or '-':<12}")
    if result["failures"]:
        print("\nfailures:")
        for key, message in sorted(result["failures"].items()):
            print(f"  {key}: {message}")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
