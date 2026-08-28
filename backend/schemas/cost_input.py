"""Request schemas for cost calculation endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.core.price_escalation import latest_index_year

PriceUnit = Literal["$/lb", "$/kg", "$/troy_oz"]
ApplicationFamily = Literal[
    "general",
    "fuel_cell",
    "direct_methanol_fuel_cell",
    "electrolyzer",
]


class ComponentInput(BaseModel):
    """One component of the catalyst formulation."""

    model_config = ConfigDict(extra="ignore")

    role: Literal["active_metal", "active_catalyst", "promoter", "support"] = "active_metal"
    material_key: str | None = Field(
        default=None,
        description="Optional materials-library key for DB-backed pricing.",
    )
    name: str | None = Field(
        default=None,
        description="Element symbol or material name (e.g. Pt, Al2O3)",
    )
    wt_pct: float = Field(..., gt=0, le=100, description="Weight percent in finished catalyst")
    price_per_lb: float | None = Field(default=None, ge=0, description="Price in $/lb")
    precursor_markup: float = Field(
        default=1.0, ge=1.0,
        description="Precursor conversion markup (1.0 = use pure metal price)",
    )

    @model_validator(mode="after")
    def validate_component(self) -> ComponentInput:
        if not self.material_key and not self.name:
            raise ValueError("Component requires either name or material_key")
        if self.price_per_lb is None and not self.material_key:
            raise ValueError("Component requires price_per_lb unless material_key is provided")
        return self


class ElectrodeCostInput(BaseModel):
    """Optional area-based coating model for electrocatalyst workflows."""

    model_config = ConfigDict(extra="ignore")

    application_family: ApplicationFamily = "general"
    catalyst_material_key: str | None = None
    ionomer_material_key: str | None = None
    substrate_material_key: str | None = None
    membrane_material_key: str | None = None
    active_area_cm2: float = Field(default=25.0, gt=0)
    catalyst_loading_mg_cm2: float = Field(default=0.5, gt=0)
    ionomer_to_catalyst_ratio: float = Field(
        default=0.0,
        ge=0,
        description="Dry ionomer mass divided by catalyst-powder mass.",
    )
    ionomer_price_per_ml: float = Field(default=0.0, ge=0)
    ionomer_price_per_kg_solids: float = Field(default=0.0, ge=0)
    ionomer_density_g_ml: float = Field(default=0.94, gt=0)
    ionomer_solids_fraction: float = Field(default=0.05, gt=0, le=1)
    substrate_cost_per_cm2: float = Field(default=0.0, ge=0)
    membrane_cost_per_cm2: float = Field(default=0.0, ge=0)
    manufacturing_scenario: Literal["rnd_batch", "pilot_roll_to_roll"] | None = Field(
        default=None,
        description=(
            "Adds an area-based MEA manufacturing (equipment, labor, facility) cost "
            "derived from Hog et al. 2026; consumables stay priced as materials."
        ),
    )


class CostCalculationRequest(BaseModel):
    """Input for POST /api/calculate.

    Components must include at least one active_metal. Supports are optional
    for electrocatalyst workflows such as unsupported Pt black or purchased
    Pt/C powders that are modeled as finished catalyst materials.
    The wt_pct values are automatically normalized to 100 % inside the engine,
    so you do not need to pre-normalize (though it is good practice).
    """

    model_config = ConfigDict(extra="ignore")

    components: list[ComponentInput] | None = Field(
        default=None,
        min_length=1,
        description="List of catalyst components (active metals, promoters, support)",
    )
    metal_symbol: str | None = None
    metal_price: float | None = Field(default=None, gt=0)
    metal_price_unit: PriceUnit = "$/troy_oz"
    metal_loading_wt_pct: float | None = Field(default=None, gt=0, le=100)
    support_name: str | None = None
    support_price_per_lb: float = Field(default=0.50, ge=0)
    precursor_metal_fraction: float = Field(default=1.0, gt=0, le=1)
    precursor_markup: float = Field(default=1.0, ge=1.0)
    steps: list[str] = Field(
        default=["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
        description="Processing step keys from the Step Library",
    )
    catalyst_domain: Literal["thermal", "electrocatalyst"] = Field(default="thermal")
    application_family: ApplicationFamily = Field(default="general")
    template_id: str | None = None
    order_size_tons: float = Field(default=10.0, gt=0)
    ga_overhead_pct: float = Field(default=0.05, ge=0, le=1)
    sard_pct: float = Field(default=0.05, ge=0, le=1)
    basis_year: int = Field(default=2017)
    target_year: int = Field(default_factory=lambda: latest_index_year("chemppi"))
    include_spent_value: bool = Field(default=False)
    reactor_type: str = Field(default="fixed")
    catalyst_bulk_density: float = Field(default=50.0, gt=0)
    electrode_input: ElectrodeCostInput | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> CostCalculationRequest:
        if self.components:
            if self.catalyst_domain == "thermal" and len(self.components) > 10:
                raise ValueError("Thermal workflows support at most ten total components")
            return self

        if (
            self.catalyst_domain == "electrocatalyst"
            and self.electrode_input is not None
            and self.electrode_input.catalyst_material_key
        ):
            return self

        required = {
            "metal_symbol": self.metal_symbol,
            "metal_price": self.metal_price,
            "metal_loading_wt_pct": self.metal_loading_wt_pct,
        }
        if not (
            self.catalyst_domain == "electrocatalyst"
            and self.metal_loading_wt_pct == 100
            and self.support_name in (None, "")
        ):
            required["support_name"] = self.support_name
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
        assert self.metal_loading_wt_pct is not None
        support_wt = max(0.0, 100.0 - self.metal_loading_wt_pct)
        components = [
            {
                "role": "active_metal",
                "name": self.metal_symbol,
                "wt_pct": self.metal_loading_wt_pct,
                "price_per_lb": 0.0,
                "precursor_markup": self.precursor_markup,
            }
        ]
        if self.support_name is not None and support_wt > 0:
            components.append({
                "role": "support",
                "name": self.support_name,
                "wt_pct": support_wt,
                "price_per_lb": self.support_price_per_lb,
                "precursor_markup": 1.0,
            })
        return components


class QuickCalculationRequest(BaseModel):
    """Simplified single-metal input for POST /api/calculate/quick."""

    model_config = ConfigDict(extra="ignore")

    metal_symbol: str = Field(..., min_length=1, max_length=64)
    metal_price: float = Field(..., gt=0)
    metal_price_unit: PriceUnit = "$/troy_oz"
    metal_loading_wt_pct: float = Field(..., gt=0, le=100)
    support_name: str = Field(default="Al2O3", min_length=1, max_length=128)
    support_price_per_lb: float = Field(default=0.50, ge=0)
    catalyst_domain: Literal["thermal", "electrocatalyst"] = "thermal"
    application_family: ApplicationFamily = "general"
    order_size_tons: float = Field(default=10.0, gt=0)
    template_id: str | None = None
