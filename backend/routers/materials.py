"""Materials library API endpoints."""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.material import Material

router = APIRouter(prefix="/api/materials", tags=["materials"])

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_library() -> dict:
    """Load materials library from JSON."""
    with open(_DATA_DIR / "materials_library.json") as f:
        return json.load(f)


@router.get("")
def list_materials(
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    session: Session = Depends(get_session),
):
    """List materials from library + user-added entries."""
    library = _load_library()
    results = []

    # Add metals from library
    for symbol, info in library.get("metals", {}).items():
        entry = {
            "id": f"metal_{symbol}",
            "name": info["name"],
            "symbol": symbol,
            "formula": symbol,
            "category": "metal",
            "mw": info.get("mw"),
            "price": info.get("reference_price", 0),
            "price_unit": info.get("unit", "$/troy_oz"),
            "source": info.get("price_source", ""),
            "is_custom": False,
        }
        if category and category != "metal":
            continue
        if q and q.lower() not in entry["name"].lower() and q.lower() != symbol.lower():
            continue
        results.append(entry)

    # Add supports from library
    for key, info in library.get("supports", {}).items():
        entry = {
            "id": f"support_{key}",
            "name": info["name"],
            "symbol": key,
            "formula": info.get("formula"),
            "category": "support",
            "mw": info.get("mw"),
            "price": info.get("estimated_bulk_price_per_lb", 0),
            "price_unit": "$/lb",
            "source": "estimated",
            "is_custom": False,
        }
        if category and category != "support":
            continue
        if q and q.lower() not in entry["name"].lower() and q.lower() != key.lower():
            continue
        results.append(entry)

    # Add user-created materials from DB
    stmt = select(Material)
    if category:
        stmt = stmt.where(Material.category == category)
    db_materials = session.exec(stmt).all()
    for m in db_materials:
        entry = {
            "id": m.id,
            "name": m.name,
            "symbol": m.symbol,
            "formula": m.formula,
            "category": m.category,
            "mw": m.mw,
            "price": m.price,
            "price_unit": m.price_unit,
            "source": m.source,
            "is_custom": True,
        }
        if q and q.lower() not in entry["name"].lower():
            continue
        results.append(entry)

    return results


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
    for f in sorted(templates_dir.glob("*.json")):
        with open(f) as fp:
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
    with open(path) as f:
        return json.load(f)


@router.get("/steps")
def list_steps():
    """List all available processing steps with costs."""
    with open(_DATA_DIR / "step_library.json") as f:
        data = json.load(f)
    return data["steps"]
