"""Path helpers for source and frozen desktop runtime."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def app_root() -> Path:
    """Return the project/app root for source and frozen builds."""
    env_root = os.getenv("CATTEA_APP_ROOT")
    if env_root:
        return Path(env_root).resolve()

    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS).resolve()
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    """Return the backend data directory."""
    env_dir = os.getenv("CATTEA_DATA_DIR")
    if env_dir:
        return Path(env_dir).resolve()
    return app_root() / "backend" / "data"
