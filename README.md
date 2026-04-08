<p align="center">
  <img src="./docs/assets/readme-hero.png" alt="CatPrice desktop app screenshot" width="100%" />
</p>

<p align="center">
  <img src="./frontend/public/app-icon.svg" width="110" alt="CatPrice app icon" />
</p>

<h1 align="center">CatPrice</h1>

<p align="center">
  <strong>Windows desktop application for catalyst cost estimation and raw-material price tracking.</strong>
</p>

<p align="center">
  <code>Windows app</code>
  <code>Local desktop workflow</code>
  <code>Source-linked library</code>
  <code>Benchmark datasets</code>
  <code>Installer download</code>
</p>

CatPrice is a desktop tool I built to bring catalyst cost screening, raw-material price tracking, and literature-linked benchmark review into one local workflow. This repository contains the Electron application, the local FastAPI backend, the calculation engine, and the curated data files used by the app.

The workflow is reaction-agnostic: choose catalyst type, define composition, set the preparation method, sync current metal prices, and review a cost estimate. Literature benchmark families are included as optional reference datasets, not as required inputs.

## Current Scope

The current repository exposes the following research-facing pieces:

- `thermocatalyst and electrocatalyst workflows`
  Bulk supported catalysts and electrode-stack cases are handled separately.
- `source-linked pricing`
  Live feeds, indexed rows, vendor rows, and literature rows carry quote basis, year, scope, and public links when those links exist.
- `preparation-route costing`
  The Step Method remains the main processing-cost layer.
- `recovery-aware thermal screening`
  Thermocatalyst runs can include an optional spent-catalyst recovery proxy.

## Implemented Now vs Planned Next

| Area | Implemented in CatPrice | Still planned, not claimed as done |
| --- | --- | --- |
| Research workflow | Thermocatalyst/electrocatalyst split, preparation templates, result-side evidence review | Structure-editor-first entry surface |
| Chemistry basis | Explicit composition rows, support closure, electrocatalyst area model | RDKit/ChemPy validation microservice |
| Lifecycle economics | Optional spent catalyst recovery proxy | Deactivation kinetics and regeneration-cycle economics |
| Complexity penalty | Route steps, campaign scale, evidence scope | SCScore-style synthesis complexity penalty |
| Validation | Backend pytest suite, desktop smoke test, data validation script | Chemistry-specific assertion harness and richer route-by-route verification |

In practice, CatPrice helps answer questions like:

- How does a change in metal price affect the estimated catalyst cost?
- Which composition or loading makes the route more expensive?
- How much does the preparation method change the final estimate?
- What is the evidence source behind each price used in the estimate?

## Workflow

| Stage | Screen | What you do | What CatPrice gives back |
| --- | --- | --- | --- |
| 1. Track the market | `Live Metal Prices` | Review live, indexed, and manual price bases with confidence and freshness metadata | A transparent sourcing basis for the catalyst recipe |
| 2. Estimate the cost | `Cost Estimate` | Move through `Catalyst Type -> Composition -> Preparation Method -> Result` and run the estimate | A catalyst preparation estimate grounded in current price data |
| 3. Check published benchmarks | `Literature Benchmarks` | Review optional literature-backed catalyst families and load one as a starting point if useful | A fast reference path without forcing the main workflow |
| 4. Review the output | `Result` | Open the final output on a separate reading surface | A result view optimized for interpretation instead of editing |
| 5. Iterate quickly | `Back to cost estimate` | Return to the cost estimate workspace, adjust pricing or steps, and rerun | The draft stays in place so scenario work remains fast |

## Screen Roles

- `Live Metal Prices` shows where each quote came from, how fresh it is, and how much confidence to place in it.
- `Cost Estimate` is the main editing surface for composition, support basis, feed selection, and preparation-step setup.
- `Literature Benchmarks` is an optional reference library for literature-backed catalyst families and route scoring.
- `Result` is the reading surface for selling price, contribution structure, and component-level source review.

## Repository Highlights

| Area | What CatPrice emphasizes |
| --- | --- |
| Core estimator | Reaction-agnostic catalyst preparation cost estimation with a separate result view |
| Price clarity | `LIVE`, `INDEXED`, and `MANUAL` states plus evidence confidence, freshness, quote year, and pack basis |
| Workflow | Step-based workspace navigation with back/forward movement instead of long scroll stacks |
| Preparation logic | Step Method, preparation extras, indexed escalation, and named preparation templates |
| Research support | Literature-backed thermocatalyst and electrocatalyst benchmark families with explicit anchor links and family banks |
| Operational trust | Quote-status panels, source-library trust labels, and result-side source records |
| Desktop release | Installer + unpacked app outputs for a clean Windows release path |

## Included Reference Families

CatPrice currently ships ten optional benchmark families.

Thermal families:

- `ammonia-cracking`
- `co2-methanol`
- `co2-methanation`
- `rwgs`
- `dry-reforming`
- `water-gas-shift`
- `formic-acid-dehydrogenation`

Electrocatalyst families:

- `fuel-cell-orr`
- `pem-electrolyzer-oer`
- `aem-electrolyzer-oer`

Each family includes candidate definitions, route templates, literature anchors, and pricing proxies that the app can load and score directly.

## Download

Download the packaged Windows app from [GitHub Releases](https://github.com/hyunjin-kor/CatPrice/releases).

Recommended asset:

- `CatPrice Setup 1.1.7.exe`

Portable asset:

- `CatPrice-win-unpacked.zip`

CatPrice is distributed as a desktop app. The public repository does not require a public server deployment to use the product.

## What It Does

- Estimates catalyst selling cost with a step-based preparation cost model referenced to published catalyst-cost literature
- Tracks metal inputs with `LIVE`, `INDEXED`, and `MANUAL` price states
- Annotates market feeds with price-evidence confidence, freshness, and acquisition mode
- Loads thermocatalyst and electrocatalyst reference families into the cost estimate workspace as editable starting points
- Attaches source-linked family literature banks built from high-confidence journal references and public vendor pages
- Opens the final estimate on a dedicated result screen for review
- Re-states the estimate basis through source records, normalization details, and route metadata on the result screen
- Adds an optional spent-catalyst recovery proxy to thermocatalyst screening runs
- Runs Monte Carlo uncertainty analysis
- Applies ChemPPI and CEPCI escalation
- Includes material, step, and process template libraries
- Ships as a packaged Windows desktop app through Electron

## Validation and Harness Engineering

The current repository validates the engine through:

- `pytest` coverage for the calculation engine and API
- `desktop smoke` checks for launch, health, prices, and sample calculation behavior
- `data validation` scripts for library consistency

Additional chemistry-specific checks and richer route-validation rules are still planned, but they are not presented as complete.

## App Mark

The mark combines a catalyst chamber silhouette, internal particles, and an upward signal line. It is meant to read as catalyst preparation and market-aware pricing in a single desktop icon.

## Desktop Release

```bash
npm install
npm run build
```

Main outputs:

- `dist-electron\CatPrice Setup 1.1.7.exe`
- `dist-electron\win-unpacked\CatPrice.exe`

Before rebuilding desktop artifacts, CatPrice stops old desktop processes automatically. You can also stop them manually:

```bash
npm run desktop:stop
```

## Desktop Smoke Test

```bash
npm run smoke:desktop
```

This checks desktop launch, backend readiness, the prices endpoint, a sample calculate request, and re-launch behavior.

## Optional API Keys

CatPrice works without API keys by falling back to indexed or manual prices.

```env
METALS_DEV_API_KEY=your_key
METALPRICE_API_KEY=your_key
BLS_API_KEY=your_key
```

## Validation

```bash
python -m pytest backend/tests -q
cd frontend && npm run build
python scripts/validate_catcost_data.py
```

Desktop packaging validation:

```bash
npm run build
npm run smoke:desktop
```

## References

CatPrice is my implementation of a local catalyst-cost desktop workflow. The repository cites CatCost methodology papers and benchmark literature, but it does not redistribute CatCost source data or reuse third-party product assets as part of this repository.

Method references:

- Baddour, F. G., et al. (2018). Journal of the American Chemical Society.
- Van Allsburg, K. M., et al. (2022). Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. Nature Catalysis.

Selected benchmark references:

- [Nature Communications 2023 on Ru ensembles for ammonia decomposition](https://doi.org/10.1038/s41467-023-36339-w)
- [Nature Communications 2025 on Ni-CeO2-x photothermal ammonia decomposition](https://doi.org/10.1038/s41467-025-66325-3)
- [Nature 2012 on electrocatalyst approaches and challenges for automotive fuel cells](https://doi.org/10.1038/nature11115)
- [Nature Catalysis 2019 on Fe-N-C cathodes for PEM fuel cells](https://www.nature.com/articles/s41929-019-0237-3)
- [Nature Energy 2022 on durable Fe-N-C PEMFC cathodes](https://www.nature.com/articles/s41560-022-01062-1)
- [Nature Communications 2025 on durable Pt/Co cathode design](https://www.nature.com/articles/s41467-025-65122-2)
- [Nature Communications 2023 on low-iridium TaOx/IrO2 PEM electrolyzer anodes](https://www.nature.com/articles/s41467-023-40912-8)
- [Nature Communications 2023 on ionomer-free porous-transport electrodes for PEM water electrolysis](https://www.nature.com/articles/s41467-023-40375-x)
- [Nature Catalysis 2026 on Co-RuO2-enabled PEM electrolysis](https://www.nature.com/articles/s41929-025-01456-w)

## License

Source-available, all rights reserved. See `LICENSE`.
