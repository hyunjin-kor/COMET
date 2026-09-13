# Selected GPT paper diagrams

The author selected both GPT v2 candidates on September 13, 2026. This folder
is the current source for Figure 1 and Figure 2(a). The preceding editable
diagrams remain in `../diagram-sources-2026-09-13/` as the v31 archive.

Each PPTX embeds the selected English image on slide 1 and its Korean localization
on slide 2. The PNG bytes in `artwork/` are unmodified image-generation outputs.
The decks contain a full-slide white frame and the image, without cropping or
distortion. Labels, illustrations and connectors are part of the raster artwork;
they are not individually editable PowerPoint objects. Do not describe these
sources or their SVG exports as fully vector artwork.

| Source | Slide size | Original pixels, both languages | Effective resolution at 178 mm width |
| --- | --- | --- | --- |
| `fig1_workflow.pptx` | 178 × 65.930 mm | 2060 × 763 | 293.96 dpi |
| `fig2a_cost_model.pptx` | 178 × 59.333 mm | 2172 × 724 | 309.94 dpi |

Microsoft PowerPoint exports a 400 dpi PNG canvas. This resampling does not add
detail beyond the original pixel dimensions above. Its SVG contains an embedded
raster image. The combined Figure 2 SVG preserves vector data panels (b,c).
No external editor or upscaler was used on the generated artwork.

The images are conceptual illustrations, not experimental observations.
Preparation equipment and operations are representative, not a process sequence
prescribed for every catalyst. The captions define the cost model and symbols;
the manuscript explains source records, assumptions, and numerical calculations.
The figure captions and acknowledgments disclose the image-generation use.

`artwork-provenance.json` records original image hashes and dimensions.
`prompts/` preserves the initial and refinement prompts that produced the
selected English candidates. The complete candidate history remains local;
the common comparison brief is in `../figure-generation-prompts-2026-09-13.md`.
`korean-localization-prompts.md` records the two additional calls used to translate
labels. Korean output retained the selected composition; pixel-identical artwork
outside the labels is not asserted. The underlying image-model version is
확인 못 함 because the tool did not expose it.

For a later change, update the source artwork through image generation or edit
the source deck as explicitly requested. Keep both language slides synchronized.
Do not hand-edit exported PNG/SVG files. After saving source changes, run from
the repository root:

```powershell
./scripts/export_note_diagram_slides.ps1
python scripts/draw_application_note_figures.py
python scripts/draw_application_note_figures.py --lang ko
python scripts/build_application_note.py --check
python -m pytest backend/tests/test_application_note.py -q
python -m ruff check scripts/
```

`exports.json` binds the decks and exports by SHA-256. The figure generator
rejects stale exports. It copies Figure 1 and places Figure 2(a) above the frozen
numerical panels. Figure 2 is now 178 × 207 mm; the numerical axes retain their
previous physical dimensions. Figures 3 and 4 and all frozen input JSON are unchanged.

If captions or prose change, edit `scripts/build_application_note.py`, synchronize
the local Korean source, and rebuild the manuscript before the checks above.
The accepted English image sources must remain available for provenance.
