"""Tests for spent catalyst recovery module."""

import pytest

from backend.core.spent_catalyst import calculate_metal_recovery_value


class TestMetalRecovery:
    def test_pt_on_carbon_fixed(self):
        result = calculate_metal_recovery_value(
            metal_symbol="Pt",
            metal_loading=0.02,  # 2 wt%
            metal_spot_price=13860,  # ~$950/TrOz * 14.58 TrOz/lb
            support="Carbon",
            reactor_type="fixed",
            catalyst_bulk_density=30.0,
        )
        # Should have positive V_metal
        assert result["V_metal_per_lb"] > 0
        # Recovery cost should be positive
        assert result["C_recovery_per_lb"] > 0
        # For PGM on carbon, reclaimed value should be positive (worth recovering)
        assert result["V_reclaimed_per_lb"] > 0

    def test_ni_on_alumina_fixed(self):
        result = calculate_metal_recovery_value(
            metal_symbol="Ni",
            metal_loading=0.21,  # 21 wt%
            metal_spot_price=7.50,
            support="Al2O3",
            reactor_type="fixed",
            catalyst_bulk_density=55.0,
        )
        # Ni is cheap, recovery cost may exceed value
        assert result["V_metal_per_lb"] > 0
        assert result["C_recovery_per_lb"] > 0

    def test_loss_factors_used(self):
        result = calculate_metal_recovery_value(
            metal_symbol="Pt",
            metal_loading=0.05,
            metal_spot_price=13860,
            support="TiO2",
            reactor_type="slurry",
            catalyst_bulk_density=60.0,
        )
        # TiO2 slurry has higher metal loss (13%) than fixed (10%)
        assert result["loss_use_pct"] == pytest.approx(13.0)

    def test_unknown_support_defaults(self):
        result = calculate_metal_recovery_value(
            metal_symbol="Pt",
            metal_loading=0.02,
            metal_spot_price=13860,
            support="UnknownSupport",
            reactor_type="fixed",
            catalyst_bulk_density=50.0,
        )
        # Should use defaults and not crash
        assert result["V_metal_per_lb"] > 0
