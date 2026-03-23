"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import create_db_and_tables
from backend.routers import calculator, catcost_import, compare, materials, prices, uncertainty
from backend.services.price_scheduler import collect_prices

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
_last_price_update: datetime | None = None


async def _scheduled_price_update():
    """Scheduled task to collect metal prices."""
    global _last_price_update
    try:
        await collect_prices()
        _last_price_update = datetime.utcnow()
        logger.info("Scheduled price update completed")
    except Exception as e:
        logger.error("Scheduled price update failed: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables and start scheduler on startup."""
    create_db_and_tables()

    # Schedule daily price collection
    scheduler.add_job(
        _scheduled_price_update,
        "cron",
        hour=settings.price_update_hour,
        minute=0,
        id="daily_price_update",
    )
    scheduler.start()
    logger.info("Price scheduler started (daily at %02d:00 UTC)", settings.price_update_hour)

    yield

    scheduler.shutdown()


app = FastAPI(
    title="CatPrice API",
    description="Real-time metal price based catalyst manufacturing cost estimation",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(calculator.router)
app.include_router(prices.router)
app.include_router(materials.router)
app.include_router(uncertainty.router)
app.include_router(compare.router)
app.include_router(catcost_import.router)


@app.get("/api/health")
def health():
    """Server health check."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "last_price_update": _last_price_update.isoformat() if _last_price_update else None,
        "scheduler_running": scheduler.running,
    }


@app.post("/api/prices/refresh")
async def refresh_prices():
    """Manually trigger a price update."""
    global _last_price_update
    prices_data = await collect_prices()
    _last_price_update = datetime.utcnow()
    return {
        "status": "ok",
        "prices_fetched": len(prices_data),
        "updated_at": _last_price_update.isoformat(),
    }
