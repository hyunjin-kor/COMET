"""Monte Carlo uncertainty analysis endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.core.uncertainty import run_monte_carlo

router = APIRouter(prefix="/api", tags=["uncertainty"])


class UncertaintyRequest(BaseModel):
    metal_symbol: str
    metal_price: float = Field(gt=0)
    metal_price_unit: str = "$/troy_oz"
    metal_loading_wt_pct: float = Field(gt=0, le=100)
    support_name: str = "Al2O3"
    support_price_per_lb: float = 0.50
    steps: list[str] = ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"]
    order_size_tons: float = 10.0
    n_simulations: int = Field(default=1000, ge=100, le=10000)
    uncertainties: dict[str, list[float]] | None = None


@router.post("/uncertainty")
def uncertainty_analysis(req: UncertaintyRequest):
    """Run Monte Carlo simulation on cost estimation."""
    base_params = {
        "metal_symbol": req.metal_symbol,
        "metal_price": req.metal_price,
        "metal_price_unit": req.metal_price_unit,
        "metal_loading_wt_pct": req.metal_loading_wt_pct,
        "support_name": req.support_name,
        "support_price_per_lb": req.support_price_per_lb,
        "steps": req.steps,
        "order_size_tons": req.order_size_tons,
    }

    uncertainties = None
    if req.uncertainties:
        uncertainties = {k: tuple(v) for k, v in req.uncertainties.items()}

    try:
        result = run_monte_carlo(
            base_params=base_params,
            uncertainties=uncertainties,
            n_simulations=req.n_simulations,
            seed=42,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
