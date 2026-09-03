"""Step Method for catalyst manufacturing cost estimation.

Implements CatCost Chapter 6 methodology (Baddour et al. 2018).
Estimates catalyst selling price based on processing steps, production scale,
and materials cost.
"""

from __future__ import annotations

from backend.core.constants import (
    CLEANING_TIME,
    DEFAULT_GA_OVERHEAD_PCT,
    DEFAULT_SARD_PCT,
    HOURS_PER_DAY,
    LB_PER_TON,
    MARGIN_COEFFICIENT,
    MARGIN_EXPONENT,
    PRODUCTION_RATES,
    SCALE_THRESHOLDS,
    STEP_COSTS,
)


def determine_scale(order_size_tons: float) -> str:
    """Determine production scale from order size.

    Args:
        order_size_tons: Order size in short tons.

    Returns:
        Scale string: "small", "medium", or "large".
    """
    if order_size_tons < SCALE_THRESHOLDS["small"][0]:
        return "small"
    for scale, (lo, hi) in SCALE_THRESHOLDS.items():
        if lo <= order_size_tons < hi:
            return scale
    return "large"


def calculate_campaign_length(
    order_size_tons: float,
    scale: str,
    production_rate_ton_per_day: float | None = None,
) -> float:
    """Calculate campaign length including synthesis and cleaning time.

    Args:
        order_size_tons: Order size in short tons.
        scale: Production scale ("small", "medium", "large").
        production_rate_ton_per_day: Effective rate overriding the nominal
            scale rate. CatCost Table 6.2 footnote b uses this for zeolite
            campaigns, where ramp-up/down cuts the 150 t/d nominal to 67 t/d.

    Returns:
        Total campaign length in days.
    """
    production_rate = production_rate_ton_per_day or PRODUCTION_RATES[scale]
    synthesis_days = order_size_tons / production_rate
    cleaning_days = CLEANING_TIME[scale]
    return synthesis_days + cleaning_days


def selling_margin_pct(order_size_tons: float) -> float:
    """Calculate selling margin as fraction of selling price (Figure 6.3).

    Uses the correlation: margin% = 39.192 * Q^(-0.23360)

    Args:
        order_size_tons: Order size in short tons.

    Returns:
        Selling margin as a decimal fraction (e.g. 0.25 for 25%).
    """
    return MARGIN_COEFFICIENT * (order_size_tons**MARGIN_EXPONENT) / 100.0


def calculate_step_method(
    materials_cost_per_lb: float,
    steps: list[str],
    order_size_tons: float,
    ga_overhead_pct: float = DEFAULT_GA_OVERHEAD_PCT,
    sard_pct: float = DEFAULT_SARD_PCT,
    chemppi_escalation: float = 1.0,
    production_rate_ton_per_day: float | None = None,
) -> dict[str, float | str]:
    """Calculate catalyst selling price using the Step Method.

    Args:
        materials_cost_per_lb: Total raw materials cost in $/lb catalyst.
        steps: List of processing step names (must exist in STEP_COSTS).
        order_size_tons: Customer order size in short tons.
        ga_overhead_pct: General & Administrative overhead fraction.
        sard_pct: Sales, Admin, R&D fraction.
        chemppi_escalation: ChemPPI escalation factor from mid-2017 basis.
        production_rate_ton_per_day: Optional effective production rate; see
            ``calculate_campaign_length``.

    Returns:
        Dict with full cost breakdown.

    Raises:
        ValueError: If a step is unavailable at the determined scale.
    """
    scale = determine_scale(order_size_tons)
    campaign_days = calculate_campaign_length(order_size_tons, scale, production_rate_ton_per_day)

    # Sum hourly costs for all steps
    hourly_total = 0.0
    step_details: list[dict[str, str | float]] = []
    for step in steps:
        if step not in STEP_COSTS:
            raise ValueError(f"Unknown step: '{step}'. Valid steps: {list(STEP_COSTS.keys())}")
        cost = STEP_COSTS[step][scale]
        if cost is None:
            raise ValueError(
                f"Step '{step}' is not available at '{scale}' scale. "
                f"Try a different scale or substitute step."
            )
        hourly_total += cost
        step_details.append({"step": step, "hourly_cost": cost})

    # Apply ChemPPI escalation (mid-2017 basis)
    hourly_total *= chemppi_escalation

    # Calculate processing cost
    daily_cost = hourly_total * HOURS_PER_DAY
    campaign_cost = daily_cost * campaign_days
    total_production_lb = order_size_tons * LB_PER_TON
    processing_cost_per_lb = campaign_cost / total_production_lb

    # Build up selling price
    subtotal = materials_cost_per_lb + processing_cost_per_lb
    ga = subtotal * ga_overhead_pct
    sard = (subtotal + ga) * sard_pct
    pre_margin = subtotal + ga + sard

    margin_frac = selling_margin_pct(order_size_tons)
    margin = pre_margin * margin_frac / (1 - margin_frac)

    estimated_price = pre_margin + margin

    return {
        "scale": scale,
        "order_size_tons": order_size_tons,
        "production_rate_ton_per_day": production_rate_ton_per_day or PRODUCTION_RATES[scale],
        "campaign_days": round(campaign_days, 2),
        "step_cost_per_hr": round(hourly_total, 2),
        "chemppi_escalation": chemppi_escalation,
        "campaign_cost": round(campaign_cost, 2),
        "total_production_lb": total_production_lb,
        "materials_cost_per_lb": round(materials_cost_per_lb, 4),
        "processing_cost_per_lb": round(processing_cost_per_lb, 4),
        "subtotal_per_lb": round(subtotal, 4),
        "ga_per_lb": round(ga, 4),
        "sard_per_lb": round(sard, 4),
        "pre_margin_per_lb": round(pre_margin, 4),
        "margin_pct": round(margin_frac * 100, 2),
        "margin_per_lb": round(margin, 4),
        "estimated_price_per_lb": round(estimated_price, 4),
        "estimated_price_per_kg": round(estimated_price * LB_PER_TON / 907.185, 4),
        "step_details": step_details,
    }
