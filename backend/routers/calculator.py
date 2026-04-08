"""Calculator API endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.core.cost_engine import estimate_catalyst_cost, estimate_catalyst_cost_simple
from backend.core.material_pricing import resolve_component_input, resolve_electrode_materials
from backend.database import get_session
from backend.models.estimate import Estimate
from backend.paths import data_dir
from backend.schemas.cost_input import CostCalculationRequest, QuickCalculationRequest

router = APIRouter(prefix="/api", tags=["calculator"])
_DATA_DIR = data_dir()


def _load_template(template_id: str | None) -> dict | None:
    """Load a process template JSON document if present."""

    if not template_id:
        return None
    template_path = _DATA_DIR / "process_templates" / f"{template_id}.json"
    if not template_path.exists():
        raise ValueError(f"Template '{template_id}' not found")
    with open(template_path, encoding="utf-8") as handle:
        return json.load(handle)


def _template_summary(template: dict | None) -> dict | None:
    """Normalize the saved route metadata returned to the frontend."""

    if template is None:
        return None
    return {
        "template_id": template["id"],
        "name": template["name"],
        "catalyst_domain": template.get("catalyst_domain", "thermal"),
        "application_family": template.get("application_family", "general"),
        "manufacturing_mode": template.get("manufacturing_mode", "batch"),
        "preprocess": template.get("preprocess", []),
        "synthesis": template.get("synthesis", []),
        "postprocess": template.get("postprocess", []),
        "quality_gates": template.get("quality_gates", []),
        "steps": template.get("steps", []),
        "route_note": template.get("route_note", ""),
        "source": template.get("source", ""),
        "reference_urls": template.get("reference_urls", []),
    }


def _component_payload(req: CostCalculationRequest) -> list[dict]:
    """Build the component payload before DB-backed price resolution."""

    if req.components:
        return [component.model_dump(exclude_none=True) for component in req.components]

    if (
        req.catalyst_domain == "electrocatalyst"
        and req.electrode_input is not None
        and req.electrode_input.catalyst_material_key
    ):
        return [{
            "role": "active_catalyst",
            "material_key": req.electrode_input.catalyst_material_key,
            "name": "Electrocatalyst powder",
            "wt_pct": 100.0,
            "precursor_markup": 1.0,
        }]

    return req.to_components()


def _prepare_calculation(req: CostCalculationRequest, session: Session) -> tuple[dict, list[dict], str]:
    """Resolve template and library-backed materials into an engine-ready payload."""

    template = _load_template(req.template_id)
    route_summary = _template_summary(template)

    application_family = req.application_family
    if template and application_family == "general":
        application_family = template.get("application_family", application_family)
    if req.electrode_input and req.electrode_input.application_family != "general":
        application_family = req.electrode_input.application_family

    resolved_components: list[dict] = []
    resolved_materials: list[dict] = []
    for component in _component_payload(req):
        resolved_component, snapshot = resolve_component_input(session, component)
        resolved_components.append(resolved_component)
        if snapshot is not None:
            resolved_materials.append(snapshot)

    raw_electrode = req.electrode_input.model_dump(exclude_none=True) if req.electrode_input else None
    electrode_payload, electrode_snapshots = resolve_electrode_materials(session, raw_electrode)
    resolved_materials.extend(electrode_snapshots)

    if electrode_payload is not None:
        electrode_payload["application_family"] = application_family
        if "catalyst_price_per_lb" not in electrode_payload:
            active_components = [
                component
                for component in resolved_components
                if component["role"] in {"active_metal", "active_catalyst"}
            ]
            if active_components:
                primary = max(active_components, key=lambda item: float(item["wt_pct"]))
                electrode_payload["catalyst_price_per_lb"] = float(primary["price_per_lb"])

    steps = req.steps
    if template and (not steps):
        steps = template.get("steps", steps)

    result = estimate_catalyst_cost(
        components=resolved_components,
        metal_symbol=req.metal_symbol,
        metal_price=req.metal_price,
        metal_price_unit=req.metal_price_unit,
        metal_loading_wt_pct=req.metal_loading_wt_pct,
        support_name=req.support_name,
        support_price_per_lb=req.support_price_per_lb,
        precursor_metal_fraction=req.precursor_metal_fraction,
        precursor_markup=req.precursor_markup,
        steps=steps,
        catalyst_domain=req.catalyst_domain,
        application_family=application_family,
        order_size_tons=req.order_size_tons,
        ga_overhead_pct=req.ga_overhead_pct,
        sard_pct=req.sard_pct,
        basis_year=req.basis_year,
        target_year=req.target_year,
        include_spent_value=req.include_spent_value,
        reactor_type=req.reactor_type,
        catalyst_bulk_density=req.catalyst_bulk_density,
        electrode_input=electrode_payload,
        route_summary=route_summary,
        resolved_materials=resolved_materials,
    )
    return result, resolved_components, application_family


@router.post("/calculate")
def calculate_cost(
    req: CostCalculationRequest,
    session: Session = Depends(get_session),
):
    """Full catalyst cost estimation with optional library-backed materials."""

    try:
        result, _, _ = _prepare_calculation(req, session)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/calculate/quick")
def calculate_cost_quick(req: QuickCalculationRequest):
    """Quick estimation with minimal single-metal inputs."""

    steps = ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"]
    if req.template_id:
        template = _load_template(req.template_id)
        if template is not None:
            steps = template.get("steps", steps)

    try:
        result = estimate_catalyst_cost_simple(
            metal_symbol=req.metal_symbol,
            metal_price=req.metal_price,
            metal_price_unit=req.metal_price_unit,
            metal_loading_wt_pct=req.metal_loading_wt_pct,
            support_name=req.support_name,
            support_price_per_lb=req.support_price_per_lb,
            steps=steps,
            catalyst_domain=req.catalyst_domain,
            application_family=req.application_family,
            order_size_tons=req.order_size_tons,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.post("/calculate/save")
def save_estimate(
    req: CostCalculationRequest,
    name: str = "Untitled",
    session: Session = Depends(get_session),
):
    """Calculate and save an estimate to the database."""

    try:
        result, resolved_components, application_family = _prepare_calculation(req, session)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    active = [
        component for component in resolved_components
        if component["role"] in {"active_metal", "active_catalyst"}
    ]
    supports = [component for component in resolved_components if component["role"] == "support"]
    primary_active = active[0] if active else {"name": req.metal_symbol or "unknown", "wt_pct": 0.0}
    primary_support = max(supports, key=lambda component: float(component["wt_pct"])) if supports else {"name": ""}

    estimate = Estimate(
        name=name,
        catalyst_domain=req.catalyst_domain,
        application_family=application_family,
        calculation_model=(
            "catcost_step_plus_electrode"
            if result.get("electrode_model") is not None
            else "catcost_step"
        ),
        metal_symbol=str(primary_active["name"]),
        metal_loading_wt_pct=float(primary_active["wt_pct"]),
        support_name=str(primary_support["name"]) if supports else "",
        order_size_tons=req.order_size_tons,
        estimated_price_per_lb=result["summary"]["estimated_price_per_lb"],
        input_json=json.dumps(req.model_dump()),
        result_json=json.dumps(result),
    )
    session.add(estimate)
    session.commit()
    session.refresh(estimate)

    return {"id": estimate.id, "result": result}
