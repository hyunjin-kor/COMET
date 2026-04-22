"""Pydantic schemas for saved-estimate catalog endpoints."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class EstimateSummary(BaseModel):
    """Compact saved-estimate metadata used by the catalog list."""

    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    description: str
    catalyst_domain: str
    application_family: str
    calculation_model: str
    metal_symbol: str
    metal_loading_wt_pct: float
    support_name: str
    order_size_tons: float
    estimated_price_per_lb: float
    created_at: str


class EstimateDetail(EstimateSummary):
    """Expanded saved-estimate payload including stored request/result JSON."""

    input: dict[str, Any]
    result: dict[str, Any]
