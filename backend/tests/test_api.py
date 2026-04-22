"""FastAPI endpoint integration tests."""

import json
from datetime import UTC, datetime

import pytest
from sqlmodel import select

import backend.main as main_module
from backend.models.material import Material
from backend.models.metal_price import MetalPrice
from backend.routers.catcost_import import MAX_IMPORT_BYTES


def _save_estimate(client, name: str, **overrides):
    payload = {
        "metal_symbol": "Ni",
        "metal_price": 7.50,
        "metal_price_unit": "$/lb",
        "metal_loading_wt_pct": 15.0,
        "support_name": "Al2O3",
        "support_price_per_lb": 0.50,
        "steps": ["mixer_slurry", "incipient_wetness"],
        "order_size_tons": 10.0,
    }
    payload.update(overrides)
    return client.post(
        f"/api/calculate/save?name={name}",
        json=payload,
    )


class TestHealth:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_docs_are_disabled_in_non_debug_mode(self, client):
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404

    def test_trusted_host_blocks_unexpected_host_header(self, client):
        resp = client.get("/api/health", headers={"host": "evil.example"})
        assert resp.status_code == 400
        assert resp.text == "Invalid host header"

    def test_security_headers_are_applied(self, client):
        resp = client.get("/api/health")
        assert resp.headers["X-Content-Type-Options"] == "nosniff"
        assert resp.headers["X-Frame-Options"] == "DENY"
        assert resp.headers["Referrer-Policy"] == "no-referrer"
        assert resp.headers["Cache-Control"] == "no-store"

    def test_manual_price_refresh_updates_health_timestamp(self, client, monkeypatch):
        async def fake_collect_prices():
            return {
                "Pt": {
                    "name": "Platinum",
                    "price": 1010.5,
                    "unit": "$/troy_oz",
                    "source": "Yahoo Finance (live)",
                    "fetched_at": "2026-04-21T04:00:00+00:00",
                }
            }

        monkeypatch.setattr(main_module, "collect_prices", fake_collect_prices)
        monkeypatch.setattr(main_module, "_last_price_update", None)

        refresh_resp = client.post("/api/prices/refresh")
        assert refresh_resp.status_code == 200
        refresh_payload = refresh_resp.json()
        assert refresh_payload["status"] == "ok"
        assert refresh_payload["prices_fetched"] == 1
        refreshed_at = datetime.fromisoformat(refresh_payload["updated_at"])
        assert refreshed_at.tzinfo is not None
        assert refreshed_at.astimezone(UTC).utcoffset() == UTC.utcoffset(refreshed_at)

        health_resp = client.get("/api/health")
        assert health_resp.status_code == 200
        health_payload = health_resp.json()
        assert health_payload["last_price_update"] == refresh_payload["updated_at"]

    def test_manual_price_refresh_rejects_non_local_request(self, client, monkeypatch):
        monkeypatch.setattr(main_module.settings, "debug", False)
        monkeypatch.setattr(main_module, "_is_local_request", lambda host: False)

        resp = client.post("/api/prices/refresh")
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Manual refresh is only available from local requests."


class TestCalculator:
    def test_calculate_basic(self, client):
        resp = client.post("/api/calculate", json={
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/lb",
            "metal_loading_wt_pct": 15.0,
            "support_name": "Al2O3",
            "support_price_per_lb": 0.50,
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["estimated_price_per_lb"] > 0

    def test_calculate_invalid_step(self, client):
        resp = client.post("/api/calculate", json={
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/lb",
            "metal_loading_wt_pct": 15.0,
            "support_name": "Al2O3",
            "steps": ["nonexistent_step"],
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert detail.startswith("Unknown step: 'nonexistent_step'.")

    def test_calculate_requires_support_name_for_thermal_legacy_inputs(self, client):
        resp = client.post("/api/calculate", json={
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/lb",
            "metal_loading_wt_pct": 15.0,
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert payload["detail"][0]["msg"] == (
            "Value error, components is required unless legacy fields are provided: support_name"
        )

    def test_calculate_requires_price_for_component_without_material_key(self, client):
        resp = client.post("/api/calculate", json={
            "components": [
                {"role": "active_metal", "name": "Ni", "wt_pct": 10.0},
                {"role": "support", "name": "Al2O3", "wt_pct": 90.0, "price_per_lb": 0.50},
            ],
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert payload["detail"][0]["loc"] == ["body", "components", 0]
        assert payload["detail"][0]["msg"] == (
            "Value error, Component requires price_per_lb unless material_key is provided"
        )

    def test_calculate_requires_name_or_material_key_for_component(self, client):
        resp = client.post("/api/calculate", json={
            "components": [
                {"role": "active_metal", "wt_pct": 10.0, "price_per_lb": 7.50},
                {"role": "support", "name": "Al2O3", "wt_pct": 90.0, "price_per_lb": 0.50},
            ],
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert payload["detail"][0]["loc"] == ["body", "components", 0]
        assert payload["detail"][0]["msg"] == (
            "Value error, Component requires either name or material_key"
        )

    def test_calculate_requires_at_least_one_active_component(self, client):
        resp = client.post("/api/calculate", json={
            "components": [
                {"role": "support", "name": "Al2O3", "wt_pct": 100.0, "price_per_lb": 0.50},
            ],
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 422
        assert resp.json()["detail"] == (
            "At least one active_metal or active_catalyst component is required"
        )

    def test_calculate_requires_at_least_one_support_component(self, client):
        resp = client.post("/api/calculate", json={
            "components": [
                {"role": "active_metal", "name": "Ni", "wt_pct": 100.0, "price_per_lb": 7.50},
            ],
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 422
        assert resp.json()["detail"] == "At least one support component is required"

    def test_calculate_rejects_zero_weight_component_with_structured_detail(self, client):
        resp = client.post("/api/calculate", json={
            "components": [
                {"role": "active_metal", "name": "Ni", "wt_pct": 12.0, "price_per_lb": 7.50},
                {"role": "promoter", "name": "", "wt_pct": 0.0, "price_per_lb": 0.0},
                {"role": "support", "name": "Al2O3", "wt_pct": 88.0, "price_per_lb": 0.50},
            ],
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert isinstance(payload["detail"], list)
        assert payload["detail"][0]["loc"][-1] == "wt_pct"

    def test_calculate_quick(self, client):
        resp = client.post("/api/calculate/quick", json={
            "metal_symbol": "Pt",
            "metal_price": 950.0,
            "metal_price_unit": "$/troy_oz",
            "metal_loading_wt_pct": 2.0,
        })
        assert resp.status_code == 200
        assert resp.json()["summary"]["estimated_price_per_lb"] > 0

    def test_calculate_quick_with_template(self, client):
        resp = client.post("/api/calculate/quick", json={
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/lb",
            "metal_loading_wt_pct": 21.0,
            "template_id": "wet_impregnation_metal_oxide",
        })
        assert resp.status_code == 200

    def test_calculate_quick_returns_422_for_unknown_template(self, client):
        resp = client.post("/api/calculate/quick", json={
            "metal_symbol": "Pt",
            "metal_price": 950.0,
            "metal_price_unit": "$/troy_oz",
            "metal_loading_wt_pct": 2.0,
            "template_id": "does-not-exist",
        })
        assert resp.status_code == 422
        assert resp.json()["detail"] == "Template 'does-not-exist' not found"

    def test_calculate_quick_rejects_unknown_metal_price_unit(self, client):
        resp = client.post("/api/calculate/quick", json={
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/stone",
            "metal_loading_wt_pct": 15.0,
            "support_name": "Al2O3",
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 422
        assert resp.json()["detail"] == "Unknown metal_price_unit: $/stone"

    def test_calculate_quick_rejects_full_metal_loading_without_support_fraction(self, client):
        resp = client.post("/api/calculate/quick", json={
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/lb",
            "metal_loading_wt_pct": 100.0,
            "support_name": "Al2O3",
            "order_size_tons": 10.0,
        })
        assert resp.status_code == 422
        assert resp.json()["detail"] == "metal_loading_wt_pct must be less than 100"

    def test_calculate_electrocatalyst_warns_about_model_scope(self, client):
        resp = client.post("/api/calculate", json={
            "components": [
                {"role": "active_metal", "name": "Pt", "wt_pct": 20.0, "price_per_lb": 12000.0},
                {"role": "support", "name": "Carbon", "wt_pct": 80.0, "price_per_lb": 1.5},
            ],
            "steps": ["mixer_slurry", "incipient_wetness"],
            "catalyst_domain": "electrocatalyst",
            "order_size_tons": 2.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["input_summary"]["catalyst_domain"] == "electrocatalyst"
        assert data["warnings"]
        assert "adjunct inputs" in data["warnings"][0]

    def test_calculate_electrocatalyst_with_library_materials(self, client):
        resp = client.post("/api/calculate", json={
            "catalyst_domain": "electrocatalyst",
            "application_family": "fuel_cell",
            "template_id": "pem_fuel_cell_ccm",
            "order_size_tons": 2.0,
            "steps": [
                "membrane_pretreatment",
                "ionomer_ink_homogenization",
                "ccm_coating_pass",
                "electrode_drying_low_temp",
                "hot_press_lamination",
            ],
            "components": [
                {
                    "role": "active_catalyst",
                    "material_key": "fcs:xt-pt20-vulcan-s",
                    "wt_pct": 100.0,
                }
            ],
            "electrode_input": {
                "application_family": "fuel_cell",
                "catalyst_material_key": "fcs:xt-pt20-vulcan-s",
                "ionomer_material_key": "fcs:pfsa-d5",
                "membrane_material_key": "fcs:pfsa-d50u",
                "substrate_material_key": "fcs:w1s1011",
                "active_area_cm2": 25.0,
                "catalyst_loading_mg_cm2": 0.4,
                "ionomer_to_catalyst_ratio": 0.8,
            },
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["electrode_model"] is not None
        assert data["electrode_model"]["cost_per_cm2_usd"] > 0
        assert data["route_summary"]["template_id"] == "pem_fuel_cell_ccm"
        assert any(item["used_for"] == "electrode:ionomer" for item in data["resolved_materials"])

    def test_calculate_aem_electrocatalyst_with_curated_library_materials(self, client):
        resp = client.post("/api/calculate", json={
            "catalyst_domain": "electrocatalyst",
            "application_family": "fuel_cell",
            "template_id": "aem_fuel_cell_ccm",
            "order_size_tons": 2.0,
            "steps": [
                "membrane_pretreatment",
                "substrate_pretreatment",
                "ion_exchange_conversion",
                "ionomer_ink_homogenization",
                "ultrasonic_dispersion",
                "ccm_coating_pass",
                "electrode_drying_low_temp",
                "hot_press_lamination",
                "electrochemical_break_in",
            ],
            "components": [
                {
                    "role": "active_catalyst",
                    "material_key": "fcs:ag20-vulcan",
                    "wt_pct": 100.0,
                }
            ],
            "electrode_input": {
                "application_family": "fuel_cell",
                "catalyst_material_key": "fcs:ag20-vulcan",
                "ionomer_material_key": "fcs:piperion-dispersion-5wt-20ml",
                "membrane_material_key": "fcs:piperion-aem40",
                "substrate_material_key": "fcs:ct-gds250",
                "active_area_cm2": 25.0,
                "catalyst_loading_mg_cm2": 0.7,
                "ionomer_to_catalyst_ratio": 0.6,
            },
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["route_summary"]["template_id"] == "aem_fuel_cell_ccm"
        assert data["electrode_model"] is not None
        assert data["electrode_model"]["cost_per_cm2_usd"] > 0
        assert any(item["material_key"] == "fcs:piperion-aem40" for item in data["resolved_materials"])

    def test_calculate_quaternary_thermal_recipe_with_promoted_support(self, client):
        resp = client.post("/api/calculate", json={
            "catalyst_domain": "thermal",
            "order_size_tons": 20.0,
            "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
            "components": [
                {"role": "active_metal", "name": "Ni", "wt_pct": 15.0, "price_per_lb": 16.83},
                {"role": "promoter", "material_key": "sigma:431346", "wt_pct": 5.0},
                {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 40.0},
                {"role": "support", "material_key": "lit:usgs-ceria-2025", "wt_pct": 40.0},
            ],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]["estimated_price_per_lb"] > 0
        assert data["input_summary"]["n_components"] == 4
        assert "/Al2O3+CeO2" in data["input_summary"]["composition"]

    def test_calculate_rejects_more_than_four_thermal_components(self, client):
        resp = client.post("/api/calculate", json={
            "catalyst_domain": "thermal",
            "order_size_tons": 20.0,
            "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
            "components": [
                {"role": "active_metal", "name": "Ni", "wt_pct": 10.0, "price_per_lb": 16.83},
                {"role": "active_metal", "name": "Co", "wt_pct": 10.0, "price_per_lb": 14.25},
                {"role": "promoter", "name": "Mo", "wt_pct": 5.0, "price_per_lb": 24.5},
                {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 35.0},
                {"role": "support", "material_key": "lit:usgs-ceria-2025", "wt_pct": 40.0},
            ],
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert payload["detail"][0]["msg"] == "Value error, Thermal workflows support at most four total components"


class TestUncertainty:
    def test_uncertainty_uses_structured_thermal_calculation_input(self, client):
        resp = client.post("/api/uncertainty", json={
            "calculation_input": {
                "catalyst_domain": "thermal",
                "order_size_tons": 20.0,
                "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
                "components": [
                    {"role": "active_metal", "name": "Ni", "wt_pct": 15.0, "price_per_lb": 16.83},
                    {"role": "promoter", "material_key": "sigma:431346", "wt_pct": 5.0},
                    {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 40.0},
                    {"role": "support", "material_key": "lit:usgs-ceria-2025", "wt_pct": 40.0},
                ],
            },
            "n_simulations": 250,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["baseline_price_per_lb"] > 0
        assert data["catalyst_domain"] == "thermal"
        assert data["composition"]

    def test_uncertainty_uses_electrocatalyst_calculation_input(self, client):
        resp = client.post("/api/uncertainty", json={
            "calculation_input": {
                "catalyst_domain": "electrocatalyst",
                "application_family": "fuel_cell",
                "template_id": "pem_fuel_cell_ccm",
                "order_size_tons": 2.0,
                "steps": [
                    "membrane_pretreatment",
                    "ionomer_ink_homogenization",
                    "ccm_coating_pass",
                    "electrode_drying_low_temp",
                    "hot_press_lamination",
                ],
                "components": [
                    {
                        "role": "active_catalyst",
                        "material_key": "fcs:xt-pt20-vulcan-s",
                        "wt_pct": 100.0,
                    }
                ],
                "electrode_input": {
                    "application_family": "fuel_cell",
                    "catalyst_material_key": "fcs:xt-pt20-vulcan-s",
                    "ionomer_material_key": "fcs:pfsa-d5",
                    "membrane_material_key": "fcs:pfsa-d50u",
                    "substrate_material_key": "fcs:w1s1011",
                    "active_area_cm2": 25.0,
                    "catalyst_loading_mg_cm2": 0.4,
                    "ionomer_to_catalyst_ratio": 0.8,
                },
            },
            "n_simulations": 250,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["baseline_price_per_lb"] > 0
        assert data["catalyst_domain"] == "electrocatalyst"
        assert data["application_family"] == "fuel_cell"

    def test_uncertainty_requires_legacy_fields_without_calculation_input(self, client):
        resp = client.post("/api/uncertainty", json={
            "order_size_tons": 10.0,
            "n_simulations": 250,
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert payload["detail"][0]["msg"] == (
            "Value error, calculation_input is required unless legacy uncertainty fields "
            "are provided: metal_symbol, metal_price, metal_loading_wt_pct"
        )

    def test_uncertainty_rejects_bounds_without_exactly_two_values(self, client):
        resp = client.post("/api/uncertainty", json={
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/lb",
            "metal_loading_wt_pct": 15.0,
            "support_name": "Al2O3",
            "support_price_per_lb": 0.50,
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
            "n_simulations": 250,
            "uncertainties": {
                "metal_price": [0.8],
            },
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert payload["detail"][0]["msg"] == "Value error, Uncertainty 'metal_price' must provide exactly two values: [low, high]"

    def test_uncertainty_rejects_inverted_bounds(self, client):
        resp = client.post("/api/uncertainty", json={
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/lb",
            "metal_loading_wt_pct": 15.0,
            "support_name": "Al2O3",
            "support_price_per_lb": 0.50,
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
            "n_simulations": 250,
            "uncertainties": {
                "metal_price": [1.2, 0.8],
            },
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert payload["detail"][0]["msg"] == "Value error, Uncertainty 'metal_price' must be a nondecreasing pair [low, high]"

    def test_uncertainty_rejects_nonpositive_bounds(self, client):
        resp = client.post("/api/uncertainty", json={
            "metal_symbol": "Ni",
            "metal_price": 7.50,
            "metal_price_unit": "$/lb",
            "metal_loading_wt_pct": 15.0,
            "support_name": "Al2O3",
            "support_price_per_lb": 0.50,
            "steps": ["mixer_slurry", "incipient_wetness"],
            "order_size_tons": 10.0,
            "n_simulations": 250,
            "uncertainties": {
                "metal_price": [0.0, 1.2],
            },
        })
        assert resp.status_code == 422
        payload = resp.json()
        assert payload["detail"][0]["msg"] == "Value error, Uncertainty 'metal_price' must use strictly positive bounds"


class TestCompare:
    def test_compare_two_compositions(self, client):
        resp = client.post("/api/compare", json={
            "compositions": [
                {
                    "metal_symbol": "Ni",
                    "metal_price": 7.50,
                    "metal_price_unit": "$/lb",
                    "metal_loading_wt_pct": 15.0,
                    "support_name": "Al2O3",
                    "support_price_per_lb": 0.50,
                    "steps": ["mixer_slurry", "incipient_wetness"],
                    "order_size_tons": 2.0,
                },
                {
                    "label": "Pt/C benchmark",
                    "metal_symbol": "Pt",
                    "metal_price": 950.0,
                    "metal_price_unit": "$/troy_oz",
                    "metal_loading_wt_pct": 2.0,
                    "support_name": "Carbon",
                    "support_price_per_lb": 0.80,
                    "steps": ["mixer_slurry", "incipient_wetness"],
                    "order_size_tons": 20.0,
                },
            ]
        })
        assert resp.status_code == 200
        payload = resp.json()
        assert len(payload["compositions"]) == 2
        assert payload["compositions"][0]["label"] == "Ni/Al2O3"
        assert payload["compositions"][1]["label"] == "Pt/C benchmark"
        assert payload["compositions"][0]["estimated_price_per_lb"] > 0
        assert payload["compositions"][1]["scale"] == "medium"

    def test_compare_uses_one_based_index_in_error_detail(self, client):
        resp = client.post("/api/compare", json={
            "compositions": [
                {
                    "metal_symbol": "Ni",
                    "metal_price": 7.50,
                    "metal_price_unit": "$/lb",
                    "metal_loading_wt_pct": 15.0,
                    "support_name": "Al2O3",
                    "support_price_per_lb": 0.50,
                    "steps": ["not_a_real_step"],
                    "order_size_tons": 2.0,
                },
                {
                    "metal_symbol": "Pt",
                    "metal_price": 950.0,
                    "metal_price_unit": "$/troy_oz",
                    "metal_loading_wt_pct": 2.0,
                    "support_name": "Carbon",
                    "support_price_per_lb": 0.80,
                    "steps": ["mixer_slurry", "incipient_wetness"],
                    "order_size_tons": 20.0,
                },
            ]
        })
        assert resp.status_code == 422
        detail = resp.json()["detail"]
        assert detail.startswith("Composition 1: Unknown step: 'not_a_real_step'.")
        assert "Composition 0" not in detail


class TestPrices:
    def test_get_all_prices(self, client):
        resp = client.get("/api/prices")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        symbols = {p["symbol"] for p in data}
        assert "Pt" in symbols
        assert "Ni" in symbols
        assert all("source_type" in p for p in data)
        assert all(p["source_type"] in {"live", "indexed"} for p in data)
        assert all("evidence" in p for p in data)
        assert all("confidence_score" in p["evidence"] for p in data)

    def test_get_single_price(self, client):
        resp = client.get("/api/prices/Pt")
        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "Pt"
        assert data["price"] > 0
        assert data["source_type"] in {"live", "indexed"}
        assert data["evidence"]["tier"]

    def test_get_unknown_metal(self, client):
        resp = client.get("/api/prices/Xx")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Metal 'Xx' not found"

    def test_get_unknown_price_history_returns_clean_404_detail(self, client):
        resp = client.get("/api/prices/Xx/history")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "No history for 'Xx'"

    def test_get_db_price_history_with_inclusive_date_range(self, client, session):
        session.add_all([
            MetalPrice(
                symbol="Ni",
                name="Nickel",
                price=8.1,
                unit="$/lb",
                source="Manual DB seed",
                fetched_at=datetime(2025, 1, 15, 12, 0, 0),
            ),
            MetalPrice(
                symbol="Ni",
                name="Nickel",
                price=8.4,
                unit="$/lb",
                source="Manual DB seed",
                fetched_at=datetime(2025, 2, 1, 12, 0, 0),
            ),
            MetalPrice(
                symbol="Ni",
                name="Nickel",
                price=8.9,
                unit="$/lb",
                source="Manual DB seed",
                fetched_at=datetime(2025, 2, 28, 12, 0, 0),
            ),
            MetalPrice(
                symbol="Ni",
                name="Nickel",
                price=9.2,
                unit="$/lb",
                source="Manual DB seed",
                fetched_at=datetime(2025, 3, 10, 12, 0, 0),
            ),
        ])
        session.commit()

        resp = client.get("/api/prices/Ni/history?from=2025-02-01&to=2025-02-28")
        assert resp.status_code == 200
        data = resp.json()
        assert data["source"] == "DB cache"
        assert data["count"] == 2
        assert [row["date"] for row in data["history"]] == ["2025-02-01", "2025-02-28"]

    def test_get_price_history_rejects_inverted_date_range(self, client):
        resp = client.get("/api/prices/Ni/history?from=2025-03-01&to=2025-02-01")
        assert resp.status_code == 422
        assert resp.json()["detail"] == "'from' must be on or before 'to'"


class TestMaterials:
    def test_list_all(self, client):
        resp = client.get("/api/materials")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) > 0
        assert all("catalyst_domain" in item for item in data)

    def test_filter_by_category(self, client):
        resp = client.get("/api/materials?category=metal")
        assert resp.status_code == 200
        data = resp.json()
        assert data
        assert all("metal" in (m["category"] or "").lower() for m in data)

    def test_search(self, client):
        resp = client.get("/api/materials?q=plat")
        assert resp.status_code == 200
        data = resp.json()
        assert any("Plat" in m["name"] for m in data)

    def test_create_and_filter_electrocatalyst_material(self, client):
        create_resp = client.post("/api/materials", json={
            "name": "Nafion ionomer",
            "category": "Ionomer",
            "price": 180.0,
            "price_unit": "$/lb",
            "source": "user",
            "catalyst_domain": "electrocatalyst",
        })
        assert create_resp.status_code == 200

        filter_resp = client.get("/api/materials?catalyst_domain=electrocatalyst&q=nafion")
        assert filter_resp.status_code == 200
        payload = filter_resp.json()
        assert payload
        assert any(item["name"] == "Nafion ionomer" for item in payload)
        assert all(item["catalyst_domain"] in {"electrocatalyst", "both"} for item in payload)

    def test_get_custom_material_detail(self, client):
        create_resp = client.post("/api/materials", json={
            "name": "Custom ceria support",
            "category": "Support",
            "formula": "CeO2",
            "price": 18.5,
            "price_unit": "$/lb",
            "source": "user",
            "catalyst_domain": "thermal",
        })
        assert create_resp.status_code == 200
        material_id = create_resp.json()["id"]

        detail_resp = client.get(f"/api/materials/{material_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["id"] == str(material_id)
        assert detail["name"] == "Custom ceria support"
        assert detail["formula"] == "CeO2"
        assert detail["is_custom"] is True

    def test_patch_custom_material_updates_mutable_fields(self, client):
        create_resp = client.post("/api/materials", json={
            "name": "Custom Pt precursor",
            "category": "Metal precursor",
            "formula": "H2PtCl6",
            "price": 250.0,
            "price_unit": "$/lb",
            "source": "user",
            "catalyst_domain": "thermal",
        })
        assert create_resp.status_code == 200
        material_id = create_resp.json()["id"]

        patch_resp = client.patch(f"/api/materials/{material_id}", json={
            "name": "Custom Pt precursor rev A",
            "price": 275.0,
            "reference_url": "https://example.com/pt-precursor",
            "application_family": "fuel_cell",
        })
        assert patch_resp.status_code == 200
        payload = patch_resp.json()
        assert payload["name"] == "Custom Pt precursor rev A"
        assert payload["price"] == pytest.approx(275.0)
        assert payload["reference_url"] == "https://example.com/pt-precursor"
        assert payload["application_family"] == "fuel_cell"

    def test_delete_custom_material_removes_row(self, client):
        create_resp = client.post("/api/materials", json={
            "name": "Custom Ni nitrate",
            "category": "Metal precursor",
            "formula": "Ni(NO3)2",
            "price": 22.0,
            "price_unit": "$/lb",
            "source": "user",
            "catalyst_domain": "thermal",
        })
        assert create_resp.status_code == 200
        material_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/api/materials/{material_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json() == {"status": "deleted", "id": material_id}

        detail_resp = client.get(f"/api/materials/{material_id}")
        assert detail_resp.status_code == 404
        list_resp = client.get("/api/materials?q=Custom Ni nitrate")
        assert list_resp.status_code == 200
        assert not any(item["name"] == "Custom Ni nitrate" for item in list_resp.json())

    def test_get_unknown_material_returns_clean_404_detail(self, client):
        resp = client.get("/api/materials/999999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Material not found"

    def test_material_mutations_return_404_for_unknown_custom_id(self, client):
        patch_resp = client.patch("/api/materials/999999", json={"name": "missing"})
        assert patch_resp.status_code == 404
        assert patch_resp.json()["detail"] == "Material not found"

        delete_resp = client.delete("/api/materials/999999")
        assert delete_resp.status_code == 404
        assert delete_resp.json()["detail"] == "Material not found"

    def test_material_mutations_reject_non_custom_library_rows(self, client, session):
        bundled = session.exec(select(Material).where(Material.is_custom == False)).first()  # noqa: E712
        assert bundled is not None

        detail_resp = client.get(f"/api/materials/{bundled.id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["id"] == (bundled.library_key or str(bundled.id))
        assert detail["name"] == bundled.name
        assert detail["is_custom"] is False

        patch_resp = client.patch(f"/api/materials/{bundled.id}", json={"name": "should fail"})
        assert patch_resp.status_code == 403
        assert patch_resp.json()["detail"] == "Bundled library materials are read-only"

        delete_resp = client.delete(f"/api/materials/{bundled.id}")
        assert delete_resp.status_code == 403
        assert delete_resp.json()["detail"] == "Bundled library materials are read-only"

    def test_list_domains(self, client):
        resp = client.get("/api/materials/domains")
        assert resp.status_code == 200
        data = resp.json()
        assert "thermal" in data

    def test_list_application_families(self, client):
        resp = client.get("/api/materials/applications")
        assert resp.status_code == 200
        data = resp.json()
        assert "general" in data

    def test_list_templates(self, client):
        resp = client.get("/api/materials/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 3
        assert any(item["catalyst_domain"] == "electrocatalyst" for item in data)

    def test_list_thermal_composition_options(self, client):
        resp = client.get("/api/materials/composition-options?catalyst_domain=thermal")
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["max_components"] == 4
        assert payload["active_metal_options"]
        assert payload["promoter_options"]
        assert payload["support_options"]
        assert any(item["material_key"] for item in payload["support_options"])
        assert any(item["display_name"] == "Al2O3" for item in payload["support_options"])
        assert any(item["display_name"] == "Carbon" for item in payload["support_options"])
        assert any(item["display_name"] == "Pt" for item in payload["active_metal_options"])
        assert "Co(NO3)2*6H2O" not in {item["display_name"] for item in payload["active_metal_options"]}
        assert "H2PtCl6*xH2O" not in {item["display_name"] for item in payload["active_metal_options"]}
        assert "Sodium silicate, 41 deg. solid, 3.22-3.25 ratio bulk, c.l., t.l., frt. equald." not in {
            item["display_name"] for item in payload["support_options"]
        }

    def test_curated_material_price_metadata_is_exposed(self, client):
        resp = client.get("/api/materials?q=Sigma 244074")
        assert resp.status_code == 200
        data = resp.json()
        assert data
        record = data[0]
        assert record["price"] == pytest.approx(0.284)
        assert record["price_unit"] == "$/g"
        assert record["pack_quantity"] == pytest.approx(500)
        assert record["pack_unit"] == "g"
        assert record["pricing_basis"] == "largest_pack_unit_price"
        assert "sigmaaldrich.com" in record["reference_url"]

    def test_domain_filter_includes_general_curated_rows(self, client):
        resp = client.get("/api/materials?catalyst_domain=electrocatalyst&q=Nickel(II) nitrate")
        assert resp.status_code == 200
        data = resp.json()
        assert data
        assert any("Nickel(II) nitrate" in item["name"] for item in data)

    def test_filter_by_application_family(self, client):
        create_resp = client.post("/api/materials", json={
            "name": "PEM ionomer dispersion",
            "category": "Ionomer",
            "price": 125.0,
            "price_unit": "$/mL",
            "source": "user",
            "catalyst_domain": "electrocatalyst",
            "application_family": "fuel_cell",
            "pricing_basis": "user_entered",
        })
        assert create_resp.status_code == 200

        filter_resp = client.get("/api/materials?application_family=fuel_cell&q=ionomer")
        assert filter_resp.status_code == 200
        payload = filter_resp.json()
        assert payload
        assert any(item["name"] == "PEM ionomer dispersion" for item in payload)
        assert all(item["application_family"] in {"fuel_cell", "general"} for item in payload)

    def test_application_family_filter_includes_general_aem_rows(self, client):
        resp = client.get("/api/materials?application_family=fuel_cell&q=PiperION")
        assert resp.status_code == 200
        data = resp.json()
        assert data
        assert any("PiperION" in item["name"] for item in data)
        assert all(item["application_family"] in {"fuel_cell", "general"} for item in data)

    def test_get_template(self, client):
        resp = client.get("/api/materials/templates/wet_impregnation_metal_oxide")
        assert resp.status_code == 200
        data = resp.json()
        assert "steps" in data

    def test_get_electrocatalyst_template(self, client):
        resp = client.get("/api/materials/templates/pem_fuel_cell_ccm")
        assert resp.status_code == 200
        data = resp.json()
        assert data["catalyst_domain"] == "electrocatalyst"
        assert data["preprocess"]

    def test_get_aem_electrocatalyst_template(self, client):
        resp = client.get("/api/materials/templates/aem_fuel_cell_ccm")
        assert resp.status_code == 200
        data = resp.json()
        assert data["catalyst_domain"] == "electrocatalyst"
        assert "ion_exchange_conversion" in data["steps"]

    def test_get_unknown_template_via_legacy_alias_returns_clean_404(self, client):
        resp = client.get("/api/materials/templates/does-not-exist")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Template 'does-not-exist' not found"

    def test_list_steps(self, client):
        resp = client.get("/api/materials/steps")
        assert resp.status_code == 200
        data = resp.json()
        assert any(step["key"] == "mixer_slurry" for step in data)
        assert any(step["key"] == "ccm_coating_pass" for step in data)


class TestCatalogRoutes:
    def test_list_templates_via_dedicated_endpoint(self, client):
        resp = client.get("/api/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 3
        assert any(item["catalyst_domain"] == "electrocatalyst" for item in data)

    def test_get_template_via_dedicated_endpoint(self, client):
        resp = client.get("/api/templates/wet_impregnation_metal_oxide")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "wet_impregnation_metal_oxide"
        assert data["catalyst_domain"] == "thermal"
        assert data["steps"]

    def test_get_unknown_template_via_dedicated_endpoint_returns_clean_404(self, client):
        resp = client.get("/api/templates/does-not-exist")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Template 'does-not-exist' not found"

    def test_list_equipment_via_dedicated_endpoint_matches_legacy_alias(self, client):
        dedicated = client.get("/api/equipment?category=dryer&q=rotary")
        legacy = client.get("/api/materials/equipment?category=dryer&q=rotary")
        assert dedicated.status_code == 200
        assert legacy.status_code == 200
        assert dedicated.json()
        assert dedicated.json() == legacy.json()

    def test_get_bundled_equipment_detail_via_legacy_alias(self, client):
        dedicated_list = client.get("/api/equipment?category=Agitators&q=Propeller for open tank")
        assert dedicated_list.status_code == 200
        bundled = dedicated_list.json()[0]

        dedicated_detail = client.get(f"/api/equipment/{bundled['id']}")
        legacy_detail = client.get(f"/api/materials/equipment/{bundled['id']}")
        assert dedicated_detail.status_code == 200
        assert legacy_detail.status_code == 200
        assert legacy_detail.json() == dedicated_detail.json()

    def test_get_unknown_equipment_detail_via_legacy_alias_returns_clean_404(self, client):
        resp = client.get("/api/materials/equipment/999999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Equipment not found"

    def test_list_bundled_equipment_includes_stable_string_ids(self, client):
        resp = client.get("/api/equipment?category=Agitators&q=Propeller for open tank")
        assert resp.status_code == 200
        payload = resp.json()
        assert payload
        record = payload[0]
        assert record["name"] == "Propeller for open tank"
        assert isinstance(record["id"], str)
        assert record["id"].startswith("bundled:")
        assert record["is_custom"] is False


class TestEquipmentCustomLibrary:
    def test_get_bundled_equipment_detail(self, client):
        list_resp = client.get("/api/equipment?category=Agitators&q=Propeller for open tank")
        assert list_resp.status_code == 200
        bundled = list_resp.json()[0]

        detail_resp = client.get(f"/api/equipment/{bundled['id']}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["id"] == bundled["id"]
        assert detail["name"] == "Propeller for open tank"
        assert detail["category"] == "Agitators"
        assert detail["materials"]
        assert detail["is_custom"] is False

    def test_create_custom_equipment_and_list_it_via_dedicated_endpoint(self, client):
        create_resp = client.post("/api/equipment", json={
            "category": "Dryers",
            "name": "Pilot rotary dryer",
            "size_units": "kg/h",
            "s_lower": 5.0,
            "s_upper": 50.0,
            "a": 12000.0,
            "b": 150.0,
            "n": 0.82,
            "function_type": "1 - Power Law",
            "source": "user",
            "year": 2026,
            "pricing_basis": "316 stainless steel",
            "installation_factor": 1.4,
            "labor_factor": 0.25,
            "note": "Pilot-scale drying train",
            "materials": ["316 stainless steel"],
            "material_factors": [1.0],
        })
        assert create_resp.status_code == 200
        created = create_resp.json()
        assert created["id"] > 0
        assert created["name"] == "Pilot rotary dryer"
        assert created["is_custom"] is True

        list_resp = client.get("/api/equipment?category=Dryers&q=Pilot rotary")
        assert list_resp.status_code == 200
        payload = list_resp.json()
        assert any(item["name"] == "Pilot rotary dryer" for item in payload)
        record = next(item for item in payload if item["name"] == "Pilot rotary dryer")
        assert record["materials"] == ["316 stainless steel"]
        assert record["material_factors"] == [1.0]

    def test_get_custom_equipment_detail(self, client):
        create_resp = client.post("/api/equipment", json={
            "category": "Reactors",
            "name": "Bench slurry reactor",
            "size_units": "L",
            "s_lower": 1.0,
            "s_upper": 25.0,
            "a": 9500.0,
            "b": 80.0,
            "n": 0.9,
            "function_type": "1 - Power Law",
            "source": "user",
            "year": 2026,
            "pricing_basis": "glass-lined steel",
            "installation_factor": 1.2,
            "labor_factor": 0.1,
            "materials": ["Glass-lined steel"],
            "material_factors": [1.0],
        })
        assert create_resp.status_code == 200
        equipment_id = create_resp.json()["id"]

        detail_resp = client.get(f"/api/equipment/{equipment_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["name"] == "Bench slurry reactor"
        assert detail["category"] == "Reactors"
        assert detail["materials"] == ["Glass-lined steel"]

    def test_get_custom_equipment_detail_via_legacy_alias(self, client):
        create_resp = client.post("/api/equipment", json={
            "category": "Reactors",
            "name": "Bench slurry reactor",
            "size_units": "L",
            "s_lower": 1.0,
            "s_upper": 25.0,
            "a": 9500.0,
            "b": 80.0,
            "n": 0.9,
            "function_type": "1 - Power Law",
            "source": "user",
            "year": 2026,
            "pricing_basis": "glass-lined steel",
            "installation_factor": 1.2,
            "labor_factor": 0.1,
            "materials": ["Glass-lined steel"],
            "material_factors": [1.0],
        })
        assert create_resp.status_code == 200
        equipment_id = create_resp.json()["id"]

        dedicated_detail = client.get(f"/api/equipment/{equipment_id}")
        legacy_detail = client.get(f"/api/materials/equipment/{equipment_id}")
        assert dedicated_detail.status_code == 200
        assert legacy_detail.status_code == 200
        assert legacy_detail.json() == dedicated_detail.json()

    def test_get_custom_equipment_detail_returns_404_for_unknown_id(self, client):
        resp = client.get("/api/equipment/999999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Equipment not found"

    def test_patch_custom_equipment_updates_mutable_fields(self, client):
        create_resp = client.post("/api/equipment", json={
            "category": "Dryers",
            "name": "Pilot rotary dryer",
            "size_units": "kg/h",
            "s_lower": 5.0,
            "s_upper": 50.0,
            "a": 12000.0,
            "b": 150.0,
            "n": 0.82,
            "function_type": "1 - Power Law",
            "source": "user",
            "year": 2026,
            "pricing_basis": "316 stainless steel",
            "installation_factor": 1.4,
            "labor_factor": 0.25,
            "note": "Pilot-scale drying train",
            "materials": ["316 stainless steel"],
            "material_factors": [1.0],
        })
        assert create_resp.status_code == 200
        equipment_id = create_resp.json()["id"]

        patch_resp = client.patch(f"/api/equipment/{equipment_id}", json={
            "name": "Pilot rotary dryer rev A",
            "installation_factor": 1.55,
            "note": "Updated after vendor quote",
            "materials": ["316 stainless steel", "PTFE liner"],
            "material_factors": [1.0, 1.08],
        })
        assert patch_resp.status_code == 200
        payload = patch_resp.json()
        assert payload["name"] == "Pilot rotary dryer rev A"
        assert payload["installation_factor"] == pytest.approx(1.55)
        assert payload["note"] == "Updated after vendor quote"
        assert payload["materials"] == ["316 stainless steel", "PTFE liner"]
        assert payload["material_factors"] == [1.0, 1.08]

    def test_patch_custom_equipment_returns_404_for_unknown_id(self, client):
        resp = client.patch("/api/equipment/999999", json={"name": "missing"})
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Equipment not found"

    def test_delete_custom_equipment_removes_row(self, client):
        create_resp = client.post("/api/equipment", json={
            "category": "Reactors",
            "name": "Bench slurry reactor",
            "size_units": "L",
            "s_lower": 1.0,
            "s_upper": 25.0,
            "a": 9500.0,
            "b": 80.0,
            "n": 0.9,
            "function_type": "1 - Power Law",
            "source": "user",
            "year": 2026,
            "pricing_basis": "glass-lined steel",
            "installation_factor": 1.2,
            "labor_factor": 0.1,
            "materials": ["Glass-lined steel"],
            "material_factors": [1.0],
        })
        assert create_resp.status_code == 200
        equipment_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/api/equipment/{equipment_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json() == {"status": "deleted", "id": equipment_id}

        detail_resp = client.get(f"/api/equipment/{equipment_id}")
        assert detail_resp.status_code == 404
        list_resp = client.get("/api/equipment?category=Reactors&q=Bench slurry")
        assert list_resp.status_code == 200
        assert not any(item["name"] == "Bench slurry reactor" for item in list_resp.json())

    def test_delete_custom_equipment_returns_404_for_unknown_id(self, client):
        resp = client.delete("/api/equipment/999999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Equipment not found"

    def test_equipment_cors_preflight_allows_patch_and_delete(self, client):
        patch_resp = client.options(
            "/api/equipment/1",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "PATCH",
            },
        )
        assert patch_resp.status_code == 200
        assert "PATCH" in patch_resp.headers["access-control-allow-methods"]

        delete_resp = client.options(
            "/api/equipment/1",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "DELETE",
            },
        )
        assert delete_resp.status_code == 200
        assert "DELETE" in delete_resp.headers["access-control-allow-methods"]


class TestIndexRoutes:
    def test_get_chemppi_index_payload(self, client):
        resp = client.get("/api/indices/chemppi")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "1.1.1"
        assert data["series_id"] == "PCU325---325---"
        assert data["annual"]["2018"] == pytest.approx(290.1583333333333)

    def test_get_cepci_index_payload(self, client):
        resp = client.get("/api/indices/cepci")
        assert resp.status_code == 200
        data = resp.json()
        assert data["version"] == "1.1.1"
        assert data["annual"]["2018"]["CEPCI"] == pytest.approx(603.1)
        assert data["annual"]["2018"]["CEPCI_equip"] == pytest.approx(734.1)


class TestImportExport:
    def test_import_rejects_non_json_extension(self, client):
        resp = client.post(
            "/api/import/catcost",
            files={"file": ("bad.txt", b"{}", "text/plain")},
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Only .json files are accepted"

    def test_import_rejects_malformed_json_with_clean_detail(self, client):
        resp = client.post(
            "/api/import/catcost",
            files={"file": ("bad.json", b"{", "application/json")},
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Invalid JSON file"

    def test_import_rejects_large_json_payload(self, client):
        oversized_payload = {"blob": "x" * MAX_IMPORT_BYTES}
        resp = client.post(
            "/api/import/catcost",
            files={"file": ("oversized.json", json.dumps(oversized_payload).encode("utf-8"), "application/json")},
        )
        assert resp.status_code == 413
        assert resp.json()["detail"] == "Imported JSON exceeds the 1 MiB size limit"

    def test_import_requires_top_level_object(self, client):
        resp = client.post(
            "/api/import/catcost",
            files={"file": ("array.json", b"[1, 2, 3]", "application/json")},
        )
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Imported JSON must contain a top-level object"

    def test_save_estimate_then_export_json(self, client):
        save_resp = client.post(
            "/api/calculate/save?name=Ni%20baseline",
            json={
                "metal_symbol": "Ni",
                "metal_price": 7.50,
                "metal_price_unit": "$/lb",
                "metal_loading_wt_pct": 15.0,
                "support_name": "Al2O3",
                "support_price_per_lb": 0.50,
                "steps": ["mixer_slurry", "incipient_wetness"],
                "order_size_tons": 10.0,
            },
        )
        assert save_resp.status_code == 200
        saved = save_resp.json()
        assert saved["id"] > 0

        export_resp = client.get(f"/api/export/{saved['id']}")
        assert export_resp.status_code == 200
        payload = export_resp.json()
        assert payload["name"] == "Ni baseline"
        assert payload["created_at"].endswith("+00:00")
        assert payload["input"]["metal_symbol"] == "Ni"
        assert payload["result"]["summary"]["estimated_price_per_lb"] > 0

    def test_export_saved_estimate_as_csv_text(self, client):
        save_resp = client.post(
            "/api/calculate/save?name=Pt%20baseline",
            json={
                "metal_symbol": "Pt",
                "metal_price": 950.0,
                "metal_price_unit": "$/troy_oz",
                "metal_loading_wt_pct": 2.0,
                "support_name": "Al2O3",
                "support_price_per_lb": 0.50,
                "steps": ["mixer_slurry", "incipient_wetness"],
                "order_size_tons": 2.0,
            },
        )
        assert save_resp.status_code == 200
        estimate_id = save_resp.json()["id"]

        export_resp = client.get(f"/api/export/{estimate_id}?format=csv")
        assert export_resp.status_code == 200
        assert export_resp.headers["content-type"].startswith("text/csv")
        lines = export_resp.text.strip().splitlines()
        assert lines[0] == "metric,value"
        assert any(line.startswith("estimated_price_per_lb,") for line in lines)
        assert any(line.startswith("estimated_price_per_kg,") for line in lines)

    def test_export_returns_404_for_unknown_saved_estimate(self, client):
        resp = client.get("/api/export/999999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Estimate not found"

    def test_export_rejects_unsupported_format(self, client):
        save_resp = _save_estimate(client, "Ni baseline")
        assert save_resp.status_code == 200
        estimate_id = save_resp.json()["id"]

        resp = client.get(f"/api/export/{estimate_id}?format=xml")
        assert resp.status_code == 400
        assert resp.json()["detail"] == "Unsupported format: xml"


class TestSavedEstimates:
    def test_list_saved_estimates_returns_newest_first_with_summary_fields(self, client):
        first = _save_estimate(client, "Ni baseline")
        assert first.status_code == 200

        second = _save_estimate(
            client,
            "Pt benchmark",
            metal_symbol="Pt",
            metal_price=950.0,
            metal_price_unit="$/troy_oz",
            metal_loading_wt_pct=2.0,
            order_size_tons=2.0,
        )
        assert second.status_code == 200

        resp = client.get("/api/estimates")
        assert resp.status_code == 200
        payload = resp.json()
        assert len(payload) >= 2
        assert payload[0]["id"] == second.json()["id"]
        assert payload[0]["name"] == "Pt benchmark"
        assert payload[0]["created_at"].endswith("+00:00")
        assert payload[0]["estimated_price_per_lb"] > 0
        assert payload[1]["id"] == first.json()["id"]

    def test_get_saved_estimate_detail_returns_input_and_result_payloads(self, client):
        save_resp = _save_estimate(client, "Ni baseline")
        assert save_resp.status_code == 200
        estimate_id = save_resp.json()["id"]

        resp = client.get(f"/api/estimates/{estimate_id}")
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["id"] == estimate_id
        assert payload["name"] == "Ni baseline"
        assert payload["created_at"].endswith("+00:00")
        assert payload["input"]["metal_symbol"] == "Ni"
        assert payload["result"]["summary"]["estimated_price_per_lb"] > 0

    def test_delete_saved_estimate_removes_it_from_catalog(self, client):
        save_resp = _save_estimate(client, "Delete me")
        assert save_resp.status_code == 200
        estimate_id = save_resp.json()["id"]

        delete_resp = client.delete(f"/api/estimates/{estimate_id}")
        assert delete_resp.status_code == 200
        assert delete_resp.json() == {"status": "deleted", "id": estimate_id}

        detail_resp = client.get(f"/api/estimates/{estimate_id}")
        assert detail_resp.status_code == 404

    def test_get_saved_estimate_returns_404_for_unknown_id(self, client):
        resp = client.get("/api/estimates/999999")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Estimate not found"


class TestDecision:
    def test_list_benchmark_families(self, client):
        resp = client.get("/api/decision/benchmarks")
        assert resp.status_code == 200
        data = resp.json()
        assert data["families"]
        families = {item["family"] for item in data["families"]}
        assert "ammonia-cracking" in families
        assert "co2-methanol" in families
        assert "co2-methanation" in families
        assert "formic-acid-dehydrogenation" in families
        assert "rwgs" in families
        assert "dry-reforming" in families
        assert "water-gas-shift" in families
        assert "fuel-cell-orr" in families
        assert "aem-electrolyzer-oer" in families
        assert "pem-electrolyzer-oer" in families
        assert all("catalyst_domain" in item for item in data["families"])

    def test_get_unknown_benchmark_family_returns_clean_404_detail(self, client):
        resp = client.get("/api/decision/benchmarks/does-not-exist")
        assert resp.status_code == 404
        payload = resp.json()
        assert payload["detail"] == "Unknown benchmark family: does-not-exist"

    def test_get_ammonia_cracking_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/ammonia-cracking")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert len(data["candidates"]) >= 3
        assert data["decision_profile"]["id"] == "balanced"
        assert data["catalyst_domain"] == "thermal"
        assert all("scores" in candidate for candidate in data["candidates"])

    def test_get_fuel_cell_orr_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/fuel-cell-orr")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert data["catalyst_domain"] == "electrocatalyst"
        assert data["application_family"] == "fuel_cell"
        assert len(data["candidates"]) >= 3
        assert all(candidate["catalyst_domain"] == "electrocatalyst" for candidate in data["candidates"])
        assert any(candidate["route"]["calculator_template_id"] == "pem_fuel_cell_ccm" for candidate in data["candidates"])

    def test_get_pem_electrolyzer_oer_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/pem-electrolyzer-oer")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert data["catalyst_domain"] == "electrocatalyst"
        assert data["application_family"] == "electrolyzer"
        assert len(data["candidates"]) >= 3
        assert all(candidate["route"]["calculator_template_id"] == "pem_electrolyzer_ccm" for candidate in data["candidates"])
        assert all(candidate["summary"]["economics_basis_unit"] == "$/cm2" for candidate in data["candidates"])
        assert all(candidate["electrode_defaults"]["substrate_material_key"] for candidate in data["candidates"])

    def test_get_co2_methanol_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/co2-methanol")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert data["catalyst_domain"] == "thermal"
        assert len(data["candidates"]) >= 3
        assert any(candidate["slug"] == "cza-baseline" for candidate in data["candidates"])

    def test_get_rwgs_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/rwgs")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert data["catalyst_domain"] == "thermal"
        assert len(data["candidates"]) >= 3
        assert any(candidate["slug"] == "mo2n-hightemp" for candidate in data["candidates"])

    def test_get_dry_reforming_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/dry-reforming")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert data["catalyst_domain"] == "thermal"
        assert len(data["candidates"]) >= 3
        assert any(candidate["slug"] == "ni-single-atom-ceria" for candidate in data["candidates"])

    def test_get_water_gas_shift_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/water-gas-shift")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert data["catalyst_domain"] == "thermal"
        assert len(data["candidates"]) >= 3
        assert any(candidate["slug"] == "co-ceria-interface" for candidate in data["candidates"])

    def test_get_co2_methanation_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/co2-methanation")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert data["catalyst_domain"] == "thermal"
        assert len(data["candidates"]) >= 3
        assert any(candidate["slug"] == "ni-alumina-baseline" for candidate in data["candidates"])

    def test_get_formic_acid_dehydrogenation_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/formic-acid-dehydrogenation")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert data["catalyst_domain"] == "thermal"
        assert len(data["candidates"]) >= 3
        assert any(candidate["slug"] == "co-nc-nonnoble" for candidate in data["candidates"])

    def test_get_aem_electrolyzer_oer_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/aem-electrolyzer-oer")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert data["catalyst_domain"] == "electrocatalyst"
        assert data["application_family"] == "electrolyzer"
        assert len(data["candidates"]) >= 3
        assert all(candidate["route"]["calculator_template_id"] == "alkaline_electrolyzer_gde" for candidate in data["candidates"])
        assert all(candidate["summary"]["economics_basis_unit"] == "$/cm2" for candidate in data["candidates"])
        assert all(candidate["electrode_defaults"]["membrane_material_key"] for candidate in data["candidates"])
