"""Response schemas for cost calculation results."""

from pydantic import BaseModel


class MaterialComponentResult(BaseModel):
    role: str
    name: str
    wt_pct: float
    wt_frac: float
    price_per_lb: float
    precursor_markup: float
    cost_per_lb_cat: float
    cost_pct: float


class MaterialsCostResult(BaseModel):
    components: list[MaterialComponentResult]
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


class ElectrodeLayerResult(BaseModel):
    application_family: str
    active_area_cm2: float
    catalyst_loading_mg_cm2: float
    catalyst_mass_g: float
    catalyst_cost_usd: float
    ionomer_to_catalyst_ratio: float
    ionomer_pricing_mode: str
    ionomer_solids_mass_g: float
    ionomer_dispersion_volume_ml: float
    ionomer_cost_usd: float
    substrate_cost_usd: float
    membrane_cost_usd: float
    total_cost_usd: float
    cost_per_cm2_usd: float
    cost_per_m2_usd: float
    breakdown: list[dict]


class ProcessRouteSummary(BaseModel):
    template_id: str
    name: str
    catalyst_domain: str
    application_family: str
    manufacturing_mode: str
    preprocess: list[str]
    synthesis: list[str]
    postprocess: list[str]
    quality_gates: list[str]
    steps: list[str]
    route_note: str
    source: str
    reference_urls: list[str]


class CostCalculationResponse(BaseModel):
    input_summary: dict
    materials: MaterialsCostResult
    step_method: StepMethodResult
    spent_catalyst: SpentCatalystResult | None = None
    electrode_model: ElectrodeLayerResult | None = None
    route_summary: ProcessRouteSummary | None = None
    resolved_materials: list[dict] = []
    summary: CostSummary
