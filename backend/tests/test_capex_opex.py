"""Tests for CapEx & OpEx factors module."""

import pytest

from backend.core.capex_opex import (
    calculate_capex,
    calculate_opex,
    equipment_cost_correlation,
    equipment_cost_scaling,
)


class TestEquipmentCost:
    def test_scaling_same_size(self):
        result = equipment_cost_scaling(100000, 100, 100)
        assert result == pytest.approx(100000)

    def test_scaling_double(self):
        # Doubling size with 0.6 exponent → 2^0.6 ≈ 1.516x cost
        result = equipment_cost_scaling(100000, 100, 200, 0.6)
        assert result == pytest.approx(100000 * 2**0.6, rel=0.01)

    def test_scaling_invalid_size(self):
        with pytest.raises(ValueError):
            equipment_cost_scaling(100000, 0, 100)

    def test_cost_correlation(self):
        # Cost = 5000 + 200 * 100^0.6
        result = equipment_cost_correlation(100, 5000, 200, 0.6)
        expected = 5000 + 200 * 100**0.6
        assert result == pytest.approx(expected)


class TestCapEx:
    def test_basic_capex(self):
        result = calculate_capex(100000)
        assert result["purchased_equipment"] == 100000
        assert result["fixed_capital_investment"] > 100000
        assert result["total_capital_investment"] > result["fixed_capital_investment"]

    def test_custom_factors(self):
        custom = {"purchased_equipment": 1.0, "installation": 0.50}
        result = calculate_capex(100000, custom)
        assert result["installation"] == 50000

    def test_all_components_positive(self):
        result = calculate_capex(100000)
        assert result["direct_capital"] > 0
        assert result["indirect_capital"] > 0
        assert result["working_capital"] > 0


class TestOpEx:
    def test_basic_opex(self):
        result = calculate_opex(
            fci=1000000,
            direct_labor_cost=100000,
            raw_materials_cost=500000,
            utilities_cost=50000,
        )
        assert result["total_annual_opex"] > 0
        assert result["raw_materials"] == 500000
        assert result["direct_labor"] == 100000

    def test_opex_components(self):
        result = calculate_opex(1000000, 100000, 500000, 50000)
        assert result["direct_operating_total"] > 0
        assert result["fixed_operating_total"] > 0
        assert result["general_expenses_total"] > 0
        total = (
            result["direct_operating_total"]
            + result["fixed_operating_total"]
            + result["general_expenses_total"]
        )
        assert result["total_annual_opex"] == pytest.approx(total, rel=0.01)
