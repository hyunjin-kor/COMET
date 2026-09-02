"""The ``prices`` override on evaluate_benchmark_family.

Callers replay historical price states through the same ranking code
(``scripts/price_volatility_screen.py``). Two properties have to hold for that
replay to mean anything: handing back the current price map must change nothing,
and a changed price must actually reach the costed candidate.
"""

from sqlmodel import Session

from backend.core.decision_engine import _latest_price_map, evaluate_benchmark_family

FAMILY = "nitrogen-reduction-reaction"


def _cost(result: dict, slug: str) -> float:
    candidate = next(c for c in result["candidates"] if c["slug"] == slug)
    return float(candidate["summary"]["landed_cost_per_lb"])


def test_passing_the_current_price_map_is_a_no_op(session: Session) -> None:
    default = evaluate_benchmark_family(session=session, family=FAMILY)
    injected = evaluate_benchmark_family(
        session=session, family=FAMILY, prices=_latest_price_map(session)
    )

    assert [c["slug"] for c in injected["candidates"]] == [
        c["slug"] for c in default["candidates"]
    ]
    for slug in (c["slug"] for c in default["candidates"]):
        assert _cost(injected, slug) == _cost(default, slug)


def test_a_raised_metal_price_raises_the_candidate_that_uses_it(session: Session) -> None:
    """li-mediated-nrr is 100 wt% Cu; plasma-nrr is 100 wt% Ni."""
    prices = _latest_price_map(session)
    baseline = evaluate_benchmark_family(session=session, family=FAMILY, prices=prices)

    dearer_copper = {symbol: dict(entry) for symbol, entry in prices.items()}
    dearer_copper["Cu"]["price"] = float(prices["Cu"]["price"]) * 2.0
    bumped = evaluate_benchmark_family(session=session, family=FAMILY, prices=dearer_copper)

    assert _cost(bumped, "li-mediated-nrr") > _cost(baseline, "li-mediated-nrr")
    assert _cost(bumped, "plasma-nrr") == _cost(baseline, "plasma-nrr")
