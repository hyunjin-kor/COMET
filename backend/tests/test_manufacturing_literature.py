"""Source fidelity and cost-boundary checks for literature preparation records."""

import json
from pathlib import Path

import pytest

from backend.core.cost_engine import estimate_catalyst_cost
from backend.core.manufacturing import evaluate_protocol
from backend.core.manufacturing_library import (
    candidate_manufacturing_evidence,
    manufacturing_library,
    reviewed_citation,
)
from backend.schemas.manufacturing import ManufacturingProtocol

DATA = Path(__file__).resolve().parents[1] / "data"


def test_registered_title_replaces_incorrect_catalog_source_description():
    citation = {"url": "https://www.nature.com/articles/s41467-024-47736-0", "note": "Unverified ternary NiFe claim"}
    result = reviewed_citation(citation)
    assert "chromium-doped amorphous electrocatalysts" in result["note"]
    assert "NiFe" not in result["note"]
    assert citation["note"] == "Unverified ternary NiFe claim"


def test_audit_covers_every_candidate_and_generic_template():
    library = manufacturing_library()
    expected = {
        (catalog["family"], candidate["slug"])
        for path in DATA.glob("*_benchmark.json")
        if "candidates" in (catalog := json.loads(path.read_text(encoding="utf-8")))
        for candidate in catalog["candidates"]
    }
    rows = library["candidates"]
    assert {(r["family"], r["slug"]) for r in rows} == expected
    assert len(rows) == len(expected)
    assert {r["id"] for r in library["templates"]} == {
        json.loads(p.read_text(encoding="utf-8"))["id"]
        for p in (DATA / "process_templates").glob("*.json")
    }
    assert all(row["notes"] for row in rows)


def test_curated_sources_are_registered_but_not_automatically_cost_complete():
    library = manufacturing_library()
    sources = {s["doi"]: s for s in library["sources"]}
    for profile in library["profiles"]:
        assert sources[profile["doi"]]["crossref_status"] == "verified"
        assert profile["locator"] and profile["sample"] and profile["limitations"]
        protocol = ManufacturingProtocol(
            operations=profile["operations"], product_basis=profile["boundary"],
            source_record_id=profile["id"], source_note=profile["url"],
        )
        result = evaluate_protocol(protocol)
        assert result["complete"] is False
        assert result["processing_cost_usd_kg"] is None
        assert result["batch_processing_cost_usd"] is None
        for operation in protocol.operations:
            assert operation.measured_energy_kwh is None
            assert operation.equipment_usd_h is None


@pytest.mark.parametrize("family,slug,needle", [
    ("ammonia-cracking", "ni-mgo-ceo2-interface", "CNT"),
    ("co2-methanation", "ni-alumina-baseline", "Y2O3"),
    ("aem-electrolyzer-oer", "cr-doped-amorphous", "binary"),
    ("co2-electroreduction", "sn-formate-co2rr", "Sn"),
])
def test_mismatched_formulations_never_become_verified_recipes(family, slug, needle):
    review = candidate_manufacturing_evidence(family, slug)
    assert review["status"] == "source_mismatch"
    assert needle in " ".join(review["notes"])


def test_overnight_is_not_a_numeric_duration_and_kelvin_is_converted():
    profiles = {p["id"]: p for p in manufacturing_library()["profiles"]}
    drying = profiles["pd-carbon-2024"]["operations"][-1]
    assert drying["temperature_profile"][0]["target_c"] == pytest.approx(69.85)
    assert drying["temperature_profile"][0]["hold_h"] is None
    assert "overnight" in drying["notes"].lower()
    ni = profiles["nimo-powder-2013"]["operations"][1]
    assert "350" in ni["notes"] and "110" in ni["notes"]
    assert not ni.get("temperature_profile")


def test_electrode_records_preserve_cost_and_cannot_use_powder_batch_costing():
    kwargs = dict(
        catalyst_domain="electrocatalyst", application_family="electrolyzer",
        components=[{"role": "active_catalyst", "name": "Ni", "wt_pct": 100, "price_per_lb": 10}],
        steps=["mixer_slurry"], order_size_tons=2,
    )
    baseline = estimate_catalyst_cost(**kwargs)
    protocol = dict(mode="record_only", product_basis="electrode", operations=[{"name": "Electrodeposition", "duration_h": .1}])
    result = estimate_catalyst_cost(**kwargs, manufacturing_protocol=protocol)
    assert result["summary"] == baseline["summary"]
    assert result["manufacturing"]["protocol"]["product_basis"] == "electrode"
    with pytest.raises(ValueError, match="dry-powder"):
        ManufacturingProtocol.model_validate({**protocol, "mode": "batch_cost"})


def test_library_endpoint_and_copy_isolation(client):
    response = client.get("/api/decision/manufacturing-literature")
    assert response.status_code == 200
    assert len(response.json()["candidates"]) == 116
    data = manufacturing_library()
    data["profiles"].clear()
    assert manufacturing_library()["profiles"]


def test_complete_electrode_record_never_reports_powder_cost():
    from backend.tests.test_manufacturing_protocol import protocol

    record = protocol()
    record.update(mode="record_only", product_basis="electrode")
    result = evaluate_protocol(ManufacturingProtocol.model_validate(record))
    assert result["complete"] is False
    assert result["processing_cost_usd_kg"] is None
    assert result["batch_processing_cost_usd"] is None
    assert "Electrode preparation" in result["missing_inputs"][0]


def test_preparation_supplement_counts_and_hash_match_curated_records():
    import hashlib

    root = DATA.parents[1]
    summary = json.loads((root / "docs/paper/manufacturing-2026-09-14/review_summary.json").read_text())
    library = manufacturing_library()
    assert summary["profiles"] == len(library["profiles"])
    assert summary["source_mismatches"] == sum(c["status"] == "source_mismatch" for c in library["candidates"])
    assert summary["source_sha256"] == hashlib.sha256((DATA / "manufacturing_literature.json").read_bytes()).hexdigest()


def test_electrode_source_record_survives_save_reload(client):
    from backend.tests.test_estimate_comparison import _electrode

    source = next(p for p in manufacturing_library()["profiles"] if p["id"] == "nioh2-film-2022")
    record = {"mode": "record_only", "product_basis": "electrode", "source_record_id": source["id"],
              "source_note": source["url"], "operations": source["operations"]}
    payload = {**_electrode(), "manufacturing_protocol": record}
    baseline = client.post("/api/calculate", json=_electrode()).json()
    saved = client.post("/api/calculate/save?name=synthetic-electrode-source-record", json=payload)
    assert saved.status_code == 200, saved.text
    loaded = client.get(f"/api/estimates/{saved.json()['id']}").json()
    assert loaded["input"]["manufacturing_protocol"]["source_record_id"] == source["id"]
    assert loaded["input"]["manufacturing_protocol"]["product_basis"] == "electrode"
    assert loaded["result"]["summary"] == baseline["summary"]
    assert loaded["result"]["manufacturing"]["processing_cost_usd_kg"] is None


def test_explicit_preparation_numbers_retain_source_value_and_locator():
    def check(record, preparation):
        for field, value in record.items():
            if field == "input_evidence":
                continue
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                evidence = record["input_evidence"][field]
                assert evidence["recorded_value"] == value
                assert evidence["doi"] == preparation["doi"]
                assert evidence["locator"] and evidence["accessed_on"]
            if field in {"temperature_profile", "purchases", "gases"}:
                for child in value:
                    check(child, preparation)
    for preparation in manufacturing_library()["profiles"]:
        for operation in preparation["operations"]:
            check(operation, preparation)


def test_nickel_cases_separate_precursor_changes_from_time_and_unknown_output():
    profiles = {p["id"]: p for p in manufacturing_library()["profiles"]}
    a, b = (profiles[f"ni-silica-gen{generation}-2024"] for generation in (1, 4))
    assert a["operations"][6]["temperature_profile"][0]["hold_h"] == 2
    assert b["operations"][6]["temperature_profile"][0]["hold_h"] == 1
    assert a["operations"][0]["purchases"][0]["quantity"] == 2
    assert b["operations"][0]["purchases"][0]["quantity"] == .97
    assert b["operations"][8]["purchases"][0]["quantity"] is None  # approximately 5 mL
    assert "conflicts" in " ".join(a["limitations"])
    for preparation in (a, b):
        protocol = ManufacturingProtocol(operations=preparation["operations"])
        assert protocol.finished_batch_mass_kg is None
        assert evaluate_protocol(protocol)["batch_processing_cost_usd"] is None
        assert all(item.price_usd_per_unit is None for op in protocol.operations for item in op.purchases)


def test_pt_sto_ramp_is_not_misread_as_an_additional_two_hour_hold():
    preparation = next(p for p in manufacturing_library()["profiles"] if p["id"] == "pt-sto-somc-2025")
    hydrothermal = preparation["operations"][5]
    assert hydrothermal["temperature_profile"][0]["ramp_c_per_min"] == 2
    assert hydrothermal["temperature_profile"][0]["hold_h"] is None
    assert hydrothermal["stirring_rpm"] == 400
    ozone = preparation["operations"][10]["gases"][0]
    assert ozone["flow_l_per_min"] == .4
    assert ozone["volume_basis"] == ""  # sccm without stated reference T/p
    assert preparation["operations"][-2]["temperature_profile"][0]["hold_h"] is None


def test_operating_references_preserve_scope_and_do_not_supply_false_measurements(client):
    data = client.get("/api/decision/manufacturing-literature").json()
    refs = {r["id"]: r for r in data["operating_references"]}
    tariff = refs["eia-us-industrial-2025-preliminary"]
    assert tariff["value"] == pytest.approx(8.62 / 100)
    assert tariff["import_field"] == "electricity_usd_kwh"
    assert tariff["evidence"]["recorded_value"] == tariff["value"]
    for reference in refs.values():
        if reference["category"] in {"labor", "equipment"}:
            assert reference["import_field"] is None
            assert reference["evidence"]["kind"] != "measured"
    assert refs["nabertherm-l9-11-skm-manual-2024"]["value"] == 3.4
    assert refs["nabertherm-l9-11-skm-web-2026"]["value"] == 3.7


def test_imported_preparation_keeps_original_quantity_after_save_and_edit(client):
    from backend.tests.test_manufacturing_protocol import payload as base_payload

    preparation = next(p for p in manufacturing_library()["profiles"] if p["id"] == "ni-silica-gen1-2024")
    protocol = {"mode": "record_only", "operations": preparation["operations"], "source_record_id": preparation["id"]}
    protocol["operations"][0]["purchases"][0]["quantity"] = 3
    payload = {**base_payload(), "manufacturing_protocol": protocol}
    saved = client.post("/api/calculate/save?name=source-import-test", json=payload)
    assert saved.status_code == 200, saved.text
    result = client.get(f"/api/estimates/{saved.json()['id']}").json()
    row = next(r for r in result["result"]["manufacturing"]["trace"]["inputs"] if r["path"] == "operations.0.purchases.0.quantity")
    assert row["source_status"] == "modified"
    assert row["value"] == 3 and row["evidence"]["recorded_value"] == 2
    assert result["result"]["manufacturing"]["processing_cost_usd_kg"] is None
