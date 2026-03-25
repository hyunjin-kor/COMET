"""Metal price schemas."""

from datetime import datetime

from pydantic import BaseModel


class MetalPriceResponse(BaseModel):
    symbol: str
    name: str
    price: float
    unit: str
    source: str
    source_type: str
    is_live: bool
    fetched_at: datetime | None


class MetalPriceHistoryResponse(BaseModel):
    symbol: str
    name: str
    current_price: float
    unit: str
    history: list[MetalPriceResponse]
