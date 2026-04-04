<p align="center">
  <img src="./docs/assets/readme-hero.png" alt="CatPrice estimate board screenshot" width="100%" />
</p>

<p align="center">
  <img src="./frontend/public/app-icon.svg" width="110" alt="CatPrice app icon" />
</p>

<h1 align="center">CatPrice</h1>

<p align="center">
  <strong>Desktop-first catalyst cost intelligence for ammonia-cracking benchmark decisions.</strong><br />
  CatCost-based economics, live metal feeds, explicit price evidence, route-aware scoring, and packaged Windows delivery.
</p>

<p align="center">
  <code>Windows app</code>
  <code>Benchmark ranking</code>
  <code>Market evidence</code>
  <code>Result board</code>
  <code>Installer download</code>
</p>

CatPrice is built to feel like shipped desktop software rather than a spreadsheet wrapper. It keeps the CatCost methodology, separates editing from result reading, makes price-source states explicit, and packages the workflow into a local Windows app without relying on public server deployment.

The current benchmark harness is centered on **ammonia cracking (ammonia decomposition)**. CatPrice now ranks benchmark catalyst routes against the current metal-price basis while preserving source confidence, route confidence, and transparent catalog anchors alongside the cost model.

## Workflow Framework

| Stage | Screen | What you do | What CatPrice gives back |
| --- | --- | --- | --- |
| 1. Track the market | `Market Board` | Review live and indexed metals with confidence and freshness metadata | A transparent price-evidence basis for each tracked metal |
| 2. Load a route | `Calculator` | Start from an ammonia-cracking benchmark preset or build a recipe manually | A synthesis draft with composition, process steps, and sourcing state |
| 3. Rank candidates | `Decision Board` | Compare benchmark routes with balanced, cost-first, or evidence-first weighting | A current winner with route, evidence, and performance context |
| 4. Review the estimate | `Estimate Board` | Open the calculator output on a dedicated review surface | A clean result board optimized for interpretation, not editing |
| 5. Iterate quickly | `Back to inputs` | Return to the calculator and adjust route, materials, or price basis | The previous draft remains in place so reruns stay fast |

## Screen Roles

- `Market Board` shows where each metal quote came from, how fresh it is, and how much confidence to place in it.
- `Calculator` is the editing surface for composition, support basis, feed selection, benchmark preset loading, and Step Method setup.
- `Decision Board` is the benchmark-ranking surface for ammonia-cracking catalyst choices.
- `Estimate Board` is the reading surface for selling price, contribution structure, and component-level ledger review.

## Benchmark Harness

CatPrice now implements a five-part benchmark framework for **ammonia cracking**:

1. `Price Evidence Layer`
   Live market feeds, indexed references, and fixed engineering proxies each carry confidence and freshness metadata.
2. `Route Library Layer`
   Benchmark routes include preprocess, synthesis, postprocess, and quality-gate stages instead of a flat step list only.
3. `Cost Engine Layer`
   The Step Method output is combined with route-specific QA/activation overhead to create a landed catalyst cost basis.
4. `Decision Engine Layer`
   Candidates are ranked with configurable weights across economics, evidence quality, route confidence, and performance.
5. `Desktop UX Layer`
   The Market Board, Calculator, Decision Board, and Estimate Board now fit together as one desktop workflow.

The initial ammonia-cracking benchmark board ships with:

- `Ni/gamma-Al2O3 baseline` as the cost anchor
- `Ni-MgO/CeO2 interface` as the non-noble performance route
- `Ru/MgO premium` as the low-temperature premium route

Public catalog anchors are also attached for transparent procurement reference, including Sigma-Aldrich pages for nickel nitrate, ruthenium chloride, magnesium oxide, cerium oxide, and alumina.

## Product Highlights

| Area | What CatPrice emphasizes |
| --- | --- |
| Result workflow | Separate calculator and estimate-board surfaces for better readability |
| Benchmarking | Ammonia-cracking candidate ranking with decision profiles |
| Desktop release | Installer + unpacked app outputs for a clean Windows release path |
| Cost workflow | Step Method, indexed escalation, route overhead, comparison, and uncertainty analysis |
| Price clarity | `LIVE`, `INDEXED`, and `MANUAL` states plus evidence confidence and freshness |
| Local architecture | Electron shell, local FastAPI sidecar, React renderer, SQLite persistence |

## Download

Download the packaged Windows app from [GitHub Releases](https://github.com/hyunjin-kor/CatPrice/releases).

Recommended asset:

- `CatPrice Setup 1.0.1.exe`

Portable asset:

- `CatPrice-win-unpacked.zip`

CatPrice is distributed as a desktop app. The public repository does not require a public server deployment to use the product.

## What It Does

- Estimates catalyst selling cost with the CatCost Step Method
- Tracks metal inputs with `LIVE`, `INDEXED`, and `MANUAL` price states
- Annotates market feeds with price-evidence confidence, freshness, and acquisition mode
- Ranks ammonia-cracking benchmark catalysts on a Decision Board
- Loads benchmark routes directly into the calculator as starting points
- Opens the final estimate on a dedicated result board for review
- Compares multiple catalyst compositions side by side
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

- `dist-electron\CatPrice Setup 1.0.1.exe`
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

Benchmark references currently reflected in the decision harness:

- [Cleaner Energy Systems 2026 ammonia decomposition economic analysis](https://naos-be.zcu.cz/server/api/core/bitstreams/ee92fa23-ea1c-42b4-ad67-e0230bce7552/content)
- [Nature Communications 2023 on Ru ensembles for ammonia decomposition](https://www.nature.com/articles/s41467-023-36339-w)
- [PubMed 2025 on Ni_xMg_1-xO/CeO2 ammonia-decomposition catalyst design](https://pubmed.ncbi.nlm.nih.gov/41452228/)
- [Sigma-Aldrich nickel nitrate catalog page](https://www.sigmaaldrich.com/US/en/product/aldrich/203874)
- [Sigma-Aldrich ruthenium chloride catalog page](https://www.sigmaaldrich.com/US/en/product/aldrich/206229)

## License

All rights reserved.
