"""Pydantic schemas for custom material library operations."""

from pydantic import BaseModel, ConfigDict, Field


class MaterialCreate(BaseModel):
    """Payload used to create a custom material row."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    formula: str | None = None
    category: str = Field(min_length=1)
    symbol: str | None = None
    mw: float | None = None
    density: float | None = None
    concentration_pct: float | None = None
    price: float = Field(default=0.0, ge=0)
    price_unit: str = "$/lb"
    price_scope: str = "historical_bulk"
    pack_quantity: float | None = None
    pack_unit: str | None = None
    source: str = ""
    quote_year: int | None = None
    notes: str = ""
    has_lab_data: bool = False
    catalyst_domain: str = "thermal"
    application_family: str = "general"
    pricing_basis: str = ""
    reference_url: str = ""


class MaterialUpdate(BaseModel):
    """Partial payload used to update a custom material row."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1)
    formula: str | None = None
    category: str | None = Field(default=None, min_length=1)
    symbol: str | None = None
    mw: float | None = None
    density: float | None = None
    concentration_pct: float | None = None
    price: float | None = Field(default=None, ge=0)
    price_unit: str | None = None
    price_scope: str | None = None
    pack_quantity: float | None = None
    pack_unit: str | None = None
    source: str | None = None
    quote_year: int | None = None
    notes: str | None = None
    has_lab_data: bool | None = None
    catalyst_domain: str | None = None
    application_family: str | None = None
    pricing_basis: str | None = None
    reference_url: str | None = None
