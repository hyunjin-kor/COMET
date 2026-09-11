"""Explicit purchased-input mass balance, without inferred precursor prices."""

from backend.core.constants import LB_PER_KG
from backend.core.materials_calc import calculate_materials_cost_multi
from backend.schemas.recipe_input import ConsumableInput, PrecursorConsumption


def calculate_recipe_materials(components: list[dict], consumables: list[dict] | None = None) -> dict:
    """Replace a component's material contribution only when a recipe is supplied.

    Retained fraction is the represented finished component per unit of pure
    precursor, purity is the pure-precursor fraction in the purchased input,
    and yield is the fraction of that component retained in the product.
    Consumables are net purchased kg/kg finished catalyst (including washing).
    """
    result = calculate_materials_cost_multi(components)
    if not consumables and not any(c.get("recipe_consumption") for c in components):
        return result

    total_wt = sum(float(c["wt_pct"]) for c in components)
    total = 0.0
    for component, item in zip(components, result["components"], strict=True):
        recipe = component.get("recipe_consumption")
        if recipe:
            if float(component.get("precursor_markup", 1.0)) != 1.0:
                raise ValueError("Recipe consumption cannot also apply a precursor markup")
            r = PrecursorConsumption.model_validate(recipe)
            mass = (float(component["wt_pct"]) / total_wt
                    / r.retained_component_fraction / r.purity_fraction / r.yield_fraction)
            cost = mass * r.price_per_kg / LB_PER_KG
            item["recipe_consumption"] = {
                **r.model_dump(),
                "purchased_kg_per_kg_catalyst": round(mass, 8),
                "cost_per_kg_catalyst": round(cost * LB_PER_KG, 6),
            }
        else:
            cost = (float(component["wt_pct"]) / total_wt * float(component["price_per_lb"])
                    * float(component.get("precursor_markup", 1.0)))
        item["cost_per_lb_cat"] = round(cost, 6)
        total += cost

    additions = []
    for raw in consumables or []:
        c = ConsumableInput.model_validate(raw)
        cost = c.kg_per_kg_catalyst * c.price_per_kg / LB_PER_KG
        additions.append({**c.model_dump(), "cost_per_lb_cat": round(cost, 6)})
        total += cost
    for item in [*result["components"], *additions]:
        item["cost_pct"] = round(item["cost_per_lb_cat"] / total * 100, 1) if total else 0.0
    result.update(
        total_materials_cost_per_lb=round(total, 6),
        consumables=additions,
        costing_basis="User-supplied purchased inputs per kg of finished catalyst; no solvent recovery credit.",
    )
    return result
