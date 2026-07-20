"""Guard against release-version drift across the repo's version-bearing files."""

import json
import re
from pathlib import Path

from backend.main import APP_VERSION

ROOT = Path(__file__).resolve().parents[2]


def test_all_version_sources_agree():
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    frontend = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))[
        "version"
    ]
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pyproject = re.search(r'^version\s*=\s*"([^"]+)"', pyproject_text, re.M).group(1)

    assert package == frontend == pyproject == APP_VERSION, (
        f"Version drift: package.json={package}, frontend={frontend}, "
        f"pyproject.toml={pyproject}, backend APP_VERSION={APP_VERSION}"
    )
