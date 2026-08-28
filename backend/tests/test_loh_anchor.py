"""Guard the Loh 2002 cross-check chain on the toller step rates.

The anchors file stores derived floor rates next to the raw inputs they came
from; these tests recompute the chain so a stored number cannot be edited
without the evidence moving with it, and pin the corroboration bookkeeping so
steps cannot silently drop out of coverage.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from backend.core.constants import STEP_COSTS

ROOT = Path(__file__).resolve().parents[2]
ANCHORS_PATH = ROOT / "backend" / "data" / "loh2002_step_anchors.json"
STEP_LIBRARY_PATH = ROOT / "backend" / "data" / "step_library.json"

_spec = importlib.util.spec_from_file_location(
    "derive_loh_step_rates", ROOT / "scripts" / "derive_loh_step_rates.py"
)
derive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(derive)


def load_anchors() -> dict:
    return json.loads(ANCHORS_PATH.read_text(encoding="utf-8"))


def load_steps() -> dict[str, dict]:
    return {s["key"]: s for s in json.loads(STEP_LIBRARY_PATH.read_text(encoding="utf-8"))["steps"]}


def corroborated_rows():
    anchors = load_anchors()
    points = anchors["equipment_points"]
    constants = anchors["method"]["constants"]
    for key, mapping in anchors["steps"].items():
        for tier, spec in mapping["tiers"].items():
            yield key, tier, spec, points, constants


@pytest.mark.parametrize(
    "key,tier,spec,points,constants",
    list(corroborated_rows()),
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_stored_floor_matches_recomputation(key, tier, spec, points, constants):
    if spec["status"] != "corroborated":
        assert "derived_floor_usd_per_hr" not in spec, f"{key}/{tier}: out-of-range tier carries a floor"
        return
    installed = sum(points[eq]["installed_1998"] for eq in spec["equipment"])
    recomputed = round(derive.floor_rate(installed, constants), 2)
    assert spec["derived_floor_usd_per_hr"] == recomputed, (
        f"{key}/{tier}: stored floor {spec['derived_floor_usd_per_hr']} != recomputed {recomputed}"
    )


@pytest.mark.parametrize(
    "key,tier,spec,points,constants",
    list(corroborated_rows()),
    ids=lambda v: v if isinstance(v, str) else "",
)
def test_floor_sits_at_or_below_toller_rate(key, tier, spec, points, constants):
    if spec["status"] != "corroborated":
        return
    rate = STEP_COSTS[key][tier]
    assert rate is not None, f"{key}/{tier}: corroborated but the engine has no rate at this tier"
    assert spec["derived_floor_usd_per_hr"] <= rate, (
        f"{key}/{tier}: floor {spec['derived_floor_usd_per_hr']} exceeds toller rate {rate} - "
        "either the rate shrank or the floor's assumptions no longer hold"
    )


def test_step_library_crosscheck_blocks_mirror_the_anchors():
    anchors = load_anchors()
    steps = load_steps()
    for key, mapping in anchors["steps"].items():
        block = steps[key].get("loh_crosscheck")
        assert block, f"{key}: mapped in anchors but step_library has no loh_crosscheck block"
        for tier in ("small", "medium", "large"):
            spec = mapping["tiers"].get(tier)
            expected = (
                spec["derived_floor_usd_per_hr"]
                if spec and spec["status"] == "corroborated"
                else None
            )
            assert block[tier] == expected, (
                f"{key}/{tier}: step_library shows {block[tier]}, anchors derive {expected}"
            )
        assert block["reference_url"] == anchors["report"]["reference_url"]
    unmapped_with_block = [
        key for key, step in steps.items()
        if "loh_crosscheck" in step and key not in anchors["steps"]
    ]
    assert not unmapped_with_block, (
        f"steps carry a loh_crosscheck without an anchors mapping: {unmapped_with_block}"
    )


def test_every_toller_step_is_mapped_or_has_a_recorded_reason():
    """Coverage bookkeeping: a new toller step must be anchored or explain why not."""
    anchors = load_anchors()
    steps = load_steps()
    toller_keys = {k for k, s in steps.items() if s["confidence"] == "toller_survey"}
    mapped = set(anchors["steps"])
    unmapped = {k for k in anchors["unmapped_steps"] if not k.startswith("_")}
    assert mapped | unmapped == toller_keys, (
        f"coverage gap: unaccounted {sorted(toller_keys - mapped - unmapped)}, "
        f"stale {sorted((mapped | unmapped) - toller_keys)}"
    )
    assert not mapped & unmapped, f"steps listed on both sides: {sorted(mapped & unmapped)}"


def test_anchor_constants_match_their_in_repo_sources():
    constants = load_anchors()["method"]["constants"]
    cepci = json.loads((ROOT / "backend" / "data" / "cepci.json").read_text(encoding="utf-8"))
    assert constants["cepci_1998"] == cepci["annual"]["1998"]["CEPCI"]
    assert constants["cepci_2017"] == cepci["annual"]["2017"]["CEPCI"]
    opex = json.loads((ROOT / "backend" / "data" / "opex_factors.json").read_text(encoding="utf-8"))
    assert constants["labor_rate_usd_per_hr"] == opex["direct_labor"]["labor_rate"]["base"]
    assert constants["maintenance_frac"] == opex["direct_operating"]["maintenance_repair"]["base"] / 100
    assert constants["taxes_frac"] == opex["fixed_operating"]["local_taxes"]["base"] / 100
    assert constants["insurance_frac"] == opex["fixed_operating"]["insurance"]["base"] / 100
    assert constants["plant_overhead_frac"] == opex["fixed_operating"]["plant_overhead"]["base"] / 100


def test_tier_equipment_points_exist():
    anchors = load_anchors()
    for key, mapping in anchors["steps"].items():
        for tier, spec in mapping["tiers"].items():
            for eq in spec.get("equipment", []):
                assert eq in anchors["equipment_points"], f"{key}/{tier}: unknown equipment point {eq}"
