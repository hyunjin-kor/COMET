import math

from backend.core.price_fetcher import (
    _extract_yahoo_history,
    _extract_yahoo_quote,
    _parse_johnson_matthey_current_prices,
    _parse_markets_insider_quote,
)


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
