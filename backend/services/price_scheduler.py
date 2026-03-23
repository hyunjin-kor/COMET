"""Scheduled price collection service.

Uses APScheduler to fetch metal prices daily and store in DB.
"""

from __future__ import annotations

import logging
from datetime import datetime

from sqlmodel import Session

from backend.core.price_fetcher import (
    fetch_metals_dev,
    fetch_metalprice_api,
    get_reference_prices,
)
from backend.database import engine
from backend.models.metal_price import MetalPrice

logger = logging.getLogger(__name__)

# Name mapping for display
METAL_NAMES = {
    "Pt": "Platinum", "Pd": "Palladium", "Rh": "Rhodium",
    "Ru": "Ruthenium", "Ir": "Iridium", "Au": "Gold", "Ag": "Silver",
    "Ni": "Nickel", "Co": "Cobalt", "Cu": "Copper",
    "Mo": "Molybdenum", "W": "Tungsten", "Fe": "Iron",
}

UNIT_MAP = {
    "Pt": "$/troy_oz", "Pd": "$/troy_oz", "Rh": "$/troy_oz",
    "Ru": "$/troy_oz", "Ir": "$/troy_oz", "Au": "$/troy_oz", "Ag": "$/troy_oz",
    "Ni": "$/lb", "Co": "$/lb", "Cu": "$/lb",
    "Mo": "$/lb", "W": "$/lb", "Fe": "$/lb",
}


async def collect_prices() -> dict[str, float]:
    """Fetch prices from APIs and save to DB.

    Tries Metals.Dev first, falls back to MetalpriceAPI, then reference prices.

    Returns:
        Dict of fetched prices.
    """
    prices: dict[str, float] = {}
    source = "reference"

    # Try primary source
    try:
        prices = await fetch_metals_dev()
        source = "metals.dev"
        logger.info("Fetched %d prices from Metals.Dev", len(prices))
    except Exception as e:
        logger.warning("Metals.Dev fetch failed: %s", e)

        # Try backup source
        try:
            prices = await fetch_metalprice_api()
            source = "metalpriceapi"
            logger.info("Fetched %d prices from MetalpriceAPI", len(prices))
        except Exception as e2:
            logger.warning("MetalpriceAPI fetch failed: %s", e2)

            # Fall back to reference
            prices = get_reference_prices()
            source = "reference"
            logger.info("Using %d reference prices as fallback", len(prices))

    # Save to DB
    if prices:
        _save_prices(prices, source)

    return prices


def _save_prices(prices: dict[str, float], source: str) -> None:
    """Save fetched prices to database."""
    now = datetime.utcnow()
    with Session(engine) as session:
        for symbol, price in prices.items():
            record = MetalPrice(
                symbol=symbol,
                name=METAL_NAMES.get(symbol, symbol),
                price=price,
                unit=UNIT_MAP.get(symbol, "$/troy_oz"),
                source=source,
                fetched_at=now,
            )
            session.add(record)
        session.commit()
    logger.info("Saved %d price records to DB", len(prices))
