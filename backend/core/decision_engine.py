"""Benchmark-driven decision engine for catalyst screening."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from sqlmodel import Session, select

from backend.core.constants import LB_PER_KG, TROY_OZ_PER_LB
from backend.core.cost_engine import estimate_catalyst_cost
from backend.core.price_evidence import build_fixed_evidence, describe_price_evidence
from backend.core.price_fetcher import get_reference_prices
from backend.models.metal_price import MetalPrice
from backend.paths import data_dir


@lru_cache(maxsize=1)
def _load_catalog() -> dict[str, Any]:
    with open(data_dir() / "ammonia_cracking_benchmark.json", encoding="utf-8") as handle:
        return json.load(handle)


def list_benchmark_families() -> list[dict[str, Any]]:
    """Return the benchmark families available to the UI."""

    catalog = _load_catalog()
    return [
        {
            "family": catalog["family"],
            "title": catalog["title"],
            "reaction": catalog["reaction"],
            "objective": catalog["objective"],
            "candidate_count": len(catalog["candidates"]),
        }
    ]


def _normalize_price_per_lb(price: float, unit: str) -> float:
    if unit == "$/lb":
        return price
    if unit == "$/kg":
        return price / LB_PER_KG
    if unit == "$/troy_oz":
        return price * TROY_OZ_PER_LB
    raise ValueError(f"Unsupported price unit: {unit}")


def _latest_price_map(session: Session) -> dict[str, dict[str, Any]]:
    stmt = select(MetalPrice).order_by(MetalPrice.fetched_at.desc())
    latest_rows = session.exec(stmt).all()

    seen: set[str] = set()
    prices: dict[str, dict[str, Any]] = {}
    for row in latest_rows:
        if row.symbol in seen:
            continue
        seen.add(row.symbol)
        prices[row.symbol] = {
            "symbol": row.symbol,
            "name": row.name,
            "price": row.price,
            "unit": row.unit,
            "source": row.source,
            "fetched_at": row.fetched_at.isoformat(),
        }

    for symbol, info in get_reference_prices().items():
        prices.setdefault(
            symbol,
            {
                "symbol": symbol,
                "name": info["name"],
                "price": info["price"],
                "unit": info["unit"],
                "source": info["source"],
                "fetched_at": info["fetched_at"],
            },
        )
    return prices


def _resolve_component_pricing(
    component: dict[str, Any],
    latest_prices: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    pricing = component["pricing"]

    if pricing["type"] == "market_feed":
        symbol = pricing["symbol"]
        latest = latest_prices[symbol]
        price_per_lb = _normalize_price_per_lb(float(latest["price"]), latest["unit"])
        evidence = describe_price_evidence(
            source=latest["source"],
            fetched_at=latest["fetched_at"],
        )
        component_input = {
            "role": component["role"],
            "name": component["name"],
            "wt_pct": component["wt_pct"],
            "price_per_lb": round(price_per_lb, 6),
            "precursor_markup": pricing.get("precursor_markup", 1.0),
        }
        component_meta = {
            "source_type": "live" if evidence["tier"] != "indexed_reference" else "indexed",
            "source": latest["source"],
            "unit": latest["unit"],
            "price_basis": "market_feed",
            "pricing_note": pricing["note"],
            "fetched_at": latest["fetched_at"],
            "evidence": evidence,
        }
        return component_input, component_meta

    evidence = build_fixed_evidence(
        label=pricing["evidence_label"],
        note=pricing["note"],
        tier=pricing["evidence_tier"],
        confidence_score=pricing["confidence_score"],
        transparency=pricing["transparency"],
    )
    component_input = {
        "role": component["role"],
        "name": component["name"],
        "wt_pct": component["wt_pct"],
        "price_per_lb": round(float(pricing["price_per_lb"]), 6),
        "precursor_markup": pricing.get("precursor_markup", 1.0),
    }
    component_meta = {
        "source_type": "fixed",
        "source": pricing["evidence_label"],
        "unit": "$/lb",
        "price_basis": "fixed",
        "pricing_note": pricing["note"],
        "fetched_at": None,
        "evidence": evidence,
    }
    return component_input, component_meta


def _component_cost_shares(
    *,
    breakdown: list[dict[str, Any]],
    component_meta: list[dict[str, Any]],
    quote_map: dict[str, dict[str, Any]],
    candidate: dict[str, Any],
) -> list[dict[str, Any]]:
    catalog_quote_ids = set(candidate.get("catalog_quote_ids", []))
    enriched: list[dict[str, Any]] = []
    for index, item in enumerate(breakdown):
        meta = component_meta[index]
        catalog_quotes = [
            quote_map[quote_id]
            for quote_id in catalog_quote_ids
            if quote_id in quote_map and item["name"] in quote_map[quote_id]["material"]
        ]
        enriched.append(
            {
                **item,
                "source_type": meta["source_type"],
                "source": meta["source"],
                "price_basis": meta["price_basis"],
                "pricing_note": meta["pricing_note"],
                "evidence": meta["evidence"],
                "catalog_quotes": catalog_quotes,
            }
        )
    return enriched


def _weighted_evidence_score(components: list[dict[str, Any]]) -> float:
    total = sum(float(item["cost_per_lb_cat"]) for item in components)
    if total <= 0:
        return 0.0
    return round(
        sum(float(item["cost_per_lb_cat"]) * float(item["evidence"]["confidence_score"]) for item in components)
        / total,
        1,
    )


def _route_score(candidate: dict[str, Any], route: dict[str, Any]) -> float:
    return round(
        (
            float(route["route_confidence"])
            + float(candidate["manufacturing_readiness"])
            + float(candidate["screening_exactness"])
        )
        / 3,
        1,
    )


def _economic_scores(candidates: list[dict[str, Any]]) -> None:
    if not candidates:
        return
    costs = [float(item["summary"]["landed_cost_per_lb"]) for item in candidates]
    high = max(costs)
    low = min(costs)
    spread = high - low
    for item in candidates:
        price = float(item["summary"]["landed_cost_per_lb"])
        if spread <= 1e-9:
            item["scores"]["economics"] = 100.0
        else:
            item["scores"]["economics"] = round((high - price) / spread * 100, 1)


def _apply_total_scores(candidates: list[dict[str, Any]], weights: dict[str, float]) -> None:
    for item in candidates:
        item["scores"]["total"] = round(
            item["scores"]["economics"] * weights["economics"]
            + item["scores"]["evidence"] * weights["evidence"]
            + item["scores"]["route"] * weights["route"]
            + item["scores"]["performance"] * weights["performance"],
            1,
        )


def evaluate_benchmark_family(
    *,
    session: Session,
    family: str = "ammonia-cracking",
    profile: str = "balanced",
) -> dict[str, Any]:
    """Evaluate one benchmark family with the current price basis."""

    catalog = _load_catalog()
    if family != catalog["family"]:
        raise KeyError(f"Unknown benchmark family: {family}")

    profile_config = catalog["decision_profiles"].get(profile)
    if profile_config is None:
        raise KeyError(f"Unknown decision profile: {profile}")

    route_map = {item["id"]: item for item in catalog["route_templates"]}
    quote_map = {item["id"]: item for item in catalog["catalog_quotes"]}
    citation_map = {item["id"]: item for item in catalog["citations"]}
    latest_prices = _latest_price_map(session)

    candidates: list[dict[str, Any]] = []
    latest_update = None
    for candidate in catalog["candidates"]:
        route = route_map[candidate["route_template_id"]]

        component_inputs: list[dict[str, Any]] = []
        component_meta: list[dict[str, Any]] = []
        for component in candidate["components"]:
            component_input, meta = _resolve_component_pricing(component, latest_prices)
            component_inputs.append(component_input)
            component_meta.append(meta)

            evidence_update = meta.get("fetched_at")
            if evidence_update:
                latest_update = max(latest_update or evidence_update, evidence_update)

        estimate = estimate_catalyst_cost(
            components=component_inputs,
            steps=route["steps"],
            order_size_tons=float(candidate["order_size_tons"]),
        )
        enriched_components = _component_cost_shares(
            breakdown=estimate["materials"]["components"],
            component_meta=component_meta,
            quote_map=quote_map,
            candidate=candidate,
        )

        extra_route_cost = float(route["non_step_cost_per_lb"])
        landed_cost_per_lb = float(estimate["summary"]["estimated_price_per_lb"]) + extra_route_cost
        landed_cost_per_kg = landed_cost_per_lb * LB_PER_KG
        weighted_evidence = _weighted_evidence_score(enriched_components)
        route_score = _route_score(candidate, route)
        dominant_driver = max(enriched_components, key=lambda item: float(item["cost_per_lb_cat"]))

        candidate_result = {
            "slug": candidate["slug"],
            "title": candidate["title"],
            "archetype": candidate["archetype"],
            "screening_basis": candidate["screening_basis"],
            "screening_summary": candidate["summary"],
            "summary": {
                "base_estimated_price_per_lb": round(float(estimate["summary"]["estimated_price_per_lb"]), 4),
                "landed_cost_per_lb": round(landed_cost_per_lb, 4),
                "landed_cost_per_kg": round(landed_cost_per_kg, 4),
                "route_extra_cost_per_lb": round(extra_route_cost, 4),
                "materials_cost_per_lb": round(float(estimate["materials"]["total_materials_cost_per_lb"]), 4),
                "processing_cost_per_lb": round(float(estimate["step_method"]["processing_cost_per_lb"]), 4),
                "scale": estimate["step_method"]["scale"],
                "temperature_window_c": candidate["temperature_window_c"],
                "dominant_cost_driver": dominant_driver["name"],
            },
            "scores": {
                "economics": 0.0,
                "evidence": weighted_evidence,
                "route": route_score,
                "performance": float(candidate["performance_index"]),
                "total": 0.0,
            },
            "route": {
                "name": route["name"],
                "manufacturing_mode": route["manufacturing_mode"],
                "preprocess": route["preprocess"],
                "synthesis": route["synthesis"],
                "postprocess": route["postprocess"],
                "quality_gates": route["quality_gates"],
                "steps": route["steps"],
                "route_note": route["route_note"],
            },
            "evidence_summary": {
                "weighted_confidence_score": weighted_evidence,
                "live_component_count": sum(1 for item in enriched_components if item["source_type"] == "live"),
                "fixed_component_count": sum(1 for item in enriched_components if item["source_type"] == "fixed"),
                "indexed_component_count": sum(1 for item in enriched_components if item["source_type"] == "indexed"),
            },
            "components": enriched_components,
            "decision_notes": candidate["decision_notes"],
            "literature_basis": [citation_map[citation_id] for citation_id in candidate["literature_basis_ids"]],
            "catalog_quotes": [quote_map[quote_id] for quote_id in candidate["catalog_quote_ids"]],
            "estimate": estimate,
        }
        candidates.append(candidate_result)

    _economic_scores(candidates)
    _apply_total_scores(candidates, profile_config["weights"])
    candidates.sort(
        key=lambda item: (
            float(item["scores"]["total"]),
            -float(item["summary"]["landed_cost_per_lb"]),
        ),
        reverse=True,
    )

    return {
        "family": catalog["family"],
        "title": catalog["title"],
        "reaction": catalog["reaction"],
        "objective": catalog["objective"],
        "decision_profile": {
            "id": profile,
            "label": profile_config["label"],
            "description": profile_config["description"],
            "weights": profile_config["weights"],
        },
        "price_basis_updated_at": latest_update,
        "winner": candidates[0] if candidates else None,
        "candidates": candidates,
        "citations": catalog["citations"],
    }
