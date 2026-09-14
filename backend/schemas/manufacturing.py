"""User-entered, ordered manufacturing protocols and batch operating inputs."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProtocolModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class TemperatureSegment(ProtocolModel):
    target_c: float | None = Field(default=None, gt=-273.15)
    ramp_c_per_min: float | None = Field(default=None, gt=0)
    hold_h: float | None = Field(default=None, ge=0)
    ramp_power_kw: float | None = Field(default=None, ge=0)
    hold_power_kw: float | None = Field(default=None, ge=0)


class ProcessGas(ProtocolModel):
    name: str = Field(min_length=1, max_length=200)
    flow_l_per_min: float | None = Field(default=None, ge=0)
    duration_h: float | None = Field(default=None, ge=0)
    price_usd_per_m3: float | None = Field(default=None, ge=0)
    volume_basis: str = Field(default="", max_length=500)


class ManufacturingOperation(ProtocolModel):
    name: str = Field(min_length=1, max_length=200)
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


class ManufacturingProtocol(ProtocolModel):
    mode: Literal["record_only", "batch_cost"] = "record_only"
    finished_batch_mass_kg: float | None = Field(default=None, gt=0)
    electricity_usd_kwh: float | None = Field(default=None, ge=0)
    labor_usd_h: float | None = Field(default=None, ge=0)
    selling_margin_fraction: float = Field(default=0, ge=0, lt=1)
    source_note: str = Field(default="", max_length=4000)
    operations: list[ManufacturingOperation] = Field(min_length=1, max_length=100)
