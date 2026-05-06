"""Unit tests for the area-based electrocatalyst layer cost model.

These tests target ``calculate_electrode_layer_cost`` directly so that the
math, validation rules, and ionomer pricing-mode selection are pinned
independently of the rest of the calculator pipeline. The wider electrode
flow (library resolution, /api/calculate integration) is exercised
elsewhere in test_api.py and test_calculation_harness.py.
"""

from __future__ import annotations

import pytest

from backend.core.electrocatalyst import (
    CM2_PER_M2,
    GRAMS_PER_LB,
    calculate_electrode_layer_cost,
)


def _bare_layer(**overrides):
    """Return a minimal valid kwargs dict for the cost helper."""

    base = {
        "catalyst_price_per_lb": 1000.0,
        "active_area_cm2": 25.0,
        "catalyst_loading_mg_cm2": 0.4,
    }
    base.update(overrides)
    return base


class TestElectrodeMath:
    def test_pure_catalyst_layer_matches_hand_calculation(self):
        """No ionomer, substrate, or membrane: result is just the powder cost."""
        result = calculate_electrode_layer_cost(**_bare_layer())

        catalyst_mass_g = 25.0 * 0.4 / 1000.0
        catalyst_cost = catalyst_mass_g / GRAMS_PER_LB * 1000.0

        assert result["catalyst_mass_g"] == pytest.approx(catalyst_mass_g, rel=1e-4)
        assert result["catalyst_cost_usd"] == pytest.approx(catalyst_cost, rel=1e-4)
        assert result["ionomer_cost_usd"] == 0.0
        assert result["substrate_cost_usd"] == 0.0
        assert result["membrane_cost_usd"] == 0.0
        assert result["total_cost_usd"] == pytest.approx(catalyst_cost, rel=1e-4)
        assert result["ionomer_pricing_mode"] == "none"

    def test_per_m2_is_per_cm2_times_ten_thousand(self):
        result = calculate_electrode_layer_cost(**_bare_layer())
        # The two outputs round to different precisions (cm2 → 6 decimals,
        # m2 → 2 decimals), so compare with the looser of the two bands.
        assert result["cost_per_m2_usd"] == pytest.approx(
            result["cost_per_cm2_usd"] * CM2_PER_M2,
            abs=0.01,
        )

    def test_substrate_and_membrane_costs_scale_with_area(self):
        """Substrate / membrane line items are area * unit cost."""
        result = calculate_electrode_layer_cost(
            **_bare_layer(
                substrate_cost_per_cm2=0.05,
                membrane_cost_per_cm2=0.07,
            )
        )
        assert result["substrate_cost_usd"] == pytest.approx(0.05 * 25.0, rel=1e-4)
        assert result["membrane_cost_usd"] == pytest.approx(0.07 * 25.0, rel=1e-4)


class TestIonomerPricingModes:
    def test_dry_solids_pricing_wins_when_kg_solids_price_set(self):
        """If both per-ml and per-kg_solids are set, kg-solids takes priority."""
        result = calculate_electrode_layer_cost(
            **_bare_layer(
                ionomer_to_catalyst_ratio=0.5,
                ionomer_price_per_kg_solids=200.0,
                ionomer_price_per_ml=999.0,  # would be huge — must be ignored
            )
        )
        catalyst_mass_g = 25.0 * 0.4 / 1000.0
        ionomer_solids_mass_g = catalyst_mass_g * 0.5
        expected_cost = ionomer_solids_mass_g / 1000.0 * 200.0

        assert result["ionomer_pricing_mode"] == "dry_solids"
        assert result["ionomer_solids_mass_g"] == pytest.approx(ionomer_solids_mass_g, rel=1e-4)
        assert result["ionomer_dispersion_volume_ml"] == 0.0
        assert result["ionomer_cost_usd"] == pytest.approx(expected_cost, rel=1e-4)

    def test_dispersion_pricing_uses_density_and_solids_fraction(self):
        """When only per-ml is given, the helper builds a wet-dispersion volume."""
        result = calculate_electrode_layer_cost(
            **_bare_layer(
                ionomer_to_catalyst_ratio=0.8,
                ionomer_price_per_ml=2.0,
                ionomer_density_g_ml=0.94,
                ionomer_solids_fraction=0.05,
            )
        )

        catalyst_mass_g = 25.0 * 0.4 / 1000.0
        ionomer_solids_mass_g = catalyst_mass_g * 0.8
        dispersion_mass_g = ionomer_solids_mass_g / 0.05
        dispersion_volume_ml = dispersion_mass_g / 0.94
        expected_cost = dispersion_volume_ml * 2.0

        assert result["ionomer_pricing_mode"] == "dispersion_volume"
        assert result["ionomer_solids_mass_g"] == pytest.approx(ionomer_solids_mass_g, rel=1e-4)
        assert result["ionomer_dispersion_volume_ml"] == pytest.approx(dispersion_volume_ml, rel=1e-4)
        assert result["ionomer_cost_usd"] == pytest.approx(expected_cost, rel=1e-4)

    def test_zero_ionomer_ratio_emits_pricing_mode_none(self):
        """An electrode with no ionomer should report mode=none and cost=0."""
        result = calculate_electrode_layer_cost(
            **_bare_layer(
                ionomer_to_catalyst_ratio=0.0,
                ionomer_price_per_kg_solids=200.0,  # provided but irrelevant
            )
        )
        assert result["ionomer_pricing_mode"] == "none"
        assert result["ionomer_cost_usd"] == 0.0
        assert result["ionomer_solids_mass_g"] == 0.0

    def test_dispersion_pricing_at_zero_per_ml_yields_zero_cost_but_keeps_volume(self):
        """A user can supply density only — cost stays 0 while volume is reported."""
        result = calculate_electrode_layer_cost(
            **_bare_layer(
                ionomer_to_catalyst_ratio=0.5,
                ionomer_price_per_ml=0.0,
            )
        )
        assert result["ionomer_pricing_mode"] == "dispersion_volume"
        assert result["ionomer_dispersion_volume_ml"] > 0
        assert result["ionomer_cost_usd"] == 0.0


class TestValidation:
    def test_zero_active_area_is_rejected(self):
        with pytest.raises(ValueError, match="active_area_cm2 must be positive"):
            calculate_electrode_layer_cost(**_bare_layer(active_area_cm2=0.0))

    def test_negative_active_area_is_rejected(self):
        with pytest.raises(ValueError, match="active_area_cm2 must be positive"):
            calculate_electrode_layer_cost(**_bare_layer(active_area_cm2=-1.0))

    def test_zero_loading_is_rejected(self):
        with pytest.raises(ValueError, match="catalyst_loading_mg_cm2 must be positive"):
            calculate_electrode_layer_cost(**_bare_layer(catalyst_loading_mg_cm2=0.0))

    def test_negative_ionomer_ratio_is_rejected(self):
        with pytest.raises(ValueError, match="ionomer_to_catalyst_ratio must be non-negative"):
            calculate_electrode_layer_cost(
                **_bare_layer(ionomer_to_catalyst_ratio=-0.01)
            )

    def test_zero_density_is_rejected(self):
        with pytest.raises(ValueError, match="ionomer_density_g_ml must be positive"):
            calculate_electrode_layer_cost(
                **_bare_layer(ionomer_density_g_ml=0.0)
            )

    def test_solids_fraction_must_be_within_open_zero_closed_one(self):
        with pytest.raises(ValueError, match="ionomer_solids_fraction must be between 0 and 1"):
            calculate_electrode_layer_cost(**_bare_layer(ionomer_solids_fraction=0.0))

        with pytest.raises(ValueError, match="ionomer_solids_fraction must be between 0 and 1"):
            calculate_electrode_layer_cost(**_bare_layer(ionomer_solids_fraction=1.5))

    def test_solids_fraction_at_one_is_allowed(self):
        """1.0 means the ionomer is fully solid (degenerate but mathematically valid)."""
        result = calculate_electrode_layer_cost(
            **_bare_layer(
                ionomer_to_catalyst_ratio=0.2,
                ionomer_price_per_ml=1.0,
                ionomer_solids_fraction=1.0,
            )
        )
        assert result["ionomer_pricing_mode"] == "dispersion_volume"


class TestResultShape:
    def test_breakdown_lists_four_canonical_lines(self):
        """The breakdown list is consumed by the UI: shape must be stable."""
        result = calculate_electrode_layer_cost(
            **_bare_layer(
                ionomer_to_catalyst_ratio=0.5,
                ionomer_price_per_kg_solids=200.0,
                substrate_cost_per_cm2=0.02,
                membrane_cost_per_cm2=0.03,
            )
        )
        labels = [item["label"] for item in result["breakdown"]]
        assert labels == ["Catalyst powder", "Ionomer", "Substrate / GDL", "Membrane"]

        breakdown_total = sum(item["cost_usd"] for item in result["breakdown"])
        assert breakdown_total == pytest.approx(result["total_cost_usd"], rel=1e-4)

    def test_application_family_is_passed_through(self):
        result = calculate_electrode_layer_cost(
            **_bare_layer(application_family="fuel_cell")
        )
        assert result["application_family"] == "fuel_cell"
