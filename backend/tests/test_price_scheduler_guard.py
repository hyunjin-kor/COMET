"""The plausibility check that stands between a feed and the price table.

The two rejection cases are the two failures that actually reached the table:
aluminium quoted per metric ton instead of per pound, and a rhodium parse
failure pinned at 1001.0. Both are recorded in
`docs/paper/price_volatility_2026-09-02.json` under `dropped_outliers`.
"""

from datetime import UTC, datetime

import pytest

from backend.models.metal_price import MetalPrice
from backend.services.price_scheduler import check_price


def previous(symbol: str, price: float, unit: str, source: str = "Yahoo Finance (live)") -> MetalPrice:
    return MetalPrice(
        symbol=symbol,
        name=symbol,
        price=price,
        unit=unit,
        source=source,
        fetched_at=datetime.now(UTC),
    )


def test_unconverted_metric_ton_quote_is_rejected() -> None:
    """2026-03-24: ALI=F came through at the per-tonne price, ~2000x too high."""
    reason = check_price("Al", 3112.0, "$/lb", previous("Al", 1.5643, "$/lb"))
    assert reason is not None
    assert "3112" in reason


def test_parse_failure_constant_is_rejected() -> None:
    """2026-04-03: Kitco rhodium returned a fixed 1001.0 against a ~10500 book."""
    reason = check_price("Rh", 1001.0, "$/troy_oz", previous("Rh", 10500.0, "$/troy_oz", "Kitco (live)"))
    assert reason is not None
    assert "1001" in reason


@pytest.mark.parametrize("price", [1594.3, 2139.6, 1747.6])
def test_real_platinum_range_is_accepted(price: float) -> None:
    """The full spread the platinum feed actually produced must pass."""
    assert check_price("Pt", price, "$/troy_oz", previous("Pt", 1610.3, "$/troy_oz")) is None


def test_first_quote_for_a_symbol_is_accepted() -> None:
    assert check_price("Re", 1179.4, "$/lb", None) is None


@pytest.mark.parametrize("bad", [0.0, -5.0, float("nan"), float("inf")])
def test_non_positive_or_non_finite_is_always_rejected(bad: float) -> None:
    assert check_price("Cu", bad, "$/lb", None) is not None


def test_unit_change_skips_the_magnitude_check() -> None:
    """A deliberate unit switch must not be blocked forever by its own history."""
    assert check_price("Al", 3112.0, "$/metric_ton", previous("Al", 1.5643, "$/lb")) is None
