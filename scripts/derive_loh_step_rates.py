"""Recompute the Loh 2002 bottom-up floor rates and compare them to the toller rates.

The stored `derived_floor_usd_per_hr` values in loh2002_step_anchors.json must
equal what this script derives from the same file's equipment points and
constants; run with --check to get a nonzero exit on any drift or on a floor
that exceeds its toller rate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANCHORS = ROOT / "backend" / "data" / "loh2002_step_anchors.json"
STEP_LIBRARY = ROOT / "backend" / "data" / "step_library.json"

TIER_TO_FIELD = {"small": "cost_small", "medium": "cost_medium", "large": "cost_large"}


def load_anchors() -> dict:
    return json.loads(ANCHORS.read_text(encoding="utf-8"))


def crf(interest: float, years: int) -> float:
    growth = (1 + interest) ** years
    return interest * growth / (growth - 1)


def floor_rate(installed_1998: float, constants: dict) -> float:
    escalation = constants["cepci_2017"] / constants["cepci_1998"]
    fixed_frac = (
        crf(constants["crf_interest"], constants["crf_years"])
        + constants["maintenance_frac"]
        + constants["taxes_frac"]
        + constants["insurance_frac"]
    )
    capital = installed_1998 * escalation * fixed_frac / constants["annual_hours"]
    labor = (
        constants["operators_per_step"]
        * constants["labor_rate_usd_per_hr"]
        * (1 + constants["plant_overhead_frac"])
    )
    return capital + labor


def recompute(anchors: dict) -> list[dict]:
    """Return one row per (step, tier) with recomputed and stored values."""
    constants = anchors["method"]["constants"]
    points = anchors["equipment_points"]
    steps = {s["key"]: s for s in json.loads(STEP_LIBRARY.read_text(encoding="utf-8"))["steps"]}

    rows = []
    for key, mapping in anchors["steps"].items():
        toller = steps.get(key)
        for tier, spec in mapping["tiers"].items():
            row = {"step": key, "tier": tier, "status": spec["status"]}
            row["toller_rate"] = toller[TIER_TO_FIELD[tier]] if toller else None
            if spec["status"] == "corroborated":
                installed = sum(points[eq]["installed_1998"] for eq in spec["equipment"])
                row["recomputed"] = round(floor_rate(installed, constants), 2)
                row["stored"] = spec["derived_floor_usd_per_hr"]
            rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 on drift or floor violations")
    args = parser.parse_args()

    anchors = load_anchors()
    rows = recompute(anchors)

    failures = []
    print(f"{'step':<24}{'tier':<8}{'floor':>8}{'stored':>8}{'toller':>8}  status")
    for row in rows:
        floor = row.get("recomputed")
        stored = row.get("stored")
        toller = row["toller_rate"]
        print(
            f"{row['step']:<24}{row['tier']:<8}"
            f"{floor if floor is not None else '-':>8}"
            f"{stored if stored is not None else '-':>8}"
            f"{toller if toller is not None else '-':>8}  {row['status']}"
        )
        if row["status"] != "corroborated":
            continue
        if floor != stored:
            failures.append(f"{row['step']}/{row['tier']}: stored {stored} != recomputed {floor}")
        if toller is None:
            failures.append(f"{row['step']}/{row['tier']}: corroborated but no toller rate at this tier")
        elif floor > toller:
            failures.append(f"{row['step']}/{row['tier']}: floor {floor} exceeds toller rate {toller}")

    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print(f"  {failure}")
        return 1 if args.check else 0
    print("\nAll stored floors match the recomputation and sit at or below their toller rates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
