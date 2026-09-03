"""Process-energy term of the LCA: first-principles duty x public emission factors."""

from __future__ import annotations

import pytest

from backend.core.lca import compute_catalyst_lca
from backend.core.process_energy import compute_process_energy, list_process_energy_factors

# Expected values follow the formulas in backend/core/process_energy.py with
# the defaults in process_energy_factors.json (cp 0.95, kiln eff 0.40, dryer
# eff 0.55, 0.7 kg water/kg, NG 0.05034 kg CO2e/MJ, grid 0.367 kg/kWh).
KILN_MJ = 0.95 * (500 - 25) / 0.40 / 1000  # 1.128125
DRYER_MJ = 0.7 * (4.18 * (150 - 25) + 2257) / 0.55 / 1000  # 3.5375
NG_GWP = 0.05034
GRID_GWP = 0.367


class TestFactorDataset:
    def test_emission_factors_are_the_epa_hub_values(self):
        data = list_process_energy_factors()
        gas = data["emission_factors"]["natural_gas"]
        grid = data["emission_factors"]["electricity_us_grid"]
        assert "53.06 kg CO2/mmBtu" in gas["source"]
        assert "771.5 lb CO2/MWh" in grid["source"]
        assert "eGRID2023" in grid["source"]
        assert gas["gwp_kg_co2eq_per_mj_hhv"] == pytest.approx(53.1145 / 1055.056, rel=1e-3)
        assert grid["gwp_kg_co2eq_per_kwh_delivered"] == pytest.approx(0.35163 / 0.958, rel=1e-3)

    def test_every_step_method_key_has_an_entry(self):
        from backend.core.constants import STEP_COSTS

        steps = list_process_energy_factors()["steps"]
        assert set(STEP_COSTS) == set(steps)


class TestProcessEnergy:
    def test_calcination_duty(self):
        p = compute_process_energy(["kiln_continuous_indirect"])
        step = p["per_step"][0]
        assert step["fuel_mj_per_kg"] == pytest.approx(KILN_MJ, rel=1e-3)
        assert step["gwp_kg_co2eq_per_kg"] == pytest.approx(KILN_MJ * NG_GWP, rel=1e-3)
        assert p["gwp_kg_co2eq_per_kg_catalyst"] == pytest.approx(KILN_MJ * NG_GWP, rel=1e-3)

    def test_calcination_temperature_override(self):
        base = compute_process_energy(["kiln_batch"])
        hot = compute_process_energy(["kiln_batch"], calcination_temp_c=800)
        assert hot["per_step"][0]["temp_c"] == 800
        assert hot["gwp_kg_co2eq_per_kg_catalyst"] > base["gwp_kg_co2eq_per_kg_catalyst"]

    def test_drying_duty_includes_latent_heat(self):
        p = compute_process_energy(["dryer_rotary_100_300C"])
        assert p["per_step"][0]["fuel_mj_per_kg"] == pytest.approx(DRYER_MJ, rel=1e-3)
        assert p["gwp_kg_co2eq_per_kg_catalyst"] == pytest.approx(DRYER_MJ * NG_GWP, rel=1e-3)

    def test_mechanical_step_uses_grid_factor(self):
        p = compute_process_energy(["mill"])
        assert p["per_step"][0]["fuel"] == "electricity"
        assert p["gwp_kg_co2eq_per_kg_catalyst"] == pytest.approx(0.015 * GRID_GWP, rel=1e-3)

    def test_repeated_steps_count_each_occurrence(self):
        one = compute_process_energy(["dryer_spray"])
        two = compute_process_energy(["dryer_spray", "dryer_spray"])
        # Totals are rounded to 4 dp, so allow the last-digit difference.
        assert two["gwp_kg_co2eq_per_kg_catalyst"] == pytest.approx(2 * one["gwp_kg_co2eq_per_kg_catalyst"], abs=2e-4)

    def test_electrode_line_steps_are_reported_not_estimated(self):
        p = compute_process_energy(["ccm_coating_pass", "hot_press_lamination", "mill"])
        assert p["unmodeled_steps"] == ["ccm_coating_pass", "hot_press_lamination"]
        assert p["modeled_step_count"] == 1
        assert p["gwp_kg_co2eq_per_kg_catalyst"] == pytest.approx(0.015 * GRID_GWP, rel=1e-3)

    def test_unknown_step_is_unmodeled_not_invented(self):
        p = compute_process_energy(["no_such_step"])
        assert p["unmodeled_steps"] == ["no_such_step"]
        assert p["gwp_kg_co2eq_per_kg_catalyst"] == 0.0


class TestLcaIntegration:
    COMP = [
        {"name": "Ni", "wt_pct": 21.0, "role": "active_metal"},
        {"name": "Al2O3", "wt_pct": 79.0, "role": "support"},
    ]
    ROUTE = ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C", "kiln_continuous_indirect"]

    def test_without_steps_is_materials_only(self):
        r = compute_catalyst_lca(self.COMP)
        assert r["process"] is None
        assert "materials only" in r["system_boundary"]
        assert r["gwp_kg_co2eq_per_kg_catalyst"] == r["materials"]["gwp_kg_co2eq_per_kg_catalyst"]

    def test_with_steps_adds_process_term(self):
        r = compute_catalyst_lca(self.COMP, steps=self.ROUTE)
        m = r["materials"]["gwp_kg_co2eq_per_kg_catalyst"]
        p = r["process"]["gwp_kg_co2eq_per_kg_catalyst"]
        assert p > 0
        assert r["gwp_kg_co2eq_per_kg_catalyst"] == pytest.approx(m + p, abs=1e-3)
        assert "4/4 steps modeled" in r["system_boundary"]

    def test_materials_dominate_for_supported_base_metal(self):
        # The CatCost paper reports raw materials dominate catalyst GHG; the
        # route term for an impregnation route should be a small fraction.
        r = compute_catalyst_lca(self.COMP, steps=self.ROUTE)
        share = r["process"]["gwp_kg_co2eq_per_kg_catalyst"] / r["gwp_kg_co2eq_per_kg_catalyst"]
        assert share < 0.10

    def test_unmodeled_steps_produce_a_warning(self):
        r = compute_catalyst_lca([{"name": "Pt", "wt_pct": 100.0}], steps=["ccm_coating_pass"])
        assert r["process"]["unmodeled_steps"] == ["ccm_coating_pass"]
        assert any("not modeled" in w for w in r["warnings"])
        assert "0/1 steps modeled" in r["system_boundary"]

    def test_cost_engine_passes_route_to_lca(self):
        from backend.core.cost_engine import estimate_catalyst_cost

        result = estimate_catalyst_cost(
            metal_symbol="Ni", metal_price=7.5, metal_price_unit="$/lb",
            metal_loading_wt_pct=21.0, support_name="Al2O3", support_price_per_lb=0.5,
            steps=self.ROUTE, order_size_tons=20.0,
        )
        assert result["lca"]["process"] is not None
        assert result["lca"]["process"]["total_step_count"] == len(self.ROUTE)
        assert "route energy" in result["lca"]["system_boundary"]
