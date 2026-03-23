"""Material library item model."""

from sqlmodel import Field, SQLModel


class Material(SQLModel, table=True):
    """Raw material entry in the materials library."""

    __tablename__ = "materials"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    formula: str | None = None
    category: str = Field(index=True)  # "metal", "support", "solvent"
    symbol: str | None = None
    mw: float | None = None  # molecular weight
    price: float = 0.0
    price_unit: str = "$/lb"
    source: str = ""
    is_custom: bool = False  # user-added materials
