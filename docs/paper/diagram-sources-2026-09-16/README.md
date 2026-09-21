# Figure decks (2026-09-16)

Every manuscript and Supporting Information figure except Figure 1 is an editable
PowerPoint deck in this folder (Figure 1 remains in `../diagram-sources-2026-09-13-h26/`).
Slide 1 is English and slide 2 is Korean. Numeric panels are matplotlib renders of the
frozen COMET analysis files, embedded as images and listed with their checksums in
`panels/panels.json`; they are not editable data. Conceptual artwork is identified in
`artwork-provenance.json`. Panel letters and labels are native slide objects.

| Deck | Figure | Panels | Artwork |
|---|---|---|---|
| `fig2_cost_model.pptx` | Figure 2 | (b) selling-price shares, (c) market deviations | (a) OpenAI schematic, labels from the h26 deck |
| `fig3_manufacturing.pptx` | Figure 3 | (b) operating contributions, (c) calcination sweep | (a) OpenAI preparation sequence, labels from the 2026-09-15 deck |
| `fig4_ranking.pptx` | Figure 4 | calculator what-if analyses: (a) metal loading, (b) order size, (c) preparation procedure; (d) ammonia-cracking cost history, (e) Ni–Co equal-cost boundary | – |
| `figS4_metal_prices.pptx` | Figure S4 | (a) precious metals, (b) base metals | – |
| `figS2_sensitivity.pptx` | Figure S2 | one-at-a-time endpoints | – |
| `figS3_monte_carlo.pptx` | Figure S3 | (a) price histogram, (b) samples versus dry output | – |
| `figS7_evidence.pptx` | Figure S7 | preparation-evidence status by family | – |
| `figS5_crossovers.pptx` | Figure S5 | (a) methane dry reforming and (b) water–gas shift cost histories | – |
| `figS6_ranking_tests.pptx` | Figure S6 | (a) first-rank frequencies, (b) families retaining the baseline candidate under each test, (c) leader cost differences after candidate removal | – |
| `figS9_interface.pptx` | Figure S9 | – | application screenshots (isolated review database) |
| `figS1_allocation.pptx` | Figure S1 | – | Gemini concept of aliquot and transfer allocation |
| `figS8_provenance.pptx` | Figure S8 | – | Gemini concept of a source-linked record |

## Regenerate

```powershell
python scripts/draw_application_note_figures.py --panels
python scripts/draw_application_note_figures.py --panels --lang ko
# only when panels changed or a deck is being authored for the first time:
python scripts/build_note_figure_decks.py [deck names]
scripts/export_note_diagram_slides.ps1 -SourceDirectory docs/paper/diagram-sources-2026-09-16 -Names fig2_cost_model,fig3_manufacturing,fig4_ranking,figS4_metal_prices,figS2_sensitivity,figS3_monte_carlo,figS7_evidence,figS5_crossovers,figS6_ranking_tests,figS9_interface,figS1_allocation,figS8_provenance
python scripts/draw_application_note_figures.py
python scripts/draw_application_note_figures.py --lang ko
```

The export script rewrites `exports.json` with the named decks only, so pass every deck name as above
(or merge the new entry into the previous manifest). The default generator command re-renders the panels, refuses a deck that does not
embed the current panel images or an export whose checksum no longer matches
`exports.json`, and then copies the exports to `../figures-note-2026-09-09/`,
`../manufacturing-study-2026-09-15/figures/` and `../figures-si-2026-09-16/`.
Edit labels in the decks and re-export; do not retouch exported or published
figure files. `build_note_figure_decks.py` overwrites label edits, so rerun it only
for decks whose panels changed. The concept artwork carries an AI-use disclosure in
the adjacent caption and the Acknowledgments under ACS policy; none of it is a TOC graphic.
