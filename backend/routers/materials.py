"""Materials library API endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.material import Material
from backend.paths import data_dir

router = APIRouter(prefix="/api/materials", tags=["materials"])

_DATA_DIR = data_dir()


def _load_library() -> list:
    """Load materials from JSON flat list."""
    with open(_DATA_DIR / "materials_library.json", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("materials", [])


@router.get("")
def list_materials(
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=200, le=1000),
    session: Session = Depends(get_session),
):
    """List materials from CatCost library + user-added entries."""
    library = _load_library()
    results = []

    for idx, mat in enumerate(library):
        mat_type = (mat.get("material_type") or "Chemical").strip()
        entry = {
            "id": f"lib_{idx}",
            "name": mat.get("name", ""),
            "symbol": None,
            "formula": None,
            "category": mat_type,
            "mw": mat.get("mw_g_mol"),
            "density": mat.get("density_g_ml"),
            "concentration_pct": mat.get("concentration_pct"),
            "price": mat.get("bulk_price_usd"),
            "price_unit": f"$/{mat.get('bulk_units', 'lb')}" if mat.get("bulk_price_usd") else None,
            "quote_year": mat.get("quote_year"),
            "quote_source": mat.get("quote_source", ""),
            "notes": mat.get("notes", ""),
            "has_lab_data": bool(mat.get("lab_qty")),
            "is_custom": False,
        }

        if category and category.lower() not in mat_type.lower():
            continue
        if q and q.lower() not in entry["name"].lower():
            continue
        results.append(entry)

    # Add user-created materials from DB
    stmt = select(Material)
    db_materials = session.exec(stmt).all()
    for m in db_materials:
        entry = {
            "id": str(m.id),
            "name": m.name,
            "symbol": m.symbol,
            "formula": m.formula,
            "category": m.category,
            "mw": m.mw,
            "density": None,
            "concentration_pct": None,
            "price": m.price,
            "price_unit": m.price_unit,
            "quote_year": None,
            "quote_source": m.source,
            "notes": "",
            "has_lab_data": False,
            "is_custom": True,
        }
        if category and (not m.category or category.lower() not in m.category.lower()):
            continue
        if q and q.lower() not in m.name.lower():
            continue
        results.append(entry)

    return results[:limit]


@router.get("/categories")
def list_categories():
    """Return all distinct material type categories."""
    library = _load_library()
    cats = sorted({(m.get("material_type") or "Chemical").strip() for m in library})
    return cats


@router.post("")
def create_material(material: Material, session: Session = Depends(get_session)):
    """Add a custom material to the library."""
    material.is_custom = True
    session.add(material)
    session.commit()
    session.refresh(material)
    return material


@router.get("/templates")
def list_templates():
    """List available process templates."""
    templates_dir = _DATA_DIR / "process_templates"
    results = []
    if not templates_dir.exists():
        return results
    for f in sorted(templates_dir.glob("*.json")):
        with open(f, encoding="utf-8") as fp:
            data = json.load(fp)
        results.append({
            "id": data["id"],
            "name": data["name"],
            "description": data["description"],
            "category": data.get("category", ""),
            "example_catalysts": data.get("example_catalysts", []),
            "steps": data.get("steps", []),
        })
    return results


@router.get("/templates/{template_id}")
def get_template(template_id: str):
    """Get a specific process template."""
    path = _DATA_DIR / "process_templates" / f"{template_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


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
