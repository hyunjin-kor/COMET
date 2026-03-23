"""Metal prices API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from backend.core.price_fetcher import get_reference_prices
from backend.database import get_session
from backend.models.metal_price import MetalPrice

router = APIRouter(prefix="/api/prices", tags=["prices"])


@router.get("")
def get_all_prices(session: Session = Depends(get_session)):
    """Get latest prices for all metals.

    Returns DB prices if available, otherwise falls back to reference prices.
    """
    # Try DB first: get latest price per symbol
    stmt = select(MetalPrice).order_by(MetalPrice.fetched_at.desc())
    db_prices = session.exec(stmt).all()

    seen = set()
    result = []
    for p in db_prices:
        if p.symbol not in seen:
            seen.add(p.symbol)
            result.append({
                "symbol": p.symbol,
                "name": p.name,
                "price": p.price,
                "unit": p.unit,
                "source": p.source,
                "fetched_at": p.fetched_at.isoformat(),
            })

    # Fill in missing metals from reference prices
    ref_prices = get_reference_prices()
    for symbol, price in ref_prices.items():
        if symbol not in seen:
            result.append({
                "symbol": symbol,
                "name": symbol,
                "price": price,
                "unit": "$/troy_oz",
                "source": "reference",
                "fetched_at": None,
            })

    return result


@router.get("/{symbol}")
def get_price(symbol: str, session: Session = Depends(get_session)):
    """Get latest price for a specific metal."""
    # Normalize symbol: capitalize first letter (e.g. "pt" → "Pt", "ni" → "Ni")
    symbol = symbol.capitalize() if len(symbol) <= 2 else symbol

    stmt = (
        select(MetalPrice)
        .where(MetalPrice.symbol == symbol)
        .order_by(MetalPrice.fetched_at.desc())
        .limit(1)
    )
    price = session.exec(stmt).first()

    if price:
        return {
            "symbol": price.symbol,
            "name": price.name,
            "price": price.price,
            "unit": price.unit,
            "source": price.source,
            "fetched_at": price.fetched_at.isoformat(),
        }

    # Fallback to reference
    ref = get_reference_prices([symbol])
    if symbol not in ref:
        raise HTTPException(status_code=404, detail=f"Metal '{symbol}' not found")

    return {
        "symbol": symbol,
        "price": ref[symbol],
        "source": "reference",
        "fetched_at": None,
    }


@router.get("/{symbol}/history")
def get_price_history(
    symbol: str,
    limit: int = Query(default=30, le=365),
    session: Session = Depends(get_session),
):
    """Get price history for a specific metal."""
    symbol = symbol.capitalize() if len(symbol) <= 2 else symbol

    stmt = (
        select(MetalPrice)
        .where(MetalPrice.symbol == symbol)
        .order_by(MetalPrice.fetched_at.desc())
        .limit(limit)
    )
    prices = session.exec(stmt).all()

    return {
        "symbol": symbol,
        "count": len(prices),
        "history": [
            {
                "price": p.price,
                "unit": p.unit,
                "source": p.source,
                "fetched_at": p.fetched_at.isoformat(),
            }
            for p in prices
        ],
    }
