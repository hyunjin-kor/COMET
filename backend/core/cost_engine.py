"""Integrated catalyst cost estimation engine."""

from __future__ import annotations

import logging

from backend.core.constants import LB_PER_KG, TROY_OZ_PER_LB
from backend.core.electrocatalyst import calculate_electrode_layer_cost
from backend.core.lca import compute_catalyst_lca
from backend.core.materials_calc import calculate_materials_cost_multi
from backend.core.price_escalation import get_escalation_factor, latest_index_year
from backend.core.spent_catalyst import calculate_metal_recovery_value
from backend.core.step_method import calculate_step_method

logger = logging.getLogger(__name__)


def estimate_catalyst_cost(
    components: list[dict] | None = None,
    metal_symbol: str | None = None,
    metal_price: float | None = None,
    metal_price_unit: str = "$/troy_oz",
    metal_loading_wt_pct: float | None = None,
    support_name: str | None = None,
    support_price_per_lb: float | None = None,
    precursor_metal_fraction: float = 1.0,
    precursor_markup: float = 1.0,
    steps: list[str] | None = None,
    catalyst_domain: str = "thermal",
    application_family: str = "general",
    order_size_tons: float = 10.0,
    ga_overhead_pct: float = 0.05,
    sard_pct: float = 0.05,
    basis_year: int = 2017,
    target_year: int | None = None,
    include_spent_value: bool = False,
    reactor_type: str = "fixed",
    catalyst_bulk_density: float = 50.0,
    electrode_input: dict | None = None,
    route_summary: dict | None = None,
    resolved_materials: list[dict] | None = None,
) -> dict:
    """Run a full catalyst cost estimation.

    Supports both the current multi-component payload and the legacy
    single-metal flat payload used by older tests and API clients.
    """

    if target_year is None:
        target_year = latest_index_year("chemppi")

    legacy_input_summary: dict[str, float | str] = {}
    if components is None:
        if None in (metal_symbol, metal_price, metal_loading_wt_pct, support_name):
            raise ValueError("Either components or legacy metal/support fields must be provided")
        if support_price_per_lb is None:
            support_price_per_lb = 0.50

        if metal_price_unit == "$/troy_oz":
            metal_price_per_lb = metal_price * TROY_OZ_PER_LB
        elif metal_price_unit == "$/lb":
            metal_price_per_lb = metal_price
        elif metal_price_unit == "$/kg":
            metal_price_per_lb = metal_price / LB_PER_KG
        else:
            raise ValueError(f"Unknown metal_price_unit: {metal_price_unit}")

        support_wt = 100.0 - metal_loading_wt_pct
        if support_wt <= 0:
            raise ValueError("metal_loading_wt_pct must be less than 100")

        components = [
            {
                "role": "active_metal",
                "name": metal_symbol,
                "wt_pct": metal_loading_wt_pct,
                "price_per_lb": metal_price_per_lb,
                "precursor_markup": precursor_markup,
            },
            {
                "role": "support",
                "name": support_name,
                "wt_pct": support_wt,
                "price_per_lb": support_price_per_lb,
                "precursor_markup": 1.0,
            },
        ]
        legacy_input_summary = {
            "metal_symbol": metal_symbol,
            "metal_price": metal_price,
            "metal_price_unit": metal_price_unit,
            "metal_price_per_lb": round(metal_price_per_lb, 4),
            "metal_loading_wt_pct": metal_loading_wt_pct,
            "support_name": support_name,
            "support_price_per_lb": support_price_per_lb,
            "precursor_metal_fraction": precursor_metal_fraction,
            "precursor_markup": precursor_markup,
        }

    active_metals = [
        component
        for component in components
        if component["role"] in {"active_metal", "active_catalyst"}
    ]
    supports = [component for component in components if component["role"] == "support"]
    if not active_metals:
        raise ValueError("At least one active_metal or active_catalyst component is required")
    if catalyst_domain != "electrocatalyst" and not supports:
        raise ValueError("At least one support component is required")

    materials = calculate_materials_cost_multi(components)
    warnings: list[str] = []

    if catalyst_domain == "electrocatalyst" and electrode_input is None:
        warnings.append(
            "Electrocatalyst mode is separated from thermocatalyst records, but no electrode-layer "
            "adjunct inputs were supplied for ionomer, membrane, or substrate costs."
        )

    try:
        chemppi_factor = get_escalation_factor(basis_year, target_year, "chemppi")
    except KeyError:
        chemppi_factor = 1.0

    if steps is None:
        steps = ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"]

    step_result = calculate_step_method(
        materials_cost_per_lb=materials["total_materials_cost_per_lb"],
        steps=steps,
        order_size_tons=order_size_tons,
        ga_overhead_pct=ga_overhead_pct,
        sard_pct=sard_pct,
        chemppi_escalation=chemppi_factor,
    )

    spent_result = None
    electrode_model = None
    net_cost_per_lb = step_result["estimated_price_per_lb"]
    total_wt = sum(float(component["wt_pct"]) for component in components)

    if include_spent_value and supports and any(component["role"] == "active_metal" for component in active_metals):
        primary = max(active_metals, key=lambda component: float(component["wt_pct"]))
        primary_support = max(supports, key=lambda component: float(component["wt_pct"]))
        metal_loading_frac = float(primary["wt_pct"]) / total_wt

        try:
            spent_result = calculate_metal_recovery_value(
                metal_symbol=primary["name"],
                metal_loading=metal_loading_frac,
                metal_spot_price=float(primary["price_per_lb"]),
                support=primary_support["name"],
                reactor_type=reactor_type,
                catalyst_bulk_density=catalyst_bulk_density,
            )
            reclaimed = spent_result.get("V_reclaimed_per_lb") or spent_result.get("V_reclaimed", 0)
            net_cost_per_lb = max(0.0, step_result["estimated_price_per_lb"] - float(reclaimed))
        except (KeyError, ValueError, TypeError, ZeroDivisionError) as exc:
            logger.warning(
                "Spent-catalyst recovery skipped (%s/%s): %s",
                primary["name"],
                primary_support["name"],
                exc,
            )
            spent_result = None

    if (
        catalyst_domain == "electrocatalyst"
        and electrode_input is not None
        and electrode_input.get("catalyst_price_per_lb", 0) > 0
    ):
        primary_component = max(active_metals, key=lambda component: float(component["wt_pct"]))
        electrode_model = calculate_electrode_layer_cost(
            catalyst_price_per_lb=float(electrode_input["catalyst_price_per_lb"]),
            active_area_cm2=float(electrode_input.get("active_area_cm2", 25.0)),
            catalyst_loading_mg_cm2=float(electrode_input.get("catalyst_loading_mg_cm2", 0.5)),
            ionomer_to_catalyst_ratio=float(electrode_input.get("ionomer_to_catalyst_ratio", 0.0)),
            ionomer_price_per_ml=float(electrode_input.get("ionomer_price_per_ml", 0.0)),
            ionomer_price_per_kg_solids=float(electrode_input.get("ionomer_price_per_kg_solids", 0.0)),
            ionomer_density_g_ml=float(electrode_input.get("ionomer_density_g_ml", 0.94)),
            ionomer_solids_fraction=float(electrode_input.get("ionomer_solids_fraction", 0.05)),
            substrate_cost_per_cm2=float(electrode_input.get("substrate_cost_per_cm2", 0.0)),
            membrane_cost_per_cm2=float(electrode_input.get("membrane_cost_per_cm2", 0.0)),
            application_family=electrode_input.get("application_family", application_family),
            manufacturing_scenario=electrode_input.get("manufacturing_scenario"),
        )
        if electrode_model.get("manufacturing"):
            warnings.append(
                "MEA manufacturing cost uses the "
                f"{electrode_model['manufacturing']['label']} operating point from Hog et al. 2026 "
                f"(EUR->USD at {electrode_model['manufacturing']['eur_to_usd']}, 2025 annual average); "
                "stage yield losses are not yet applied."
            )
        else:
            warnings.append(
                "Electrocatalyst results now include area-based catalyst, ionomer, membrane, and substrate "
                "costs, but line throughput and stack assembly are not costed. Select a manufacturing "
                "scenario to add an equipment/labor/facility estimate per cm2."
            )
        if primary_component["role"] == "active_catalyst":
            composition = primary_component["name"]
        else:
            composition = primary_component["name"]
    else:
        composition = None

    metals_label = "+".join(
        f"{float(component['wt_pct']) / total_wt * 100:.1f}% {component['name']}"
        for component in active_metals
    )
    promoters_label = "+".join(
        component["name"] for component in components if component["role"] == "promoter"
    )
    support_label = "+".join(component["name"] for component in supports)
    if composition is None:
        if support_label:
            composition = f"{metals_label}/{support_label}"
            if promoters_label:
                composition = f"{metals_label}+{promoters_label}/{support_label}"
        else:
            composition = metals_label if not promoters_label else f"{metals_label}+{promoters_label}"

    estimated = step_result["estimated_price_per_lb"]

    lca_result = compute_catalyst_lca(components)

    return {
        "input_summary": {
            **legacy_input_summary,
            "composition": composition,
            "catalyst_domain": catalyst_domain,
            "application_family": application_family,
            "n_components": len(components),
            "order_size_tons": order_size_tons,
            "basis_year": basis_year,
            "target_year": target_year,
            "chemppi_escalation": round(chemppi_factor, 4),
        },
        "materials": materials,
        "step_method": step_result,
        "spent_catalyst": spent_result,
        "electrode_model": electrode_model,
        "route_summary": route_summary,
        "resolved_materials": resolved_materials or [],
        "warnings": warnings,
        "lca": lca_result,
        "summary": {
            "estimated_price_per_lb": round(estimated, 4),
            "estimated_price_per_kg": round(estimated * LB_PER_KG, 4),
            "net_cost_per_lb": round(net_cost_per_lb, 4),
            "net_cost_per_kg": round(net_cost_per_lb * LB_PER_KG, 4),
            "materials_pct": round(
                materials["total_materials_cost_per_lb"] / estimated * 100, 1
            ) if estimated > 0 else 0.0,
            "processing_pct": round(
                step_result["processing_cost_per_lb"] / estimated * 100, 1
            ) if estimated > 0 else 0.0,
            "gwp_kg_co2eq_per_kg_catalyst": lca_result.get("gwp_kg_co2eq_per_kg_catalyst"),
            "ced_mj_per_kg_catalyst": lca_result.get("ced_mj_per_kg_catalyst"),
            "lca_coverage_pct": lca_result.get("coverage_pct"),
        },
    }


def estimate_catalyst_cost_simple(
    metal_symbol: str,
    metal_price: float,
    metal_price_unit: str,
    metal_loading_wt_pct: float,
    support_name: str,
    support_price_per_lb: float,
    steps: list[str] | None = None,
    catalyst_domain: str = "thermal",
    application_family: str = "general",
    order_size_tons: float = 10.0,
    precursor_markup: float = 1.0,
    ga_overhead_pct: float = 0.05,
    sard_pct: float = 0.05,
    basis_year: int = 2017,
    target_year: int | None = None,
) -> dict:
    """Legacy single-metal wrapper used by the quick calculator."""

    return estimate_catalyst_cost(
        metal_symbol=metal_symbol,
        metal_price=metal_price,
        metal_price_unit=metal_price_unit,
        metal_loading_wt_pct=metal_loading_wt_pct,
        support_name=support_name,
        support_price_per_lb=support_price_per_lb,
        precursor_markup=precursor_markup,
        steps=steps,
        catalyst_domain=catalyst_domain,
        application_family=application_family,
        order_size_tons=order_size_tons,
        ga_overhead_pct=ga_overhead_pct,
        sard_pct=sard_pct,
        basis_year=basis_year,
        target_year=target_year,
    )
