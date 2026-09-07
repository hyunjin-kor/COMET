"""Submission claims must remain bound to both frozen scientific runs."""

import pytest

from scripts import build_submission_manuscript as paper


def test_submission_distinguishes_controlled_channels_from_historical_replay():
    run = paper.PaperRun(paper.PAPER / 'submission-2026-09-07')
    text = paper.manuscript(run)
    assert 'summary.changed_winner_counts.evidence_only' in text
    assert 'summary.changed_winner_counts.price_only' in text
    assert 'distinct from the historical metal-series replay' in text
    assert 'not a purely measured-cost ranking' in text
    assert 'legacy records declaring CatCost workbook/sheet origins' in text
    assert paper.verify_references(text, run) > 80
    assert paper.verify_references(paper.supporting_information(run), run) > 1100


def test_changed_controlled_numerics_cannot_build_submission(monkeypatch):
    original = paper.digest
    monkeypatch.setattr(paper, 'digest', lambda path: 'changed' if path == paper.PAPER / paper.CONTROLLED_NAME else original(path))
    with pytest.raises(ValueError, match='Controlled numerical output changed'):
        paper.PaperRun(paper.PAPER / 'submission-2026-09-07')


def test_controlled_seed_mismatch_is_rejected(monkeypatch):
    original = paper.load

    def load(path):
        value = original(path)
        if path == paper.PAPER / paper.CONTROLLED_NAME:
            value['seed'] += 1
        return value

    monkeypatch.setattr(paper, 'load', load)
    with pytest.raises(ValueError, match='seeds differ'):
        paper.PaperRun(paper.PAPER / 'submission-2026-09-07')
