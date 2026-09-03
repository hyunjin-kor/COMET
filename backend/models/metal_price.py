"""Metal price history model."""

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlmodel import Column, Field, SQLModel

# "live" is what the app shows day to day (daily feeds plus anchors);
# "reference" is the academic basis: institutional monthly averages, one row
# per symbol and month, dated at month end.
PRICE_BASES = ("live", "reference")


class MetalPrice(SQLModel, table=True):
    """Historical metal price record."""

    __tablename__ = "metal_prices"

    id: int | None = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    name: str
    price: float
    unit: str  # "$/troy_oz" or "$/lb"
    source: str  # API source name
    basis: str = Field(default="live", index=True)
    fetched_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
