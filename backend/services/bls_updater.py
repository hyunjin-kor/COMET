"""BLS API client for ChemPPI automatic updates.

Fetches Chemical Producer Price Index from the U.S. Bureau of Labor Statistics.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
CHEMPPI_SERIES_ID = "PCU325---325---"


async def update_chemppi() -> dict[str, float]:
    """Fetch latest ChemPPI data from BLS and update local JSON.

    Returns:
        Updated annual index dict.
    """
    params: dict = {
        "seriesid": [CHEMPPI_SERIES_ID],
        "startyear": "2008",
        "endyear": "2026",
    }
    if settings.bls_api_key:
        params["registrationkey"] = settings.bls_api_key

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(BLS_API_URL, json=params)
        resp.raise_for_status()
        data = resp.json()

    if data.get("status") != "REQUEST_SUCCEEDED":
        logger.error("BLS API error: %s", data.get("message", "Unknown"))
        raise ValueError(f"BLS API error: {data.get('message')}")

    series_data = data["Results"]["series"][0]["data"]

    # Compute annual averages from monthly data
    yearly: dict[str, list[float]] = {}
    for entry in series_data:
        year = entry["year"]
        value = float(entry["value"])
        yearly.setdefault(year, []).append(value)

    annual = {year: round(sum(vals) / len(vals), 1) for year, vals in yearly.items()}

    # Update local file
    filepath = _DATA_DIR / "chemppi.json"
    with open(filepath) as f:
        existing = json.load(f)

    existing["annual"].update(annual)

    with open(filepath, "w") as f:
        json.dump(existing, f, indent=2)

    logger.info("Updated ChemPPI with %d years of data", len(annual))
    return existing["annual"]
