# COMET manuscript and manufacturing-study reproduction

This snapshot accompanies the September 15, 2026 manuscript revision. The
application version remains 1.4.0; the source commit and SHA-256 file manifest
identify the supplied local implementation more precisely than the version label.

The preparation library contains 92 records from 71 primary sources, linked to
75 of 116 screening candidates. These links can describe related formulations.
They do not establish complete industrial cost validation. The other 41 candidates,
26 source-mismatch flags, missing recoveries and missing operating inputs are
reported explicitly. The manufacturing study is an assumed software demonstration;
its prices, dry output and operating inputs are not experimental measurements.

## Contents

- `backend/data/manufacturing_literature.json`: preparation records, original
  values, source locators, candidate assessments and literature-review metadata.
- `backend/data/manufacturing_operating_references.json`: separately scoped
  operating references; these do not supply measured batch power or staffing.
- `docs/paper/manufacturing-literature-2026-09-14.md`: complete readable evidence
  companion, including unresolved inputs.
- `docs/paper/supporting-information-2026-09-15.md`: methods, assumed inputs,
  independent cost balance, sensitivity results and frozen screening tables.
- `docs/paper/manufacturing-study-2026-09-15/`: frozen numerical study and
  generated manufacturing figures.
- `docs/paper/diagram-sources-2026-09-16/`: editable bilingual PowerPoint decks for
  Figures 2–4 and S1–S8, their rendered numeric panels, conceptual artwork, prompts,
  provenance and export manifest (Figure 1 remains in `diagram-sources-2026-09-13-h26/`).
- `docs/paper/figures-si-2026-09-16/`: published Supporting Information figures.
- `docs/paper/application-note-2026-09-09.md`: generated main manuscript.

## Reproduce the stored analysis

Use a separate local environment with Python 3.11 or later. Install the declared
project dependencies with `python -m pip install -e ".[dev]"`. Figure generation
also requires Matplotlib and Pillow (`python -m pip install matplotlib pillow`).
These are existing figure-script dependencies, not external data services.
No API key or paid source is required for these stored-input checks.

From the source root, first verify the data-derived outputs:

```text
python scripts/reproduce_manufacturing_study.py --check
python scripts/build_manufacturing_literature_review.py --check
python -m scripts.build_note_si --check
python -m pytest backend/tests/test_manufacturing_study.py backend/tests/test_manufacturing_literature.py backend/tests/test_paper_mass_units.py -q
```

Then run the manuscript checks in this order (the first two commands re-render the
numeric panels and refuse a deck or export that no longer matches them):

```text
python scripts/draw_application_note_figures.py
python scripts/draw_application_note_figures.py --lang ko
python scripts/build_application_note.py --check
python -m pytest backend/tests/test_application_note.py -q
python -m ruff check scripts/
```

The main article has four figures, no tables and 14 references. Its conservative
count is 4,566 word equivalents, including a 300-word TOC allowance. The build
script enforces the 5,000-word limit. Edit generators before rebuilding; do not
edit the generated article or numerical plots. Native PowerPoint exports are
already included; Windows PowerPoint is needed only to revise and re-export
the editable conceptual labels.

For the application source, install the locked JavaScript dependencies with
`npm ci` and `npm --prefix frontend ci`, then run
`npm --prefix frontend run build`, `npm --prefix frontend run lint` and
`npm --prefix frontend run check:i18n`. `python -m pytest backend/tests -q`
runs the complete backend suite; the calculation-harness matrix can take several
minutes. The supplied Windows directory build contains its own backend runtime.

## Calculation boundaries

Manufacturing inputs retain their units and evidence. Electricity uses measured
kWh or specified average power and time. Equipment occupancy, attended labor and
gas are separate contributions. Transfers allocate upstream expenditure by an
explicit mass or homogeneous-solution volume fraction, or charge the whole batch.
Unknown required inputs prevent a complete batch calculation. Temperature alone
does not predict power, yield, activity or catalyst lifetime. The published
manufacturing study reports manufacturing cost before overheads separately from
selling price after G&A, SARD and margin.

Original screening studies retain their own frozen formulations and assumptions;
they are not silently recalculated from the newly curated preparations. Powder
costs in manuscript tables and figures use USD/kg. Original machine-readable
records can retain explicitly identified legacy units and electrode area bases.

Software is licensed under PolyForm Noncommercial 1.0.0. Third-party source terms
remain applicable. Primary article files, third-party SI, private author files,
credentials and the CatCost source workbook are excluded from the reproduction
archive. A local package is not evidence of public deposition or redistribution
clearance, and no new release DOI is asserted.

## Supporting Information and nomenclature

The scientific SI contains methods, numbered equations and tables, numerical
verification, uncertainty assumptions and references. Installation commands and
file checksums belong to this reproduction guide and its package manifest.
The manufacturing random stream consumes five price/order multiplier columns
before the manufacturing draws; the checked reproduction script preserves this
order with seed 20260915 and 1,000 trials.

Generate the SI with `python -m scripts.build_note_si`; use `--check` to verify it.
Publication labels expand reaction abbreviations (for example, RWGS, reverse
water–gas shift) and identify candidate composition or structure. The original
JSON family and candidate identifiers remain unchanged for reproducibility.
The labels identify screening models, not source-verified formulations.

A local source archive includes development records and is not the proposed
SI for Publication. Select the scientific input/output records separately;
author confirmation of software access and final data distribution remains
outstanding. No local file or archive has been uploaded by this workflow.
