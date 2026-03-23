"""Saved cost estimate model."""

import json
from datetime import datetime

from sqlmodel import Column, Field, SQLModel, Text


class Estimate(SQLModel, table=True):
    """Saved catalyst cost estimation result."""

    __tablename__ = "estimates"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = ""
    metal_symbol: str = ""
    metal_loading_wt_pct: float = 0.0
    support_name: str = ""
    order_size_tons: float = 0.0
    estimated_price_per_lb: float = 0.0
    input_json: str = Field(default="{}", sa_column=Column(Text))
    result_json: str = Field(default="{}", sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def get_input(self) -> dict:
        return json.loads(self.input_json)

    def get_result(self) -> dict:
        return json.loads(self.result_json)
