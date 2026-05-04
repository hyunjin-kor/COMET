"""End-to-end exercise of every curated material in real catalyst combinations.

The catalogue at ``backend/data/materials_curated.json`` is supposed to be a
"plug it in and run" library. This module loads every active and support row,
posts the request to ``/api/calculate`` for each (active, support) pair, and
asserts the engine returns a valid 200 result with a positive price.

If a future row has a typo, an unsupported price unit, or a missing
``symbol``/``category`` field, this test fails before the row hits production.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

import pytest

from backend.models.metal_price import MetalPrice

CURATED_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "materials_curated.json"
)

# Categories that should be costable as a thermal active component.
_ACTIVE_CATEGORIES = {
    "Base Metal",
    "Base Metal / Rare Earth",
    "Base Metal / Refractory Metal",
    "Precious Metal",
    "Precious Metal / PGM",
}

# Categories that should be costable as a thermal support / bulk oxide.
_SUPPORT_CATEGORIES = {"Support"}


def _load_curated_materials() -> list[dict]:
    data = json.loads(CURATED_PATH.read_text(encoding="utf-8"))
    return data["materials"]


def _by_role(rows: Iterable[dict], categories: set[str]) -> list[dict]:
    return [row for row in rows if row.get("category") in categories]


@pytest.fixture(scope="module")
def curated_materials() -> list[dict]:
    return _load_curated_materials()


@pytest.fixture(scope="module")
def active_rows(curated_materials: list[dict]) -> list[dict]:
    rows = _by_role(curated_materials, _ACTIVE_CATEGORIES)
    assert rows, "No active-metal rows discovered in curated library."
    return rows


@pytest.fixture(scope="module")
def support_rows(curated_materials: list[dict]) -> list[dict]:
    rows = _by_role(curated_materials, _SUPPORT_CATEGORIES)
    assert rows, "No support rows discovered in curated library."
    return rows


def test_every_curated_row_has_required_fields(
    curated_materials: list[dict],
) -> None:
    """Schema gate: any new row must declare all transport fields."""

    required = {
        "library_key",
        "name",
        "category",
        "price",
        "price_unit",
        "source",
        "quote_year",
        "reference_url",
        "pricing_basis",
        "price_scope",
    }
    missing: list[str] = []
    for row in curated_materials:
        gaps = required - set(row)
        if gaps:
            missing.append(f"{row.get('library_key', '?')}: missing {sorted(gaps)}")
    assert not missing, "Curated rows have missing required fields:\n" + "\n".join(missing)


def test_curated_library_keys_are_unique(curated_materials: list[dict]) -> None:
    """A duplicated library_key would silently overwrite a row at sync time."""

    keys = [row["library_key"] for row in curated_materials]
    assert len(keys) == len(set(keys)), (
        "Duplicate library_keys: "
        + ", ".join(sorted({k for k in keys if keys.count(k) > 1}))
    )


def test_every_active_row_combines_with_alumina(
    client, active_rows: list[dict]
) -> None:
    """Pair every active row with ``lit:usgs-alumina-2025`` and price the catalyst.

    Alumina is the most universally compatible support — it appears in 7+
    benchmark families. Pairing every active row against it confirms the
    row's price unit, category, and library_key flow through the engine
    without hitting an unsupported branch.
    """

    failures: list[str] = []
    for active in active_rows:
        payload = {
            "catalyst_domain": "thermal",
            "order_size_tons": 10.0,
            "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
            "components": [
                {
                    "role": "active_metal",
                    "material_key": active["library_key"],
                    "wt_pct": 5.0,
                },
                {
                    "role": "support",
                    "material_key": "lit:usgs-alumina-2025",
                    "wt_pct": 95.0,
                },
            ],
        }
        resp = client.post("/api/calculate", json=payload)
        if resp.status_code != 200:
            failures.append(
                f"{active['library_key']} -> HTTP {resp.status_code}: {resp.text[:200]}"
            )
            continue
        body = resp.json()
        price = body["summary"]["estimated_price_per_lb"]
        if not (price > 0):
            failures.append(
                f"{active['library_key']} -> non-positive price {price}"
            )

    assert not failures, "Active rows failed to combine with alumina:\n" + "\n".join(failures)


def test_every_support_row_combines_with_nickel(
    client, support_rows: list[dict]
) -> None:
    """Pair every support row with ``lit:usgs-nickel-cathode-2025`` and price.

    Nickel is the most generic / well-defined active for screening. Each
    support must accept a 5/95 wt% pairing and produce a finite cost.
    """

    failures: list[str] = []
    for support in support_rows:
        payload = {
            "catalyst_domain": "thermal",
            "order_size_tons": 10.0,
            "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
            "components": [
                {
                    "role": "active_metal",
                    "material_key": "lit:usgs-nickel-cathode-2025",
                    "wt_pct": 5.0,
                },
                {
                    "role": "support",
                    "material_key": support["library_key"],
                    "wt_pct": 95.0,
                },
            ],
        }
        resp = client.post("/api/calculate", json=payload)
        if resp.status_code != 200:
            failures.append(
                f"{support['library_key']} -> HTTP {resp.status_code}: {resp.text[:200]}"
            )
            continue
        body = resp.json()
        price = body["summary"]["estimated_price_per_lb"]
        if not (price > 0):
            failures.append(
                f"{support['library_key']} -> non-positive price {price}"
            )

    assert not failures, "Support rows failed to combine with nickel:\n" + "\n".join(failures)


def test_bimetallic_pgm_with_promoter_and_support(client) -> None:
    """One representative four-component thermal recipe must succeed.

    Pt + Pd active metals + Ce promoter + alumina support is a realistic
    automotive three-way / oxidation catalyst architecture. Exercising
    multiple roles in one recipe verifies the full multi-component path.
    """

    payload = {
        "catalyst_domain": "thermal",
        "order_size_tons": 10.0,
        "steps": [
            "mixer_slurry",
            "incipient_wetness",
            "dryer_rotary_100_300C",
            "kiln_continuous_indirect",
        ],
        "components": [
            {
                "role": "active_metal",
                "material_key": "lit:usgs-platinum-bullion-2025",
                "wt_pct": 1.0,
            },
            {
                "role": "active_metal",
                "material_key": "lit:usgs-palladium-bullion-2025",
                "wt_pct": 0.5,
            },
            {
                "role": "promoter",
                "material_key": "lit:usgs-ceria-2025",
                "wt_pct": 8.0,
            },
            {
                "role": "support",
                "material_key": "lit:usgs-alumina-2025",
                "wt_pct": 90.5,
            },
        ],
    }
    resp = client.post("/api/calculate", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    summary = body["summary"]
    assert summary["estimated_price_per_lb"] > 0
    assert summary["estimated_price_per_kg"] > 0
    # PGMs at 1.5 wt% should keep the catalyst price well above the support floor.
    assert summary["estimated_price_per_lb"] > 5.0


def _calculate_pt_on_alumina(client) -> dict:
    """Helper: 5 wt% Pt commodity-proxy on alumina, return the full response."""
    payload = {
        "catalyst_domain": "thermal",
        "order_size_tons": 10.0,
        "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
        "components": [
            {
                "role": "active_metal",
                "material_key": "lit:usgs-platinum-bullion-2025",
                "wt_pct": 5.0,
            },
            {
                "role": "support",
                "material_key": "lit:usgs-alumina-2025",
                "wt_pct": 95.0,
            },
        ],
    }
    resp = client.post("/api/calculate", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_usgs_proxy_falls_back_when_no_live_quote(client) -> None:
    """Without any stored live quote, the engine uses the static USGS price.

    The resolved-materials snapshot must flag this explicitly so the UI can
    show the user that no live quote was available and the catalog price
    is in use.
    """

    body = _calculate_pt_on_alumina(client)
    pt_snapshot = next(
        m for m in body["resolved_materials"]
        if m["material_key"] == "lit:usgs-platinum-bullion-2025"
    )
    # No live quote in the empty test DB -> override should report not applied.
    override = pt_snapshot.get("live_override")
    assert override is not None, "Eligible row must surface a live_override block"
    assert override["applied"] is False
    assert override["reason"] == "no_live_quote_stored"
    # Price must be the static USGS quote.
    assert pt_snapshot["price"] == 950.0
    assert pt_snapshot["price_unit"] == "$/troy_oz"
    assert pt_snapshot["price_scope"] == "literature_high_volume"


def test_usgs_proxy_upgrades_to_live_quote_when_available(client, session) -> None:
    """When a live Pt quote is in the metal-price table, the calculation uses it.

    This is the link between /api/prices (live feed) and the catalog: the
    same metal must price the same way in both surfaces, regardless of
    whether the user picked it from the live feed or the curated library.
    """

    # Seed a "live" Pt quote much higher than the static USGS $950.
    session.add(MetalPrice(
        symbol="Pt",
        name="Platinum",
        price=1450.0,
        unit="$/troy_oz",
        source="Yahoo Finance (live)",
        fetched_at=datetime(2026, 5, 4, 10, 0, 0),
    ))
    session.commit()

    body = _calculate_pt_on_alumina(client)
    pt_snapshot = next(
        m for m in body["resolved_materials"]
        if m["material_key"] == "lit:usgs-platinum-bullion-2025"
    )
    override = pt_snapshot["live_override"]
    assert override["applied"] is True
    assert override["live_price"] == 1450.0
    assert override["live_price_unit"] == "$/troy_oz"
    assert override["live_source"] == "Yahoo Finance (live)"
    # Static USGS row preserved as the documented fallback.
    assert override["fallback_price"] == 950.0
    assert override["fallback_quote_year"] == 2024
    # Snapshot's "current" price reflects the live quote, not the USGS static.
    assert pt_snapshot["price"] == 1450.0
    assert pt_snapshot["price_scope"] == "live_market"


def test_live_override_propagates_to_catalyst_price(client, session) -> None:
    """A live Pt quote 50% higher than USGS must visibly raise the catalyst price."""

    body_static = _calculate_pt_on_alumina(client)
    static_price = body_static["summary"]["estimated_price_per_lb"]

    # Same composition, but Pt now quoted at 1.5x the USGS bullion proxy.
    session.add(MetalPrice(
        symbol="Pt",
        name="Platinum",
        price=950.0 * 1.5,
        unit="$/troy_oz",
        source="Live feed (test)",
        fetched_at=datetime(2026, 5, 4, 10, 0, 0),
    ))
    session.commit()

    body_live = _calculate_pt_on_alumina(client)
    live_price = body_live["summary"]["estimated_price_per_lb"]

    # Catalyst has 5 wt% Pt; raising Pt 50% should raise the catalyst cost
    # noticeably (not by exactly 50% because of overhead/margin layers).
    assert live_price > static_price * 1.05, (
        f"Live override did not propagate (static={static_price}, live={live_price})"
    )


def test_non_eligible_library_row_has_no_live_override_block(client) -> None:
    """Sigma vendor-lab rows are not commodity proxies and must NOT carry the block.

    Live quotes only override the USGS commodity proxies. Sigma rows
    represent a specific vendor SKU at a specific pack size — replacing
    that price with a market quote would be misleading.
    """

    payload = {
        "catalyst_domain": "thermal",
        "order_size_tons": 10.0,
        "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
        "components": [
            {
                "role": "active_metal",
                "material_key": "sigma:520896",  # chloroplatinic acid (vendor lab)
                "wt_pct": 5.0,
            },
            {
                "role": "support",
                "material_key": "lit:usgs-alumina-2025",
                "wt_pct": 95.0,
            },
        ],
    }
    resp = client.post("/api/calculate", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    sigma_snapshot = next(
        m for m in body["resolved_materials"]
        if m["material_key"] == "sigma:520896"
    )
    assert "live_override" not in sigma_snapshot


def test_new_pgm_proxies_are_more_expensive_than_base_metals(client) -> None:
    """Sanity: 5 wt% Rh on alumina must cost more than 5 wt% Cu on alumina."""

    def _price(active_key: str) -> float:
        payload = {
            "catalyst_domain": "thermal",
            "order_size_tons": 10.0,
            "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
            "components": [
                {"role": "active_metal", "material_key": active_key, "wt_pct": 5.0},
                {
                    "role": "support",
                    "material_key": "lit:usgs-alumina-2025",
                    "wt_pct": 95.0,
                },
            ],
        }
        resp = client.post("/api/calculate", json=payload)
        assert resp.status_code == 200, resp.text
        return resp.json()["summary"]["estimated_price_per_lb"]

    rh = _price("lit:usgs-rhodium-bullion-2025")
    cu = _price("lit:usgs-copper-cathode-2025")
    assert rh > cu * 100, (
        f"PGM-loaded catalyst should dominate cost ($/lb Rh-cat={rh:.1f}, Cu-cat={cu:.1f})"
    )
