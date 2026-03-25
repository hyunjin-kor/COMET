# CatPrice

Real-time metal price based catalyst manufacturing cost estimation tool.

## Overview

CatPrice estimates catalyst manufacturing costs using the Step Method and CapEx/OpEx Factors methodology from CatCost (Baddour et al. 2018, Van Allsburg et al. 2022), enhanced with real-time metal spot price integration.

**This tool complements CatCost by adding real-time pricing and a modern web interface. It does not replace CatCost.**

## Features

- Step Method catalyst cost calculator
- Real-time metal prices (Metals.Dev, MetalpriceAPI)
- Multi-composition comparison (up to 4)
- Monte Carlo uncertainty analysis
- ChemPPI/CEPCI price escalation
- Spent catalyst recovery value estimation
- Process template library
- CatCost JSON import compatibility

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.11+, SQLModel, SQLite |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Charts | Recharts |
| Scheduler | APScheduler |
| Desktop | Electron |

## Quick Start

```bash
# Backend
pip install -e .
cp .env.example .env
uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Desktop App

```bash
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

## API Keys (Optional)

Works without API keys using reference prices. For live data, add to `.env`:

```
METALS_DEV_API_KEY=your_key
METALPRICE_API_KEY=your_key
BLS_API_KEY=your_key
```

## Testing

```bash
pytest backend/tests/ -v
cd frontend && npm run lint && npm run build
python scripts/validate_catcost_data.py
```

## Academic Citation

> Baddour, F.G., et al. (2018). *J. Am. Chem. Soc.*
> Van Allsburg, K.M., et al. (2022). "Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost." *Nature Catalysis*.

## License

MIT
