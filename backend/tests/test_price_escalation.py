"""Tests for price escalation module."""

import pytest

from backend.core.price_escalation import escalate_cost, get_escalation_factor


class TestEscalation:
    def test_same_year_no_change(self):
        result = escalate_cost(100.0, 2017, 2017)
        assert result == 100.0

    def test_escalation_forward(self):
        # ChemPPI 2017→2022 should increase (inflation)
        result = escalate_cost(100.0, 2017, 2022, "chemppi")
        assert result > 100.0

    def test_escalation_backward(self):
        # Going backwards should decrease
        result = escalate_cost(100.0, 2022, 2017, "chemppi")
        assert result < 100.0

    def test_cepci_escalation(self):
        result = escalate_cost(100.0, 2017, 2022, "cepci")
        assert result > 100.0

    def test_unknown_year(self):
        with pytest.raises(KeyError):
            escalate_cost(100.0, 1950, 2020, "chemppi")

    def test_escalation_factor(self):
        factor = get_escalation_factor(2017, 2022, "chemppi")
        assert factor > 1.0

    def test_escalation_factor_same_year(self):
        factor = get_escalation_factor(2020, 2020)
        assert factor == 1.0

    def test_round_trip(self):
        # Escalate forward then backward should return to original
        original = 100.0
        escalated = escalate_cost(original, 2017, 2022, "chemppi")
        back = escalate_cost(escalated, 2022, 2017, "chemppi")
        assert back == pytest.approx(original, rel=1e-10)
