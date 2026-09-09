# 논문 독립 검토 — 2026-09-09

Codex 인계분을 독립 검토자 입장에서 대조한 기록이다. 기준 커밋 `1492e7f65eb9b109791d1b2ff0db9af6e1f11ad2`, 브랜치 `autonomous/2026-09-06`, PR #112. 검토 대상은 현재 원고·SI(2026-09-08 파일명)와 생성기, 재현 스크립트, 핵심 엔진 코드다. 소프트웨어 기능 확장은 하지 않았고, 확인된 결함과 원고 불일치만 수정했다.

## 인계 상태 확인

| 항목 | 확인 결과 |
|---|---|
| 작업 폴더·브랜치 | `C:/Users/user/Desktop/COMET-autonomous-2026-09-06`, `autonomous/2026-09-06`; `C:/Users/user/Desktop/COMET`은 별도 체크아웃으로 건드리지 않음 |
| HEAD·원격 | `1492e7f` = `origin/autonomous/2026-09-06`; 작업 트리 깨끗; 인계 후 추가 커밋 없음 |
| PR #112 | OPEN, Draft 아님, MERGEABLE, head `1492e7f` |
| CI 34304006679 | desktop·backend·frontend 모두 success |
| `methods_study.json` SHA-256 | `3e0334cae853187259e65d147375c1e2b68361b42b8cd9a75dd6682bbf9725ca` (인계값과 일치) |
| 버전 | `package.json`·`frontend/package.json`·`pyproject.toml` 1.4.0; `gh release list -L 1` → v1.3.24 (2026-08-31). 1.4.0은 준비 버전 |
| 기준월·시드 | manifest `basis_month` 2026-05, seed 20260906 |

## A. 독립 감사 결과

### A1. 코드와 원고 수식의 대조

| 원고 기술 | 코드 위치 | 판정 |
|---|---|---|
| $P_{\rm selling}=(C_m+C_p)(1+g)(1+s)/(1-m)$ (SI S9) | `step_method.py`: `ga = subtotal·g`, `sard = (subtotal+ga)·s`, `margin = pre_margin·m/(1−m)` | 일치. $(1+g)(1+s)$ 순차 적용과 마진의 판매가 기준 정의가 식과 같음 |
| $C_{\rm processing}=HIT/M$ | `hourly_total·chemppi·24·campaign_days / total_production_lb` | 일치 |
| $a_i=w_i/(f_i p_i y_i)$, $\sum q_jP_j$ | `recipe_costing.py` | 일치. markup≠1과 recipe 동시 사용 거부도 기술과 일치 |
| $E_i=100(c_{\max}-c_i)/(c_{\max}-c_{\min})$, 1자리 반올림 | `decision_engine._economic_scores` | 일치. 단, 원문 "Equal costs receive the same maximum economics score"는 `spread ≤ 1e-9`인 전원 동일 원가 경우만 해당 → 문장 수정 (R04) |
| 종합 점수 1자리 반올림, 동점은 기능 단위 원가→slug | `_apply_total_scores`, `rank_candidates` | 일치 |
| MC: 그룹별 독립 균일 계수, 그룹 내 공유, 실패 사유 보고, 전부 실패 시 거부, 규모 변경 시 장비 치환 | `uncertainty.run_cost_request_monte_carlo`, `_sample_steps` | 일치 |
| Rubric 상자 검사의 "worst corner" 논리 | `rubric_audit` | 타당. 각 후보 총점은 자기 점수에 단조·타 후보와 독립이고, 반올림도 단조이므로 corner에서 1위 유지 ⇒ 상자 전체에서 유지. 동점 규칙(원가·slug)은 상자 내부에서도 같음 |
| 정규화 예제 수치 89.3→77.4, 87.3→87.3 | `methods_study.json:normalization.example` | 재현 일치 (아래 D) |

수치 정합: 1771 = C(23,3), 286 = C(13,3), 4,728,570 = 89×1771×30, 86 = 116−30, 83+29+4 = 116, SI Table S2 28개 제조법, Table S1 116행. Table 1 잔차 −0.00183%는 (27.3695−27.37)/27.37이다.

### A2. 참고문헌 Crossref 확인 (2026-09-09, 무료 API, 계정·결제 없음)

| 번호 | DOI | 응답 | 서지 대조 |
|---|---|---|---|
| 1 | 10.1021/acs.oprd.8b00245 | 200 | OPRD 2018, 22(12), 1599–1605 일치 |
| 2 | 10.1038/s41929-022-00759-6 | 200 | Nat. Catal. 2022, 5(4), 342–353 일치 |
| 3 | 10.1021/acssuschemeng.9b07040 | 200 | ACS SCE 2020, 8(8), 3302–3310 일치 |
| 4 | 10.1002/adsu.202300030 | 200 | Adv. Sustain. Syst. vol 8, issue 10, art. 2300030; online 2023-04-25, print 2024-10 → 항목을 "2024, 8 (10), 2300030"으로 정리 (R03) |
| 5 | 10.1007/s41981-024-00342-z | 200 | J. Flow Chem. 2025, 15(1), 21–38 일치 |
| 6 | 10.1371/journal.pone.0101298 | 200 | PLoS ONE 2014, 9(7), e101298 일치 |
| 7 | 10.1002/mcda.1806 | 200 | JMCDA 2023, 30(5-6), 163–172 일치 |
| 8 | 10.1787/9789264043466-en | 200 | OECD 2008, book, 기관 저자 일치 |
| 9 | 10.1021/acssuschemeng.5c06752 | 200 | ACS SCE 2025, 13(41), 17370–17379 일치 |
| 10 | 10.1039/d5cy00189g | 200 | Catal. Sci. Technol. 2025, 15(15), 4419–4429 일치 |

인용 순서(첫 등장 순)와 SI의 "main reference 4" 대응도 확인했다.

### A3. 저널 형식·지표 (무료 공식 자료만)

- ACS Engineering Au 저자 안내(`researcher-resources.acs.org/publish/author_guidelines?coden=aeacb3`): HTTP 200. Article 초록 300단어 이내, Letters 2,200단어, TOC 3.25×1.75 in, AI 도구 사용은 Acknowledgments에 시점·방법과 함께 공개(저자 자격 없음), 완전 OA·APC 필요(기본 CC BY-NC-ND), 마지막 갱신 2026-08-27. 현재 원고(초록 197단어, TOC 규격, Acknowledgments의 AI 공개)는 이 항목들에 부합한다.
- 저널 홈페이지(`pubs.acs.org/engineeringau`): HTTP 403. JIF·CiteScore·JCR 분위는 **확인 못 함**. 사용자의 Q1·IF 8–15 목표 부합 여부는 미확정으로 유지한다. 유료 DB는 사용하지 않았다.

### A4. 발견한 원고·생성기 불일치와 코드 결함

| ID | 위치 | 문제 | 조치 |
|---|---|---|---|
| R01 | Data and code availability | 재생성 명령에 `--methods-study`가 없고 다음 문단에서 "추가로 넘기라"고만 함. 명령을 그대로 실행하면 현재 원고와 다른 문서가 생성됨 | `paper_methods_text.py`에서 명령에 옵션을 삽입하고, 대상 문자열이 없으면 오류로 중단 |
| R02 | 참고문헌 8 (OECD) | 서지 항목 안에 편집 주석("Crossref and JRC bibliographic identity checked; ...")이 포함됨 | 항목에서 제거. 확인 기록은 `docs/sources/robustness-methods-2026-09-08.md`에 그대로 남음 |
| R03 | 참고문헌 4 (Petel) | "(published online 2023)" 주석과 호수 누락 | Crossref 기준 "2024, 8 (10), 2300030" |
| R04 | Methods, 정규화 | "Equal costs receive the same maximum economics score"가 두 후보 동가격을 뜻하는 것으로 읽힘. 코드는 전원 동일 원가일 때만 100 | "When every candidate in the set has the same cost, each receives the maximum economics score." |
| R05 | Results, break-even | 생성값 1에 대해 "Only 1 crossings lie" | 생성기에 단복수 분기 추가 → "Only 1 crossing lies" |
| R06 | Introduction | "desktop and web software"가 호스팅 서비스로 읽힐 수 있음(공개 endpoint 없음) | "desktop and browser-based software" |
| R07 | Conclusions | "Materials dominate reported GWP"가 모델 공정 경계(전구체 분해열·NOx·용매 등 제외) 조건을 생략 | "Within the modelled process boundary, ..." |
| R08 | Acknowledgments | AI 지원 공개에 이번 편집 주체 누락 | "OpenAI Codex and Anthropic Claude assisted with ... manuscript drafting and editing." (저널 안내의 AI 공개 요건) |
| R09 | `docs/methodology.md` | 2026-09-07 `--check` 명령이 현재 생성기에서 실패함(직접 실행: `Generated submission file differs: manuscript_2026-09-07.md`) | 현재 09-08 명령으로 교체하고 과거 초안은 해당 시점 생성기 커밋이 필요함을 명시 |
| R10 | `docs/paper/cover-letter-2026-09-07.md` | 제목이 이전 원고 제목이며 공동 민감도 분석 언급 없음 | 현재 제목으로 교체, 한 문장 추가, 갱신일 표기 |
| C01 | `scripts/run_decision_robustness.py` `removal_audit` | 재정규화 후 `after` 장부의 `scores.total`을 다시 쓰지 않음. 순위는 명시 가중치로 계산되어 정확하지만, "독립 재계산용 장부"의 필드가 제거 전 값을 그대로 가짐. 동결 JSON 250개 after 항목 중 62개가 재계산값과 다름(예: co-mgo-la2o3 89.3 vs 77.4) | `_apply_total_scores(survivors, weights)` 1줄 추가 + 회귀 테스트. 동결 파일은 덮어쓰지 않고 README에 주석 |

R01·R04·R05·R07·R08은 생성된 Markdown이 아니라 생성기에서 고쳤고, 원고를 재생성한 뒤 `--check`로 일치를 확인했다. SI, TOC SVG/TIFF, `submission_metadata_2026-09-08.json`은 바이트 변화가 없다. 본문 118개·SI 1,353개 수치 참조와 고정 산출물 27개 검사는 그대로 통과한다.

## B. 변경 파일

| 파일 | 변경 |
|---|---|
| `scripts/run_decision_robustness.py` | C01 수정 (import 1줄, 호출 1줄) |
| `backend/tests/test_decision_robustness.py` | `test_removal_audit_after_ledger_totals_use_recomputed_economics` 추가 (수정 전 코드에서 실패함을 확인) |
| `scripts/build_submission_manuscript.py` | R05·R06·R07·R08 |
| `scripts/research_manuscript_extension.py` | R02 |
| `scripts/paper_methods_text.py` | R01·R03·R04 |
| `docs/paper/manuscript_2026-09-08.md`, `submission_manuscript_checks_2026-09-08.json` | 재생성 결과 (본문 단어 수 3,771→3,788) |
| `docs/methodology.md` | R09 |
| `docs/paper/cover-letter-2026-09-07.md` | R10 |
| `docs/paper/robustness-2026-09-08/README.md` | C01 장부 주석 |
| `docs/paper/README.md` | 이 기록 링크 |

원가식, 추천식, 가격 라이브러리, 고정 분석 패키지, LICENSE, 프론트엔드·Electron 코드는 바꾸지 않았다.

## C. C01의 근거와 재현

```bash
python scripts/run_decision_robustness.py --out-dir _local/robustness-replay-2026-09-09-baseline --seed 20260906   # 수정 전 스크립트
python scripts/run_decision_robustness.py --out-dir _local/robustness-replay-2026-09-09-fixed --seed 20260906      # 수정 후 스크립트
```

| 산출물 | 수정 전 재현 vs 동결본 | 수정 후 재현 vs 동결본 |
|---|---|---|
| `decision_robustness.json` | 바이트 일치 (`1b3cf44a…`) | 62개 leaf만 차이, 모두 `families[*].candidate_removal[*].after[*].scores.total`; `summary` 동일 |
| `candidate_robustness.csv` | 바이트 일치 | 바이트 일치 (`36156c9d…`) |
| `decision_robustness.png` | 바이트 일치 | 바이트 일치 (`9c64caa0…`) |
| `decision_robustness.svg` | 바이트 일치 | 바이트 일치 (`d7aeab1d…`) |

수정 후 재현의 62개 항목은 모두 네 성분 점수와 균형 가중치로 재계산한 값과 같다. 동결 패키지의 `provenance.json`은 당시 스크립트 해시를 기록하고 있으므로, 현재 스크립트로 재현하면 이 필드에서만 차이가 난다는 사실을 robustness README에 남겼다. 실행 시간은 각각 약 37초였다.

## D. 검증 명령과 실제 결과

| 명령 | 결과 |
|---|---|
| `python scripts/build_submission_manuscript.py --date 2026-09-08 --directory docs/paper/submission-2026-09-08 --robustness docs/paper/robustness-2026-09-08 --methods-study docs/paper/methods-2026-09-09/methods_study.json` (재생성 후 `--check`) | 통과. 본문 118·SI 1,353 키, 고정 산출물 27개 |
| `python -m ruff check .` | All checks passed |
| `python -m pytest backend/tests/test_decision_robustness.py backend/tests/test_paper_methods_supplement.py backend/tests/test_paper_submission_claims.py backend/tests/test_reproduce_paper.py backend/tests/test_reproducibility.py -q` | 42 passed (5.71 s) |
| `python -m pytest backend/tests -q` | 907 passed in 514.57 s (경과 8 m 38 s); 인계 시점 906개 + 신규 회귀 테스트 1개. 로그: `_local/review-full-pytest-2026-09-09.log` (미추적) |
| `python scripts/reproduce_catcost_table62.py` | Pt/C 27.3695 (센트 일치), Ni/Al₂O₃ 19.2206 (−6.65%), FCC 각주 b 2.4380 (+1.16%); 명목 150 t/d 1.6090은 진단값 |
| `python scripts/reproduce_paper_methods.py --out-dir _local/methods-replay-2026-09-09-review` | JSON·PNG SHA-256 동결본과 일치 (2.3 s) |
| 프론트 lint/build/i18n, 데스크톱 빌드·smoke | 실행하지 않음. 프론트·Electron 코드와 의존성을 바꾸지 않았다 |
| 실제 브라우저 UI 검사 | 실행하지 않음. UI 변경 없음 |

## E. 연구 논리에 대한 독립 비평 (이번에 수정하지 않은 구조적 사항)

1. **연구 질문→결론 연결**: 서론의 질문(추천이 가격 상태·경계·후보군·선호 변화에 살아남는가)에 대해 Methods의 각 분석(통제 비교, 가중치 격자, 월별 재생, 손익분기, 공동 열거, 후보 제거, rubric 상자)이 대응하고, 결론은 조건부 모델 결과로 제한되어 있다. 연결은 성립한다.
2. **외부 타당성 부재**: 모든 정량 결과는 저자 구성 라이브러리(116 후보)와 저자 부여 route/performance 점수의 성질이다. 원고는 이를 반복해 명시하지만, 리뷰어는 "이 진단이 실제 선택을 개선했는가"를 물을 것이다. 필요한 근거: 조건 일치 산업 원가 관측(MAPE), 같은 반응 조건의 활성·선택도·수명 대응 자료, 실제 연구자 평가. 현재 0건이며 이는 사람·자료의 문제다.
3. **기여의 크기**: 정규화 순위 역전(9/86)은 알려진 현상의 촉매 사례이고, 통제 비교·공동 열거·상자 검사도 일반 기법이다. 논문의 기여는 "가격 상태·근거·경계·기능 단위·추천 가정을 함께 추적하는 절차와 그 절차로 얻은 진단"으로 정리되어 있고, 최초 발명 주장은 없다. Q1급 저널에서는 이 절차가 실제 결정 사례에서 무엇을 바꾸는지 보여 주는 하나 이상의 실증이 요구될 가능성이 크다.
4. **환경 결론의 조건성**: "materials dominate GWP"는 모델 공정 경계와 54개 적격 후보 부분집합에 한정된다. 결론 문장에 경계 조건을 추가했다(R07).
5. **저널 적합성**: Engineering Au의 작성 요건은 충족하지만 JIF·JCR 분위·APC 지원은 확인 못 했다. 형식은 잠정 상태로 유지한다.

## F. 범위 밖 관찰 (수정하지 않음)

- `backend/core/step_method.py`의 `estimated_price_per_kg`는 907.185를 하드코딩하고, `constants.py`의 `KG_PER_LB` 0.453592로는 907.184다. 상대 차이 1×10⁻⁶ 수준이며 논문 수치는 lb 기준이라 영향이 없다. 상수 통일은 동결 산출물 해시를 바꾸므로 별도 판단이 필요하다.
- `README.md`의 재현 명령은 09-07 입력 파일을 사용한다. 09-08 파일과 SHA-256이 같아(price/support/live/monthly 모두 일치) 결과는 동일하지만, 원고 명령과 파일명이 다르다.
- 이전 날짜 원고(`manuscript_2026-09-07.md` 등)는 현재 생성기로 `--check`가 실패한다. 문서 정책대로 과거 기록으로 두었다.

## G. 가정과 확인 못 한 것

- 인계 보고의 검증 수치는 실제 명령으로 재확인한 범위(원고 검사, ruff, Table 6.2, methods·robustness 재현, 집중·전체 pytest)에서만 사실로 취급했다. Windows 패키징·프론트 검사는 최종 CI 결과로 확인한다.
- 조건 일치 산업 원가 관측, 외부 연구자 평가, 성능·수명 대응 자료, 회사·기관 권리, 원자료 재배포 허락, 저자·지원 과제·이해관계, 투고 저널의 JIF·분위는 여전히 미확정이다. MAPE 미산정은 오차 0%가 아니다.
- 병합·태그·릴리스·Zenodo·배포·결제·외부 연락은 하지 않았다.

## H. 같은 날 후속: JCIM Application Note 투고 준비 기록

A3·E5의 Engineering Au 판단은 사용자 조건(연구실은 SCIE만 실적 인정, ESCI 불가)으로 대체됐다. Digital Discovery(사용자 JCR 확인)와 ACS Engineering Au(제3자 색인 표기, Clarivate MJL은 읽지 못함)는 ESCI로 보고 제외했고, Journal of Chemical Information and Modeling의 Application Note(SCIE, 제3자 IF 6.4; JCR 원본은 확인 못 함)를 준비했다. 선례 AutoDock Vina 1.2.0, NEXTorch, AI4Green, ProcessOptimizer는 Crossref로 DOI를 확인했다. 공식 투고 안내(HTTP 200)에서 확인한 요건: 제목에 소프트웨어명, 초록+본문+그림 5,000단어(그림 300/600 환산), 그림 1개 이상, 학술·상업 모두 평가 또는 구매 가능, 가능하면 OS 무관, 심사자 직접 테스트.

| 커밋 | 내용 | 검증 |
|---|---|---|
| `cdd9acd` | `scripts/build_application_note.py`(동결 09-08 run + robustness + methods study에서 렌더, `--check`), `docs/paper/application-note-2026-09-09.md`, `application_note_checks_2026-09-09.json`, `backend/tests/test_application_note.py`, `cover-letter-jcim-2026-09-09.md`, `submission-brief-2026-09-09.ko.md`, `journal-targets-2026-09-07.md` 부록 | `--check` CHECK_OK, ruff, 노트 테스트 통과 |
| `436bc01` | `scripts/draw_application_note_figures.py` → `docs/paper/figures-note-2026-09-09/` 벡터 도판 3종(계층 스택, 결과 화면 주석, 진단 3패널). 이전 초안은 Preparation Method 캡처(`docs/assets/screen-result.png`)를 결과 화면 캡션으로 쓰고 있어 `screen-cost-estimate-result.png`로 교체 | CI 34331609165 success |
| `3c268a2` | Fig. 1을 Sources→Decision 위→아래 순서, 아래 방향 화살표로 바꾸고 그림 안 제목 제거(캡션이 대신) | CI 34339423351 success |
| `f2cfe56` | 문장 대신 키워드 칩, 번호 원(01–05) 세로 스파인, 출처 필드 사이드 레일, 한 줄 범례로 도판 글자 수 축소. 칩·번호·카드 문법은 사용자의 디자인 아카이브(로컬, 미추적)에서 가져옴 | `--check` CHECK_OK, ruff, 노트 테스트 2 passed, CI 34341046067 success(3 job) |

최종 노트 분량: 초록 171 + 본문 2,523 + 그림 3×600 = 4,494 word-equivalent(한도 5,000), JSON 키 참조 49개, 표 0개.

확인 못 한 것과 하지 않은 것:

- 저자·소속·연구비·이해관계 문구·상업 라이선스 문의처·심사용 버전(v1.4.0 태그 여부)은 원고에 placeholder로 남아 있으며 사람이 정해야 한다.
- JCIM의 SCIE 수록과 IF는 제3자 자료로만 확인했다. JCR 원본 확인은 사용자 몫이다.
- 연구실 V8 양식 docx(영문·한글판, Word 검토 메모 6개)와 Gemini·ChatGPT 참고 렌더 6장은 `_local/`에 두고 추적하지 않는다. 원고 도판은 matplotlib 벡터본만 쓴다.
- 투고·외부 연락·태그·릴리스·병합은 하지 않았다.
