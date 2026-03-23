"""Calculator API endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.core.cost_engine import estimate_catalyst_cost
from backend.database import get_session
from backend.models.estimate import Estimate
from backend.schemas.cost_input import CostCalculationRequest, QuickCalculationRequest

router = APIRouter(prefix="/api", tags=["calculator"])


@router.post("/calculate")
def calculate_cost(req: CostCalculationRequest):
    """Full catalyst cost estimation using Step Method."""
    try:
        result = estimate_catalyst_cost(
            metal_symbol=req.metal_symbol,
            metal_price=req.metal_price,
            metal_price_unit=req.metal_price_unit,
            metal_loading_wt_pct=req.metal_loading_wt_pct,
            support_name=req.support_name,
            support_price_per_lb=req.support_price_per_lb,
            precursor_metal_fraction=req.precursor_metal_fraction,
            precursor_markup=req.precursor_markup,
            steps=req.steps,
            order_size_tons=req.order_size_tons,
            solvent_cost_per_lb_cat=req.solvent_cost_per_lb_cat,
            ga_overhead_pct=req.ga_overhead_pct,
            sard_pct=req.sard_pct,
            basis_year=req.basis_year,
            target_year=req.target_year,
            include_spent_value=req.include_spent_value,
            reactor_type=req.reactor_type,
            catalyst_bulk_density=req.catalyst_bulk_density,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/calculate/quick")
def calculate_cost_quick(req: QuickCalculationRequest):
    """Quick estimation with minimal inputs (Step Method only)."""
    # Load template steps if provided
    steps = ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"]
    if req.template_id:
        from backend.core.constants import STEP_COSTS
        import json as _json
        from pathlib import Path

        template_path = (
            Path(__file__).resolve().parent.parent
            / "data"
            / "process_templates"
            / f"{req.template_id}.json"
        )
        if template_path.exists():
            with open(template_path) as f:
                template = _json.load(f)
            steps = template.get("steps", steps)

    try:
        result = estimate_catalyst_cost(
            metal_symbol=req.metal_symbol,
            metal_price=req.metal_price,
            metal_price_unit=req.metal_price_unit,
            metal_loading_wt_pct=req.metal_loading_wt_pct,
            support_name=req.support_name,
            support_price_per_lb=req.support_price_per_lb,
            steps=steps,
            order_size_tons=req.order_size_tons,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/calculate/save")
def save_estimate(
    req: CostCalculationRequest,
    name: str = "Untitled",
    session: Session = Depends(get_session),
):
    """Calculate and save an estimate."""
    try:
        result = estimate_catalyst_cost(
            metal_symbol=req.metal_symbol,
            metal_price=req.metal_price,
            metal_price_unit=req.metal_price_unit,
            metal_loading_wt_pct=req.metal_loading_wt_pct,
            support_name=req.support_name,
            support_price_per_lb=req.support_price_per_lb,
            precursor_metal_fraction=req.precursor_metal_fraction,
            precursor_markup=req.precursor_markup,
            steps=req.steps,
            order_size_tons=req.order_size_tons,
            solvent_cost_per_lb_cat=req.solvent_cost_per_lb_cat,
            ga_overhead_pct=req.ga_overhead_pct,
            sard_pct=req.sard_pct,
            basis_year=req.basis_year,
            target_year=req.target_year,
            include_spent_value=req.include_spent_value,
            reactor_type=req.reactor_type,
            catalyst_bulk_density=req.catalyst_bulk_density,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    estimate = Estimate(
        name=name,
        metal_symbol=req.metal_symbol,
        metal_loading_wt_pct=req.metal_loading_wt_pct,
        support_name=req.support_name,
        order_size_tons=req.order_size_tons,
        estimated_price_per_lb=result["summary"]["estimated_price_per_lb"],
        input_json=json.dumps(req.model_dump()),
        result_json=json.dumps(result),
    )
    session.add(estimate)
    session.commit()
    session.refresh(estimate)

    return {"id": estimate.id, "result": result}
