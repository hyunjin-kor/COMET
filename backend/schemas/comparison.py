"""Schemas for the multi-composition comparison endpoint."""

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.cost_input import PriceUnit


class CompareCompositionInput(BaseModel):
    """One composition submitted to the comparison endpoint."""

    model_config = ConfigDict(allow_inf_nan=False)

    label: str = ""
    metal_symbol: str
    metal_price: float = Field(gt=0)
    metal_price_unit: PriceUnit = "$/troy_oz"
    metal_loading_wt_pct: float = Field(gt=0, le=100)
    support_name: str = "Al2O3"
    support_price_per_lb: float = Field(default=0.50, ge=0)
    steps: list[str] = ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"]
    order_size_tons: float = Field(default=10.0, gt=0)


class CompareRequest(BaseModel):
    """Request payload for POST /api/compare."""

    compositions: list[CompareCompositionInput] = Field(..., min_length=2, max_length=4)


class CompareCompositionResult(BaseModel):
    """One row returned from the comparison endpoint."""

    index: int
    label: str
    metal_symbol: str
    metal_loading_wt_pct: float
    support_name: str
    order_size_tons: float
    estimated_price_per_lb: float
    estimated_price_per_kg: float
    materials_cost_per_lb: float
    processing_cost_per_lb: float
    materials_pct: float
    processing_pct: float
    scale: str


class CompareResponse(BaseModel):
    """Response payload for POST /api/compare."""

    compositions: list[CompareCompositionResult]
