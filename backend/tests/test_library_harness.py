"""Harness tests for bundled library sources and pricing helpers."""

from __future__ import annotations

import json

import pytest
from sqlmodel import select

from backend.core.material_pricing import (
    area_price_to_per_cm2,
    mass_price_to_per_kg,
    mass_price_to_per_lb,
    volume_price_to_per_ml,
)
from backend.models.material import Material
from backend.paths import data_dir


def _load_json(name: str) -> dict:
    with open(data_dir() / name, encoding="utf-8") as handle:
        return json.load(handle)


def test_curated_library_rows_have_traceable_source_metadata() -> None:
    files = ("materials_curated.json", "electrocatalyst_library.json")
    for filename in files:
        payload = _load_json(filename)
        assert payload["materials"], f"{filename} should contain at least one material row"
        for row in payload["materials"]:
            assert row.get("library_key"), f"{filename}: missing library_key for {row.get('name')}"
            assert row.get("name"), f"{filename}: missing name"
            assert row.get("source"), f"{filename}: missing source for {row.get('library_key')}"
            assert row.get("quote_year"), f"{filename}: missing quote_year for {row.get('library_key')}"
            assert row.get("pricing_basis"), f"{filename}: missing pricing_basis for {row.get('library_key')}"
            assert row.get("reference_url"), f"{filename}: missing reference_url for {row.get('library_key')}"
            assert row.get("price") is not None, f"{filename}: missing price for {row.get('library_key')}"
            assert row.get("price_unit"), f"{filename}: missing price_unit for {row.get('library_key')}"


def test_electrocatalyst_templates_reference_known_steps_and_sources() -> None:
    step_keys = {step["key"] for step in _load_json("step_library.json")["steps"]}
    template_names = (
        "pem_fuel_cell_ccm.json",
        "pem_electrolyzer_ccm.json",
        "dmfc_gde_route.json",
        "aem_fuel_cell_ccm.json",
        "alkaline_electrolyzer_gde.json",
    )

    for filename in template_names:
        template = _load_json(f"process_templates/{filename}")
        assert template["catalyst_domain"] == "electrocatalyst"
        assert template["source"], f"{filename}: source should be populated"
        assert template["reference_urls"], f"{filename}: reference_urls should not be empty"
        assert template["preprocess"], f"{filename}: preprocess should not be empty"
        assert template["synthesis"], f"{filename}: synthesis should not be empty"
        assert template["postprocess"], f"{filename}: postprocess should not be empty"
        assert set(template["steps"]).issubset(step_keys), f"{filename}: unknown step key detected"


def test_material_pricing_helpers_cover_mass_volume_and_area_units() -> None:
    assert mass_price_to_per_lb(1.0, "$/g") == pytest.approx(453.59237)
    assert mass_price_to_per_kg(0.284, "$/g") == pytest.approx(284.0, abs=1e-3)
    assert volume_price_to_per_ml(2000.0, "$/L") == pytest.approx(2.0)
    assert area_price_to_per_cm2(500.0, "$/m2") == pytest.approx(0.05)


def test_material_pricing_helpers_reject_unsupported_mass_units() -> None:
    with pytest.raises(ValueError) as excinfo:
        mass_price_to_per_lb(1.0, "$/stone")
    assert str(excinfo.value) == "Unsupported mass price unit: $/stone"


def test_material_pricing_helpers_reject_unsupported_volume_units() -> None:
    with pytest.raises(ValueError) as excinfo:
        volume_price_to_per_ml(1.0, "$/gallon")
    assert str(excinfo.value) == "Unsupported volume price unit: $/gallon"


def test_seeded_library_contains_sigma_and_fuel_cell_store_rows(session) -> None:
    keys = set(
        session.exec(select(Material.library_key).where(Material.is_custom == False)).all()  # noqa: E712
    )
    assert "sigma:244074" in keys
    assert "fcs:xt-pt20-vulcan-s" in keys
    assert "sigma:203548" in keys
    assert "fcs:sustainion-xa9-25ml" in keys
    assert "fcs:ptru-gde-paper-2" in keys
    assert "fcs:ag40-vulcan" in keys
    assert "lit:usgs-alumina-2025" in keys
    assert "lit:usgs-ceria-2025" in keys
    assert "lit:usgs-indium-metal-2025" in keys
    assert "lit:dti-pem-membrane-2010" in keys
    assert "lit:dti-pem-ionomer-2010" in keys
    assert "lit:dti-pem-gdl-2010" in keys


def test_benchmark_catalogs_have_traceable_routes_and_citations() -> None:
    step_keys = {step["key"] for step in _load_json("step_library.json")["steps"]}

    for path in sorted(data_dir().glob("*_benchmark.json")):
        payload = _load_json(path.name)
        citation_ids = {citation["id"] for citation in payload["citations"]}
        route_ids = {route["id"] for route in payload["route_templates"]}

        assert payload["family"], f"{path.name}: family should be populated"
        assert payload["candidates"], f"{path.name}: candidates should not be empty"
        assert payload["citations"], f"{path.name}: citations should not be empty"
        assert payload["route_templates"], f"{path.name}: route_templates should not be empty"

        for route in payload["route_templates"]:
            assert route["name"], f"{path.name}: route name missing"
            assert route["steps"], f"{path.name}: route {route['id']} missing steps"
            assert set(route["steps"]).issubset(step_keys), f"{path.name}: route {route['id']} uses unknown step key"
            assert route["preprocess"], f"{path.name}: route {route['id']} missing preprocess"
            assert route["synthesis"], f"{path.name}: route {route['id']} missing synthesis"
            assert route["postprocess"], f"{path.name}: route {route['id']} missing postprocess"
            assert route["quality_gates"], f"{path.name}: route {route['id']} missing quality_gates"

        for candidate in payload["candidates"]:
            assert candidate["route_template_id"] in route_ids, (
                f"{path.name}: candidate {candidate['slug']} references unknown route_template_id"
            )
            assert candidate["components"], f"{path.name}: candidate {candidate['slug']} missing components"
            assert candidate["literature_basis_ids"], f"{path.name}: candidate {candidate['slug']} missing literature_basis_ids"
            assert set(candidate["literature_basis_ids"]).issubset(citation_ids), (
                f"{path.name}: candidate {candidate['slug']} references unknown citation ids"
            )
