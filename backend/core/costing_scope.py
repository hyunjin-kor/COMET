"""Describe the operations represented by a result without changing its costs."""

from __future__ import annotations

import json
from collections import Counter
from functools import lru_cache

from backend.core.constants import STEP_COSTS
from backend.core.step_method import fit_steps_to_scale
from backend.paths import data_dir


@lru_cache(maxsize=1)
def _step_metadata() -> dict[str, dict]:
    with (data_dir() / "step_library.json").open(encoding="utf-8") as handle:
        return {step["key"]: step for step in json.load(handle)["steps"]}


def summarize_costing_scope(
    route_summary: dict | None,
    actual_steps: list[str],
    scale: str,
    catalyst_domain: str,
    electrode_model: dict | None = None,
) -> dict:
    """Report declared omissions, fitted equipment and the actual charged steps.

    Repeated operations count separately. A priced selection is only a Step
    Method boundary, never evidence that every plant operation is covered.
    """
    route = route_summary or {}
    declared = list(route.get("steps", []))
    fitted, proposed_substitutions, unavailable = fit_steps_to_scale(declared, scale)
    actual_counts = Counter(actual_steps)
    omitted = list((Counter(fitted) - actual_counts).elements()) if declared else []
    added = list((actual_counts - Counter(fitted)).elements()) if declared else []
    substitution_counts = actual_counts.copy()
    substitutions = []
    for substitution in proposed_substitutions:
        if substitution_counts[substitution["to"]] > 0:
            substitutions.append(substitution)
            substitution_counts[substitution["to"]] -= 1

    metadata = _step_metadata()
    costed_steps = []
    dropped = list(unavailable)
    for step in actual_steps:
        if STEP_COSTS.get(step, {}).get(scale) is None:
            if step not in dropped:
                dropped.append(step)
            continue
        entry = metadata.get(step, {})
        costed_steps.append({
            "step": step,
            "name": entry.get("name", step),
            "status": "proxy" if entry.get("confidence") == "proxy" else "costed",
            "source": entry.get("source", ""),
            "reference_url": entry.get("reference_url"),
            "basis": entry.get("basis", ""),
        })

    uncosted = list(route.get("uncosted_operations", []))
    area_boundary = None
    if catalyst_domain == "electrocatalyst":
        boundary = "Step Method processing describes the powder route; it is not added to the electrode-area total."
        if electrode_model and electrode_model.get("manufacturing"):
            area_boundary = (
                "Electrode-area total includes the selected material stack and the published "
                "manufacturing operating point. Stage yield losses and complete stack assembly are not costed."
            )
        else:
            area_boundary = (
                "Electrode-area total includes the selected material stack only. "
                "Manufacturing throughput, stage yield losses and complete stack assembly are not costed."
            )
    else:
        boundary = (
            "Selected Step Method operations, materials, overhead and selling margin only. "
            "A priced operation list does not establish complete plant coverage."
        )
    partial = bool(uncosted or dropped or omitted or not costed_steps or area_boundary)
    proxy = bool(substitutions or any(step["status"] == "proxy" for step in costed_steps))
    return {
        "status": "partial" if partial else "proxy" if proxy else "modeled_steps",
        "boundary": boundary,
        "actual_steps": list(actual_steps),
        "costed_steps": costed_steps,
        "declared_steps": declared,
        "substitutions": substitutions,
        "dropped_steps": dropped,
        "omitted_template_steps": omitted,
        "added_steps": added,
        "uncosted_operations": uncosted,
        "route_modified": bool(declared and Counter(fitted) != actual_counts),
        "template_name": route.get("name"),
        "area_cost_boundary": area_boundary,
    }
