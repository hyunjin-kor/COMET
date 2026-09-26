"""Monte Carlo uncertainty analysis endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlmodel import Session

from backend.core.manufacturing_analysis import (
    manufacturing_variables,
    prepare_manufacturing_ranges,
    varied_manufacturing_protocol,
)
from backend.core.uncertainty import run_cost_request_monte_carlo, run_monte_carlo
from backend.database import get_session
from backend.routers.calculator import _estimate_from_context, _prepare_calculation_context
from backend.schemas.cost_input import CostCalculationRequest, PriceUnit
from backend.schemas.manufacturing_analysis import (
    ManufacturingRange,
    ManufacturingSensitivityRequest,
)

router = APIRouter(prefix="/api", tags=["uncertainty"])


class UncertaintyRequest(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, extra="forbid")

    calculation_input: CostCalculationRequest | None = None
    metal_symbol: str | None = None
    metal_price: float | None = Field(default=None, gt=0)
    metal_price_unit: PriceUnit = "$/troy_oz"
    metal_loading_wt_pct: float | None = Field(default=None, gt=0, le=100)
    support_name: str = "Al2O3"
    support_price_per_lb: float = Field(default=0.50, ge=0)
    steps: list[str] = ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"]
    order_size_tons: float = Field(default=10.0, gt=0)
    n_simulations: int = Field(default=1000, ge=100, le=10000)
    seed: int | None = Field(default=None, ge=0)
    uncertainties: dict[str, list[float]] | None = None
    manufacturing_ranges: list[ManufacturingRange] = Field(default_factory=list, max_length=40)

    @model_validator(mode="after")
    def validate_payload(self) -> "UncertaintyRequest":
        if self.manufacturing_ranges and self.calculation_input is None:
            raise ValueError("Manufacturing ranges require calculation_input")
        if self.uncertainties:
            supported = ({"active_component_price", "promoter_price", "support_price",
                          "electrode_adjunct_price", "order_size_tons"} if self.calculation_input is not None
                         else {"metal_price", "support_price_per_lb", "order_size_tons", "metal_loading_wt_pct"})
            unknown = set(self.uncertainties) - supported
            if unknown:
                raise ValueError(f"Unsupported uncertainty parameters: {', '.join(sorted(unknown))}")
            for name, bounds in self.uncertainties.items():
                if len(bounds) != 2:
                    raise ValueError(
                        f"Uncertainty '{name}' must provide exactly two values: [low, high]"
                    )
                low, high = bounds
                if low <= 0 or high <= 0:
                    raise ValueError(
                        f"Uncertainty '{name}' must use strictly positive bounds"
                    )
                if low > high:
                    raise ValueError(
                        f"Uncertainty '{name}' must be a nondecreasing pair [low, high]"
                    )

        if self.calculation_input is not None:
            return self
        required = {
            "metal_symbol": self.metal_symbol,
            "metal_price": self.metal_price,
            "metal_loading_wt_pct": self.metal_loading_wt_pct,
        }
        missing = [name for name, value in required.items() if value in (None, "")]
        if missing:
            raise ValueError(
                "calculation_input is required unless legacy uncertainty fields are provided: "
                + ", ".join(missing)
            )
        return self


@router.post("/uncertainty")
def uncertainty_analysis(
    req: UncertaintyRequest,
    session: Session = Depends(get_session),
):
    """Run Monte Carlo simulation on cost estimation."""
    uncertainties = None
    if req.uncertainties is not None:
        uncertainties = {k: tuple(v) for k, v in req.uncertainties.items()}

    try:
        if req.calculation_input is not None:
            context = _prepare_calculation_context(req.calculation_input, session)
            return run_cost_request_monte_carlo(
                req=req.calculation_input,
                context=context,
                uncertainties=uncertainties,
                n_simulations=req.n_simulations,
                seed=req.seed,
                manufacturing_ranges=req.manufacturing_ranges,
            )

        base_params = {
            "metal_symbol": req.metal_symbol,
            "metal_price": req.metal_price,
            "metal_price_unit": req.metal_price_unit,
            "metal_loading_wt_pct": req.metal_loading_wt_pct,
            "support_name": req.support_name,
            "support_price_per_lb": req.support_price_per_lb,
            "steps": req.steps,
            "order_size_tons": req.order_size_tons,
        }
        result = run_monte_carlo(
            base_params=base_params,
            uncertainties=uncertainties,
            n_simulations=req.n_simulations,
            seed=req.seed,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/uncertainty/manufacturing-inputs")
def list_manufacturing_inputs(req: CostCalculationRequest, session: Session = Depends(get_session)):
    try:
        result = _estimate_from_context(req, _prepare_calculation_context(req, session))
        report = result.get("manufacturing")
        variables = manufacturing_variables(report)
        return {"variables": variables, "protocol_sha256": report["trace"]["protocol_sha256"]}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/uncertainty/manufacturing-sensitivity")
def manufacturing_sensitivity(req: ManufacturingSensitivityRequest, session: Session = Depends(get_session)):
    try:
        original = req.calculation_input
        context = _prepare_calculation_context(original, session)
        baseline = _estimate_from_context(original, context)
        analysis = prepare_manufacturing_ranges(baseline.get("manufacturing"), req.manufacturing_ranges)
        analysis.update(calculation_input=original.model_dump(mode="json"), resolved_context=context)
        key = "net_cost_per_kg" if original.include_spent_value else "estimated_price_per_kg"
        rows = []
        for variable in analysis["variables"]:
            row = dict(variable)
            for endpoint in ("low", "high"):
                try:
                    changed = varied_manufacturing_protocol(original.manufacturing_protocol, {variable["path"]: variable[endpoint]})
                    result = _estimate_from_context(original.model_copy(update={"manufacturing_protocol": changed}), context)
                    row[endpoint + "_usd_kg"] = result["summary"][key]
                    row[endpoint + "_error"] = None
                except ValueError as exc:
                    row[endpoint + "_usd_kg"] = None
                    row[endpoint + "_error"] = str(exc)
            rows.append(row)
        return {**analysis, "rows": rows, "baseline_usd_kg": baseline["summary"][key], "unit": "USD/kg",
                "metric": "selling_price_less_recovery" if original.include_spent_value else "selling_price",
                "method": "One input at a time; all other baseline values remain fixed. Endpoint changes are scenarios, not confidence intervals."}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
