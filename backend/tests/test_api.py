"""FastAPI endpoint integration tests."""

import json

import pytest

from backend.routers.catcost_import import MAX_IMPORT_BYTES


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

    def test_security_headers_are_applied(self, client):
        resp = client.get("/api/health")
        assert resp.headers["X-Content-Type-Options"] == "nosniff"
        assert resp.headers["X-Frame-Options"] == "DENY"
        assert resp.headers["Referrer-Policy"] == "no-referrer"
        assert resp.headers["Cache-Control"] == "no-store"


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
        assert "at most four total components" in resp.text


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

    def test_list_steps(self, client):
        resp = client.get("/api/materials/steps")
        assert resp.status_code == 200
        data = resp.json()
        assert any(step["key"] == "mixer_slurry" for step in data)
        assert any(step["key"] == "ccm_coating_pass" for step in data)


class TestImportExport:
    def test_import_rejects_large_json_payload(self, client):
        oversized_payload = {"blob": "x" * MAX_IMPORT_BYTES}
        resp = client.post(
            "/api/import/catcost",
            files={"file": ("oversized.json", json.dumps(oversized_payload).encode("utf-8"), "application/json")},
        )
        assert resp.status_code == 413

    def test_import_requires_top_level_object(self, client):
        resp = client.post(
            "/api/import/catcost",
            files={"file": ("array.json", b"[1, 2, 3]", "application/json")},
        )
        assert resp.status_code == 400
        assert "top-level object" in resp.text


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
