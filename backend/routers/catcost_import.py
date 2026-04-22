"""CatCost JSON import/export endpoints."""

import csv
import json
from datetime import UTC, datetime
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from sqlmodel import Session

from backend.database import get_session
from backend.models.estimate import Estimate

router = APIRouter(prefix="/api", tags=["import_export"])
MAX_IMPORT_BYTES = 1_048_576


def _summary_to_csv(summary: dict) -> str:
    """Serialize a summary payload into a small metric/value CSV document."""

    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["metric", "value"])
    for key, value in summary.items():
        writer.writerow([key, value])
    return buffer.getvalue()


def _iso_utc(value: datetime) -> str:
    """Serialize datetimes as explicit UTC ISO-8601 strings."""

    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat()


@router.post("/import/catcost")
async def import_catcost_json(file: UploadFile):
    """Import a CatCost-compatible JSON file.

    Accepts JSON with materials, steps, and parameters.
    Returns a normalized input suitable for /api/calculate.
    """
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are accepted")

    content = await file.read()
    await file.close()
    if len(content) > MAX_IMPORT_BYTES:
        raise HTTPException(status_code=413, detail="Imported JSON exceeds the 1 MiB size limit")

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Imported JSON must contain a top-level object")

    # Normalize CatCost JSON format to CatPrice input
    normalized = {
        "metal_symbol": data.get("metal", {}).get("symbol", ""),
        "metal_price": data.get("metal", {}).get("price", 0),
        "metal_price_unit": data.get("metal", {}).get("price_unit", "$/troy_oz"),
        "metal_loading_wt_pct": data.get("loading_wt_pct", 0),
        "support_name": data.get("support", {}).get("name", "Al2O3"),
        "support_price_per_lb": data.get("support", {}).get("price_per_lb", 0.5),
        "steps": data.get("steps", []),
        "order_size_tons": data.get("order_size_tons", 10),
    }

    return {"status": "imported", "normalized_input": normalized, "raw_keys": list(data.keys())}


@router.get("/export/{estimate_id}")
def export_estimate(
    estimate_id: int,
    format: str = "json",
    session: Session = Depends(get_session),
):
    """Export a saved estimate as JSON or CSV."""
    estimate = session.get(Estimate, estimate_id)
    if not estimate:
        raise HTTPException(status_code=404, detail="Estimate not found")

    result = estimate.get_result()
    input_data = estimate.get_input()

    if format == "json":
        return {
            "name": estimate.name,
            "created_at": _iso_utc(estimate.created_at),
            "input": input_data,
            "result": result,
        }
    elif format == "csv":
        summary = result.get("summary", {})
        return PlainTextResponse(
            content=_summary_to_csv(summary),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="estimate-{estimate.id}.csv"',
            },
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
