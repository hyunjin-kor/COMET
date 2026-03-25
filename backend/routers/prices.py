"""Metal prices API endpoints — live via yfinance + DB cache."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from backend.core.price_fetcher import fetch_history, get_reference_prices
from backend.database import get_session
from backend.models.metal_price import MetalPrice

router = APIRouter(prefix="/api/prices", tags=["prices"])


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
    return {
        "symbol": symbol,
        "name": name,
        "price": price,
        "unit": unit,
        "source": source,
        "source_type": source_type,
        "is_live": source_type == "live",
        "fetched_at": fetched_at,
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
    session: Session = Depends(get_session),
):
    """Return OHLC price history from Yahoo Finance (live) or DB records."""
    symbol = _normalize(symbol)

    # Try yfinance live history first (covers Pt, Pd, Au, Ag, Cu, Al)
    live_history = await fetch_history(symbol, period)
    if live_history:
        return {
            "symbol": symbol,
            "period": period,
            "source": "Yahoo Finance",
            "count":  len(live_history),
            "history": live_history,
        }

    # Fall back to DB collected history
    stmt = (
        select(MetalPrice)
        .where(MetalPrice.symbol == symbol)
        .order_by(MetalPrice.fetched_at.asc())
        .limit(500)
    )
    db_rows = session.exec(stmt).all()
    if db_rows:
        return {
            "symbol": symbol,
            "period": period,
            "source": "DB cache",
            "count":  len(db_rows),
            "history": [
                {"date": p.fetched_at.strftime("%Y-%m-%d"), "price": p.price,
                 "open": p.price, "high": p.price, "low": p.price}
                for p in db_rows
            ],
        }

    raise HTTPException(status_code=404, detail=f"No history for '{symbol}'")
