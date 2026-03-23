"""Multi-composition comparison endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.cost_engine import estimate_catalyst_cost

router = APIRouter(prefix="/api", tags=["compare"])


class CompositionInput(BaseModel):
    label: str = ""
    metal_symbol: str
    metal_price: float = Field(gt=0)
    metal_price_unit: str = "$/troy_oz"
    metal_loading_wt_pct: float = Field(gt=0, le=100)
    support_name: str = "Al2O3"
    support_price_per_lb: float = 0.50
    steps: list[str] = ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"]
    order_size_tons: float = 10.0


class CompareRequest(BaseModel):
    compositions: list[CompositionInput] = Field(..., min_length=2, max_length=4)


@router.post("/compare")
def compare_compositions(req: CompareRequest):
    """Compare up to 4 catalyst compositions side-by-side."""
    results = []
    for i, comp in enumerate(req.compositions):
        try:
            result = estimate_catalyst_cost(
                metal_symbol=comp.metal_symbol,
                metal_price=comp.metal_price,
                metal_price_unit=comp.metal_price_unit,
                metal_loading_wt_pct=comp.metal_loading_wt_pct,
                support_name=comp.support_name,
                support_price_per_lb=comp.support_price_per_lb,
                steps=comp.steps,
                order_size_tons=comp.order_size_tons,
            )
            results.append({
                "index": i,
                "label": comp.label or f"{comp.metal_symbol}/{comp.support_name}",
                "metal_symbol": comp.metal_symbol,
                "metal_loading_wt_pct": comp.metal_loading_wt_pct,
                "support_name": comp.support_name,
                "order_size_tons": comp.order_size_tons,
                "estimated_price_per_lb": result["summary"]["estimated_price_per_lb"],
                "estimated_price_per_kg": result["summary"]["estimated_price_per_kg"],
                "materials_cost_per_lb": result["materials"]["total_materials_cost_per_lb"],
                "processing_cost_per_lb": result["step_method"]["processing_cost_per_lb"],
                "materials_pct": result["summary"]["materials_pct"],
                "processing_pct": result["summary"]["processing_pct"],
                "scale": result["step_method"]["scale"],
            })
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"Composition {i}: {e}")

    return {"compositions": results}
