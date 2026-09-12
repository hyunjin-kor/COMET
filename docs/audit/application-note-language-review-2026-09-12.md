# Application Note 문장·용어 검토 기록 — 2026-09-12

검토 기준은 `f880c2f`의 영문 원고, 한글 원문, 네 그림과 캡션이다. 사용자가 지적한 문제는
단순한 격식의 부족이 아니라, 임의로 조합한 명칭·불완전한 라벨·불명확한 지시 대상·내부 개발
표현이 논문에 남아 있다는 점이다. 제목부터 참고문헌까지 순서대로 읽고 수정한 뒤, 계산의
의미와 수치가 유지되는지 별도로 대조했다. 아래 P 번호는 개정 전 생성 템플릿의 문단 번호다.

문체 선택은 편집 판단이다. 대체 표현을 모두 해당 분야의 확립된 전문용어라고 주장하지 않는다.
전문용어와 계산 정의는 기존 코드·동결 자료 또는 인용한 원문에서 확인하고, 나머지는 대상을
직접 설명하는 문장으로 썼다. 공개된 [JCIM Application Note](https://pmc.ncbi.nlm.nih.gov/articles/PMC8630643/)도
비교해서 읽었지만 문구를 가져오거나 새 참고문헌으로 추가하지 않았다.

## 제목·본문·캡션 전수 검토

| 위치 | 검토 후 처리 | 이유와 확인 기준 |
|---|---|---|
| P00 제목 | `Software for Catalyst Manufacturing Cost Estimation and Sensitivity Analysis` | 기능을 직접 기술하고 중첩된 수식어를 줄임. COMET 명칭 유지. |
| P01 저자란 | 자리표시자 유지 | 실제 저자 정보는 로컬 원문에만 보존. |
| P02·05·09·15·23·33·37·39·41·44·46 절 제목 | 읽고 유지 | 절의 내용과 일치하는 명칭. |
| P03 초록 | 목적·계산 방법·입력·산출물·검증 범위의 순서로 재작성 | `agrees to the reported cent`, `cost basis`, `price-source records`와 같은 압축 표현을 정리. |
| P04 핵심어 | 원가 추정·민감도·다기준 분석 중심으로 정리 | `price traceability` 등 수식적인 표현보다 실제 연구 내용을 표시. |
| P06 도입 1 | Step Method의 입력과 판매 단가 계산을 설명 | 문헌의 방법을 COMET의 새 수식으로 제시하지 않음. |
| P07 도입 2 | 가격일·공정 경계·기능 단위의 비교 문제를 구체화 | `inventory-coverage measures` 대신 무엇의 비율인지 명시. |
| P08 도입 3 | 기능과 이 논문에서 제시하는 분석을 설명 | 기여를 선언하는 문장과 `universally preferred catalyst` 같은 추상적 결론 제거. |
| P10 구현 개요 | 다섯 계산 단계와 보존 정보를 기술 | `software organization`, `supply the cost model`의 모호한 연결을 해소. |
| P11 Figure 1 캡션 | 계산 흐름·기록의 의미와 재작성 이력을 설명 | 그림의 설명 문구를 캡션으로 옮기고 AI 사용 이력을 실제 작업에 맞춤. |
| P12 실행 환경 | 로컬 저장·런타임·검증 플랫폼·오프라인 조건을 구분 | `installable`, `complete browser-mode testing` 등 개발 문구 정리. API 첫 등장에 풀어 씀. |
| P13 원가 예시 | 현물 시세를 사용한 저장 계산임을 명시 | 현재 시세와 동결 월평균 사례의 혼동 방지. 수치 참조 네 개 유지. CSV 정의. |
| P14 Figure 2 캡션 | 기호·단위·후보 선택·분모·출처 정의 보완 | G&A·SARD·HS·FCC·USY·SCR을 정의. H·T·I·M의 의미와 단위 명확화. |
| P16 재료비 | 전구체·소모재의 소요량 계산으로 설명 | `purchased-input recipe`, `retained-component yield`를 명칭으로 쓰는 대신 f·p·y를 물리적으로 정의. |
| P17 가공비 | 준비 절차·조작·규모·간접비·이윤 순서로 서술 | `cleaning allowance`, `selling-margin correlation`의 연결을 풀어 씀. SARD 원문 확인. |
| P18 환경성 | 재료·공정 기여와 질량 반영률 정의 | 질량 반영률을 전체 환경 영향의 반영률로 오해하지 않도록 구분. |
| P19 가격 절 제목 | `Price data and sources` | 필요한 내용을 직접 나타냄. |
| P20 가격 자료 | 현재 시세·월평균·수입 단가를 구분 | `support-material HS series`를 품목 코드별 자료로 설명. IMF·PCPS·HS 정의. |
| P21 가격 신뢰도 | evidence가 가격 자료의 신뢰도임을 명시 | 촉매 성능의 근거와 혼동 방지. 재료비 비중으로 가중한다는 코드 정의 확인. |
| P22 Figure 3 캡션 | 월별 가격과 최대/최소 비율을 직접 기술 | `retained record`, `frozen inputs`, `historical repricing`의 개발 문구를 줄임. |
| P24 후보 순위 | 조성 근거와 네 평가 기준을 설명 | `literature-architecture proxies`, `engineering proxies`, `route-readiness`를 설명 없이 사용하지 않음. 경로 점수의 평균 계산 확인. |
| P25 개별 민감도 | 가중치·과거 가격·몬테카를로 분석을 구분 | 단체 격자의 조건 정의. `monthly price states`, `single-metal break-even prices`를 실제 계산 의미로 설명. |
| P26 결합 민감도 | 시나리오·점수 차이·후보 제거·점수 변화 절차를 설명 | `family-month-weight scenarios`, `score regret`, `least favourable corner`, 잔여 `leader` 표현 제거·정의. 점수 변화는 route·performance에만 적용됨을 명시. |
| P27 저장 결과 비교 | 원래 결과와 공통 가정 재계산을 구분 | `saved-case`류 명칭 대신 비교 동작 설명. |
| P28 검증 절 제목 | `Verification and reproducibility` | 구현 확인과 독립적인 산업 검증을 구분. |
| P29 문헌 재현 | 계산값·문헌값·차이·적용 조건을 명시 | `COMET gives ... versus ...`를 완전한 문장으로 정리. |
| P30 시장·무역 비교 | 추정값의 편차와 비교 자료의 한계를 설명 | `formulation-matched validation errors`, `reference-leading`, `unity` 등을 명료하게 기술. |
| P31 검증 해석 | 구현 검증과 새로운 조성의 오차 평가를 구분 | `bounds the error`, `condition-matched industrial observation`을 풀어 씀. |
| P32 재현성 | 테스트·체크섬·환경·난수 사용 여부를 설명 | 결정론적 열거에 난수 시드가 필요한 듯한 표현 제거. 저장한다는 사실과 재현을 돕는다는 의미를 구분. |
| P34 암모니아 사례 | 비용·가중치·종합 점수·빈도를 설명 | 원가와 economics, 가격 신뢰도와 evidence의 의미를 일치시킴. |
| P35 순위 역전 | 후보 제거→범위 축소→점수 변화의 관계를 기술 | `cobalt composite`, `economic-score difference` 등 생략된 명사를 보완. |
| P36 Figure 4 캡션 | 각 색과 테스트의 집계 기준을 설명 | 대안 후보의 선택 기준, 두 점수의 변화 방향, 0–100 제한, 다섯 반응 약어 정의. |
| P38 한계 | 관측 부족·점수 가정·환경 범위·사용 단계 제외를 기술 | `unestimated`, `adopted empirical method`, `external validity of rankings`를 구체적인 제한으로 표현. |
| P40 공개 안내 | 버전·라이선스·접근 방법의 확인 상태를 구분 | 미공개 버전과 파일이 이미 공개된 것처럼 쓰지 않음. 공개/상용 결정을 대신하지 않고 자리표시자 사용. |
| P42 연구비 | 저자 작성 자리표시자 유지 | 없는 지원 사실을 만들지 않음. |
| P43 AI 고지 | 이전 생성 그림과 현재 코드 도식을 구분 | 새 원고를 사람이 이미 최종 검증했다고 주장하지 않음. 최종 검증 책임을 명시. |
| P45 이해상충 | 진술문 작성 자리표시자로 정리 | 회사 관계·권한 확인을 요구하는 내부 작업 지시를 본문에서 제거. 기존 계획은 로컬 저자 결정 기록에 보존. |
| P47 참고문헌 1–14 | 제목·서지·DOI를 검토하고 원문 유지 | 인용 문헌의 제목을 임의로 윤문하지 않음. 아래 참조. |

## 그림의 모든 문구 검토

| 그림 | 처리 |
|---|---|
| Figure 1 | 다섯 단계와 보존 정보만 남겨 코드로 다시 그림. `Electrode per cm²`, `grade per line`, `partial LCA`, `Leave-one-out test` 등의 불완전한 설명을 제거. 세부 내용은 본문·캡션에 배치. 현재 PNG·SVG 모두 같은 생성기에서 출력. |
| Figure 2 (a) | 조성·가격·절차·주문량·재료비·가공비·판매가 라벨과 세 수식을 대조 후 유지. 식의 연결은 H13의 확정 배치. |
| Figure 2 (b) | 23개 반응명·원가 항목·축·단위를 읽고 유지. 약어는 캡션에서 정의. |
| Figure 2 (c) | 비교 대상을 `Baddour et al.`로 표시. 세 촉매명과 편차의 정의 대조. |
| Figure 2 (d) | 축을 `Estimated price / import unit value`로 명시. 세 범주·코드와 기준 후보 범례 확인. 결측 표시는 H14 수정 유지. |
| Figure 3 | 두 금속 범주, 14개 원소 기호, 가격·날짜 축과 단위 확인. 한글 `일반 금속`은 `비귀금속`으로 수정. |
| Figure 4 (a) | `Leading alternative`를 `Alternative candidate`로 바꾸고 선택 기준은 캡션에 명시. `First-rank frequency`는 `Frequency of ranking first`로 표시. 30개 반응명 검토. |
| Figure 4 (b) | `Joint share`, `Top rank retained (families)`를 제거. 시나리오의 ≥50%에서 1위라는 기준, 점수 변화, 반응군의 수를 직접 표시. |
| Figure 4 (c) | 두 후보의 의미, 아홉 반응명, 비용 단위와 로그 축 확인. 동결 기록의 아홉 사례 모두 $/lb 비교임을 대조. |

## 출처·참고문헌 확인

- SARD는 [Baddour 등의 공개 원문](https://www.osti.gov/servlets/purl/1477947) 3쪽에서
  sales, administrative, research, and distribution costs로 정의된다. 6쪽 표 주석도 일치한다.
  따라서 `S&ARD`를 `SARD`로 고쳤다. 원문 2쪽의 USY 정의도 확인했다. 로컬 엔진 주석의
  `R&D` 설명은 이 원문의 풀어쓴 말과 다르지만, 계산이나 논문 밖의 코드는 이번에 바꾸지 않았다.
- 참고문헌 1·2·3·4·5·6·11·12·13·14의 DOI 10개는 무료 Crossref API에서 레코드를 조회했다.
  각 DOI와 제목을 확인했다. 첫 조회에서 2·4번은 HTTP 429였으며 시간을 두고 순차 재조회하여
  확인했다. 실제 응답은 `_local/language-review-2026-09-12/crossref.json`에 보존한다.
- 13번의 온라인 공개일과 권·호의 발행 연도는 서로 다를 수 있으므로 온라인 날짜만으로 원문의
  권·호 연도를 바꾸지 않았다. 나머지 문헌의 제목·권·호·쪽 범위와 제공된 표기를 대조했다.
- 7–10번은 데이터 제공 사이트다. 기관·서비스·접근일의 표기를 검토했으며, 이번 작업에서
  그 접근일을 새 방문일로 바꾸거나 수집 데이터를 갱신하지 않았다.
- CatCost 사용자 안내서의 새 다운로드는 DNS 오류로 **확인 못 함**이었다. SARD와 USY의
  정의는 대신 실제로 내려받은 위의 논문 원문에서 확인했다. 문헌의 원자료는 재배포하지 않는다.

## 확정 전 남는 항목

공개/상용 배포 방식, 버전별 접근 경로, 실제 이해상충·연구비 진술은 저자 결정이 필요하다.
종전 계획은 `_local/language-review-2026-09-12/author_decisions.md`와 인수인계 §8에 보존했다.
이 기록은 저자의 결정을 대신하거나 외부 공개를 승인하지 않는다. Word의 실제 페이지 검토도
렌더러 부재로 아직 완료하지 못했다. 수치·그림·분량·재생성 검증 결과는 주 감사 기록 H16에 남긴다.
