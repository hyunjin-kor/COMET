"""Material library item model."""

from sqlmodel import Field, SQLModel


class Material(SQLModel, table=True):
    """Raw material entry in the materials library."""

    __tablename__ = "materials"

    id: int | None = Field(default=None, primary_key=True)
    library_key: str | None = Field(default=None, index=True)
    name: str = Field(index=True)
    formula: str | None = None
    category: str = Field(index=True)  # "metal", "support", "solvent"
    symbol: str | None = None
    mw: float | None = None  # molecular weight
    density: float | None = None
    concentration_pct: float | None = None
    price: float = 0.0
    price_unit: str = "$/lb"
    price_scope: str = "historical_bulk"
    pack_quantity: float | None = None
    pack_unit: str | None = None
    source: str = ""
    quote_year: int | None = None
    notes: str = ""
    has_lab_data: bool = False
    catalyst_domain: str = Field(default="thermal", index=True)
    application_family: str = Field(default="general", index=True)
    pricing_basis: str = ""
    reference_url: str = ""
    is_custom: bool = False  # user-added materials
