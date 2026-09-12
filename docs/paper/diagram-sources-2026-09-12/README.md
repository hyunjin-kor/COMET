# Editable paper diagrams

These PowerPoint files are the editable sources for the non-data diagrams in the
Application Note. Each deck contains English on slide 1 and Korean on slide 2.

| Source | Paper use | Intended size |
| --- | --- | --- |
| `fig1_workflow.pptx` | Figure 1 | 178 × 100 mm |
| `fig2a_cost_model.pptx` | Figure 2(a) | 178 × 76 mm |

Edit labels, boxes, equations, and connectors in PowerPoint. Figure 1 retains the
five original illustrated icons as embedded images. Equation symbols, subscripts,
fraction bars, and connecting lines are editable slide objects; they are not
screenshots or Office equation objects. Keep both language slides synchronized.
Do not overwrite these decks by running an older slide builder.

After saving an edited deck, run from the repository root:

```powershell
./scripts/export_note_diagram_slides.ps1
python scripts/draw_application_note_figures.py
python scripts/draw_application_note_figures.py --lang ko
python scripts/build_application_note.py --check
python -m pytest backend/tests/test_application_note.py -q
python -m ruff check scripts/
```

The export script opens an untitled copy of each deck without a window in installed
Microsoft PowerPoint. It exports PNG at 400 dpi relative to slide size and SVG,
without saving changes to the source. PNG uses
[Slide.Export](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slide.export);
SVG uses [Shape.Export](https://learn.microsoft.com/en-us/office/vba/api/powerpoint.shape.export)
on a temporary group containing the slide objects and its white background.

`exports.json` binds each export to the source deck and output SHA-256 hashes.
The figure generator rejects changed source decks or altered exports until this
export step is repeated. Routine figure regeneration and tests use these checked
exports and do not require PowerPoint.

The figure generator copies Figure 1 exports directly and combines Figure 2(a)
with the Python plots in Figure 2(b,c). It preserves native SVG text and paths in
the combined SVG. The numerical panels, Figures 3 and 4, and all frozen JSON
remain generated from the original analysis records. Figure 2 is now 178 × 194 mm;
the numerical panels retain their previous physical size. Figure count and column
widths are unchanged.

Figure 1's earlier ChatGPT image-generation history and icon attribution remain in
[its provenance record](../figures-note-2026-09-09/fig1_workflow_stack.provenance.md)
and in the manuscript caption and acknowledgments. These decks introduce no new
image-generation output or numerical results. Cost-method attribution remains in
the manuscript and Figure 2 caption.
