# CatPrice — Real-Time Catalyst Cost Estimator

> A desktop tool that takes a catalyst composition and returns its
> manufacturing cost using real-time metal market prices.

## Current implementation status (as of 2026-07-20)

- GitHub repository: `https://github.com/hyunjin-kor/CatPrice`
- Latest verified release: `v1.3.9`
- Current desktop packaging: Electron (`electron/`, `dist-electron/`)
- Current Claude hand-off entry point: `CLAUDE.md`
- Blog / homepage URL: not currently surfaced in the repo or GitHub metadata.
- The Tauri / web-deployment content below comes from the original planning
  doc; for the current implementation, prefer `README.md`, `AGENTS.md`,
  `CLAUDE.md`, and the actual source layout.

## 1. Project overview

### 1.1 Problem statement
- CatCost (NREL, v1.1.1, July 2025) has a strong methodology, but the user has
  to enter metal prices manually.
- It updates the CEPCI / ChemPPI indices, but the underlying Ru / Ni / Co
  prices do not refresh automatically.
- Excel-based, which limits team collaboration, mobile access, and visualization.
- Evonik CCCT is biased toward their own products and lacks general applicability.

### 1.2 Solution: CatPrice
CatCost-Step-Method methodology + **live metal price-feed integration** + a
modern web/app UI.
- Any catalyst recipe → today's manufacturing cost / retail estimate, instantly.
- Per-metal price trend and volatility indicator.
- TEA / LCOH simulation (optional extension).

### 1.3 Relationship to CatCost
- Not a replacement for CatCost — cites and uses the CatCost methodology.
- Fills the gaps CatCost does not cover (real-time pricing, modern UI).
- Academically cites the CatCost papers (Baddour 2018, Van Allsburg 2022).

### 1.4 Open-repository operations
- License: All rights reserved
- Public GitHub repository
- Zenodo DOI (for academic citation)

---

## 2. Tech stack

### 2.1 Architecture

```
┌────────────────────────────────────────────────┐
│                  Frontend                       │
│  ┌────────────┐    ┌────────────────────────┐  │
│  │ Web (React) │    │ Desktop (Tauri 2.0)    │  │
│  └──────┬─────┘    └──────────┬─────────────┘  │
│         └──────────┬──────────┘                 │
│          ┌─────────▼─────────┐                  │
│          │  Shared UI Layer   │                  │
│          │ React + Tailwind   │                  │
│          │ + shadcn/ui        │                  │
│          └─────────┬─────────┘                  │
└────────────────────┼────────────────────────────┘
                     │ REST API
┌────────────────────┼────────────────────────────┐
│                    │     Backend                  │
│          ┌─────────▼─────────┐                   │
│          │   FastAPI Server   │                   │
│          └─────────┬─────────┘                   │
│    ┌───────────────┼───────────────┐             │
│  ┌─▼────┐   ┌─────▼──────┐  ┌────▼─────┐       │
│  │ Cost  │   │ Price      │  │ TEA      │       │
│  │ Calc  │   │ Fetcher    │  │ Module   │       │
│  │Engine │   │ (LME/Kitco)│  │(optional)│       │
│  └──┬────┘   └─────┬──────┘  └────┬─────┘       │
│     └───────────────┼──────────────┘             │
│           ┌─────────▼──────────┐                 │
│           │   SQLite / Postgres │                 │
│           │  (Price History DB) │                 │
│           └────────────────────┘                 │
└──────────────────────────────────────────────────┘
```

### 2.2 Technology choices

| Layer | Tech | Rationale |
|-------|------|-----------|
| Frontend | React 18 + TypeScript + Vite | Fast iteration, large ecosystem |
| Desktop | Tauri 2.0 | ~10x lighter than Electron |
| UI | shadcn/ui + Tailwind CSS | Clean, customizable |
| Charts | Recharts + Plotly.js | Interactive visualizations |
| Backend | FastAPI (Python 3.11+) | async, automatic API docs |
| Engine | Python (NumPy, Pandas) | Calculation logic |
| DB | SQLite → PostgreSQL | Price-history storage |
| Price API | httpx + APScheduler | Async price collection |
| Testing | pytest + Playwright | Backend + E2E |
| Deploy | Docker + GitHub Actions | CI/CD |

---

## 3. Core features

### 3.1 Catalyst price calculator (core feature)

The user enters a catalyst composition; the calculator returns the
manufacturing cost based on real-time prices.

#### Input UI
```
┌─────────────────────────────────────────────┐
│  🔧 Catalyst Composition                    │
│                                             │
│  Active Metals:                             │
│  ┌─────────┬────────┬──────────────┐       │
│  │ Metal ▼ │ wt%    │ Precursor ▼  │  [+]  │
│  │ Ru      │ 5.0    │ RuCl₃·xH₂O  │       │
│  └─────────┴────────┴──────────────┘       │
│                                             │
│  Support:    [γ-Al₂O₃    ▼]                │
│  Promoter:   [None        ▼]  wt%: [  ]    │
│                                             │
│  Synthesis:  [Impregnation ▼]               │
│  Scale:      [Industrial (ton) ▼]           │
│                                             │
│  [Calculate Cost →]                         │
└─────────────────────────────────────────────┘
```

#### Calculation logic (CatCost Step Method-based)
```python
def calculate_catalyst_cost(composition: CatalystInput) -> CostResult:
    """
    CatCost Step Method (Baddour et al., Org. Process Res. Dev. 2018)
    + automatic live metal-price refresh.
    """

    # Step 1: raw material cost — apply live prices
    metal_costs = []
    for metal in composition.active_metals:
        live_price = price_db.get_latest(metal.symbol)  # ← live!
        precursor = get_precursor(metal.symbol, metal.precursor)
        # Convert metal price to precursor price.
        precursor_cost = live_price / precursor.metal_fraction * precursor.markup
        metal_costs.append(metal.loading_wt_pct / 100 * precursor_cost)

    support_cost = composition.support_fraction * price_db.get_support(composition.support)
    promoter_cost = sum(p.wt_pct/100 * price_db.get_promoter(p.name)
                        for p in composition.promoters)

    C_raw = sum(metal_costs) + support_cost + promoter_cost

    # Step 2: manufacturing cost — per-method factor
    f_mfg = MANUFACTURING_FACTORS[composition.synthesis_method]  # 1.3~8.0
    C_mfg = C_raw * f_mfg

    # Step 3: overhead (R&D, admin, profit)
    C_overhead = (C_raw + C_mfg) * composition.overhead_factor  # default 0.30

    # Step 4: scale adjustment
    f_scale = SCALE_FACTORS[composition.production_scale]  # 0.7~50
    manufacturing_cost = (C_raw + C_mfg + C_overhead) * f_scale

    # Step 5: retail estimate
    f_dist = DISTRIBUTION_MARKUP[composition.production_scale]  # 1.5~5.0
    retail_estimate = manufacturing_cost * f_dist

    # Step 6: spent-catalyst recovery value
    recovery = calculate_spent_value(composition.active_metals)
    net_cost = manufacturing_cost - recovery

    return CostResult(
        raw_material_cost=C_raw,
        manufacturing_cost=C_mfg,
        overhead=C_overhead,
        total_manufacturing=manufacturing_cost,
        retail_low=manufacturing_cost * f_dist_low,
        retail_high=manufacturing_cost * f_dist_high,
        spent_recovery=recovery,
        net_cost=net_cost,
        breakdown_pct=calculate_percentages(...),
        metal_prices_used={m.symbol: price_db.get_latest(m.symbol)
                          for m in composition.active_metals},
        price_timestamp=datetime.utcnow(),
    )
```

#### Output UI
```
┌─────────────────────────────────────────────────────┐
│  💰 Cost Estimate: 5wt% Ru/Al₂O₃                   │
│  ─────────────────────────────────────────────       │
│  Today's Ru price: $50,000/kg (Heraeus, 2026-03-23) │
│                                                     │
│  Raw Materials     $961/kg cat    ████████████ 33%   │
│  Manufacturing     $1,442/kg     ██████████   28%   │
│  Overhead          $721/kg       ██████       14%   │
│  ──────────────────────────────────                 │
│  Manufacturing Cost: $2,892/kg cat                   │
│  Retail Estimate:    $7,200 — $10,100/kg cat         │
│  Spent Recovery:     -$588/kg (Ru recovery 95%)      │
│  ──────────────────────────────────                 │
│  ★ Net Cost:         $2,304/kg cat                   │
│                                                     │
│  [📊 Breakdown Chart]  [📈 Price History]  [💾 Export]│
└─────────────────────────────────────────────────────┘
```

---

### 3.2 Live metal prices (price feed)

#### Data sources
| Metals | Source | Cadence | API / method |
|--------|--------|---------|--------------|
| Ru, Pt, Ir, Rh, Pd | Kitco / Heraeus | daily | scraping or API |
| Ni, Co, Cu, Zn, Mo | LME | daily | LME API or scraping |
| Fe, rare earths | USGS / World Bank | weekly–monthly | CSV / API |

#### Capabilities
- Per-metal live-price dashboard
- 5-year price-trend chart
- Volatility indicator (so catalyst cost uncertainty is visible)
- Price alerts (when thresholds are crossed)
- Price-history DB (for time-series analysis)

#### DB schema
```sql
CREATE TABLE metal_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,           -- 'Ru', 'Ni', 'Co', ...
    price_usd_per_kg REAL NOT NULL,
    source TEXT NOT NULL,           -- 'kitco', 'lme', 'heraeus'
    price_date DATE NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE UNIQUE INDEX idx_symbol_date_source ON metal_prices(symbol, price_date, source);
```

---

### 3.3 Materials library

A built-in library similar to CatCost's, with the option to add user materials.

#### Categories
- **Metals**: Ru, Ni, Co, Fe, Mo, Cu, Pt, Ir, Rh, Pd, Li, Mn, ...
- **Supports**: γ-Al₂O₃, α-Al₂O₃, SiO₂, TiO₂, CeO₂, MgO, MgAl₂O₄, CNT, SiC, BN, zeolites, ...
- **Promoters**: K₂O, Cs₂CO₃, BaO, La₂O₃, Na₂CO₃, CeO₂, ...
- **Precursors**: RuCl₃, Ni(NO₃)₂·6H₂O, Co(NO₃)₂·6H₂O, H₂PtCl₆, ... (with metal fraction and markup)

#### Price-source priority
1. Live API (metals)
2. User custom override
3. Built-in default (seed data)

---

### 3.4 Cost comparison & visualization

- **Composition comparison**: up to four catalyst recipes side-by-side
- **Pie chart**: raw materials (metal / support / promoter) vs manufacturing vs overhead
- **Scale curve**: lab → pilot → industrial price changes
- **Metal price sensitivity**: Tornado chart (which element dominates the cost?)
- **Time series**: how the manufacturing cost of the same recipe has tracked the metal market

---

### 3.5 TEA / LCOH module (Phase 2 extension)

Optional module that connects the catalyst-cost result directly to TEA.
- Catalyst cost → LCOH contribution, computed automatically.
- LCOH curve by scale (0.1~100 TPD).
- Process-specific TEA templates for NH₃ / H₂ / methanol.
- Sensitivity analysis (NH₃ price, electricity rate, catalyst lifetime, etc.).

---

## 4. Project structure

```
catprice/
├── README.md
├── LICENSE (All rights reserved)
├── pyproject.toml
├── docker-compose.yml
│
├── backend/
│   ├── main.py                      # FastAPI entry
│   ├── config.py                    # Env vars, API keys
│   ├── database.py                  # SQLAlchemy
│   │
│   ├── core/                        # Core calculation engine
│   │   ├── cost_engine.py           # Catalyst-cost calculation
│   │   ├── price_fetcher.py         # Metal price collection
│   │   ├── constants.py             # Manufacturing factors, thermo constants
│   │   └── tea_engine.py            # TEA module (Phase 2)
│   │
│   ├── models/                      # SQLAlchemy DB models
│   │   ├── metal_price.py
│   │   └── estimate.py              # Saved estimate
│   │
│   ├── schemas/                     # Pydantic I/O schemas
│   │   ├── cost_input.py
│   │   ├── cost_result.py
│   │   └── metal_price.py
│   │
│   ├── routers/                     # API routers
│   │   ├── calculator.py            # POST /api/calculate
│   │   ├── prices.py                # GET  /api/prices
│   │   ├── materials.py             # GET  /api/materials
│   │   └── compare.py               # POST /api/compare
│   │
│   ├── data/                        # Seed data
│   │   ├── manufacturing_factors.json
│   │   ├── raw_material_prices.json
│   │   ├── supports.json
│   │   ├── promoters.json
│   │   └── precursors.json
│   │
│   └── tests/
│       ├── test_cost_engine.py      # Cost validation (compare to CatCost)
│       ├── test_price_fetcher.py
│       └── test_api.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   │
│   └── src/
│       ├── App.tsx
│       ├── pages/
│       │   ├── Calculator.tsx       # Main: catalyst price calculator
│       │   ├── Prices.tsx           # Metal-price dashboard
│       │   ├── Compare.tsx          # Composition comparison
│       │   ├── Library.tsx          # Materials library
│       │   └── TEA.tsx              # TEA module (Phase 2)
│       │
│       └── components/
│           ├── CompositionInput.tsx  # Composition form
│           ├── CostBreakdown.tsx     # Pie / bar chart
│           ├── PriceTimeline.tsx     # Metal price time series
│           ├── TornadoChart.tsx      # Sensitivity analysis
│           └── ScaleCurve.tsx        # Scale-by-cost curve
│
├── desktop/                         # Tauri wrapper
│   └── src-tauri/
│       └── tauri.conf.json
│
└── docs/                            # MkDocs
    ├── index.md
    ├── methodology.md               # CatCost Step Method explanation
    └── api-reference.md
```

---

## 5. Roadmap

### Phase 1: MVP (2~3 weeks)
- [ ] `cost_engine.py` — core calculation logic (composition → manufacturing cost)
- [ ] `constants.py` — manufacturing factors, scale factors, precursor data
- [ ] Seed data (metal / support / promoter / precursor prices)
- [ ] FastAPI: `POST /api/calculate`, `GET /api/materials`
- [ ] React: Calculator page (input form → result + pie chart)
- [ ] Read metal prices from seed data (before live API integration)

### Phase 2: Live Prices (2~3 weeks)
- [ ] `price_fetcher.py` — LME / Kitco real-time price collection
- [ ] Price-history DB + scheduler (daily auto-collect)
- [ ] Prices dashboard (time series, volatility)
- [ ] Calculator results auto-reflect "today's basis"

### Phase 3: Advanced features (3~4 weeks)
- [ ] Composition-comparison mode (up to 4)
- [ ] Cost-by-scale curve
- [ ] Sensitivity analysis (Tornado chart)
- [ ] TEA / LCOH module — basic version
- [ ] Tauri desktop-app packaging

### Phase 4: Community release (2~3 weeks)
- [ ] Docker compose one-click deploy
- [ ] GitHub Actions CI/CD
- [ ] MkDocs docs site
- [ ] Zenodo DOI registration
- [ ] README, Contributing guide, Examples

---

## 6. Key data (seed data)

### 6.1 Manufacturing-cost factors
→ `catprice_seed_data/manufacturing_factors.json` (already created)

### 6.2 Raw-material price DB
→ `catprice_seed_data/raw_material_prices.json` (already created)

### 6.3 Validation method
Use known CatCost examples (ZSM-5, Pt/TiO₂, Mo₂C) with the same inputs and
write tests that the result is within ±20%.

---

## 7. API design

### Core endpoints
```
POST /api/calculate          — Catalyst composition → cost
GET  /api/prices             — Latest price for every metal
GET  /api/prices/{symbol}    — Latest price + history for one metal
GET  /api/materials          — Materials library (metals / supports / promoters)
POST /api/compare            — Multi-composition comparison
GET  /api/health             — Server status + last price-update time
```

### POST /api/calculate example
```json
// Request
{
  "active_metals": [
    {"symbol": "Ru", "loading_wt_pct": 5.0, "precursor": "RuCl3"}
  ],
  "support": {"material": "gamma_Al2O3"},
  "promoters": [],
  "synthesis_method": "INCIPIENT_WETNESS",
  "production_scale": "INDUSTRIAL",
  "overhead_factor": 0.30
}

// Response
{
  "raw_material_cost_per_kg": 961.0,
  "manufacturing_cost_per_kg": 1442.0,
  "overhead_per_kg": 721.0,
  "total_manufacturing_cost": 2892.0,
  "retail_estimate": {"low": 7230, "high": 10120},
  "spent_recovery": 588.0,
  "net_cost": 2304.0,
  "breakdown_pct": {
    "metal_Ru": 92.1, "support": 0.5, "manufacturing": 4.9, "overhead": 2.5
  },
  "prices_used": {
    "Ru": {"price": 50000, "unit": "$/kg", "source": "heraeus", "date": "2026-03-23"}
  },
  "methodology": "CatCost Step Method (Baddour et al. 2018)",
  "timestamp": "2026-03-23T15:30:00Z"
}
```

---

## 8. References

1. Baddour et al., "Estimating Precommercial Heterogeneous Catalyst Price: A Simple Step-Based Method", *Org. Process Res. Dev.* **2018**, 22(12). DOI: 10.1021/acs.oprd.8b00245
2. Van Allsburg et al., "Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost", *Nature Catalysis* **2022**. DOI: 10.1038/s41929-022-00759-6
3. CatCost Tool v1.1.1 (July 2025): https://catcost.chemcatbio.org/
4. Peters, Timmerhaus, West, *Plant Design and Economics for Chemical Engineers*, 5th Ed.

---

## 9. How to use this with Codex

```bash
# Drop this file at the project root and say:
# "Read CatPrice_Project.md and start implementing from Phase 1".

# Seed data is already prepared under catprice_seed_data/:
# - manufacturing_factors.json (manufacturing-cost factors)
# - raw_material_prices.json (metal / support / promoter / precursor prices)
```
