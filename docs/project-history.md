# COMET Project History

The GitHub benchmarking notes and the original Codex phase plan, split out of
[`AGENTS.md`](../AGENTS.md). Both are historical. They record how the project was
scoped at the start; `git log --oneline` is the ground truth for what shipped.

---

## GitHub benchmarking results and adopted ideas

### Directly related projects

| Project | Key idea | COMET adoption |
|---------|----------|-------------------|
| **NREL/catcost-data-tools** | Python tool for CatCost Excel↔JSON conversion | Reference Excel-parsing logic, keep the Materials Library JSON schema compatible. |
| **ChemEngDPpy** | Python equipment sizing + CapEx/OpEx | Reference power-law equipment-cost correlations, implement Garrett/Peters factors. |
| **BioSTEAM** | Biorefinery TEA + LCA + uncertainty + OOP | Borrow the **Monte Carlo uncertainty** module structure and the unit-based OOP pattern. |
| **pyH2A** | Hydrogen LCOH analysis with Markdown input → report | Reference the LCOH module structure and the **plugin architecture** idea. |
| **NREL/H2Integrate** | Hybrid energy-system modeling | Possible TEA/LCOH Phase-2 integration target. |

### Metal price-feed ecosystem

| API / tool | Notes | Recommendation |
|------------|-------|----------------|
| **Metals-API** (metals-api.com) | REST API, 168 currencies, LME/LBMA sources, 60-second refresh | ★★★★ (free tier available) |
| **MetalpriceAPI** | Includes PGMs, ships a Python SDK | ★★★★ |
| **Metals.Dev** | Industrial + precious metals, JSON API, ~60-second delay | ★★★★★ (most comprehensive) |
| **tiagocordeiro/lme** | LME Python package with historical data | ★★★ (auxiliary) |
| **Kitco scraping** | PGM (Ru, Ir, Rh) prices — no API | ★★★ (backup; check robots.txt) |

**Strategy**: Metals.Dev as the primary source, MetalpriceAPI as backup. For PGMs,
consider scraping Heraeus / Johnson Matthey.

### Full-stack architecture references

| Project | Architecture | Adoption |
|---------|--------------|----------|
| **tauri-fastapi-full-stack-template** | Tauri 2 + React + FastAPI + SQLite (sidecar) | Initial boilerplate reference. The current implementation uses Electron. |
| **stock-market-dashboard** | FastAPI + React + SQLite + Docker | Live-price dashboard WebSocket pattern. |
| **Dynamic-pricing-optimization-system** | FastAPI + React + ML | Reference for the Tornado-chart sensitivity UI. |

### Additional ideas from benchmarking

1. **Uncertainty analysis**: BioSTEAM-style Monte Carlo simulation to deliver a
   cost range, going beyond CatCost's Low/Base/High slots.
2. **Plugin architecture**: pyH2A-style separation of process-specific TEA modules
   (NH₃ cracking, H₂ production, etc.).
3. **catcost-data-tools compatibility**: Accept the CatCost JSON export format on
   import so existing users can migrate easily.
4. **ChemPPI / CEPCI auto-update**: Pull ChemPPI from the BLS API automatically
   (CatCost requires manual updates).
5. **Comparison Mode**: Interactive dashboard that compares several catalyst
   compositions side-by-side.

---

## Development phases (Codex work units)

> **Historical reference.** Phases 1–5 below were the original Codex work plan. The current repo state (v1.3.9, 2026-07) has implemented the bulk of every phase plus material that was never on the original list (LCA, decision engine, electrocatalyst layer model, curated USGS proxy library, source-evidence tagging, multi-family benchmark library). Use `git log --oneline` and the `Live additions` section of `architecture.md` for the current ground truth; treat the lists below as the seed plan, not an open backlog.

### Phase 1: Calculation engine core (MVP)
```
Task 1.1: Project bootstrap (pyproject.toml, directory layout, DB setup)
Task 1.2: Seed data JSON files (materials, steps, equipment, indices)
Task 1.3: materials_calc.py — stoichiometry + scaling (eq 4.1~4.4)
Task 1.4: step_method.py — full Step Method + 12 templates
Task 1.5: cost_engine.py — integrated calculation engine
Task 1.6: spent_catalyst.py — spent-catalyst recovery value
Task 1.7: price_escalation.py — ChemPPI / CEPCI escalation
Task 1.8: constants.py — gather every coefficient / constant
Task 1.9: tests — 3 CatCost validation cases (Pt/C, Ni/Al₂O₃, FCC) within ±20%
```

### Phase 2: API server + basic UI
```
Task 2.1: FastAPI app skeleton (main.py, config.py, database.py)
Task 2.2: DB models + Alembic migrations
Task 2.3: API routers (calculator, materials, prices)
Task 2.4: React frontend bootstrap (Vite + Tailwind)
Task 2.5: Calculator page (input form → result + pie chart)
Task 2.6: Library page (material search / select)
```

### Phase 3: Live price-feed integration
```
Task 3.1: price_fetcher.py — Metals.Dev / MetalpriceAPI integration
Task 3.2: price_scheduler.py — APScheduler daily auto-collect
Task 3.3: Prices dashboard (time series, volatility)
Task 3.4: Calculator results auto-reflect "today's basis"
Task 3.5: bls_updater.py — BLS API → ChemPPI auto-update
```

### Phase 4: Advanced features
```
Task 4.1: capex_opex.py — full CapEx & OpEx Factors method
Task 4.2: uncertainty.py — Monte Carlo uncertainty analysis
Task 4.3: Compare page (up to 4 compositions)
Task 4.4: Tornado-chart sensitivity analysis
Task 4.5: Cost-by-scale curve (ScaleCurve)
Task 4.6: Sankey-diagram cost-flow visualization
Task 4.7: CatCost JSON import/export compatibility
```

### Phase 5: Deployment + desktop
```
Task 5.1: Docker Compose one-click deployment
Task 5.2: Electron desktop app (sidecar: FastAPI)
Task 5.3: GitHub Actions CI/CD
Task 5.4: Documentation site (MkDocs etc.)
Task 5.5: Zenodo DOI registration
Task 5.6: README + Contributing guide
```
