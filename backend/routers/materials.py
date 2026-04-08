"""Materials library API endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlmodel import Session, select

from backend.core.material_pricing import mass_price_to_per_lb
from backend.database import ensure_material_library_seeded, get_session
from backend.models.material import Material
from backend.paths import data_dir

router = APIRouter(prefix="/api/materials", tags=["materials"])

_DATA_DIR = data_dir()
_THERMAL_DOMAIN_MARKERS = {"thermal", "general", "both"}
_SUPPORT_TOKENS = (
    "support",
    "alumina",
    "al2o3",
    "silica",
    "sio2",
    "titania",
    "tio2",
    "ceria",
    "ceo2",
    "magnesia",
    "mgo",
    "zirconia",
    "zro2",
    "zeolite",
    "zsm-5",
    "usy",
    "silica-alumina",
    "carbon black",
)


def _material_to_response(material: Material) -> dict:
    """Normalize DB rows into the API response shape used by the frontend."""

    return {
        "id": material.library_key or str(material.id),
        "name": material.name,
        "symbol": material.symbol,
        "formula": material.formula,
        "category": material.category,
        "mw": material.mw,
        "density": material.density,
        "concentration_pct": material.concentration_pct,
        "price": material.price,
        "price_unit": material.price_unit,
        "price_scope": material.price_scope,
        "pack_quantity": material.pack_quantity,
        "pack_unit": material.pack_unit,
        "quote_year": material.quote_year,
        "quote_source": material.source,
        "notes": material.notes,
        "has_lab_data": material.has_lab_data,
        "catalyst_domain": material.catalyst_domain,
        "application_family": material.application_family,
        "pricing_basis": material.pricing_basis,
        "reference_url": material.reference_url,
        "is_custom": material.is_custom,
    }


def _template_domain(template: dict) -> str:
    """Return the template catalyst-domain marker."""

    return template.get("catalyst_domain", "thermal")


def _is_thermal_material(material: Material) -> bool:
    """Return whether a material row can be used in the thermal workflow."""

    return (material.catalyst_domain or "thermal").strip().lower() in _THERMAL_DOMAIN_MARKERS


def _is_support_material(material: Material) -> bool:
    """Classify support-like materials used for thermal catalyst carriers."""

    haystack = " ".join(
        filter(None, [material.name, material.formula, material.category])
    ).lower()
    category = (material.category or "").lower()
    return "support" in category or any(token in haystack for token in _SUPPORT_TOKENS)


def _is_active_or_promoter_material(material: Material) -> bool:
    """Classify thermal active/promoter candidates from the library."""

    if not _is_thermal_material(material) or _is_support_material(material):
        return False

    category = (material.category or "").lower()
    if "solvent" in category:
        return False

    # Keep genuine catalyst precursors and metal rows. This avoids flooding the
    # composition selector with generic solvents while still surfacing the broad
    # thermal library beyond the previously hardcoded list.
    return bool(material.symbol) or category != "chemical"


def _normalized_per_lb(material: Material) -> float | None:
    """Normalize the stored material quote into USD per pound when possible."""

    try:
        return round(mass_price_to_per_lb(material.price or 0.0, material.price_unit), 6)
    except ValueError:
        return None


def _composition_option(material: Material) -> dict | None:
    """Serialize a material row for the thermal composition selector."""

    normalized_price = _normalized_per_lb(material)
    if normalized_price is None:
        return None

    display_name = material.formula or material.name
    source_type = "manual" if material.is_custom else "indexed"
    return {
        "material_key": material.library_key or str(material.id),
        "name": material.name,
        "display_name": display_name,
        "symbol": material.symbol,
        "formula": material.formula,
        "category": material.category,
        "price_per_lb": normalized_price,
        "price_unit": material.price_unit,
        "price_scope": material.price_scope,
        "quote_source": material.source,
        "quote_year": material.quote_year,
        "reference_url": material.reference_url,
        "source_type": source_type,
        "selection_key": f"library:{material.library_key or material.id}",
        "label": (
            f"{display_name} | {material.category}"
            + (f" | {material.source}" if material.source else "")
        ),
    }


@router.get("/composition-options")
def list_composition_options(
    catalyst_domain: str = Query(default="thermal"),
    session: Session = Depends(get_session),
):
    """Return DB-backed composition choices for the thermal catalyst workspace."""

    if catalyst_domain.strip().lower() != "thermal":
        return {
            "max_components": 4,
            "active_metal_options": [],
            "promoter_options": [],
            "support_options": [],
        }

    ensure_material_library_seeded(session)
    materials = session.exec(select(Material).order_by(Material.name)).all()
    thermal_rows = [material for material in materials if _is_thermal_material(material)]

    active_materials = [
        option
        for material in thermal_rows
        if _is_active_or_promoter_material(material)
        for option in [_composition_option(material)]
        if option is not None
    ]
    support_materials = [
        option
        for material in thermal_rows
        if _is_support_material(material)
        for option in [_composition_option(material)]
        if option is not None
    ]

    active_materials.sort(
        key=lambda item: (
            item["display_name"].lower() != item["name"].lower(),
            item["display_name"].lower(),
            item["name"].lower(),
        )
    )
    support_materials.sort(
        key=lambda item: (
            item["display_name"].lower(),
            item["name"].lower(),
        )
    )

    return {
        "max_components": 4,
        "active_metal_options": active_materials,
        "promoter_options": active_materials,
        "support_options": support_materials,
    }


@router.get("")
def list_materials(
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    catalyst_domain: str | None = Query(default=None),
    application_family: str | None = Query(default=None),
    limit: int = Query(default=200, le=1000),
    session: Session = Depends(get_session),
):
    """List materials from the DB-backed library plus user-added entries."""

    ensure_material_library_seeded(session)

    stmt = select(Material)
    if category:
        stmt = stmt.where(Material.category.ilike(f"%{category}%"))

    if catalyst_domain:
        normalized_domain = catalyst_domain.strip().lower()
        stmt = stmt.where(
            or_(
                Material.catalyst_domain == normalized_domain,
                Material.catalyst_domain == "general",
                Material.catalyst_domain == "both",
            )
        )

    if application_family:
        normalized_application = application_family.strip().lower()
        stmt = stmt.where(
            or_(
                Material.application_family == normalized_application,
                Material.application_family == "general",
            )
        )

    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            or_(
                Material.name.ilike(pattern),
                Material.formula.ilike(pattern),
                Material.symbol.ilike(pattern),
            )
        )

    stmt = stmt.order_by(Material.is_custom.desc(), Material.name).limit(limit)
    materials = session.exec(stmt).all()
    return [_material_to_response(material) for material in materials]


@router.get("/categories")
def list_categories(session: Session = Depends(get_session)):
    """Return all distinct material type categories."""

    ensure_material_library_seeded(session)
    categories = session.exec(select(Material.category)).all()
    return sorted({category for category in categories if category})


@router.get("/domains")
def list_domains(session: Session = Depends(get_session)):
    """Return all catalyst-domain markers present in the material library."""

    ensure_material_library_seeded(session)
    domains = session.exec(select(Material.catalyst_domain)).all()
    return sorted({domain for domain in domains if domain})


@router.get("/applications")
def list_application_families(session: Session = Depends(get_session)):
    """Return all application-family markers present in the material library."""

    ensure_material_library_seeded(session)
    applications = session.exec(select(Material.application_family)).all()
    return sorted({application for application in applications if application})


@router.post("")
def create_material(material: Material, session: Session = Depends(get_session)):
    """Add a custom material to the library."""
    material.library_key = None
    material.is_custom = True
    session.add(material)
    session.commit()
    session.refresh(material)
    return material


@router.get("/templates")
def list_templates(catalyst_domain: str | None = Query(default=None)):
    """List available process templates."""
    templates_dir = _DATA_DIR / "process_templates"
    results = []
    if not templates_dir.exists():
        return results
    for f in sorted(templates_dir.glob("*.json")):
        with open(f, encoding="utf-8") as fp:
            data = json.load(fp)
        template_domain = _template_domain(data)
        if catalyst_domain and catalyst_domain.strip().lower() != template_domain:
            continue
        results.append({
            "id": data["id"],
            "name": data["name"],
            "description": data["description"],
            "category": data.get("category", ""),
            "catalyst_domain": template_domain,
            "application_family": data.get("application_family", "general"),
            "manufacturing_mode": data.get("manufacturing_mode", "batch"),
            "example_catalysts": data.get("example_catalysts", []),
            "preprocess": data.get("preprocess", []),
            "synthesis": data.get("synthesis", []),
            "postprocess": data.get("postprocess", []),
            "quality_gates": data.get("quality_gates", []),
            "steps": data.get("steps", []),
            "route_note": data.get("route_note", ""),
            "source": data.get("source", ""),
            "reference_urls": data.get("reference_urls", []),
        })
    return results


@router.get("/templates/{template_id}")
def get_template(template_id: str):
    """Get a specific process template."""
    path = _DATA_DIR / "process_templates" / f"{template_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("catalyst_domain", _template_domain(data))
    return data


@router.get("/steps")
def list_steps():
    """List all available processing steps with costs."""
    with open(_DATA_DIR / "step_library.json", encoding="utf-8") as f:
        data = json.load(f)
    return data["steps"]


@router.get("/equipment")
def list_equipment(
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
):
    """List equipment from library."""
    with open(_DATA_DIR / "equipment_library.json", encoding="utf-8") as f:
        data = json.load(f)
    equipment = data.get("equipment", [])
    results = []
    for eq in equipment:
        if category and category.lower() not in (eq.get("category") or "").lower():
            continue
        if q and q.lower() not in (eq.get("name") or "").lower():
            continue
        results.append(eq)
    return results[:limit]
