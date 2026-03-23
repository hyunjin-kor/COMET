"""Response schemas for cost calculation results."""

from pydantic import BaseModel


class MaterialsCostResult(BaseModel):
    metal_precursor_cost_per_lb: float
    support_cost_per_lb: float
    solvent_cost_per_lb: float
    total_materials_cost_per_lb: float


class StepDetail(BaseModel):
    step: str
    hourly_cost: float


class StepMethodResult(BaseModel):
    scale: str
    order_size_tons: float
    campaign_days: float
    step_cost_per_hr: float
    chemppi_escalation: float
    campaign_cost: float
    total_production_lb: float
    materials_cost_per_lb: float
    processing_cost_per_lb: float
    subtotal_per_lb: float
    ga_per_lb: float
    sard_per_lb: float
    pre_margin_per_lb: float
    margin_pct: float
    margin_per_lb: float
    estimated_price_per_lb: float
    estimated_price_per_kg: float
    step_details: list[StepDetail]


class SpentCatalystResult(BaseModel):
    metal_symbol: str
    metal_loading_lb_per_lb: float
    loss_use_pct: float
    loss_refining_pct: float
    V_metal_per_lb: float
    C_recovery_per_lb: float
    V_reclaimed_per_lb: float


class CostSummary(BaseModel):
    estimated_price_per_lb: float
    estimated_price_per_kg: float
    net_cost_per_lb: float
    net_cost_per_kg: float
    materials_pct: float
    processing_pct: float


class CostCalculationResponse(BaseModel):
    input_summary: dict
    materials: MaterialsCostResult
    step_method: StepMethodResult
    spent_catalyst: SpentCatalystResult | None = None
    summary: CostSummary
