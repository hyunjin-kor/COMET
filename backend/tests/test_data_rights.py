"""Release approval must match the exact data bytes and intended use."""

import hashlib
import json

import pytest

from backend.core.data_rights import check_data_rights


@pytest.fixture
def rights_bundle(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    source = data / "test.json"
    source.write_text('{"synthetic_test_input": true}\n', encoding="utf-8")
    manifest = tmp_path / "rights.json"
    entry = {
        "path": "test.json",
        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "public_distribution": "approved",
        "commercial_use": "pending",
        "reviewer": "synthetic test reviewer",
        "reviewed_on": "2026-09-07",
        "evidence": "synthetic test fixture; not a real rights clearance",
    }
    manifest.write_text(json.dumps({"schema_version": 1, "files": [entry]}), encoding="utf-8")
    return data, manifest, entry


def test_public_permission_does_not_grant_commercial_use(rights_bundle):
    data, manifest, _ = rights_bundle
    assert check_data_rights(data, manifest, "public_distribution") == []
    assert any("commercial_use" in item for item in check_data_rights(data, manifest, "commercial_use"))


def test_changed_data_invalidates_approval(rights_bundle):
    data, manifest, _ = rights_bundle
    (data / "test.json").write_text('{}', encoding="utf-8")
    assert any("hash" in item for item in check_data_rights(data, manifest, "public_distribution"))


def test_new_or_nested_file_cannot_silently_ship(rights_bundle):
    data, manifest, _ = rights_bundle
    (data / "nested").mkdir()
    (data / "nested/new.csv").write_text('unreviewed', encoding="utf-8")
    assert any("nested/new.csv" in item for item in check_data_rights(data, manifest, "public_distribution"))


@pytest.mark.parametrize("field", ["reviewer", "reviewed_on", "evidence"])
def test_approval_without_review_record_fails(rights_bundle, field):
    data, manifest, entry = rights_bundle
    entry[field] = ""
    manifest.write_text(json.dumps({"schema_version": 1, "files": [entry]}), encoding="utf-8")
    assert check_data_rights(data, manifest, "public_distribution")


@pytest.mark.parametrize("content", ["not json", "{}", '{"schema_version":1,"files":[]}', '{"schema_version":1,"files":[null]}'])
def test_missing_or_malformed_manifest_fails_closed(rights_bundle, content):
    data, manifest, _ = rights_bundle
    manifest.write_text(content, encoding="utf-8")
    assert check_data_rights(data, manifest, "public_distribution")
    assert check_data_rights(data, manifest.with_name("absent.json"), "public_distribution")


def test_duplicate_or_outside_paths_are_rejected(rights_bundle):
    data, manifest, entry = rights_bundle
    manifest.write_text(json.dumps({"schema_version": 1, "files": [entry, entry]}), encoding="utf-8")
    assert check_data_rights(data, manifest, "public_distribution")
    entry["path"] = "../test.json"
    manifest.write_text(json.dumps({"schema_version": 1, "files": [entry]}), encoding="utf-8")
    assert check_data_rights(data, manifest, "public_distribution")


def test_unknown_purpose_is_rejected(rights_bundle):
    data, manifest, _ = rights_bundle
    with pytest.raises(ValueError):
        check_data_rights(data, manifest, "skip_review")
