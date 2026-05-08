"""Integration tests for the POST /api/capex endpoint.

The math itself lives in ``test_capex_opex.py`` (factor-by-factor unit
checks). This module exercises the new HTTP wrapper introduced for the
desktop CapEx workspace: payload validation, both lump-sum and
equipment-list paths, optional OpEx layering, and the audit-trail summary
fields the UI reads to render the metric tiles.
"""

from __future__ import annotations

import pytest


def test_capex_lump_sum_path_returns_full_breakdown(client) -> None:
    """A purchased-equipment lump value flows through the factor pipeline.

    Peters & Timmerhaus default factors expand $1M of purchased equipment to
    a fixed-capital investment around $5M and a total capital investment
    around $5.9M. This is the reference behaviour the UI shows in the dark
    headline tile, so we assert both the absolute values and the FCI/PE and
    TCI/PE ratios that drive the chips below the headline.
    """

    resp = client.post("/api/capex", json={"purchased_equipment_cost_usd": 1_000_000})
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["purchased_equipment_cost_usd"] == 1_000_000
    assert body["equipment_resolution"] == []
    assert body["opex"] is None

    capex = body["capex"]
    assert capex["purchased_equipment"] == pytest.approx(1_000_000)
    assert capex["fixed_capital_investment"] > 4_000_000
    assert capex["fixed_capital_investment"] < 7_000_000
    assert capex["total_capital_investment"] > capex["fixed_capital_investment"]
    assert capex["working_capital"] > 0

    summary = body["summary"]
    assert summary["fci_to_purchased_equipment_ratio"] == pytest.approx(
        capex["fixed_capital_investment"] / 1_000_000, rel=0.001
    )
    assert summary["tci_to_purchased_equipment_ratio"] > summary["fci_to_purchased_equipment_ratio"]
    assert summary["annual_opex_usd"] is None


def test_capex_equipment_list_path_scales_six_tenths_rule(client) -> None:
    """Equipment items scale via Cost = base * (target/base)^exponent."""

    resp = client.post(
        "/api/capex",
        json={
            "equipment": [
                {
                    "name": "Reactor",
                    "base_cost_usd": 200_000,
                    "base_size": 10,
                    "target_size": 50,  # 5x larger
                    "exponent": 0.6,
                    "quantity": 1,
                },
                {
                    "name": "Dryer",
                    "base_cost_usd": 80_000,
                    "base_size": 5,
                    "target_size": 20,  # 4x larger
                    "exponent": 0.65,
                    "quantity": 2,
                },
            ]
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert len(body["equipment_resolution"]) == 2
    reactor, dryer = body["equipment_resolution"]

    # Reactor: 200000 * 5^0.6 = 200000 * 2.626 = 525,306
    assert reactor["scaled_unit_cost_usd"] == pytest.approx(525_306, abs=10)
    assert reactor["line_total_usd"] == pytest.approx(525_306, abs=10)
    # Dryer: 80000 * 4^0.65 = 80000 * 2.462 = 196,983; quantity 2 -> 393,966
    assert dryer["scaled_unit_cost_usd"] == pytest.approx(196_983, abs=10)
    assert dryer["line_total_usd"] == pytest.approx(393_966, abs=20)

    purchased = body["purchased_equipment_cost_usd"]
    assert purchased == pytest.approx(reactor["line_total_usd"] + dryer["line_total_usd"], abs=20)
    assert body["capex"]["fixed_capital_investment"] > purchased


def test_capex_with_opex_inputs_layers_annual_operating_costs(client) -> None:
    """OpEx is computed when any of direct labor / raw materials / utilities is positive."""

    resp = client.post(
        "/api/capex",
        json={
            "purchased_equipment_cost_usd": 1_000_000,
            "opex_inputs": {
                "direct_labor_cost_usd": 250_000,
                "raw_materials_cost_usd": 800_000,
                "utilities_cost_usd": 120_000,
            },
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()

    opex = body["opex"]
    assert opex is not None
    # Direct operating must equal at least the input numbers (engine adds derived items on top).
    assert opex["raw_materials"] == pytest.approx(800_000)
    assert opex["direct_labor"] == pytest.approx(250_000)
    assert opex["utilities"] == pytest.approx(120_000)
    assert opex["direct_operating_total"] > 800_000 + 250_000 + 120_000
    assert opex["total_annual_opex"] > opex["direct_operating_total"]
    assert body["summary"]["annual_opex_usd"] == pytest.approx(opex["total_annual_opex"])


def test_capex_rejects_payload_without_purchased_or_equipment(client) -> None:
    """Empty payload must fail Pydantic validation with a 422."""

    resp = client.post("/api/capex", json={})
    assert resp.status_code == 422

    resp = client.post("/api/capex", json={"opex_inputs": {"direct_labor_cost_usd": 1.0}})
    assert resp.status_code == 422


def test_capex_zero_opex_inputs_skip_opex_block(client) -> None:
    """If all three OpEx inputs are zero, the engine returns ``opex: null``."""

    resp = client.post(
        "/api/capex",
        json={
            "purchased_equipment_cost_usd": 500_000,
            "opex_inputs": {
                "direct_labor_cost_usd": 0,
                "raw_materials_cost_usd": 0,
                "utilities_cost_usd": 0,
            },
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["opex"] is None
    assert body["summary"]["annual_opex_usd"] is None
