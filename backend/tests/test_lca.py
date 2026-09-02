"""Tests for the cradle-to-gate LCA engine seeded from Nuss & Eckelman 2014."""

from __future__ import annotations

from backend.core.lca import compute_catalyst_lca, list_factors


class TestLcaSeedDataset:
    def test_dataset_has_primary_reference_and_license(self):
        payload = list_factors()
        ref = payload["primary_reference"]
        assert ref["doi"] == "10.1371/journal.pone.0101298"
        assert "Nuss" in ref["citation"]
        assert ref["license"] == "CC BY 4.0"

    def test_dataset_includes_pgms_and_oxide_aliases(self):
        payload = list_factors()
        for symbol in ("Pt", "Pd", "Rh", "Ru", "Ir", "Au", "Ag", "Ce", "La", "Y", "TiO2", "ZrO2"):
            assert symbol in payload["factors"], f"missing {symbol}"
        assert payload["form_aliases"]["Al2O3"] == "Al"
        assert payload["form_aliases"]["CeO2"] == "Ce"

    def test_pt_factor_matches_published_total(self):
        payload = list_factors()
        pt = payload["factors"]["Pt"]
        # Nuss & Eckelman 2014 Table S38 Pt TOTAL: GWP 12500, CED 243000.
        assert pt["gwp_kg_co2eq_per_kg"] == 12500
        assert pt["ced_mj_per_kg"] == 243000


class TestComputeCatalystLca:
    def test_pure_pt_returns_pt_factor(self):
        result = compute_catalyst_lca([{"name": "Pt", "wt_pct": 100.0, "role": "active_metal"}])
        # 100% Pt -> impact equals the Pt factor exactly.
        assert result["gwp_kg_co2eq_per_kg_catalyst"] == 12500.0
        assert result["ced_mj_per_kg_catalyst"] == 243000.0
        assert result["coverage_pct"] == 100.0
        assert result["data_gap_pct"] == 0.0

    def test_pt_on_alumina_uses_alias(self):
        # 5 wt% Pt on Al2O3 -> Al alias resolves; both contribute.
        result = compute_catalyst_lca([
            {"name": "Pt", "wt_pct": 5.0, "role": "active_metal"},
            {"name": "Al2O3", "wt_pct": 95.0, "role": "support"},
        ])
        # 0.05 * 12500 + 0.95 * 8.2 = 625 + 7.79 = 632.79
        assert result["gwp_kg_co2eq_per_kg_catalyst"] == round(0.05 * 12500 + 0.95 * 8.2, 4)
        assert result["coverage_pct"] == 100.0
        # Al2O3 row should report it matched via alias.
        al = next(c for c in result["per_component"] if c["name"] == "Al2O3")
        assert al["matched_key"] == "Al"
        assert al["factor_status"] == "matched_alias"

    def test_unsupported_support_creates_data_gap_with_warning(self):
        # SiO2 / activated carbon are NOT in the seed dataset — must be flagged.
        result = compute_catalyst_lca([
            {"name": "Pt", "wt_pct": 5.0, "role": "active_metal"},
            {"name": "Carbon black", "wt_pct": 95.0, "role": "support"},
        ])
        # Pt contributes 0.05 * 12500 = 625; the Carbon row is excluded.
        assert result["gwp_kg_co2eq_per_kg_catalyst"] == round(0.05 * 12500, 4)
        assert result["data_gap_pct"] == 95.0
        assert result["coverage_pct"] == 5.0
        carbon_row = next(c for c in result["per_component"] if c["name"] == "Carbon black")
        assert carbon_row["matched_key"] is None
        assert carbon_row["factor_status"] == "explicitly_unsupported"
        assert any("Carbon black" in w for w in result["warnings"])
        # Coverage <50% triggers a partial-estimate warning.
        assert any("partial estimate" in w for w in result["warnings"])

    def test_unknown_material_records_data_gap_without_inventing_value(self):
        result = compute_catalyst_lca([
            {"name": "Pt", "wt_pct": 50.0, "role": "active_metal"},
            {"name": "MysteryX", "wt_pct": 50.0, "role": "promoter"},
        ])
        # MysteryX has no factor; gap_pct should be 50.
        assert result["data_gap_pct"] == 50.0
        # Half the catalyst is Pt; half is unknown (treated as zero contribution).
        assert result["gwp_kg_co2eq_per_kg_catalyst"] == round(0.5 * 12500, 4)
        unknown_row = next(c for c in result["per_component"] if c["name"] == "MysteryX")
        assert unknown_row["factor_status"] == "no_factor_in_dataset"

    def test_zero_total_weight_returns_none(self):
        result = compute_catalyst_lca([{"name": "Pt", "wt_pct": 0.0, "role": "active_metal"}])
        # Pydantic schema rejects wt_pct=0 upstream, but the engine itself
        # has to behave when called directly with zero-weight rows.
        assert result["gwp_kg_co2eq_per_kg_catalyst"] is None
        assert result["coverage_pct"] == 0.0

    def test_parenthetical_qualifier_does_not_hide_a_factor(self):
        # Benchmark rows name forms like "TiO2 (anatase)"; the qualifier must
        # not turn a covered material into a data gap.
        result = compute_catalyst_lca([
            {"name": "TiO2 (anatase)", "wt_pct": 99.0, "role": "support"},
            {"name": "Cu (from Cu2O)", "wt_pct": 1.0, "role": "active_metal"},
        ])
        assert result["coverage_pct"] == 100.0
        keys = {c["name"]: c["matched_key"] for c in result["per_component"]}
        assert keys == {"TiO2 (anatase)": "TiO2", "Cu (from Cu2O)": "Cu"}

    def test_oxide_and_compound_aliases_map_to_dominant_element(self):
        result = compute_catalyst_lca([
            {"name": "ZnO", "wt_pct": 40.0}, {"name": "V2O5", "wt_pct": 20.0},
            {"name": "In2O3", "wt_pct": 20.0}, {"name": "MoS2", "wt_pct": 20.0},
        ])
        assert result["coverage_pct"] == 100.0
        keys = {c["name"]: c["matched_key"] for c in result["per_component"]}
        assert keys == {"ZnO": "Zn", "V2O5": "V", "In2O3": "In", "MoS2": "Mo"}

    def test_true_gaps_stay_gaps(self):
        # Carbons, silica and zeolites are not in Nuss & Eckelman; no alias
        # may quietly map them onto an element.
        result = compute_catalyst_lca([
            {"name": "Activated carbon", "wt_pct": 50.0}, {"name": "H-ZSM-5", "wt_pct": 50.0},
        ])
        assert result["coverage_pct"] == 0.0


class TestLcaApi:
    def test_factors_endpoint_returns_dataset(self, client):
        resp = client.get("/api/lca/factors")
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["primary_reference"]["doi"] == "10.1371/journal.pone.0101298"
        assert "Pt" in payload["factors"]

    def test_calculate_endpoint_runs_engine(self, client):
        resp = client.post(
            "/api/lca/calculate",
            json={
                "components": [
                    {"name": "Pt", "wt_pct": 5.0, "role": "active_metal"},
                    {"name": "Al2O3", "wt_pct": 95.0, "role": "support"},
                ]
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert payload["coverage_pct"] == 100.0
        assert payload["gwp_kg_co2eq_per_kg_catalyst"] > 0

    def test_calculate_endpoint_rejects_empty_payload(self, client):
        resp = client.post("/api/lca/calculate", json={"components": []})
        assert resp.status_code == 422


class TestCalculatorIncludesLca:
    def test_calculate_response_includes_lca_block(self, client):
        resp = client.post(
            "/api/calculate",
            json={
                "catalyst_domain": "thermal",
                "order_size_tons": 10.0,
                "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
                "components": [
                    {"role": "active_metal", "name": "Pt", "wt_pct": 5.0, "price_per_lb": 700.0},
                    {"role": "support", "name": "Al2O3", "wt_pct": 95.0, "price_per_lb": 0.5},
                ],
            },
        )
        assert resp.status_code == 200
        payload = resp.json()
        assert "lca" in payload
        assert payload["summary"]["gwp_kg_co2eq_per_kg_catalyst"] > 0
        assert payload["summary"]["lca_coverage_pct"] == 100.0
        # Citation must be embedded so users always know the source.
        assert payload["lca"]["reference"]["doi"] == "10.1371/journal.pone.0101298"
