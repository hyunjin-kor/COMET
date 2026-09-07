"""Monte Carlo uncertainty analysis for catalyst cost estimation.

Inspired by BioSTEAM's uncertainty analysis approach.
Provides probabilistic cost ranges instead of single-point estimates.
"""

from __future__ import annotations

from collections import Counter

import numpy as np

from backend.core.constants import LB_PER_KG
from backend.core.cost_engine import estimate_catalyst_cost
from backend.core.step_method import determine_scale, fit_steps_to_scale
from backend.schemas.cost_input import CostCalculationRequest


def _sample_steps(steps: list[str], original_size: float, sampled_size: float) -> list[str]:
    if determine_scale(original_size) == determine_scale(sampled_size):
        return steps
    fitted, _, dropped = fit_steps_to_scale(steps, determine_scale(sampled_size))
    if dropped:
        raise ValueError("Sampled scale has uncosted operations: " + ", ".join(dropped))
    return fitted


def run_monte_carlo(
    base_params: dict,
    uncertainties: dict[str, tuple[float, float]] | None = None,
    n_simulations: int = 1000,
    seed: int | None = None,
) -> dict:
    """Run Monte Carlo simulation on catalyst cost estimation.

    Args:
        base_params: Base parameters for estimate_catalyst_cost().
        uncertainties: Dict mapping parameter name to (low_factor, high_factor)
                       relative to base value. E.g. {"metal_price": (0.8, 1.2)}
                       means metal price varies from 80% to 120% of base.
        n_simulations: Number of Monte Carlo iterations.
        seed: Random seed for reproducibility.

    Returns:
        Dict with statistical summary and raw results.
    """
    rng = np.random.default_rng(seed)

    if uncertainties is None:
        uncertainties = {
            "metal_price": (0.8, 1.2),
            "support_price_per_lb": (0.9, 1.1),
            "order_size_tons": (0.8, 1.2),
        }

    results = []
    failures = Counter()
    for _ in range(n_simulations):
        params = dict(base_params)
        for param, (lo, hi) in uncertainties.items():
            if param in params:
                base_val = base_params[param]
                factor = rng.uniform(lo, hi)
                params[param] = base_val * factor

        try:
            params["steps"] = _sample_steps(base_params["steps"], base_params["order_size_tons"], params["order_size_tons"])
            result = estimate_catalyst_cost(**params)
            results.append(result["summary"]["estimated_price_per_lb"])
        except (ValueError, KeyError) as exc:
            failures[str(exc)] += 1
            continue

    if not results:
        raise ValueError("All simulations failed")

    arr = np.array(results)

    return {
        "n_simulations": n_simulations,
        "n_successful": len(results),
        "n_failed": n_simulations - len(results),
        "failure_reasons": dict(failures),
        "seed": seed,
        "mean": round(float(np.mean(arr)), 4),
        "median": round(float(np.median(arr)), 4),
        "std": round(float(np.std(arr)), 4),
        "min": round(float(np.min(arr)), 4),
        "max": round(float(np.max(arr)), 4),
        "p5": round(float(np.percentile(arr, 5)), 4),
        "p25": round(float(np.percentile(arr, 25)), 4),
        "p75": round(float(np.percentile(arr, 75)), 4),
        "p95": round(float(np.percentile(arr, 95)), 4),
        "unit": "$/lb",
        "uncertainties_applied": uncertainties,
    }


def run_cost_request_monte_carlo(
    *,
    req: CostCalculationRequest,
    context: dict,
    uncertainties: dict[str, tuple[float, float]] | None = None,
    n_simulations: int = 1000,
    seed: int | None = None,
) -> dict:
    """Run Monte Carlo analysis from the full calculator request."""

    rng = np.random.default_rng(seed)

    if uncertainties is None:
        uncertainties = {
            "active_component_price": (0.7, 1.3),
            "promoter_price": (0.8, 1.2),
            "support_price": (0.8, 1.2),
            "electrode_adjunct_price": (0.85, 1.15),
            "order_size_tons": (0.8, 1.2),
        }

    baseline = estimate_catalyst_cost(
        components=context["resolved_components"],
        steps=context["steps"],
        catalyst_domain=req.catalyst_domain,
        application_family=context["application_family"],
        order_size_tons=req.order_size_tons,
        ga_overhead_pct=req.ga_overhead_pct,
        sard_pct=req.sard_pct,
        basis_year=req.basis_year,
        target_year=req.target_year,
        include_spent_value=req.include_spent_value,
        reactor_type=req.reactor_type,
        catalyst_bulk_density=req.catalyst_bulk_density,
        electrode_input=context["electrode_payload"],
        route_summary=context["route_summary"],
        resolved_materials=context["resolved_materials"],
        production_rate_ton_per_day=req.production_rate_ton_per_day,
        production_rate_note=req.production_rate_note,
        consumables=[c.model_dump() for c in req.consumables],
    )

    area_cost = baseline.get("electrode_model") is not None
    precision = 6 if area_cost else 4

    def outcome(result):
        if area_cost:
            return result["electrode_model"]["cost_per_cm2_usd"]
        key = "net_cost_per_lb" if req.include_spent_value else "estimated_price_per_lb"
        return result["summary"][key]

    baseline_value = float(outcome(baseline))
    bounds = np.array([uncertainties.get(key, (1.0, 1.0)) for key in (
        "active_component_price", "promoter_price", "support_price",
        "electrode_adjunct_price", "order_size_tons",
    )])
    factors = rng.uniform(bounds[:, 0], bounds[:, 1], size=(n_simulations, 5))
    results = []
    failures = Counter()
    for factor_row in factors:
        active_factor, promoter_factor, support_factor, adjunct_factor, order_factor = map(float, factor_row)
        varied_components = [dict(component) for component in context["resolved_components"]]
        varied_electrode = dict(context["electrode_payload"]) if context["electrode_payload"] is not None else None
        order_size = req.order_size_tons

        for component in varied_components:
            base_price = float(component.get("price_per_lb", 0.0))
            if component.get("recipe_consumption"):
                recipe = dict(component["recipe_consumption"])
                factor = (support_factor if component["role"] == "support" else
                          promoter_factor if component["role"] == "promoter" else active_factor)
                recipe["price_per_kg"] = float(recipe["price_per_kg"]) * factor
                component["recipe_consumption"] = recipe
            if base_price <= 0:
                continue
            if component["role"] in {"active_metal", "active_catalyst"}:
                component["price_per_lb"] = base_price * active_factor
            elif component["role"] == "promoter":
                component["price_per_lb"] = base_price * promoter_factor
            elif component["role"] == "support":
                component["price_per_lb"] = base_price * support_factor

        if varied_electrode is not None:
            if "catalyst_price_per_lb" in varied_electrode:
                varied_electrode["catalyst_price_per_lb"] = (
                    float(varied_electrode["catalyst_price_per_lb"]) * active_factor
                )
            for key in (
                "ionomer_price_per_ml",
                "ionomer_price_per_kg_solids",
                "substrate_cost_per_cm2",
                "membrane_cost_per_cm2",
            ):
                if key in varied_electrode:
                    varied_electrode[key] = float(varied_electrode[key]) * adjunct_factor

        if not area_cost:
            order_size *= order_factor

        try:
            result = estimate_catalyst_cost(
                components=varied_components,
                steps=_sample_steps(context["steps"], req.order_size_tons, order_size),
                catalyst_domain=req.catalyst_domain,
                application_family=context["application_family"],
                order_size_tons=order_size,
                ga_overhead_pct=req.ga_overhead_pct,
                sard_pct=req.sard_pct,
                basis_year=req.basis_year,
                target_year=req.target_year,
                include_spent_value=req.include_spent_value,
                reactor_type=req.reactor_type,
                catalyst_bulk_density=req.catalyst_bulk_density,
                electrode_input=varied_electrode,
                route_summary=context["route_summary"],
                resolved_materials=context["resolved_materials"],
                production_rate_ton_per_day=req.production_rate_ton_per_day,
                production_rate_note=req.production_rate_note,
                consumables=[c.model_dump() for c in req.consumables],
            )
            results.append(outcome(result))
        except (ValueError, KeyError) as exc:
            failures[str(exc)] += 1
            continue

    if not results:
        raise ValueError("All simulations failed")

    arr = np.array(results)

    return {
        "n_simulations": n_simulations,
        "n_successful": len(results),
        "n_failed": n_simulations - len(results),
        "failure_reasons": dict(failures),
        "seed": seed,
        "mean": round(float(np.mean(arr)), precision),
        "median": round(float(np.median(arr)), precision),
        "std": round(float(np.std(arr)), precision),
        "min": round(float(np.min(arr)), precision),
        "max": round(float(np.max(arr)), precision),
        "p5": round(float(np.percentile(arr, 5)), precision),
        "p25": round(float(np.percentile(arr, 25)), precision),
        "p75": round(float(np.percentile(arr, 75)), precision),
        "p95": round(float(np.percentile(arr, 95)), precision),
        "unit": "$/cm2" if area_cost else "$/lb",
        "metric": "electrode_assembly_cost" if area_cost else "selling_price_less_recovery" if req.include_spent_value else "selling_price",
        "baseline": round(baseline_value, precision),
        **({} if area_cost else {
            "baseline_price_per_lb": round(baseline_value, 4),
            "baseline_price_per_kg": round(baseline_value * LB_PER_KG, 4),
        }),
        "composition": str(baseline["input_summary"]["composition"]),
        "catalyst_domain": req.catalyst_domain,
        "application_family": context["application_family"],
        "uncertainties_applied": {key: value for key, value in uncertainties.items()
                                  if not area_cost or key in {"active_component_price", "electrode_adjunct_price"}},
        **({"fixed_recipe_assumptions": "Precursor content, purity, retention yield, production rate and "
            "consumable quantities/prices are fixed; precursor purchase prices follow their component role."}
           if req.consumables or any(c.get("recipe_consumption") for c in context["resolved_components"]) else {}),
    }
