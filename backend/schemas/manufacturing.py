"""User-entered, ordered manufacturing protocols and batch operating inputs."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProtocolModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, validate_default=True, str_strip_whitespace=True)


class InputEvidence(ProtocolModel):
    kind: Literal["literature", "measured", "supplier", "assumption"]
    citation: str = Field(min_length=1, max_length=1000)
    locator: str = Field(default="", max_length=500)
    url: str = Field(default="", max_length=1500)
    doi: str = Field(default="", max_length=250)
    accessed_on: str = Field(default="", max_length=30)
    recorded_value: float | str | bool | None = None
    note: str = Field(default="", max_length=2000)


class SourcedProtocolModel(ProtocolModel):
    input_evidence: dict[str, InputEvidence] = Field(default_factory=dict, max_length=100)

    @model_validator(mode="after")
    def valid_evidence_fields(self):
        for key in self.input_evidence:
            if key not in type(self).model_fields or key in {"input_evidence", "operations", "gases", "temperature_profile", "purchases", "intermediate_batches"}:
                raise ValueError(f"input_evidence must refer to a scalar input on this record: {key}")
        return self


class TemperatureSegment(SourcedProtocolModel):
    target_c: float | None = Field(default=None, gt=-273.15)
    ramp_c_per_min: float | None = Field(default=None, gt=0)
    hold_h: float | None = Field(default=None, ge=0)
    ramp_power_kw: float | None = Field(default=None, ge=0)
    hold_power_kw: float | None = Field(default=None, ge=0)


class ProcessGas(SourcedProtocolModel):
    name: str = Field(min_length=1, max_length=200)
    flow_l_per_min: float | None = Field(default=None, ge=0)
    duration_h: float | None = Field(default=None, ge=0)
    duration_basis: Literal["entered", "operation", "holds"] = "entered"
    price_usd_per_m3: float | None = Field(default=None, ge=0)
    volume_basis: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def one_duration_basis(self):
        if self.duration_basis != "entered" and self.duration_h is not None:
            raise ValueError("A linked gas duration cannot also specify an independent duration_h")
        return self


class BatchPurchase(SourcedProtocolModel):
    name: str = Field(min_length=1, max_length=200)
    quantity: float | None = Field(default=None, ge=0)
    unit: Literal["kg", "g", "L", "mL", "item"] = "kg"
    quantity_basis: Literal["entered", "solvent_volume"] = "entered"
    price_usd_per_unit: float | None = Field(default=None, ge=0)
    notes: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def linked_quantity(self):
        if self.quantity_basis == "solvent_volume" and (self.quantity is not None or self.unit != "mL"):
            raise ValueError("Solvent-volume purchases use the operation volume in mL, without an independent quantity")
        return self


class IntermediateBatch(SourcedProtocolModel):
    id: str = Field(min_length=1, max_length=150)
    name: str = Field(min_length=1, max_length=200)
    allocation_basis: Literal["mass_used", "whole_batch"] = "mass_used"
    produced_mass_kg: float | None = Field(default=None, gt=0)
    used_mass_kg: float | None = Field(default=None, gt=0)
    notes: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def usable_mass(self):
        if self.produced_mass_kg is not None and self.used_mass_kg is not None and self.used_mass_kg > self.produced_mass_kg:
            raise ValueError("Intermediate mass used cannot exceed recovered mass")
        return self


class ManufacturingOperation(SourcedProtocolModel):
    name: str = Field(min_length=1, max_length=200)
    intermediate_batch_id: str = Field(default="", max_length=150)
    equipment: str = Field(default="", max_length=300)
    atmosphere: str = Field(default="", max_length=300)
    pressure_bar_abs: float | None = Field(default=None, gt=0)
    stirring_rpm: float | None = Field(default=None, ge=0)
    ph: float | None = Field(default=None, ge=0, le=14)
    solvent: str = Field(default="", max_length=200)
    solvent_volume_ml: float | None = Field(default=None, ge=0)
    repetitions: int = Field(default=1, ge=1, le=1000)
    start_temperature_c: float | None = Field(default=None, gt=-273.15)
    temperature_profile: list[TemperatureSegment] = Field(default_factory=list, max_length=30)
    duration_h: float | None = Field(default=None, ge=0)
    additional_time_h: float | None = Field(default=None, ge=0)
    average_power_kw: float | None = Field(default=None, ge=0)
    additional_power_kw: float | None = Field(default=None, ge=0)
    measured_energy_kwh: float | None = Field(default=None, ge=0)
    energy_basis: Literal["power", "measured"] = "power"
    equipment_usd_h: float | None = Field(default=None, ge=0)
    attended_labor_h: float | None = Field(default=None, ge=0)
    other_cost_usd: float | None = Field(default=None, ge=0)
    gases: list[ProcessGas] = Field(default_factory=list, max_length=10)
    purchases: list[BatchPurchase] = Field(default_factory=list, max_length=30)
    notes: str = Field(default="", max_length=4000)

    @model_validator(mode="after")
    def distinct_time_and_energy_bases(self):
        if not self.name.strip():
            raise ValueError("Operation name cannot be blank")
        if self.temperature_profile and self.duration_h is not None:
            raise ValueError("Use either a temperature profile or a simple duration, not both")
        powers = [self.average_power_kw, self.additional_power_kw]
        powers += [p for s in self.temperature_profile for p in (s.ramp_power_kw, s.hold_power_kw)]
        if self.temperature_profile and self.average_power_kw is not None:
            raise ValueError("Temperature profiles use segment powers, not an overall average power")
        if (self.energy_basis == "measured" or self.measured_energy_kwh is not None) and any(p is not None for p in powers):
            raise ValueError("Use measured electricity or power-times-duration, not both")
        return self


class ManufacturingProtocol(SourcedProtocolModel):
    mode: Literal["record_only", "batch_cost"] = "record_only"
    product_basis: Literal["catalyst_powder", "electrode"] = "catalyst_powder"
    materials_basis: Literal["composition", "purchases"] = "composition"
    source_record_id: str = Field(default="", max_length=150)
    finished_batch_mass_kg: float | None = Field(default=None, gt=0)
    electricity_usd_kwh: float | None = Field(default=None, ge=0)
    labor_usd_h: float | None = Field(default=None, ge=0)
    selling_margin_fraction: float = Field(default=0, ge=0, lt=1)
    source_note: str = Field(default="", max_length=4000)
    intermediate_batches: list[IntermediateBatch] = Field(default_factory=list, max_length=30)
    operations: list[ManufacturingOperation] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def powder_cost_basis(self):
        if self.mode == "batch_cost" and self.product_basis != "catalyst_powder":
            raise ValueError("Electrode preparation records cannot use dry-powder batch costing")
        ids = [batch.id for batch in self.intermediate_batches]
        assigned = {op.intermediate_batch_id for op in self.operations if op.intermediate_batch_id}
        if len(ids) != len(set(ids)):
            raise ValueError("Intermediate batch identifiers must be unique")
        if assigned - set(ids):
            raise ValueError("Every operation must refer to a defined intermediate batch or the final batch")
        if set(ids) - assigned:
            raise ValueError("Every intermediate batch needs at least one assigned operation")
        if ids and all(op.intermediate_batch_id for op in self.operations):
            raise ValueError("At least one operation must belong to the final batch")
        return self
