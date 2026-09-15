"""Source-specific preparation records, separate from screening cost assumptions."""

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _library() -> dict:
    path = Path(__file__).resolve().parents[1] / "data" / "manufacturing_literature.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    operating = json.loads(path.with_name("manufacturing_operating_references.json").read_text(encoding="utf-8"))
    return {**data, "operating_references": operating["references"]}


def manufacturing_library() -> dict:
    return deepcopy(_library())


def reviewed_citation(citation: dict) -> dict:
    """Use registered titles instead of unverified catalog descriptions in the UI."""
    source = next((s for s in _library()["sources"] if citation["url"] in s["catalog_urls"]), None)
    return {**citation, "note": source["title"]} if source else deepcopy(citation)


def candidate_manufacturing_evidence(family: str, slug: str) -> dict:
    data = _library()
    review = next(row for row in data["candidates"] if row["family"] == family and row["slug"] == slug)
    profiles = [p for p in data["profiles"] if p["id"] in review["profile_ids"]]
    return deepcopy({**review, "profiles": profiles, "review_date": data["review_date"]})
