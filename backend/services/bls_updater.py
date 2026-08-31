"""BLS API client for producer price index updates.

Fetches the Chemical and primary nonferrous metals Producer Price Indexes from
the U.S. Bureau of Labor Statistics.
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


METAL_PPI_SERIES_ID = "WPU1022"


async def update_chemppi() -> dict[str, float]:
    """Fetch latest ChemPPI data from BLS and update local JSON.

    Returns:
        Updated annual index dict.
    """
    return await _update_ppi_index(CHEMPPI_SERIES_ID, "chemppi.json", "ChemPPI")


async def update_metal_ppi() -> dict[str, float]:
    """Refresh the primary nonferrous metals PPI used for Co, Mo and W."""
    return await _update_ppi_index(METAL_PPI_SERIES_ID, "metalppi.json", "metals PPI")


async def _update_ppi_index(series_id: str, filename: str, label: str) -> dict[str, float]:
    # Unregistered BLS v2 requests are capped at a 10-year span; a wider
    # window is silently truncated and recent years never arrive. The local
    # file already carries the deep history, so only refresh recent years.
    current_year = datetime.now(UTC).year
    params: dict = {
        "seriesid": [series_id],
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
    filepath = _DATA_DIR / filename
    with open(filepath, encoding="utf-8") as f:
        existing = json.load(f)

    existing["annual"].update(annual)

    fd, tmp_path = tempfile.mkstemp(prefix=f"{filepath.stem}.", suffix=".json", dir=str(filepath.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(existing, tmp, indent=2)
        os.replace(tmp_path, filepath)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

    logger.info("Updated %s with %d years of data", label, len(annual))
    return existing["annual"]
