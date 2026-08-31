import math
from datetime import UTC, datetime

from backend.core.price_fetcher import (
    _extract_yahoo_history,
    _extract_yahoo_quote,
    _parse_johnson_matthey_current_prices,
    _parse_johnson_matthey_history,
    _parse_markets_insider_quote,
    _parse_westmetall_table,
    get_reference_prices,
)


def _assert_utc_timestamp(value: str) -> None:
    parsed = datetime.fromisoformat(value)
    assert parsed.tzinfo is not None
    assert parsed.astimezone(UTC).utcoffset() == UTC.utcoffset(parsed)


def test_extract_yahoo_quote_uses_market_price_and_factor():
    payload = {
        "chart": {
            "result": [{
                "meta": {
                    "regularMarketPrice": 3148.5,
                    "regularMarketTime": 1710000000,
                },
                "indicators": {
                    "quote": [{
                        "close": [3100.0, 3148.5],
                    }],
                },
            }],
        },
    }

    price, fetched_at = _extract_yahoo_quote(payload, 1 / 2204.62)

    assert math.isclose(price or 0, 1.4282, rel_tol=1e-4)
    assert fetched_at.startswith("2024-03-09T")
    _assert_utc_timestamp(fetched_at)


def test_extract_yahoo_history_scales_ohlc_rows():
    payload = {
        "chart": {
            "result": [{
                "timestamp": [1710000000, 1710086400],
                "indicators": {
                    "quote": [{
                        "open": [3000.0, 3100.0],
                        "high": [3050.0, 3150.0],
                        "low": [2950.0, 3090.0],
                        "close": [3020.0, 3148.5],
                    }],
                },
            }],
        },
    }

    history = _extract_yahoo_history(payload, 1 / 2204.62)

    assert len(history) == 2
    assert history[0]["date"] == "2024-03-09"
    assert math.isclose(history[1]["price"], 1.4282, rel_tol=1e-4)
    assert math.isclose(history[1]["high"], 1.4289, rel_tol=1e-4)


def test_parse_johnson_matthey_current_prices_reads_hidden_input():
    html = """
    <input id="currentMetalPrices" type="hidden" value="{&quot;currentMetalList&quot;:[
      {&quot;metalCode&quot;:&quot;Ir&quot;,&quot;metalValueDate&quot;:&quot;25/03/2026&quot;,&quot;price&quot;:&quot;8000&quot;,&quot;metalName&quot;:&quot;Iridium&quot;},
      {&quot;metalCode&quot;:&quot;Ru&quot;,&quot;metalValueDate&quot;:&quot;25/03/2026&quot;,&quot;price&quot;:&quot;1750&quot;,&quot;metalName&quot;:&quot;Ruthenium&quot;}
    ]}" />
    """

    results = _parse_johnson_matthey_current_prices(html)

    assert results["Ir"]["price"] == 8000.0
    assert results["Ir"]["source"] == "Johnson Matthey (live)"
    assert results["Ru"]["price"] == 1750.0
    assert results["Ru"]["fetched_at"].startswith("2026-03-25T")
    _assert_utc_timestamp(results["Ru"]["fetched_at"])


def test_parse_markets_insider_quote_converts_metric_ton_to_lb():
    html = """
    <div class="price-section__current-value">16816</div>
    <div class="price-section__additionals">
      <span></span>
      <span>07:39:21 AM</span>
      <span>MI Indication</span>
    </div>
    """

    quote = _parse_markets_insider_quote(
        html,
        symbol="Ni",
        name="Nickel",
        unit="$/lb",
        factor=1 / 2204.62,
    )

    assert quote is not None
    assert quote["symbol"] == "Ni"
    assert quote["source"] == "Markets Insider (live)"
    assert math.isclose(quote["price"], 7.6276, rel_tol=1e-4)
    _assert_utc_timestamp(quote["fetched_at"])


def test_parse_johnson_matthey_history_groups_and_sorts_by_symbol():
    rows = [
        {"metalCode": "Rh", "metalValueDate": "31/08/2026", "price": "9050", "metalName": "Rhodium"},
        {"metalCode": "Rh", "metalValueDate": "02/03/2026", "price": "12050", "metalName": "Rhodium"},
        {"metalCode": "Ir", "metalValueDate": "02/03/2026", "price": "6700", "metalName": "Iridium"},
        {"metalCode": "Ir", "metalValueDate": "bad-date", "price": "1", "metalName": "Iridium"},
    ]

    series = _parse_johnson_matthey_history(rows)

    assert [point["date"] for point in series["Rh"]] == ["2026-03-02", "2026-08-31"]
    assert series["Rh"][-1]["price"] == 9050.0
    assert len(series["Ir"]) == 1


def test_parse_westmetall_table_converts_metric_ton_to_lb():
    page = """
    <table>
      <tr><th>date</th><th>settlement</th></tr>
      <tr><td>28. August 2026</td><td>16,850.00</td><td>17,000.00</td><td>268,362</td></tr>
      <tr><td>27. August 2026</td><td>16,660.00</td><td>16,840.00</td><td>268,314</td></tr>
    </table>
    """

    points = _parse_westmetall_table(page)

    assert [point["date"] for point in points] == ["2026-08-27", "2026-08-28"]
    assert math.isclose(points[-1]["price"], 16850.0 / 2204.62, rel_tol=1e-4)


def test_reference_prices_use_usgs_anchors_for_co_mo_w():
    ref = get_reference_prices()

    for sym, anchor in (("Co", 21.0), ("Mo", 34.71), ("W", 21.74)):
        assert ref[sym]["price"] == anchor
        assert ref[sym]["source"] == "USGS MCS 2026 (2025 avg)"
    assert ref["Fe"]["source"] == "CatCost 2018 + ChemPPI escalation"
