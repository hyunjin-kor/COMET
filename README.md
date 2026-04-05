<p align="center">
  <img src="./docs/assets/readme-hero.png" alt="CatPrice desktop app screenshot" width="100%" />
</p>

<p align="center">
  <img src="./frontend/public/app-icon.svg" width="110" alt="CatPrice app icon" />
</p>

<h1 align="center">CatPrice</h1>

<p align="center">
  <strong>Desktop-first catalyst manufacturing cost estimator with live metal feeds, transparent price evidence, and packaged Windows delivery.</strong><br />
  CatCost-based economics, market-aware feed inputs, route-aware manufacturing steps, and a dedicated result board for readable desktop review.
</p>

<p align="center">
  <code>Windows app</code>
  <code>CatCost workflow</code>
  <code>Market evidence</code>
  <code>Result board</code>
  <code>Installer download</code>
</p>

CatPrice is built to feel like shipped desktop software rather than a spreadsheet wrapper. The core workflow is reaction-agnostic: define a catalyst recipe, map the manufacturing route, sync current metal prices, and read a clean selling-cost estimate on a separate result board. Optional benchmark families can be loaded as reference starting points, but they do not define the product scope.

## Workflow Framework

| Stage | Screen | What you do | What CatPrice gives back |
| --- | --- | --- | --- |
| 1. Track the market | `Metal Feed` | Review live, indexed, and manual price bases with confidence and freshness metadata | A transparent sourcing basis for the catalyst recipe |
| 2. Build the recipe | `Build` | Enter active metals, promoters, support, pricing overrides, order size, and process steps | A catalyst manufacturing estimate grounded in current feed data |
| 3. Sanity-check with references | `Reference Routes` | Review optional literature-backed route families and load one as a starting point if useful | A fast reference path without locking the app to one reaction family |
| 4. Review the output | `Estimate Board` | Open the final output on a dedicated reading surface | A clean result board optimized for interpretation instead of editing |
| 5. Iterate quickly | `Back to build` | Return to the build workspace, adjust pricing or steps, and rerun | The draft stays in place so scenario work remains fast |

## Screen Roles

- `Metal Feed` shows where each quote came from, how fresh it is, and how much confidence to place in it.
- `Build` is the main editing surface for composition, support basis, feed selection, and Step Method setup.
- `Reference Routes` is an optional reference library for literature-backed catalyst families and route scoring.
- `Estimate Board` is the reading surface for selling price, contribution structure, and component-level ledger review.

## Product Highlights

| Area | What CatPrice emphasizes |
| --- | --- |
| Core estimator | Reaction-agnostic catalyst manufacturing cost estimation |
| Price clarity | `LIVE`, `INDEXED`, and `MANUAL` states plus evidence confidence and freshness |
| Workflow | Separate build and estimate-board surfaces for better readability |
| Route logic | Step Method, route extras, indexed escalation, and optional reference routes |
| Research support | Literature-backed thermocatalyst and electrocatalyst benchmark families with explicit source banks |
| Desktop release | Installer + unpacked app outputs for a clean Windows release path |

## Included Reference Families

CatPrice currently ships three optional benchmark reference families:

- `Ammonia decomposition reference family`
  Thermocatalyst routes including `Ni/gamma-Al2O3 baseline`, `Ni-MgO/CeO2 interface`, and `Ru/MgO premium`.
- `Fuel-cell ORR cathode reference family`
  Electrocatalyst routes including `Pt/C baseline cathode`, `Pt-Co intermetallic cathode`, and `Fe-N-C PGM-free cathode`.
- `PEM electrolyzer OER reference family`
  Electrocatalyst routes including `IrO2 PEM anode baseline`, `Low-Ir interface-engineered PEM route`, and `Ru-rich acidic OER route`.

All families expose candidate-level evidence anchors plus a larger family literature bank in the Compare screen. The benchmark library distinguishes `Thermocatalyst` and `Electrocatalyst` routes explicitly, electrocatalyst presets now push stack defaults into the calculator, and full-stack electrocatalyst families can rank on area-based electrode cost instead of powder-only cost.

## Download

Download the packaged Windows app from [GitHub Releases](https://github.com/hyunjin-kor/CatPrice/releases).

Recommended asset:

- `CatPrice Setup 1.1.1.exe`

Portable asset:

- `CatPrice-win-unpacked.zip`

CatPrice is distributed as a desktop app. The public repository does not require a public server deployment to use the product.

## What It Does

- Estimates catalyst selling cost with the CatCost Step Method
- Tracks metal inputs with `LIVE`, `INDEXED`, and `MANUAL` price states
- Annotates market feeds with price-evidence confidence, freshness, and acquisition mode
- Loads thermocatalyst and electrocatalyst reference families into the build workspace as editable starting points
- Attaches source-linked family literature banks built from high-confidence journal references and public vendor pages
- Opens the final estimate on a dedicated result board for review
- Runs Monte Carlo uncertainty analysis
- Applies ChemPPI and CEPCI escalation
- Includes material, step, and process template libraries
- Ships as a packaged Windows desktop app through Electron

## App Mark

The mark combines a catalyst chamber silhouette, internal particles, and an upward signal line. It is meant to read as catalyst manufacturing and market-aware pricing in a single desktop icon.

## Desktop Release

```bash
npm install
npm run build
```

Main outputs:

- `dist-electron\CatPrice Setup 1.1.1.exe`
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

## Academic Basis

> Baddour, F. G., et al. (2018). Journal of the American Chemical Society.
>
> Van Allsburg, K. M., et al. (2022). Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. Nature Catalysis.

Current benchmark-library anchors now include top-journal thermocatalyst and electrocatalyst references such as:

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
