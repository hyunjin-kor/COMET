"""Request schemas for cost calculation endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ComponentInput(BaseModel):
    """One component of the catalyst formulation."""

    role: Literal["active_metal", "promoter", "support"] = "active_metal"
    name: str = Field(..., description="Element symbol or material name (e.g. Pt, Al2O3)")
    wt_pct: float = Field(..., gt=0, le=100, description="Weight percent in finished catalyst")
    price_per_lb: float = Field(..., ge=0, description="Price in $/lb")
    precursor_markup: float = Field(
        default=1.0, ge=1.0,
        description="Precursor conversion markup (1.0 = use pure metal price)",
    )


class CostCalculationRequest(BaseModel):
    """Input for POST /api/calculate.

    Components must include at least one active_metal and one support.
    The wt_pct values are automatically normalized to 100 % inside the engine,
    so you do not need to pre-normalize (though it is good practice).
    """

    components: list[ComponentInput] | None = Field(
        default=None, min_length=2,
        description="List of catalyst components (active metals, promoters, support)",
    )
    metal_symbol: str | None = None
    metal_price: float | None = Field(default=None, gt=0)
    metal_price_unit: str = "$/troy_oz"
    metal_loading_wt_pct: float | None = Field(default=None, gt=0, le=100)
    support_name: str | None = None
    support_price_per_lb: float = Field(default=0.50, ge=0)
    precursor_metal_fraction: float = Field(default=1.0, gt=0, le=1)
    precursor_markup: float = Field(default=1.0, ge=1.0)
    steps: list[str] = Field(
        default=["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
        description="Processing step keys from the Step Library",
    )
    order_size_tons: float = Field(default=10.0, gt=0)
    ga_overhead_pct: float = Field(default=0.05, ge=0, le=1)
    sard_pct: float = Field(default=0.05, ge=0, le=1)
    basis_year: int = Field(default=2017)
    target_year: int = Field(default=2024)
    include_spent_value: bool = Field(default=False)
    reactor_type: str = Field(default="fixed")
    catalyst_bulk_density: float = Field(default=50.0, gt=0)

    @model_validator(mode="after")
    def validate_payload(self) -> "CostCalculationRequest":
        if self.components:
            return self

        required = {
            "metal_symbol": self.metal_symbol,
            "metal_price": self.metal_price,
            "metal_loading_wt_pct": self.metal_loading_wt_pct,
            "support_name": self.support_name,
        }
        missing = [name for name, value in required.items() if value in (None, "")]
        if missing:
            raise ValueError(
                "components is required unless legacy fields are provided: "
                + ", ".join(missing)
            )
        return self

    def to_components(self) -> list[dict]:
        if self.components:
            return [component.model_dump() for component in self.components]

        assert self.metal_symbol is not None
        assert self.support_name is not None
        assert self.metal_loading_wt_pct is not None
        support_wt = 100.0 - self.metal_loading_wt_pct
        return [
            {
                "role": "active_metal",
                "name": self.metal_symbol,
                "wt_pct": self.metal_loading_wt_pct,
                "price_per_lb": 0.0,
                "precursor_markup": self.precursor_markup,
            },
            {
                "role": "support",
                "name": self.support_name,
                "wt_pct": support_wt,
                "price_per_lb": self.support_price_per_lb,
                "precursor_markup": 1.0,
            },
        ]


class QuickCalculationRequest(BaseModel):
    """Simplified single-metal input for POST /api/calculate/quick."""

    metal_symbol: str
    metal_price: float = Field(..., gt=0)
    metal_price_unit: str = "$/troy_oz"
    metal_loading_wt_pct: float = Field(..., gt=0, le=100)
    support_name: str = "Al2O3"
    support_price_per_lb: float = 0.50
    order_size_tons: float = 10.0
    template_id: str | None = None
