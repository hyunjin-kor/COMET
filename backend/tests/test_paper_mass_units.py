"""Publication unit conversion must preserve the frozen scientific comparisons."""

import csv
import json
import re

import pytest

from scripts import build_application_note as note
from scripts import draw_application_note_figures as figures
from scripts.export_price_crossovers_kg import mechanisms_in_kg
from scripts.paper_units import publication_cost


def test_exact_mass_conversion_and_unchanged_area_basis():
    assert publication_cost(453.59237, "$/lb") == pytest.approx(1000)
    assert publication_cost(31.1034768, "$/troy_oz") == pytest.approx(1000)
    assert publication_cost(23, "$/kg") == 23
    assert publication_cost(0.01234, "$/cm2") == 0.01234
    with pytest.raises(KeyError):
        publication_cost(1, "$/oz")  # An unspecified ounce is not a troy ounce.


def test_note_converts_every_mass_value_and_preserves_source_references():
    run = note.load_run()
    text = note.note(run)
    visible = re.sub(r"<!--.*?-->", "", text)
    assert not re.search(r"USD/lb|USD/troy|per lb|in lb|short ton", visible)
    assert "60.3394" in visible and "60,781.4" in visible and "18,143.7" in visible
    records = run.publication_conversions
    # 17 original conversions plus the four cobalt-price and October-2025 cost values of the crossover paragraph.
    assert len(records) == 21
    assert sum("per_lb" in row["key"] for row in records) == 11
    for row in records:
        assert row["display"] + "<!-- " + row["source"] + ":" + row["key"] + " -->" in text
    assert re.search(r"0\.85 USD/kg (?:cost )?difference", visible)


def test_all_metal_history_points_are_converted_without_smoothing():
    series = json.loads(figures.HISTORY.read_text(encoding="utf-8"))["series"]
    figures.set_language("en")
    fig = figures.figure3_metal_prices()
    try:
        for ax, symbols in zip(fig.axes, (figures.PRECIOUS_METALS, figures.BASE_METALS), strict=True):
            assert "USD/kg" in ax.get_ylabel()
            for line, symbol in zip(ax.lines[:len(symbols)], symbols, strict=True):
                divisor = 0.0311034768 if series[symbol]["unit"] == "$/troy_oz" else 0.45359237
                expected = [point["price"] / divisor for point in series[symbol]["points"]]
                assert list(line.get_ydata()) == pytest.approx(expected)
                assert len(expected) == 89
    finally:
        figures.plt.close(fig)


def test_all_publication_csv_rows_preserve_scores_and_cost_order():
    directory = figures.ROOT / "docs/paper/price-crossovers-2026-09-13"
    study = json.loads((directory / "price_crossovers.json").read_text(encoding="utf-8"))
    lookup = {(f["family"], period, row["date"]): (f["unit"], row)
              for f in study["families"] for period, data in f["periods"].items() for row in data["records"]}
    with (directory / "candidate_costs.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 30740
    for row in rows:
        unit, source = lookup[row["family"], row["period"], row["date"]]
        slug = row["candidate"]
        divisor = 0.45359237 if unit == "$/lb" else 1
        assert float(row["modeled_cost"]) == pytest.approx(source["costs"][slug] / divisor, rel=1e-12)
        assert row["unit"] == ("$/kg" if unit == "$/lb" else unit)
        assert float(row["application_score"]) == source["scores"][slug]["total"]
        assert float(row["frozen_nonprice_continuous_score"]) == source["continuous_scores"][slug]
        assert row["lowest_cost"] == str(slug == source["cost_winner"])
        assert row["application_first"] == str(slug == source["app_winner"])
    source = json.loads((directory / "crossover_mechanisms.json").read_text(encoding="utf-8"))
    preserved = json.dumps(source, sort_keys=True)
    converted = mechanisms_in_kg(source)
    assert json.dumps(source, sort_keys=True) == preserved
    for key in ("gap_low", "gap_high"):
        assert converted["photo_daily"]["threshold_bracket"][key] == source["photo_daily"]["threshold_bracket"][key]
    assert converted["photo_daily"]["Pt_threshold"] == pytest.approx(77785.68436194908)
    assert converted["cases"][0]["costs_after"]["ni-alumina-baseline"] == pytest.approx(8.888816)
