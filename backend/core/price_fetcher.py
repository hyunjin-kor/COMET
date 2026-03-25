"""Metal price fetcher — real-time via yfinance (Yahoo Finance futures).

Primary source  : yfinance (FREE, no API key) — Pt, Pd, Au, Ag, Cu, Al
Optional upgrade: Metals.Dev / MetalpriceAPI when API keys are set in .env
Reference fallback: CatCost 2018 reference prices + ChemPPI escalation
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime
from pathlib import Path

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ── Yahoo Finance ticker map ──────────────────────────────────────────────────
# (symbol, ticker, name, unit, price_factor)
YFINANCE_METALS: list[tuple[str, str, str, str, float]] = [
    ("Pt", "PL=F",  "Platinum",  "$/troy_oz", 1.0),
    ("Pd", "PA=F",  "Palladium", "$/troy_oz", 1.0),
    ("Au", "GC=F",  "Gold",      "$/troy_oz", 1.0),
    ("Ag", "SI=F",  "Silver",    "$/troy_oz", 1.0),
    ("Cu", "HG=F",  "Copper",    "$/lb",      1.0),
    # ALI=F (COMEX Aluminum) is quoted in $/MT — convert to $/lb
    ("Al", "ALI=F", "Aluminum",  "$/lb",      1 / 2204.62),
]

# Metals without free live data — covered by paid APIs or reference escalation
_NAMES: dict[str, str] = {
    "Au": "Gold",       "Ag": "Silver",     "Pt": "Platinum",
    "Pd": "Palladium",  "Rh": "Rhodium",    "Ir": "Iridium",
    "Ru": "Ruthenium",  "Ni": "Nickel",     "Co": "Cobalt",
    "Cu": "Copper",     "Al": "Aluminum",   "Mo": "Molybdenum",
    "W":  "Tungsten",   "Fe": "Iron",
}
_UNITS: dict[str, str] = {
    "Au": "$/troy_oz", "Ag": "$/troy_oz", "Pt": "$/troy_oz",
    "Pd": "$/troy_oz", "Rh": "$/troy_oz", "Ir": "$/troy_oz",
    "Ru": "$/troy_oz", "Ni": "$/lb",      "Co": "$/lb",
    "Cu": "$/lb",      "Al": "$/lb",      "Mo": "$/lb",
    "W":  "$/lb",      "Fe": "$/lb",
}

# CatCost 2018 reference prices (basis for ChemPPI escalation)
_CATCOST_REF: dict[str, float] = {
    "Au": 1200.8, "Ir": 1440.0, "Pd":  975.0, "Pt":  793.5,
    "Rh": 2390.0, "Ru":  260.0, "Ag":   14.58,
    "Al":    0.96, "Co":  29.6, "Cu":    2.75,
    "Fe":    0.0475, "Mo": 12.0, "Ni":   6.08, "W":  24.04,
}


def _escalate(price_2018: float) -> float:
    """Scale a 2018 price to today using ChemPPI index."""
    try:
        with open(_DATA_DIR / "chemppi.json", encoding="utf-8") as f:
            annual = json.load(f).get("annual", {})
        base = float(annual.get("2018", 0))
        latest_year = max(int(y) for y in annual if annual[y])
        latest = float(annual.get(str(latest_year), 0))
        if base and latest:
            return round(price_2018 * (latest / base), 4)
    except Exception:
        pass
    return price_2018


# ── yfinance (primary free source) ───────────────────────────────────────────

def _yfinance_sync() -> dict[str, dict]:
    try:
        import yfinance as yf  # type: ignore
    except ImportError:
        logger.warning("yfinance not installed — pip install yfinance")
        return {}

    results: dict[str, dict] = {}
    for sym, ticker, name, unit, factor in YFINANCE_METALS:
        try:
            hist = yf.Ticker(ticker).history(period="5d", auto_adjust=True)
            if hist.empty:
                continue
            closes = hist["Close"].dropna()
            if closes.empty:
                continue
            price = round(float(closes.iloc[-1]) * factor, 4)
            results[sym] = {
                "name": name, "price": price, "unit": unit,
                "source": "Yahoo Finance (live)", "ticker": ticker,
                "fetched_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.debug("yfinance %s: %s", sym, e)

    logger.info("yfinance: %d metals — %s", len(results), list(results))
    return results


async def fetch_yfinance() -> dict[str, dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _yfinance_sync)


# ── Metals.Dev (optional paid) ───────────────────────────────────────────────

async def fetch_metals_dev() -> dict[str, dict]:
    api_key = settings.metals_dev_api_key
    if not api_key:
        raise ValueError("METALS_DEV_API_KEY not set")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://api.metals.dev/v1/latest",
            params={"api_key": api_key, "currency": "USD", "unit": "toz"},
        )
        resp.raise_for_status()
        raw = resp.json().get("metals", {})
    name_to_sym = {
        "gold": "Au", "silver": "Ag", "platinum": "Pt", "palladium": "Pd",
        "rhodium": "Rh", "iridium": "Ir", "ruthenium": "Ru",
        "nickel": "Ni", "cobalt": "Co", "copper": "Cu",
        "aluminum": "Al", "molybdenum": "Mo", "tungsten": "W",
    }
    results: dict[str, dict] = {}
    for raw_name, sym in name_to_sym.items():
        val = raw.get(raw_name)
        if val:
            results[sym] = {
                "name": _NAMES.get(sym, sym), "price": round(float(val), 4),
                "unit": _UNITS.get(sym, "$/troy_oz"), "source": "Metals.Dev",
                "fetched_at": datetime.utcnow().isoformat(),
            }
    return results


# ── MetalpriceAPI (optional paid) ────────────────────────────────────────────

async def fetch_metalprice_api() -> dict[str, dict]:
    api_key = settings.metalprice_api_key
    if not api_key:
        raise ValueError("METALPRICE_API_KEY not set")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            "https://api.metalpriceapi.com/v1/latest",
            params={"api_key": api_key, "base": "USD"},
        )
        resp.raise_for_status()
        rates = resp.json().get("rates", {})
    iso_map = {"XPT": "Pt", "XPD": "Pd", "XAU": "Au", "XAG": "Ag"}
    results: dict[str, dict] = {}
    for iso, sym in iso_map.items():
        rate = rates.get(f"USD{iso}") or rates.get(iso)
        if rate and float(rate) > 0:
            results[sym] = {
                "name": _NAMES.get(sym, sym),
                "price": round(1.0 / float(rate), 4),
                "unit": "$/troy_oz", "source": "MetalpriceAPI",
                "fetched_at": datetime.utcnow().isoformat(),
            }
    return results


# ── Kitco scraper (Rh — free, scraping permitted per robots.txt) ─────────────

async def fetch_kitco() -> dict[str, dict]:
    """Scrape Kitco precious-metals page for Rhodium spot price.

    Kitco embeds live quote data in a Next.js __NEXT_DATA__ script tag.
    robots.txt: Allow: /  — scraping is permitted.
    Returns a dict with 'Rh' (and potentially cross-check metals).
    """
    url = "https://www.kitco.com/price/precious-metals"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            html = resp.text

        # Extract __NEXT_DATA__ JSON
        m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
        if not m:
            logger.warning("Kitco: __NEXT_DATA__ not found in page")
            return {}

        data = json.loads(m.group(1))

        # Navigate: props → pageProps → dehydratedState → queries
        queries = (
            data.get("props", {})
                .get("pageProps", {})
                .get("dehydratedState", {})
                .get("queries", [])
        )

        # Find the allMetalsQuote query
        metals_data = None
        for q in queries:
            qkey = q.get("queryKey", [])
            if isinstance(qkey, list) and "allMetalsQuote" in qkey:
                metals_data = q.get("state", {}).get("data", {})
                break

        if not metals_data:
            logger.warning("Kitco: allMetalsQuote query not found")
            return {}

        results: dict[str, dict] = {}

        # Map Kitco metal names to our symbols
        kitco_map = {
            "rhodium":  ("Rh", "Rhodium",  "$/troy_oz"),
            "platinum": ("Pt", "Platinum", "$/troy_oz"),
            "palladium":("Pd", "Palladium","$/troy_oz"),
            "gold":     ("Au", "Gold",     "$/troy_oz"),
            "silver":   ("Ag", "Silver",   "$/troy_oz"),
        }

        for kitco_name, (sym, name, unit) in kitco_map.items():
            metal_obj = metals_data.get(kitco_name, {})
            entries = metal_obj.get("results", [])
            if not entries:
                continue
            entry = entries[0]
            bid = entry.get("bid")
            ask = entry.get("ask")
            mid = entry.get("mid")
            if mid and float(mid) > 0:
                price = float(mid)
            elif bid and ask and float(bid) > 0:
                price = (float(bid) + float(ask)) / 2
            elif bid and float(bid) > 0:
                price = float(bid)
            else:
                continue
            results[sym] = {
                "name": name,
                "price": round(price, 4),
                "unit": unit,
                "source": "Kitco (live)",
                "fetched_at": datetime.utcnow().isoformat(),
            }

        logger.info("Kitco: %d metals — %s", len(results), list(results))
        return results

    except Exception as e:
        logger.warning("Kitco scraper failed: %s", e)
        return {}


# ── Kitco Base Metals ── NOTE: base metals are loaded via client-side XHR,
# not in SSR __NEXT_DATA__. Scraping confirmed non-viable. Kept as stub.

async def fetch_kitco_base() -> dict[str, dict]:
    """Scrape Kitco base-metals page for Ni, Cu, Al live prices.

    Same Next.js __NEXT_DATA__ structure as the precious-metals page.
    """
    url = "https://www.kitco.com/price/base-metals"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    # Base metals Kitco quotes in $/lb
    KITCO_BASE_MAP = {
        "nickel":   ("Ni", "Nickel",   "$/lb"),
        "copper":   ("Cu", "Copper",   "$/lb"),
        "aluminum": ("Al", "Aluminum", "$/lb"),
        "zinc":     ("Zn", "Zinc",     "$/lb"),
        "lead":     ("Pb", "Lead",     "$/lb"),
        "tin":      ("Sn", "Tin",      "$/lb"),
    }
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            html = resp.text

        m = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html, re.S,
        )
        if not m:
            logger.warning("Kitco base: __NEXT_DATA__ not found")
            return {}

        data = json.loads(m.group(1))
        queries = (
            data.get("props", {})
                .get("pageProps", {})
                .get("dehydratedState", {})
                .get("queries", [])
        )

        metals_data: dict | None = None
        for q in queries:
            qkey = q.get("queryKey", [])
            if isinstance(qkey, list) and "allMetalsQuote" in qkey:
                metals_data = q.get("state", {}).get("data", {})
                break

        if not metals_data:
            logger.warning("Kitco base: allMetalsQuote query not found")
            return {}

        results: dict[str, dict] = {}
        for kitco_name, (sym, name, unit) in KITCO_BASE_MAP.items():
            metal_obj = metals_data.get(kitco_name, {})
            entries = metal_obj.get("results", [])
            if not entries:
                continue
            entry = entries[0]
            bid = entry.get("bid")
            ask = entry.get("ask")
            mid = entry.get("mid")
            if mid and float(mid) > 0:
                price = float(mid)
            elif bid and ask and float(bid) > 0:
                price = (float(bid) + float(ask)) / 2
            elif bid and float(bid) > 0:
                price = float(bid)
            else:
                continue
            results[sym] = {
                "name": name, "price": round(price, 6), "unit": unit,
                "source": "Kitco (live)", "fetched_at": datetime.utcnow().isoformat(),
            }

        logger.info("Kitco base: %d metals — %s", len(results), list(results))
        return results

    except Exception as e:
        logger.warning("Kitco base scraper failed: %s", e)
        return {}


# ── Johnson Matthey — Ru, Ir (and cross-check PGMs) ─────────────────────────

async def fetch_johnson_matthey() -> dict[str, dict]:
    """Fetch PGM prices from Johnson Matthey's market data page.

    JM publishes daily AM/PM fixings for Pt, Pd, Rh, Ru, Ir.
    The page embeds data in a JSON API response loaded at runtime.
    Tries the Next.js __NEXT_DATA__ route first, then falls back to
    scanning inline script tags for embedded price objects.
    """
    url = "https://matthey.com/en/market-data/pgm-data"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://matthey.com/",
    }
    JM_MAP = {
        "platinum":  ("Pt", "Platinum",  "$/troy_oz"),
        "palladium": ("Pd", "Palladium", "$/troy_oz"),
        "rhodium":   ("Rh", "Rhodium",   "$/troy_oz"),
        "ruthenium": ("Ru", "Ruthenium", "$/troy_oz"),
        "iridium":   ("Ir", "Iridium",   "$/troy_oz"),
    }
    try:
        async with httpx.AsyncClient(timeout=25, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            html = resp.text

        results: dict[str, dict] = {}

        # Strategy 1: __NEXT_DATA__ JSON blob
        m = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html, re.S,
        )
        if m:
            try:
                page_data = json.loads(m.group(1))
                # Walk all nested dicts/lists looking for price keys
                raw_str = json.dumps(page_data)
                for metal_key, (sym, name, unit) in JM_MAP.items():
                    # Look for patterns like "platinum":{"am":XXXX,"pm":XXXX}
                    pat = rf'"{metal_key}"\s*:\s*\{{[^}}]*?"(?:am|pm|price|value)"\s*:\s*([0-9]+(?:\.[0-9]+)?)'
                    hit = re.search(pat, raw_str, re.I)
                    if hit:
                        price = float(hit.group(1))
                        if price > 0:
                            results[sym] = {
                                "name": name, "price": round(price, 2),
                                "unit": unit, "source": "Johnson Matthey (live)",
                                "fetched_at": datetime.utcnow().isoformat(),
                            }
            except Exception:
                pass

        # Strategy 2: scan all inline <script> tags for price data objects
        if not results:
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.S)
            for script in scripts:
                for metal_key, (sym, name, unit) in JM_MAP.items():
                    pat = rf'{metal_key}["\s:]+([0-9]{{3,5}}(?:\.[0-9]+)?)'
                    hit = re.search(pat, script, re.I)
                    if hit and sym not in results:
                        price = float(hit.group(1))
                        if price > 0:
                            results[sym] = {
                                "name": name, "price": round(price, 2),
                                "unit": unit, "source": "Johnson Matthey (live)",
                                "fetched_at": datetime.utcnow().isoformat(),
                            }

        logger.info("Johnson Matthey: %d metals — %s", len(results), list(results))
        return results

    except Exception as e:
        logger.warning("Johnson Matthey scraper failed: %s", e)
        return {}


# ── Reference prices ─────────────────────────────────────────────────────────

def get_reference_prices() -> dict[str, dict]:
    """Return all metals with 2018 CatCost prices escalated by ChemPPI."""
    return {
        sym: {
            "name": _NAMES.get(sym, sym),
            "price": _escalate(base),
            "unit": _UNITS.get(sym, "$/troy_oz"),
            "source": "CatCost 2018 + ChemPPI escalation",
            "fetched_at": None,
        }
        for sym, base in _CATCOST_REF.items()
    }


# ── Master fetch ──────────────────────────────────────────────────────────────

async def fetch_all_prices() -> dict[str, dict]:
    """Fetch prices from all available sources (best-effort, layered).

    Layer 1 : Reference prices for everything (always works — CatCost 2018 + ChemPPI)
    Layer 2 : Metals.Dev if METALS_DEV_API_KEY set (overwrites all — Ni, Co, Ru, Ir too)
    Layer 3 : yfinance (free — Pt, Pd, Au, Ag, Cu, Al)
    Layer 4 : Kitco precious-metals scraper (free — Rh, cross-checks PGMs)
    Layer 5 : MetalpriceAPI if METALPRICE_API_KEY set (fills remaining PGMs)

    Free live coverage: Pt, Pd, Au, Ag, Cu, Al (yfinance) + Rh (Kitco)
    For Ni, Co, Ru, Ir, Mo, W — configure METALS_DEV_API_KEY or METALPRICE_API_KEY.
    """
    results = get_reference_prices()

    if settings.metals_dev_api_key:
        try:
            paid = await fetch_metals_dev()
            results.update(paid)
        except Exception as e:
            logger.warning("Metals.Dev failed: %s", e)

    # Run free scrapers concurrently
    yf_task    = asyncio.create_task(fetch_yfinance())
    kitco_task = asyncio.create_task(fetch_kitco())

    yf_data, kitco_data = await asyncio.gather(yf_task, kitco_task, return_exceptions=True)

    if isinstance(yf_data, dict):
        results.update(yf_data)
    else:
        logger.warning("yfinance failed: %s", yf_data)

    if isinstance(kitco_data, dict):
        for sym, data in kitco_data.items():
            existing_src = results.get(sym, {}).get("source", "")
            if "CatCost" in existing_src or sym == "Rh":
                results[sym] = data
    else:
        logger.warning("Kitco failed: %s", kitco_data)

    if settings.metalprice_api_key:
        try:
            backup = await fetch_metalprice_api()
            for sym, data in backup.items():
                src = results.get(sym, {}).get("source", "")
                if "CatCost" in src:
                    results[sym] = data
        except Exception as e:
            logger.warning("MetalpriceAPI failed: %s", e)

    live_count = sum(1 for v in results.values() if "CatCost" not in v.get("source", ""))
    logger.info("fetch_all_prices: %d total, %d live", len(results), live_count)
    return results


async def fetch_history(symbol: str, period: str = "1y") -> list[dict]:
    """Return OHLC history for a metal from Yahoo Finance.

    Args:
        symbol: e.g. "Pt", "Au"
        period: yfinance period string — "1mo", "3mo", "6mo", "1y", "2y", "5y"
    """
    ticker_map = {sym: t for sym, t, *_ in YFINANCE_METALS}
    ticker = ticker_map.get(symbol)
    if not ticker:
        return []

    def _get() -> list[dict]:
        import yfinance as yf  # type: ignore
        hist = yf.Ticker(ticker).history(period=period, auto_adjust=True)
        out = []
        for ts, row in hist.iterrows():
            out.append({
                "date":  ts.strftime("%Y-%m-%d"),
                "price": round(float(row["Close"]), 4),
                "open":  round(float(row["Open"]),  4),
                "high":  round(float(row["High"]),  4),
                "low":   round(float(row["Low"]),   4),
            })
        return out

    try:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _get)
    except Exception as e:
        logger.warning("fetch_history(%s, %s): %s", symbol, period, e)
        return []
