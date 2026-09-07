"""Reprice saved formulations without changing their stored evidence."""

from __future__ import annotations

from copy import deepcopy

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.core.step_method import determine_scale, fit_steps_to_scale
from backend.database import get_session
from backend.models.estimate import Estimate
from backend.routers.calculator import _estimate_from_context, _prepare_calculation_context
from backend.schemas.cost_input import CostCalculationRequest
from backend.schemas.estimate_comparison import EstimateComparisonRequest

router = APIRouter(prefix="/api/estimates", tags=["estimates"])

_SHARED_FIELDS = (
    "basis_year", "target_year", "ga_overhead_pct", "sard_pct",
    "include_spent_value", "reactor_type", "catalyst_bulk_density",
    "production_rate_ton_per_day", "production_rate_note",
)
_ELECTRODE_SHARED = (
    "active_area_cm2", "catalyst_loading_mg_cm2", "ionomer_to_catalyst_ratio",
    "manufacturing_scenario",
)
_ELECTRODE_PRICES = {
    "catalyst": ("catalyst_price_per_lb",),
    "ionomer": ("ionomer_price_per_ml", "ionomer_price_per_kg_solids",
                "ionomer_density_g_ml", "ionomer_solids_fraction"),
    "substrate": ("substrate_cost_per_cm2",),
    "membrane": ("membrane_cost_per_cm2",),
}


def _identity(component: dict) -> str:
    if component.get("material_key"):
        return f"library:{component['material_key']}"
    evidence = component.get("purchase_evidence") or {}
    grade = str(evidence.get("grade", "")).strip().casefold()
    name = str(component.get("name", "")).strip().casefold()
    return f"manual:{name}:{grade}"


def _headline(result: dict, domain: str) -> float | None:
    if domain == "electrocatalyst":
        value = (result.get("electrode_model") or {}).get("cost_per_cm2_usd")
    else:
        value = result.get("summary", {}).get("net_cost_per_lb")
    return float(value) if value is not None else None


def _electrode_identity(slot: str, raw: dict, payload: dict) -> str:
    key = raw.get(f"{slot}_material_key")
    if key or slot != "ionomer":
        return f"electrode:{slot}:{key or 'manual'}"
    mode = "solids" if payload.get("ionomer_price_per_kg_solids", 0) > 0 else "dispersion"
    return (
        f"electrode:ionomer:manual:{mode}:"
        f"{payload.get('ionomer_density_g_ml')}:{payload.get('ionomer_solids_fraction')}"
    )


@router.post("/compare")
def compare_saved_estimates(
    req: EstimateComparisonRequest,
    session: Session = Depends(get_session),
):
    """Apply a single price snapshot and the named reference's operating conditions.

    Manual identities are matched only by name and grade. Prices from the explicit
    reference win; materials absent there use the lowest selected estimate ID.
    Full composition, recipe consumption and manufacturing steps remain individual.
    """
    try:
        return _compare(req, session)
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _compare(req: EstimateComparisonRequest, session: Session) -> dict:
    records: dict[int, Estimate] = {}
    inputs: dict[int, CostCalculationRequest] = {}
    for estimate_id in sorted(req.estimate_ids):
        record = session.get(Estimate, estimate_id)
        if record is None:
            raise HTTPException(status_code=404, detail=f"Estimate {estimate_id} not found")
        records[estimate_id] = record
        inputs[estimate_id] = CostCalculationRequest.model_validate(record.get_input())
    reference = inputs[req.reference_estimate_id]
    domain = reference.catalyst_domain
    if any(item.catalyst_domain != domain for item in inputs.values()):
        raise ValueError("Compare estimates within the same catalyst domain")
    shared = {
        key: value for key, value in reference.model_dump().items() if key in _SHARED_FIELDS
    }
    shared.update(price_basis=req.price_basis, order_size_tons=req.order_size_tons)
    contexts = {}
    for estimate_id, original in inputs.items():
        price_request = original.model_copy(update={
            "price_basis": req.price_basis, "target_year": reference.target_year,
        })
        contexts[estimate_id] = _prepare_calculation_context(price_request, session)
    family = contexts[req.reference_estimate_id]["application_family"]
    if any(context["application_family"] != family for context in contexts.values()):
        raise ValueError("Compare estimates within the same application family")
    if domain == "electrocatalyst" and any(
        context["electrode_payload"] is None for context in contexts.values()
    ):
        raise ValueError("Electrode comparisons require electrode assembly inputs in every estimate")

    warnings = [
        "Comparison preserves each formulation, precursor consumption and manufacturing route; "
        "differences are not a route-only effect.",
        "Saved results may use an older model. The saved-to-repriced difference is not proof "
        "of a pure market-price effect when the model has changed.",
        "Manual materials with the same name and grade are assumed identical; distinct grades "
        "must have distinct names or purchase-evidence grades.",
    ]
    pool: dict[str, dict] = {}
    priority = [req.reference_estimate_id] + [
        key for key in sorted(records) if key != req.reference_estimate_id
    ]

    def record_price(key: str, values: dict, estimate_id: int, evidence: dict | None = None):
        if key not in pool:
            pool[key] = {
                "key": key, "values": values, "source_estimate_id": estimate_id,
                "source_estimate_name": records[estimate_id].name,
                "evidence": deepcopy(evidence), "overridden_estimate_ids": [],
            }
        elif pool[key]["values"] != values:
            if estimate_id not in pool[key]["overridden_estimate_ids"]:
                pool[key]["overridden_estimate_ids"].append(estimate_id)

    for estimate_id in priority:
        context = contexts[estimate_id]
        for component in context["resolved_components"]:
            evidence = next((entry for entry in context["resolved_materials"]
                             if entry.get("material_key") == component.get("material_key")
                             and entry.get("used_for", "").startswith("component:")), None)
            record_price(_identity(component), {"price_per_lb": component["price_per_lb"]},
                         estimate_id, evidence or component.get("purchase_evidence"))
            recipe = component.get("recipe_consumption")
            if recipe:
                key = "precursor:" + recipe["precursor_name"].strip().casefold()
                record_price(key, {"price_per_kg": recipe["price_per_kg"],
                                   "source_note": recipe["source_note"]}, estimate_id)
        for consumable in inputs[estimate_id].model_dump().get("consumables", []):
            key = "consumable:" + consumable["name"].strip().casefold()
            record_price(key, {"price_per_kg": consumable["price_per_kg"],
                               "source_note": consumable["source_note"]}, estimate_id)
        electrode = context["electrode_payload"]
        if electrode:
            raw = inputs[estimate_id].electrode_input.model_dump()
            for slot, fields in _ELECTRODE_PRICES.items():
                key = raw.get(f"{slot}_material_key")
                # Without a catalyst-library key, the active component supplies its price.
                if slot == "catalyst" and not key:
                    continue
                identity = _electrode_identity(slot, raw, electrode)
                values = {field: electrode.get(field, 0.0) for field in fields}
                record_price(identity, values, estimate_id)
    identity_names: dict[str, set[str]] = {}
    for context in contexts.values():
        for component in context["resolved_components"]:
            name = str(component.get("name", "")).strip().casefold()
            identity_names.setdefault(name, set()).add(_identity(component))
    if any(len(identities) > 1 for identities in identity_names.values()):
        warnings.append(
            "Some equal material names have distinct library identities or grades. Their prices "
            "remain separate because equivalent purchasing specifications have not been established."
        )
    if any(row["overridden_estimate_ids"] for row in pool.values()):
        warnings.append("Conflicting saved prices were harmonized; see each price snapshot's source and overrides.")

    shared_electrode = None
    if domain == "electrocatalyst":
        shared_electrode = {
            key: contexts[req.reference_estimate_id]["electrode_payload"].get(key)
            for key in _ELECTRODE_SHARED
        }
        warnings.append("Unlabelled manual electrode adjuncts are assumed to be the same material in each slot.")
        warnings.append("Manual ionomer dispersions with different concentrations, densities or pricing forms keep distinct prices.")
        shared["electrode_input"] = shared_electrode

    rows = []
    for estimate_id in req.estimate_ids:
        original = inputs[estimate_id]
        context = deepcopy(contexts[estimate_id])
        context["resolved_materials"] = []
        for component in context["resolved_components"]:
            price = pool[_identity(component)]
            component.update(price["values"])
            if not component.get("material_key"):
                if price["evidence"]:
                    component["purchase_evidence"] = deepcopy(price["evidence"])
                else:
                    component.pop("purchase_evidence", None)
            if price["evidence"] and component.get("material_key"):
                evidence = deepcopy(price["evidence"])
                evidence["used_for"] = f"component:{component['role']}"
                evidence["comparison_source_estimate_id"] = price["source_estimate_id"]
                context["resolved_materials"].append(evidence)
            recipe = component.get("recipe_consumption")
            if recipe:
                recipe.update(pool["precursor:" + recipe["precursor_name"].strip().casefold()]["values"])
        repriced_payload = original.model_dump()
        for consumable in repriced_payload.get("consumables", []):
            consumable.update(pool["consumable:" + consumable["name"].strip().casefold()]["values"])
        repriced_request = CostCalculationRequest.model_validate(repriced_payload)
        electrode = context["electrode_payload"]
        if electrode:
            raw = original.electrode_input.model_dump()
            for slot in _ELECTRODE_PRICES:
                key = raw.get(f"{slot}_material_key")
                if slot == "catalyst" and not key:
                    active = [component for component in context["resolved_components"]
                              if component["role"] in {"active_metal", "active_catalyst"}]
                    electrode["catalyst_price_per_lb"] = max(active, key=lambda item: item["wt_pct"])["price_per_lb"]
                else:
                    electrode.update(pool[_electrode_identity(slot, raw, electrode)]["values"])
        repriced = _estimate_from_context(repriced_request, context)
        common_updates = {key: value for key, value in shared.items() if key != "electrode_input"}
        common_request = CostCalculationRequest.model_validate({**repriced_request.model_dump(), **common_updates})
        common_context = deepcopy(context)
        fitted, substitutions, dropped = fit_steps_to_scale(
            context["steps"], determine_scale(req.order_size_tons),
        )
        common_context["steps"] = fitted
        if shared_electrode:
            common_context["electrode_payload"].update(shared_electrode)
        common = _estimate_from_context(common_request, common_context)
        scope = common.get("costing_scope")
        if scope:
            # The engine can infer template substitutions, but a custom saved
            # operation list also needs its comparison-time substitutions kept.
            if not scope["declared_steps"]:
                scope["substitutions"] = substitutions
                scope["dropped_steps"] = dropped
            if dropped:
                scope["status"] = "partial"
            elif substitutions and scope["status"] == "modeled_steps":
                scope["status"] = "proxy"
        if dropped:
            common["warnings"].append(
                "Comparison at the shared production scale leaves these unavailable steps "
                "uncosted: " + ", ".join(dropped)
            )
        for result in (repriced, common):
            result["input_summary"]["price_basis"] = req.price_basis
        historical = records[estimate_id].get_result()
        rows.append({
            "estimate_id": estimate_id, "name": records[estimate_id].name,
            "saved_at": records[estimate_id].created_at.isoformat(),
            "saved": historical, "repriced_original_conditions": repriced,
            "common_conditions": common,
            "scale_adjustment": {"substitutions": substitutions, "uncosted_steps": dropped},
            "values": {
                "saved": _headline(historical, domain),
                "repriced_original_conditions": _headline(repriced, domain),
                "common_conditions": _headline(common, domain),
            },
        })
    return {
        "reference_estimate_id": req.reference_estimate_id,
        "catalyst_domain": domain, "application_family": family,
        "unit": "USD/cm2" if domain == "electrocatalyst" else "USD/lb",
        "metric": "electrode_assembly_cost" if domain == "electrocatalyst" else "selling_price_less_recovery",
        "common_conditions": shared,
        "price_snapshot": [pool[key] for key in sorted(pool)],
        "warnings": warnings, "estimates": rows,
    }
