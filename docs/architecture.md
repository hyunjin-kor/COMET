# COMET Architecture Reference

Reference detail split out of [`AGENTS.md`](../AGENTS.md): the directory layout,
the core calculation modules, and the API surface. `AGENTS.md` keeps the operating
rules an agent must follow; this file is the map it navigates by.

---

## Project directory structure

```
comet/
├── AGENTS.md                          (agent operating rules)
├── README.md
├── LICENSE                            (PolyForm Noncommercial 1.0.0)
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

### Live additions since the initial scaffold

The tree above is the original Phase-1 scaffold. The repo has since grown the
following modules. Always run `git ls-files backend` for the authoritative
current layout — this list is a navigation aid, not a contract.

- `backend/core/`: `decision_engine.py` (benchmark scoring), `electrocatalyst.py` (electrode-area cost model), `lca.py` (GWP / CED, materials + route terms), `process_energy.py` (per-step fuel/electricity from first-principles duty × EPA factors), `material_pricing.py` (library-backed price resolution), `price_evidence.py` (confidence / freshness tagging)
- `backend/routers/`: `decision.py`, `estimates.py` (saved-estimate CRUD), `lca.py`, `indices.py`
- `backend/data/`: 30 reaction-family benchmark JSON files (`*_benchmark.json`), `electrocatalyst_library.json`, `lca_factors.json`, `process_energy_factors.json`, `materials_curated.json` (curated public-source proxies in addition to `materials_library.json`), 19 process templates (PEM/AEM/DMFC/USY/ZSM-5/etc.)
- `backend/launcher.py`, `backend/paths.py`: PyInstaller-friendly resource resolution for the packaged sidecar
- `backend/services/bls_updater.py`: ChemPPI auto-update from BLS API
- `electron/preload.js`: contextBridge for window controls and menu IPC
- `scripts/` highlights: `build_backend_bundle.ps1` (PyInstaller), `smoke_test_desktop.ps1`, `stop_comet_processes.ps1`, `validate_catcost_data.py` (local-only, requires gitignored CatCost workbook), `capture_readme_screens.mjs`, `generate_app_icons.py`

---

## Core calculation logic (faithful CatCost reimplementation)

### Materials calculation (eq 4.1~4.4)

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

### Materials pricing

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

### Step Method (Chapter 6)

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

### CapEx & OpEx Factors (Chapter 7)

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

### Spent catalyst value (Chapter 9)

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

    # V_metal (salvage value per lb catalyst). Metals recovered as scrap
    # rather than refined metal (currently Fe) price their salvage from the
    # CatCost scrap anchor in backend/data/spent_catalyst.json
    # (ChemPPI-escalated from its quote year), so a precursor-based input
    # price cannot inflate the credit.
    V_metal = (1 - L_metal_use) * (1 - L_metal_ref) * metal_loading * metal_spot_price

    # C_recovery (cost to recover per lb catalyst)
    L_solids_use = L_support_use * (1 - metal_loading) + L_metal_use * metal_loading
    F_thermox = 0.1375  # avg of low(0.125) and high(0.15) $/lb
    F_incoming = 110     # avg $/ft^3 (depends on support)
    # Charges are $/TrOz of recovered metal and exist only for precious
    # metals (non-precious anchors carry None -> no toll refining).
    F_refining = (REFINING_CHARGES.get(metal_symbol) or 0) * TROY_OZ_PER_LB * metal_loading

    C_recovery = (1 - L_solids_use) * (F_thermox + F_incoming / catalyst_bulk_density) + \
                 F_refining * (1 - L_metal_use) * (1 - L_metal_ref)

    V_reclaimed = V_metal - C_recovery
    return {"V_metal": V_metal, "C_recovery": C_recovery, "V_reclaimed": V_reclaimed}
```

### Price escalation (ChemPPI / CEPCI)

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

## API endpoint design

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
