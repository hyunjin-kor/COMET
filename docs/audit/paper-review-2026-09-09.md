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

## H2. 모범 소프트웨어 논문 조사 (2026-09-10, 공개 접근본만)

사용자 요청('논문 수준이 높지 않다, 다른 소프트웨어 논문을 다시 학습해')으로 조사했다. 전문을 읽은 것: AutoDock Vina 1.2.0(PMC10683950), NEXTorch(OSTI 1977906), AI4Green(PMC10207257), ProcessOptimizer(PMC11863379), QSDsan(arXiv 2203.06243), OpenMM 7(PLOS Comput Biol), Psi4 1.4(PMC7228781), pymatgen(eScholarship 30v0j6cc), ASE(DTU Orbit 수리본), Step Method(OSTI 1477947). BioSTEAM과 CatCost 본문은 유료라 초록·기록만 확인했다(확인 못 함).

얻은 판단:

1. 인용 많은 소프트웨어 논문을 가르는 것은 분량이나 그림 수가 아니라 **외부 기준점**이다. Vina는 DUD-E, QSDsan은 MATLAB/Simulink 대비 상대오차 1% 미만, Step Method는 시장 가격 ±20%. 외부 기준점이 없는 논문(AI4Green, Psi4, pymatgen)도 널리 인용되지만 '도구'로 인용되지 '근거'로 인용되지 않는다.
2. 계산 엔진 논문(Vina, NEXTorch, OpenMM, Psi4)에는 화면 캡처가 하나도 없다. 화면을 넣는 것은 웹 ELN 계열뿐이다. 이번에 캡처 도판을 뺀 결정은 관행에 맞는다.
3. 강한 논문은 본문의 3분의 1가량을 사례 하나에 끝까지 쓴다(NEXTorch의 Applications 절 전체가 한 반응기의 두 사례). 우리 원고는 암모니아 분해 사례가 별도 절로 떨어져 있어 기능 소개처럼 읽힐 여지가 있다. 분량 여유가 73 word-equivalent 뿐이라 다른 절을 줄여야 가능하다.
4. **라이선스가 가장 큰 투고 위험이다.** JCIM 저자 안내는 소프트웨어가 학술과 상업 용도 모두 평가 또는 구매 가능해야 한다고 명시한다. PolyForm Noncommercial만으로는 걸리므로 상업 라이선스 문의처·조건을 채우고 투고 전 에디터 확인을 권한다. docx 검토 메모에 별표로 표시했다.
5. 재현성은 조사한 네 논문 중 셋이 약했다(Psi4는 'data sharing not applicable'). 우리 `scripts/reproduce_catcost_table62.py`와 해시 매니페스트는 이 축에서 오히려 앞선다.

확인 못 한 것: BioSTEAM이 Aspen Plus와 맞춘다는 구체 수치, CatCost 본문. 유료 접근이라 보지 않았다.

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
| `be97513` | 도판을 저널 스타일로 다시 그림(사용자 피드백: 칩 버전은 논문 도판 같지 않음, 예시는 유명 촉매로, 반응명 정식 표기, 패널 겹침). Fig. 1은 3c268a2식 층 스택으로 복귀하되 얇은 테두리와 평이한 용어(price sources, price basis, cost model, cost ledger, decision analysis, provenance)로 다시 씀. Fig. 2는 새 `scripts/capture_note_result_screen.py`가 로컬 백엔드(8765, 빌드된 프런트)에서 Playwright로 캡처한 20 wt% Ni/Al₂O₃ 추정(초기습윤 함침 템플릿, 20 t, live tier, 5.21 USD/lb) 화면에 주석 6개. Fig. 3은 FAMILY_NAMES 사전의 정식 반응명, Arial mathtext 아래첨자, 넓힌 오른쪽 열. 노트 본문·캡션을 새 예시로 갱신 | `--check` CHECK_OK, ruff, 노트 테스트 2 passed, CI 34345735835 success(3 job) |
| `0a40f61` | 사용자가 matplotlib Fig. 1을 거부하고 ChatGPT 이미지 생성으로 4종(A 층 스택, B 등축, C 선화, D 일러스트)을 만들게 함 → D 채택, 그림 안 글자 제거·cm² 수정·오른쪽 아이콘 태그 패널로 재생성(D2), 연결선은 저자 요청대로 수평 점선으로 스크립트 수정. `fig1_workflow_stack.png`(최종)·`fig1_workflow_stack_raw_chatgpt.png`(원본)·`fig1_workflow_stack.provenance.md`(프롬프트 전문, 정책, 권리)·`scripts/straighten_note_fig1_leaders.py`(원본→최종 바이트 동일)를 커밋하고 SVG 삭제. 캡션과 AI 사용 문장에 ACS AI 정책(캡션 설명 + Acknowledgments 기술, TOC 그래픽 금지)대로 공개 | `--check` CHECK_OK(4,567 word-equivalent), ruff, 노트 테스트 2 passed, CI 34423057204 success(3 job) |
| `4cd50cb` | 사용자 요청(Fig. 2·3을 더 낫게, Fig. 3은 네이처 스타일)으로 재설계. Fig. 2: 캡처 스크립트가 쓰는 JSON 사이드카(`screen_result_ni_al2o3.json`)에서 입력 요약 카드 4개(조성·템플릿·규모·가격 계층)를 그리고, 헤더를 잘라낸 결과 화면에 주석 5개(CSV 주석 삭제). 캡처는 2026-09-10 live 시세로 갱신(5.213 USD/lb). Fig. 3: (a) 반응군별 기준 1위·최강 경쟁자·나머지의 1위 비율 누적 막대, (b) 검사별 생존 반응군 수(과반 19, 후보 제거 21, ±2 20, ±5 10, ±10 7 / 30), (c) 암모니아 분해 예시 덤벨. 캡션 갱신 | `--check` CHECK_OK(4,570 word-equivalent), ruff, 노트 테스트 2 passed, CI 34426414121 success(3 job) |
| `4cf9443` | 사용자 결정: 실제 화면 캡처 대신 방법론을 도식화한 도판으로. Fig. 2 = (a) 입력→재료비 C_m=Σw_i c_i → Step Method C_p=24·T·I·ΣH_j/M → 간접비·마진 P=(C_m+C_p)(1+g)(1+s)/(1−m) → 장부 도식, (b) 20 wt% Ni/Al₂O₃ 예시의 판매 단가 워터폴(Ni 1.51, Al₂O₃ 0.62, 가공 1.68, G&A 0.19, S&ARD 0.20, 마진 1.01 → 5.21 USD/lb; 캡처 JSON 사이드카), (c) 09-08 동결 니켈 월평균(IMF PCPS)+2026-05 기준값 8.52+2026-09-10 live 7.56+89개월 재생 구간. 본문 예시 숫자는 `ex()` 키 참조(총 53개). 캡처 도판 파일 삭제, 캡처 스크립트는 사이드카에 materials·step_method를 기록. 런칭 배너(`docs/assets/hero-banner.webp`)는 AI 생성 이미지·워드마크 포함이라 저널 도판에 쓰지 않음 (2026-09-11 정정: 당초 'Claude Opus 5가 만든 이미지'라고 적었으나 틀렸다. 커밋의 Co-Authored-By는 커밋을 쓴 주체일 뿐이고, Claude는 2026-08-28 세션에서 프롬프트만 썼으며 이미지는 사용자가 외부 도구로 생성해 2026-08-30 세션에 붙여 넣은 것이다. 생성 도구는 ChatGPT, 2026-09-11 사용자 확인) | `--check` CHECK_OK(4,665 word-equivalent), ruff, 노트 테스트 2 passed, CI 34431773733 success(3 job) |
| `2f84d55` | 사용자 요청((a)는 더 논문답게, (c)는 귀금속까지 연도별 USD로). Fig. 2a: 재료비·가공비를 병렬 상자로 두고 화살표에 C_m·C_p·P를 표시한 흐름도로 다시 그림, 설명 문구는 상자 안에 두 줄로. Fig. 2c: 09-08 동결 패키지의 Pt·Pd·Rh·Ru·Ir·Au·Ag·Ni 월평균(Johnson Matthey, IMF PCPS) 소형 다중 패널, 각 패널에 2026-05 기준값(청록)과 패키지의 live 시세(주황, 2026-09-04~06 관측), 89개월 재생 음영. 캡션에 b의 예시는 2026-09-10 니켈 시세를 썼음을 명시 | `--check` CHECK_OK(4,665 word-equivalent), ruff, 노트 테스트 2 passed, CI 34436195544 success(3 job) |
| `8119167` | 사용자 지적('컴공 용어라 AI티가 난다')에 따라 원고·도판·한글판의 용어를 이 분야 관행어로 전면 교체. price tier→price basis(현물 spot / 기준월 monthly average), ledger→cost breakdown, decision diagnostics→sensitivity analyses, weight sweep→weighting sensitivity, price replay→historical repricing, candidate-removal control→leave-one-out test, score perturbation→score sensitivity, rubric→criterion, reference winner→candidate ranked first at the reference conditions, joint→combined, input hashes→checksums, renderer→user interface. 제목도 'Reproducible Decision Diagnostics'→'Reproducible Sensitivity Analysis'. Fig. 1은 레이아웃을 그대로 두고 라벨만 바꿔 재생성(Provenance→Traceability 등), 연결선 스크립트는 좌표 하드코딩 대신 원본에서 밴드·패널·태그를 측정하도록 재작성해 재생성본에도 적용됨 | `--check` CHECK_OK(4,699 word-equivalent), ruff, 노트 테스트 2 passed, CI 34439163441 3개 job success |
| `c8b1ff9` | 사용자 요청(예시 촉매 하나로 충분한가, 상용 가격 대비 정확도와 반응별 원가 구성을 보여 달라, 한글판도 달라). Fig. 2를 4패널로 확장: (b) 동결 `all_families_2026-09-08.json`에서 열촉매 반응군 23개 각각의 최저 원가 후보 판매 단가 구성(재료비·가공비·간접비와 마진), (c) `table62_reproduction_2026-09-08.json`의 발표된 시장 가격 대비 검증(Pt/C −19.7%, Ni/Al₂O₃ −9.9%, FCC 2.4380 vs 2.73 USD/lb), (d) 금속 8종 가격 기준. 검증 절에 시장 가격 비교 문단 추가(발표된 Step Method 추정값도 비슷하게 아래에 있으므로 차이는 채택 원가 경계의 성질). 도판 스크립트에 `--lang ko` 추가(Malgun Gothic, 반응군·금속·라벨 한글 사전), Fig. 1 한글판은 라벨만 한국어로 재생성 후 같은 연결선 스크립트 적용(밴드 검출에 얇은 틈 병합 추가) | `--check` CHECK_OK(4,857 word-equivalent), ruff, 노트 테스트 2 passed, CI 34442951805 3개 job success |
| `351dbd7` | 사용자 지적(수식이 이상하다, '무료' 표현을 빼라). Arial에는 진짜 이탤릭 수학 글꼴이 없어 matplotlib이 가짜 이탤릭으로 그리고 있었음 → mathtext를 stixsans로 바꿔 변수 이탤릭·합 기호를 정상화하고, 가공비 식을 H=Σ_j H_j로 묶어 분수로 다시 씀. 초록의 'free desktop and browser software'와 가용성의 'permits free noncommercial use'에서 free 제거(한글판 '무료' 2건 포함), 원고 전체 free 0건 | ruff, `--check` CHECK_OK, 노트 테스트 2 passed, CI 34444961066 |
| `25b9247` | 사용자 지적(점 두 개가 겹쳐 뭘 뜻하는지 모르겠다, 쓸모없어 보인다). 옳은 지적이었음: (c)는 로그 축이라 10~20% 차이가 점 굵기에 묻혔고 (d)의 기준월·현물 두 점은 차이가 몇 %라 같은 자리에 찍혔음. (c)를 시장 가격 대비 차이 막대(COMET vs 발표된 추정값)로, (d)를 금속 시세 대신 **도구 출력의 변동**(열촉매 28개 반응군 1위 후보를 89개월 각 시점에서 재산정 후 기준월로 나눔, CO₂ 전기환원 ×6.2 ~ 프로판 탈수소 ×1.0)으로 교체. 검증 절에 원 Step Method 논문의 ±20% 시장 가격 일치 주장을 추가(OSTI 공개본 원문에서 직접 확인, 시장 가격 출처는 업계 전문가 개인 교신) | `--check` CHECK_OK(4,927 word-equivalent), ruff, 노트 테스트 2 passed, CI 34445604299 3개 job success |
| `59c15ed` | 사용자 요청(대상 공정을 다 비교하고, 시간에 따라 촉매 경제성이 달라지는 것을 보이라). 조건이 일치하는 공개 상용 가격은 여전히 3건뿐이므로 **가격 대 가격 오차표 대신 외부 거래 가격대**를 붙였다. 새 `scripts/fetch_catalyst_price_history.py`가 UN Comtrade 무료 무인증 preview 엔드포인트에서 HS 3815 네 개 소호(381511 니켈계, 381512 귀금속계, 381519 기타, 381590 비담지)의 미국 월별 수입 단가를 모아 `docs/paper/catalyst_market_2026-09-10.json`으로 동결(요청 356건, 채택 303건, 거부 53건은 중량이 추정치로 표시되었거나 값이 0 이하인 HTTP 200 응답). Fig. 2d를 열촉매 반응군 23개의 1위 후보를 89개월 각 시점에 재산정한 값 대 대응 소호 거래 단가 비교로 교체(활성 성분 분류: 니켈 4, 귀금속 3, 기타 16). 본문에는 범주 시장 밴드이지 조성이 일치하는 오차가 아니라고 명시 | `--check` CHECK_OK(4,994 word-equivalent), ruff, 노트 테스트 2 passed, CI 34457291361 success(3 job) |
| `2cd36f6` | 사용자가 Fig. 1에서 빨간 박스로 표시한 네모 얼룩은 AI 그림의 결함이 아니라 **내 연결선 스크립트가 패널의 둥근 모서리 위에 채움색을 칠하고 테두리를 지운 것**이었다. 스터브 지우기를 패널이 최대 폭인 행으로 제한해 수정(수정 후 모서리 픽셀 0개 변경). 프로베넌스 문서의 저자 수정 기술도 같이 고침 | 재생성 후 모서리 픽셀 diff 0. CI 34464235445는 다음 푸시로 취소됨(cancelled), 같은 트리는 34464892079에서 success |
| `14b4c96` | 원고에 TOC 그래픽이 없는데 Acknowledgments는 이미 '그래픽 초록에 AI를 쓰지 않았다'고 적고 있었음. `scripts/draw_note_toc_graphic.py`로 3.25×1.75 in, SVG+300 dpi LZW TIFF+PNG, 영문·한글판 제작. ACS가 TOC에는 AI 이미지를 금지하므로(캡션이 없어 설명할 자리가 없다) 전부 직접 그렸고 AI 픽셀은 한 점도 쓰지 않았다 | ruff, 파일 6종 생성, CI 34464892079 success(3 job) |
| `426d679` | TOC 그래픽 다듬기. 고정 시드 난수와 기각 샘플링으로 다공성 펠릿을 그리고, 범례 순서를 누적 막대와 맞추고, 범위 끝값을 캡슐 아래로 내리고, 추정값을 마커 옆에 붙임. GPT가 만든 TOC 시안을 따라 그리자는 내 제안은 사용자 지적('재구성을 해서 괜찮은건가?')대로 철회했다. AI 렌더를 옮겨 그리면 파생물이 되고, 파생물이면 공개해야 하며, TOC에는 공개할 자리가 없다 | ruff, 재생성 일치, CI 34467441092 success(3 job) |

최종 노트 분량: 초록 174 + 본문 3,020 + 그림 3×600 = 4,994 word-equivalent(한도 5,000), JSON 키 참조 57개, 표 0개. TOC 그래픽은 한도 밖 별도 제출물이다.

### H3. 표지 후보 (2026-09-10~11, 커밋하지 않음)

사용자 요청('GPT랑 제미나이로 조합해서 만들자, PPT에서 재조합해서 새로운 이미지로, 전체 저널 규정에 맞춰서')에 따라 표지 후보를 만들었다. 먼저 규정을 정리해 사용자에게 알렸다: **PPT에서 재조합해도 AI 이미지는 AI 이미지다.** ACS 규정은 회피가 아니라 공개를 요구하며, 공개할 자리가 없는 곳은 TOC 그래픽뿐이다. 따라서 Fig. 1(이미 공개함)과 표지(캡션에 공개)는 AI 사용이 허용되고, TOC는 계속 직접 그린 것만 쓰며, Fig. 2·3은 데이터 도판이라 대상이 아니다.

2026-09-11 사용자 질문('표지 아트를 AI 조합이 가능하면 깃허브에 있는 이미지 써도 되잖아')에는 **된다**고 답했다. 조건은 ACS 표지 지침(Supplementary Cover Images, 2026-05-07 갱신, 공개 PDF)에서 확인했다. 로고·상표가 금지이므로 배너의 COMET 워드마크와 부제를 지워야 한다. 이미 README에 공개된 그림이라 '미발표 원작 권장' 항목과는 어긋나지만 권장일 뿐 금지는 아니다. 같은 문서의 저널별 표에서 JCIM 표지 규격은 8.19×7.70 in(제목 오버레이 표기 없음)이었으므로, 처음 가정했던 세로 8.5×11 in 후보와 그 파일은 폐기했다.

- 원본: ChatGPT(PSID_KHU 계정, 1254×1254)·Gemini(사용자 계정, 1024×1024) 렌더 각 1장과 저장소 배너 무손실본(`cc77db3`, 2172×724)을 `_local/note-figures/ai-renders/`에 그대로 보관.
- `_local/note-figures/compose_cover_candidates.py`가 두 후보를 2457×2310 px, 300 dpi로 합성한다. A는 GPT 펠릿이 화면 전체를 채우고 Gemini 입자 꼬리(구체와 우하단 표식을 뺀 크롭, 반전·타원 페이드 후 17° 회전)가 꼬리를 오른쪽 위로 잇는다. B는 배너에서 글자 상자를 지운 뒤 x≥880 영역(혜성·꼬리·분자 4개)을 2.1배 확대·24° 회전해 핵을 (1760, 1500)에 두고, 배경 별은 확대로 흐려지지 않게 시드 20260906으로 새로 그린다. 모든 층을 밝기 기반 투명도 PNG와 `cover_layers.json`으로 내보내 PPT에서도 합성본과 같은 모습으로 쌓이게 했다(이전 PPT는 층의 검은 배경이 아래 층을 가리는 결함이 있었다).
- `_local/note-figures/build_cover_pptx.py` → `cover_composition.pptx`: 후보별 층 슬라이드, 합성본 슬라이드, 원본 3장.
- 글자 제거 검증: 두 글자 상자를 최종 층 좌표로 사상해 알파를 쟀다. 워드마크 상자는 최대 0, 부제 상자는 최대 55/255·99백분위 0·평균 0.01(가장자리 번짐 몇 픽셀). 그 영역을 4배 밝힌 크롭에서도 글자 형태는 없다.
- 품질: 구 내부 라플라시안 분산은 A 131, B 73이다. 처음 B에 넣은 unsharp mask는 이 값을 148로 부풀리고 원본 질감을 과장해서 뺐다. B의 고리 모양 입자와 분화구 안 격자 무늬는 배너 원본을 1:1(최근접 3배 확대)로 봐도 보이므로 합성 과정에서 생긴 것이 아니다. 없애려면 고해상도 재생성이 필요하다.
- 정정: 위 `4cf9443` 행과 메모리에 배너를 'Claude Opus 5가 만든 이미지'라고 적은 것은 틀렸다. 2026-08-28 세션에서 Claude는 프롬프트만 썼고, 사용자가 외부 도구로 만든 이미지를 2026-08-30 세션에 붙여 넣었다. 생성 도구는 ChatGPT(OpenAI)라고 사용자가 2026-09-11에 확인했다.
- `_local/note-figures/cover_art.provenance.md`에 프롬프트 전문, 도구·날짜·계정, 합성 방법, ACS 표지·AI 규정, 후보별 제안 캡션 문구를 적었다.
- 확인 못 함: 배너에 실제로 쓰인 프롬프트 변형, OpenAI(두 후보)·Google(A)의 이용약관(상업적 이용·출력물 소유), Gemini 파일의 비가시 워터마크, 표지 비용 여부. 표지를 낼지는 사람이 정한다.
- 사용자 결정(2026-09-11): B를 논문에 소프트웨어 소개용으로 넣을 수 있는지 물어, 규정상으로는 가능(그림 캡션·Acknowledgments 공개, 금지는 TOC뿐)하지만 분량이 4,994/5,000이라 그림 하나(1단 300, 2단 600 word-equivalent)를 넣으려면 본문을 그만큼 줄여야 하고, 데이터·방법이 없는 그림은 심사에서 불리하며, Acknowledgments의 'Fig. 1 외에는 쓰지 않았다' 문장도 고쳐야 한다고 설명했다. 사용자는 **표지로만** 쓰기로 했다. 원고·그림·Acknowledgments는 바꾸지 않았다.

### H4. 저자 블록과 v1.4.0 릴리스 요청 (2026-09-11)

- 사용자가 저자 순서와 교신저자를 정했다. 제출용 docx(`_local/`, 추적 안 함)의 저자 블록을 사용자 본인의 기존 원고에서 가져온 소속·연락처로 채웠고, 공개 저장소의 원고 md와 이 기록에는 이름·연락처를 넣지 않았다(개인정보 커밋 금지 원칙).
- 보내기 전 확인에서 v15가 v14의 Word 검토 메모 6개를 잃은 것을 발견했다. 본문·그림은 v15가 최신 원고와 같았으므로(변환 결과 바이트 일치, 그림 md5 일치) 메모만 옮겨 붙인 v16을 만들고, v17에서는 저자 문단 하나만 바꾸고 저자 메모를 '정리됨'으로 갱신했다. 옮겨 붙이는 스크립트(`_local/docx/carry_review_comments.py`)는 모든 메모가 문단 하나에만 맞아야 저장한다.
- 사용자가 v1.4.0 전체 릴리스를 지시했다. 먼저 확인한 결과 `release.yml`의 데이터 권리 게이트(`scripts/check_data_rights.py --purpose public_distribution`, 매니페스트 `docs/commercial/data-rights-2026-09-07.json`)가 로컬에서 exit 1, 데이터 파일 81개에 걸쳐 405건(공개 배포 미승인, 검토자·검토일·근거 없음)으로 실패한다. 태그를 밀면 워크플로가 이 단계에서 멈춰 설치본·GitHub Release·Zenodo 버전이 만들어지지 않는다. 게이트는 `c2a17d1`(2026-09-07)에 들어왔고 v1.3.24에는 없었다. 권리 검토는 사람의 판단이므로 매니페스트를 대신 채우거나 게이트를 우회하지 않았고, 병합·태그·릴리스는 하지 않았다.
- 같은 날 재확인: GitHub 최신 릴리스 v1.3.24(2026-08-31), Zenodo 개념 기록의 최신 버전 v1.3.24(10.5281/zenodo.22213096), `package.json`·`frontend/package.json`·`pyproject.toml` 1.4.0(준비 버전).

### H5. 참고문헌 보강과 커버레터 갱신 (2026-09-11)

교수님 결정을 기다리는 동안 결정과 무관한 부분만 고쳤다. Availability(버전·문의처), Competing interests, 연구비 문구는 그대로 두었다.

- 참고문헌 8편 → 14편. 소프트웨어가 실제로 쓰는 가격 출처 네 곳(Johnson Matthey PGM 가격 페이지, Westmetall 시장 데이터, IMF PCPS, UN Comtrade)을 원고가 처음 언급하는 자리에 인용했다. 가격 출처 추적이 이 소프트웨어의 핵심인데 원고가 출처를 하나도 인용하지 않고 있었다. 서론에는 09-09 Crossref 확인을 거친 촉매 합성 원가 연구 2편(Gkika & Kyzas 2025, Ferdous et al. 2025)을 넣었다. 번호는 첫 등장 순으로 다시 매겼다(1–14, 목록 전부 인용됨을 검사).
- 출처 URL 접근 확인(2026-09-11, 자동 요청): Johnson Matthey·Westmetall은 200이고 본문이 읽힌다. UN Comtrade Plus는 200이지만 브라우저 앱 껍데기만 와서 내용은 자동으로 확인하지 못했다. IMF 안내 페이지 두 곳은 403(Access Denied)이어서, 소프트웨어가 호출하는 IMF SDMX 데이터 서비스 주소를 인용했다(데이터플로 200, 이름 'Primary Commodity Price System (PCPS)'; 니켈 시계열 200, 61 KB).
- 분량을 유지하려고 세 곳을 줄였다: 가격 화면의 빠른 조회 설명, 니켈 예시의 설명 문장, 테스트 수 괄호 '(907 at the time of writing)'. 마지막 것은 오늘 수집 기준 909개라 이미 낡은 숫자였다. 공용 검사기는 인용 태그 `<sup>n</sup>`의 'sup'까지 단어로 세므로 인용 하나가 3단어로 잡힌다. 합계는 4,994 word-equivalent로 그대로다.
- 한글판 초안(`_local/`)에 같은 변경을 반영했다. 영어에 없던 '무료 공개 무역 통계'의 '무료'도 지웠다(사용자 지시: 무료 표현 금지).
- 커버레터(손으로 쓴 초안)를 현재 원고에 맞췄다: 옛 제목('Reproducible Decision Diagnostics'), 'free', 'tiers', 'weight sweeps·price replays·candidate-removal controls·score-perturbation', 'renderer', '4,494 word-equivalents'를 고쳤다. '산업 원가 정확도는 검증되지 않았다'는 서술은 발표된 시장 가격 대비 비교와 무역 통계 비교가 들어간 현재 원고에 맞게 바꾸되, 새 조성의 오차는 계산하지 않았다는 점은 유지했다. 공개 경로는 저자 결정 대기로 표시했다.
- 검증: `--check` CHECK_OK(4,994), 인용 첫 등장 순서 1–14, 노트 테스트 2 passed, `python -m ruff check` 통과.

확인 못 한 것과 하지 않은 것:

- 저자·소속·연구비·이해관계 문구·상업 라이선스 문의처·심사용 버전(v1.4.0 태그 여부)은 원고에 placeholder로 남아 있으며 사람이 정해야 한다.
- JCIM의 SCIE 수록과 IF는 제3자 자료로만 확인했다. JCR 원본 확인은 사용자 몫이다.
- 연구실 V8 양식 docx(영문·한글판, Word 검토 메모 6개)와 Gemini·ChatGPT 참고 렌더 6장은 `_local/`에 두고 추적하지 않는다. 원고 도판은 matplotlib 벡터본만 쓴다.
- 상용 촉매 가격과의 비교는 CatCost 표 6.2에 함께 실린 시장 가격 3건이 전부다. 조건이 일치하는 다른 상용 가격 관측은 찾지 못했으므로 반응군 전체에 대한 오차표는 만들지 않았다. Fig. 2b는 모델 출력이지 실측 원가가 아니다.
- 본문의 예시 숫자는 실행 시점의 현물 시세에 따라 달라지므로 바이트 단위로 재현되지 않는다. 커밋한 JSON 사이드카(`screen_result_ni_al2o3.json`)가 도판과 본문의 입력이고, 캡처 스크립트는 만드는 방법의 기록이다. 같은 이름의 PNG는 참고용 화면이며 원고에는 쓰지 않는다.
- Fig. 1은 AI 생성 그림이라 생성 스크립트로 재현되지 않는다. 원본 PNG와 프롬프트 전문, 저자 수정 스크립트를 함께 커밋해 검증 가능하게 했다. ACS AI 정책은 공식 페이지에서 읽었고(2026-09-10), OpenAI 이용약관의 출력물 권리 조항은 자동 요청이 차단돼 확인 못 했다(저자 확인 항목).
- 투고·외부 연락·태그·릴리스·병합은 하지 않았다.
