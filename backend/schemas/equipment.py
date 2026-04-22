"""Pydantic schemas for custom equipment library operations."""

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EquipmentBase(BaseModel):
    """Shared request/response fields for equipment entries."""

    model_config = ConfigDict(extra="forbid")

    category: str = Field(min_length=1)
    name: str = Field(min_length=1)
    size_units: str = Field(min_length=1)
    s_lower: float | None = None
    s_upper: float | None = None
    a: float | None = None
    b: float | None = None
    n: float | None = None
    c: float | None = None
    d: float | None = None
    function_type: str = Field(min_length=1)
    source: str = "user"
    cepci_basis: float | None = None
    nf_refinery_basis: float | None = None
    year: int | None = None
    pricing_basis: str = ""
    installation_factor: float = 1.0
    labor_factor: float = 0.0
    note: str = ""
    materials: list[str] = Field(default_factory=list)
    material_factors: list[float] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_material_metadata(self) -> "EquipmentBase":
        if self.material_factors and len(self.materials) != len(self.material_factors):
            raise ValueError("materials and material_factors must have the same length")
        return self


class EquipmentCreate(EquipmentBase):
    """Payload used to create a custom equipment row."""


class EquipmentUpdate(BaseModel):
    """Partial payload used to update a custom equipment row."""

    model_config = ConfigDict(extra="forbid")

    category: str | None = Field(default=None, min_length=1)
    name: str | None = Field(default=None, min_length=1)
    size_units: str | None = Field(default=None, min_length=1)
    s_lower: float | None = None
    s_upper: float | None = None
    a: float | None = None
    b: float | None = None
    n: float | None = None
    c: float | None = None
    d: float | None = None
    function_type: str | None = Field(default=None, min_length=1)
    source: str | None = None
    cepci_basis: float | None = None
    nf_refinery_basis: float | None = None
    year: int | None = None
    pricing_basis: str | None = None
    installation_factor: float | None = None
    labor_factor: float | None = None
    note: str | None = None
    materials: list[str] | None = None
    material_factors: list[float] | None = None

    @model_validator(mode="after")
    def validate_material_metadata(self) -> "EquipmentUpdate":
        if (self.materials is None) != (self.material_factors is None):
            raise ValueError("materials and material_factors must be provided together")
        if self.materials is not None and self.material_factors is not None:
            if len(self.materials) != len(self.material_factors):
                raise ValueError("materials and material_factors must have the same length")
        return self


class EquipmentResponse(EquipmentBase):
    """Serialized equipment payload returned by the dedicated API."""

    model_config = ConfigDict(from_attributes=True)

    id: int | str
    is_custom: bool = True
