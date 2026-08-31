"""Spent catalyst recovery value calculation.

Implements CatCost Chapter 9 methodology (Baddour et al. 2018).
Estimates the reclaimed value of spent catalyst after metal recovery.
"""

from __future__ import annotations

import json
from functools import lru_cache

from backend.core.constants import (
    DEFAULT_INCOMING_PER_FT3,
    DEFAULT_THERMOX_PER_LB,
    LB_PER_KG,
    LB_PER_METRIC_TON,
    LB_PER_TON,
    LOSSES_REFINING,
    LOSSES_USE,
    REFINING_CHARGES,
    SUPPORT_RECOVERY_COSTS,
    TROY_OZ_PER_LB,
)
from backend.core.price_escalation import get_escalation_factor, latest_index_year
from backend.paths import data_dir

_ANCHOR_SYMBOLS = {
    "Aluminum": "Al", "Cobalt": "Co", "Copper": "Cu", "Gold": "Au", "Iridium": "Ir",
    "Iron": "Fe", "Molybdenum": "Mo", "Nickel": "Ni", "Palladium": "Pd",
    "Platinum": "Pt", "Rhodium": "Rh", "Ruthenium": "Ru", "Silver": "Ag", "Tungsten": "W",
}
_SPOT_UNIT_TO_LB = {
    "lb": 1.0,
    "kg": 1.0 / LB_PER_KG,
    "oz t": TROY_OZ_PER_LB,
    "ton": 1.0 / LB_PER_TON,
    "tonne": 1.0 / LB_PER_METRIC_TON,
}
# Metals whose recoverable form is scrap rather than refined metal: their
# salvage anchor is a different commodity from the purchase price. Refined
# metals (precious or base) keep the caller's market price as salvage basis.
_SCRAP_SALVAGE = frozenset({"Fe"})


@lru_cache(maxsize=1)
def _metal_anchors() -> dict[str, dict]:
    """CatCost Chapter 9 per-metal salvage anchors, keyed by element symbol."""
    with open(data_dir() / "spent_catalyst.json", encoding="utf-8") as f:
        metals = json.load(f)["metals"]
    anchors: dict[str, dict] = {}
    for name, row in metals.items():
        symbol = _ANCHOR_SYMBOLS.get(name)
        unit_factor = _SPOT_UNIT_TO_LB.get(row.get("spot_unit"))
        if not symbol or not unit_factor or not row.get("spot_price"):
            continue
        anchors[symbol] = {
            "spot_per_lb": float(row["spot_price"]) * unit_factor,
            "spot_year": int(row.get("spot_year") or 2018),
            "is_precious": bool(row.get("is_precious_metal")),
            "refining_charge_per_troy_oz": row.get("refining_charge_per_troy_oz"),
        }
    return anchors


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
        metal_spot_price: Current metal spot price ($/lb). Used as the salvage
            basis for metals recovered as refined metal; scrap-recovered metals
            (Fe) are priced from the CatCost scrap anchor instead, so a
            precursor-based input price cannot inflate the credit.
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

    anchor = _metal_anchors().get(metal_symbol)
    if metal_symbol in _SCRAP_SALVAGE and anchor:
        # These metals are recovered as scrap, not refined metal, so salvage
        # trades at the scrap anchor — never at whatever the catalyst input
        # was bought at (the Fe precursor basis sits ~40x above scrap iron).
        metal_spot_price = anchor["spot_per_lb"] * get_escalation_factor(
            anchor["spot_year"], latest_index_year("chemppi"), "chemppi"
        )

    # Salvage value of metal per lb catalyst
    v_metal = (1 - l_metal_use) * (1 - l_metal_ref) * metal_loading * metal_spot_price

    # Recovery cost per lb catalyst
    l_solids_use = l_support_use * (1 - metal_loading) + l_metal_use * metal_loading

    # Toll-refining charge is quoted per troy oz of recovered metal and only
    # exists for precious metals (non-precious anchors carry None).
    charge_per_troy_oz = REFINING_CHARGES.get(metal_symbol)
    if charge_per_troy_oz is None and anchor:
        charge_per_troy_oz = anchor["refining_charge_per_troy_oz"]
    f_refining = (charge_per_troy_oz or 0.0) * TROY_OZ_PER_LB * metal_loading

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
