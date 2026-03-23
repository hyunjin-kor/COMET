"""CatCost JSON import/export endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session

from backend.database import get_session
from backend.models.estimate import Estimate

router = APIRouter(prefix="/api", tags=["import_export"])


@router.post("/import/catcost")
async def import_catcost_json(file: UploadFile):
    """Import a CatCost-compatible JSON file.

    Accepts JSON with materials, steps, and parameters.
    Returns a normalized input suitable for /api/calculate.
    """
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only .json files are accepted")

    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

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
            "created_at": estimate.created_at.isoformat(),
            "input": input_data,
            "result": result,
        }
    elif format == "csv":
        # Simple CSV-like dict for frontend to convert
        summary = result.get("summary", {})
        return {
            "format": "csv",
            "headers": list(summary.keys()),
            "values": list(summary.values()),
        }
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
