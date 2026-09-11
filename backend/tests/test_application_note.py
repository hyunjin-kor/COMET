"""The Application Note must stay bound to the frozen runs and the journal's limits."""

import json

from scripts import build_application_note as note_builder
from scripts import build_submission_manuscript as paper


def test_note_renders_within_limits_and_matches_committed_files():
    run = note_builder.load_run()
    text = note_builder.note(run)
    record = note_builder.counts(text, run)
    assert record["total_word_equivalent"] <= note_builder.WORD_LIMIT
    assert record["software_named_in_title"]
    assert record["figure_count"] == 3
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
