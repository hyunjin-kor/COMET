# CatPrice

CatPrice is a catalyst manufacturing cost estimator built around the CatCost methodology, updated with live metal feeds, indexed reference prices, and a desktop-friendly workflow.

It is designed for quick early-stage costing of catalyst compositions and process routes without forcing users into a spreadsheet-heavy workflow.

## What It Does

- Estimates catalyst selling cost with the CatCost Step Method
- Tracks metal inputs with `LIVE`, `INDEXED`, and `MANUAL` price states
- Compares multiple catalyst compositions side by side
- Runs Monte Carlo uncertainty analysis
- Applies ChemPPI and CEPCI escalation
- Includes material, step, and process template libraries
- Supports desktop usage through Electron

## Price Sources

CatPrice now makes the price source explicit in the UI:

- `LIVE`: current tracked market feed
- `INDEXED`: CatCost reference price adjusted with ChemPPI trend logic
- `MANUAL`: user-entered price

This avoids mixing real-time data and reference values without telling the user which is which.

## Why This Project

CatPrice is not a replacement for CatCost. It is a more approachable interface around the same methodology, with better visibility into source data, faster iteration, and a modern desktop/web experience.

Methodology basis:

- Baddour et al. 2018
- Van Allsburg et al. 2022

## Stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI, Python, SQLModel, SQLite |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Desktop | Electron |
| Charts | Recharts |
| Scheduling | APScheduler |

## Getting Started

### Desktop-first use

For normal use, install or run the desktop app from this repository and work through the Electron wrapper.

### Desktop packaging

```bash
npm install
npm run pack
```

The packaged desktop executable is created at:

```text
dist-electron\win-unpacked\CatPrice.exe
```

Before rebuilding desktop artifacts, CatPrice now stops old desktop processes automatically. You can also stop them manually:

```bash
npm run desktop:stop
```

### Desktop smoke test

After packaging, run:

```bash
npm run smoke:desktop
```

This checks desktop launch, backend readiness, the prices endpoint, a sample calculate request, and re-launch behavior.

### Local development

```bash
# backend
pip install -e .
cp .env.example .env
uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload

# frontend
cd frontend
npm install
npm run dev
```

The local development UI runs at `http://localhost:5173`.
This is a loopback-only development address on your own machine, not a public deployment URL.

### Full app development

```bash
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

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
cd frontend && npm run lint
cd frontend && npm run build
python scripts/validate_catcost_data.py
```

Desktop packaging validation:

```bash
npm run pack
npm run smoke:desktop
```

## Troubleshooting

- Desktop launcher log: `C:\Users\<your-user>\AppData\Roaming\CatPrice\catprice-launcher.log`
- If packaging fails with `Access is denied`, run `npm run desktop:stop` and retry.
- If the splash screen appears to stall, check `http://127.0.0.1:8765/api/health` and the launcher log first.

## Project Scope

CatPrice focuses on:

- catalyst composition costing
- early-stage process cost estimation
- price-source transparency
- faster iteration than spreadsheet-based workflows

It does not try to be a full plant design simulator.

## Academic Basis

> Baddour, F. G., et al. (2018). Journal of the American Chemical Society.
>
> Van Allsburg, K. M., et al. (2022). Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. Nature Catalysis.

## License

All rights reserved.
