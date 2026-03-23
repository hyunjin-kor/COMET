"""Request schemas for cost calculation endpoints."""

from pydantic import BaseModel, Field


class CostCalculationRequest(BaseModel):
    """Input for POST /api/calculate."""

    metal_symbol: str = Field(..., description="Metal element symbol (e.g. Pt, Ni)")
    metal_price: float = Field(..., gt=0, description="Metal spot price")
    metal_price_unit: str = Field(
        default="$/troy_oz", description="Price unit: $/troy_oz, $/lb, $/kg"
    )
    metal_loading_wt_pct: float = Field(
        ..., gt=0, le=100, description="Metal loading weight percent"
    )
    support_name: str = Field(..., description="Support material name")
    support_price_per_lb: float = Field(default=0.50, ge=0)
    precursor_metal_fraction: float = Field(default=1.0, gt=0, le=1)
    precursor_markup: float = Field(default=1.0, ge=1.0)
    steps: list[str] = Field(
        default=["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"]
    )
    order_size_tons: float = Field(default=10.0, gt=0)
    solvent_cost_per_lb_cat: float = Field(default=0.0, ge=0)
    ga_overhead_pct: float = Field(default=0.05, ge=0, le=1)
    sard_pct: float = Field(default=0.05, ge=0, le=1)
    basis_year: int = Field(default=2017)
    target_year: int = Field(default=2024)
    include_spent_value: bool = Field(default=False)
    reactor_type: str = Field(default="fixed")
    catalyst_bulk_density: float = Field(default=50.0, gt=0)


class QuickCalculationRequest(BaseModel):
    """Simplified input for POST /api/calculate/quick."""

    metal_symbol: str
    metal_price: float = Field(..., gt=0)
    metal_price_unit: str = "$/troy_oz"
    metal_loading_wt_pct: float = Field(..., gt=0, le=100)
    support_name: str = "Al2O3"
    support_price_per_lb: float = 0.50
    order_size_tons: float = 10.0
    template_id: str | None = None
