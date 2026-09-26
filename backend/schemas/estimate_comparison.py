"""Explicit common conditions for comparison of saved complete estimates."""

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.schemas.cost_input import PriceBasis


class EstimateComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    estimate_ids: list[int] = Field(min_length=2, max_length=4)
    reference_estimate_id: int = Field(gt=0)
    price_basis: PriceBasis
    order_size_tons: float = Field(gt=0)

    @model_validator(mode="after")
    def validate_selection(self):
        if len(set(self.estimate_ids)) != len(self.estimate_ids):
            raise ValueError("Select distinct saved estimates")
        if any(value <= 0 for value in self.estimate_ids):
            raise ValueError("Estimate identifiers must be positive")
        if self.reference_estimate_id not in self.estimate_ids:
            raise ValueError("The reference estimate must be selected")
        return self
