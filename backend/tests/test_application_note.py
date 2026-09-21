"""The Application Note must stay bound to the frozen runs and the journal's limits."""

import json
import math
import shutil

import pytest

from scripts import build_application_note as note_builder
from scripts import build_submission_manuscript as paper


def test_si_publication_labels_preserve_every_frozen_screening_value():
    from scripts import build_note_si as si
    from scripts.paper_labels import CANDIDATE_LABELS, FAMILY_LABELS
    from scripts.paper_units import PER_LB_TO_PER_KG

    text = si.render()
    assert text == si.OUTPUT.read_text(encoding="utf-8")
    section = text.split("Table S7. ", 1)[1].split("Names identify", 1)[0]
    rows = [line.strip("|").split("|") for line in section.splitlines()
            if line.startswith("| ")][1:]
    source = si.load(f"{si.RUN}/all_families_{si.RUN_DATE}.json")
    expected = [(f["family"], c) for f in source["families"] for c in f["candidates"]]
    assert len(rows) == len(expected) == 116
    for row, (family, candidate) in zip(rows, expected, strict=True):
        assert row[0].strip() == FAMILY_LABELS[family]
        assert row[1].strip() == CANDIDATE_LABELS[family][candidate["slug"]]
        assert float(row[2]) == pytest.approx(candidate["landed_cost_per_lb"] * PER_LB_TO_PER_KG, abs=0.000051)
        assert float(row[3]) == pytest.approx(candidate["lca"]["coverage_pct"], abs=0.0051)
    assert "RWGS (reverse water–gas shift)" in section
    assert "| rwgs |" not in text
    assert "premium" not in section and "workhorse" not in section and "lifetime play" not in section


def test_preparation_tables_cover_the_same_candidates_with_readable_names():
    from scripts import build_manufacturing_literature_review as evidence
    from scripts import build_note_si as si
    from scripts.paper_labels import CANDIDATE_LABELS, FAMILY_LABELS, STATUS_LABELS

    library = si.load("backend/data/manufacturing_literature.json")
    rendered = evidence.render(library)
    for candidate in library["candidates"]:
        family, slug = candidate["family"], candidate["slug"]
        assert f"{FAMILY_LABELS[family]} / {CANDIDATE_LABELS[family][slug]}" in rendered
        assert STATUS_LABELS[candidate["status"]] in rendered
    assert "| rwgs /" not in rendered
    assert "| source_mismatch |" not in rendered


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


def _figure_numbers(captions, tool):
    """Figure labels whose caption discloses artwork from the named tool."""
    import re

    return {match.group(1) for match in re.finditer(r"!\[Figure (S?\d+)\.([^\]]*)\]", captions) if tool in match.group(2)}


def test_ai_artwork_acknowledgment_matches_the_disclosing_captions():
    """Renumbered figures must not leave the Acknowledgments pointing at the wrong artwork."""
    import re

    from scripts import build_note_si as si

    note_text = note_builder.note(note_builder.load_run())
    si_text = si.render()
    acknowledgment = note_text.split("## Acknowledgments", 1)[1].split("## Competing interests", 1)[0]
    gemini = {"S" + n for n in re.findall(r"Supporting Information Figures? S(\d+)(?: and S(\d+))?", acknowledgment)[0] if n}
    assert gemini == _figure_numbers(si_text, "Gemini")
    openai = _figure_numbers(note_text, "OpenAI")
    assert openai == {"1", "2", "3"} and "Figures 1–3" in acknowledgment
    assert "Anthropic Claude" in acknowledgment


def test_si_tables_are_numbered_and_cited_in_order():
    import re

    from scripts import build_note_si as si

    text = si.render()
    captions = [int(n) for n in re.findall(r"^Table S(\d+)\. ", text, flags=re.M)]
    assert captions == list(range(1, len(captions) + 1))
    first_citation = []
    for match in re.finditer(r"Tables? S(\d+)(?:(?:–| and |, )S?(\d+))?", text):
        for number in (match.group(1), match.group(2)):
            if number and int(number) not in first_citation:
                first_citation.append(int(number))
    assert first_citation == captions


def test_reference_example_matches_a_fresh_calculation():
    from scripts import record_note_reference_example as example

    stored = json.loads(example.OUTPUT.read_text(encoding="utf-8"))
    assert stored == json.loads(json.dumps(example.record()))
    assert stored["nickel_quote"]["source"].startswith("IMF")
    assert stored["alumina_row"]["material_key"] == example.ALUMINA_KEY


def test_note_reuses_the_manuscript_numbers():
    run = note_builder.load_run()
    text = note_builder.note(run)
    assert f"{note_builder.RUN}/paper_summary_{note_builder.RUN_DATE}.json:table62[0].comet_usd_per_lb" in text
    assert f"{note_builder.ROBUSTNESS}:summary.candidate_removal_winner_changes" in text
    assert f"{note_builder.MARKET}:[1].margin.comet_pct_of_premargin" in text
    assert f"{note_builder.WHATIF}:order_size.ni[10].selling_price_per_lb" in text
    assert "Accuracy against industrial prices is not established" in text


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


def test_rank_reversal_cost_difference_matches_independent_ammonia_example():
    pytest.importorskip("matplotlib")
    from scripts import draw_application_note_figures as figures

    methods = json.loads(figures.METHODS.read_text(encoding="utf-8"))
    example = methods["normalization"]["example"]["rows"]
    baseline, alternative = example[0]["cost"], example[2]["cost"]
    expected = 100 * (alternative - baseline) / baseline
    figures.set_language("en")
    fig = figures.figure4_diagnostics()
    try:
        ax = fig.axes[-1]
        labels = [label.get_text().replace("\n", " ") for label in ax.get_yticklabels()]
        assert len(ax.patches) == len(labels) == methods["normalization"]["changed"]
        bar = ax.patches[labels.index("Ammonia cracking")]
        assert bar.get_width() == pytest.approx(expected)
        assert bar.get_x() == 0
        assert ax.get_xscale() == "linear"
    finally:
        figures.plt.close(fig)


@pytest.mark.parametrize("changed_file", ["fig2_cost_model.pptx", "exports/fig2_cost_model.en.png"])
def test_changed_deck_or_export_requires_a_new_powerpoint_export(tmp_path, monkeypatch, changed_file):
    pytest.importorskip("matplotlib")
    from scripts import draw_application_note_figures as figures

    decks = tmp_path / "decks"
    (decks / "exports").mkdir(parents=True)
    for relative in ("exports.json", "fig2_cost_model.pptx", "exports/fig2_cost_model.en.png", "exports/fig2_cost_model.en.svg"):
        shutil.copyfile(figures.DECKS / relative, decks / relative)
    figures.set_language("en")
    assert figures._diagram_asset("fig2_cost_model", "png", decks).is_file()
    modified = decks / changed_file
    modified.write_bytes(modified.read_bytes() + b"changed after export")
    with pytest.raises(ValueError, match="run scripts/export_note_diagram_slides.ps1"):
        figures._diagram_asset("fig2_cost_model", "png", decks)


def test_figure_decks_embed_the_current_numeric_panels():
    """A changed frozen input or an unrebuilt deck must fail before any figure is published."""
    pytest.importorskip("matplotlib")
    from scripts import draw_application_note_figures as figures

    for lang in ("en", "ko"):
        figures.set_language(lang)
        figures.check_panels_current()
    figures.verify_decks()
    manifest = json.loads((figures.PANELS / "panels.json").read_text(encoding="utf-8"))
    assert {row["figure"] for row in manifest["panels"]} == set(figures.PANEL_LAYOUTS)
    assert len(manifest["panels"]) == 2 * sum(len(boxes) for _f, boxes in figures.PANEL_LAYOUTS.values())


def test_note_states_the_cost_only_scope_and_the_planned_performance_coupling():
    text = note_builder.note(note_builder.load_run())
    limitations = text.split("### Limitations", 1)[1].split("## Conclusions", 1)[0]
    conclusions = text.split("## Conclusions", 1)[1].split("## Supporting Information", 1)[0]
    assert "manufacturing cost only" in limitations and "not measured or predicted activity" in limitations
    assert "performance-prediction models" in conclusions


def test_whatif_study_matches_a_fresh_calculation():
    from scripts import note_whatif_study as whatif

    stored = json.loads(whatif.OUTPUT.read_text(encoding="utf-8"))
    assert stored == json.loads(json.dumps(whatif.study()))
    assert stored["inputs"]["reference_basis"].endswith(f"reference_basis_{note_builder.RUN_DATE}.json")
