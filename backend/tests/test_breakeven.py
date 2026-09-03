"""Break-even metal price solver: pure search plus one engine-backed contest."""

from __future__ import annotations

import pytest

from backend.core.breakeven import (
    advantage_of_b,
    breakeven_for_pair,
    classify_contest,
    feed_symbols,
    find_crossings,
    history_side_counts,
    monthly_last,
)
from backend.core.decision_engine import _latest_price_map


class TestFindCrossings:
    def test_single_root_on_log_grid(self):
        roots, evals = find_crossings(lambda x: x - 3.0, 1.0, 10.0, scan=16)
        assert len(roots) == 1
        assert roots[0] == pytest.approx(3.0, rel=1e-3)
        assert evals > 16

    def test_no_sign_change_returns_empty(self):
        roots, _ = find_crossings(lambda x: x + 1.0, 1.0, 10.0, scan=8)
        assert roots == []

    def test_two_roots_are_both_found(self):
        roots, _ = find_crossings(lambda x: (x - 2.0) * (x - 5.0), 1.0, 10.0, scan=32)
        assert [round(r, 2) for r in roots] == [2.0, 5.0]

    def test_rejects_bad_range(self):
        with pytest.raises(ValueError):
            find_crossings(lambda x: x, 0.0, 1.0)


class TestHelpers:
    def test_feed_symbols_reads_market_feed_components(self):
        assert feed_symbols("ammonia-cracking", "ru-mgo-premium") == {"Ru": 3.0}
        assert feed_symbols("ammonia-cracking", "ni-alumina-baseline") == {"Ni": 12.0}

    def test_classify_contest(self):
        assert classify_contest({"Ru"}, {"Ni"}) == "precious_vs_base"
        assert classify_contest({"Pt"}, {"Ru"}) == "precious_vs_precious"
        assert classify_contest({"Cu"}, {"Ni"}) == "base_vs_base"
        assert classify_contest(set(), {"Pt"}) == "metal_vs_none"
        assert classify_contest({"Ag"}, {"Ag"}) == "same_metals"
        assert classify_contest(set(), set()) == "no_feed"

    def test_monthly_last_keeps_last_observation_per_month(self):
        pts = [{"date": "2026-01-05", "price": 1}, {"date": "2026-01-20", "price": 2}, {"date": "2026-02-01", "price": 3}]
        assert monthly_last(pts) == [{"date": "2026-01-20", "price": 2.0}, {"date": "2026-02-01", "price": 3.0}]

    def test_history_side_counts_above_and_below(self):
        pts = [{"date": f"2026-0{m}-01", "price": p} for m, p in zip(range(1, 6), (1, 2, 3, 4, 5))]
        above = history_side_counts(pts, 2.5, "above")
        assert (above["months_b_wins"], above["months_a_wins"]) == (3, 2)
        below = history_side_counts(pts, 2.5, "below")
        assert (below["months_b_wins"], below["months_a_wins"]) == (2, 3)


class TestEngineContest:
    """Ru/MgO against Ni/Al2O3 for ammonia cracking, priced from the reference basis."""

    FAMILY = "ammonia-cracking"
    A, B, SYMBOL = "ni-alumina-baseline", "ru-mgo-premium", "Ru"

    def test_cost_breakeven_exists_and_separates_the_sides(self, session):
        baseline = _latest_price_map(session)
        be = breakeven_for_pair(session, self.FAMILY, self.A, self.B, self.SYMBOL, baseline, metric="cost", scan=16)
        assert "error" not in be, be
        assert len(be["crossings"]) == 1
        assert be["b_wins_when"] == "below"  # Ru candidate wins only when Ru is cheap
        cross = be["crossings"][0]

        def at(price: float) -> float:
            prices = {s: dict(e) for s, e in baseline.items()}
            prices[self.SYMBOL] = {**prices[self.SYMBOL], "price": price}
            return advantage_of_b(session, self.FAMILY, self.A, self.B, prices, metric="cost")

        assert at(cross * 0.9) > 0  # Ru cheaper than break-even: Ru/MgO wins
        assert at(cross * 1.1) < 0  # Ru dearer: Ni/Al2O3 wins

    def test_unknown_symbol_is_reported_not_raised(self, session):
        baseline = _latest_price_map(session)
        be = breakeven_for_pair(session, self.FAMILY, self.A, self.B, "Xx", baseline)
        assert "error" in be

    def test_unknown_candidate_is_reported_not_raised(self, session):
        baseline = _latest_price_map(session)
        be = breakeven_for_pair(session, self.FAMILY, self.A, "no-such-slug", self.SYMBOL, baseline)
        assert "error" in be

    def test_mixed_basis_family_falls_back_to_landed_cost(self, session):
        # glycerol-electrooxidation prices some candidates per cm2 and others
        # per lb; the engine ranks such a family on landed $/lb, and so must we.
        baseline = _latest_price_map(session)
        be = breakeven_for_pair(
            session, "glycerol-electrooxidation", "niooh-glycerol-anode", "pt-bi-dha", "Pt", baseline, metric="cost", scan=12
        )
        assert "error" not in be, be
        assert be["verdict"] in {"crosses", "a_always_wins", "b_always_wins"}
