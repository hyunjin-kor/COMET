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
    basis: str = Query(default="live", pattern="^(live|reference)$"),
    session: Session = Depends(get_session),
):
    """Evaluate one optional benchmark family with the selected decision profile and price basis."""

    try:
        return evaluate_benchmark_family(session=session, family=family, profile=profile, basis=basis)
    except KeyError as exc:
        detail = exc.args[0] if exc.args else "Decision benchmark not found"
        raise HTTPException(status_code=404, detail=detail)
