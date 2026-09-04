"""Dedicated process-template API endpoints."""

from fastapi import APIRouter, Query

from backend.core.constants import LB_PER_KG
from backend.core.price_escalation import get_escalation_factor, latest_index_year
from backend.core.step_method import calculate_step_method, determine_scale, fit_steps_to_scale
from backend.routers import materials

router = APIRouter(prefix="/api/templates", tags=["templates"])

STEP_BASIS_YEAR = 2017


@router.get("")
def list_templates(catalyst_domain: str | None = Query(default=None)):
    """List available process templates."""

    return materials.list_templates(catalyst_domain)


@router.get("/costs")
def template_costs(
    order_size_tons: float = Query(default=20.0, gt=0),
    catalyst_domain: str | None = Query(default=None),
):
    """Processing cost of every template at one campaign size.

    Steps are fitted to the campaign's scale first (batch kiln at Small,
    continuous kiln at Medium and Large, and so on), and the fitted list is
    returned so a caller applying the method gets a route the Step Method can
    price. Materials are excluded, so the figure is the route's own cost.
    """

    scale = determine_scale(order_size_tons)
    target_year = latest_index_year("chemppi")
    try:
        escalation = get_escalation_factor(STEP_BASIS_YEAR, target_year, "chemppi")
    except KeyError:
        escalation = 1.0

    templates = []
    for template in materials.list_templates(catalyst_domain):
        if not template["steps"]:
            continue
        fitted, substitutions, dropped = fit_steps_to_scale(template["steps"], scale)
        entry = {
            "id": template["id"],
            "name": template["name"],
            "category": template["category"],
            "catalyst_domain": template["catalyst_domain"],
            "steps": template["steps"],
            "steps_fitted": fitted,
            "substitutions": substitutions,
            "dropped_steps": dropped,
            "uncosted_operations": template.get("uncosted_operations", []),
            "processing_cost_per_lb": None,
            "processing_cost_per_kg": None,
            "step_cost_per_hr": None,
            "campaign_days": None,
        }
        if fitted:
            result = calculate_step_method(
                materials_cost_per_lb=0.0,
                steps=fitted,
                order_size_tons=order_size_tons,
                chemppi_escalation=escalation,
            )
            per_lb = float(result["processing_cost_per_lb"])
            entry.update(
                processing_cost_per_lb=round(per_lb, 4),
                processing_cost_per_kg=round(per_lb * LB_PER_KG, 4),
                step_cost_per_hr=result["step_cost_per_hr"],
                campaign_days=result["campaign_days"],
            )
        templates.append(entry)

    return {
        "order_size_tons": order_size_tons,
        "scale": scale,
        "basis_year": STEP_BASIS_YEAR,
        "target_year": target_year,
        "chemppi_escalation": round(escalation, 4),
        "templates": templates,
    }


@router.get("/{template_id}")
def get_template(template_id: str):
    """Return one process template by id."""

    return materials.get_template(template_id)
