# CatPrice — Codex Development Framework

> Master guide for AI-coding agents (Codex / Claude) working on this project.
> Built on top of `CatPrice_Project.md`'s scope, with adopted ideas from
> GitHub benchmarking and the original CatCost methodology.

---

## 0. Project identity

- **Name**: CatPrice (suggesting that the catalyst cost is "cracked" open and analyzed)
- **One-liner**: A desktop tool that estimates catalyst manufacturing cost from real-time metal market prices.
- **License**: All rights reserved.
- **Differentiator**: CatCost-derived methodology, but with automatic live market-price refresh and a modern web/desktop UI.
- **Academic citations**: Baddour et al. 2018, Van Allsburg et al. 2022.

### 0.1 Current implementation status (as of 2026-04-26)

- **Remote repository**: `https://github.com/hyunjin-kor/CatPrice`
- **Latest verified release**: `v1.1.13`
- **Current desktop shell**: Electron (`electron/`, `dist-electron/`)
- **Frontend stack**: React 19 + TypeScript + Vite
- **Backend stack**: FastAPI + SQLModel + SQLite
- **Claude hand-off entry point**: root `CLAUDE.md`
- **Note**: The original plan below mentions Tauri, but the actual implementation
  and packaging target is Electron.

---

## 1. GitHub benchmarking results and adopted ideas

### 1.1 Directly related projects

| Project | Key idea | CatPrice adoption |
|---------|----------|-------------------|
| **NREL/catcost-data-tools** | Python tool for CatCost Excel↔JSON conversion | Reference Excel-parsing logic, keep the Materials Library JSON schema compatible. |
| **ChemEngDPpy** | Python equipment sizing + CapEx/OpEx | Reference power-law equipment-cost correlations, implement Garrett/Peters factors. |
| **BioSTEAM** | Biorefinery TEA + LCA + uncertainty + OOP | Borrow the **Monte Carlo uncertainty** module structure and the unit-based OOP pattern. |
| **pyH2A** | Hydrogen LCOH analysis with Markdown input → report | Reference the LCOH module structure and the **plugin architecture** idea. |
| **NREL/H2Integrate** | Hybrid energy-system modeling | Possible TEA/LCOH Phase-2 integration target. |

### 1.2 Metal price-feed ecosystem

| API / tool | Notes | Recommendation |
|------------|-------|----------------|
| **Metals-API** (metals-api.com) | REST API, 168 currencies, LME/LBMA sources, 60-second refresh | ★★★★ (free tier available) |
| **MetalpriceAPI** | Includes PGMs, ships a Python SDK | ★★★★ |
| **Metals.Dev** | Industrial + precious metals, JSON API, ~60-second delay | ★★★★★ (most comprehensive) |
| **tiagocordeiro/lme** | LME Python package with historical data | ★★★ (auxiliary) |
| **Kitco scraping** | PGM (Ru, Ir, Rh) prices — no API | ★★★ (backup; check robots.txt) |

**Strategy**: Metals.Dev as the primary source, MetalpriceAPI as backup. For PGMs,
consider scraping Heraeus / Johnson Matthey.

### 1.3 Full-stack architecture references

| Project | Architecture | Adoption |
|---------|--------------|----------|
| **tauri-fastapi-full-stack-template** | Tauri 2 + React + FastAPI + SQLite (sidecar) | Initial boilerplate reference. The current implementation uses Electron. |
| **stock-market-dashboard** | FastAPI + React + SQLite + Docker | Live-price dashboard WebSocket pattern. |
| **Dynamic-pricing-optimization-system** | FastAPI + React + ML | Reference for the Tornado-chart sensitivity UI. |

### 1.4 Additional ideas from benchmarking

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

## 2. Tech stack (locked in)

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

## 3. Project directory structure

```
catprice/
├── AGENTS.md                          ← this file (Codex master guide)
├── README.md
├── LICENSE                            (All rights reserved)
├── pyproject.toml                     (Python deps, ruff, pytest config)
├── docker-compose.yml
├── .github/
│   └── workflows/
│       ├── ci.yml                     (lint + test + build)
│       └── release.yml                (tag → GitHub Release)
│
├── backend/
│   ├── __init__.py
│   ├── main.py                        # FastAPI entry point
│   ├── config.py                      # Pydantic Settings (env vars, API keys)
│   ├── database.py                    # SQLModel engine, session
│   │
│   ├── core/                          # === Core calculation engine ===
│   │   ├── __init__.py
│   │   ├── cost_engine.py             # CatCost Step Method + CapEx/OpEx integrated calculation
│   │   ├── materials_calc.py          # Stoichiometry (eq 4.1~4.4), scaling (k_SF)
│   │   ├── step_method.py             # 3a Step Method logic
│   │   ├── capex_opex.py              # 3b~3e CapEx/OpEx Factors logic
│   │   ├── spent_catalyst.py          # Spent-catalyst recovery / sale / disposal value
│   │   ├── price_fetcher.py           # Metal price collector (Metals.Dev, MetalpriceAPI)
│   │   ├── price_escalation.py        # ChemPPI / CEPCI year-over-year escalation
│   │   ├── uncertainty.py             # Monte Carlo uncertainty (BioSTEAM-inspired)
│   │   └── constants.py               # Manufacturing factors, thermo constants, scale factors
│   │
│   ├── models/                        # SQLModel DB models
│   │   ├── __init__.py
│   │   ├── metal_price.py             # Metal price history
│   │   ├── material.py                # Materials library item
│   │   ├── equipment.py               # Equipment library (cost correlation included)
│   │   └── estimate.py                # Saved cost estimate
│   │   # Note: process templates ship as JSON files in `data/process_templates/`,
│   │   # not as a SQL model.
│   │
│   ├── schemas/                       # Pydantic I/O schemas
│   │   ├── __init__.py
│   │   ├── cost_input.py              # POST /api/calculate request schema
│   │   ├── cost_result.py             # Cost-calculation result schema
│   │   ├── metal_price.py             # Metal-price schema
│   │   └── comparison.py              # Multi-composition comparison schema
│   │
│   ├── routers/                       # FastAPI routers
│   │   ├── __init__.py
│   │   ├── calculator.py              # POST /api/calculate (Step + CapEx/OpEx)
│   │   ├── prices.py                  # GET  /api/prices, /api/prices/{symbol}
│   │   ├── materials.py               # CRUD /api/materials
│   │   ├── equipment.py               # CRUD /api/equipment
│   │   ├── templates.py               # GET  /api/templates (process templates)
│   │   ├── compare.py                 # POST /api/compare
│   │   ├── uncertainty.py             # POST /api/uncertainty (Monte Carlo)
│   │   └── catcost_import.py          # POST /api/import/catcost (JSON compatibility)
│   │
│   ├── services/                      # Business-logic services
│   │   ├── __init__.py
│   │   ├── price_scheduler.py         # APScheduler: daily price auto-collection
│   │   └── bls_updater.py             # BLS API → ChemPPI auto-update
│   │
│   ├── data/                          # Seed data
│   │   ├── materials_library.json     # CatCost Materials Library compatible (independently sourced)
│   │   ├── equipment_library.json     # Equipment cost correlations (public-literature based)
│   │   ├── step_library.json          # Step Method hourly cost per step
│   │   ├── spent_catalyst.json        # Spent-catalyst processing parameters
│   │   ├── process_templates/         # Process templates
│   │   │   ├── wet_impregnation_metal_oxide.json
│   │   │   ├── metal_pgm_carbon.json
│   │   │   ├── zeolite_fcc.json
│   │   │   ├── metal_carbide_bulk.json
│   │   │   └── nanoparticles_flow.json
│   │   ├── chemppi.json               # Chemical Producer Price Index
│   │   ├── cepci.json                 # Chemical Engineering Plant Cost Index
│   │   └── unit_conversions.json      # Unit-conversion table
│   │
│   ├── migrations/                    # Alembic migrations
│   │   └── ...
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_cost_engine.py        # CatCost validation cases (Pt/C, Ni/Al₂O₃, FCC)
│       ├── test_materials_calc.py     # Stoichiometry + scaling validation
│       ├── test_step_method.py        # Step Method ±20% validation
│       ├── test_capex_opex.py         # CapEx/OpEx factor validation
│       ├── test_spent_catalyst.py     # Spent-catalyst recovery-value validation
│       ├── test_price_fetcher.py      # API mocking tests
│       ├── test_price_escalation.py   # ChemPPI / CEPCI escalation validation
│       └── test_api.py                # FastAPI endpoint integration tests
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   │
│   └── src/
│       ├── App.tsx
│       ├── main.tsx
│       ├── lib/
│       │   ├── api.ts                 # API client (TanStack Query)
│       │   └── utils.ts
│       │
│       ├── pages/
│       │   ├── Calculator.tsx         # Main: catalyst price calculator (Step + CapEx/OpEx selector)
│       │   ├── Prices.tsx             # Metal-price dashboard
│       │   ├── Compare.tsx            # Composition comparison (up to 4)
│       │   ├── Library.tsx            # Materials / equipment library management
│       │   ├── Templates.tsx          # Process-template browser
│       │   ├── Uncertainty.tsx        # Monte Carlo uncertainty analysis
│       │   └── TEA.tsx                # TEA / LCOH module (Phase 2)
│       │
│       └── components/
│           ├── layout/
│           │   ├── Sidebar.tsx
│           │   └── Header.tsx
│           ├── calculator/
│           │   ├── CompositionInput.tsx    # Catalyst composition form
│           │   ├── StepMethodConfig.tsx    # Step Method parameters
│           │   ├── CapExOpExConfig.tsx     # CapEx/OpEx parameters
│           │   ├── CostBreakdown.tsx       # Cost breakdown (pie / donut / Sankey)
│           │   └── ResultSummary.tsx       # Result summary card
│           ├── prices/
│           │   ├── PriceTimeline.tsx       # Metal price time series
│           │   ├── PriceCard.tsx           # Per-metal price card
│           │   └── VolatilityBadge.tsx     # Volatility indicator
│           ├── charts/
│           │   ├── TornadoChart.tsx        # Sensitivity analysis
│           │   ├── ScaleCurve.tsx          # Cost-by-scale curve
│           │   ├── SankeyDiagram.tsx       # Cost-flow Sankey
│           │   └── MonteCarloHist.tsx      # Uncertainty histogram
│           └── shared/
│               ├── MaterialSelector.tsx    # Material dropdown
│               ├── EquipmentSelector.tsx   # Equipment dropdown
│               └── ExportButton.tsx        # JSON / CSV / PDF export
│
├── electron/                          # Electron desktop shell + sidecar management
│   ├── main.js
│   └── preload.js
│
└── docs/                              # Project documentation
    ├── index.md
    ├── getting-started.md
    ├── methodology.md                 # CatCost Step Method + CapEx/OpEx description
    ├── api-reference.md
    ├── project-links.md               # Verified external links + Claude hand-off status
    └── contributing.md
```

### 3.1 Live additions since the initial scaffold

The tree above is the original Phase-1 scaffold. The repo has since grown the
following modules. Always run `git ls-files backend` for the authoritative
current layout — this list is a navigation aid, not a contract.

- `backend/core/`: `decision_engine.py` (benchmark scoring), `electrocatalyst.py` (electrode-area cost model), `lca.py` (GWP / CED), `material_pricing.py` (library-backed price resolution), `price_evidence.py` (confidence / freshness tagging)
- `backend/routers/`: `decision.py`, `estimates.py` (saved-estimate CRUD), `lca.py`, `indices.py`
- `backend/data/`: 10 reaction-family benchmark JSON files (`*_benchmark.json`), `electrocatalyst_library.json`, `lca_factors.json`, `materials_curated.json` (curated public-source proxies in addition to `materials_library.json`), 19 process templates (PEM/AEM/DMFC/USY/ZSM-5/etc.)
- `backend/launcher.py`, `backend/paths.py`: PyInstaller-friendly resource resolution for the packaged sidecar
- `backend/services/bls_updater.py`: ChemPPI auto-update from BLS API
- `electron/preload.js`: contextBridge for window controls and menu IPC
- `scripts/` highlights: `build_backend_bundle.ps1` (PyInstaller), `smoke_test_desktop.ps1`, `validate_catcost_data.py` (local-only, requires gitignored CatCost workbook), `capture_readme_screens.mjs`, `generate_app_icons.py`, `generate_social_preview.py`

---

## 4. Core calculation logic (faithful CatCost reimplementation)

### 4.1 Materials calculation (eq 4.1~4.4)

```python
# backend/core/materials_calc.py

def calculate_active_phase_mass(m_LR, MW_LR, mol_ratio, MW_AP, yield_pct):
    """eq 4.1: active-phase mass."""
    return (m_LR / MW_LR) * mol_ratio * MW_AP * (yield_pct / 100)

def calculate_catalyst_mass(m_AP, m_sup):
    """eq 4.2: total catalyst mass."""
    return m_AP + m_sup

def calculate_support_mass(m_AP, wt_pct):
    """eq 4.3: support mass (wt%-based)."""
    return (m_AP / (wt_pct / 100)) - m_AP

def calculate_scaling_factor(M_cat_plant, m_cat_lab):
    """eq 4.4: lab→plant scaling factor."""
    return M_cat_plant / m_cat_lab
```

### 4.2 Materials pricing

```python
# backend/core/materials_calc.py

def extrapolate_bulk_price(lab_prices: list, bulk_quantity: float):
    """
    eq 4.5: bulk-price extrapolation via log-log regression.
    p(Q) = b * Q^gamma
    lab_prices: [(quantity_lb, total_price_usd), ...]
    """
    import numpy as np
    Q = np.array([q for q, _ in lab_prices])
    p = np.array([P/q for q, P in lab_prices])  # unit price
    log_Q, log_p = np.log10(Q), np.log10(p)
    gamma, log_b = np.polyfit(log_Q, log_p, 1)
    b = 10**log_b
    return b * bulk_quantity**gamma

def precursor_price_from_metal(metal_spot_price, metal_fraction, conversion_markup=1.05):
    """
    Precious-metal precursor price = metal spot price / metal fraction * conversion markup
    (CatCost User Guide, Section 4.3.)
    """
    return metal_spot_price / metal_fraction * conversion_markup
```

### 4.3 Step Method (Chapter 6)

```python
# backend/core/step_method.py

STEP_COSTS = {
    # step_name: {scale: hourly_cost_usd}  (Table 6.1, mid-2017 basis)
    "ball_forming":              {"small": 100, "medium": 150, "large": None},
    "crystallizer":              {"small": 100, "medium": 200, "large": 300},
    "dryer_batch_vacuum_tray":   {"small": 50,  "medium": None,"large": None},
    "dryer_rotary_40_100C":      {"small": 75,  "medium": 100, "large": 200},
    "dryer_rotary_100_300C":     {"small": 100, "medium": 150, "large": 300},
    "dryer_spray":               {"small": None,"medium": 300, "large": 550},
    "extruder_with_feeder":      {"small": 100, "medium": 200, "large": 425},
    "filter_belt_vacuum":        {"small": 125, "medium": 175, "large": 400},
    "filter_plate_frame":        {"small": 75,  "medium": None,"large": None},
    "filter_rotary_vacuum":      {"small": None,"medium": 100, "large": 300},
    "flare":                     {"small": 50,  "medium": 75,  "large": 150},
    "incipient_wetness":         {"small": 75,  "medium": 100, "large": 200},
    "kiln_batch":                {"small": 75,  "medium": None,"large": None},
    "kiln_continuous_direct":    {"small": None,"medium": 225, "large": 400},
    "kiln_continuous_indirect":  {"small": None,"medium": 175, "large": 325},
    "mill":                      {"small": 50,  "medium": 100, "large": 200},
    "mixer_dry_blender":         {"small": 50,  "medium": 100, "large": 200},
    "mixer_slurry":              {"small": 75,  "medium": 100, "large": 200},
    "reactor_simple":            {"small": 30,  "medium": 60,  "large": 200},
    "reactor_multistep":         {"small": 100, "medium": 175, "large": 600},
    "scrubber_nox":              {"small": 35,  "medium": 75,  "large": 200},
}

SCALE_THRESHOLDS = {
    "small": (1, 5),       # 1~5 tons → Small (1 t/day)
    "medium": (5, 70),     # 5~70 tons → Medium (10 t/day)
    "large": (70, 1000),   # 70~1000 tons → Large (150 t/day)
}

CLEANING_TIME = {"small": 0.5, "medium": 1.0, "large": 1.0}  # days

def determine_scale(order_size_tons):
    for scale, (lo, hi) in SCALE_THRESHOLDS.items():
        if lo <= order_size_tons < hi:
            return scale
    return "large"

def calculate_campaign_length(order_size_tons, scale):
    production_rate = {"small": 1, "medium": 10, "large": 150}[scale]
    synthesis_days = order_size_tons / production_rate
    cleaning_days = CLEANING_TIME[scale]
    return synthesis_days + cleaning_days

def selling_margin_pct(order_size_tons):
    """Figure 6.3: selling margin as % of selling price."""
    import math
    return 39.192 * (order_size_tons ** -0.23360) / 100

def calculate_step_method(
    materials_cost_per_unit: float,
    steps: list[str],
    order_size_tons: float,
    ga_overhead_pct: float = 0.05,
    sard_pct: float = 0.05,
    chemppi_escalation: float = 1.0,  # year-basis adjustment
):
    scale = determine_scale(order_size_tons)
    campaign_days = calculate_campaign_length(order_size_tons, scale)

    # Hourly cost sum
    hourly_total = 0
    for step in steps:
        cost = STEP_COSTS[step][scale]
        if cost is None:
            raise ValueError(f"Step '{step}' not available at {scale} scale")
        hourly_total += cost

    # ChemPPI escalation (mid-2017 basis → user basis year)
    hourly_total *= chemppi_escalation

    daily_cost = hourly_total * 24  # 24 hr/day operation
    campaign_cost = daily_cost * campaign_days
    campaign_cost_per_unit = campaign_cost / (order_size_tons * 1000)  # $/kg

    subtotal = materials_cost_per_unit + campaign_cost_per_unit
    ga = subtotal * ga_overhead_pct
    sard = (subtotal + ga) * sard_pct
    margin_pct = selling_margin_pct(order_size_tons)
    pre_margin = subtotal + ga + sard
    margin = pre_margin * margin_pct / (1 - margin_pct)

    return {
        "scale": scale,
        "campaign_days": campaign_days,
        "step_cost_per_hr": hourly_total,
        "campaign_cost": campaign_cost,
        "materials_cost_per_kg": materials_cost_per_unit,
        "processing_cost_per_kg": campaign_cost_per_unit,
        "subtotal_per_kg": subtotal,
        "ga_per_kg": ga,
        "sard_per_kg": sard,
        "margin_per_kg": margin,
        "estimated_price_per_kg": pre_margin + margin,
    }
```

### 4.4 CapEx & OpEx Factors (Chapter 7)

```python
# backend/core/capex_opex.py

# Table 7.1: Peters & Timmerhaus factored costs (% of purchased equipment)
CAPEX_FACTORS_DEFAULT = {
    # Direct Capital
    "purchased_equipment": 1.00,    # 100% (basis)
    "installation": 0.47,           # 39~47%
    "instrumentation": 0.36,        # 18~36%
    "piping": 0.68,                 # 16~68%
    "electrical": 0.11,             # 10~11%
    "buildings": 0.18,              # 18~25%
    "yard_improvements": 0.10,      # 10~15%
    "service_facilities": 0.70,     # 40~70%
    "land": 0.06,                   # 4~8%
    # Indirect Capital
    "engineering_supervision": 0.33, # 32~33%
    "construction": 0.41,           # 34~41%
    "legal": 0.04,                  # 4%
    "contractors_fee": 0.19,        # 17~22%
    "contingency": 0.44,            # 35~44%
    # Working Capital
    "working_capital": 0.89,        # 70~89%
}

OPEX_FACTORS_DEFAULT = {
    # Direct Operating (% of direct labor)
    "supervisory_clerical": 0.18,
    "laboratory": 0.15,
    "maintenance_repair": 0.05,     # % of FCI
    "operating_supplies": 0.15,     # % of M&R
    # Fixed Operating
    "local_taxes": 0.025,           # % of FCI
    "insurance": 0.008,             # % of FCI
    "rent": 0.10,                   # % of land
    "plant_overhead": 0.60,         # % of LSM
    # General Expenses
    "administration": 0.20,         # % of LSM
    "distribution_marketing": 0.10, # % of operating costs
    "rnd": 0.05,                    # % of operating costs
}

def equipment_cost_scaling(base_price, base_size, target_size, exponent=0.6):
    """eq 7.1: power-law equipment-cost scaling."""
    return base_price * (target_size / base_size) ** exponent

def equipment_cost_correlation(S, a, b, n):
    """eq 7.2: Cost = a + b * S^n"""
    return a + b * S**n
```

### 4.5 Spent catalyst value (Chapter 9)

```python
# backend/core/spent_catalyst.py

# Table 9.1: support / metal losses during use
LOSSES_USE = {
    # support: {reactor_type: {L_support_use, L_metal_use}}
    "TiO2":     {"fixed": {"support": 0.02, "metal": 0.10}, "slurry": {"support": 0.03, "metal": 0.13}},
    "Al2O3":    {"fixed": {"support": 0.02, "metal": 0.03}, "slurry": {"support": 0.02, "metal": 0.04}},
    "SiO2":     {"fixed": {"support": 0.02, "metal": 0.03}, "slurry": {"support": 0.02, "metal": 0.04}},
    "Carbon":   {"fixed": {"support": 0.02, "metal": 0.025},"slurry": {"support": 0.06, "metal": 0.05}},
    "Carbonate":{"fixed": {"support": 0.05, "metal": 0.05}, "slurry": {"support": 0.05, "metal": 0.05}},
    "Clay":     {"fixed": {"support": 0.05, "metal": 0.05}, "slurry": {"support": 0.05, "metal": 0.05}},
}

# Table 9.2: metal loss from refining
LOSSES_REFINING = {
    "Pd": {"high": 0.04, "low": 0.01, "avg": 0.035},
    "Pt": {"high": 0.03, "low": 0.01, "avg": 0.030},
    "Rh": {"high": 0.10, "low": 0.05, "avg": 0.075},
    "Ru": {"high": 0.25, "low": 0.15, "avg": 0.200},
    "Au": {"avg": 0.10},
    "Ir": {"avg": 0.10},
    "Ni": {"avg": 0.20},
    "Co": {"avg": 0.20},
}

# Table 9.4: refining charges
REFINING_CHARGES = {  # $/TrOz recovered
    "Pt": 14.5, "Pd": 12.5, "Rh": 16, "Au": 11,
    "Ru": 20, "Ir": 25, "Ag": 11.5,
}

def calculate_metal_recovery_value(
    metal_symbol: str,
    metal_loading: float,        # lb metal / lb catalyst
    metal_spot_price: float,     # $/lb
    support: str,
    reactor_type: str,           # "fixed" or "slurry"
    catalyst_bulk_density: float, # lb/ft^3
):
    losses = LOSSES_USE.get(support, {}).get(reactor_type, {})
    L_metal_use = losses.get("metal", 0.05)
    L_support_use = losses.get("support", 0.02)
    L_metal_ref = LOSSES_REFINING.get(metal_symbol, {}).get("avg", 0.10)

    # V_metal (salvage value per lb catalyst)
    V_metal = (1 - L_metal_use) * (1 - L_metal_ref) * metal_loading * metal_spot_price

    # C_recovery (cost to recover per lb catalyst)
    L_solids_use = L_support_use * (1 - metal_loading) + L_metal_use * metal_loading
    F_thermox = 0.1375  # avg of low(0.125) and high(0.15) $/lb
    F_incoming = 110     # avg $/ft^3 (depends on support)
    F_refining = REFINING_CHARGES.get(metal_symbol, 15) * metal_loading

    C_recovery = (1 - L_solids_use) * (F_thermox + F_incoming / catalyst_bulk_density) + \
                 F_refining * (1 - L_metal_use) * (1 - L_metal_ref)

    V_reclaimed = V_metal - C_recovery
    return {"V_metal": V_metal, "C_recovery": C_recovery, "V_reclaimed": V_reclaimed}
```

### 4.6 Price escalation (ChemPPI / CEPCI)

```python
# backend/core/price_escalation.py

def escalate_cost(cost, from_year, to_year, index_data, index_type="chemppi"):
    """
    Escalate cost from a base year to a target year.
    index_type: "chemppi" (operating / raw materials) or "cepci" (equipment / capital).
    """
    idx_from = index_data[index_type][str(from_year)]
    idx_to = index_data[index_type][str(to_year)]
    return cost * (idx_to / idx_from)
```

---

## 5. API endpoint design

```
POST   /api/calculate              Catalyst-cost estimate (Step Method / CapEx&OpEx / Combined)
POST   /api/calculate/quick        Quick estimate (Step Method only, minimal input)
POST   /api/uncertainty            Monte Carlo uncertainty analysis
POST   /api/compare                Multi-composition comparison (up to 4)

GET    /api/prices                 Latest price for every metal
GET    /api/prices/{symbol}        Latest price + history for one metal
GET    /api/prices/{symbol}/history?from=&to=  Historical price range

GET    /api/materials              Materials library (search / filter)
POST   /api/materials              Add a user material
GET    /api/equipment              Equipment library
GET    /api/templates              Process-template list
GET    /api/templates/{id}         One process template

GET    /api/indices/chemppi        ChemPPI index
GET    /api/indices/cepci          CEPCI index

POST   /api/import/catcost         Import a CatCost JSON file
GET    /api/export/{estimate_id}   Export an estimate (JSON / CSV)

GET    /api/health                 Server status + last price-update time
```

---

## 6. Development phases (Codex work units)

> **Historical reference.** Phases 1–5 below were the original Codex work plan. The current repo state (v1.3.4, 2026-05) has implemented the bulk of every phase plus material that was never on the original list (LCA, decision engine, electrocatalyst layer model, curated USGS proxy library, source-evidence tagging, multi-family benchmark library). Use `git log --oneline` and the `## 3.1 Live additions` section above for the current ground truth; treat the lists below as the seed plan, not an open backlog.

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

---

## 7. Validation strategy

### CatCost validation cases (per User Guide Table 6.2)

| Catalyst | Conditions | CatCost estimate | Market price | Tolerance |
|----------|------------|------------------|--------------|-----------|
| 2 wt% Pt/C | 2 ton, Small scale | $27.37/lb | $34.09/lb | ±20% |
| 21 wt% Ni/Al₂O₃ | 20 ton, Medium scale | $20.59/lb | $21.33/lb | ±20% |
| USY-based FCC | 200 ton, Large scale | $2.41/lb | $2.73/lb | ±25% |

Run these three cases as a regression at the end of every Phase. The FCC band is wider (±25%) because reproducing the large-scale slurry/spray-dry route precisely requires proprietary precursor pricing that CatPrice does not redistribute; tightening it back to ±20% is a follow-up once a public USY proxy is in the materials library. See `backend/tests/test_cost_engine.py` for the live tolerance values.

---

## 8. Coding conventions

- Python: ruff (formatter + linter, configured in `pyproject.toml`), type hints encouraged on public APIs
- TypeScript: strict mode in `frontend/tsconfig.app.json`, ESLint via `frontend/eslint.config.js`
- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `style:`)
- PRs: feature-scoped, must include tests for non-trivial logic
- Environment variables: provide `.env.example`; never commit secrets

---

## 9. Important notes

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
