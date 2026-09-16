# Manufacturing-condition study

This dated run is an illustrative software verification, not an experimentally
validated catalyst recipe, industrial quotation or optimum synthesis condition.
It preserves all assumed inputs, an independent arithmetic balance, the resolved
calculation, eight endpoint tests, 63 time/output scenarios, and 1,000 seeded
Monte Carlo samples. Unknown dry output is also tested as an invalid input.

See [Supporting Information](../supporting-information-2026-09-15.md) for the
boundary, units, formulas, full input tables, results and limitations.
The preparation evidence library is a separate dataset; it does not supply the
hypothetical operating costs or dry output in this study.

From the COMET repository root:

```text
python scripts/reproduce_manufacturing_study.py --check
python -m pytest backend/tests/test_manufacturing_study.py -q
python scripts/draw_application_note_figures.py --panels
python scripts/draw_application_note_figures.py --panels --lang ko
python scripts/draw_application_note_figures.py
python scripts/draw_application_note_figures.py --lang ko
python -m scripts.build_note_si --check
```

To intentionally regenerate this run after a reviewed implementation change,
omit `--check`, then regenerate its figures, SI and main manuscript. Code hashes
are normalized to UTF-8 text with LF line endings. The source manifest and each
input's assumption record distinguish this calculation from physical measurements.
The numerical outputs are not altered in a drawing program. Since 16 September 2026
the complete Figure 3 is an editable deck, `fig3_manufacturing.pptx` in
[diagram-sources-2026-09-16](../diagram-sources-2026-09-16/README.md), which embeds the
rendered panels (b) and (c) as images and carries the conceptual artwork and labels;
`figures/fig_manufacturing*.png|svg` are its PowerPoint exports. The earlier
[diagram-sources-2026-09-15](../diagram-sources-2026-09-15/README.md) deck is retained as the
artwork and label source that was transplanted into the 2026-09-16 deck.
