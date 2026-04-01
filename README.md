# CatPrice

CatPrice is a desktop-first catalyst manufacturing cost estimator built around the CatCost methodology, live metal feeds, indexed reference prices, and a packaged Electron workflow.

It is designed for early-stage costing of catalyst compositions and process routes without a spreadsheet-heavy workflow or any public server deployment.

## What It Does

- Estimates catalyst selling cost with the CatCost Step Method
- Tracks metal inputs with `LIVE`, `INDEXED`, and `MANUAL` price states
- Compares multiple catalyst compositions side by side
- Runs Monte Carlo uncertainty analysis
- Applies ChemPPI and CEPCI escalation
- Includes material, step, and process template libraries
- Ships as a Windows desktop app through Electron

## Why This Project

CatPrice is not a replacement for CatCost. It is a desktop-focused interface around the same methodology, with better visibility into source data and faster iteration.

Methodology basis:

- Baddour et al. 2018
- Van Allsburg et al. 2022

## Stack

| Layer | Technology |
| --- | --- |
| Desktop shell | Electron |
| Renderer UI | React 19, TypeScript, Vite, Tailwind CSS |
| Local sidecar API | FastAPI, Python, SQLModel, SQLite |
| Charts | Recharts |
| Scheduling | APScheduler |

## Desktop Packaging

```bash
npm install
npm run build
```

The Windows installer and unpacked app are created under:

```text
dist-electron\
```

Main outputs:

- `dist-electron\CatPrice Setup 1.0.1.exe`
- `dist-electron\win-unpacked\CatPrice.exe`

Before rebuilding desktop artifacts, CatPrice stops old desktop processes automatically. You can also stop them manually:

```bash
npm run desktop:stop
```

## Desktop Smoke Test

After packaging, run:

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

The browser URL is only a local renderer development service for the Electron shell. CatPrice is no longer intended for any public server deployment.

## Optional API Keys

CatPrice works without API keys by falling back to indexed or manual prices.

Add these to `.env` only if you want external data integrations:

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

## Troubleshooting

- Desktop launcher log: `C:\Users\<your-user>\AppData\Roaming\CatPrice\catprice-launcher.log`
- If packaging fails with `Access is denied`, run `npm run desktop:stop` and retry.
- If the splash screen appears to stall, check `http://127.0.0.1:8765/api/health` and the launcher log first.

## Academic Basis

> Baddour, F. G., et al. (2018). Journal of the American Chemical Society.
>
> Van Allsburg, K. M., et al. (2022). Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. Nature Catalysis.

## License

All rights reserved.
