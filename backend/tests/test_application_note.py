"""The Application Note must stay bound to the frozen runs and the journal's limits."""

import json
import math

import pytest

from scripts import build_application_note as note_builder
from scripts import build_submission_manuscript as paper


def test_note_renders_within_limits_and_matches_committed_files():
    run = note_builder.load_run()
    text = note_builder.note(run)
    record = note_builder.counts(text, run)
    assert record["total_word_equivalent"] <= note_builder.WORD_LIMIT
    assert record["software_named_in_title"]
    assert record["figure_count"] == 4
    assert record["json_key_references"] > 40
    committed = (paper.PAPER / f"application-note-{note_builder.DATE}.md").read_text(encoding="utf-8")
    assert committed == text
    saved = json.loads((paper.PAPER / f"application_note_checks_{note_builder.DATE}.json").read_text(encoding="utf-8"))
    assert saved == record


def test_note_reuses_the_manuscript_numbers():
    run = note_builder.load_run()
    text = note_builder.note(run)
    assert "submission-2026-09-08/paper_summary_2026-09-08.json:table62[0].comet_usd_per_lb" in text
    assert "robustness-2026-09-08/decision_robustness.json:summary.candidate_removal_winner_changes" in text
    assert "methods-2026-09-09/methods_study.json:normalization.example.rows[0].total_after" in text
    assert "mean absolute percentage error" in text and "unestimated" in text


def test_trade_plot_preserves_months_with_missing_observations():
    pytest.importorskip("matplotlib")
    from scripts import draw_application_note_figures as figures

    study = json.loads(figures.STUDY.read_text(encoding="utf-8"))
    months = {row["month"] for row in study["families"][0]["monthly_ledgers"]}
    market = json.loads(figures.MARKET.read_text(encoding="utf-8"))["series"]
    fig = figures.plt.figure()
    gaps = 0
    try:
        figures._market_panel(fig)
        for ax, (code, _) in zip(fig.axes, figures.MARKET_GROUPS, strict=True):
            observed = {p["date"][:7] for p in market[code]["points"] if p["price"] > 0}
            for line in ax.lines[:-1]:  # The last line is the unit-ratio reference.
                dates, ratios = line.get_data()
                assert {date.strftime("%Y-%m") for date in dates} == months
                for date, ratio in zip(dates, ratios, strict=True):
                    missing = date.strftime("%Y-%m") not in observed
                    assert math.isnan(ratio) == missing
                    gaps += missing
        assert gaps > 0, "The frozen trade record includes missing monthly observations"
    finally:
        figures.plt.close(fig)
