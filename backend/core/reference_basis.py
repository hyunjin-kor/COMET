"""Reference price basis for the paper: monthly averages from institutional series.

The desktop app shows live quotes. The paper prices from monthly averages
instead (IMF Primary Commodity Prices; Johnson Matthey base prices averaged by
month), because those can be cited, are archived by their publishers, and do
not depend on the day the tool was run. These helpers turn the frozen history
written by scripts/fetch_price_history.py into a price map in the shape
decision_engine._latest_price_map returns, so every analysis script can take it
through --price-basis.
"""

from __future__ import annotations

import calendar
from datetime import date
from statistics import mean
from typing import Any


def monthly_average(points: list[dict], *, exclude_month: str | None = None) -> list[dict]:
    """Average observations by calendar month, dated at month end.

    ``exclude_month`` (YYYY-MM) drops a month that is still running, so a
    partial average never enters the record.
    """
    by_month: dict[str, list[float]] = {}
    for point in points:
        month = str(point["date"])[:7]
        if month == exclude_month:
            continue
        by_month.setdefault(month, []).append(float(point["price"]))
    out: list[dict] = []
    for month in sorted(by_month):
        year, mon = int(month[:4]), int(month[5:7])
        last_day = date(year, mon, calendar.monthrange(year, mon)[1])
        out.append({"date": last_day.isoformat(), "price": round(mean(by_month[month]), 4)})
    return out


def latest_common_month(series: dict[str, dict[str, Any]]) -> str:
    """Latest YYYY-MM that every series has an observation in."""
    months: set[str] | None = None
    for entry in series.values():
        have = {str(p["date"])[:7] for p in entry["points"]}
        months = have if months is None else months & have
    if not months:
        raise ValueError("no month is covered by every series")
    return max(months)


def truncate_series(series: dict[str, dict[str, Any]], month: str) -> dict[str, dict[str, Any]]:
    """Drop every point after ``month`` and refresh first/last/n."""
    out: dict[str, dict[str, Any]] = {}
    for symbol, entry in series.items():
        points = [p for p in entry["points"] if str(p["date"])[:7] <= month]
        out[symbol] = {
            **entry,
            "points": points,
            "first": points[0]["date"] if points else None,
            "last": points[-1]["date"] if points else None,
            "n": len(points),
        }
    return out


def build_price_basis(
    series: dict[str, dict[str, Any]],
    month: str,
    anchors: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Price map for one month: series values where a series exists, anchors elsewhere.

    ``anchors`` is get_reference_prices(): USGS annual averages and escalated
    CatCost values for metals with no published series. A series with no
    observation in ``month`` raises rather than falling back silently.
    """
    basis: dict[str, dict[str, Any]] = {}
    for symbol, entry in series.items():
        point = next((p for p in entry["points"] if str(p["date"])[:7] == month), None)
        if point is None:
            raise ValueError(f"{symbol}: no observation in {month}")
        basis[symbol] = {
            "symbol": symbol,
            "name": (anchors.get(symbol) or {}).get("name", symbol),
            "price": float(point["price"]),
            "unit": entry["unit"],
            "source": entry["source"],
            "fetched_at": point["date"],
        }
    for symbol, info in anchors.items():
        if symbol not in basis:
            basis[symbol] = {"symbol": symbol, **info}
    return basis
