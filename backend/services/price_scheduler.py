"""Scheduled price collection — uses fetch_all_prices() (yfinance + optional APIs)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlmodel import Session

from backend.core.price_fetcher import fetch_all_prices
from backend.database import engine
from backend.models.metal_price import MetalPrice

logger = logging.getLogger(__name__)


async def collect_prices() -> dict[str, dict]:
    """Fetch all metal prices and persist to DB.

    Returns:
        Dict of {symbol: price_info_dict} from fetch_all_prices().
    """
    results = await fetch_all_prices()
    if results:
        _save_prices(results)
    return results


def _save_prices(prices: dict[str, dict]) -> None:
    now = datetime.now(timezone.utc)
    with Session(engine) as session:
        for symbol, info in prices.items():
            record = MetalPrice(
                symbol=symbol,
                name=info.get("name", symbol),
                price=float(info.get("price", 0)),
                unit=info.get("unit", "$/troy_oz"),
                source=info.get("source", "unknown"),
                fetched_at=now,
            )
            session.add(record)
        session.commit()
    logger.info("Saved %d price records to DB", len(prices))
