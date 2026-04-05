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
