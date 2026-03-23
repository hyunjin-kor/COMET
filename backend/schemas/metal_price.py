"""Metal price schemas."""

from datetime import datetime

from pydantic import BaseModel


class MetalPriceResponse(BaseModel):
    symbol: str
    name: str
    price: float
    unit: str
    source: str
    fetched_at: datetime


class MetalPriceHistoryResponse(BaseModel):
    symbol: str
    name: str
    current_price: float
    unit: str
    history: list[MetalPriceResponse]
