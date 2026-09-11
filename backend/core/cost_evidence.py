"""Conservative comparisons between saved estimates and local cost evidence."""

import re
from collections import Counter
from math import isclose

from backend.core.constants import LB_PER_KG
from backend.schemas.cost_evidence import ActualCostObservation


def _text(value: object) -> str:
    return " ".join(str(value or "").split()).casefold()


def _price_period(request: dict, result: dict) -> str | None:
    """Require a known common month for every input price, not just one metal."""
    snapshots = {
        row.get("material_key"): row
        for row in result.get("resolved_materials", [])
        if row.get("used_for", "").startswith("component:")
    }
    months = []
    for component in request.get("components") or []:
        if component.get("material_key"):
            snapshot = snapshots.get(component["material_key"], {})
            basis = snapshot.get("pricing_basis") or ""
            match = re.search(r"reference_monthly:[^:]+:(\d{4}-\d{2})$", basis)
            month = match.group(1) if match else (
                snapshot.get("live_override", {}).get("live_fetched_at") or ""
            )[:7]
        else:
            month = str((component.get("purchase_evidence") or {}).get("quote_date") or "")[:7]
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month):
            return None
        months.append(month)
    return months[0] if months and len(set(months)) == 1 else None


def expected_cost_reference(request: dict, result: dict) -> dict:
    """Return the preserved snapshot conditions; never synthesize missing evidence."""
    components = request.get("components") or []
    total = sum(float(item.get("wt_pct", 0)) for item in components)
    breakdown = result.get("materials", {}).get("components", [])
    if not breakdown:
        breakdown = result.get("materials", {}).get("breakdown", [])
    resolved_names = [row.get("name") for row in breakdown]
    normalized = [
        {
            "name": (
                resolved_names[index] if index < len(resolved_names) else None
            ) if item.get("material_key") else item.get("name"),
            "wt_pct": float(item.get("wt_pct", 0)) / total * 100 if total else None,
            "grade": (item.get("purchase_evidence") or {}).get("grade"),
        }
        for index, item in enumerate(components)
    ]
    step_method = result.get("step_method") or {}
    return {
        "catalyst_domain": request.get("catalyst_domain", "thermal"),
        "components": normalized,
        "order_size_tons": request.get("order_size_tons"),
        "production_rate_ton_per_day": step_method.get("production_rate_ton_per_day"),
        "template_id": request.get("template_id"),
        "steps": [row["step"] for row in step_method.get("step_details", [])],
        "price_period": _price_period(request, result),
        "price_basis": request.get("price_basis", "live"),
        "costing_scope": result.get("costing_scope"),
    }


def assess_actual_cost(request: dict, result: dict, observation: dict) -> dict:
    """Keep errors null unless independently entered conditions match the snapshot."""
    actual = ActualCostObservation.model_validate(observation)
    expected = expected_cost_reference(request, result)
    reasons: list[str] = []
    if not actual.verified_by_user:
        reasons.append("The source and entered conditions have not been confirmed by the user.")
    if actual.evidence_type not in {"invoice", "production_record", "public_literature"}:
        reasons.append("A quote is not an observed full manufacturing cost or completed transaction.")
    if actual.cost_boundary not in {
        "full_manufacturing_cost", "full_selling_price", "full_net_after_recovery",
    }:
        reasons.append("The observation is not a full cost with a comparable selling-margin/recovery boundary.")
    if not actual.cost_scope_note or not actual.production_conditions_note:
        reasons.append("Document both the observed cost inclusions and production conditions.")
    if expected["catalyst_domain"] != "thermal" or actual.price_unit == "cm2":
        reasons.append("Full-cost error assessment is currently limited to mass-based thermal catalysts.")
    if actual.currency != "USD":
        reasons.append("The saved estimate is in USD; no currency conversion has been assumed.")
    if not expected["price_period"] or actual.price_period != expected["price_period"]:
        reasons.append("The price month is missing or differs from the saved component price month.")
    if actual.price_period and actual.observation_date.strftime("%Y-%m") != actual.price_period:
        reasons.append("The observation date and stated price month differ.")
    for key, label in (
        ("order_size_tons", "Production quantity"),
        ("production_rate_ton_per_day", "Effective production rate"),
    ):
        observed = getattr(actual, key)
        reference = expected[key]
        if observed is None or reference is None or not isclose(observed, reference, rel_tol=1e-6):
            reasons.append(f"{label} is missing or differs from the saved production conditions.")
    if actual.template_id != expected["template_id"]:
        reasons.append("The manufacturing template differs from the saved estimate.")
    if not expected["steps"] or Counter(actual.steps) != Counter(expected["steps"]):
        reasons.append("The observed manufacturing steps do not match the saved costed steps.")

    reference_components = expected["components"]
    actual_components = actual.components
    reference_names = [_text(item["name"]) for item in reference_components]
    actual_names = [_text(item.name) for item in actual_components]
    if (
        not reference_components or len(set(reference_names)) != len(reference_names)
        or len(set(actual_names)) != len(actual_names)
        or sorted(reference_names) != sorted(actual_names)
    ):
        reasons.append("The observed composition does not uniquely match the saved components.")
    else:
        by_name = {_text(item.name): item for item in actual_components}
        actual_total = sum(item.wt_pct for item in actual_components)
        if not isclose(actual_total, 100, abs_tol=0.01):
            reasons.append("Observed composition must total 100 wt%; it is not normalized automatically.")
        for reference in reference_components:
            item = by_name[_text(reference["name"])]
            if not isclose(item.wt_pct, reference["wt_pct"], abs_tol=0.01):
                reasons.append(f"Composition differs for {reference['name']}.")
            if not _text(reference["grade"]) or _text(item.grade) != _text(reference["grade"]):
                reasons.append(f"Grade is unknown or differs for {reference['name']}.")

    scope = expected["costing_scope"] or {}
    route = result.get("route_summary") or {}
    if (
        scope.get("status") == "partial" or scope.get("uncosted_operations")
        or scope.get("dropped_steps") or scope.get("omitted_template_steps")
        or route.get("uncosted_operations")
    ):
        reasons.append("The estimate omits manufacturing operations; a full-cost error would be misleading.")
    scope_steps = scope.get("costed_steps") or []
    if (
        scope.get("status") not in {"modeled_steps", "proxy"} or not scope_steps
        or any(step.get("status") not in {"costed", "proxy"} for step in scope_steps)
        or Counter(step.get("step") for step in scope_steps) != Counter(expected["steps"])
    ):
        reasons.append("The saved estimate does not preserve a recognized, consistent manufacturing costing scope.")
    if request.get("consumables") or any(
        component.get("recipe_consumption")
        for component in request.get("components") or []
    ):
        reasons.append("Actual precursor and auxiliary consumption must be matched before recipe costs are compared.")

    summary = result.get("summary") or {}
    predicted_per_lb = {
        "full_manufacturing_cost": (result.get("step_method") or {}).get("pre_margin_per_lb"),
        "full_selling_price": summary.get("estimated_price_per_lb"),
        "full_net_after_recovery": summary.get("net_cost_per_lb"),
    }.get(actual.cost_boundary)
    if predicted_per_lb is None:
        reasons.append("No saved prediction exists for the observation's cost boundary.")
    predicted = None if predicted_per_lb is None else float(predicted_per_lb) * (
        LB_PER_KG if actual.price_unit == "kg" else 1.0
    )
    eligible = not reasons
    signed_error = (predicted - actual.observed_price) / actual.observed_price * 100 if eligible else None
    return {
        "eligible": eligible,
        "exclusion_reasons": reasons,
        "predicted_price": round(predicted, 6) if predicted is not None else None,
        "signed_error_pct": round(signed_error, 6) if signed_error is not None else None,
        "absolute_percentage_error": round(abs(signed_error), 6) if signed_error is not None else None,
        "verification": "user_supplied_not_independently_verified",
    }


def summarize_observations(request: dict, result: dict) -> dict:
    observations = []
    for stored in result.get("local_cost_observations", []):
        observations.append({**stored, "assessment": assess_actual_cost(request, result, stored["observation"])})
    errors = [row["assessment"]["absolute_percentage_error"] for row in observations if row["assessment"]["eligible"]]
    return {
        "expected_reference": expected_cost_reference(request, result),
        "observations": observations,
        "eligible_count": len(errors),
        "mape_pct": round(sum(errors) / len(errors), 6) if errors else None,
        "verification": "user_supplied_not_independently_verified",
    }
