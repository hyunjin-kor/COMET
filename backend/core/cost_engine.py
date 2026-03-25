"""Integrated catalyst cost estimation engine."""

from __future__ import annotations

from backend.core.constants import LB_PER_KG, TROY_OZ_PER_LB
from backend.core.materials_calc import calculate_materials_cost_multi
from backend.core.price_escalation import get_escalation_factor
from backend.core.spent_catalyst import calculate_metal_recovery_value
from backend.core.step_method import calculate_step_method


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
    order_size_tons: float = 10.0,
    ga_overhead_pct: float = 0.05,
    sard_pct: float = 0.05,
    basis_year: int = 2017,
    target_year: int = 2024,
    include_spent_value: bool = False,
    reactor_type: str = "fixed",
    catalyst_bulk_density: float = 50.0,
) -> dict:
    """Run a full catalyst cost estimation.

    Supports both the current multi-component payload and the legacy
    single-metal flat payload used by older tests and API clients.
    """

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

    active_metals = [component for component in components if component["role"] == "active_metal"]
    supports = [component for component in components if component["role"] == "support"]
    if not active_metals:
        raise ValueError("At least one active_metal component is required")
    if not supports:
        raise ValueError("At least one support component is required")

    materials = calculate_materials_cost_multi(components)

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
    net_cost_per_lb = step_result["estimated_price_per_lb"]
    total_wt = sum(float(component["wt_pct"]) for component in components)

    if include_spent_value:
        primary = max(active_metals, key=lambda component: float(component["wt_pct"]))
        metal_loading_frac = float(primary["wt_pct"]) / total_wt

        try:
            spent_result = calculate_metal_recovery_value(
                metal_symbol=primary["name"],
                metal_loading=metal_loading_frac,
                metal_spot_price=float(primary["price_per_lb"]),
                support=supports[0]["name"],
                reactor_type=reactor_type,
                catalyst_bulk_density=catalyst_bulk_density,
            )
            reclaimed = spent_result.get("V_reclaimed_per_lb") or spent_result.get("V_reclaimed", 0)
            net_cost_per_lb = max(0.0, step_result["estimated_price_per_lb"] - float(reclaimed))
        except Exception:
            spent_result = None

    metals_label = "+".join(
        f"{float(component['wt_pct']) / total_wt * 100:.1f}% {component['name']}"
        for component in active_metals
    )
    promoters_label = "+".join(
        component["name"] for component in components if component["role"] == "promoter"
    )
    support_label = supports[0]["name"]
    composition = f"{metals_label}/{support_label}"
    if promoters_label:
        composition = f"{metals_label}+{promoters_label}/{support_label}"

    estimated = step_result["estimated_price_per_lb"]

    return {
        "input_summary": {
            **legacy_input_summary,
            "composition": composition,
            "n_components": len(components),
            "order_size_tons": order_size_tons,
            "basis_year": basis_year,
            "target_year": target_year,
            "chemppi_escalation": round(chemppi_factor, 4),
        },
        "materials": materials,
        "step_method": step_result,
        "spent_catalyst": spent_result,
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
    order_size_tons: float = 10.0,
    precursor_markup: float = 1.0,
    ga_overhead_pct: float = 0.05,
    sard_pct: float = 0.05,
    basis_year: int = 2017,
    target_year: int = 2024,
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
        order_size_tons=order_size_tons,
        ga_overhead_pct=ga_overhead_pct,
        sard_pct=sard_pct,
        basis_year=basis_year,
        target_year=target_year,
    )
