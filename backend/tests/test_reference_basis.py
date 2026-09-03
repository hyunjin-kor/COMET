"""The paper's reference price basis: monthly averaging and basis construction."""

import pytest

from backend.core.decision_engine import evaluate_benchmark_family
from backend.core.price_fetcher import get_reference_prices
from backend.core.reference_basis import (
    build_price_basis,
    latest_common_month,
    monthly_average,
    truncate_series,
)


def test_monthly_average_dates_at_month_end_and_skips_the_running_month():
    pts = [
        {"date": "2026-01-05", "price": 1.0},
        {"date": "2026-01-20", "price": 3.0},
        {"date": "2026-02-01", "price": 5.0},
        {"date": "2026-03-02", "price": 9.0},
    ]
    assert monthly_average(pts, exclude_month="2026-03") == [
        {"date": "2026-01-31", "price": 2.0},
        {"date": "2026-02-28", "price": 5.0},
    ]


def test_latest_common_month_is_the_intersection():
    series = {
        "Pt": {"points": [{"date": "2026-06-30"}, {"date": "2026-07-31"}, {"date": "2026-08-31"}]},
        "Co": {"points": [{"date": "2026-06-30"}, {"date": "2026-07-31"}]},
    }
    assert latest_common_month(series) == "2026-07"


def test_latest_common_month_raises_when_series_do_not_overlap():
    series = {"Pt": {"points": [{"date": "2026-08-31"}]}, "Co": {"points": [{"date": "2026-07-31"}]}}
    with pytest.raises(ValueError):
        latest_common_month(series)


def test_truncate_series_cuts_after_month_and_refreshes_summary():
    series = {
        "Pt": {
            "source": "s",
            "points": [{"date": "2026-06-30", "price": 1.0}, {"date": "2026-08-31", "price": 2.0}],
            "first": "2026-06-30",
            "last": "2026-08-31",
            "n": 2,
        }
    }
    cut = truncate_series(series, "2026-07")
    assert cut["Pt"]["points"] == [{"date": "2026-06-30", "price": 1.0}]
    assert (cut["Pt"]["first"], cut["Pt"]["last"], cut["Pt"]["n"]) == ("2026-06-30", "2026-06-30", 1)
    assert cut["Pt"]["source"] == "s"


ANCHORS = {
    "Co": {"name": "Cobalt", "price": 21.0, "unit": "$/lb", "source": "USGS MCS 2026 (2025 avg)", "fetched_at": None},
    "W": {"name": "Tungsten", "price": 21.74, "unit": "$/lb", "source": "USGS MCS 2026 (2025 avg)", "fetched_at": None},
}
SERIES = {
    "Co": {
        "unit": "$/lb",
        "source": "IMF PCPS (monthly average)",
        "points": [{"date": "2026-06-30", "price": 24.0}, {"date": "2026-07-31", "price": 25.3435}],
    }
}


def test_build_price_basis_uses_series_then_anchors():
    basis = build_price_basis(SERIES, "2026-07", ANCHORS)
    assert basis["Co"] == {
        "symbol": "Co",
        "name": "Cobalt",
        "price": 25.3435,
        "unit": "$/lb",
        "source": "IMF PCPS (monthly average)",
        "fetched_at": "2026-07-31",
    }
    assert basis["W"]["symbol"] == "W"
    assert basis["W"]["price"] == 21.74
    assert basis["W"]["source"].startswith("USGS")


def test_build_price_basis_refuses_a_month_the_series_lacks():
    with pytest.raises(ValueError, match="Co: no observation in 2026-08"):
        build_price_basis(SERIES, "2026-08", ANCHORS)


def test_reference_basis_is_accepted_by_the_decision_engine(session):
    basis = build_price_basis({}, "2026-07", get_reference_prices())
    result = evaluate_benchmark_family(session=session, family="ammonia-cracking", prices=basis)
    assert result["winner"] is not None
    assert all(c["evidence_summary"]["live_component_count"] == 0 for c in result["candidates"])
