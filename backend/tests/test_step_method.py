"""Tests for Step Method module."""

import pytest

from backend.core.step_method import (
    calculate_campaign_length,
    calculate_step_method,
    determine_scale,
    selling_margin_pct,
)


class TestScaleAndCampaign:
    def test_small_scale(self):
        assert determine_scale(2) == "small"

    def test_medium_scale(self):
        assert determine_scale(20) == "medium"

    def test_large_scale(self):
        assert determine_scale(200) == "large"

    def test_boundary_small_medium(self):
        assert determine_scale(4.9) == "small"
        assert determine_scale(5) == "medium"

    def test_boundary_medium_large(self):
        assert determine_scale(69) == "medium"
        assert determine_scale(70) == "large"

    def test_very_large(self):
        assert determine_scale(5000) == "large"

    def test_campaign_small(self):
        # 2 tons at small (1 t/day) → 2 days synthesis + 0.5 cleaning
        result = calculate_campaign_length(2, "small")
        assert result == pytest.approx(2.5)

    def test_campaign_medium(self):
        # 20 tons at medium (10 t/day) → 2 days + 1 cleaning
        result = calculate_campaign_length(20, "medium")
        assert result == pytest.approx(3.0)

    def test_campaign_large(self):
        # 200 tons at large (150 t/day) → 1.333 days + 1 cleaning
        result = calculate_campaign_length(200, "large")
        assert result == pytest.approx(200 / 150 + 1.0)


class TestSellingMargin:
    def test_margin_decreases_with_scale(self):
        m_small = selling_margin_pct(2)
        m_large = selling_margin_pct(200)
        assert m_small > m_large

    def test_margin_positive(self):
        assert selling_margin_pct(1) > 0
        assert selling_margin_pct(1000) > 0

    def test_margin_reasonable_range(self):
        # Margin should be between 10-50% for typical orders
        for tons in [2, 20, 200]:
            m = selling_margin_pct(tons)
            assert 0.10 < m < 0.50


class TestStepMethod:
    def test_unknown_step(self):
        with pytest.raises(ValueError, match="Unknown step"):
            calculate_step_method(1.0, ["nonexistent_step"], 10)

    def test_unavailable_scale(self):
        # dryer_batch_vacuum_tray only available at small scale
        with pytest.raises(ValueError, match="not available"):
            calculate_step_method(1.0, ["dryer_batch_vacuum_tray"], 20)

    def test_basic_calculation(self):
        result = calculate_step_method(
            materials_cost_per_lb=1.0,
            steps=["mixer_slurry", "incipient_wetness"],
            order_size_tons=20,
        )
        assert result["scale"] == "medium"
        assert result["estimated_price_per_lb"] > result["materials_cost_per_lb"]
        assert result["margin_per_lb"] > 0
        assert result["processing_cost_per_lb"] > 0

    def test_chemppi_escalation(self):
        base = calculate_step_method(1.0, ["mixer_slurry"], 20, chemppi_escalation=1.0)
        escalated = calculate_step_method(1.0, ["mixer_slurry"], 20, chemppi_escalation=1.3)
        assert escalated["processing_cost_per_lb"] > base["processing_cost_per_lb"]

    def test_larger_order_lower_unit_cost(self):
        small = calculate_step_method(
            1.0, ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"], 3
        )
        medium = calculate_step_method(
            1.0, ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"], 20
        )
        # Processing cost per lb should generally be lower for larger orders
        assert medium["processing_cost_per_lb"] < small["processing_cost_per_lb"]
