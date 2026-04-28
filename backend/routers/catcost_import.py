"""CatCost JSON import/export endpoints."""

import csv
import json
from datetime import UTC, datetime
from io import StringIO
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlmodel import Session

from backend.database import get_session
from backend.models.estimate import Estimate

router = APIRouter(prefix="/api", tags=["import_export"])
MAX_IMPORT_BYTES = 1_048_576

PriceUnit = Literal["$/lb", "$/kg", "$/troy_oz"]


class CatCostMetalSection(BaseModel):
    """Metal block of a CatCost-style import payload."""

    model_config = ConfigDict(extra="allow")

    symbol: str = ""
    price: float = Field(default=0.0, ge=0.0)
    price_unit: PriceUnit = "$/troy_oz"


class CatCostSupportSection(BaseModel):
    """Support block of a CatCost-style import payload."""

    model_config = ConfigDict(extra="allow")

    name: str = "Al2O3"
    price_per_lb: float = Field(default=0.5, ge=0.0)


class CatCostImportPayload(BaseModel):
    """Top-level schema accepted by /api/import/catcost.

    Unknown keys are preserved (`extra='allow'`) so we keep `raw_keys`
    transparency in the response, but the typed fields below are enforced
    so a malformed loading or negative price is rejected up front rather
    than producing an invalid normalized payload that crashes downstream.
    """

    model_config = ConfigDict(extra="allow")

    metal: CatCostMetalSection = Field(default_factory=CatCostMetalSection)
    support: CatCostSupportSection = Field(default_factory=CatCostSupportSection)
    loading_wt_pct: float = Field(default=0.0, ge=0.0, le=100.0)
    steps: list[str] = Field(default_factory=list)
    order_size_tons: float = Field(default=10.0, gt=0.0)


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
        raise HTTPException(status_code=400, detail="Invalid JSON file") from None
    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Imported JSON must contain a top-level object")

    try:
        payload = CatCostImportPayload.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail={"message": "Imported JSON is malformed", "errors": exc.errors()},
        ) from exc

    normalized = {
        "metal_symbol": payload.metal.symbol,
        "metal_price": payload.metal.price,
        "metal_price_unit": payload.metal.price_unit,
        "metal_loading_wt_pct": payload.loading_wt_pct,
        "support_name": payload.support.name,
        "support_price_per_lb": payload.support.price_per_lb,
        "steps": payload.steps,
        "order_size_tons": payload.order_size_tons,
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
