"""Guard the provenance contract on the preparation-cost libraries.

Every step rate and process template must say where it came from, and a claim
stronger than "we inherited this" must carry a URL that can be checked. The
point is that a re-sourced entry cannot be promoted by editing one field: the
evidence has to arrive with it.
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STEP_LIBRARY = ROOT / "backend" / "data" / "step_library.json"
TEMPLATE_DIR = ROOT / "backend" / "data" / "process_templates"

# toller_survey: an all-in rate inherited from the CatCost workbook, which
# derives it from toll-manufacturer quotations rather than a public correlation.
# proxy: a stand-in borrowed from a different process family, currently the
# thermocatalyst steps used to approximate MEA manufacture.
CONFIDENCE_LEVELS = {"vendor_quote", "literature", "derived", "toller_survey", "proxy", "unsourced"}

# Levels that assert a publicly checkable origin, so they owe a link.
CITED_LEVELS = {"vendor_quote", "literature", "derived"}


def load_steps():
    return json.loads(STEP_LIBRARY.read_text(encoding="utf-8"))["steps"]


def load_templates():
    return [(p.name, json.loads(p.read_text(encoding="utf-8"))) for p in sorted(TEMPLATE_DIR.glob("*.json"))]


@pytest.mark.parametrize("step", load_steps(), ids=lambda s: s["key"])
def test_step_declares_confidence(step):
    assert step.get("confidence") in CONFIDENCE_LEVELS, (
        f"{step['key']}: confidence is {step.get('confidence')!r}, expected one of {sorted(CONFIDENCE_LEVELS)}"
    )


@pytest.mark.parametrize("step", load_steps(), ids=lambda s: s["key"])
def test_cited_step_carries_a_reference(step):
    if step["confidence"] not in CITED_LEVELS:
        return
    url = step.get("reference_url")
    assert url and url.startswith("http"), (
        f"{step['key']}: confidence {step['confidence']!r} claims a public origin "
        f"but reference_url is {url!r}. Re-anchor it or drop it back to toller_survey."
    )
    assert step.get("quote_year"), f"{step['key']}: a cited rate must record the vintage of its source"


@pytest.mark.parametrize("step", load_steps(), ids=lambda s: s["key"])
def test_step_source_matches_its_confidence(step):
    if step["confidence"] == "unsourced":
        assert not step.get("source"), f"{step['key']}: marked unsourced but carries a source"
    else:
        assert step.get("source"), f"{step['key']}: confidence {step['confidence']!r} requires a source"


@pytest.mark.parametrize("name,template", load_templates(), ids=lambda v: v if isinstance(v, str) else "")
def test_template_declares_confidence(name, template):
    assert template.get("confidence") in CONFIDENCE_LEVELS, (
        f"{name}: confidence is {template.get('confidence')!r}"
    )


@pytest.mark.parametrize("name,template", load_templates(), ids=lambda v: v if isinstance(v, str) else "")
def test_cited_template_carries_a_reference(name, template):
    if template["confidence"] not in CITED_LEVELS:
        return
    urls = template.get("reference_urls") or []
    assert urls and all(u.startswith("http") for u in urls), (
        f"{name}: confidence {template['confidence']!r} requires resolvable reference_urls, got {urls!r}"
    )


def test_proxy_steps_are_the_known_set():
    """Proxies are a debt, not a category to grow.

    These nine approximate membrane-electrode-assembly manufacture with
    thermocatalyst equipment. Removing one is progress and should update this
    list; adding one silently is what this guards against.
    """
    expected = {
        "ccm_coating_pass",
        "electrochemical_break_in",
        "electrode_drying_low_temp",
        "hot_press_lamination",
        "ion_exchange_conversion",
        "ionomer_ink_homogenization",
        "membrane_pretreatment",
        "substrate_pretreatment",
        "ultrasonic_dispersion",
    }
    actual = {s["key"] for s in load_steps() if s["confidence"] == "proxy"}
    assert actual == expected, (
        f"proxy set changed: added {sorted(actual - expected)}, removed {sorted(expected - actual)}"
    )


def test_unsourced_templates_are_the_known_set():
    """Templates with no provenance at all, tracked so they cannot grow.

    Was three, then one, now empty: the impregnation routes cite the ACS
    impregnation review and zeolite_fcc cites the standard FCC review for its
    route structure. Any name appearing here again is a regression.
    """
    expected: set[str] = set()
    actual = {name for name, t in load_templates() if t["confidence"] == "unsourced"}
    assert actual == expected, (
        f"unsourced set changed: added {sorted(actual - expected)}, removed {sorted(expected - actual)}"
    )


def test_every_referenced_step_exists():
    keys = {s["key"] for s in load_steps()}
    for name, template in load_templates():
        missing = [s for s in (template.get("steps") or []) if s not in keys]
        assert not missing, f"{name} references steps absent from the library: {missing}"
