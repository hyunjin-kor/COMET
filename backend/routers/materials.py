"""Materials library API endpoints."""

import hashlib
import json
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlmodel import Session, select

from backend.core.material_pricing import mass_price_to_per_lb
from backend.database import ensure_material_library_seeded, get_session
from backend.models.equipment import Equipment
from backend.models.material import Material
from backend.paths import data_dir
from backend.schemas.equipment import EquipmentResponse
from backend.schemas.material import MaterialCreate, MaterialUpdate

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
_ELEMENT_NAME_TO_SYMBOL = {
    "aluminium": "Al",
    "aluminum": "Al",
    "cobalt": "Co",
    "copper": "Cu",
    "cuprous": "Cu",
    "cupric": "Cu",
    "cerium": "Ce",
    "ceria": "Ce",
    "iron": "Fe",
    "ferric": "Fe",
    "ferrous": "Fe",
    "indium": "In",
    "iridium": "Ir",
    "lanthanum": "La",
    "magnesium": "Mg",
    "manganese": "Mn",
    "molybdenum": "Mo",
    "molybdate": "Mo",
    "nickel": "Ni",
    "palladium": "Pd",
    "platinum": "Pt",
    "rhodium": "Rh",
    "ruthenium": "Ru",
    "silver": "Ag",
    "tungsten": "W",
    "tungstate": "W",
    "metatungstate": "W",
    "zinc": "Zn",
}
_SUPPORT_IDENTITY_RULES = (
    (("silica-alumina", "sio2-al2o3"), "SiO2-Al2O3"),
    (("al2o3", "alumina", "aluminum oxide", "aluminium oxide"), "Al2O3"),
    (("ceo2", "ceria", "cerium oxide"), "CeO2"),
    (("tio2", "titania", "titanium dioxide"), "TiO2"),
    (("mgo", "magnesia", "magnesium oxide"), "MgO"),
    (("zro2", "zirconia", "zirconium oxide"), "ZrO2"),
    (("sio2", "silica"), "SiO2"),
    (("carbon black", "activated carbon", "carbon support", "graphitic carbon"), "Carbon"),
    (("zsm-5",), "ZSM-5"),
    (("usy",), "USY"),
    (("beta zeolite", "zeolite beta"), "Beta zeolite"),
)


def _load_equipment_library() -> list[dict]:
    """Load the bundled equipment library rows."""

    with open(_DATA_DIR / "equipment_library.json", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("equipment", [])


def _equipment_library_key(equipment: dict) -> str:
    """Generate a deterministic key for one bundled equipment row."""

    fingerprint = json.dumps(equipment, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:16]
    return f"bundled:{digest}"


def _equipment_to_response(equipment: dict) -> dict:
    """Normalize a bundled equipment row into the API response shape."""

    payload = dict(equipment)
    payload["id"] = _equipment_library_key(equipment)
    payload["is_custom"] = False
    return payload


def get_bundled_equipment_detail(equipment_id: str) -> dict:
    """Load one bundled equipment row by its stable deterministic id."""

    for equipment in _load_equipment_library():
        if _equipment_library_key(equipment) == equipment_id:
            return _equipment_to_response(equipment)
    raise HTTPException(status_code=404, detail="Equipment not found")


def _custom_equipment_to_response(record: Equipment) -> dict:
    """Normalize a custom equipment row into the dedicated API response shape."""

    return EquipmentResponse.model_validate(record).model_dump()


def get_equipment_detail(equipment_id: str, session: Session) -> dict:
    """Resolve bundled and custom equipment identifiers into one response shape."""

    if equipment_id.isdigit():
        record = session.get(Equipment, int(equipment_id))
        if record is not None:
            return _custom_equipment_to_response(record)

    return get_bundled_equipment_detail(equipment_id)


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


def _get_material_or_404(material_id: int, session: Session) -> Material:
    """Load one material row by numeric identifier."""

    material = session.get(Material, material_id)
    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


def _get_custom_material_or_error(material_id: int, session: Session) -> Material:
    """Load one custom material row and reject bundled reference rows."""

    material = _get_material_or_404(material_id, session)
    if not material.is_custom:
        raise HTTPException(status_code=403, detail="Bundled library materials are read-only")
    return material


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


def _infer_symbol(material: Material) -> str | None:
    """Infer a concise elemental identity from the stored material row."""

    if material.symbol:
        symbol = material.symbol.strip()
        if symbol:
            return symbol

    haystack = " ".join(filter(None, [material.name, material.formula])).lower()
    for token, symbol in _ELEMENT_NAME_TO_SYMBOL.items():
        if re.search(rf"\b{re.escape(token)}\b", haystack):
            return symbol
    return None


def _matches_identity_token(haystack: str, token: str) -> bool:
    """Match canonical identity tokens without over-matching precursor text."""

    return re.search(
        rf"(?<![A-Za-z0-9]){re.escape(token)}(?![A-Za-z0-9])",
        haystack,
    ) is not None


def _canonical_support_identity(material: Material) -> str | None:
    """Return the exact support identity exposed in the calculator selector."""

    haystack = " ".join(filter(None, [material.formula, material.name, material.category])).lower()
    for tokens, identity in _SUPPORT_IDENTITY_RULES:
        if any(_matches_identity_token(haystack, token) for token in tokens):
            return identity

    if material.formula:
        formula = material.formula.strip()
        if formula:
            return formula
    return None


def _canonical_active_identity(material: Material) -> str | None:
    """Return the exact active/promoter identity exposed in the calculator selector."""

    return _infer_symbol(material)


def _composition_option(material: Material, display_name: str) -> dict | None:
    """Serialize a material row for the thermal composition selector."""

    normalized_price = _normalized_per_lb(material)
    if normalized_price is None:
        return None

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
        for display_name in [_canonical_active_identity(material)]
        if display_name is not None
        for option in [_composition_option(material, display_name)]
        if option is not None
    ]
    support_materials = [
        option
        for material in thermal_rows
        if _is_support_material(material)
        for display_name in [_canonical_support_identity(material)]
        if display_name is not None
        for option in [_composition_option(material, display_name)]
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
def create_material(payload: MaterialCreate, session: Session = Depends(get_session)):
    """Add a custom material to the library."""
    material = Material(**payload.model_dump())
    material.library_key = None
    material.is_custom = True
    session.add(material)
    session.commit()
    session.refresh(material)
    return _material_to_response(material)


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
    equipment = _load_equipment_library()
    results = []
    for eq in equipment:
        if category and category.lower() not in (eq.get("category") or "").lower():
            continue
        if q and q.lower() not in (eq.get("name") or "").lower():
            continue
        results.append(_equipment_to_response(eq))
    return results[:limit]


@router.get("/equipment/{equipment_id}")
def get_equipment_detail_via_legacy_alias(
    equipment_id: str,
    session: Session = Depends(get_session),
):
    """Support legacy material-scoped equipment detail lookups."""

    return get_equipment_detail(equipment_id, session)


@router.get("/{material_id}")
def get_material(
    material_id: int,
    session: Session = Depends(get_session),
):
    """Get one material row by numeric identifier."""

    material = _get_material_or_404(material_id, session)
    return _material_to_response(material)


@router.patch("/{material_id}")
def update_material(
    material_id: int,
    payload: MaterialUpdate,
    session: Session = Depends(get_session),
):
    """Patch mutable fields on a custom material row."""

    material = _get_custom_material_or_error(material_id, session)
    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(material, field_name, value)

    session.add(material)
    session.commit()
    session.refresh(material)
    return _material_to_response(material)


@router.delete("/{material_id}")
def delete_material(
    material_id: int,
    session: Session = Depends(get_session),
):
    """Delete one custom material row by numeric identifier."""

    material = _get_custom_material_or_error(material_id, session)
    session.delete(material)
    session.commit()
    return {"status": "deleted", "id": str(material_id)}
