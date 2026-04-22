"""Custom equipment library item model."""

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


class Equipment(SQLModel, table=True):
    """User-defined equipment entry layered on top of the bundled library."""

    __tablename__ = "equipment"

    id: int | None = Field(default=None, primary_key=True)
    category: str = Field(index=True)
    name: str = Field(index=True)
    size_units: str
    s_lower: float | None = None
    s_upper: float | None = None
    a: float | None = None
    b: float | None = None
    n: float | None = None
    c: float | None = None
    d: float | None = None
    function_type: str
    source: str = "user"
    cepci_basis: float | None = None
    nf_refinery_basis: float | None = None
    year: int | None = None
    pricing_basis: str = ""
    installation_factor: float = 1.0
    labor_factor: float = 0.0
    note: str = ""
    materials: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    material_factors: list[float] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    is_custom: bool = Field(default=True, index=True)
