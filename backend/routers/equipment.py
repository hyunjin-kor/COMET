"""Dedicated equipment-library API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.equipment import Equipment
from backend.routers import materials
from backend.schemas.equipment import EquipmentCreate, EquipmentResponse, EquipmentUpdate

router = APIRouter(prefix="/api/equipment", tags=["equipment"])


def _custom_equipment_payload(record: Equipment) -> dict:
    """Serialize custom equipment rows into the API response shape."""

    return EquipmentResponse.model_validate(record).model_dump()


def _matches_filters(record: Equipment, category: str | None, q: str | None) -> bool:
    """Apply the same lightweight category/name filters used by the bundled list."""

    if category and category.lower() not in record.category.lower():
        return False
    if q and q.lower() not in record.name.lower():
        return False
    return True


@router.get("")
def list_equipment(
    category: str | None = Query(default=None),
    q: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
    session: Session = Depends(get_session),
):
    """List bundled equipment plus user-defined custom rows."""

    bundled = materials.list_equipment(category=category, q=q, limit=limit)
    custom_rows = session.exec(select(Equipment).order_by(Equipment.name)).all()
    custom_payload = [
        _custom_equipment_payload(record)
        for record in custom_rows
        if _matches_filters(record, category=category, q=q)
    ]
    return (bundled + custom_payload)[:limit]


@router.post("", response_model=EquipmentResponse)
def create_equipment(
    payload: EquipmentCreate,
    session: Session = Depends(get_session),
):
    """Create a custom equipment row for the dedicated library."""

    record = Equipment(**payload.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment(
    equipment_id: str,
    session: Session = Depends(get_session),
):
    """Get one custom or bundled equipment row by identifier."""

    return materials.get_equipment_detail(equipment_id, session)


@router.patch("/{equipment_id}", response_model=EquipmentResponse)
def update_equipment(
    equipment_id: int,
    payload: EquipmentUpdate,
    session: Session = Depends(get_session),
):
    """Patch mutable fields on a custom equipment row."""

    record = session.get(Equipment, equipment_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Equipment not found")

    for field_name, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field_name, value)

    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.delete("/{equipment_id}")
def delete_equipment(
    equipment_id: int,
    session: Session = Depends(get_session),
):
    """Delete a custom equipment row by numeric identifier."""

    record = session.get(Equipment, equipment_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Equipment not found")

    session.delete(record)
    session.commit()
    return {"status": "deleted", "id": equipment_id}
