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

    def test_list_templates(self, client):
        resp = client.get("/api/materials/templates")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 3

    def test_get_template(self, client):
        resp = client.get("/api/materials/templates/wet_impregnation_metal_oxide")
        assert resp.status_code == 200
        data = resp.json()
        assert "steps" in data

    def test_list_steps(self, client):
        resp = client.get("/api/materials/steps")
        assert resp.status_code == 200
        data = resp.json()
        assert any(step["key"] == "mixer_slurry" for step in data)


class TestDecision:
    def test_list_benchmark_families(self, client):
        resp = client.get("/api/decision/benchmarks")
        assert resp.status_code == 200
        data = resp.json()
        assert data["families"]
        assert data["families"][0]["family"] == "ammonia-cracking"

    def test_get_ammonia_cracking_benchmark(self, client):
        resp = client.get("/api/decision/benchmarks/ammonia-cracking")
        assert resp.status_code == 200
        data = resp.json()
        assert data["winner"] is not None
        assert len(data["candidates"]) >= 3
        assert data["decision_profile"]["id"] == "balanced"
        assert all("scores" in candidate for candidate in data["candidates"])
