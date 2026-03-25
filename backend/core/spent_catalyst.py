"""Spent catalyst recovery value calculation.

Implements CatCost Chapter 9 methodology (Baddour et al. 2018).
Estimates the reclaimed value of spent catalyst after metal recovery.
"""

from __future__ import annotations

from backend.core.constants import (
    DEFAULT_INCOMING_PER_FT3,
    DEFAULT_THERMOX_PER_LB,
    LOSSES_REFINING,
    LOSSES_USE,
    REFINING_CHARGES,
    SUPPORT_RECOVERY_COSTS,
)


def calculate_metal_recovery_value(
    metal_symbol: str,
    metal_loading: float,
    metal_spot_price: float,
    support: str,
    reactor_type: str,
    catalyst_bulk_density: float,
    thermox_per_lb: float = DEFAULT_THERMOX_PER_LB,
    incoming_per_ft3: float = DEFAULT_INCOMING_PER_FT3,
) -> dict[str, float]:
    """Calculate the net reclaimed value of spent catalyst.

    Args:
        metal_symbol: Metal element symbol (e.g. "Pt", "Pd").
        metal_loading: Metal loading as lb metal / lb catalyst.
        metal_spot_price: Current metal spot price ($/lb).
        support: Support material name (e.g. "Al2O3", "Carbon").
        reactor_type: Reactor type ("fixed" or "slurry").
        catalyst_bulk_density: Catalyst bulk density (lb/ft3).
        thermox_per_lb: Thermal oxidation processing fee ($/lb).
        incoming_per_ft3: Incoming inspection fee ($/ft3).

    Returns:
        Dict with V_metal (salvage value), C_recovery (recovery cost),
        and V_reclaimed (net reclaimed value), all per lb catalyst.
    """
    # Get loss fractions
    use_losses = LOSSES_USE.get(support, {}).get(reactor_type, {})
    l_metal_use = use_losses.get("metal", 0.05)
    l_support_use = use_losses.get("support", 0.02)
    l_metal_ref = LOSSES_REFINING.get(metal_symbol, {}).get("avg", 0.10)
    support_costs = SUPPORT_RECOVERY_COSTS.get(support, {})
    if thermox_per_lb == DEFAULT_THERMOX_PER_LB:
        thermox_per_lb = support_costs.get("thermox_per_lb", thermox_per_lb)
    if incoming_per_ft3 == DEFAULT_INCOMING_PER_FT3:
        incoming_per_ft3 = support_costs.get("incoming_fee_per_ft3", incoming_per_ft3)

    # Salvage value of metal per lb catalyst
    v_metal = (1 - l_metal_use) * (1 - l_metal_ref) * metal_loading * metal_spot_price

    # Recovery cost per lb catalyst
    l_solids_use = l_support_use * (1 - metal_loading) + l_metal_use * metal_loading

    # Refining charge per lb metal content
    f_refining = REFINING_CHARGES.get(metal_symbol, 15.0) * metal_loading

    c_recovery = (
        (1 - l_solids_use) * (thermox_per_lb + incoming_per_ft3 / catalyst_bulk_density)
        + f_refining * (1 - l_metal_use) * (1 - l_metal_ref)
    )

    v_reclaimed = v_metal - c_recovery

    return {
        "metal_symbol": metal_symbol,
        "metal_loading_lb_per_lb": metal_loading,
        "loss_use_pct": round(l_metal_use * 100, 2),
        "loss_refining_pct": round(l_metal_ref * 100, 2),
        "V_metal_per_lb": round(v_metal, 4),
        "C_recovery_per_lb": round(c_recovery, 4),
        "V_reclaimed_per_lb": round(v_reclaimed, 4),
    }
