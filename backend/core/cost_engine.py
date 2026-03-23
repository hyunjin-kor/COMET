"""Integrated cost estimation engine.

Combines materials calculation, Step Method, CapEx/OpEx, and spent catalyst
recovery into a unified estimation pipeline.
"""

from __future__ import annotations

from backend.core.constants import LB_PER_KG, TROY_OZ_PER_LB
from backend.core.materials_calc import calculate_materials_cost
from backend.core.price_escalation import get_escalation_factor
from backend.core.spent_catalyst import calculate_metal_recovery_value
from backend.core.step_method import calculate_step_method


def estimate_catalyst_cost(
    # Metal / composition
    metal_symbol: str,
    metal_price: float,
    metal_price_unit: str,
    metal_loading_wt_pct: float,
    # Support
    support_name: str,
    support_price_per_lb: float,
    # Precursor info
    precursor_metal_fraction: float = 1.0,
    precursor_markup: float = 1.0,
    # Process
    steps: list[str] | None = None,
    order_size_tons: float = 10.0,
    # Cost adjustment
    solvent_cost_per_lb_cat: float = 0.0,
    ga_overhead_pct: float = 0.05,
    sard_pct: float = 0.05,
    # Price escalation
    basis_year: int = 2017,
    target_year: int = 2024,
    # Spent catalyst recovery
    include_spent_value: bool = False,
    reactor_type: str = "fixed",
    catalyst_bulk_density: float = 50.0,
) -> dict:
    """Run a full catalyst cost estimation.

    Args:
        metal_symbol: Element symbol (e.g. "Pt", "Ni").
        metal_price: Metal spot price.
        metal_price_unit: Price unit ("$/troy_oz" or "$/lb").
        metal_loading_wt_pct: Active metal loading weight percent.
        support_name: Support material name.
        support_price_per_lb: Support cost in $/lb.
        precursor_metal_fraction: Metal mass fraction in precursor compound.
        precursor_markup: Markup over pure metal for precursor conversion.
        steps: Processing step names for Step Method.
        order_size_tons: Production order size in short tons.
        solvent_cost_per_lb_cat: Additional solvent/additive cost per lb catalyst.
        ga_overhead_pct: G&A overhead fraction.
        sard_pct: Sales/Admin/R&D fraction.
        basis_year: Basis year for step costs (default 2017).
        target_year: Target year for escalation.
        include_spent_value: Whether to calculate spent catalyst recovery.
        reactor_type: Reactor type for spent catalyst calc ("fixed"/"slurry").
        catalyst_bulk_density: Bulk density in lb/ft3.

    Returns:
        Comprehensive cost estimation dict.
    """
    # Convert metal price to $/lb
    if metal_price_unit == "$/troy_oz":
        metal_price_per_lb = metal_price * TROY_OZ_PER_LB
    elif metal_price_unit == "$/lb":
        metal_price_per_lb = metal_price
    elif metal_price_unit == "$/kg":
        metal_price_per_lb = metal_price / LB_PER_KG
    else:
        raise ValueError(f"Unknown metal_price_unit: {metal_price_unit}")

    # 1. Materials cost
    materials = calculate_materials_cost(
        metal_price_per_lb=metal_price_per_lb,
        metal_loading_wt_pct=metal_loading_wt_pct,
        support_price_per_lb=support_price_per_lb,
        precursor_metal_fraction=precursor_metal_fraction,
        precursor_markup=precursor_markup,
        solvent_cost_per_lb_cat=solvent_cost_per_lb_cat,
    )

    # 2. ChemPPI escalation factor
    try:
        chemppi_factor = get_escalation_factor(basis_year, target_year, "chemppi")
    except KeyError:
        chemppi_factor = 1.0

    # 3. Step Method calculation
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

    # 4. Spent catalyst recovery (optional)
    spent_result = None
    net_cost_per_lb = step_result["estimated_price_per_lb"]
    if include_spent_value:
        metal_loading_frac = metal_loading_wt_pct / 100.0
        spent_result = calculate_metal_recovery_value(
            metal_symbol=metal_symbol,
            metal_loading=metal_loading_frac,
            metal_spot_price=metal_price_per_lb,
            support=support_name,
            reactor_type=reactor_type,
            catalyst_bulk_density=catalyst_bulk_density,
        )
        net_cost_per_lb = step_result["estimated_price_per_lb"] - spent_result["V_reclaimed_per_lb"]

    return {
        "input_summary": {
            "metal": metal_symbol,
            "metal_price": metal_price,
            "metal_price_unit": metal_price_unit,
            "metal_price_per_lb": round(metal_price_per_lb, 2),
            "metal_loading_wt_pct": metal_loading_wt_pct,
            "support": support_name,
            "support_price_per_lb": support_price_per_lb,
            "order_size_tons": order_size_tons,
            "basis_year": basis_year,
            "target_year": target_year,
        },
        "materials": materials,
        "step_method": step_result,
        "spent_catalyst": spent_result,
        "summary": {
            "estimated_price_per_lb": round(step_result["estimated_price_per_lb"], 4),
            "estimated_price_per_kg": round(step_result["estimated_price_per_lb"] * LB_PER_KG, 4),
            "net_cost_per_lb": round(net_cost_per_lb, 4),
            "net_cost_per_kg": round(net_cost_per_lb * LB_PER_KG, 4),
            "materials_pct": round(
                materials["total_materials_cost_per_lb"]
                / step_result["estimated_price_per_lb"]
                * 100,
                1,
            ),
            "processing_pct": round(
                step_result["processing_cost_per_lb"]
                / step_result["estimated_price_per_lb"]
                * 100,
                1,
            ),
        },
    }
