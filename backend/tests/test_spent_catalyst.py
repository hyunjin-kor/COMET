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
        # CatCost workbook average for TiO2 slurry metal loss is 12.5%
        assert result["loss_use_pct"] == pytest.approx(12.5)

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

    def test_precious_refining_charge_converts_troy_oz_to_lb(self):
        result = calculate_metal_recovery_value(
            metal_symbol="Pt",
            metal_loading=0.02,
            metal_spot_price=13860,
            support="Carbon",
            reactor_type="fixed",
            catalyst_bulk_density=30.0,
        )
        # 14.5 $/TrOz x 14.5833 TrOz/lb x 0.02 lb metal/lb cat, net of losses
        refining = 14.5 * 14.5833 * 0.02 * (1 - 0.025) * (1 - 0.02)
        l_solids = 0.02 * (1 - 0.02) + 0.025 * 0.02
        handling = (1 - l_solids) * (0.1375 + 104.5 / 30.0)
        assert result["C_recovery_per_lb"] == pytest.approx(handling + refining, rel=1e-4)

    def test_non_precious_salvage_uses_scrap_anchor_not_input_price(self):
        result = calculate_metal_recovery_value(
            metal_symbol="Fe",
            metal_loading=0.30,
            metal_spot_price=2.44,  # precursor-basis input price
            support="SiO2",
            reactor_type="fixed",
            catalyst_bulk_density=55.0,
        )
        # Salvage must come from the $95/short-ton scrap anchor (escalated),
        # not the precursor input: (1-0.03)(1-0.40) x 0.30 x ~0.06 $/lb
        assert result["V_metal_per_lb"] < 0.05
        assert result["loss_refining_pct"] == pytest.approx(40.0)
        # and no phantom precious-metal refining charge
        l_solids = 0.02 * 0.70 + 0.03 * 0.30
        handling = (1 - l_solids) * (0.1375 + 115.5 / 55.0)
        assert result["C_recovery_per_lb"] == pytest.approx(handling, rel=1e-4)
