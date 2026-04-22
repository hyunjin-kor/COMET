"""Saved-estimate catalog API endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from backend.database import get_session
from backend.models.estimate import Estimate
from backend.schemas.estimate import EstimateDetail, EstimateSummary

router = APIRouter(prefix="/api/estimates", tags=["estimates"])


def _iso_utc(value: datetime) -> str:
    """Serialize datetimes as explicit UTC ISO-8601 strings."""

    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat()


def _serialize_summary(record: Estimate) -> EstimateSummary:
    """Normalize one saved estimate into the shared catalog response shape."""

    return EstimateSummary(
        id=record.id,
        name=record.name,
        description=record.description,
        catalyst_domain=record.catalyst_domain,
        application_family=record.application_family,
        calculation_model=record.calculation_model,
        metal_symbol=record.metal_symbol,
        metal_loading_wt_pct=record.metal_loading_wt_pct,
        support_name=record.support_name,
        order_size_tons=record.order_size_tons,
        estimated_price_per_lb=record.estimated_price_per_lb,
        created_at=_iso_utc(record.created_at),
    )


def _get_estimate_or_404(estimate_id: int, session: Session) -> Estimate:
    """Load one saved estimate row or raise a 404."""

    record = session.get(Estimate, estimate_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Estimate not found")
    return record


@router.get("", response_model=list[EstimateSummary])
def list_estimates(
    q: str | None = Query(default=None),
    catalyst_domain: str | None = Query(default=None),
    limit: int = Query(default=100, le=500),
    session: Session = Depends(get_session),
):
    """List saved estimates newest-first with optional lightweight filters."""

    stmt = select(Estimate)
    if q:
        stmt = stmt.where(Estimate.name.ilike(f"%{q}%"))
    if catalyst_domain:
        stmt = stmt.where(Estimate.catalyst_domain == catalyst_domain.strip().lower())
    stmt = stmt.order_by(Estimate.created_at.desc(), Estimate.id.desc()).limit(limit)
    records = session.exec(stmt).all()
    return [_serialize_summary(record) for record in records]


@router.get("/{estimate_id}", response_model=EstimateDetail)
def get_estimate(
    estimate_id: int,
    session: Session = Depends(get_session),
):
    """Return the saved input/result payloads for one estimate."""

    record = _get_estimate_or_404(estimate_id, session)
    summary = _serialize_summary(record)
    return EstimateDetail(
        **summary.model_dump(),
        input=record.get_input(),
        result=record.get_result(),
    )


@router.delete("/{estimate_id}")
def delete_estimate(
    estimate_id: int,
    session: Session = Depends(get_session),
):
    """Delete a saved estimate by numeric identifier."""

    record = _get_estimate_or_404(estimate_id, session)
    session.delete(record)
    session.commit()
    return {"status": "deleted", "id": estimate_id}
