"""Request and response schemas for the CapEx & OpEx Factors workspace."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EquipmentScalingItem(BaseModel):
    """One equipment line scaled via the power-law six-tenths rule."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., min_length=1, max_length=120)
    base_cost_usd: float = Field(..., gt=0, description="Known purchased cost at base size, in USD.")
    base_size: float = Field(..., gt=0)
    target_size: float = Field(..., gt=0)
    exponent: float = Field(default=0.6, gt=0, le=1.5)
    quantity: int = Field(default=1, ge=1, le=50)


class OpExInputs(BaseModel):
    """Optional OpEx inputs layered on top of CapEx output."""

    model_config = ConfigDict(extra="ignore")

    direct_labor_cost_usd: float = Field(default=0.0, ge=0)
    raw_materials_cost_usd: float = Field(default=0.0, ge=0)
    utilities_cost_usd: float = Field(default=0.0, ge=0)


class CapExRequest(BaseModel):
    """Input for POST /api/capex.

    Two ways to declare purchased-equipment cost:
      1. ``purchased_equipment_cost_usd`` — already-summed lump value.
      2. ``equipment`` — list of items that the engine scales and sums via the
         six-tenths rule.

    At least one path must be populated.
    """

    model_config = ConfigDict(extra="ignore")

    purchased_equipment_cost_usd: float | None = Field(default=None, ge=0)
    equipment: list[EquipmentScalingItem] | None = Field(
        default=None, max_length=50, description="Equipment lines scaled via the six-tenths rule."
    )
    opex_inputs: OpExInputs | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> CapExRequest:
        has_lump = self.purchased_equipment_cost_usd is not None and self.purchased_equipment_cost_usd > 0
        has_items = self.equipment is not None and len(self.equipment) > 0
        if not (has_lump or has_items):
            raise ValueError(
                "Provide either purchased_equipment_cost_usd or a non-empty equipment list."
            )
        return self


class EquipmentResolution(BaseModel):
    """Per-line scaling result for the engineering audit trail."""

    name: str
    base_cost_usd: float
    base_size: float
    target_size: float
    exponent: float
    quantity: int
    scaled_unit_cost_usd: float
    line_total_usd: float


class CapExBreakdown(BaseModel):
    """Itemised capital-cost breakdown returned by the engine."""

    purchased_equipment: float
    installation: float
    instrumentation: float
    piping: float
    electrical: float
    buildings: float
    yard_improvements: float
    service_facilities: float
    land: float
    engineering_supervision: float
    construction: float
    legal: float
    contractors_fee: float
    contingency: float
    direct_capital: float
    indirect_capital: float
    fixed_capital_investment: float
    working_capital: float
    total_capital_investment: float


class OpExBreakdown(BaseModel):
    """Itemised annual operating expense breakdown."""

    raw_materials: float
    direct_labor: float
    supervisory_clerical: float
    utilities: float
    laboratory: float
    maintenance_repair: float
    operating_supplies: float
    direct_operating_total: float
    local_taxes: float
    insurance: float
    rent: float
    plant_overhead: float
    fixed_operating_total: float
    administration: float
    distribution_marketing: float
    rnd: float
    general_expenses_total: float
    total_annual_opex: float


class CapExResult(BaseModel):
    """Response payload of POST /api/capex."""

    purchased_equipment_cost_usd: float
    equipment_resolution: list[EquipmentResolution]
    capex: CapExBreakdown
    opex: OpExBreakdown | None
    summary: dict
