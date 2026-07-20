"""BLS API client for ChemPPI automatic updates.

Fetches Chemical Producer Price Index from the U.S. Bureau of Labor Statistics.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import UTC, datetime

import httpx

from backend.config import settings
from backend.paths import data_dir

logger = logging.getLogger(__name__)

_DATA_DIR = data_dir()
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
CHEMPPI_SERIES_ID = "PCU325---325---"


async def update_chemppi() -> dict[str, float]:
    """Fetch latest ChemPPI data from BLS and update local JSON.

    Returns:
        Updated annual index dict.
    """
    # Unregistered BLS v2 requests are capped at a 10-year span; a wider
    # window is silently truncated and recent years never arrive. The local
    # file already carries the deep history, so only refresh recent years.
    current_year = datetime.now(UTC).year
    params: dict = {
        "seriesid": [CHEMPPI_SERIES_ID],
        "startyear": str(current_year - 4),
        "endyear": str(current_year),
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

    # Update local file (atomic write so a partial failure doesn't corrupt the index).
    filepath = _DATA_DIR / "chemppi.json"
    with open(filepath, encoding="utf-8") as f:
        existing = json.load(f)

    existing["annual"].update(annual)

    fd, tmp_path = tempfile.mkstemp(prefix="chemppi.", suffix=".json", dir=str(filepath.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(existing, tmp, indent=2)
        os.replace(tmp_path, filepath)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

    logger.info("Updated ChemPPI with %d years of data", len(annual))
    return existing["annual"]
