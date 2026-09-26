"""Freeze dated public daily prices for a separate catalyst crossover replay."""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import html
import io
import json
import re
import sys
from datetime import UTC, date, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.core.price_fetcher import (  # noqa: E402
    WESTMETALL_FIELDS,
    fetch_johnson_matthey,
    fetch_westmetall_history,
)

JM_URL = "https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management"
WM_URL = "https://www.westmetall.com/en/markdaten.php"
JM_COLUMNS = {"Platinum": "Pt", "Palladium": "Pd", "Rhodium": "Rh", "Iridium": "Ir", "Ruthenium": "Ru"}


def parse_daily_csv(raw: str) -> dict:
    """The explicit New York DAILY download, with strict header/date checks."""
    lines = [line for line in raw.splitlines() if line.strip()]
    if lines[0].strip() != "Daily PGM prices for New York":
        raise ValueError("Expected New York daily PGM prices")
    reader = csv.DictReader(io.StringIO("\n".join(lines[1:])))
    if reader.fieldnames != ["Date", *JM_COLUMNS]:
        raise ValueError("Unexpected PGM column order")
    result = {symbol: [] for symbol in JM_COLUMNS.values()}
    for row in reader:
        day = datetime.strptime(row["Date"], "%d-%b-%Y").date().isoformat()
        for name, symbol in JM_COLUMNS.items():
            result[symbol].append({"date": day, "price": float(row[name])})
    return result


async def daily_jm(start: date, end: date) -> tuple[dict, str, str]:
    # The default chart request aggregates long ranges. The public CSV control
    # explicitly sets DAILY and region USA. Its export values have fixed metal
    # order, so request that order rather than silently relabeling the columns.
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
        page = (await client.get(JM_URL)).text
        portlet = re.search(r'id="getPortletId"[^>]*value="([^"]+)"', page).group(1)
        url = html.unescape(re.search(r'id="getUrl"[^>]*>(.*?)</', page, re.S).group(1).strip())
        payload = {f"{portlet}selectedMetal{i}": symbol for i, symbol in enumerate(JM_COLUMNS.values())}
        payload.update({f"{portlet}start_Date": start.strftime("%d-%m-%Y"),
                        f"{portlet}end_Date": end.strftime("%d-%m-%Y"),
                        f"{portlet}IntervalType": "DAILY", f"{portlet}selectedRegion": "USA"})
        response = await client.post(url, data=payload, headers={"X-Requested-With": "XMLHttpRequest"})
        response.raise_for_status()
        download = response.json()["url"]
        response = await client.get(download)
        response.raise_for_status()
        raw = response.text
    return parse_daily_csv(raw), raw, download


async def fetch(start: date, end: date) -> dict:
    series, failures = {}, {}
    jm, raw, download = await daily_jm(start, end)
    for symbol in JM_COLUMNS.values():
        rows = (jm or {}).get(symbol, [])
        if rows:
            series[symbol] = {"source": "Johnson Matthey New York daily base price", "url": JM_URL,
                              "download_url": download, "request_interval": "DAILY", "region": "USA",
                              "unit": "$/troy_oz", "points": rows}
        else:
            failures[symbol] = "확인 못 함: Johnson Matthey returned no daily observations"
    # A separate current quotation checks the end of the daily response.
    current = await fetch_johnson_matthey()
    checked = []
    for symbol, rows in jm.items():
        quote = current.get(symbol)
        last = rows[-1]
        if quote and quote["fetched_at"][:10] == last["date"]:
            if last["price"] != quote["price"]:
                raise ValueError(f"{symbol}: daily export/current quote mismatch; reject column mapping")
            checked.append(symbol)
    if len(checked) != len(JM_COLUMNS):
        raise ValueError("Current quote cross-check unavailable for all five PGM columns")
    semaphore = asyncio.Semaphore(2)

    async def westmetall(symbol):
        async with semaphore:
            return symbol, await fetch_westmetall_history(symbol)

    for symbol, rows in await asyncio.gather(*(westmetall(s) for s in WESTMETALL_FIELDS)):
        if rows:
            series[symbol] = {"source": "Westmetall LME cash settlement",
                              "url": f"{WM_URL}?action=table&field={WESTMETALL_FIELDS[symbol]}",
                              "unit": "$/lb", "conversion": "USD per metric tonne / 2204.62, rounded to 4 decimals",
                              "points": rows}
        else:
            failures[symbol] = "확인 못 함: Westmetall returned no daily observations"
    for symbol, entry in series.items():
        points = [p for p in entry["points"] if start.isoformat() <= p["date"] <= end.isoformat()]
        if len({p["date"] for p in points}) != len(points):
            raise ValueError(f"{symbol}: duplicate daily observations")
        if not points or any(not 0 < float(p["price"]) < float("inf") for p in points):
            raise ValueError(f"{symbol}: missing or invalid daily observations")
        entry.update(points=points, first=points[0]["date"], last=points[-1]["date"], n=len(points), cadence="daily")
    if not series:
        raise ValueError(f"No public observations obtained: {failures}")
    return {"retrieved_at": datetime.now(UTC).isoformat(), "requested_start": start.isoformat(),
            "requested_end": end.isoformat(), "series": series, "failures": failures,
            "current_jm_quotes": current,
            "jm_latest_column_crosschecks": checked,
            "jm_daily_csv": raw,
            "scope": "Public daily observations, no paid or authenticated price APIs. Current quotes are not substituted for historical gaps.",
            "rights_note": "Publicly accessible prices do not establish redistribution rights; source terms remain applicable.",
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "fetcher_sha256": hashlib.sha256((ROOT / "backend/core/price_fetcher.py").read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default=date.today().isoformat())
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Use a new output path to preserve the previous observation snapshot")
    result = asyncio.run(fetch(date.fromisoformat(args.start), date.fromisoformat(args.end)))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"series": {s: {k: e[k] for k in ("n", "first", "last", "unit")}
                                  for s, e in result["series"].items()}, "failures": result["failures"],
                      "current_jm_quotes": result["current_jm_quotes"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
