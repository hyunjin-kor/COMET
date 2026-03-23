"""CapEx & OpEx Factors Method for catalyst manufacturing cost estimation.

Implements CatCost Chapter 7 methodology (Baddour et al. 2018).
Uses factored estimation approach based on purchased equipment cost.
"""

from __future__ import annotations

from backend.core.constants import (
    CAPEX_FACTORS_DEFAULT,
    DEFAULT_SCALING_EXPONENT,
    OPEX_FACTORS_DEFAULT,
)


def equipment_cost_scaling(
    base_price: float,
    base_size: float,
    target_size: float,
    exponent: float = DEFAULT_SCALING_EXPONENT,
) -> float:
    """Scale equipment cost using the power-law six-tenths rule (eq 7.1).

    Cost_target = Cost_base * (Size_target / Size_base) ^ exponent

    Args:
        base_price: Known equipment cost at base size.
        base_size: Base sizing parameter value.
        target_size: Target sizing parameter value.
        exponent: Scaling exponent (default 0.6).

    Returns:
        Estimated equipment cost at target size.
    """
    if base_size <= 0 or target_size <= 0:
        raise ValueError("Size parameters must be positive")
    return base_price * (target_size / base_size) ** exponent


def equipment_cost_correlation(
    s: float, a: float, b: float, n: float
) -> float:
    """Calculate equipment cost from correlation (eq 7.2).

    Cost = a + b * S^n

    Args:
        s: Sizing parameter value.
        a: Fixed cost coefficient.
        b: Variable cost coefficient.
        n: Sizing exponent.

    Returns:
        Estimated purchased equipment cost.
    """
    return a + b * s**n


def calculate_capex(
    purchased_equipment_cost: float,
    factors: dict[str, float] | None = None,
) -> dict[str, float]:
    """Calculate total capital investment using Lang factors.

    Args:
        purchased_equipment_cost: Total purchased equipment cost ($).
        factors: Override factors dict (uses defaults if None).

    Returns:
        Dict with itemized capital costs and totals.
    """
    f = factors or CAPEX_FACTORS_DEFAULT

    direct_items = [
        "purchased_equipment", "installation", "instrumentation",
        "piping", "electrical", "buildings", "yard_improvements",
        "service_facilities", "land",
    ]
    indirect_items = [
        "engineering_supervision", "construction", "legal",
        "contractors_fee", "contingency",
    ]

    result: dict[str, float] = {}
    direct_total = 0.0
    for item in direct_items:
        cost = purchased_equipment_cost * f.get(item, 0)
        result[item] = round(cost, 2)
        direct_total += cost

    indirect_total = 0.0
    for item in indirect_items:
        cost = purchased_equipment_cost * f.get(item, 0)
        result[item] = round(cost, 2)
        indirect_total += cost

    fci = direct_total + indirect_total
    working_capital = purchased_equipment_cost * f.get("working_capital", 0)

    result["direct_capital"] = round(direct_total, 2)
    result["indirect_capital"] = round(indirect_total, 2)
    result["fixed_capital_investment"] = round(fci, 2)
    result["working_capital"] = round(working_capital, 2)
    result["total_capital_investment"] = round(fci + working_capital, 2)

    return result


def calculate_opex(
    fci: float,
    direct_labor_cost: float,
    raw_materials_cost: float,
    utilities_cost: float,
    factors: dict[str, float] | None = None,
) -> dict[str, float]:
    """Calculate annual operating expenses.

    Args:
        fci: Fixed capital investment ($).
        direct_labor_cost: Annual direct labor cost ($).
        raw_materials_cost: Annual raw materials cost ($).
        utilities_cost: Annual utilities cost ($).
        factors: Override factors dict (uses defaults if None).

    Returns:
        Dict with itemized operating costs and totals.
    """
    f = factors or OPEX_FACTORS_DEFAULT

    # Direct operating costs
    supervisory = direct_labor_cost * f.get("supervisory_clerical", 0)
    laboratory = direct_labor_cost * f.get("laboratory", 0)
    maintenance = fci * f.get("maintenance_repair", 0)
    operating_supplies = maintenance * f.get("operating_supplies", 0)

    direct_operating = (
        raw_materials_cost + direct_labor_cost + supervisory + utilities_cost
        + laboratory + maintenance + operating_supplies
    )

    # Fixed operating costs
    local_taxes = fci * f.get("local_taxes", 0)
    insurance = fci * f.get("insurance", 0)
    land_cost = fci * CAPEX_FACTORS_DEFAULT.get("land", 0.06)
    rent = land_cost * f.get("rent", 0)

    lsm = direct_labor_cost + supervisory + maintenance  # Labor, supervision, maintenance
    plant_overhead = lsm * f.get("plant_overhead", 0)

    fixed_operating = local_taxes + insurance + rent + plant_overhead

    # General expenses
    administration = lsm * f.get("administration", 0)
    total_operating_before_ge = direct_operating + fixed_operating
    distribution = total_operating_before_ge * f.get("distribution_marketing", 0)
    rnd = total_operating_before_ge * f.get("rnd", 0)

    general_expenses = administration + distribution + rnd

    total_opex = direct_operating + fixed_operating + general_expenses

    return {
        "raw_materials": round(raw_materials_cost, 2),
        "direct_labor": round(direct_labor_cost, 2),
        "supervisory_clerical": round(supervisory, 2),
        "utilities": round(utilities_cost, 2),
        "laboratory": round(laboratory, 2),
        "maintenance_repair": round(maintenance, 2),
        "operating_supplies": round(operating_supplies, 2),
        "direct_operating_total": round(direct_operating, 2),
        "local_taxes": round(local_taxes, 2),
        "insurance": round(insurance, 2),
        "rent": round(rent, 2),
        "plant_overhead": round(plant_overhead, 2),
        "fixed_operating_total": round(fixed_operating, 2),
        "administration": round(administration, 2),
        "distribution_marketing": round(distribution, 2),
        "rnd": round(rnd, 2),
        "general_expenses_total": round(general_expenses, 2),
        "total_annual_opex": round(total_opex, 2),
    }
