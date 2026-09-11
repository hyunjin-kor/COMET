"""Check data reuse approvals before a public release or commercial deployment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.core.data_rights import PURPOSES, check_data_rights  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "backend/data")
    parser.add_argument("--manifest", type=Path, default=ROOT / "docs/commercial/data-rights-2026-09-07.json")
    parser.add_argument("--purpose", choices=sorted(PURPOSES), required=True)
    args = parser.parse_args()
    errors = check_data_rights(args.data_dir, args.manifest, args.purpose)
    print(json.dumps({"purpose": args.purpose, "ready": not errors, "blocking_reasons": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
