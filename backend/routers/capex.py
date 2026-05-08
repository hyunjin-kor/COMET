"""CapEx & OpEx Factors API endpoint.

Exposes the Chapter-7 factored-cost methodology that already lived in
``backend/core/capex_opex.py`` via a single ``POST /api/capex`` route the
desktop UI's CapEx workspace consumes.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.core.capex_opex import (
    calculate_capex,
    calculate_opex,
    equipment_cost_scaling,
)
from backend.schemas.capex_opex import (
    CapExRequest,
    CapExResult,
    EquipmentResolution,
)

router = APIRouter(prefix="/api", tags=["capex"])


def _resolve_equipment(req: CapExRequest) -> tuple[float, list[EquipmentResolution]]:
    """Sum equipment-line scaling into a purchased-equipment basis."""

    if req.purchased_equipment_cost_usd is not None and req.purchased_equipment_cost_usd > 0:
        return float(req.purchased_equipment_cost_usd), []

    resolutions: list[EquipmentResolution] = []
    total = 0.0
    assert req.equipment is not None  # validated upstream
    for item in req.equipment:
        scaled_unit = equipment_cost_scaling(
            base_price=item.base_cost_usd,
            base_size=item.base_size,
            target_size=item.target_size,
            exponent=item.exponent,
        )
        line_total = scaled_unit * item.quantity
        total += line_total
        resolutions.append(
            EquipmentResolution(
                name=item.name,
                base_cost_usd=item.base_cost_usd,
                base_size=item.base_size,
                target_size=item.target_size,
                exponent=item.exponent,
                quantity=item.quantity,
                scaled_unit_cost_usd=round(scaled_unit, 2),
                line_total_usd=round(line_total, 2),
            )
        )
    return round(total, 2), resolutions


@router.post("/capex", response_model=CapExResult)
def calculate_capex_endpoint(req: CapExRequest) -> CapExResult:
    """Run the CatCost Chapter-7 factored CapEx (and optional OpEx) estimate."""

    try:
        purchased_equipment_cost, resolutions = _resolve_equipment(req)
        capex_breakdown = calculate_capex(purchased_equipment_cost)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    opex_breakdown = None
    if req.opex_inputs is not None and (
        req.opex_inputs.direct_labor_cost_usd > 0
        or req.opex_inputs.raw_materials_cost_usd > 0
        or req.opex_inputs.utilities_cost_usd > 0
    ):
        opex_breakdown = calculate_opex(
            fci=capex_breakdown["fixed_capital_investment"],
            direct_labor_cost=req.opex_inputs.direct_labor_cost_usd,
            raw_materials_cost=req.opex_inputs.raw_materials_cost_usd,
            utilities_cost=req.opex_inputs.utilities_cost_usd,
        )

    fci = capex_breakdown["fixed_capital_investment"]
    tci = capex_breakdown["total_capital_investment"]
    summary = {
        "purchased_equipment_cost_usd": purchased_equipment_cost,
        "fixed_capital_investment_usd": fci,
        "total_capital_investment_usd": tci,
        "fci_to_purchased_equipment_ratio": round(fci / purchased_equipment_cost, 3) if purchased_equipment_cost > 0 else 0.0,
        "tci_to_purchased_equipment_ratio": round(tci / purchased_equipment_cost, 3) if purchased_equipment_cost > 0 else 0.0,
        "annual_opex_usd": opex_breakdown["total_annual_opex"] if opex_breakdown else None,
    }

    return CapExResult(
        purchased_equipment_cost_usd=purchased_equipment_cost,
        equipment_resolution=resolutions,
        capex=capex_breakdown,
        opex=opex_breakdown,
        summary=summary,
    )
