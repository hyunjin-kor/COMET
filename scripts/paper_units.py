"""Exact mass-unit conversions for publication displays, preserving frozen inputs."""

KG_PER_LB = 0.45359237
KG_PER_TROY_OZ = 0.0311034768
KG_PER_SHORT_TON = 2000 * KG_PER_LB
PER_LB_TO_PER_KG = 1 / KG_PER_LB


def publication_cost(value, unit):
    """Convert a mass-based quote; retain an electrode's area-based cost."""
    factors = {"$/lb": PER_LB_TO_PER_KG, "$/troy_oz": 1 / KG_PER_TROY_OZ,
               "$/kg": 1, "$/cm2": 1}
    return value * factors[unit]


def publication_unit(unit):
    return {"$/lb": "$/kg", "$/troy_oz": "$/kg", "$/kg": "$/kg", "$/cm2": "$/cm2"}[unit]
