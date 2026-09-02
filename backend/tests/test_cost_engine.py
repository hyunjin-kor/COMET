"""Integration tests for cost engine with CatCost verification cases.

The Step Method is reproduced line by line against CatCost User Guide
Table 6.2 (mid-2017 basis, public). Inputs are the published per-case
materials totals, the published step lists with multiplicities, and the
published order sizes. Nothing is tuned to hit the target.

  - 2 wt% Pt/C,       2 ton,  Small:  CatCost=$27.37/lb, Market=$34.09/lb
  - 21 wt% Ni/Al2O3, 20 ton, Medium: CatCost=$20.59/lb, Market=$21.33/lb
  - USY-based FCC,  200 ton, Large:  CatCost=$2.41/lb,  Market=$2.73/lb

Two residuals are documented departures in the table itself, not engine error:
  - Ni/Al2O3 margin: footnote f applies 33% of pre-margin cost, while the
    Figure 6.3 correlation the guide publishes gives 24% at 20 ton. COMET
    follows the correlation, so its price lands 6.7% under the table.
  - FCC campaign: footnote b uses an effective 67 t/d (zeolite ramp-up)
    instead of the 150 t/d nominal rate. With that rate passed explicitly
    COMET lands within 1.2%.

See scripts/reproduce_catcost_table62.py for the full comparison.
"""

import pytest

from backend.core.constants import TROY_OZ_PER_LB
from backend.core.cost_engine import estimate_catalyst_cost
from backend.core.step_method import calculate_step_method
from backend.core.uncertainty import run_monte_carlo


class TestStepMethodVerification:
    """Reproduce CatCost User Guide Table 6.2 with the published inputs."""

    def test_pt_carbon_small_scale_step_method(self):
        """2 wt% Pt/C, 2 ton, Small. Every printed line of Table 6.2 matches."""
        result = calculate_step_method(
            materials_cost_per_lb=10.70,
            steps=[
                "incipient_wetness",
                "reactor_multistep",
                "scrubber_nox",
                "filter_plate_frame",
                "reactor_simple",
                "dryer_rotary_40_100C",
            ],
            order_size_tons=2.0,
            chemppi_escalation=1.0,
        )
        assert result["scale"] == "small"
        assert result["step_cost_per_hr"] == 390.0
        assert result["campaign_days"] == 2.5
        assert result["campaign_cost"] == 23400.0
        assert result["processing_cost_per_lb"] == pytest.approx(5.85, abs=0.005)
        assert result["subtotal_per_lb"] == pytest.approx(16.55, abs=0.005)
        assert result["ga_per_lb"] == pytest.approx(0.83, abs=0.01)
        assert result["sard_per_lb"] == pytest.approx(0.87, abs=0.01)
        assert result["margin_per_lb"] == pytest.approx(9.12, abs=0.01)
        assert result["estimated_price_per_lb"] == pytest.approx(27.37, abs=0.01)

    def test_ni_alumina_medium_scale_step_method(self):
        """21 wt% Ni/Al2O3, 20 ton, Medium. Exact through pre-margin cost.

        The table's margin (footnote f, 33% of pre-margin) departs from the
        Figure 6.3 correlation (24% at 20 ton) that COMET implements, so the
        final price is held to the resulting 6.7% residual rather than widened.
        """
        result = calculate_step_method(
            materials_cost_per_lb=11.88,
            steps=[
                "incipient_wetness",
                "dryer_rotary_40_100C",
                "kiln_continuous_indirect",
                "scrubber_nox",
                "crystallizer",
                "filter_rotary_vacuum",
                "dryer_rotary_40_100C",
                "kiln_continuous_indirect",
                "kiln_continuous_indirect",
            ],
            order_size_tons=20.0,
            chemppi_escalation=1.0,
        )
        assert result["scale"] == "medium"
        assert result["step_cost_per_hr"] == 1200.0
        assert result["campaign_days"] == 3.0
        assert result["campaign_cost"] == 86400.0
        assert result["processing_cost_per_lb"] == pytest.approx(2.16, abs=0.005)
        assert result["subtotal_per_lb"] == pytest.approx(14.04, abs=0.005)
        assert result["pre_margin_per_lb"] == pytest.approx(15.48, abs=0.01)
        assert result["estimated_price_per_lb"] == pytest.approx(20.59, rel=0.07)

    def test_fcc_zeolite_large_scale_step_method(self):
        """USY-based FCC, 200 ton, Large, at the footnote-b effective rate.

        Hourly step cost matches exactly. Footnote b gives an effective
        67 t/d for the zeolite campaign (4 days), which the override passes
        through; at the nominal 150 t/d COMET would run 2.33 days and land
        33% low, so the override is the published condition, not a fit.
        """
        steps = (
            ["reactor_simple", "crystallizer"]
            + ["filter_rotary_vacuum"] * 2
            + ["reactor_simple"] * 3
            + ["kiln_continuous_indirect", "reactor_multistep", "filter_rotary_vacuum", "reactor_multistep"]
            + ["reactor_simple"] * 2
            + ["dryer_spray"] * 2
            + ["reactor_simple"] * 4
            + ["filter_rotary_vacuum"] * 2
            + ["dryer_rotary_100_300C"]
        )
        result = calculate_step_method(
            materials_cost_per_lb=0.352,
            steps=steps,
            order_size_tons=200.0,
            chemppi_escalation=1.0,
            production_rate_ton_per_day=67.0,
        )
        assert result["scale"] == "large"
        assert result["step_cost_per_hr"] == 6725.0
        assert result["production_rate_ton_per_day"] == 67.0
        assert result["campaign_days"] == pytest.approx(4.0, abs=0.02)
        assert result["processing_cost_per_lb"] == pytest.approx(1.61, abs=0.005)
        assert result["estimated_price_per_lb"] == pytest.approx(2.41, rel=0.02)

    def test_fcc_nominal_rate_is_the_default(self):
        """Without the override the engine keeps the nominal 150 t/d rate."""
        result = calculate_step_method(0.352, ["reactor_simple"], 200.0)
        assert result["production_rate_ton_per_day"] == 150
        assert result["campaign_days"] == pytest.approx(200 / 150 + 1.0, abs=0.01)

    def test_relative_ordering(self):
        """Larger orders should have lower per-unit processing costs."""
        small = calculate_step_method(1.0, ["mixer_slurry", "incipient_wetness"], 3)
        medium = calculate_step_method(1.0, ["mixer_slurry", "incipient_wetness"], 20)
        assert medium["processing_cost_per_lb"] < small["processing_cost_per_lb"]

    def test_more_steps_higher_cost(self):
        """More processing steps should increase the price."""
        few = calculate_step_method(1.0, ["mixer_slurry"], 20)
        many = calculate_step_method(
            1.0, ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"], 20
        )
        assert many["estimated_price_per_lb"] > few["estimated_price_per_lb"]


class TestCostEngine:
    """Unit tests for integrated cost engine."""

    def test_basic_estimation(self):
        result = estimate_catalyst_cost(
            metal_symbol="Ni",
            metal_price=7.50,
            metal_price_unit="$/lb",
            metal_loading_wt_pct=10.0,
            support_name="Al2O3",
            support_price_per_lb=0.50,
            steps=["mixer_slurry", "incipient_wetness"],
            order_size_tons=10.0,
        )
        assert "summary" in result
        assert "materials" in result
        assert "step_method" in result
        assert result["summary"]["estimated_price_per_lb"] > 0

    def test_ni_alumina_full_pipeline(self):
        """Full pipeline test for Ni/Al2O3 with precursor."""
        result = estimate_catalyst_cost(
            metal_symbol="Ni",
            metal_price=7.50,
            metal_price_unit="$/lb",
            metal_loading_wt_pct=21.0,
            support_name="Al2O3",
            support_price_per_lb=0.50,
            precursor_metal_fraction=0.2018,
            precursor_markup=1.05,
            steps=[
                "mixer_slurry",
                "incipient_wetness",
                "dryer_rotary_100_300C",
                "kiln_continuous_indirect",
                "mill",
                "scrubber_nox",
            ],
            order_size_tons=20.0,
            basis_year=2017,
            target_year=2017,
        )
        # Materials cost should be reasonable for base metal precursor
        mat = result["materials"]["total_materials_cost_per_lb"]
        assert 0.5 < mat < 5.0
        # Total price should be in a reasonable range for base metal catalyst
        assert 2 < result["summary"]["estimated_price_per_lb"] < 15

    def test_with_spent_catalyst(self):
        result = estimate_catalyst_cost(
            metal_symbol="Pt",
            metal_price=950.0,
            metal_price_unit="$/troy_oz",
            metal_loading_wt_pct=5.0,
            support_name="Al2O3",
            support_price_per_lb=0.50,
            steps=["mixer_slurry", "incipient_wetness"],
            order_size_tons=5.0,
            include_spent_value=True,
            reactor_type="fixed",
            catalyst_bulk_density=55.0,
        )
        assert result["spent_catalyst"] is not None
        assert result["summary"]["net_cost_per_lb"] < result["summary"]["estimated_price_per_lb"]

    def test_troy_oz_to_lb_conversion(self):
        result = estimate_catalyst_cost(
            metal_symbol="Au",
            metal_price=2000.0,
            metal_price_unit="$/troy_oz",
            metal_loading_wt_pct=1.0,
            support_name="Al2O3",
            support_price_per_lb=0.50,
            steps=["mixer_slurry"],
            order_size_tons=5.0,
        )
        assert result["input_summary"]["metal_price_per_lb"] == pytest.approx(
            2000 * TROY_OZ_PER_LB, rel=0.01
        )

    def test_invalid_price_unit(self):
        with pytest.raises(ValueError) as excinfo:
            estimate_catalyst_cost(
                metal_symbol="Ni",
                metal_price=7.50,
                metal_price_unit="$/gallon",
                metal_loading_wt_pct=10.0,
                support_name="Al2O3",
                support_price_per_lb=0.50,
            )
        assert str(excinfo.value) == "Unknown metal_price_unit: $/gallon"

    def test_cost_breakdown_percentages(self):
        result = estimate_catalyst_cost(
            metal_symbol="Ni",
            metal_price=7.50,
            metal_price_unit="$/lb",
            metal_loading_wt_pct=15.0,
            support_name="Al2O3",
            support_price_per_lb=0.50,
            steps=["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
            order_size_tons=20.0,
        )
        assert result["summary"]["materials_pct"] > 0
        assert result["summary"]["processing_pct"] > 0

    def test_escalation_increases_price(self):
        """Escalating from 2017 to 2022 should increase the price."""
        base = estimate_catalyst_cost(
            metal_symbol="Ni", metal_price=7.50, metal_price_unit="$/lb",
            metal_loading_wt_pct=10.0, support_name="Al2O3",
            support_price_per_lb=0.50,
            steps=["mixer_slurry", "incipient_wetness"],
            order_size_tons=10.0, basis_year=2017, target_year=2017,
        )
        escalated = estimate_catalyst_cost(
            metal_symbol="Ni", metal_price=7.50, metal_price_unit="$/lb",
            metal_loading_wt_pct=10.0, support_name="Al2O3",
            support_price_per_lb=0.50,
            steps=["mixer_slurry", "incipient_wetness"],
            order_size_tons=10.0, basis_year=2017, target_year=2022,
        )
        assert escalated["summary"]["estimated_price_per_lb"] > base["summary"]["estimated_price_per_lb"]


class TestUncertaintyEngine:
    def test_run_monte_carlo_raises_when_all_simulations_fail(self):
        base_params = {
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/lb",
            "metal_loading_wt_pct": 15.0,
            "support_name": "Al2O3",
            "support_price_per_lb": 0.50,
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
        }

        with pytest.raises(ValueError, match="All simulations failed"):
            run_monte_carlo(
                base_params,
                uncertainties={"metal_loading_wt_pct": (10.0, 10.0)},
                n_simulations=5,
                seed=42,
            )
