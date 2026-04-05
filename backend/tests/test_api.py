"""FastAPI endpoint integration tests."""

import pytest


class TestHealth:
    def test_health(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


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


class TestDecision:
    def test_list_benchmark_families(self, client):
        resp = client.get("/api/decision/benchmarks")
        assert resp.status_code == 200
        data = resp.json()
        assert data["families"]
        families = {item["family"] for item in data["families"]}
        assert "ammonia-cracking" in families
        assert "fuel-cell-orr" in families
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
