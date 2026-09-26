"""Absolute, user-specified bounds for manufacturing cost inputs."""

from pydantic import Field, model_validator

from backend.schemas.cost_input import CostCalculationRequest
from backend.schemas.manufacturing import ProtocolModel


class ManufacturingRange(ProtocolModel):
    path: str = Field(min_length=1, max_length=200)
    low: float
    high: float
    rationale: str = Field(default="", max_length=1000)

    @model_validator(mode="after")
    def ordered_bounds(self):
        if self.low > self.high:
            raise ValueError("Manufacturing bounds must be nondecreasing absolute values")
        return self


class ManufacturingSensitivityRequest(ProtocolModel):
    calculation_input: CostCalculationRequest
    manufacturing_ranges: list[ManufacturingRange] = Field(min_length=1, max_length=40)
