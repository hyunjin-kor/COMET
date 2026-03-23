"""Metal price fetcher for real-time spot prices.

Supports Metals.Dev and MetalpriceAPI as data sources.
Falls back to reference prices from materials library when APIs are unavailable.
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx

from backend.config import settings

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_reference_prices() -> dict[str, dict]:
    """Load reference prices from materials library as fallback."""
    filepath = _DATA_DIR / "materials_library.json"
    with open(filepath) as f:
        data = json.load(f)
    return data.get("metals", {})


async def fetch_metals_dev(symbols: list[str] | None = None) -> dict[str, float]:
    """Fetch prices from Metals.Dev API.

    Args:
        symbols: Optional list of metal symbols to fetch. Fetches all if None.

    Returns:
        Dict mapping symbol to price in USD.
    """
    api_key = settings.metals_dev_api_key
    if not api_key:
        raise ValueError("METALS_DEV_API_KEY not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://api.metals.dev/v1/latest",
            params={"api_key": api_key, "currency": "USD", "unit": "toz"},
        )
        resp.raise_for_status()
        data = resp.json()

    prices = {}
    metals_data = data.get("metals", {})
    symbol_map = {
        "gold": "Au", "silver": "Ag", "platinum": "Pt", "palladium": "Pd",
        "rhodium": "Rh", "iridium": "Ir", "ruthenium": "Ru",
        "nickel": "Ni", "cobalt": "Co", "copper": "Cu",
        "molybdenum": "Mo", "tungsten": "W",
    }
    for name, symbol in symbol_map.items():
        if name in metals_data:
            if symbols is None or symbol in symbols:
                prices[symbol] = metals_data[name]

    return prices


async def fetch_metalprice_api(symbols: list[str] | None = None) -> dict[str, float]:
    """Fetch prices from MetalpriceAPI (backup source).

    Args:
        symbols: Optional list of metal symbols.

    Returns:
        Dict mapping symbol to price in USD.
    """
    api_key = settings.metalprice_api_key
    if not api_key:
        raise ValueError("METALPRICE_API_KEY not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://api.metalpriceapi.com/v1/latest",
            params={"api_key": api_key, "base": "USD"},
        )
        resp.raise_for_status()
        data = resp.json()

    prices = {}
    rates = data.get("rates", {})
    for key, rate in rates.items():
        if key.startswith("USD"):
            symbol = key[3:]
            if rate > 0 and (symbols is None or symbol in symbols):
                prices[symbol] = 1.0 / rate  # Convert from 1/price to price

    return prices


def get_reference_prices(symbols: list[str] | None = None) -> dict[str, float]:
    """Get fallback reference prices from materials library.

    Args:
        symbols: Optional list of metal symbols.

    Returns:
        Dict mapping symbol to reference price.
    """
    metals = _load_reference_prices()
    prices = {}
    for symbol, info in metals.items():
        if symbols is None or symbol in symbols:
            prices[symbol] = info.get("reference_price", 0)
    return prices
