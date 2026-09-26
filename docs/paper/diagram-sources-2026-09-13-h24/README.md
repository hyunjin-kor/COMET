# COMET diagram sources — H24, September 13, 2026

These are the current sources for Figure 1 and Figure 2(a). Slide 1 is English;
slide 2 is Korean. Each slide combines an unchanged generated illustration with
native editable PowerPoint labels. The selected GPT v2 images and the preceding
Korean localizations remain in `../diagram-sources-2026-09-13-gpt/`.

The OpenAI image-generation tool removed lettering from the selected English
illustrations. The two returned PNG files in `artwork/` were copied unchanged and
embedded without manual raster edits, cropping, or distortion. Both languages
use the same text-free artwork. These are new generated images; non-text pixels
are not asserted to be identical to the earlier illustrations. The exact image
model/version was not exposed by the tool: **확인 못 함**.

| Source | Slide size (mm) | Illustration pixels | Native text objects per slide |
| --- | --- | --- | --- |
| `fig1_workflow.pptx` | 178 × 65.930 | 2060 × 763 | 9 |
| `fig2a_cost_model.pptx` | 178 × 59.333 | 2172 × 724 | 13 |

Workflow labels use 9.5 pt Arial in English and Malgun Gothic in Korean; record
labels use 8.5 pt. Cost-node labels use 8.5–9.5 pt, cost symbols 12 pt with
subscripts, and the panel label 10 pt. The source decks are authoritative for
subsequent typography edits. Illustrations and connectors remain raster artwork;
these decks and SVG files are not entirely vector illustrations.

Microsoft PowerPoint exports the slides to a 400 dpi PNG canvas and SVG with an
embedded illustration and native vector text. The original illustrations provide
293.96 and 309.94 dpi, respectively, at 178 mm width; resampling does not add detail.
The figure generator preserves vector numerical panels when composing Figure 2.
The equipment and materials are schematic, not experimental observations.
The illustrated operations do not prescribe a common route for all catalysts.

Edit the source decks, then run `scripts/export_note_diagram_slides.ps1`.
Run `scripts/draw_application_note_figures.py` and its `--lang ko` variant
to regenerate the canonical assets. `exports.json` binds each source and output
by SHA-256; the generator rejects stale exports. `artwork-provenance.json` records
the generated files, input images, and exact prompts. Do not hand-edit the exports.

The design follows the clean alignment and restrained typography principles in
[Nature's figure guide](https://research-figure-guide.nature.com/figures/building-and-exporting-figure-panels/).
It remains a JCIM Application Note: this is not a claim of compliance with
Nature's numerical artwork specifications. The author's larger-text preference,
four-sided axes, parenthesized panel labels, and selected illustration style take
precedence. Explanations, equations, and interpretation are in the manuscript;
captions retain short titles, panel definitions, and image-generation disclosure.
