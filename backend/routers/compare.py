"""Multi-composition comparison endpoint."""

from fastapi import APIRouter, HTTPException

from backend.core.cost_engine import estimate_catalyst_cost_simple
from backend.schemas.comparison import CompareRequest, CompareResponse

router = APIRouter(prefix="/api", tags=["compare"])


@router.post("/compare", response_model=CompareResponse)
def compare_compositions(req: CompareRequest):
    """Compare up to 4 catalyst compositions side-by-side."""
    results = []
    for i, comp in enumerate(req.compositions):
        try:
            result = estimate_catalyst_cost_simple(
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
            raise HTTPException(status_code=422, detail=f"Composition {i + 1}: {e}")

    return {"compositions": results}
