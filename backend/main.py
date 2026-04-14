"""FastAPI sidecar entry point for the desktop app."""

import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from backend.config import settings
from backend.database import create_db_and_tables, engine, sync_material_library
from backend.routers import (
    calculator,
    catcost_import,
    compare,
    decision,
    materials,
    prices,
    uncertainty,
)
from backend.services.price_scheduler import collect_prices

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone=UTC)
_last_price_update: datetime | None = None


async def _scheduled_price_update() -> None:
    """Scheduled task to collect metal prices."""
    global _last_price_update
    try:
        await collect_prices()
        _last_price_update = datetime.now(UTC)
        logger.info("Scheduled price update completed")
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Scheduled price update failed: %s", exc)


def _is_local_request(host: str | None) -> bool:
    """Allow manual refresh only from loopback/test clients by default."""
    return host in {"127.0.0.1", "::1", "localhost", "testclient", None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables, fetch prices on startup, then schedule daily updates."""
    create_db_and_tables()
    with Session(engine) as session:
        sync_material_library(session, force=True)

    # Fetch prices immediately on startup without blocking the Electron shell.
    import asyncio

    asyncio.create_task(_scheduled_price_update())

    scheduler.add_job(
        _scheduled_price_update,
        "cron",
        hour=settings.price_update_hour,
        minute=0,
        id="daily_price_update",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        "Price scheduler started (daily refresh at %02d:00 UTC + immediate fetch on startup)",
        settings.price_update_hour,
    )

    yield

    scheduler.shutdown()


app = FastAPI(
    title="CatPrice API",
    description="Loopback API sidecar for the CatPrice desktop app",
    version="1.1.11",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculator.router)
app.include_router(prices.router)
app.include_router(materials.router)
app.include_router(uncertainty.router)
app.include_router(compare.router)
app.include_router(catcost_import.router)
app.include_router(decision.router)


@app.get("/api/health")
def health():
    """Server health check."""
    return {
        "status": "ok",
        "version": "1.1.11",
        "last_price_update": _last_price_update.isoformat() if _last_price_update else None,
        "scheduler_running": scheduler.running,
    }


@app.post("/api/prices/refresh")
async def refresh_prices(request: Request):
    """Manually trigger a price update."""
    client_host = request.client.host if request.client else None
    if not settings.debug and not _is_local_request(client_host):
        raise HTTPException(status_code=403, detail="Manual refresh is only available from local requests.")

    global _last_price_update
    prices_data = await collect_prices()
    _last_price_update = datetime.now(UTC)
    return {
        "status": "ok",
        "prices_fetched": len(prices_data),
        "updated_at": _last_price_update.isoformat(),
    }
