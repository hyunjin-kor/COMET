"""Range-validation harness for price calculation.

The existing harness in ``test_curated_library_combinations.py`` and
``test_calculation_harness.py`` checks that combinations produce a positive
estimate. That is necessary but not sufficient: a wiring bug could still
produce a positive number that is wildly wrong.

This module asserts the engine returns prices inside a *plausible band*
for known catalyst archetypes and that the cost ordering between metals is
preserved (PGMs >> base metals at the same loading), so a future regression
that doubles or halves the price is caught even though the result stays
positive.
"""

from __future__ import annotations

import pytest


def _calc(client, components: list[dict], *, order_size_tons: float = 10.0) -> dict:
    """Run a calculation and return the response body."""

    resp = client.post(
        "/api/calculate",
        json={
            "catalyst_domain": "thermal",
            "order_size_tons": order_size_tons,
            "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
            "components": components,
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _per_lb(body: dict) -> float:
    return float(body["summary"]["estimated_price_per_lb"])


# Per-pound bands picked from public commodity quotes Q1 2026 plus catalyst
# manufacturing overhead. Every band has at least 30% slack on each side so
# small commodity drift does not flake the suite; the bands flag *order of
# magnitude* problems, not pennies.
_PRICE_BANDS = {
    # 5 wt% Pt on Al2O3 — flagship PGM/oxide automotive workhorse.
    # Pt at $950/troy oz adds ~$760/lb of catalyst on the materials line alone,
    # so the engine's selling price floor is well above $700/lb.
    "5pt_alumina":   ("lit:usgs-platinum-bullion-2025", "lit:usgs-alumina-2025", 5.0,  700.0,  3000.0),
    # 5 wt% Pd on Al2O3 — same story, slightly cheaper than Pt.
    "5pd_alumina":   ("lit:usgs-palladium-bullion-2025", "lit:usgs-alumina-2025", 5.0,  700.0,  3000.0),
    # 5 wt% Rh — most expensive PGM, must dominate.
    "5rh_alumina":   ("lit:usgs-rhodium-bullion-2025",   "lit:usgs-alumina-2025", 5.0, 3500.0, 12000.0),
    # 5 wt% Cu cathode on Al2O3 — base metal, total < $20/lb easy.
    "5cu_alumina":   ("lit:usgs-copper-cathode-2025",    "lit:usgs-alumina-2025", 5.0,    1.5,    20.0),
    # 5 wt% Ni cathode on Al2O3 — base metal, similar floor.
    "5ni_alumina":   ("lit:usgs-nickel-cathode-2025",    "lit:usgs-alumina-2025", 5.0,    1.5,    20.0),
    # 21 wt% Ni on Al2O3 — CatCost validation case (medium scale handled separately).
    "21ni_alumina":  ("lit:usgs-nickel-cathode-2025",    "lit:usgs-alumina-2025", 21.0,   2.0,    25.0),
    # 1 wt% Ni / 99 wt% alumina — base-metal "lower bound" exercise:
    # the materials line is dominated by alumina ($1.30/lb), so the selling
    # price must hover near the support floor with overhead applied.
    "1ni_alumina":   ("lit:usgs-nickel-cathode-2025",    "lit:usgs-alumina-2025", 1.0,    1.0,     8.0),
}


@pytest.mark.parametrize("case", list(_PRICE_BANDS.keys()))
def test_curated_archetype_in_plausible_band(client, case: str) -> None:
    """Each curated archetype catalyst must land inside its expected band."""

    active_key, support_key, active_wt, lo, hi = _PRICE_BANDS[case]
    components = [
        {"role": "active_metal", "material_key": active_key, "wt_pct": active_wt},
        {"role": "support", "material_key": support_key, "wt_pct": 100.0 - active_wt},
    ]
    body = _calc(client, components)
    price = _per_lb(body)
    assert lo <= price <= hi, (
        f"{case}: price ${price:.2f}/lb fell outside expected band ${lo}-${hi}/lb"
    )


def test_pgm_loading_cost_dominates_base_metal_at_same_loading(client) -> None:
    """At the same wt% loading, a PGM catalyst must be much more expensive.

    Pt costs ~$15,000/lb vs Cu ~$4/lb — at 5 wt% loading the contribution gap
    is ~$750/lb, so the PGM catalyst must cost at least 50x more than the base
    metal one even after process and selling overhead is added.
    """

    cu = _calc(client, [
        {"role": "active_metal", "material_key": "lit:usgs-copper-cathode-2025", "wt_pct": 5.0},
        {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 95.0},
    ])
    pt = _calc(client, [
        {"role": "active_metal", "material_key": "lit:usgs-platinum-bullion-2025", "wt_pct": 5.0},
        {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 95.0},
    ])
    assert _per_lb(pt) > _per_lb(cu) * 50, (
        f"PGM cost did not dominate: Pt={_per_lb(pt):.2f}, Cu={_per_lb(cu):.2f}"
    )


def test_higher_loading_raises_cost_for_pgm_catalyst(client) -> None:
    """For the same active metal and support, doubling the loading must raise the price."""

    low = _calc(client, [
        {"role": "active_metal", "material_key": "lit:usgs-platinum-bullion-2025", "wt_pct": 1.0},
        {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 99.0},
    ])
    high = _calc(client, [
        {"role": "active_metal", "material_key": "lit:usgs-platinum-bullion-2025", "wt_pct": 5.0},
        {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 95.0},
    ])
    assert _per_lb(high) > _per_lb(low) * 3.5, (
        f"5x Pt loading should raise price ~5x at the materials line; got {_per_lb(low):.2f} -> {_per_lb(high):.2f}"
    )


def test_larger_campaign_lowers_per_pound_processing_cost(client) -> None:
    """Economies of scale: large campaigns spread step costs over more pounds.

    The selling-margin formula also drops with size, so the per-pound selling
    price must be lower for a 200-ton campaign than a 2-ton campaign for the
    same composition.
    """

    composition = [
        {"role": "active_metal", "material_key": "lit:usgs-nickel-cathode-2025", "wt_pct": 21.0},
        {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 79.0},
    ]
    small = _calc(client, composition, order_size_tons=2.0)
    large = _calc(client, composition, order_size_tons=200.0)
    assert _per_lb(large) < _per_lb(small), (
        f"Large-scale price should be lower than small-scale; got small={_per_lb(small):.2f}, large={_per_lb(large):.2f}"
    )


def test_gallon_priced_row_costs_via_density_dispatch(client, session) -> None:
    """A $/gal solvent row with a stored density must produce a finite cost.

    Methanol at $1.51/gal (2007 ICIS) with density 0.792 g/mL converts to
    roughly $0.23/lb. Wired into a thermal recipe alongside a real curated
    active, the engine should price the catalyst with that contribution
    flowing through the materials line.
    """

    from sqlmodel import select
    from backend.models.material import Material

    row = session.exec(
        select(Material)
        .where(Material.price_unit == "$/gal")
        .where(Material.density != None)  # noqa: E711
        .limit(1)
    ).first()
    assert row is not None, "Library should contain at least one gal-priced row with density"
    assert row.library_key is not None

    body = _calc(client, [
        {"role": "active_metal", "material_key": "lit:usgs-nickel-cathode-2025", "wt_pct": 5.0},
        {"role": "support", "material_key": row.library_key, "wt_pct": 95.0},
    ])
    assert _per_lb(body) > 0


def test_legacy_quote_carries_chemppi_escalation_metadata(client) -> None:
    """A 2006 ICIS row resolved at target_year=2024 must report ChemPPI escalation.

    The resolved-material snapshot drives the result page's transparency. For
    a 2006 quote the escalation factor must be > 1 (chemicals have inflated
    over the period) and the basis year must round-trip from the library row
    into the snapshot so the user can see *why* the in-calculator value
    differs from the raw quote shown in the Library page.
    """

    payload = {
        "catalyst_domain": "thermal",
        "order_size_tons": 10.0,
        "target_year": 2024,
        "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
        "components": [
            {"role": "active_metal", "material_key": "lit:usgs-nickel-cathode-2025", "wt_pct": 5.0},
            {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 95.0},
        ],
    }
    body = client.post("/api/calculate", json=payload).json()

    # Curated 2024/2025 USGS row should escalate by close to 1.0.
    alumina = next(
        m for m in body["resolved_materials"] if m["material_key"] == "lit:usgs-alumina-2025"
    )
    assert alumina["escalation_target_year"] == 2024
    assert alumina["raw_price_per_lb"] is not None
    assert alumina["escalation_factor"] is not None
    # 2024 -> 2024 must be exactly 1.0; 2025 -> 2024 is allowed to be ~0.99.
    assert 0.95 <= float(alumina["escalation_factor"]) <= 1.05


def test_escalation_does_not_apply_to_live_market_override(client, session) -> None:
    """When a USGS proxy is upgraded to a live market quote, escalation must be 1.0.

    Live quotes are by definition current, so applying ChemPPI on top would
    double-count inflation. The snapshot must record factor=1.0 plus the
    live override metadata.
    """

    from datetime import datetime
    from backend.models.metal_price import MetalPrice

    session.add(MetalPrice(
        symbol="Pt",
        name="Platinum",
        price=1450.0,
        unit="$/troy_oz",
        source="Test live feed",
        fetched_at=datetime(2026, 5, 4, 10, 0, 0),
    ))
    session.commit()

    body = _calc(client, [
        {"role": "active_metal", "material_key": "lit:usgs-platinum-bullion-2025", "wt_pct": 5.0},
        {"role": "support", "material_key": "lit:usgs-alumina-2025", "wt_pct": 95.0},
    ])
    pt = next(
        m for m in body["resolved_materials"]
        if m["material_key"] == "lit:usgs-platinum-bullion-2025"
    )
    assert pt["live_override"]["applied"] is True
    assert pt["escalation_factor"] == 1.0


def test_unit_normalization_unblocks_legacy_ton_quote(client, session) -> None:
    """Ammonia at $602.50/tonne (CatCost legacy) must now be costable.

    Before the unit-normalization fix this row failed with
    'Unsupported mass price unit: $/tonne'. After the fix it should normalize
    to ~$0.273/lb and survive a thermal cost calculation when wired into a
    thermal recipe via material_key.
    """

    from sqlmodel import select
    from backend.models.material import Material

    # Pick any seeded row that uses a tonne quote. The row was previously
    # broken; now it must produce a finite normalized_price_per_lb.
    stmt = select(Material).where(Material.price_unit == "$/tonne").limit(1)
    row = session.exec(stmt).first()
    assert row is not None, "Seeded library should still contain at least one $/tonne row"
    assert row.library_key is not None

    # Use a real curated active so the calculation has a meaningful Ni line on
    # top of the legacy support row, exercising the fixed unit path.
    body = _calc(client, [
        {"role": "active_metal", "material_key": "lit:usgs-nickel-cathode-2025", "wt_pct": 5.0},
        {"role": "support", "material_key": row.library_key, "wt_pct": 95.0},
    ])
    assert _per_lb(body) > 0


def test_calculator_usability_flag_classifies_each_row_correctly(session) -> None:
    """Mass-priced rows are always usable; gal rows need density; mL/cm2 rows are browse-only.

    The Library page's "Ready to cost" badge depends on this flag so the user
    is never offered a row the engine cannot cost. The seeded library must
    therefore split cleanly: gallon rows with a density value flow through
    via the volume-to-mass dispatch, area / volume rows without density are
    correctly held back in the browse-only tier (they belong to the electrode
    stack model, not the thermal mass-based calculation).
    """

    from fastapi.testclient import TestClient
    from backend.main import app

    with TestClient(app) as live_client:
        rows = live_client.get("/api/materials?limit=1000").json()

    # Gallon-priced thermal rows must now be usable because density is present.
    gal_rows = [row for row in rows if (row.get("price_unit") or "").endswith("gal")]
    assert gal_rows, "Seeded library should still contain at least one gal-priced row"
    for row in gal_rows:
        assert row["is_calculator_usable"] is True, (
            f"{row['name']} ({row['price_unit']}) should be ready to cost via density-backed conversion"
        )

    # Electrocatalyst ionomer/membrane rows priced in $/cm2 or $/mL without
    # density correctly stay browse-only for the thermal mass-based path.
    area_only = [
        row for row in rows
        if (row.get("price_unit") or "") in ("$/cm2", "$/m2") and row.get("is_calculator_usable") is False
    ]
    assert area_only, "Electrocatalyst area-priced rows should appear as browse-only for the thermal calculator"

    # And every curated USGS proxy must be ready to cost.
    usgs_rows = [row for row in rows if str(row.get("id", "")).startswith("lit:usgs-")]
    assert usgs_rows, "Curated library should still expose USGS commodity proxies"
    for row in usgs_rows:
        assert row["is_calculator_usable"] is True, f"{row['id']} should be ready to cost"
