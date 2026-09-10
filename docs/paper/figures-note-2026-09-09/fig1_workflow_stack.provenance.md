# Figure 1 provenance (Application Note, 2026-09-09 draft)

`fig1_workflow_stack.png` is an AI-assisted illustration, not an output of `scripts/draw_application_note_figures.py`. This note records how it was made so that the caption and the AI-use statement in the manuscript can be checked.

## Files

| File | Role |
|---|---|
| `fig1_workflow_stack_raw_chatgpt.png` | Raw image as downloaded from ChatGPT (1672 x 941 px), unmodified |
| `fig1_workflow_stack.png` | Final figure: raw image with the connector lines redrawn by `scripts/straighten_note_fig1_leaders.py` (byte-identical to the script output) |

## Generation

- Tool: ChatGPT image generation (OpenAI), used through the chatgpt.com web interface in a conversation titled "Generate Figure Schematic". The interface names the chat model tier ("Pro") but not the image model, so the image model version is not recorded here.
- Dates: candidate versions A to D on 2026-09-09; the adopted version (a cleaned variant of D) on 2026-09-10.
- Content: every label, layer name and pictogram was specified in writing by the authors. The tool contributed the drawing only. The authors compared every word of the output with the specification; the only correction needed was `cm2` to `cm²`, which the final prompt fixed.
- Authors' edits: the raw image had stepped dotted leaders between the five bands and the provenance panel. The script clears the gap between the bands and the panel, removes the leader stubs inside the panel and draws one straight horizontal dotted leader per band. Nothing else was altered.

## Prompts (verbatim, in order)

1. Initial specification (version A):

   > Generate an image (PNG, wide 16:9, print quality) of Figure 1 for a journal article, in the restrained style of a Nature or ACS schematic. Hard rules: white background; flat vector look; Helvetica-like sans-serif; thin dark-grey outlines; no drop shadows, no 3D, no gradients, no glow; one accent colour (teal #1B6F78) plus greys; NO title, NO caption, NO logo, NO watermark, NO words other than those listed; spell every label exactly; keep text small. Content: five horizontal layers stacked top to bottom as light-grey rounded bands, each with a small monoline icon at the left, a bold layer name, and short items; thin downward arrows between bands. Layer 1 (icon: database): 'Price sources' - 'IMF PCPS, Johnson Matthey, UN Comtrade, USGS' / 'Library: 116 catalysts, 30 reactions'. Layer 2 (icon: calendar): 'Price basis' - 'Live tier: current quotes' / 'Reference tier: frozen monthly averages'. Layer 3 (icon: flask with calculator): 'Cost model' - 'Materials and precursor recipe' / 'Step Method processing, overhead, margin' / 'Electrode per cm2; partial LCA'. Layer 4 (icon: ledger sheet): 'Cost ledger' - 'Price, source, date, grade per line' / 'Steps priced, substituted or uncosted' / 'Monte Carlo range; CSV export'. Layer 5 (icon: balance scale): 'Decision analysis' - 'Weighted composite score' / 'Weight sensitivity; monthly price replay' / 'Leave-one-out removal; score perturbation'. On the right, a tall narrow pale-teal panel headed 'Provenance' with eight bullet items: 'Source and quote date', 'Reliability grade', 'Price basis', 'Manufacturing scope', 'Functional unit', 'LCA coverage', 'SHA-256 input hashes', 'Seed and environment', linked to each layer by thin dotted leader lines.

2. Version D (illustrated):

   > Version D: generate another image with the same content, the same exact labels and the same hard rules (no title, no extra words, white background, one teal accent plus greys, flat, small text). Style change only: restrained two-tone flat illustration instead of icons - at the left of each band place one small flat illustration: a short stack of price tables for 'Price sources', a calendar with one month highlighted for 'Price basis', a reactor flask with a cost ticket for 'Cost model', a printed ledger sheet for 'Cost ledger', and a balance weighing three catalyst pellets for 'Decision analysis'; keep the five light-grey bands stacked top to bottom with thin downward arrows and the pale-teal 'Provenance' panel with its eight bullet items on the right.

3. Clean-up of version D:

   > Redo Version D (the fourth image) as a clean final image. Keep the five light-grey bands stacked top to bottom with thin teal downward arrows, the same exact labels and the same hard rules (no title, no caption, no logo, no words other than the labels, white background, teal #1B6F78 plus greys only, flat, no gradients, no shadows, small sharp text). Fix 1: the five flat illustrations at the left must be simple, clean and fully drawn with NO letters or text inside them - a neat stack of three blank price tables, a calendar with one cell highlighted in teal, a conical flask half-filled with teal beside a plain blank cost ticket, a printed ledger sheet with a blank grid, and a two-pan balance holding three round grey catalyst pellets; every shape closed, aligned and the same visual size. Fix 2: write 'Electrode per cm²; partial LCA' with a real superscript ². Fix 3: redesign the right-hand 'Provenance' panel - one pale-teal rounded panel spanning exactly the height of the five bands, a bold heading 'Provenance' at its top, and the eight items evenly spaced down the panel, each as a white rounded tag with a small teal monoline icon at its left: calendar for 'Source and quote date', shield with a check mark for 'Reliability grade', price tag for 'Price basis', factory for 'Manufacturing scope', ruler for 'Functional unit', leaf for 'LCA coverage', hash sign for 'SHA-256 input hashes', dice for 'Seed and environment'; a thin dotted leader runs from the right edge of each band to the panel; equal margins everywhere and all text horizontally aligned.

4. Adopted variant (D2, the raw file above):

   > Variant D2: generate one more image, same as the last image (same bands, same exact labels, same rules, same right-hand 'Provenance' panel with the eight icon tags and dotted leaders, keep 'cm²'). Change only the five left illustrations: make them larger flat two-tone illustrations in the spirit of the fourth image rather than small icons - a neat stack of three blank price tables with ruled rows, a desk calendar with one cell filled teal, a conical flask half-filled with teal next to a blank cost ticket, a printed ledger sheet with a blank grid curling slightly at one corner, and a two-pan balance holding three round grey catalyst pellets - all drawn cleanly with closed shapes, no letters or text inside, all the same visual size and vertically centred in their bands.

## Journal policy and rights

- ACS Publications, "Artificial Intelligence (AI) Best Practices and Policies" (https://researcher-resources.acs.org/publish/aipolicy, read 2026-09-10): the use of AI tools for image generation must be disclosed in the Acknowledgments with a description of when and how the tools were used, and "for graphics, a brief description of AI use should be included in the figure caption to explain to readers how the image was created". AI-generated images must not be used in the Table of Contents graphic. The manuscript caption and AI-use statement follow this wording; the TOC graphic must not reuse this illustration.
- Rights to the output: 확인 못 함. The OpenAI Terms of Use page (https://openai.com/policies/terms-of-use/) could not be retrieved on 2026-09-10 (HTTP 403 to automated requests, browser load timed out). The authors must read the terms in force on the generation dates and confirm that the output may be used in a publication before submission.
