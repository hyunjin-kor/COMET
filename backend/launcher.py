"""Standalone FastAPI launcher for desktop sidecar builds."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    """Run the FastAPI app with host/port from the environment."""
    uvicorn.run(
        "backend.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8765")),
        log_level=os.getenv("CATPRICE_LOG_LEVEL", "warning"),
    )


if __name__ == "__main__":
    main()
