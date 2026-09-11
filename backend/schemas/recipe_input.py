"""Optional, user-supplied mass consumption per kg of finished thermal catalyst."""

from pydantic import BaseModel, ConfigDict, Field


class PrecursorConsumption(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, str_strip_whitespace=True)

    precursor_name: str = Field(min_length=1, max_length=200)
    retained_component_fraction: float = Field(gt=0, le=1)
    purity_fraction: float = Field(gt=0, le=1)
    yield_fraction: float = Field(gt=0, le=1)
    price_per_kg: float = Field(ge=0)
    source_note: str = Field(min_length=1, max_length=2000)


class ConsumableInput(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False, str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=200)
    kg_per_kg_catalyst: float = Field(gt=0)
    price_per_kg: float = Field(ge=0)
    source_note: str = Field(min_length=1, max_length=2000)
