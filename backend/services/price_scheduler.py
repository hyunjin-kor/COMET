"""Scheduled price collection — uses fetch_all_prices() (yfinance + optional APIs)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlmodel import Session

from backend.core.price_fetcher import fetch_all_prices, fetch_yfinance
from backend.database import engine
from backend.models.metal_price import MetalPrice

logger = logging.getLogger(__name__)


async def collect_prices(source: str | None = None) -> dict[str, dict]:
    """Fetch metal prices and persist to DB.

    Args:
        source: ``"yahoo"`` skips the slower scrapers and only refreshes the
            Yahoo Finance-backed symbols — used by the desktop client's
            in-page polling so frequent ticks don't hammer Kitco/JM.
            Default fetches every configured source.
    """
    if source == "yahoo":
        results = await fetch_yfinance()
    else:
        results = await fetch_all_prices()
    if results:
        _save_prices(results)
    return results


def _save_prices(prices: dict[str, dict]) -> None:
    now = datetime.now(UTC)
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
