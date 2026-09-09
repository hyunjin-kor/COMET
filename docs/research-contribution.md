# COMET의 연구 기여와 근거

COMET은 촉매 제조 원가·환경 영향·의사결정 분석을 연결하는 독립 개발 소프트웨어다. 연구 기여는 가격과 제조 조건을 추적하고, 산정 범위가 드러나는 비교를 구성하며, 추천이 어떤 가정에 의존하는지 재현 가능한 분석으로 확인하는 데 있다.

CatCost와 공개 Step Method는 선행연구이자 채택한 원가 산정 근거다. COMET의 설명은 해결하려는 연구 문제와 자체 구현에서 시작하며, 사용한 기존 식·단가·계수와 데이터의 출처는 해당 근거에 명시한다. 아래의 미해결 질문은 이 연구가 다루는 문제이며, 선행 도구에 모든 관련 기능이 없다는 주장이 아니다.

## 연구 질문에서 구현과 검증으로

| 연구에서 해결할 문제 | COMET의 방법과 소프트웨어 기여 | 구현·분석 근거 | 해석의 범위 |
|---|---|---|---|
| 시세가 다른 날의 원가를 같은 조건처럼 비교하기 어려움 | 실무용 live와 고정 월 reference 기준을 분리하고, 원자료·시점·입력 해시를 결과에 연결 | [가격 기준](methodology.md#price-basis), [재현 실행 기록](paper/submission-2026-09-08/reproduction_manifest_2026-09-08.json) | 무료 공개 가격과 수입 단가는 특정 등급의 구매 견적을 보장하지 않음 |
| 제조 경로의 비용 누락과 규모 가정이 총액에 가려짐 | 제조 단계의 반복·규모별 장비 치환·미산정 공정·실효 생산 속도와 원료 투입량을 드러냄 | [실무 원가 방법](methodology.md#practical-costing-inputs-and-saved-case-comparisons), [제조 조건 통제 사례](paper/controlled-2026-09-08/controlled_cases.json) | 채택한 시간당 단가와 규모 경계는 실측 장비 성능이 아니며 미산정 공정의 단가를 유도하지 않음 |
| 분말과 전극을 서로 다른 기능 단위로 비교할 위험 | 열촉매는 질량, 완전한 전극 조립체는 면적으로 비교하고 입력이 부족한 전극 후보군은 분말 기준을 명시 | [전극 사용법](getting-started.ko.md#전극-조립체-계산), [비교 단위 수정 근거](audit/research-numerical-delta-2026-09-08.json) | 면적·질량이 같아도 반응 성능이나 수명이 같다는 뜻은 아님 |
| 낮은 환경 영향과 부족한 환경 자료를 혼동함 | 재료·공정 기여와 계수가 연결된 질량 반영률을 함께 제시 | [환경 영향 산정](methodology.md#life-cycle-assessment), [현재 분석 요약](paper/submission-2026-09-08/paper_summary_2026-09-08.json) | 부분 목록에 대한 선별 평가이며, 사용 단계와 누락된 담체·소모품을 포함한 완전한 LCA가 아님 |
| 추천이 바뀌었을 때 가격·근거·선호 중 원인을 구분하기 어려움 | 가격 값과 출처 평가의 통제 비교, 가격 이력×가중치 분석, 후보 제외와 평가 점수 민감도를 연결 | [통제 사례](paper/controlled-2026-09-08/controlled_cases.json), [추천 안정성 분석](paper/robustness-2026-09-08/decision_robustness.json), [공유 순위 정책](../backend/core/decision_engine.py) | 조건부 모델 분석이며 미래 승률이나 실험으로 확인한 성능 우위가 아님 |
| 서로 다른 입력의 추정·실적을 정확도처럼 합산할 위험 | 저장한 조성을 공통 조건으로 재계산하고, 구매 근거·실제 비용은 조건 일치 여부와 함께 보관 | [비교·실적 API](api-reference.md#saved-complete-estimate-comparison), [실적 입력 규칙](methodology.md#local-purchase-and-actual-cost-evidence) | 사용자가 기록한 근거와 외부 독립 검증은 구분하며, 부적격 항목은 오차 평균에 포함하지 않음 |

## 채택한 선행 방법과 자체 기여의 경계

| 구분 | 이 프로젝트에서의 위치 |
|---|---|
| 공개 Step Method와 CatCost의 열촉매 시간당 단가·간접비·판매 마진 | 채택한 원가 산정 근거. 기존 식과 단가의 출처를 유지한다. |
| CatCost User Guide Table 6.2 | 공개된 방법의 재현 검증. 새로운 촉매의 산업 원가 정확도를 검증하는 실측 자료와 구분한다. |
| 설비비·운영비 계수와 회수 가치 가정 | 인용한 계수·가정에 따른 선별 추정. COMET이 실험으로 새로 측정한 계수로 소개하지 않는다. |
| COMET의 가격 상태·산정 범위·기능 단위·순위 분석을 연결하는 절차 | 이 연구가 명시하고 구현한 방법론 기여. 사용한 일반 수학 기법 자체의 최초 발명은 주장하지 않는다. |
| 라이브러리 가격·문헌 후보·환경 계수 | 항목별 실제 출처와 적용 범위를 유지한다. 소프트웨어 독립 개발과 데이터의 독립 수집·재사용 허락은 별개다. |

[Baddour 등의 공개 Step Method](https://doi.org/10.1021/acs.oprd.8b00245)와 [Van Allsburg 등의 CatCost 연구](https://doi.org/10.1038/s41929-022-00759-6)는 원가 산정의 선행 근거다. [BioSTEAM](https://biosteam.readthedocs.io/en/latest/) 등에도 공정·원가·환경·불확실성 분석이 존재하므로, 통합이나 민감도 분석 자체를 최초 기여로 주장하지 않는다. 이 실행의 접근·서지 확인은 [출처 확인 기록](sources/positioning-prior-work-2026-09-08.json)에 남긴다.

## 제품과 논문에 사용할 설명

> COMET은 촉매 제조 원가, 부분 환경 영향과 후보 비교를 함께 다루는 독립 개발 소프트웨어다. 기존 원가 산정 연구를 바탕으로 가격 출처와 제조 조건을 추적하고, 비교 단위와 산정 범위를 명시하며, 추천의 안정성을 재현 가능한 분석으로 확인하는 방법론을 구현했다.

> COMET is independently developed software connecting catalyst manufacturing cost, partial environmental inventories and reproducible decision analysis. Building on established costing research, its methodology links traceable price states, explicit manufacturing boundaries and functional-unit-aware comparisons to diagnostics of recommendation robustness.

현재 원고와 SI는 [논문 자료 안내](paper/README.md)에서 찾는다. 모델 재현과 자동 시험은 확보했으나, 조건이 일치하는 독립 산업 원가 관측과 실제 연구자 평가가 아직 부족하다. 기존 [권리 검토표](commercial/rights-register-2026-09-07.md), 라이선스와 배포 조건은 이 설명 변경으로 달라지지 않는다.

2026-09-09 보완: [선행연구 8개 대조](sources/paper-methods-prior-work-2026-09-09.md)에 원가를 이용한 합성 개선과 정규화에 따른 순위 역전의 선례를 명시했다. [추가 방법 검증](paper/methods-2026-09-09/README.md)은 구매량·MC·실제 후보 제외 사례를 원고/SI의 수식에 연결한다. 이는 기존 계산식의 새 저작성이나 실측 산업 정확도를 뜻하지 않는다.
