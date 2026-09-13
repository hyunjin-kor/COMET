# AI figure-generation prompts — September 13, 2026

The author requested actual figure alternatives from GPT and Gemini after reviewing v31. This pass generates the two non-numerical diagrams: Figure 1 and Figure 2(a). The previously requested exclusion of Python-generated numerical results is retained. Figures 2(b,c), 3 and 4 are not redrawn by an image model.

## Execution and source status

- OpenAI: the built-in `image_gen` image-generation tool, not a paid API runner. The exact image-model version is not exposed by the tool and is not inferred.
- Google: image generation in the signed-in Gemini web interface, with the visible conversation selector set to `3.1 Pro` / `Pro`. This identifies the conversation mode; the underlying image-model version was not verified.
- The initial Figure 1 and Figure 2(a) prompts below were submitted to both services. Output-specific refinements followed visual review; the complete prompt log, unmodified downloaded PNGs, SHA-256 manifest, and comparison gallery are retained in `_local/note-figures/ai-candidates-2026-09-13/`.
- These are local design candidates. They have not replaced the canonical PowerPoint sources, generated article figures, English/Korean manuscript, or v31 Word documents. The canonical manuscript remains at 4,944/5,000 word-equivalent.
- The generation request authorizes sending the diagram specifications to the named services. No author details, full manuscript, CatCost source data, or frozen numerical data files were sent. One previously generated Gemini diagram was attached for a focused correction. No GitHub/Zenodo publication, payment, paid API call, or external correspondence was performed.
- The drawings are conceptual illustrations, not experimental observations. In Figure 2(a), pictured mixing, drying and furnace operations are representative preparation operations, not a universal process sequence. Detailed model equations, including the selling-price-based margin and order-size dependence, remain in the manuscript/caption.

## Review and later adoption

The OpenAI v2 images are the preferred candidates for structural clarity and illustrative detail. Early Gemini attempts had duplicated labels or damaged lettering; these are retained as rejected intermediates, not silently described as successful. Fresh Gemini generations provide separate comparison candidates. The local gallery records version-specific limitations.

If a candidate is adopted, integrate it through the figure source pipeline, synchronize English/Korean captions and AI-use disclosure, and rebuild and inspect the Word documents. Do not overwrite a canonical generated PNG or SVG by hand. An image model's nominal print-quality request does not establish vector editability or a specific resolution; use the actual PNG dimensions in the local manifest.

## Figure 1 — initial shared prompt

```text
Generate an actual image, not a written explanation or code.

Use case: infographic-diagram.
Asset: Figure 1 of a chemistry software journal article, showing COMET's workflow for estimating catalyst manufacturing costs and comparing candidates. Wide landscape, approximately 2.7:1, pure white background, crisp print-resolution image.

Create an exceptionally polished scientific editorial schematic, with the visual restraint and clarity of a Nature chemistry figure. Use precise, refined scientific illustrations with charcoal contours, deep teal #1B6F78, muted blue-teal #6FA8AE and cool greys. Very subtle tonal fills are acceptable within illustrations. No glossy 3D, cast shadows, gradients behind the diagram, banners, marketing graphics, oversized business icons, mascots, coins, rocket or comet imagery.

Show a coherent left-to-right five-stage workflow:
"Input data" → "Price basis" → "Cost estimation" → "Cost breakdown" → "Candidate ranking".
Use concise exact labels below five related illustrative vignettes, aligned on one reading line. Do not put the entire diagram inside boxes. Use short fine arrows, clear separation, and carefully balanced visual weight. Allow the central scientific calculation vignette slightly more emphasis.
1. Input data: neatly layered research data sheets and a small cluster of catalyst/support granules.
2. Price basis: a refined compact calendar with a single highlighted cell and a price-record sheet. No invented dates or numbers.
3. Cost estimation: a small preparation vessel and catalyst pellet accompanied by a precise cost-sheet motif; this represents calculation, not an experimental observation.
4. Cost breakdown: a ledger with three simple coloured component strips, no numerical axis and no pseudo-data.
5. Candidate ranking: three distinguishable catalyst specimens arranged for comparison beside an ordered list motif; no winning trophy and no invented scores.

Below the five stages, one understated shared record rail connects the workflow to a slim analysis-record strip. This must read as retained information shared by all stages, not a second scientific processing route.
Text on this strip, exactly: "Analysis record", "Data sources", "Model assumptions", "Reproducibility".
Text whitelist is ONLY the five stage names and these four strip labels. No figure number, title, caption, sentences, software version, footnotes, logos, watermark, tiny illegible filler text, date, number, or currency amount. Data sheets should contain quiet non-text rules, not gibberish. Use clean Helvetica/Arial-like lettering, readable when printed at 178 mm width.
The complete composition should feel drawn and art-directed as ONE scientific figure. Keep the icons refined and meaningful, with consistent viewpoint, line weight, scale and material treatment. Every label and arrow must be precisely aligned. Scientific clarity and controlled negative space take priority over decorative detail.
```

## Figure 2(a) — initial shared prompt

```text
Generate an actual image, not a written explanation or code.

Use case: infographic-diagram.
Asset: Figure 2(a) for a chemistry software journal article. A sophisticated scientific schematic of catalyst manufacturing cost estimation. Landscape, approximately 3:1, crisp print-resolution artwork on pure white.

Visual direction: restrained editorial illustration at the quality of a carefully art-directed Nature chemistry figure. Precise geometry and polished, small scientific pictograms, charcoal typography, deep teal #1B6F78, muted blue-teal #6FA8AE, cool grey and one restrained ochre accent. Generous white space. All text in a clean Helvetica/Arial-like sans serif. No poster title, no caption, no decorative border, no shadows, no glossy 3D, no clip-art calculator, no dollar-sign coins, no slogans.

The visual argument must be understood in one glance: TWO independent cost contributions are calculated, then combined, then overhead and margin are applied to obtain the estimated selling price. Organize this as two neatly aligned parallel lanes on the left, a clear convergence near the middle, and one simple output on the right. Avoid a forest of boxes and long empty arrows.

Upper lane: a beautifully drawn compact scientific vignette of a precursor bottle beside several catalyst/support granules and a small price-sheet motif. Label exactly "Formulation and prices". A short arrow leads to "Materials" with the mathematical symbol Cₘ.
Lower lane: a compact orthographic line illustration of a preparation sequence, such as mixing vessel, drying tray, and furnace, with a small batch-stack motif. These are representative preparation operations, not a claim that every catalyst uses all three. Label exactly "Route and order size". A short arrow leads to "Processing" with symbol Cₚ.
Both contributions feed the SAME small plus junction. From this junction, one short directed path passes through a restrained adjustment element labelled exactly "Overheads and margin" and ends at "Selling price" with symbol P. The result is an estimated selling price, not profit or revenue. The adjustment must NOT look like an independent raw-material input or a third additive cost measurement.

Text whitelist: "(a)", "Formulation and prices", "Route and order size", "Materials", "Processing", "Overheads and margin", "Selling price", "Cₘ", "Cₚ", "P", "+".
Spell every label exactly. Keep subscripts correct. Each label appears once. Use only these words and symbols; no equations, numbers, body text, footnotes or additional process labels. Put "(a)" at the upper left.
Science context for you, NOT text to draw: the calculation is P=(Cm+Cp)(1+g)(1+s)/(1-m). The margin m is a fraction of selling price; order size also affects the margin. These details are explained in the manuscript caption and must not be contradicted by the schematic.
Make the illustrations integral to a coherent, beautifully balanced diagram, not five unrelated large icons. Align lanes, text baselines and connector centers meticulously. Prioritize legibility at 178 mm total printed width.
```
