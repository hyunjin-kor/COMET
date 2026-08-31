"""Metal prices API endpoints — live via yfinance + DB cache."""

from __future__ import annotations

import asyncio
import re
import time
from datetime import date, timedelta
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from backend.core.decision_engine import list_benchmark_catalogs
from backend.core.price_evidence import describe_price_evidence
from backend.core.price_fetcher import (
    WESTMETALL_FIELDS,
    fetch_history,
    fetch_johnson_matthey_history,
    fetch_westmetall_history,
    get_reference_prices,
)
from backend.database import get_session
from backend.models.metal_price import MetalPrice

router = APIRouter(prefix="/api/prices", tags=["prices"])

TRACKED_SYMBOLS = ["Pt", "Pd", "Rh", "Ru", "Ir", "Au", "Ag", "Ni", "Co", "Cu", "Al", "Mo", "W", "Fe"]

_PERIOD_DAYS = {"1mo": 31, "3mo": 92, "6mo": 183, "1y": 366, "2y": 731, "5y": 1827}

# Trend payloads are cached per period so reopening the page (or switching
# the change basis back and forth) does not re-hit the Yahoo chart API.
_TRENDS_TTL_SECONDS = 600.0
_trends_cache: dict[str, tuple[float, dict]] = {}


def _normalize(symbol: str) -> str:
    return symbol.capitalize() if len(symbol) <= 2 else symbol


def _is_live_source(source: str | None) -> bool:
    return any(
        label in (source or "")
        for label in (
            "Yahoo Finance",
            "Metals.Dev",
            "Kitco",
            "Johnson Matthey",
            "Markets Insider",
            "MetalpriceAPI",
        )
    )


def _source_type_from_source(source: str | None) -> str:
    return "live" if _is_live_source(source) else "indexed"


def _filter_history_range(
    history: list[dict],
    from_date: date | None,
    to_date: date | None,
) -> list[dict]:
    """Apply an inclusive date filter to price-history rows."""

    if from_date is None and to_date is None:
        return history

    filtered: list[dict] = []
    for row in history:
        row_date = date.fromisoformat(row["date"])
        if from_date is not None and row_date < from_date:
            continue
        if to_date is not None and row_date > to_date:
            continue
        filtered.append(row)
    return filtered


def _serialize_price_row(
    *,
    symbol: str,
    name: str,
    price: float,
    unit: str,
    source: str,
    fetched_at: str | None,
) -> dict:
    source_type = _source_type_from_source(source)
    evidence = describe_price_evidence(source=source, fetched_at=fetched_at)
    return {
        "symbol": symbol,
        "name": name,
        "price": price,
        "unit": unit,
        "source": source,
        "source_type": source_type,
        "is_live": source_type == "live",
        "fetched_at": fetched_at,
        "evidence": evidence,
    }


@router.get("")
def get_all_prices(session: Session = Depends(get_session)):
    """Get latest price for every metal (DB cache first, then reference)."""
    stmt = select(MetalPrice).order_by(MetalPrice.fetched_at.desc())
    db_prices = session.exec(stmt).all()

    seen: set[str] = set()
    result = []
    for p in db_prices:
        if p.symbol not in seen:
            seen.add(p.symbol)
            result.append(_serialize_price_row(
                symbol=p.symbol,
                name=p.name,
                price=p.price,
                unit=p.unit,
                source=p.source,
                fetched_at=p.fetched_at.isoformat(),
            ))

    # Fill missing symbols from reference
    for sym, info in get_reference_prices().items():
        if sym not in seen:
            result.append(_serialize_price_row(
                symbol=sym,
                name=info["name"],
                price=info["price"],
                unit=info["unit"],
                source=info["source"],
                fetched_at=info["fetched_at"],
            ))

    # Sort: live prices first, then alphabetical
    result.sort(key=lambda x: (0 if x["source_type"] == "live" else 1, x["symbol"]))
    return result


def _downsample(points: list[dict], limit: int = 60) -> list[dict]:
    """Thin a daily series to at most `limit` points, always keeping the last one."""

    if len(points) <= limit:
        return points
    stride = (len(points) - 1) / (limit - 1)
    picked = [points[round(i * stride)] for i in range(limit - 1)]
    picked.append(points[-1])
    return picked


def _dedupe_by_date(points: list[dict]) -> list[dict]:
    by_date: dict[str, dict] = {}
    for point in points:
        by_date[point["date"]] = point
    return [by_date[key] for key in sorted(by_date)]


async def _symbol_trend(
    symbol: str,
    period: str,
    session: Session,
    jm_history: dict[str, list[dict]] | None = None,
) -> dict:
    history = await fetch_history(symbol, period)
    source = "Yahoo Finance"
    cutoff = date.today() - timedelta(days=_PERIOD_DAYS.get(period, 366))
    if not history and jm_history and jm_history.get(symbol):
        history = jm_history[symbol]
        source = "Johnson Matthey"
    if not history and symbol in WESTMETALL_FIELDS:
        history = [
            row
            for row in await fetch_westmetall_history(symbol)
            if date.fromisoformat(row["date"]) >= cutoff
        ]
        if history:
            source = "Westmetall (LME)"
    if not history:
        source = "DB cache"
        stmt = (
            select(MetalPrice)
            .where(MetalPrice.symbol == symbol)
            .order_by(MetalPrice.fetched_at.desc())
            .limit(500)
        )
        history = [
            {"date": p.fetched_at.strftime("%Y-%m-%d"), "price": p.price}
            for p in reversed(session.exec(stmt).all())
            if p.fetched_at.date() >= cutoff
        ]

    points = _dedupe_by_date([{"date": row["date"], "price": row["price"]} for row in history])
    prices = [point["price"] for point in points]
    first = prices[0] if prices else None
    last = prices[-1] if prices else None
    change_pct = ((last - first) / first * 100) if first and last is not None and first != 0 else None
    return {
        "symbol": symbol,
        "source": source,
        "count": len(points),
        "first": first,
        "last": last,
        "high": max(prices) if prices else None,
        "low": min(prices) if prices else None,
        "change_pct": change_pct,
        "points": _downsample(points),
    }


@router.get("/trends")
async def get_price_trends(
    period: str = Query(default="3mo", pattern="^(1mo|3mo|6mo|1y|2y|5y)$"),
    session: Session = Depends(get_session),
):
    """Compact per-symbol trend series and change stats for every tracked metal.

    Yahoo-backed symbols come from the chart API; the rest fall back to the
    per-refresh snapshots accumulated in the local DB (deduplicated by day),
    so change figures are only reported for series with real depth.
    """

    cached = _trends_cache.get(period)
    if cached and time.monotonic() - cached[0] < _TRENDS_TTL_SECONDS:
        return cached[1]

    # One JM request covers every PGM, so fetch it before fanning out.
    jm_history = await fetch_johnson_matthey_history(
        date.today() - timedelta(days=_PERIOD_DAYS.get(period, 366)), date.today()
    )
    trends = await asyncio.gather(
        *[_symbol_trend(symbol, period, session, jm_history) for symbol in TRACKED_SYMBOLS]
    )
    payload = {"period": period, "trends": {trend["symbol"]: trend for trend in trends}}
    _trends_cache[period] = (time.monotonic(), payload)
    return payload


# Tokens that look like element symbols but are route/reaction acronyms in
# benchmark candidate names (WGS, USY w/ RE, PEM, ...). Skipped during the scan.
_USAGE_STOPWORDS = {
    "AEM", "CCM", "FCC", "FTS", "GDE", "GDL", "HDO", "HER", "LDH", "MEA", "MTH",
    "MTO", "NRR", "OER", "ORR", "PDH", "PEM", "PGM", "PROX", "RE", "SCR", "SMR",
    "USY", "WGS", "RWGS",
}
_SYMBOL_PATTERNS = {
    symbol: re.compile(rf"(?<![A-Za-z]){symbol}(?![a-z])") for symbol in TRACKED_SYMBOLS
}
_ELEMENT_NAMES = {
    "Pt": "platinum", "Pd": "palladium", "Rh": "rhodium", "Ru": "ruthenium",
    "Ir": "iridium", "Au": "gold", "Ag": "silver", "Ni": "nickel",
    "Co": "cobalt", "Cu": "copper", "Al": "aluminum", "Mo": "molybdenum",
    "W": "tungsten", "Fe": "iron",
}


@lru_cache(maxsize=1)
def _usage_map() -> dict[str, list[dict]]:
    usage: dict[str, list[dict]] = {symbol: [] for symbol in TRACKED_SYMBOLS}
    for catalog in list_benchmark_catalogs():
        texts: list[str] = []
        for candidate in catalog.get("candidates", []):
            texts.append(str(candidate.get("title", "")))
            for component in candidate.get("components", []):
                texts.append(str(component.get("name", "")))
        matched: set[str] = set()
        for text in texts:
            lowered = text.lower()
            tokens = [token for token in re.split(r"[^A-Za-z0-9]+", text) if token]
            for symbol in TRACKED_SYMBOLS:
                if symbol in matched:
                    continue
                if any(
                    token not in _USAGE_STOPWORDS and _SYMBOL_PATTERNS[symbol].search(token)
                    for token in tokens
                ) or _ELEMENT_NAMES[symbol] in lowered:
                    matched.add(symbol)
        entry = {
            "family": catalog["family"],
            "title": catalog["title"],
            "reaction": catalog.get("reaction", ""),
        }
        for symbol in matched:
            usage[symbol].append(entry)
    return usage


@router.get("/usage")
def get_price_usage():
    """Map each tracked metal to the reaction families whose benchmark
    candidates name it in a composition or candidate title."""

    return {"usage": _usage_map()}


@router.get("/{symbol}")
def get_price(symbol: str, session: Session = Depends(get_session)):
    """Get latest price for a specific metal."""
    symbol = _normalize(symbol)
    stmt = (
        select(MetalPrice)
        .where(MetalPrice.symbol == symbol)
        .order_by(MetalPrice.fetched_at.desc())
        .limit(1)
    )
    p = session.exec(stmt).first()
    if p:
        return _serialize_price_row(
            symbol=p.symbol,
            name=p.name,
            price=p.price,
            unit=p.unit,
            source=p.source,
            fetched_at=p.fetched_at.isoformat(),
        )
    refs = get_reference_prices()
    if symbol not in refs:
        raise HTTPException(status_code=404, detail=f"Metal '{symbol}' not found")
    info = refs[symbol]
    return _serialize_price_row(
        symbol=symbol,
        name=info["name"],
        price=info["price"],
        unit=info["unit"],
        source=info["source"],
        fetched_at=info["fetched_at"],
    )


@router.get("/{symbol}/history")
async def get_price_history(
    symbol: str,
    period: str = Query(default="1y", pattern="^(1mo|3mo|6mo|1y|2y|5y)$"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    session: Session = Depends(get_session),
):
    """Return OHLC price history from Yahoo Finance (live) or DB records."""
    symbol = _normalize(symbol)
    if from_date is not None and to_date is not None and from_date > to_date:
        raise HTTPException(status_code=422, detail="'from' must be on or before 'to'")

    # Try yfinance live history first (covers Pt, Pd, Au, Ag, Cu, Al)
    live_history = await fetch_history(symbol, period)
    if live_history:
        filtered_history = _filter_history_range(live_history, from_date, to_date)
        return {
            "symbol": symbol,
            "period": period,
            "source": "Yahoo Finance",
            "count": len(filtered_history),
            "history": filtered_history,
        }

    # Fall back to DB collected history
    stmt = (
        select(MetalPrice)
        .where(MetalPrice.symbol == symbol)
        .order_by(MetalPrice.fetched_at.desc())
        .limit(500)
    )
    db_rows = list(reversed(session.exec(stmt).all()))
    if db_rows:
        history = _filter_history_range(
            [
                {
                    "date": p.fetched_at.strftime("%Y-%m-%d"),
                    "price": p.price,
                    "open": p.price,
                    "high": p.price,
                    "low": p.price,
                }
                for p in db_rows
            ],
            from_date,
            to_date,
        )
        return {
            "symbol": symbol,
            "period": period,
            "source": "DB cache",
            "count": len(history),
            "history": history,
        }

    raise HTTPException(status_code=404, detail=f"No history for '{symbol}'")
