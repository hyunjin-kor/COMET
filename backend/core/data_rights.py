"""Check a review manifest against the exact files intended for distribution.

This is a release control, not an automatic legal opinion. Approval entries must
be supplied by an authorized reviewer after checking the underlying permissions.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path, PurePosixPath

PURPOSES = {"public_distribution", "commercial_use"}


def check_data_rights(data_root: Path, manifest_path: Path, purpose: str) -> list[str]:
    """Return blocking reasons; missing, changed or unreviewed files fail closed."""
    if purpose not in PURPOSES:
        raise ValueError("Unsupported data-rights purpose")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["Rights manifest is missing or unreadable"]
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        return ["Unsupported rights manifest schema"]
    rows = manifest.get("files")
    if not isinstance(rows, list) or not rows:
        return ["Rights manifest has no reviewed file inventory"]

    entries = {}
    errors = []
    for entry in rows:
        if not isinstance(entry, dict):
            errors.append("Invalid file review entry")
            continue
        name = entry.get("path")
        if (not isinstance(name, str) or not name or "\\" in name
                or ":" in name or PurePosixPath(name).is_absolute()
                or ".." in PurePosixPath(name).parts or name in entries):
            errors.append("Invalid or duplicate file review path")
            continue
        entries[name] = entry

    if not data_root.is_dir():
        return errors + ["Data directory is missing"]
    actual = {path.relative_to(data_root).as_posix(): path
              for path in data_root.rglob("*") if path.is_file()}
    if not actual:
        errors.append("Data directory is empty")
    for name in sorted(set(entries) - set(actual)):
        errors.append(f"{name}: reviewed file is missing")
    for name, path in sorted(actual.items()):
        entry = entries.get(name)
        if entry is None:
            errors.append(f"{name}: no review entry")
            continue
        if not path.resolve().is_relative_to(data_root.resolve()):
            errors.append(f"{name}: redirected file outside data directory")
            continue
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            errors.append(f"{name}: unreadable file")
            continue
        if entry.get("sha256") != digest:
            errors.append(f"{name}: hash changed since review")
        if entry.get(purpose) != "approved":
            errors.append(f"{name}: {purpose} not approved")
        for field in ("reviewer", "reviewed_on", "evidence"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                errors.append(f"{name}: missing {field}")
        try:
            date.fromisoformat(entry.get("reviewed_on", ""))
        except (TypeError, ValueError):
            errors.append(f"{name}: invalid review date")
    return errors
