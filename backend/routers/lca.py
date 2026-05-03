"""LCA endpoints — read-only access to the cradle-to-gate impact dataset."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from backend.core.lca import compute_catalyst_lca, list_factors

router = APIRouter(prefix="/api/lca", tags=["lca"])


class LcaComponentInput(BaseModel):
    """One catalyst component for an ad-hoc LCA query."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., min_length=1, max_length=128)
    wt_pct: float = Field(..., gt=0, le=100)
    role: str | None = None


class LcaRequest(BaseModel):
    """Request body for POST /api/lca/calculate."""

    model_config = ConfigDict(extra="ignore")

    components: list[LcaComponentInput] = Field(..., min_length=1, max_length=20)


@router.get("/factors")
def get_lca_factors():
    """Return the full LCA factor dataset and its citation."""
    return list_factors()


@router.post("/calculate")
def calculate_lca(req: LcaRequest):
    """Compute cradle-to-gate impact per kg of finished catalyst.

    Reuses the same engine the main /api/calculate endpoint embeds, so the
    numbers are consistent between the cost panel and standalone queries.
    """
    components = [c.model_dump() for c in req.components]
    try:
        return compute_catalyst_lca(components)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="LCA dataset is not available") from exc
