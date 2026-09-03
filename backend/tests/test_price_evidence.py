"""Unit tests for price-source evidence tagging.

The evidence block ships with every price the desktop app surfaces, so the
mapping table, freshness staging, manual override path, and fixed-evidence
helper need direct assertions independent of the live fetchers.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from backend.core.price_evidence import build_fixed_evidence, describe_price_evidence


def _hours_ago(hours: float) -> str:
    """Return an ISO timestamp ``hours`` in the past, in UTC."""

    return (datetime.now(UTC) - timedelta(hours=hours)).isoformat()


class TestSourceMatching:
    def test_yahoo_finance_maps_to_exchange_screen(self):
        ev = describe_price_evidence(source="Yahoo Finance (live)")
        assert ev["tier"] == "exchange_screen"
        assert ev["confidence_score"] == 86
        assert ev["acquisition_mode"] == "api"
        assert ev["freshness_target_hours"] == 24

    def test_metals_dev_and_metalprice_share_aggregated_tier_with_distinct_scores(self):
        metals_dev = describe_price_evidence(source="Metals.Dev")
        metalprice = describe_price_evidence(source="MetalpriceAPI")
        assert metals_dev["tier"] == "aggregated_market_api"
        assert metalprice["tier"] == "aggregated_market_api"
        # Metals.Dev is rated slightly higher than MetalpriceAPI in the rule table.
        assert metals_dev["confidence_score"] > metalprice["confidence_score"]

    def test_monthly_average_sources_share_the_reference_tier(self):
        imf = describe_price_evidence(source="IMF PCPS (monthly average)", fetched_at="2026-07-31")
        jm = describe_price_evidence(source="Johnson Matthey (monthly average)", fetched_at="2026-07-31")
        assert imf["tier"] == jm["tier"] == "indexed_reference"
        assert imf["confidence_score"] == jm["confidence_score"] == 88
        assert imf["freshness_status"] == "reference"
        # The daily Johnson Matthey board keeps its own rule.
        assert describe_price_evidence(source="Johnson Matthey (live)")["tier"] == "supplier_board"

    def test_johnson_matthey_is_supplier_board_with_long_freshness_window(self):
        ev = describe_price_evidence(source="Johnson Matthey (live)")
        assert ev["tier"] == "supplier_board"
        assert ev["confidence_score"] == 90  # highest in the rule table
        assert ev["freshness_target_hours"] == 48

    def test_kitco_and_markets_insider_use_screen_scrape_tier(self):
        kitco = describe_price_evidence(source="Kitco (live)")
        mi = describe_price_evidence(source="Markets Insider (live)")
        assert kitco["tier"] == "screen_scrape"
        assert mi["tier"] == "screen_scrape"
        assert kitco["acquisition_mode"] == "scrape"
        assert mi["acquisition_mode"] == "scrape"

    def test_indexed_reference_carries_no_freshness_target(self):
        ev = describe_price_evidence(source="CatCost 2018 + ChemPPI escalation")
        assert ev["tier"] == "indexed_reference"
        assert ev["freshness_target_hours"] is None
        assert ev["freshness_status"] == "reference"
        assert ev["age_hours"] is None

    def test_unknown_source_returns_unclassified_block(self):
        ev = describe_price_evidence(source="Some Unrecognised Vendor")
        assert ev["tier"] == "unknown"
        assert ev["confidence_score"] == 50
        assert ev["label"] == "Unclassified source"

    def test_empty_or_none_source_also_returns_unclassified_block(self):
        for source in (None, "", "   "):
            ev = describe_price_evidence(source=source)
            assert ev["tier"] == "unknown"


class TestManualOverride:
    def test_manual_overrides_source_match(self):
        """Manual flag should win even when the source string matches a live rule."""
        ev = describe_price_evidence(source="Yahoo Finance (live)", manual=True)
        assert ev["tier"] == "manual_input"
        assert ev["acquisition_mode"] == "manual"
        assert ev["confidence_score"] == 35
        assert ev["label"] == "Manual input"

    def test_manual_with_no_source_returns_manual_evidence(self):
        ev = describe_price_evidence(source=None, manual=True)
        assert ev["tier"] == "manual_input"


class TestFreshnessStaging:
    def test_recent_quote_within_target_is_current(self):
        ev = describe_price_evidence(
            source="Yahoo Finance (live)",
            fetched_at=_hours_ago(1.0),
        )
        assert ev["freshness_status"] == "current"
        assert ev["age_hours"] is not None
        assert ev["age_hours"] < 24

    def test_quote_between_target_and_three_target_is_aging(self):
        # Yahoo target = 24h. 30h falls in the (24, 72] window.
        ev = describe_price_evidence(
            source="Yahoo Finance (live)",
            fetched_at=_hours_ago(30.0),
        )
        assert ev["freshness_status"] == "aging"

    def test_quote_past_three_target_is_stale(self):
        # Yahoo target = 24h. 100h is well past 3 * 24 = 72h.
        ev = describe_price_evidence(
            source="Yahoo Finance (live)",
            fetched_at=_hours_ago(100.0),
        )
        assert ev["freshness_status"] == "stale"

    def test_target_none_always_reports_reference_regardless_of_fetched_at(self):
        ev = describe_price_evidence(
            source="CatCost 2018 + ChemPPI escalation",
            fetched_at=_hours_ago(1.0),
        )
        assert ev["freshness_status"] == "reference"

    def test_missing_fetched_at_with_target_set_yields_unknown(self):
        ev = describe_price_evidence(
            source="Yahoo Finance (live)",
            fetched_at=None,
        )
        assert ev["freshness_status"] == "unknown"
        assert ev["age_hours"] is None


class TestDatetimeParsing:
    def test_z_suffix_is_treated_as_utc(self):
        # Z is a valid UTC marker; the helper should normalize it to +00:00.
        iso_with_z = (datetime.now(UTC) - timedelta(hours=2)).isoformat().replace("+00:00", "Z")
        ev = describe_price_evidence(
            source="Yahoo Finance (live)",
            fetched_at=iso_with_z,
        )
        assert ev["age_hours"] is not None
        assert ev["age_hours"] >= 1.9  # parsed correctly

    def test_naive_datetime_string_is_treated_as_utc(self):
        # No timezone suffix: helper assigns UTC rather than failing.
        naive = (datetime.now(UTC) - timedelta(hours=3)).replace(tzinfo=None).isoformat()
        ev = describe_price_evidence(
            source="Yahoo Finance (live)",
            fetched_at=naive,
        )
        assert ev["age_hours"] is not None
        assert ev["age_hours"] >= 2.9

    def test_unparseable_fetched_at_is_treated_as_unknown(self):
        ev = describe_price_evidence(
            source="Yahoo Finance (live)",
            fetched_at="not-a-real-date",
        )
        assert ev["freshness_status"] == "unknown"
        assert ev["age_hours"] is None


class TestFixedEvidenceHelper:
    def test_build_fixed_evidence_passes_through_input_and_pins_static_fields(self):
        ev = build_fixed_evidence(
            label="Vendor lab quote",
            note="Sigma-Aldrich 2024 catalogue price.",
            tier="vendor_lab",
            confidence_score=70,
            transparency="vendor_quote",
        )

        assert ev["label"] == "Vendor lab quote"
        assert ev["note"] == "Sigma-Aldrich 2024 catalogue price."
        assert ev["tier"] == "vendor_lab"
        assert ev["confidence_score"] == 70
        assert ev["transparency"] == "vendor_quote"

        # Fields that fixed evidence always pins, regardless of input.
        assert ev["acquisition_mode"] == "static"
        assert ev["freshness_target_hours"] is None
        assert ev["freshness_status"] == "reference"
        assert ev["age_hours"] is None
