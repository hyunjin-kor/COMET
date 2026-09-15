"""Select causal numeric inputs from the engine trace; never infer missing values."""

from backend.schemas.manufacturing import ManufacturingProtocol
from backend.schemas.manufacturing_analysis import ManufacturingRange


def manufacturing_variables(report: dict | None) -> list[dict]:
    if not report or not report["trace"]["headline_uses_protocol"] or not report["complete"]:
        raise ValueError("Manufacturing analysis requires a complete dry-powder batch cost calculation")
    purchases = report["protocol"]["materials_basis"] == "purchases"
    return [dict(row) for row in report["trace"]["inputs"]
            if row["effect"] == "cost_input" and row["unit"]
            and isinstance(row["value"], (int, float)) and not isinstance(row["value"], bool)
            and (purchases or ".purchases." not in row["path"])]


def prepare_manufacturing_ranges(report: dict, ranges: list[ManufacturingRange]) -> dict:
    available = {row["path"]: row for row in manufacturing_variables(report)}
    selected = []
    seen = set()
    for item in ranges:
        if item.path in seen:
            raise ValueError("Duplicate manufacturing variation: " + item.path)
        seen.add(item.path)
        if item.path not in available:
            raise ValueError("Manufacturing variation must name an active, known numeric cost input: " + item.path)
        row = available[item.path]
        if row["unit"] == "count" and (not item.low.is_integer() or not item.high.is_integer()):
            raise ValueError("Repetition bounds must be integers")
        selected.append({**row, **item.model_dump(), "distribution": "discrete_uniform" if row["unit"] == "count" else "uniform"})
    return {"protocol_sha256": report["trace"]["protocol_sha256"], "variables": selected,
            "assumptions": "Bounds are user-specified scenarios in absolute input units. Selected inputs are sampled independently; all others remain fixed. "
            "Constraints are rechecked for every sample; statistics exclude failed samples and are conditional on valid runs. "
            "No temperature-to-power, activity or yield relationship is inferred. Source snapshots describe baseline evidence, not a verified uncertainty distribution."}


def varied_manufacturing_protocol(protocol: ManufacturingProtocol, values: dict[str, float]) -> ManufacturingProtocol:
    """Paths must first pass prepare_manufacturing_ranges against the baseline trace."""
    data = protocol.model_dump()
    for path, value in values.items():
        parts = path.split(".")
        node = data
        for part in parts[:-1]:
            node = node[int(part)] if isinstance(node, list) else node[part]
        node[parts[-1]] = value
    return ManufacturingProtocol.model_validate(data)
