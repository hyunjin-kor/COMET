<p align="center">
  <img src="./docs/assets/readme-hero.png" alt="CatPrice estimate board screenshot" width="100%" />
</p>

<p align="center">
  <img src="./frontend/public/app-icon.svg" width="110" alt="CatPrice app icon" />
</p>

<h1 align="center">CatPrice</h1>

<p align="center">
  <strong>Desktop-first catalyst cost intelligence with a dedicated result board.</strong><br />
  CatCost-based economics, live metal feeds, explicit price-source states, and packaged Windows delivery.
</p>

<p align="center">
  <code>Windows desktop</code>
  <code>Electron shell</code>
  <code>Local FastAPI sidecar</code>
  <code>React renderer</code>
  <code>SQLite</code>
</p>

CatPrice is built to feel like shipped desktop software rather than a spreadsheet wrapper. It keeps the CatCost methodology, separates editing from result reading, makes price-source states explicit, and packages the full workflow into a local Windows app without relying on public server deployment.

## Workflow Framework

| Stage | Screen | What you do | What CatPrice gives back |
| --- | --- | --- | --- |
| 1. Build the recipe | `Calculator` | Set active metals, promoters, support, order size, and process steps | A draftable synthesis basis with live, indexed, or manual pricing |
| 2. Run the estimate | `Calculator` | Click `Calculate and open result board` | A dedicated result board instead of a cramped inline output panel |
| 3. Review the estimate | `Estimate Board` | Read selling price, cost structure, material ledger, and process basis | A clean review surface optimized for interpretation, not editing |
| 4. Iterate quickly | `Back to inputs` | Return to the calculator and change composition or process steps | The previous draft remains in place so reruns are fast |

## Screen Roles

- `Calculator` is the editing surface for composition, support basis, feed selection, and Step Method setup.
- `Estimate Board` is the reading surface for selling price, contribution structure, and component-level ledger review.
- The intended loop is simple: edit on `Calculator`, review on `Estimate Board`, then go back and rerun.

## Product Highlights

| Area | What CatPrice emphasizes |
| --- | --- |
| Result workflow | Separate calculator and estimate-board surfaces for better readability |
| Desktop release | Installer + unpacked app outputs for a clean Windows release path |
| Cost workflow | Step Method, indexed escalation, comparison, and uncertainty analysis |
| Price clarity | `LIVE`, `INDEXED`, and `MANUAL` states shown directly in the app |
| Local architecture | Electron shell, local FastAPI sidecar, React renderer, SQLite persistence |

## What It Does

- Estimates catalyst selling cost with the CatCost Step Method
- Tracks metal inputs with `LIVE`, `INDEXED`, and `MANUAL` price states
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

## Local Desktop Development

```bash
npm install
npm run dev
```

This starts:

- the FastAPI sidecar on `127.0.0.1:8765`
- the Vite renderer on `http://localhost:5173`
- the Electron desktop shell

The browser URL is only a local renderer development service for the Electron shell. CatPrice is not intended for public server deployment.

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

## License

All rights reserved.
