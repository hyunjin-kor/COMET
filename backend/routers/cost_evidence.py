"""Local-only evidence records attached to existing saved-estimate JSON."""

import json
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.core.cost_evidence import summarize_observations
from backend.database import get_session
from backend.models.estimate import Estimate
from backend.schemas.cost_evidence import ActualCostObservation

router = APIRouter(prefix="/api/estimates", tags=["local cost evidence"])


def _record(estimate_id: int, session: Session) -> Estimate:
    record = session.get(Estimate, estimate_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Estimate not found")
    return record


@router.get("/{estimate_id}/observations")
def list_cost_observations(estimate_id: int, session: Session = Depends(get_session)):
    record = _record(estimate_id, session)
    return summarize_observations(record.get_input(), record.get_result())


@router.post("/{estimate_id}/observations", status_code=201)
def add_cost_observation(
    estimate_id: int,
    observation: ActualCostObservation,
    session: Session = Depends(get_session),
):
    record = _record(estimate_id, session)
    result = record.get_result()
    observations = result.setdefault("local_cost_observations", [])
    if len(observations) >= 500:
        raise HTTPException(status_code=422, detail="This saved estimate already has 500 local observations")
    observations.append({
        "id": str(uuid4()),
        "recorded_at": datetime.now(UTC).isoformat(),
        "observation": observation.model_dump(mode="json"),
    })
    record.result_json = json.dumps(result, ensure_ascii=False, allow_nan=False)
    session.add(record)
    session.commit()
    return summarize_observations(record.get_input(), result)
