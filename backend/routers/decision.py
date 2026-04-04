"""APIs for optional benchmark reference families."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from backend.core.decision_engine import evaluate_benchmark_family, list_benchmark_families
from backend.database import get_session

router = APIRouter(prefix="/api/decision", tags=["decision"])


@router.get("/benchmarks")
def get_benchmark_families():
    """List optional benchmark reference families available to the desktop app."""

    return {"families": list_benchmark_families()}


@router.get("/benchmarks/{family}")
def get_benchmark_family(
    family: str,
    profile: str = Query(default="balanced", pattern="^(balanced|cost-first|evidence-first)$"),
    session: Session = Depends(get_session),
):
    """Evaluate one optional benchmark family with the selected decision profile."""

    try:
        return evaluate_benchmark_family(session=session, family=family, profile=profile)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
