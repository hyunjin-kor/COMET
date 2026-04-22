"""Bundled index-data API endpoints."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from backend.paths import data_dir

router = APIRouter(prefix="/api/indices", tags=["indices"])

_DATA_DIR = data_dir()
_INDEX_FILES = {
    "chemppi": _DATA_DIR / "chemppi.json",
    "cepci": _DATA_DIR / "cepci.json",
}


def _load_index_payload(index_name: str) -> dict:
    """Load one bundled index payload from disk."""

    path = _INDEX_FILES.get(index_name)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


@router.get("/chemppi")
def get_chemppi_index():
    """Return the bundled annual ChemPPI dataset."""

    return _load_index_payload("chemppi")


@router.get("/cepci")
def get_cepci_index():
    """Return the bundled annual CEPCI dataset."""

    return _load_index_payload("cepci")
