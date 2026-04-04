# CatPrice — Codex Development Framework

> 이 파일은 Codex가 프로젝트를 이해하고 일관성 있게 개발하기 위한 마스터 가이드입니다.
> `CatPrice_Project.md`의 기획을 기반으로, GitHub 벤치마킹 결과와 CatCost 원본 방법론을 반영했습니다.

---

## 0. 프로젝트 정체성

- **이름**: CatPrice (촉매 비용을 "crack"해서 분석한다는 의미)
- **한줄 설명**: 실시간 금속 시세 기반 촉매 제조원가 추정 데스크톱 도구
- **라이선스**: All rights reserved
- **핵심 차별점**: CatCost 방법론 기반이지만, 실시간 시세 자동 반영 + 현대적 웹/데스크탑 UI
- **학술 인용**: Baddour et al. 2018, Van Allsburg et al. 2022

---

## 1. GitHub 벤치마킹 결과 및 채택 아이디어

### 1.1 직접 관련 프로젝트

| 프로젝트 | 핵심 아이디어 | CatPrice 적용 |
|---------|------------|-------------|
| **NREL/catcost-data-tools** | CatCost Excel↔JSON 변환 Python 도구 | Excel 데이터 파싱 로직 참고, Materials Library JSON 스키마 호환 |
| **ChemEngDPpy** | Python으로 화공 장비 sizing + CapEx/OpEx 계산 | 장비 비용 상관식(power-law) 엔진 참고, Garrett/Peters 계수 구현 |
| **BioSTEAM** | 바이오리파이너리 TEA+LCA, 불확실성 분석, OOP 설계 | **Monte Carlo 불확실성 분석** 모듈 구조 차용, Unit 기반 OOP 패턴 |
| **pyH2A** | 수소 생산 LCOH 분석, Markdown 입력→리포트 출력 | LCOH 계산 모듈 구조, **플러그인 아키텍처** 참고 |
| **NREL/H2Integrate** | 하이브리드 에너지 시스템 모델링 | TEA/LCOH Phase 2 확장 시 연계 가능성 |

### 1.2 금속 시세 API 생태계

| API/도구 | 특징 | 추천도 |
|---------|------|-------|
| **Metals-API** (metals-api.com) | REST API, 168통화, LME/LBMA 소스, 60초 업데이트 | ★★★★ (무료 플랜 있음) |
| **MetalpriceAPI** | PGM 포함, Python SDK 제공 | ★★★★ |
| **Metals.Dev** | 산업 금속+귀금속, JSON API, 60초 지연 | ★★★★★ (가장 포괄적) |
| **tiagocordeiro/lme** | LME Python 패키지, 히스토리컬 데이터 | ★★★ (보조용) |
| **Kitco 스크래핑** | PGM(Ru, Ir, Rh) 가격 - API 없음 | ★★★ (백업용, robots.txt 확인 필요) |

**전략**: Metals.Dev를 1차 소스로, MetalpriceAPI를 백업으로. PGM은 Heraeus/Johnson Matthey 스크래핑 검토.

### 1.3 풀스택 아키텍처 참고

| 프로젝트 | 아키텍처 | 채택 포인트 |
|---------|---------|----------|
| **tauri-fastapi-full-stack-template** | Tauri 2 + React + FastAPI + SQLite (sidecar) | **이 템플릿을 보일러플레이트로 사용** |
| **stock-market-dashboard** | FastAPI + React + SQLite + Docker | 실시간 가격 대시보드 WebSocket 패턴 |
| **Dynamic-pricing-optimization-system** | FastAPI + React + ML | Tornado chart 민감도 분석 UI 참고 |

### 1.4 벤치마킹에서 도출한 추가 아이디어

1. **불확실성 분석**: BioSTEAM처럼 Monte Carlo 시뮬레이션으로 비용 범위 제공 (CatCost의 Low/Base/High보다 진보)
2. **플러그인 아키텍처**: pyH2A처럼 공정별 TEA 모듈을 플러그인으로 분리 (NH₃ cracking, H₂ production 등)
3. **catcost-data-tools 호환**: CatCost JSON export 포맷을 import할 수 있게 하면 기존 사용자 마이그레이션 용이
4. **ChemPPI/CEPCI 자동 업데이트**: BLS API에서 ChemPPI 자동 가져오기 (CatCost는 수동 업데이트)
5. **Comparison Mode**: 여러 촉매 조성을 side-by-side로 비교하는 인터랙티브 대시보드

---

## 2. 기술 스택 (확정)

```
Frontend:  React 18 + TypeScript + Vite
UI:        shadcn/ui + Tailwind CSS 4
Charts:    Recharts (기본) + Plotly.js (3D/Sankey)
Desktop:   Tauri 2.0 (sidecar: FastAPI를 PyInstaller로 번들)
Backend:   FastAPI (Python 3.11+), async
ORM:       SQLModel (SQLAlchemy + Pydantic 통합)
DB:        SQLite (개발/데스크탑) → PostgreSQL (배포)
Migration: Alembic
Scheduler: APScheduler (가격 자동 수집)
HTTP:      httpx (async)
Testing:   pytest + pytest-asyncio + Playwright (E2E)
CI/CD:     GitHub Actions
Deploy:    Docker Compose
Docs:      MkDocs Material
```

**보일러플레이트**: `tauri-fastapi-full-stack-template` 기반으로 시작

---

## 3. 프로젝트 디렉토리 구조

```
catprice/
├── AGENTS.md                          ← 이 파일 (Codex 마스터 가이드)
├── README.md
├── LICENSE                            (All rights reserved)
├── pyproject.toml                     (Python 의존성, ruff, pytest 설정)
├── docker-compose.yml
├── .github/
│   └── workflows/
│       ├── ci.yml                     (lint + test + build)
│       └── release.yml                (태그 → GitHub Release + Docker Hub)
│
├── backend/
│   ├── __init__.py
│   ├── main.py                        # FastAPI entry point
│   ├── config.py                      # Pydantic Settings (환경변수, API keys)
│   ├── database.py                    # SQLModel engine, session
│   │
│   ├── core/                          # === 핵심 계산 엔진 ===
│   │   ├── __init__.py
│   │   ├── cost_engine.py             # CatCost Step Method + CapEx/OpEx 통합 계산
│   │   ├── materials_calc.py          # 화학양론 (eq 4.1~4.4), 스케일링 (k_SF)
│   │   ├── step_method.py             # 3a Step Method 전용 로직
│   │   ├── capex_opex.py              # 3b~3e CapEx/OpEx Factors 전용 로직
│   │   ├── spent_catalyst.py          # 폐촉매 회수/매각/매립 가치 계산
│   │   ├── price_fetcher.py           # 금속 시세 수집기 (Metals.Dev, MetalpriceAPI)
│   │   ├── price_escalation.py        # ChemPPI/CEPCI 기반 연도별 물가 보정
│   │   ├── uncertainty.py             # Monte Carlo 불확실성 분석 (BioSTEAM 영감)
│   │   ├── tea_engine.py              # TEA/LCOH 모듈 (Phase 2)
│   │   └── constants.py               # 제조 계수, 열역학 상수, 스케일 팩터
│   │
│   ├── models/                        # SQLModel DB 모델
│   │   ├── __init__.py
│   │   ├── metal_price.py             # 금속 가격 이력
│   │   ├── material.py                # 원료 라이브러리 아이템
│   │   ├── equipment.py               # 장비 라이브러리 (비용 상관식 포함)
│   │   ├── estimate.py                # 저장된 비용 추정 결과
│   │   └── process_template.py        # 공정 템플릿 (Step + CapEx/OpEx)
│   │
│   ├── schemas/                       # Pydantic I/O 스키마
│   │   ├── __init__.py
│   │   ├── cost_input.py              # POST /api/calculate 요청 스키마
│   │   ├── cost_result.py             # 비용 계산 결과 스키마
│   │   ├── metal_price.py             # 금속 가격 스키마
│   │   └── comparison.py              # 다중 조성 비교 스키마
│   │
│   ├── routers/                       # FastAPI 라우터
│   │   ├── __init__.py
│   │   ├── calculator.py              # POST /api/calculate (Step + CapEx/OpEx)
│   │   ├── prices.py                  # GET  /api/prices, /api/prices/{symbol}
│   │   ├── materials.py               # CRUD /api/materials
│   │   ├── equipment.py               # CRUD /api/equipment
│   │   ├── templates.py               # GET  /api/templates (공정 템플릿)
│   │   ├── compare.py                 # POST /api/compare
│   │   ├── uncertainty.py             # POST /api/uncertainty (Monte Carlo)
│   │   └── catcost_import.py          # POST /api/import/catcost (JSON 호환)
│   │
│   ├── services/                      # 비즈니스 로직 서비스
│   │   ├── __init__.py
│   │   ├── price_scheduler.py         # APScheduler: 매일 시세 자동 수집
│   │   └── bls_updater.py             # BLS API → ChemPPI 자동 업데이트
│   │
│   ├── data/                          # Seed 데이터
│   │   ├── materials_library.json     # CatCost Materials Library 호환 포맷 (자체 수집)
│   │   ├── equipment_library.json     # 장비 비용 상관식 (공개 문헌 기반)
│   │   ├── step_library.json          # Step Method 단계별 시간당 비용
│   │   ├── spent_catalyst.json        # 폐촉매 처리 파라미터
│   │   ├── process_templates/         # 공정 템플릿들
│   │   │   ├── wet_impregnation_metal_oxide.json
│   │   │   ├── metal_pgm_carbon.json
│   │   │   ├── zeolite_fcc.json
│   │   │   ├── metal_carbide_bulk.json
│   │   │   └── nanoparticles_flow.json
│   │   ├── chemppi.json               # Chemical Producer Price Index
│   │   ├── cepci.json                 # Chemical Engineering Plant Cost Index
│   │   └── unit_conversions.json      # 단위 변환 테이블
│   │
│   ├── migrations/                    # Alembic migrations
│   │   └── ...
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_cost_engine.py        # CatCost 검증 케이스 (Pt/C, Ni/Al₂O₃, FCC)
│       ├── test_materials_calc.py     # 화학양론 + 스케일링 검증
│       ├── test_step_method.py        # Step Method ±20% 검증
│       ├── test_capex_opex.py         # CapEx/OpEx 계수 검증
│       ├── test_spent_catalyst.py     # 폐촉매 회수가치 검증
│       ├── test_price_fetcher.py      # API 모킹 테스트
│       ├── test_price_escalation.py   # ChemPPI/CEPCI 물가 보정 검증
│       └── test_api.py                # FastAPI 엔드포인트 통합 테스트
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
│       │   ├── api.ts                 # API 클라이언트 (TanStack Query)
│       │   └── utils.ts
│       │
│       ├── pages/
│       │   ├── Calculator.tsx         # 메인: 촉매 가격 계산기 (Step + CapEx/OpEx 선택)
│       │   ├── Prices.tsx             # 금속 시세 대시보드
│       │   ├── Compare.tsx            # 조성 비교 (최대 4개)
│       │   ├── Library.tsx            # 원료/장비 라이브러리 관리
│       │   ├── Templates.tsx          # 공정 템플릿 브라우저
│       │   ├── Uncertainty.tsx        # Monte Carlo 불확실성 분석
│       │   └── TEA.tsx                # TEA/LCOH 모듈 (Phase 2)
│       │
│       └── components/
│           ├── layout/
│           │   ├── Sidebar.tsx
│           │   └── Header.tsx
│           ├── calculator/
│           │   ├── CompositionInput.tsx    # 촉매 조성 입력 폼
│           │   ├── StepMethodConfig.tsx    # Step Method 파라미터
│           │   ├── CapExOpExConfig.tsx     # CapEx/OpEx 파라미터
│           │   ├── CostBreakdown.tsx       # 비용 분해 (파이/도넛/Sankey)
│           │   └── ResultSummary.tsx       # 결과 요약 카드
│           ├── prices/
│           │   ├── PriceTimeline.tsx       # 금속 시세 시계열
│           │   ├── PriceCard.tsx           # 개별 금속 가격 카드
│           │   └── VolatilityBadge.tsx     # 변동성 지표
│           ├── charts/
│           │   ├── TornadoChart.tsx        # 민감도 분석
│           │   ├── ScaleCurve.tsx          # 규모별 비용 곡선
│           │   ├── SankeyDiagram.tsx       # 비용 흐름 Sankey
│           │   └── MonteCarloHist.tsx      # 불확실성 히스토그램
│           └── shared/
│               ├── MaterialSelector.tsx    # 원료 선택 드롭다운
│               ├── EquipmentSelector.tsx   # 장비 선택 드롭다운
│               └── ExportButton.tsx        # JSON/CSV/PDF 내보내기
│
├── desktop/                           # Tauri 래퍼
│   └── src-tauri/
│       ├── tauri.conf.json
│       ├── Cargo.toml
│       └── src/
│           └── main.rs                # sidecar(FastAPI) 관리
│
└── docs/                              # MkDocs Material
    ├── mkdocs.yml
    ├── index.md
    ├── getting-started.md
    ├── methodology.md                 # CatCost Step Method + CapEx/OpEx 설명
    ├── api-reference.md
    └── contributing.md
```

---

## 4. 핵심 계산 로직 상세 (CatCost 충실 재현)

### 4.1 Materials Calculation (eq 4.1~4.4)

```python
# backend/core/materials_calc.py

def calculate_active_phase_mass(m_LR, MW_LR, mol_ratio, MW_AP, yield_pct):
    """eq 4.1: 활성상 질량 계산"""
    return (m_LR / MW_LR) * mol_ratio * MW_AP * (yield_pct / 100)

def calculate_catalyst_mass(m_AP, m_sup):
    """eq 4.2: 총 촉매 질량"""
    return m_AP + m_sup

def calculate_support_mass(m_AP, wt_pct):
    """eq 4.3: 담체 질량 (wt% 기반)"""
    return (m_AP / (wt_pct / 100)) - m_AP

def calculate_scaling_factor(M_cat_plant, m_cat_lab):
    """eq 4.4: lab→plant 스케일링 팩터"""
    return M_cat_plant / m_cat_lab
```

### 4.2 Materials Pricing

```python
# backend/core/materials_calc.py

def extrapolate_bulk_price(lab_prices: list, bulk_quantity: float):
    """
    eq 4.5: Log-log 회귀로 벌크 가격 외삽
    p(Q) = b × Q^γ
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
    귀금속 전구체 가격 = 금속 spot price / 금속 함량 × 변환 마크업
    (CatCost User Guide Section 4.3 기반)
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
    """Figure 6.3: Selling margin as % of selling price"""
    import math
    return 39.192 * (order_size_tons ** -0.23360) / 100

def calculate_step_method(
    materials_cost_per_unit: float,
    steps: list[str],
    order_size_tons: float,
    ga_overhead_pct: float = 0.05,
    sard_pct: float = 0.05,
    chemppi_escalation: float = 1.0,  # 기준연도 보정
):
    scale = determine_scale(order_size_tons)
    campaign_days = calculate_campaign_length(order_size_tons, scale)

    # 시간당 비용 합산
    hourly_total = 0
    for step in steps:
        cost = STEP_COSTS[step][scale]
        if cost is None:
            raise ValueError(f"Step '{step}' not available at {scale} scale")
        hourly_total += cost

    # ChemPPI 물가 보정 (mid-2017 기준 → 사용자 기준연도)
    hourly_total *= chemppi_escalation

    daily_cost = hourly_total * 24  # 24hr/day operation
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
    """eq 7.1: Power-law 장비 비용 스케일링"""
    return base_price * (target_size / base_size) ** exponent

def equipment_cost_correlation(S, a, b, n):
    """eq 7.2: Cost = a + b * S^n"""
    return a + b * S**n
```

### 4.5 Spent Catalyst Value (Chapter 9)

```python
# backend/core/spent_catalyst.py

# Table 9.1: Support/metal losses during use
LOSSES_USE = {
    # support: {reactor_type: {L_support_use, L_metal_use}}
    "TiO2":     {"fixed": {"support": 0.02, "metal": 0.10}, "slurry": {"support": 0.03, "metal": 0.13}},
    "Al2O3":    {"fixed": {"support": 0.02, "metal": 0.03}, "slurry": {"support": 0.02, "metal": 0.04}},
    "SiO2":     {"fixed": {"support": 0.02, "metal": 0.03}, "slurry": {"support": 0.02, "metal": 0.04}},
    "Carbon":   {"fixed": {"support": 0.02, "metal": 0.025},"slurry": {"support": 0.06, "metal": 0.05}},
    "Carbonate":{"fixed": {"support": 0.05, "metal": 0.05}, "slurry": {"support": 0.05, "metal": 0.05}},
    "Clay":     {"fixed": {"support": 0.05, "metal": 0.05}, "slurry": {"support": 0.05, "metal": 0.05}},
}

# Table 9.2: Metal loss from refining
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

# Table 9.4: Refining charges
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
    catalyst_bulk_density: float, # lb/ft³
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
    F_incoming = 110     # avg $/ft³ (depends on support)
    F_refining = REFINING_CHARGES.get(metal_symbol, 15) * metal_loading

    C_recovery = (1 - L_solids_use) * (F_thermox + F_incoming / catalyst_bulk_density) + \
                 F_refining * (1 - L_metal_use) * (1 - L_metal_ref)

    V_reclaimed = V_metal - C_recovery
    return {"V_metal": V_metal, "C_recovery": C_recovery, "V_reclaimed": V_reclaimed}
```

### 4.6 Price Escalation (ChemPPI / CEPCI)

```python
# backend/core/price_escalation.py

def escalate_cost(cost, from_year, to_year, index_data, index_type="chemppi"):
    """
    비용을 기준연도에서 목표연도로 물가 보정
    index_type: "chemppi" (운영비/원료) 또는 "cepci" (장비/자본비)
    """
    idx_from = index_data[index_type][str(from_year)]
    idx_to = index_data[index_type][str(to_year)]
    return cost * (idx_to / idx_from)
```

---

## 5. API 엔드포인트 설계

```
POST   /api/calculate              촉매 비용 산출 (Step Method / CapEx&OpEx / Combined)
POST   /api/calculate/quick        간이 계산 (Step Method only, 최소 입력)
POST   /api/uncertainty            Monte Carlo 불확실성 분석
POST   /api/compare                다중 조성 비교 (최대 4개)

GET    /api/prices                 전체 금속 최신 시세
GET    /api/prices/{symbol}        특정 금속 시세 + 이력
GET    /api/prices/{symbol}/history?from=&to=  가격 이력 조회

GET    /api/materials              원료 라이브러리 (검색/필터)
POST   /api/materials              사용자 원료 추가
GET    /api/equipment              장비 라이브러리
GET    /api/templates              공정 템플릿 목록
GET    /api/templates/{id}         특정 템플릿 상세

GET    /api/indices/chemppi        ChemPPI 지수
GET    /api/indices/cepci          CEPCI 지수

POST   /api/import/catcost         CatCost JSON 파일 임포트
GET    /api/export/{estimate_id}   추정 결과 내보내기 (JSON/CSV)

GET    /api/health                 서버 상태 + 시세 업데이트 시각
```

---

## 6. 개발 Phase 순서 (Codex 작업 단위)

### Phase 1: 계산 엔진 코어 (MVP)
```
Task 1.1: 프로젝트 초기화 (pyproject.toml, 디렉토리, DB 설정)
Task 1.2: Seed 데이터 JSON 파일 생성 (materials, steps, equipment, indices)
Task 1.3: materials_calc.py — 화학양론 + 스케일링 (eq 4.1~4.4)
Task 1.4: step_method.py — Step Method 전체 구현 + 12개 템플릿
Task 1.5: cost_engine.py — 통합 계산 엔진
Task 1.6: spent_catalyst.py — 폐촉매 회수가치
Task 1.7: price_escalation.py — ChemPPI/CEPCI 물가 보정
Task 1.8: constants.py — 모든 계수/상수 정리
Task 1.9: 테스트 — CatCost 검증 케이스 3개 (Pt/C, Ni/Al₂O₃, FCC) ±20% 검증
```

### Phase 2: API 서버 + 기본 UI
```
Task 2.1: FastAPI 앱 구조 (main.py, config.py, database.py)
Task 2.2: DB 모델 + Alembic 마이그레이션
Task 2.3: API 라우터 구현 (calculator, materials, prices)
Task 2.4: React 프론트엔드 초기화 (Vite + shadcn/ui)
Task 2.5: Calculator 페이지 (입력 폼 → 결과 + 파이 차트)
Task 2.6: Library 페이지 (원료 검색/선택)
```

### Phase 3: 실시간 시세 연동
```
Task 3.1: price_fetcher.py — Metals.Dev / MetalpriceAPI 연동
Task 3.2: price_scheduler.py — APScheduler 매일 자동 수집
Task 3.3: Prices 대시보드 (시계열 차트, 변동성)
Task 3.4: 계산 결과에 "오늘 시세 기준" 자동 반영
Task 3.5: bls_updater.py — BLS API → ChemPPI 자동 업데이트
```

### Phase 4: 고급 기능
```
Task 4.1: capex_opex.py — CapEx & OpEx Factors Method 전체 구현
Task 4.2: uncertainty.py — Monte Carlo 불확실성 분석
Task 4.3: Compare 페이지 (최대 4개 조성 비교)
Task 4.4: Tornado chart 민감도 분석
Task 4.5: 규모별 비용 곡선 (ScaleCurve)
Task 4.6: Sankey diagram 비용 흐름 시각화
Task 4.7: CatCost JSON import/export 호환
```

### Phase 5: 배포 + 데스크탑
```
Task 5.1: Docker Compose 원클릭 배포
Task 5.2: Tauri 2.0 데스크탑 앱 (sidecar: FastAPI)
Task 5.3: GitHub Actions CI/CD
Task 5.4: MkDocs 문서 사이트
Task 5.5: Zenodo DOI 등록
Task 5.6: README + Contributing guide
```

---

## 7. 검증 전략

### CatCost 검증 케이스 (User Guide Table 6.2 기반)

| 촉매 | 조건 | CatCost 추정가 | 시장가 | 허용 오차 |
|-----|------|-------------|-------|---------|
| 2 wt% Pt/C | 2 ton, Small scale | $27.37/lb | $34.09/lb | ±20% |
| 21 wt% Ni/Al₂O₃ | 20 ton, Medium scale | $20.59/lb | $21.33/lb | ±20% |
| USY-based FCC | 200 ton, Large scale | $2.41/lb | $2.73/lb | ±20% |

각 Phase 완료 시 이 3개 케이스로 회귀 테스트 실행.

---

## 8. 코딩 컨벤션

- Python: ruff (formatter + linter), type hints 필수, docstring (Google style)
- TypeScript: ESLint + Prettier, strict mode
- 커밋 메시지: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`)
- PR: 기능 단위, 테스트 포함 필수
- 환경변수: `.env.example` 제공, 시크릿은 절대 커밋 금지

---

## 9. 중요 참고사항

### 라이선스 주의
- CatCost는 DOE/NREL 소유, 비상업적 내부 사용 제한
- **방법론 인용은 OK** (학술 논문 기반)
- **데이터 직접 복사는 위험** → 공개 소스에서 자체 수집
- Materials Library 가격은 ICIS public, Sigma-Aldrich, USGS 등에서 독립 수집

### 금속 시세 API 키
- Metals.Dev: 무료 플랜 월 50 요청, 유료 $9.99/월 (1만 요청)
- MetalpriceAPI: 무료 플랜 월 50 요청
- BLS API: 무료 (등록 필요)

### CatCost와의 관계 명시
- README에 "CatCost의 방법론을 학술적으로 인용/활용" 명시
- "CatCost를 대체하는 것이 아니라 보완" 강조
- Baddour 2018, Van Allsburg 2022 논문 인용
