"""Scheduled price collection — uses fetch_all_prices() (yfinance + optional APIs)."""

from __future__ import annotations

import logging
import math
from datetime import UTC, datetime

from sqlmodel import Session, select

from backend.core.price_fetcher import fetch_all_prices, fetch_yfinance
from backend.database import engine
from backend.models.metal_price import MetalPrice

logger = logging.getLogger(__name__)

# A feed that changes unit or fails to parse lands orders of magnitude away from
# the last good value; a real tick never does. Two such clusters reached the
# table before this check existed: aluminium quoted per metric ton instead of
# per pound (~2000x high) and a rhodium parse failure pinned at 1001.0 (~10x
# low). The bound is deliberately loose so no genuine move is ever refused.
MAX_TICK_RATIO = 5.0


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


def check_price(
    symbol: str,
    price: float,
    unit: str,
    previous: MetalPrice | None,
) -> str | None:
    """Return a rejection reason, or None when the quote may be stored.

    ``previous`` is the last stored quote for the symbol. Without one there is
    nothing to compare against, so only the value itself is checked.
    """
    if not math.isfinite(price) or price <= 0:
        return f"price is not a positive finite number ({price!r})"

    if previous is None:
        return None
    if previous.unit != unit:
        # A unit switch makes the magnitudes incomparable; let it through so a
        # deliberate unit change is not permanently blocked by its own history.
        logger.warning(
            "%s: unit changed %s -> %s; skipping magnitude check", symbol, previous.unit, unit
        )
        return None

    ratio = price / float(previous.price)
    if ratio > MAX_TICK_RATIO or ratio < 1 / MAX_TICK_RATIO:
        return (
            f"{price:g} {unit} is {ratio:.4g}x the last stored value "
            f"({previous.price:g} {unit} from {previous.source})"
        )
    return None


def _latest_by_symbol(session: Session, symbols: list[str]) -> dict[str, MetalPrice]:
    latest: dict[str, MetalPrice] = {}
    rows = session.exec(
        select(MetalPrice)
        .where(MetalPrice.symbol.in_(symbols))
        .order_by(MetalPrice.fetched_at.desc())
    ).all()
    for row in rows:
        latest.setdefault(row.symbol, row)
    return latest


def _save_prices(prices: dict[str, dict]) -> None:
    now = datetime.now(UTC)
    with Session(engine) as session:
        latest = _latest_by_symbol(session, list(prices))
        saved = 0
        for symbol, info in prices.items():
            price = float(info.get("price", 0))
            unit = info.get("unit", "$/troy_oz")
            reason = check_price(symbol, price, unit, latest.get(symbol))
            if reason is not None:
                logger.warning("Rejected %s quote: %s", symbol, reason)
                continue
            session.add(
                MetalPrice(
                    symbol=symbol,
                    name=info.get("name", symbol),
                    price=price,
                    unit=unit,
                    source=info.get("source", "unknown"),
                    fetched_at=now,
                )
            )
            saved += 1
        session.commit()
    rejected = len(prices) - saved
    if rejected:
        logger.warning("Saved %d price records to DB, rejected %d", saved, rejected)
    else:
        logger.info("Saved %d price records to DB", saved)
