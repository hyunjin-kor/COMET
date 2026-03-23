"""Tests for materials calculation module."""

import pytest

from backend.core.materials_calc import (
    calculate_active_phase_mass,
    calculate_catalyst_mass,
    calculate_materials_cost,
    calculate_scaling_factor,
    calculate_support_mass,
    extrapolate_bulk_price,
    precursor_price_from_metal,
)


class TestStoichiometry:
    def test_active_phase_mass(self):
        # 100g limiting reagent, MW 100, 1:1 ratio, MW_AP 50, 90% yield
        result = calculate_active_phase_mass(100, 100, 1.0, 50, 90)
        assert result == pytest.approx(45.0)

    def test_active_phase_mass_100_yield(self):
        result = calculate_active_phase_mass(100, 100, 1.0, 100, 100)
        assert result == pytest.approx(100.0)

    def test_support_mass(self):
        # 2 wt% Pt on support: m_AP = 2, wt% = 2 → support = 98
        result = calculate_support_mass(2.0, 2.0)
        assert result == pytest.approx(98.0)

    def test_support_mass_20_pct(self):
        result = calculate_support_mass(20.0, 20.0)
        assert result == pytest.approx(80.0)

    def test_support_mass_invalid(self):
        with pytest.raises(ValueError):
            calculate_support_mass(10, 0)
        with pytest.raises(ValueError):
            calculate_support_mass(10, 100)

    def test_catalyst_mass(self):
        result = calculate_catalyst_mass(2.0, 98.0)
        assert result == pytest.approx(100.0)

    def test_scaling_factor(self):
        result = calculate_scaling_factor(1000, 0.1)
        assert result == pytest.approx(10000.0)

    def test_scaling_factor_invalid(self):
        with pytest.raises(ValueError):
            calculate_scaling_factor(100, 0)


class TestPricing:
    def test_bulk_price_extrapolation(self):
        # Two-point log-log regression
        lab_prices = [(1, 25.0), (5, 100.0), (25, 375.0)]
        result = extrapolate_bulk_price(lab_prices, 1000)
        assert result > 0
        # Bulk unit price should be less than or equal to smallest lab unit price
        assert result <= 25.0

    def test_bulk_price_insufficient_points(self):
        with pytest.raises(ValueError):
            extrapolate_bulk_price([(1, 10)], 100)

    def test_precursor_price(self):
        # Pt at $950/TrOz, H2PtCl6 has 37.68% Pt, 5% markup
        result = precursor_price_from_metal(950, 0.3768, 1.05)
        assert result == pytest.approx(950 / 0.3768 * 1.05, rel=0.01)

    def test_precursor_price_invalid_fraction(self):
        with pytest.raises(ValueError):
            precursor_price_from_metal(100, 0, 1.05)

    def test_materials_cost_simple(self):
        # Ni at $7.50/lb, 21 wt% on Al2O3 at $0.50/lb
        result = calculate_materials_cost(
            metal_price_per_lb=7.50,
            metal_loading_wt_pct=21,
            support_price_per_lb=0.50,
        )
        assert result["total_materials_cost_per_lb"] > 0
        # Metal cost should be 21% * 7.50 = 1.575
        assert result["metal_precursor_cost_per_lb"] == pytest.approx(1.575)
        # Support cost should be 79% * 0.50 = 0.395
        assert result["support_cost_per_lb"] == pytest.approx(0.395)

    def test_materials_cost_with_precursor(self):
        result = calculate_materials_cost(
            metal_price_per_lb=13860,  # Pt ~$950/TrOz * 14.58 TrOz/lb
            metal_loading_wt_pct=2,
            support_price_per_lb=0.75,
            precursor_metal_fraction=0.3768,
            precursor_markup=1.05,
        )
        # Precursor is much more expensive than pure metal per lb of catalyst
        assert result["metal_precursor_cost_per_lb"] > result["support_cost_per_lb"]
