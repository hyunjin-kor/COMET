# COMET diagram sources — H26, September 13, 2026

These are the current Figure 1 and Figure 2(a) sources. Each deck contains
English and Korean slides. Figure 2(a), its artwork and labels are unchanged
from H24. Previous source folders are retained.

Figure 1 retains the original upper workflow artwork and five native labels
at their previous size and position. The original PNG bytes are embedded
unchanged; a native PowerPoint picture crop hides the former narrow record
strip. This preserves the upper artwork rather than regenerating it.

Four new record illustrations were generated with the built-in OpenAI
image-generation tool using the H24 text-free workflow as a style reference.
They represent a saved analysis record, dated source documents, calculation
assumptions, and repeatable calculations. The report marks are schematic
illustration elements, not measured data. The new PNG is embedded unchanged.
Native picture cropping removes surrounding whitespace. No raster image or
canonical figure export was manually edited.

The larger lower row uses one illustration per record item, a shared connector
branch, and native 10.5 pt bold labels below the illustrations. Previously the
record labels were 8.5 pt alongside small line icons. Upper labels remain
9.5 pt. English uses Arial and Korean uses Malgun Gothic.

| Source | Slide size (mm) | Native labels per slide |
| --- | --- | --- |
| fig1_workflow.pptx | 178 × 102 | 9 |
| fig2a_cost_model.pptx | 178 × 59.333 | 13 |

The upper Figure 1 illustration is 2060 × 763 pixels and the new lower row
is 2172 × 724. At their source-deck widths of 178 and 166 mm, respectively,
they provide approximately 294 and 332 dpi. The 400 dpi PowerPoint output
canvas does not add illustration detail. The SVG contains raster artwork
and vector text/connectors; it is not entirely vector artwork. Figure 2's
numerical panels remain vector plots generated from frozen data.

Exact generation prompts, dates, input hashes and original output hashes are
in artwork-provenance.json and artwork/*.prompt.md. The exact image model
version was not exposed by the tool: **확인 못 함**.

Figure 1 remains authored here. Since 16 September 2026 the Figure 2(a) labels
of fig2a_cost_model.pptx live in ../diagram-sources-2026-09-16/fig2_cost_model.pptx,
which holds the complete Figure 2; this fig2a deck is retained as their source.
Edit the source decks, then run scripts/export_note_diagram_slides.ps1.
Run scripts/draw_application_note_figures.py and its --lang ko variant to
regenerate the canonical figures. exports.json binds sources and exports by
SHA-256, and the generator rejects stale exports. Do not edit generated
PNG/SVG files directly. The original slide authoring and crop repair scripts
are retained in the private build directory. PowerPoint's native crop must
remain asymmetric on the upper image to preserve its original placement.

Figure 1 remains one double-column figure. Detailed explanations stay in
the manuscript, and the short caption retains the image-generation disclosure.
The English and Korean AI acknowledgments include the new record artwork.
