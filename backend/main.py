"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import create_db_and_tables
from backend.paths import frontend_dist_dir
from backend.routers import calculator, catcost_import, compare, materials, prices, uncertainty
from backend.services.price_scheduler import collect_prices

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
_last_price_update: datetime | None = None


async def _scheduled_price_update() -> None:
    """Scheduled task to collect metal prices."""
    global _last_price_update
    try:
        await collect_prices()
        _last_price_update = datetime.utcnow()
        logger.info("Scheduled price update completed")
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Scheduled price update failed: %s", exc)


def _is_local_request(host: str | None) -> bool:
    """Allow manual refresh only from loopback/test clients by default."""
    return host in {"127.0.0.1", "::1", "localhost", "testclient", None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables, fetch prices on startup, then schedule hourly updates."""
    create_db_and_tables()

    # Fetch prices immediately on startup without blocking boot.
    import asyncio

    asyncio.create_task(_scheduled_price_update())

    scheduler.add_job(
        _scheduled_price_update,
        "interval",
        hours=1,
        id="hourly_price_update",
    )
    scheduler.start()
    logger.info("Price scheduler started (hourly refresh + immediate fetch on startup)")

    yield

    scheduler.shutdown()


app = FastAPI(
    title="CatPrice API",
    description="Real-time metal price based catalyst manufacturing cost estimation",
    version="1.0.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SPA catch-all is registered after all API routers.
_FRONTEND_DIST = frontend_dist_dir().resolve()

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
        "version": "1.0.1",
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
    _last_price_update = datetime.utcnow()
    return {
        "status": "ok",
        "prices_fetched": len(prices_data),
        "updated_at": _last_price_update.isoformat(),
    }


if _FRONTEND_DIST.exists():
    _assets_dir = _FRONTEND_DIST / "assets"
    if _assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")

    def _no_cache_html(path: str) -> Response:
        """Return index.html with headers that prevent browser caching."""
        content = Path(path).read_bytes()
        return Response(
            content=content,
            media_type="text/html",
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    def _resolve_frontend_asset(full_path: str) -> Path | None:
        """Resolve a frontend asset path without allowing traversal outside dist."""
        candidate = (_FRONTEND_DIST / full_path).resolve()
        try:
            candidate.relative_to(_FRONTEND_DIST)
        except ValueError:
            return None
        if candidate.is_file():
            return candidate
        return None

    @app.get("/", include_in_schema=False)
    async def serve_root():
        return _no_cache_html(str(_FRONTEND_DIST / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve the React SPA for non-API paths."""
        candidate = _resolve_frontend_asset(full_path)
        if candidate is not None:
            return FileResponse(str(candidate))
        return _no_cache_html(str(_FRONTEND_DIST / "index.html"))
