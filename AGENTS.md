# COMET — Codex Development Framework

> Master guide for AI-coding agents (Codex / Claude) working on this project.
> Built on the original project plan's scope, with adopted ideas from
> GitHub benchmarking and the original CatCost methodology.


Reference detail lives beside this file, so this guide stays short enough to read
in full before touching anything:

- [`docs/architecture.md`](docs/architecture.md) — directory layout, core calculation modules, API surface
- [`docs/project-history.md`](docs/project-history.md) — GitHub benchmarking notes and the original Codex phase plan

---

## Project identity

- **Name**: COMET: Catalyst Overall Manufacturing Estimation Tool
- **One-liner**: A desktop tool that estimates catalyst manufacturing cost from real-time metal market prices.
- **License**: PolyForm Noncommercial License 1.0.0 (noncommercial use permitted; commercial use requires a separate license).
- **Differentiator**: CatCost-derived methodology, but with automatic live market-price refresh and a modern web/desktop UI.
- **Academic citations**: Baddour et al. 2018, Van Allsburg et al. 2022.

### Current implementation status

- **Remote repository**: `https://github.com/hyunjin-kor/COMET`
- **Latest verified release**: `v1.3.24` (verified 2026-09-02; re-verify with `gh release list -L 1` before quoting)
- **Current desktop shell**: Electron (`electron/`, `dist-electron/`)
- **Frontend stack**: React 19 + TypeScript + Vite
- **Backend stack**: FastAPI + SQLModel + SQLite
- **Claude hand-off entry point**: root `CLAUDE.md`
- **Note**: The original plan in `docs/project-history.md` mentions Tauri, but the
  actual implementation and packaging target is Electron.

---

## Tech stack (locked in)

```
Frontend:  React 19 + TypeScript + Vite
UI:        Tailwind CSS 4
Charts:    Recharts
Desktop:   Electron 41 (sidecar: FastAPI bundled with PyInstaller)
Backend:   FastAPI (Python 3.11+), async
ORM:       SQLModel (SQLAlchemy + Pydantic integration)
DB:        SQLite (desktop / dev) — single-file, ships embedded with the app
Scheduler: APScheduler (auto price collection)
HTTP:      httpx (async)
Testing:   pytest (backend), tsc + vite build (frontend type/build), PowerShell desktop smoke
CI/CD:     GitHub Actions (CI on push/PR, release.yml on tag)
Docs:      Markdown docs in `docs/` (MkDocs Material is a candidate for a future hosted site)
```

**Status notes**:
- The project moved from the initial Tauri boilerplate plan to Electron-based desktop packaging.
- The original plan referenced Plotly.js, Alembic, Playwright, pytest-asyncio, Docker Compose, and a PostgreSQL deploy target. None of those are wired up in the current repo. Treat the plan's mention of them as "considered, not adopted" — only the items above are in `package.json` / `pyproject.toml`.

---

## Validation strategy

### CatCost validation cases (per User Guide Table 6.2)

The Step Method is reproduced line by line from the *published* Table 6.2 inputs (mid-2017 basis): per-case materials totals, the exact step lists with multiplicities, and order sizes. No input is tuned to hit the target. `scripts/reproduce_catcost_table62.py` prints every intermediate the table prints, side by side.

| Catalyst | Conditions | Materials (published) | CatCost | COMET | Residual | Market |
|----------|------------|----------------------:|--------:|------:|---------:|-------:|
| 2 wt% Pt/C | 2 ton, Small | $10.70/lb | $27.37/lb | $27.37/lb | 0.00% | $34.09/lb |
| 21 wt% Ni/Al₂O₃ | 20 ton, Medium | $11.88/lb | $20.59/lb | $19.22/lb | −6.65% | $21.33/lb |
| USY-based FCC | 200 ton, Large, 67 t/d | $0.352/lb | $2.41/lb | $2.44/lb | +1.16% | $2.73/lb |

Hourly step cost, campaign length, processing cost, subtotal, G&A and SARD match the table to the cent on all three cases. The two residuals are documented departures inside the table itself, not engine error:

- **Ni/Al₂O₃ margin** — footnote f applies 33% of pre-margin cost; the Figure 6.3 correlation the guide publishes (`39.192·Q^−0.2336` % of selling price) gives 24% at 20 ton. COMET follows the correlation.
- **FCC campaign length** — footnote b uses an effective 67 t/d for the zeolite campaign (ramp-up/down) instead of the 150 t/d nominal rate. `calculate_step_method(..., production_rate_ton_per_day=67)` reproduces the published 4-day campaign; at the nominal rate COMET runs 2.33 days and lands 33% low.

Run these three cases as a regression at the end of every Phase. Live tolerances are in `backend/tests/test_cost_engine.py::TestStepMethodVerification`.

---

## Coding conventions

- Python: ruff (formatter + linter, configured in `pyproject.toml`), type hints encouraged on public APIs
- TypeScript: strict mode in `frontend/tsconfig.app.json`, ESLint via `frontend/eslint.config.js`
- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `style:`)
- PRs: feature-scoped, must include tests for non-trivial logic
- Environment variables: provide `.env.example`; never commit secrets

---

## Important notes

### License caveats
- CatCost is owned by DOE / NREL with non-commercial internal-use restrictions.
- **Citing the methodology is fine** (academic reference).
- **Direct copying of CatCost data is risky** → re-collect from public sources.
- Materials Library prices are independently sourced from ICIS public, Sigma-Aldrich,
  USGS, etc.

### Metal price-feed API keys
- Metals.Dev: free tier 50 requests/month, paid $9.99/month (10 k requests).
- MetalpriceAPI: free tier 50 requests/month.
- BLS API: free (registration required).

### Relationship to CatCost
- README states: "academically cites and uses the CatCost methodology".
- Emphasizes: "complements CatCost rather than replacing it".
