# 실무 원가 계산 개선 최종 보고 — 2026-09-07

다섯 가지 개선과 검증을 마쳤으며 기존 기본 계산과 5월 논문 결과를 보존했습니다. 이번 P01–P06은 **완료 6개·보류 0개·부분 완료 0개**입니다. 누적 T01–T19·D01–D07·V01–V04·P01–P06은 **완료 34개·부분 완료 2개·보류 0개**입니다. 독립 실측 원가 자료의 공백은 그대로 남아 있습니다.

구현 커밋은 `066844e` (`feat: add practical recipe costing and local comparison evidence`)입니다. 같은 `autonomous/2026-09-06` 브랜치와 [PR112](https://github.com/hyunjin-kor/COMET/pull/112)를 유지하며, master 머지·태그·릴리스·외부 배포는 하지 않았습니다. 소스 버전은 릴리스 준비 상태인 1.4.0입니다. `gh release list -L 1`로 이번 실행에서 재확인한 공개 릴리스는 v1.3.24입니다.

## 이번 작업 결과

| ID | 상태 | 커밋 | 근거 명령 출력 요약 | 사용자에게 달라진 점 |
|---|---|---|---|---|
| P01 | 완료 | `066844e` | 산정 범위 테스트 8개, 저장·불러오기·CSV·실제 Chrome 확인 | 실제 산정·대체 장비·미산정 공정을 결과까지 표시. 회수 차감 단가 문구, 전극 가격 줄바꿈, 원가 비중 차트 분모 수정 |
| P02 | 완료 | `066844e` | 실무 입력 관련 테스트 13개, 생산 기간·근거 저장과 화면 확인 | 열촉매 실효 생산 속도를 선택 입력하고 기존 세척 시간을 포함한 생산 기간 계산 |
| P03 | 완료 | `066844e` | 전구체·수율 산술, 중복 가산 방지, 0가격·잘못된 입력, CSV·재로딩 확인 | 구매 전구체 함량·순도·수율과 용매·세척액 순구매량을 재료비에 반영 |
| P04 | 완료 | `066844e` | 저장된 계산 비교 테스트 17개, Chrome에서 2개 계산 비교 | 전체 조성을 유지한 2~4개 계산의 과거 결과·공통 가격·공통 조건을 분리. 가격 출처와 규모 치환 공개 |
| P05 | 완료 | `066844e` | 구매·실적 근거 테스트 32개, 공급사·날짜 왕복 저장, 미적격 견적 제외·MAPE null 화면 확인 | 로컬 구매 근거와 실제 비용을 기록. 조건이 맞는 열촉매 실적만 오차 평가 |
| P06 | 완료 | `066844e` | 전체 pytest 780 passed/423.66s, Ruff·프론트·번역·Node 통과, 동결 입력 회귀 일치; Windows 빌드 193.396s + 스모크 17.228s 통과, 버전 1.4.0·창 1개·가격/계산 HTTP200; [구현 CI 성공](https://github.com/hyunjin-kor/COMET/actions/runs/34080912267) (066844e, backend/frontend; CI pytest 780 passed/512.10s) | 추정 범위 화면에도 새 입력을 전달하고 전체 검증·로그·동일 PR 마무리 |

전체 백엔드는 직전 710개에서 **780개 통과**로 늘었습니다(423.66초, 전체 경과 426.933초). 프론트 `check:i18n`의 누락 키·미번역 UI 라벨은 각각 0개이며 lint/build가 통과했습니다. Node 계산기 규칙 12개와 추정 범위 입력 규칙 6개도 통과했습니다. 실제 Chrome에서 조성 입력, 구매 근거, 전구체·생산 속도, 미산정 공정, 저장·불러오기, CSV, 비교, 전극 면적 단가를 확인했고, 추정 범위 화면도 1,000/1,000회 성공과 기준 계산 11.9234 USD/lb와의 정확한 일치를 확인했습니다. 여섯 흐름의 최종 스크린샷 9장을 저장했고 페이지 오류는 0개였습니다. 추정 범위 CSV에도 고정된 수율·순도·투입량·생산 속도 가정을 표시합니다.

근거 파일은 `docs/audit/` 아래 `practical-costing-2026-09-07.md`, `practical-checks-2026-09-07.json`, `practical-default-regression-2026-09-07.json`, `practical-ui-2026-09-07.json`, `practical-range-2026-09-07.json`에 있습니다. 명령 출력 원문은 같은 폴더의 `practical-*.log`에 보존했습니다.

## 계산 변화와 방법론 재현

새 선택 입력을 사용하지 않으면 기존 수치가 유지됩니다. `ff6155e`를 별도로 추출한 기준 코드와 현재 코드에 같은 2026-05 가격을 넣어 비교했습니다. **30개 반응군·116개 후보·90개 가중치별 순위·성능 가중치 0의 30개 순위에서 차이는 0개**입니다. 현재 코드의 두 실행과 동결 논문 JSON도 바이트까지 일치했습니다. 기본 API의 재료비·공정비·요약·회수 가치·전극·LCA 수치는 같고, 산정 범위 설명만 추가되었습니다. 고정 seed `20260906`의 MC 1,000회·10,000회 결과 JSON도 기준 코드와 정확히 같습니다.

| CatCost Table 6.2 | COMET, USD/lb | 출판값, USD/lb | 판정 |
|---|---:|---:|---|
| Pt/C | 27.3695 → 27.37 | 27.37 | 센트 일치 |
| Ni/Al₂O₃ | 19.2206 | 20.59 | −6.65%, 7% 이내 |
| FCC, 각주 b의 67 short tons/day | 2.4380 | 2.41 | +1.16%, 2% 이내 |

방법론의 시간당 단가·마진 상관식은 바꾸지 않았습니다. FCC 명목 속도 150 short tons/day의 1.6090 USD/lb는 별도 진단값이며 합격값으로 쓰지 않습니다.

새 입력에 따른 변화는 명시적인 질량수지와 생산 기간 계산입니다. 다음은 실제 가격이나 실적이 아닌 **합성 검증 입력**입니다. 최종 Ni 20 wt% / 순수 전구체의 Ni 함량 25% / 순도 80% / 수율 50%이면 전구체 2 kg/kg-catalyst가 필요합니다. 전구체를 5 USD/kg로 입력하면 10 USD/kg-catalyst, 세척액 순구매량 3 kg/kg와 0.5 USD/kg를 입력하면 1.5 USD/kg-catalyst가 반영됩니다. 기존 금속 기준 가격을 여기에 중복 가산하지 않습니다. 20 short tons를 하루 5 short tons로 생산하면 세척 1일을 포함해 5일이며, 기존 기본 속도의 3일보다 가공비가 5/3배가 됩니다.

원가 비중 차트는 서로 다른 분모를 섞던 표시를 바로잡았습니다. 합성 사례에서 150%로 보이던 합계가 판매 단가 기준 100%가 되었으며, 원가 계산식은 바뀌지 않았습니다. 회수 차감 단가는 판매 마진을 포함한 단가에서 회수 가치를 뺀 값으로 설명합니다.

## 성능 전후

| 측정 | 기준 `ff6155e` | 현재 | 관측 변화 |
|---|---:|---:|---|
| `/api/calculate` 20회 중앙값 | 2.539 ms | 2.591 ms | +2.0% |
| MC 1,000회 | 0.0730 s | 0.0794 s | +8.7% |
| MC 10,000회, 2회 중앙값 | 0.4362 s | 0.5542 s | **+27.1%** |
| `run_all_families.py` | 1.907 s | 1.774 s | −7.0% |

동일한 합성 API 입력·seed와 동결 5월 가격을 사용했습니다. 다른 검증이 함께 실행된 워크스테이션 관측이며, 독립적인 성능 개선 실험은 아닙니다. 특히 MC 10,000회는 시간이 늘었고 그 원인을 따로 분리하지 않았습니다. 이번 변경을 최적화 성과로 주장하지 않습니다.

## 기존 작업과 남은 자료 공백

원래 T01–T19는 완료 상태이며, 무료 자료 보완 D01–D07과 세 우선순위 V01–V04를 합한 기존 집계는 완료 28개·부분 완료 2개였습니다. 기존 개별 커밋·명령 근거와 이전 시점의 수집 결과는 아래 원본 표 및 누적 로그에 보존합니다.

<details>
<summary>기존 T01–T19 작업 표 — 당시 결과 보존</summary>

| ID | 상태 | 커밋 | 근거 명령 출력 요약 | 메모 |
|---|---|---|---|---|
| T01 | 완료 | 06b33e3, 84d416f | All four baseline signals passed; outputs above | 필수; Draft PR #112 |
| T02 | 완료 | 87a4791 | Browser thermal/electrode HTTP 200; calculate median 4.15 ms, MC10000 2.812 s; 104 raw JSX/2 missing keys; 1,520 structural objects without direct source | 필수; 2026-09-06-baseline.md |
| T03 | 완료 | 9d08443 | 23 targeted passed; full 605 passed; frontend lint/build passed; browser reference review 18 to 0 | Publication month and fixed anchors; live review age 7 days |
| T04 | 완료 | a8e4597 | 7 focused passed; same seed both request shapes equal; two full family JSON outputs byte-identical; full605 passed | Default seed None replaces implicit42; deterministic score/cost/slug order |
| T05 | 완료 | f8ab863 | 17 focused passed; full pipeline completed; fresh14-series input; hashes/environment captured; full605 passed | Final data regenerated under T16; README and methodology command documented |
| T06 | 완료 | ccfedb6 | 80JSON,3046objects;317/317Crossref;467URLs:287ok,179unverified,1notfound; ruff passed | No source price corrected; Mo23.13 retained; exhaustive status evidence |
| T07 | 완료 | 3001c1b | 28 thermal methods x3 scales API parity; native Node9 passed; full605 and frontendlintbuild pass | Explicit card ID; repeated operations retained; catalog 28+custom+5electrode documented |
| T08 | 완료 | f0ed93e | Node defaults and poisoned-thermal ledger assertions pass; real PEM browser HTTP200 and area ledger verified | Application/template default table; area ledger matches headline; thermal campaign/margin hidden |
| T09 | 완료 | afc1615 | 27 focused tests pass; actual public feeds retrieved; Pt/Pd JM and Cu/Al Westmetall verified; Yahoo300s | Source deltas and full selected snapshot recorded; optional paid feeds not invoked |
| T10 | 완료 | 88bab31 | 38/83 support entries linked;20 focused pass;synthetic90 profile cases; frozen paper has noHS observations so values unchanged | 45 ambiguous entries explicitly unlinked; immutable fixed-price fallbacks |
| T11 | 완료 | 74175cb | 18 focused tests; exact seeded MC JSON equality; final MC10k 0.4188 s vs paired 2.4119 s (5.76x); Table 6.2 unchanged | mtime/size cache and row-major batched RNG; final performance evidence supersedes intermediate run |
| T12 | 완료 | 60c0588 | Methodology error-budget table cites exact price bounds, index inputs, 1/10/150 vs 67 t/day, recovery defaults, LCA gaps and uncosted routes | Prose landed with T05 (f8ab863); validated against regenerated summary and SI; no invented aggregate error bar |
| T13 | 완료 | b93c62d | Clean coverage run 625 passed in 347.52 s; backend/core 94%, every module at least89%; 20 provider HTTP contract tests added | pytest-cov temporary environment only; check:i18n and CI wiring land with T14 translations to keep intermediate CI green |
| T14 | 완료 | e209ff1 | check:i18n 781 calls/822 keys,0 missing/0 untranslated; frontend lint/build and Node9 pass; 3 real browser flows200; 11 README screenshots regenerated | Data text unchanged; Korean guide added; reference review0; capture failures and initial422 recorded honestly |
| T15 | 완료 | 300fbf7 | All4 versions1.4.0; final desktop build156.36s and smoke200/one window; total172.41s; latest public release remains1.3.24 | Prepared metadata, notes and checklist only; isolated junction packaging issue recovered with unchanged-lockfile npm ci |
| T16 | 완료 | ea787f0 | Full pipeline2026-07/seed20260906;14series91months; six PNG/SVGfigures; 26outputs+80data+34code hash checks pass; staged raw SHA preserved | Fresh history fetched; actual live12quote snapshot; latest-common July; live-classification edge tests11 included in final636 |
| T17 | 완료 | e7effeb | Manuscript69+SI980 keys resolve;466 numeric checks;4Crossref citations;165-word abstract; estimated6624 word equivalents; six figures inspected | New3.4/3.5/3.6 and4SI tables; ACS guidelines verified; no invented authorship or version DOI |
| T18 | 완료 | 5365889 | Reviewer checklist plus10 evidence-linked questions/answers; no fabricated performance/coverage/reuse claims | Expected objections cover method reproduction, proxies, sources, LCA, licensing and price reproducibility |
| T19 | 완료 | 0844666 | Final636 passed; ruff, frontend/i18n/Node9, desktop1.4.0, Table6.2 and paper hashes pass; final report prepared | Single PR #112; no merge/tag/release/deployment |

</details>

부분 완료 **D03**은 일부 담체의 적격 관측 공백, **V01**은 조건을 모두 맞춘 독립 제조 원가 실적의 부재입니다. 이를 이번 기능 구현 완료와 혼동하지 않았습니다. 기존 무료 담체 자료 10시계열·28관측값과 2026-05 기준 원고·SI·그림·입력 스냅샷을 보존했습니다. 이번에는 새 가격·LCA 계수·공정 단가를 수집하거나 추가하지 않았고, 유료 자료·과금 API·구독·키 발급·구매를 사용하지 않았습니다.

실적 기록 기능이 생겼지만 **산업 전체 제조 원가에 대한 독립 정확도 검증은 여전히 없습니다**. 사용자 확인은 독립 검증이 아니며, 가격·조성·등급·규모·생산 속도·제조 단계·비용 범위가 맞지 않는 기록은 보관만 합니다. 전극과 실제 투입량을 대조하지 못한 전구체·소모품 계산은 현재 오차 평균에서 제외합니다. 적격 사례가 없을 때 MAPE는 `null`입니다.

## 가정한 것

- 실효 생산 속도는 기존 엔진과 같은 short ton/day를 사용하고, 생산 기간은 세척 시간을 포함해 계산합니다. 서로 모순될 수 있는 별도 기간 입력은 만들지 않았습니다.
- 전구체 함량·순도·수율·구매 가격은 근거와 함께 명시적으로 입력합니다. 물성·수율·누락 가격을 추정하지 않고, 전구체 가산계수의 중복 적용을 막았습니다.
- 용매·세척액은 완제품 질량당 순구매량입니다. 자동 회수율·폐수 처리비를 만들지 않았습니다. 전구체·용매 입력이 기존 LCA의 누락 인벤토리를 채웠다고 간주하지 않습니다.
- 비교에서는 기준 계산의 공통 조건을 사용하되 조성·수율·제조 경로 차이는 유지합니다. 과거 결과와의 차이를 순수 가격 효과, 다른 조성의 차이를 순수 제조법 효과로 부르지 않습니다.
- 같은 이름이라도 서로 다른 라이브러리 항목·등급은 같은 구매 조건으로 단정하지 않습니다. 같은 재료의 가격을 치환할 때 공급사·날짜 근거도 함께 옮깁니다.

## 확인하지 못한 것과 사람이 할 일

- 새 live 가격 수집 성공, 전체 담체의 7·8월 발표 상황, 장기 담체 변동성, 미접근 원문·SI의 제조 조건은 이번 실행에서 새로 확인하지 않았습니다.
- 일반 탄소·실리카·제올라이트 LCA 계수, 탄소흑 적격 가격 관측, 미산정 공정 단가는 공백을 유지했습니다. 라이선스 파일과 CatCost 원본 워크북의 비재배포 조건도 유지했습니다.
- 사람은 PR112와 최종 CI를 검토한 뒤 별도로 master 머지를 결정하고 태그 `v1.4.0`을 푸시해야 합니다. 실제 릴리스 설치 파일과 이전 버전의 자동 업데이트를 확인해야 합니다.
- Zenodo 버전 DOI와 concept DOI `10.5281/zenodo.21451931` 연결을 확인하고, 저자·소속·연구비·이해상충·최종 분량·커버레터 및 ACS Sustainable Chemistry & Engineering 투고 승인을 확정해야 합니다.
- D03·V01의 후속 보완과 미산정 공정·LCA 공백의 우선순위를 결정해야 합니다. 후속 자료도 무료로 검증 가능한 경우에만 반영합니다.


## 감사와 검증 범위

- 시작점은 깨끗한 `ff6155e1b56d1e400438fbcb5a4f40dea06e605e`였습니다. 이전 실행의 710 passed/459.11초와 Windows build+smoke 197.81초를 이번 검증 결과와 구분했습니다. 첫 로그 커밋은 `68ddbf3`, 기능 커밋은 `066844e`입니다.
- 독립 변경 검토에서 데이터·라이선스·의존성 명세/잠금 파일·DB 모델/마이그레이션·기존 논문 산출물·독점 워크북 변경과 파일 삭제는 없었습니다. 추가 줄의 인증정보·개인 키·파괴적 SQL 패턴 검사는 0건이었습니다. 이 검사를 완전한 보안 인증으로 확대하지 않습니다.
- 기존 차트 분모와 단가 줄바꿈 외에, 추정 범위 페이지가 새 입력을 누락하던 전달 경로를 함께 고쳤습니다. 전구체 가격의 0값 경고, 모호한 라이브러리 이름/등급, 불명확한 비용 범위가 실측 오차 평가에 들어갈 수 있는 경계 조건도 테스트로 고정했습니다.
- 브라우저 보조 검사에서는 한국어 버튼 선택자, 접힌 실적 입력 영역, 선택 항목까지 포함한 라벨을 잘못 찾은 경우를 바로잡았습니다. 서로 다른 하위 검사에서 생긴 선택자 문제이며 앱 예외는 없었습니다. 최종 전체 흐름을 다시 통과했고 중간 실패 스크린샷도 보존했습니다.
- Node 검사 자체가 통과한 뒤 Windows cp949 출력에서 체크 기호를 인쇄하지 못한 보조 실행기를 UTF-8로 고쳤고 다시 통과했습니다. 기존 Tailwind sourcemap 경고와 PyInstaller의 미사용 모듈 경고는 성공한 빌드의 원문 로그에 남겼습니다. 원문 로그 끝의 빈 줄은 그대로 보존했으며 이를 제품 코드의 공백 검사 통과로 포장하지 않습니다.
- 성능 측정 보조 스크립트는 `_local`에 있습니다. 제출 JSON에는 입력·명령·환경·소스/입력 해시·관측 시간이 있지만, 새 체크아웃에서 그 보조 스크립트를 그대로 실행할 수는 없습니다. 영구 회귀 테스트와 `run_all_families.py` 및 동결 입력은 저장소에 있습니다.
- 구현 커밋의 CI 성공을 위에 기록했습니다. 이 최종 보고·실행 로그만 추가하는 다음 커밋도 푸시 후 CI를 확인하고, 정확한 최종 head와 실행 링크는 PR본문에 기록합니다. 보고 파일만 바꾸며 검사를 무한 반복하지 않습니다.
