"""Metal price history model."""

from datetime import datetime

from sqlmodel import Field, SQLModel


class MetalPrice(SQLModel, table=True):
    """Historical metal price record."""

    __tablename__ = "metal_prices"

    id: int | None = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    name: str
    price: float
    unit: str  # "$/troy_oz" or "$/lb"
    source: str  # API source name
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
