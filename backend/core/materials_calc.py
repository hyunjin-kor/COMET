"""Materials calculation module: stoichiometry, scaling, and pricing.

Implements equations 4.1-4.5 from CatCost methodology (Baddour et al. 2018).
"""

from __future__ import annotations

import numpy as np


def calculate_active_phase_mass(
    m_lr: float,
    mw_lr: float,
    mol_ratio: float,
    mw_ap: float,
    yield_pct: float,
) -> float:
    """Calculate active-phase mass from limiting reagent (eq 4.1).

    Args:
        m_lr: Mass of limiting reagent (any consistent unit).
        mw_lr: Molecular weight of limiting reagent (g/mol).
        mol_ratio: Molar ratio of active phase to limiting reagent.
        mw_ap: Molecular weight of active phase (g/mol).
        yield_pct: Reaction yield as a percentage (0-100).

    Returns:
        Mass of active phase in the same unit as *m_lr*.
    """
    return (m_lr / mw_lr) * mol_ratio * mw_ap * (yield_pct / 100.0)


def calculate_support_mass(m_ap: float, wt_pct: float) -> float:
    """Calculate support mass given active-phase mass and weight percent (eq 4.3).

    Args:
        m_ap: Mass of active phase.
        wt_pct: Weight percent of active phase on total catalyst (0-100).

    Returns:
        Mass of support material.
    """
    if wt_pct <= 0 or wt_pct >= 100:
        raise ValueError(f"wt_pct must be between 0 and 100 exclusive, got {wt_pct}")
    return (m_ap / (wt_pct / 100.0)) - m_ap


def calculate_catalyst_mass(m_ap: float, m_sup: float) -> float:
    """Calculate total catalyst mass (eq 4.2).

    Args:
        m_ap: Mass of active phase.
        m_sup: Mass of support.

    Returns:
        Total catalyst mass.
    """
    return m_ap + m_sup


def calculate_scaling_factor(m_cat_plant: float, m_cat_lab: float) -> float:
    """Calculate lab-to-plant scaling factor (eq 4.4).

    Args:
        m_cat_plant: Plant-scale catalyst mass.
        m_cat_lab: Lab-scale catalyst mass.

    Returns:
        Scaling factor k_SF.
    """
    if m_cat_lab <= 0:
        raise ValueError("m_cat_lab must be positive")
    return m_cat_plant / m_cat_lab


def extrapolate_bulk_price(
    lab_prices: list[tuple[float, float]],
    bulk_quantity: float,
) -> float:
    """Extrapolate bulk price using log-log regression (eq 4.5).

    Fits p(Q) = b * Q^gamma where p is the unit price ($/unit_mass)
    and Q is quantity.

    Args:
        lab_prices: List of (quantity, total_price) tuples from supplier quotes.
        bulk_quantity: Target bulk quantity for price estimation.

    Returns:
        Estimated unit price at the bulk quantity.
    """
    if len(lab_prices) < 2:
        raise ValueError("At least 2 price points are required for regression")

    quantities = np.array([q for q, _ in lab_prices], dtype=float)
    unit_prices = np.array([p / q for q, p in lab_prices], dtype=float)

    log_q = np.log10(quantities)
    log_p = np.log10(unit_prices)

    gamma, log_b = np.polyfit(log_q, log_p, 1)
    b = 10**log_b

    return float(b * bulk_quantity**gamma)


def precursor_price_from_metal(
    metal_spot_price: float,
    metal_fraction: float,
    conversion_markup: float = 1.05,
) -> float:
    """Estimate precursor price from metal spot price.

    Based on CatCost User Guide Section 4.3:
    precursor_price = metal_spot / metal_fraction * markup

    Args:
        metal_spot_price: Current spot price of pure metal ($/unit_mass).
        metal_fraction: Mass fraction of metal in the precursor compound.
        conversion_markup: Additional processing/conversion cost factor.

    Returns:
        Estimated precursor price ($/unit_mass of precursor).
    """
    if metal_fraction <= 0 or metal_fraction > 1:
        raise ValueError(f"metal_fraction must be in (0, 1], got {metal_fraction}")
    return metal_spot_price / metal_fraction * conversion_markup


def calculate_materials_cost(
    metal_price_per_lb: float,
    metal_loading_wt_pct: float,
    support_price_per_lb: float,
    precursor_metal_fraction: float = 1.0,
    precursor_markup: float = 1.0,
    solvent_cost_per_lb_cat: float = 0.0,
) -> dict[str, float]:
    """Calculate total raw materials cost per lb of finished catalyst.

    Args:
        metal_price_per_lb: Metal spot price in $/lb.
        metal_loading_wt_pct: Metal loading as weight percent (0-100).
        support_price_per_lb: Support price in $/lb.
        precursor_metal_fraction: Mass fraction of metal in precursor.
        precursor_markup: Markup factor for precursor over pure metal.
        solvent_cost_per_lb_cat: Solvent/additive cost per lb catalyst.

    Returns:
        Dict with cost breakdown per lb of catalyst.
    """
    loading_frac = metal_loading_wt_pct / 100.0
    support_frac = 1.0 - loading_frac

    # Precursor cost per lb of catalyst
    # When using a precursor compound:
    #   - Need loading_frac lb of metal per lb catalyst
    #   - Need loading_frac/metal_fraction lb of precursor per lb catalyst
    #   - Precursor price ≈ metal_spot × metal_fraction × markup (per lb precursor)
    #   - Total = loading_frac × metal_spot × markup (metal_fraction cancels)
    if precursor_metal_fraction < 1.0:
        precursor_cost_per_lb_cat = loading_frac * metal_price_per_lb * precursor_markup
    else:
        precursor_cost_per_lb_cat = metal_price_per_lb * loading_frac

    support_cost_per_lb_cat = support_price_per_lb * support_frac

    total = precursor_cost_per_lb_cat + support_cost_per_lb_cat + solvent_cost_per_lb_cat

    return {
        "metal_precursor_cost_per_lb": precursor_cost_per_lb_cat,
        "support_cost_per_lb": support_cost_per_lb_cat,
        "solvent_cost_per_lb": solvent_cost_per_lb_cat,
        "total_materials_cost_per_lb": total,
    }
