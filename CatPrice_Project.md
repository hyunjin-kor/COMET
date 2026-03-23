# CatPrice — Real-Time Catalyst Cost Estimator

> 촉매 조성을 입력하면 실시간 금속 시세 기반으로 제조원가를 산출하는 오픈소스 도구

## 1. 프로젝트 개요

### 1.1 문제 정의
- CatCost(NREL, v1.1.1 July 2025)는 방법론은 탄탄하나 금속 시세를 사용자가 수동 입력해야 함
- CEPCI/ChemPPI 지수는 업데이트하지만, 실제 Ru/Ni/Co 등 원료 가격은 자동 반영 안 됨
- Excel 기반이라 팀 협업, 모바일 접근, 시각화에 한계
- Evonik CCCT는 자사 제품 편향, 범용성 부족

### 1.2 솔루션: CatPrice
CatCost Step Method 방법론 기반 + **실시간 금속 시세 API 연동** + 현대적 웹/앱 UI
- 어떤 촉매든 조성 입력 → 오늘 기준 제조원가/유통가 즉시 산출
- 금속 가격 변동 추이, 변동성 지표 제공
- TEA/LCOH 시뮬레이션 (선택적 확장)

### 1.3 CatCost와의 관계
- CatCost를 대체하는 것이 아님 → CatCost의 방법론을 인용/활용
- CatCost가 못하는 것(실시간 시세, 현대 UI)을 보완
- CatCost 논문(Baddour 2018, Van Allsburg 2022)을 학술적으로 인용

### 1.4 오픈소스
- License: MIT
- GitHub public repository
- Zenodo DOI (학술 인용용)

---

## 2. 기술 스택

### 2.1 아키텍처

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

### 2.2 기술 선택

| 레이어 | 기술 | 이유 |
|--------|------|------|
| Frontend | React 18 + TypeScript + Vite | 빠른 개발, 생태계 |
| Desktop | Tauri 2.0 | Electron보다 10배 가벼움 |
| UI | shadcn/ui + Tailwind CSS | 깔끔, 커스터마이징 |
| Charts | Recharts + Plotly.js | 인터랙티브 시각화 |
| Backend | FastAPI (Python 3.11+) | async, 자동 API docs |
| Engine | Python (NumPy, Pandas) | 계산 로직 |
| DB | SQLite → PostgreSQL | 가격 이력 저장 |
| Price API | httpx + APScheduler | 비동기 시세 수집 |
| Testing | pytest + Playwright | 백엔드 + E2E |
| Deploy | Docker + GitHub Actions | CI/CD |

---

## 3. 핵심 기능

### 3.1 촉매 가격 계산기 (Core Feature)

사용자가 촉매 조성을 입력하면 실시간 시세 기반으로 제조원가를 산출.

#### 입력 UI
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

#### 계산 로직 (CatCost Step Method 기반)
```python
def calculate_catalyst_cost(composition: CatalystInput) -> CostResult:
    """
    CatCost Step Method (Baddour et al., Org. Process Res. Dev. 2018)
    + 실시간 금속 시세 자동 반영
    """

    # Step 1: 원료비 (Raw Material Cost) — 실시간 시세 적용
    metal_costs = []
    for metal in composition.active_metals:
        live_price = price_db.get_latest(metal.symbol)  # ← 실시간!
        precursor = get_precursor(metal.symbol, metal.precursor)
        # 금속 가격 → 전구체 가격 변환
        precursor_cost = live_price / precursor.metal_fraction * precursor.markup
        metal_costs.append(metal.loading_wt_pct / 100 * precursor_cost)

    support_cost = composition.support_fraction * price_db.get_support(composition.support)
    promoter_cost = sum(p.wt_pct/100 * price_db.get_promoter(p.name)
                        for p in composition.promoters)

    C_raw = sum(metal_costs) + support_cost + promoter_cost

    # Step 2: 제조비 — 합성 방법별 계수
    f_mfg = MANUFACTURING_FACTORS[composition.synthesis_method]  # 1.3~8.0
    C_mfg = C_raw * f_mfg

    # Step 3: 오버헤드 (R&D, 관리, 이윤)
    C_overhead = (C_raw + C_mfg) * composition.overhead_factor  # default 0.30

    # Step 4: 규모 보정
    f_scale = SCALE_FACTORS[composition.production_scale]  # 0.7~50
    manufacturing_cost = (C_raw + C_mfg + C_overhead) * f_scale

    # Step 5: 유통가 추정
    f_dist = DISTRIBUTION_MARKUP[composition.production_scale]  # 1.5~5.0
    retail_estimate = manufacturing_cost * f_dist

    # Step 6: 폐촉매 회수 가치
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

#### 출력 UI
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
│  Spent Recovery:     -$588/kg (Ru회수 95%)           │
│  ──────────────────────────────────                 │
│  ★ Net Cost:         $2,304/kg cat                   │
│                                                     │
│  [📊 Breakdown Chart]  [📈 Price History]  [💾 Export]│
└─────────────────────────────────────────────────────┘
```

---

### 3.2 실시간 금속 시세 (Price Feed)

#### 데이터 소스
| 금속 | 소스 | 빈도 | API/방법 |
|------|------|------|----------|
| Ru, Pt, Ir, Rh, Pd | Kitco / Heraeus | 매일 | 웹 스크래핑 or API |
| Ni, Co, Cu, Zn, Mo | LME | 매일 | LME API or 스크래핑 |
| Fe, rare earths | USGS / World Bank | 매주-매월 | CSV/API |

#### 기능
- 금속별 실시간 가격 대시보드
- 5년 가격 추이 차트
- 변동성 지표 (촉매 비용 불확실성 반영)
- 가격 알림 (임계치 초과 시)
- 가격 이력 DB (시계열 분석용)

#### DB 스키마
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

### 3.3 원료 라이브러리 (Materials Library)

CatCost처럼 내장 라이브러리 제공 + 사용자 추가 가능.

#### 카테고리
- **Metals**: Ru, Ni, Co, Fe, Mo, Cu, Pt, Ir, Rh, Pd, Li, Mn, ...
- **Supports**: γ-Al₂O₃, α-Al₂O₃, SiO₂, TiO₂, CeO₂, MgO, MgAl₂O₄, CNT, SiC, BN, zeolites, ...
- **Promoters**: K₂O, Cs₂CO₃, BaO, La₂O₃, Na₂CO₃, CeO₂, ...
- **Precursors**: RuCl₃, Ni(NO₃)₂·6H₂O, Co(NO₃)₂·6H₂O, H₂PtCl₆, ... (금속분율, 마크업 포함)

#### 가격 소스 우선순위
1. 실시간 API (금속)
2. 사용자 커스텀 입력
3. 내장 기본값 (seed data)

---

### 3.4 비용 비교 & 시각화

- **조성 비교**: 최대 4개 촉매 조성 side-by-side
- **파이 차트**: 원료(금속/담체/촉진제) vs 제조 vs 오버헤드 비중
- **규모 곡선**: lab → pilot → industrial 가격 변화
- **금속 가격 민감도**: Tornado chart (어떤 원소가 가격에 가장 큰 영향?)
- **시계열**: 같은 조성의 제조원가가 금속 시세 변동에 따라 어떻게 변했는지

---

### 3.5 TEA/LCOH 모듈 (Phase 2 확장)

촉매 가격 계산 결과를 TEA에 바로 연결하는 선택적 모듈.
- 촉매 비용 → LCOH 기여도 자동 산출
- 규모별(0.1~100 TPD) LCOH 곡선
- NH₃/H₂/메탄올 등 공정별 TEA 템플릿
- 민감도 분석 (NH₃ 가격, 전기료, 촉매 수명 등)

---

## 4. 프로젝트 구조

```
catprice/
├── README.md
├── LICENSE (MIT)
├── pyproject.toml
├── docker-compose.yml
│
├── backend/
│   ├── main.py                      # FastAPI entry
│   ├── config.py                    # 환경변수, API keys
│   ├── database.py                  # SQLAlchemy
│   │
│   ├── core/                        # 핵심 계산 엔진
│   │   ├── cost_engine.py           # 촉매 가격 계산
│   │   ├── price_fetcher.py         # 금속 시세 수집
│   │   ├── constants.py             # 제조 계수, 열역학 상수
│   │   └── tea_engine.py            # TEA 모듈 (Phase 2)
│   │
│   ├── models/                      # SQLAlchemy DB 모델
│   │   ├── metal_price.py
│   │   └── estimate.py              # 저장된 추정 결과
│   │
│   ├── schemas/                     # Pydantic I/O 스키마
│   │   ├── cost_input.py
│   │   ├── cost_result.py
│   │   └── metal_price.py
│   │
│   ├── routers/                     # API 라우터
│   │   ├── calculator.py            # POST /api/calculate
│   │   ├── prices.py                # GET  /api/prices
│   │   ├── materials.py             # GET  /api/materials
│   │   └── compare.py              # POST /api/compare
│   │
│   ├── data/                        # Seed 데이터
│   │   ├── manufacturing_factors.json
│   │   ├── raw_material_prices.json
│   │   ├── supports.json
│   │   ├── promoters.json
│   │   └── precursors.json
│   │
│   └── tests/
│       ├── test_cost_engine.py      # 계산 검증 (CatCost 결과와 비교)
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
│       │   ├── Calculator.tsx       # 메인: 촉매 가격 계산기
│       │   ├── Prices.tsx           # 금속 시세 대시보드
│       │   ├── Compare.tsx          # 조성 비교
│       │   ├── Library.tsx          # 원료 라이브러리
│       │   └── TEA.tsx              # TEA 모듈 (Phase 2)
│       │
│       └── components/
│           ├── CompositionInput.tsx  # 조성 입력 폼
│           ├── CostBreakdown.tsx     # 파이/바 차트
│           ├── PriceTimeline.tsx     # 금속 시세 추이
│           ├── TornadoChart.tsx      # 민감도 분석
│           └── ScaleCurve.tsx        # 규모별 비용 곡선
│
├── desktop/                         # Tauri 래퍼
│   └── src-tauri/
│       └── tauri.conf.json
│
└── docs/                            # MkDocs
    ├── index.md
    ├── methodology.md               # CatCost Step Method 설명
    └── api-reference.md
```

---

## 5. 개발 로드맵

### Phase 1: MVP (2~3주)
- [ ] `cost_engine.py` — 핵심 계산 로직 (조성→제조원가)
- [ ] `constants.py` — 제조 계수, 규모 계수, 전구체 데이터
- [ ] Seed 데이터 (금속/담체/촉진제/전구체 가격)
- [ ] FastAPI: `POST /api/calculate`, `GET /api/materials`
- [ ] React: Calculator 페이지 (입력 폼 → 결과 + 파이 차트)
- [ ] 금속 가격은 seed data에서 불러오기 (API 연동 전)

### Phase 2: Live Prices (2~3주)
- [ ] `price_fetcher.py` — LME/Kitco 실시간 시세 수집
- [ ] 가격 이력 DB + 스케줄러 (매일 자동 수집)
- [ ] Prices 대시보드 (시계열 차트, 변동성)
- [ ] 계산 결과에 "오늘 시세 기준" 자동 반영

### Phase 3: Advanced Features (3~4주)
- [ ] 조성 비교 모드 (최대 4개)
- [ ] 규모별 비용 곡선
- [ ] 민감도 분석 (Tornado chart)
- [ ] TEA/LCOH 모듈 기본 버전
- [ ] Tauri 데스크탑 앱 패키징

### Phase 4: Community Release (2~3주)
- [ ] Docker compose 원클릭 배포
- [ ] GitHub Actions CI/CD
- [ ] MkDocs 문서 사이트
- [ ] Zenodo DOI 등록
- [ ] README, Contributing guide, Examples

---

## 6. 핵심 데이터 (Seed Data)

### 6.1 제조 비용 계수
→ `catprice_seed_data/manufacturing_factors.json` (이미 생성됨)

### 6.2 원료 가격 DB
→ `catprice_seed_data/raw_material_prices.json` (이미 생성됨)

### 6.3 검증 방법
CatCost의 알려진 예시(ZSM-5, Pt/TiO₂, Mo₂C)와 동일 입력으로 계산해서
±20% 이내 일치 여부를 test case로 작성

---

## 7. API 설계

### 핵심 엔드포인트
```
POST /api/calculate          — 촉매 조성 → 비용 산출
GET  /api/prices             — 전체 금속 최신 시세
GET  /api/prices/{symbol}    — 특정 금속 시세 + 이력
GET  /api/materials          — 원료 라이브러리 (금속/담체/촉진제)
POST /api/compare            — 다중 조성 비교
GET  /api/health             — 서버 상태 + 시세 업데이트 시각
```

### POST /api/calculate 예시
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

## 8. 참고 문헌

1. Baddour et al., "Estimating Precommercial Heterogeneous Catalyst Price: A Simple Step-Based Method", *Org. Process Res. Dev.* **2018**, 22(12). DOI: 10.1021/acs.oprd.8b00245
2. Van Allsburg et al., "Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost", *Nature Catalysis* **2022**. DOI: 10.1038/s41929-022-00759-6
3. CatCost Tool v1.1.1 (July 2025): https://catcost.chemcatbio.org/
4. Peters, Timmerhaus, West, *Plant Design and Economics for Chemical Engineers*, 5th Ed.

---

## 9. Claude Code 사용법

```bash
# 이 파일을 프로젝트 루트에 놓고:
# "CatPrice_Project_Spec.md 읽고 Phase 1부터 구현해줘" 라고 하면 됨

# Seed 데이터는 catprice_seed_data/ 폴더에 이미 준비됨:
# - manufacturing_factors.json (제조 계수)
# - raw_material_prices.json (금속/담체/촉진제/전구체 가격)
```
