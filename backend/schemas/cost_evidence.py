"""User-supplied, local purchase and production evidence.

These records are not independently verified observations or library prices.
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PurchaseEvidence(BaseModel):
    """Optional provenance attached to an explicitly entered component price."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    supplier: str | None = Field(default=None, max_length=300)
    quote_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    quantity: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    quantity_unit: str | None = Field(default=None, max_length=40)
    grade: str | None = Field(default=None, max_length=300)
    cost_boundary: str | None = Field(default=None, max_length=500)
    reference: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("quote_date")
    @classmethod
    def valid_quote_date(cls, value: str | None) -> str | None:
        if value is not None:
            date.fromisoformat(value)
        return value


class ObservedComponent(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    wt_pct: float = Field(gt=0, le=100, allow_inf_nan=False)
    grade: str | None = Field(default=None, max_length=300)


class ActualCostObservation(BaseModel):
    """An observed price plus the conditions needed for a defensible comparison."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    observed_price: float = Field(gt=0, allow_inf_nan=False)
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    price_unit: Literal["lb", "kg", "cm2"] = "kg"
    observation_date: date
    price_period: str | None = Field(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    order_size_tons: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    production_rate_ton_per_day: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    components: list[ObservedComponent] = Field(default_factory=list, max_length=20)
    template_id: str | None = Field(default=None, max_length=200)
    steps: list[str] = Field(default_factory=list, max_length=100)
    cost_boundary: Literal[
        "material_purchase", "full_manufacturing_cost", "full_selling_price",
        "full_net_after_recovery", "other",
    ] = "material_purchase"
    cost_scope_note: str = Field(default="", max_length=2000)
    production_conditions_note: str = Field(default="", max_length=2000)
    source: str = Field(min_length=3, max_length=1000)
    evidence_type: Literal[
        "supplier_quote", "invoice", "production_record", "public_literature", "other",
    ] = "supplier_quote"
    verified_by_user: bool = False
    notes: str = Field(default="", max_length=2000)
