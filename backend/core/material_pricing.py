"""Helpers for resolving library-backed material prices into calculation units."""

from __future__ import annotations

from sqlmodel import Session, select

from backend.core.constants import LB_PER_KG, TROY_OZ_PER_LB
from backend.models.material import Material

GRAMS_PER_LB = 453.59237
MG_PER_LB = GRAMS_PER_LB * 1000.0
ML_PER_L = 1000.0
CM2_PER_M2 = 10_000.0


def normalize_price_unit(unit: str | None) -> str:
    """Normalize common price-unit spellings into a compact internal form."""

    normalized = (unit or "").strip().lower().replace(" ", "")
    normalized = normalized.replace("usd", "$")
    normalized = normalized.replace("us$", "$")
    normalized = normalized.replace("²", "2")
    normalized = normalized.replace("^2", "2")
    normalized = normalized.replace("μ", "u").replace("µ", "u")
    return normalized


def mass_price_to_per_lb(price: float, unit: str | None) -> float:
    """Convert a mass-based price into USD per pound."""

    normalized = normalize_price_unit(unit)
    if normalized == "$/lb":
        return price
    if normalized == "$/kg":
        return price / LB_PER_KG
    if normalized == "$/g":
        return price * GRAMS_PER_LB
    if normalized == "$/mg":
        return price * MG_PER_LB
    if normalized == "$/troy_oz":
        return price * TROY_OZ_PER_LB
    raise ValueError(f"Unsupported mass price unit: {unit}")


def mass_price_to_per_kg(price: float, unit: str | None) -> float:
    """Convert a mass-based price into USD per kilogram."""

    return mass_price_to_per_lb(price, unit) * LB_PER_KG


def volume_price_to_per_ml(price: float, unit: str | None) -> float:
    """Convert a volume-based price into USD per milliliter."""

    normalized = normalize_price_unit(unit)
    if normalized == "$/ml":
        return price
    if normalized == "$/l":
        return price / ML_PER_L
    if normalized == "$/ul":
        return price * ML_PER_L
    raise ValueError(f"Unsupported volume price unit: {unit}")


def area_price_to_per_cm2(price: float, unit: str | None) -> float:
    """Convert an area-based price into USD per square centimeter."""

    normalized = normalize_price_unit(unit)
    if normalized == "$/cm2":
        return price
    if normalized == "$/m2":
        return price / CM2_PER_M2
    raise ValueError(f"Unsupported area price unit: {unit}")


def resolve_library_material(session: Session, material_key: str) -> Material:
    """Fetch a material row by library key or numeric primary key."""

    stmt = select(Material).where(Material.library_key == material_key)
    material = session.exec(stmt).first()
    if material is not None:
        return material

    if material_key.isdigit():
        stmt = select(Material).where(Material.id == int(material_key))
        material = session.exec(stmt).first()
        if material is not None:
            return material

    raise ValueError(f"Unknown material_key: {material_key}")


# Library rows that represent a pure-metal commodity proxy (USGS bulk
# reference). These are eligible for runtime upgrade to a live market
# quote when one is available, so the calculator and the live-prices
# panel never disagree on the same metal.
_LIVE_ELIGIBLE_LIBRARY_KEYS: set[str] = {
    "lit:usgs-platinum-bullion-2025",
    "lit:usgs-palladium-bullion-2025",
    "lit:usgs-rhodium-bullion-2025",
    "lit:usgs-iridium-bullion-2025",
    "lit:usgs-ruthenium-bullion-2025",
    "lit:usgs-gold-bullion-2025",
    "lit:usgs-silver-bullion-2025",
    "lit:usgs-copper-cathode-2025",
    "lit:usgs-nickel-cathode-2025",
    "lit:usgs-cobalt-cathode-2025",
    "lit:usgs-aluminum-ingot-2025",
}


def _latest_live_price(session: Session, symbol: str) -> "MetalPrice | None":  # noqa: F821
    """Return the most recent stored live quote for ``symbol``, if any."""

    from backend.models.metal_price import MetalPrice  # local import to avoid cycle

    stmt = (
        select(MetalPrice)
        .where(MetalPrice.symbol == symbol)
        .order_by(MetalPrice.fetched_at.desc())
        .limit(1)
    )
    return session.exec(stmt).first()


def _live_override_for_material(
    session: Session, material: Material
) -> dict | None:
    """If ``material`` is a USGS commodity proxy and a live quote exists, return it.

    Returns a dict with ``price``, ``price_unit``, ``source``, ``fetched_at``
    suitable for swapping into the resolved component. Returns ``None`` when
    the row is not eligible for live upgrade or no live quote is stored.
    """

    library_key = material.library_key or ""
    if library_key not in _LIVE_ELIGIBLE_LIBRARY_KEYS:
        return None
    symbol = (material.symbol or "").strip()
    if not symbol:
        return None

    quote = _latest_live_price(session, symbol)
    if quote is None or quote.price is None or quote.price <= 0:
        return None

    return {
        "price": float(quote.price),
        "price_unit": quote.unit,
        "source": quote.source,
        "fetched_at": quote.fetched_at.isoformat() if quote.fetched_at else None,
        "symbol": symbol,
    }


def material_snapshot(material: Material, *, used_for: str) -> dict:
    """Serialize a material row for calculation evidence reporting."""

    return {
        "material_key": material.library_key or str(material.id),
        "used_for": used_for,
        "name": material.name,
        "category": material.category,
        "catalyst_domain": material.catalyst_domain,
        "application_family": material.application_family,
        "price": material.price,
        "price_unit": material.price_unit,
        "price_scope": material.price_scope,
        "pack_quantity": material.pack_quantity,
        "pack_unit": material.pack_unit,
        "quote_year": material.quote_year,
        "quote_source": material.source,
        "pricing_basis": material.pricing_basis,
        "reference_url": material.reference_url,
        "notes": material.notes,
    }


def component_engine_name(material: Material, role: str) -> str:
    """Choose a concise calculation-facing label for a resolved library row."""

    if role == "support":
        return material.formula or material.name
    if role in {"active_metal", "promoter"}:
        return material.symbol or material.formula or material.name
    return material.formula or material.symbol or material.name


def resolve_component_input(session: Session, component: dict) -> tuple[dict, dict | None]:
    """Resolve a component row against the library when a material key is provided.

    For library rows that are USGS commodity-metal proxies, the resolver
    upgrades the static USGS quote to the latest live market quote when
    one is stored in the metal-price table. This keeps the catalog-backed
    catalog calculation aligned with the live prices the user sees in the
    market panel. The static USGS price is preserved in the snapshot
    metadata as the offline fallback so the audit trail still shows it.
    """

    material_key = component.get("material_key")
    if not material_key:
        if component.get("price_per_lb") is None:
            raise ValueError(
                f"Component '{component.get('name') or component.get('role', 'unknown')}' is missing price_per_lb"
            )
        return component, None

    material = resolve_library_material(session, str(material_key))
    resolved = dict(component)
    resolved["material_key"] = material.library_key or str(material.id)
    resolved["name"] = component_engine_name(material, str(component.get("role", "")))

    snapshot = material_snapshot(material, used_for=f"component:{component.get('role', 'component')}")

    live = _live_override_for_material(session, material)
    if live is not None:
        resolved["price_per_lb"] = round(
            mass_price_to_per_lb(live["price"], live["price_unit"]), 6
        )
        snapshot["price"] = live["price"]
        snapshot["price_unit"] = live["price_unit"]
        snapshot["price_scope"] = "live_market"
        snapshot["quote_source"] = live["source"]
        snapshot["normalized_price_per_lb"] = resolved["price_per_lb"]
        # Preserve the static USGS quote so the audit trail still shows it.
        snapshot["live_override"] = {
            "applied": True,
            "live_price": live["price"],
            "live_price_unit": live["price_unit"],
            "live_source": live["source"],
            "live_fetched_at": live["fetched_at"],
            "fallback_price": material.price,
            "fallback_price_unit": material.price_unit,
            "fallback_source": material.source,
            "fallback_quote_year": material.quote_year,
        }
    else:
        resolved["price_per_lb"] = round(
            mass_price_to_per_lb(material.price or 0.0, material.price_unit), 6
        )
        snapshot["normalized_price_per_lb"] = resolved["price_per_lb"]
        if (material.library_key or "") in _LIVE_ELIGIBLE_LIBRARY_KEYS:
            # Eligible for live but no quote stored; surface that for clarity.
            snapshot["live_override"] = {
                "applied": False,
                "reason": "no_live_quote_stored",
            }

    return resolved, snapshot


def resolve_electrode_materials(session: Session, raw: dict | None) -> tuple[dict | None, list[dict]]:
    """Resolve electrocatalyst adjunct materials into numeric inputs for the engine."""

    if raw is None:
        return None, []

    payload = {
        "application_family": raw.get("application_family", "general"),
        "active_area_cm2": float(raw.get("active_area_cm2", 25.0)),
        "catalyst_loading_mg_cm2": float(raw.get("catalyst_loading_mg_cm2", 0.5)),
        "ionomer_to_catalyst_ratio": float(raw.get("ionomer_to_catalyst_ratio", 0.0)),
        "ionomer_density_g_ml": float(raw.get("ionomer_density_g_ml", 0.94)),
        "ionomer_solids_fraction": float(raw.get("ionomer_solids_fraction", 0.05)),
        "substrate_cost_per_cm2": float(raw.get("substrate_cost_per_cm2", 0.0)),
        "membrane_cost_per_cm2": float(raw.get("membrane_cost_per_cm2", 0.0)),
    }
    if raw.get("ionomer_price_per_ml") is not None:
        payload["ionomer_price_per_ml"] = float(raw["ionomer_price_per_ml"])
    if raw.get("ionomer_price_per_kg_solids") is not None:
        payload["ionomer_price_per_kg_solids"] = float(raw["ionomer_price_per_kg_solids"])

    snapshots: list[dict] = []

    catalyst_key = raw.get("catalyst_material_key")
    if catalyst_key:
        material = resolve_library_material(session, str(catalyst_key))
        payload["catalyst_price_per_lb"] = round(
            mass_price_to_per_lb(material.price or 0.0, material.price_unit),
            6,
        )
        snapshot = material_snapshot(material, used_for="electrode:catalyst_powder")
        snapshot["normalized_price_per_lb"] = payload["catalyst_price_per_lb"]
        snapshots.append(snapshot)

    ionomer_key = raw.get("ionomer_material_key")
    if ionomer_key:
        material = resolve_library_material(session, str(ionomer_key))
        normalized_unit = normalize_price_unit(material.price_unit)
        snapshot = material_snapshot(material, used_for="electrode:ionomer")
        if normalized_unit in {"$/ml", "$/l", "$/ul"}:
            payload["ionomer_price_per_ml"] = round(
                volume_price_to_per_ml(material.price or 0.0, material.price_unit),
                6,
            )
            if material.density is not None:
                payload["ionomer_density_g_ml"] = float(material.density)
            if material.concentration_pct is not None:
                payload["ionomer_solids_fraction"] = float(material.concentration_pct) / 100.0
            snapshot["normalized_price_per_ml"] = payload["ionomer_price_per_ml"]
        elif normalized_unit in {"$/lb", "$/kg", "$/g", "$/mg", "$/troy_oz"}:
            payload["ionomer_price_per_kg_solids"] = round(
                mass_price_to_per_kg(material.price or 0.0, material.price_unit),
                6,
            )
            snapshot["normalized_price_per_kg_solids"] = payload["ionomer_price_per_kg_solids"]
        else:
            raise ValueError(
                f"Ionomer material '{material.name}' uses unsupported price unit '{material.price_unit}'"
            )
        snapshots.append(snapshot)

    substrate_key = raw.get("substrate_material_key")
    if substrate_key:
        material = resolve_library_material(session, str(substrate_key))
        payload["substrate_cost_per_cm2"] = round(
            area_price_to_per_cm2(material.price or 0.0, material.price_unit),
            6,
        )
        snapshot = material_snapshot(material, used_for="electrode:substrate")
        snapshot["normalized_price_per_cm2"] = payload["substrate_cost_per_cm2"]
        snapshots.append(snapshot)

    membrane_key = raw.get("membrane_material_key")
    if membrane_key:
        material = resolve_library_material(session, str(membrane_key))
        payload["membrane_cost_per_cm2"] = round(
            area_price_to_per_cm2(material.price or 0.0, material.price_unit),
            6,
        )
        snapshot = material_snapshot(material, used_for="electrode:membrane")
        snapshot["normalized_price_per_cm2"] = payload["membrane_cost_per_cm2"]
        snapshots.append(snapshot)

    return payload, snapshots
