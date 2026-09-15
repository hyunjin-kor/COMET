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

### H6. Data and Software Availability 절 (2026-09-11)

- JCIM 투고 요건을 원문으로 확인했다. JCIM 저자 체크리스트(`jcisd8_checklist.pdf`, 2022-11-16)와 2020 사설(*J. Chem. Inf. Model.* **2020**, *60*, 5868; DOI 10.1021/acs.jcim.0c01389, Crossref 확인, 본문은 브라우저로 읽음)은 원고 끝에 별도의 'Data and Software Availability' 절을 요구하고, 없으면 심사 없이 반려한다고 적는다. 라이선스가 필요한 소프트웨어는 심사자에게 한시적 무료 평가 라이선스를 익명으로 제공해야 하고, 데이터는 SI나 공개 저장소, 또는 공개 출처에서 다시 추출하는 스크립트로 제공한다. JCIM은 커버레터 대신 이 체크리스트 양식을 받는다.
- 'Availability' 절을 'Data and Software Availability'로 바꾸고, 소프트웨어 접근 경로에 더해 데이터(동결 가격 스냅샷, 수치·그림의 근거 산출물, SHA-256 manifest, 재생성 명령)의 위치와 공개 출처 재추출 스크립트를 적었다. 이 절과 겹치는 검증 절의 저장소 재생성 문장은 빼고, 'The repository carries'는 'COMET carries'로 바꿨다. 합계 4,994 → 4,991 word-equivalent, `--check`·노트 테스트·ruff 통과. 검토 메모가 붙은 첫 문장은 그대로 두어 메모 위치를 유지했다.
- 사용자 지시(2026-09-11): 2026-09-14 회의에서 정할 때까지 GitHub·Zenodo에 올리지 않는다. 이 커밋부터는 로컬에만 두고 푸시하지 않았다.

### H7. 금속 시세 패널 (2026-09-12)

- 사용자 지적: Fig. 2에서 시세가 움직이는 모습이 니켈 쪽에서만 보이고 귀금속은 드러나지 않는다. 촉매 경제성이 시세에 따라 달라진다는 것이 이 소프트웨어의 존재 이유이므로 패널을 넣었다.
- Fig. 2에 (e) 패널 추가. 동결 `submission-2026-09-08/monthly_history_2026-09-08.json`의 금속 14종 월평균(2019-01~2026-05, 89개월)을 일반 금속 7종(USD/lb)과 귀금속 7종(USD/troy oz) 두 로그 축에 나누어 그리고, 선 끝에 원소 기호와 최고/최저 배수를 적었다. 라이브러리는 가격이 붙은 14종을 모두 쓴다(후보 수 Al 31, Ni 21, Cu 17, Pt 14, Co 11, Ru 10, Mo 8, Zn 8, Pd 8, Ag 7, Ir 5, Au 4, Sn 4, Rh 2).
- 기록 안에서의 변동 배수: Rh 11.6, Ru 6.8, Ag 6.2, Ir 5.3, Mo 4.8, Au 3.9, Co 3.8, Sn 3.6, Pt 3.2, Pd 3.1, Ni 2.9, Cu 2.7, Al 2.5, Zn 2.3.
- 그림 높이를 205 → 248 mm로 늘리고, 기존 (a)~(d) 패널과 패널 문자는 위에서부터의 위치가 유지되도록 좌표를 다시 계산했다. 본문에는 '(Figure 2e)' 두 단어만 더해 4,991 → 4,993 word-equivalent. 배수 수치는 분량에 포함되지 않는 캡션에 적었다. 한글판 초안도 같은 캡션·참조를 반영했다.
- 검증: `--check` CHECK_OK(4,993), 노트 테스트 2 passed, `python -m ruff check scripts/` 통과, 영문·한글 도판 재생성. 업로드 보류 지시에 따라 푸시하지 않았다.

### H8. 그림 분리와 글씨 확대 (2026-09-12)

- 사용자 요청: 피규어만 봐도 무엇인지 알 수 있게 글씨를 크게 하고, 한 그림에 다 넣지 말고 나눌 것.
- 먼저 그림의 단어 환산 규칙(1단 300, 2단 600 word-equivalent)을 설명하고 선택지를 드렸다. 사용자는 '금속 시세만 1단 폭으로 분리'를 골랐다.
- Fig. 2의 (e)를 떼어 1단 폭 Figure 3(86×122 mm)으로 만들었다. 위는 귀금속 7종(USD/troy oz), 아래는 일반 금속 7종(USD/lb), 둘 다 로그 축이며 각 선 끝에 원소 기호와 최고/최저 배수를 적었다. 기존 민감도 그림은 Figure 4가 되었고 파일명도 `fig4_decision_diagnostics`로 바꿨다(구 `fig3_decision_diagnostics` 4개 삭제).
- 모든 도판의 글자·눈금 크기를 1.25배로 키웠다(5.0~8.6 pt → 6.2~10.8 pt). 그 결과 생긴 겹침 네 곳을 고쳤다: Fig. 2 (b) 설명과 x축 제목, (c) 설명과 사례 이름, (d) 범례 잘림, Fig. 4 왼쪽 반응군 이름 잘림. (c)의 시장 가격 숫자는 눈금에서 빼고 본문과 캡션에 남겼다. Fig. 2는 178×225 mm, Fig. 4는 178×120 mm.
- 1단 그림 300단어를 치르려고 본문을 3,019 → 2,723단어로 줄였다. 줄인 곳은 다른 절과 겹치는 설명이다: 구현 절의 원가 모델 요약(바로 다음 절이 전부 서술), 제조법 28종 나열, 몬테카를로 상·하한 나열, 저장 추정 비교 문단, 장비 대체·대리 단가 문장, 전극·회수 시나리오 세부, 구매 근거 괄호 목록. 검증 수치와 한계 서술은 건드리지 않았다.
- 합계 4,997 word-equivalent(초록 174 + 본문 2,723 + 그림 600+600+300+600), 그림 4개. `--check` 통과, 노트 테스트(그림 수 4로 갱신) 2 passed, `python -m ruff check scripts/` 통과. 한글판 초안도 같은 분리·번호·삭감을 반영했다. 업로드 보류 지시에 따라 푸시하지 않았다.

### H9. 도판 문구 정리와 검토용 슬라이드 (2026-09-12)

- 사용자 질문('파이썬으로 뽑은 것 맞나')에 대한 확인: Fig. 2·3·4는 matplotlib이 동결 JSON에서 직접 그린다. 산출된 SVG 안에 글자가 텍스트 요소로 남아 있고(각각 151·37·77개) 'Matplotlib v3.10.8'이 기록되어 있다. 화면 캡처라면 이런 요소 없이 래스터 한 장만 들어간다. Fig. 1만 ChatGPT로 만든 그림이며 캡션과 Acknowledgments에 밝혀 두었다.
- 범례·축 제목·주석 문구를 영문 22곳, 한글 21곳 고쳐 사람이 쓴 말투로 바꿨다. 예: 'Cases in which the candidate ranks first (%)' → 'How often the candidate ranks first (%)', 'Ru candidate removed' → 'Ruthenium candidate removed', '후보가 1위를 차지한 경우의 비율' → '1위를 차지한 경우의 비율', '그 외 활성 물질' → '그 밖의 활성 물질'.
- 길어진 라벨이 상자를 넘쳐 16곳을 다시 맞췄다. 두 줄 처리(간접비 설명, Fig. 4b 검사 이름), 짧은 표현('spot or monthly average'), 원가 내역 6줄의 간격·크기 조정이다. 뜻은 그대로 두고 길이만 맞췄다.
- `_local/note-figures/build_figure_review_pptx.py`로 그림 설명용 슬라이드 6장을 만들었다. 그림마다 '무엇을 보여 주는가 / 왜 넣었는가 / 수정 요청' 칸이 있어 사용자가 고칠 점을 적을 수 있다. 로컬 파일이라 커밋하지 않는다.
- 검증: `python -m ruff check` 통과, 영문·한글 도판 재생성, docx v22 재빌드(검토 메모 6개 유지, 그림 4개 최신본 확인). 원고 본문과 캡션은 바뀌지 않아 분량은 4,997 그대로다. 업로드 보류 지시에 따라 푸시하지 않았다.

### H10. 사용자 도판 검토 반영 (2026-09-12)

사용자가 검토용 슬라이드의 '수정 요청' 칸에 적어 준 요청을 반영했다.

- **Fig. 1의 미세한 점**: 밴드와 Traceability 패널을 잇던 점선 연결선이었다. `scripts/straighten_note_fig1_leaders.py`가 이제 간격만 정리하고 연결선은 그리지 않으며, 원본 PNG에서 영문·한글판을 다시 만들었다.
- **모든 도판의 테두리**: 축을 왼쪽·아래만 있는 형태에서 네 면이 모두 있는 네모 박스로 바꿨다(`_clean`).
- **Fig. 3의 ×배수와 그림 안 설명**: 선 끝 라벨에서 배수를 빼고 원소 기호만 남겼으며, 그림 아래 설명 문구도 없앴다. 배수(아연 2.3 ~ 로듐 11.6, 니켈 2.9, 루테늄 6.8)는 캡션으로 옮겼다. 같은 지시('피규어만 놓고 설명은 본문·캡션으로')에 따라 Fig. 2의 (b)·(c)·(d) 아래 설명 문구도 모두 없애고 캡션에 넣었다.
- **Fig. 2 (a)의 선**: 엇갈리던 대각선 화살표를 직각 연결선으로 바꿨다. 제조 경로는 세로 버스로 두 상자에 들어가고, C_m과 C_p는 한 지점에서 모여 간접비 상자로 들어간다.
- **Fig. 2 (d)가 Fig. 3과 비슷하다는 지적**: 절대 수준을 그리던 것을 '추정값 ÷ 거래 단가' 비율로 바꾸고 거래 수준을 1로 놓았다. 이제 Fig. 3은 금속 시세 자체를, Fig. 2d는 추정값이 그 범주의 거래 수준에서 얼마나 떨어져 있는지를 보여 준다.
- **Fig. 4 (c)에 루테늄 사례만 있다는 지적**: 후보 하나를 빼면 1위가 바뀌는 반응군 9개를 모두 로그 원가 축에 담았다(동결 파일의 `winner_changed`·`renormalized_winner`와 제거 전 원가). 동결 파일의 '제거 후 점수'는 C01 결함으로 갱신 전 값이라 쓰지 않았다. 그림 높이는 120 → 150 mm.
- 검증: `--check` 4,997 word-equivalent·그림 4개, 노트 테스트 2 passed, `python -m ruff check scripts/` 통과, 영문·한글 도판과 docx v23 재생성. 업로드 보류 지시에 따라 푸시하지 않았다.

### H11. 도판 2차 검토 반영 (2026-09-12)

H10에서 잘못 읽은 요청 하나를 되돌리고, 새로 받은 두 가지를 반영했다.

- **Figure 1**: 저자가 말한 '미세한 점'은 밴드와 패널을 잇는 점선 연결선이 아니라, 원본 그림이
  태그 상자 왼쪽에 남겨 둔 리더 자국이었다. H10에서 지운 연결선을 되살리고, 자국을 지우는 범위를
  `[panel + 3, tag - 3]`에서 `[panel + 2, tag]`로 넓혔다. 출력에서 패널 안 띠의 잔여 화소 0개를
  확인했다.
- **수식**: `mathtext`를 stixsans에서 Arial로 바꿨다(`fontset=custom`, rm/it/bf/sf = Arial,
  심볼만 stixsans 대체). 한글판도 본문은 Malgun Gothic, 수식은 Arial이다.
- **Figure 2 (a)**: 가격 상자를 40 → 47 mm로 넓혀 상자 밖으로 삐져나오던 P 식을 안에 넣었고,
  중간 상자는 57 → 52 mm로 줄였다. 선은 직각만 쓰고, 입력 셋은 x = 34의 세로 트렁크 하나로
  모인다. C_m과 C_p가 한 점에서 합쳐져 화살표 하나로 들어가던 ㄷ자 합류를 없애고, 각자 다른
  높이(y = 28, 18)로 가격 상자에 들어가게 했다. 기호는 선 위·아래로 옮겨 모서리와 겹치지 않는다.
- **편집용 슬라이드**: `_local/note-figures/build_editable_figure_pptx.py`. Figure 2 (a)를
  파워포인트 도형(상자·연결선·수식 텍스트)으로 다시 만들어 저자가 직접 옮기고 고칠 수 있게 했다.
  데이터가 들어가는 판은 동결 파일과의 연결이 끊기므로 그림으로만 넣고, 그리는 함수 이름을 적었다.
  이 PC에 변환기가 없어 슬라이드를 실제로 렌더해 눈으로 확인하지는 못했다. 도형이 슬라이드 밖으로
  나가지 않는 것만 좌표로 확인했다.
- **인수인계 문서**: `_local/handoff/gpt-figure-handoff-2026-09-12.md`. 저자가 이 작업을 GPT에
  넘길 수 있도록 붙여넣을 프롬프트, 파일 지도, 분량 규칙, 요청별 처리 상태, 남은 일, 금지 사항을
  정리했다.
- 검증: `--check` 4,997 word-equivalent·그림 4개, 노트 테스트 2 passed, 손댄 파일 ruff 통과,
  영문·한글 도판 재생성. 업로드 보류 지시에 따라 푸시하지 않았다.
- 워드 원고는 아직 v23(H10 시점 그림)이다. 새 그림으로 다시 만들려면 변환기를 다시 돌려야 한다.

확인 못 한 것과 하지 않은 것:

- 저자·소속·연구비·이해관계 문구·상업 라이선스 문의처·심사용 버전(v1.4.0 태그 여부)은 원고에 placeholder로 남아 있으며 사람이 정해야 한다.
- JCIM의 SCIE 수록과 IF는 제3자 자료로만 확인했다. JCR 원본 확인은 사용자 몫이다.
- 연구실 V8 양식 docx(영문·한글판, Word 검토 메모 6개)와 Gemini·ChatGPT 참고 렌더 6장은 `_local/`에 두고 추적하지 않는다. 원고 도판은 matplotlib 벡터본만 쓴다.
- 상용 촉매 가격과의 비교는 CatCost 표 6.2에 함께 실린 시장 가격 3건이 전부다. 조건이 일치하는 다른 상용 가격 관측은 찾지 못했으므로 반응군 전체에 대한 오차표는 만들지 않았다. Fig. 2b는 모델 출력이지 실측 원가가 아니다.
- 본문의 예시 숫자는 실행 시점의 현물 시세에 따라 달라지므로 바이트 단위로 재현되지 않는다. 커밋한 JSON 사이드카(`screen_result_ni_al2o3.json`)가 도판과 본문의 입력이고, 캡처 스크립트는 만드는 방법의 기록이다. 같은 이름의 PNG는 참고용 화면이며 원고에는 쓰지 않는다.
- Fig. 1은 AI 생성 그림이라 생성 스크립트로 재현되지 않는다. 원본 PNG와 프롬프트 전문, 저자 수정 스크립트를 함께 커밋해 검증 가능하게 했다. ACS AI 정책은 공식 페이지에서 읽었고(2026-09-10), OpenAI 이용약관의 출력물 권리 조항은 자동 요청이 차단돼 확인 못 했다(저자 확인 항목).
- 투고·외부 연락·태그·릴리스·병합은 하지 않았다.

### H12. GPT 인수인계 확인과 Word 갱신 준비 (2026-09-12)

- 인수인계 문서와 이 감사 기록을 읽고 지정된 작업 폴더·브랜치를 확인했다. 시작 시 HEAD는
  `d80848f`, 작업 트리는 깨끗하며 원격 추적 브랜치보다 로컬 커밋 6개 앞서 있었다. 별도
  `COMET` 체크아웃은 읽거나 수정하지 않았다.
- **Figure 2 (a)는 아직 확정하지 않았다.** 작업 폴더에서 찾은
  `_local/note-figures/COMET_figures_editable.pptx`의 2쪽 XML을 편집용 생성기의
  `cost_model_slide()`가 메모리에서 만든 XML과 정규화해 비교했으며 완전히 일치했다.
  검토 코멘트 파트도 없었다. 저자가 수정한 배치를 확인할 수 없어 수정본의 로컬 경로나
  원하는 배치 변경을 요청했다. 기존 배치를 저자가 승인했다고 간주하지 않았다.
- 영문·한글 그림 재생성 → 원고 `--check` → 노트 pytest → scripts ruff를 지시한 순서로
  실행했다. 모두 통과했고 재생성 결과는 추적 파일과 같았다. 초록 174 + 본문 2,723 +
  그림 2,100 = **4,997 word-equivalent**, 그림 4개·표 0개, pytest **2 passed**다.
  본문·캡션·동결 JSON·그림 생성기는 변경하지 않았다.
- **Word v24 검토용 중간본**: 기존 변환기와 연구실 V8 생성기를 사용해 영문·한글판을
  `_local/docx/`에 만들고 `carry_review_comments.py`로 v23의 검토 메모를 각각 6개 옮겼다.
  문단 텍스트·메모 내용·앵커·작성자 정보가 v23과 같고, 삽입된 네 그림의 바이트가 각 언어의
  최신 PNG와 같음을 검사했다. 개인정보를 포함한 원고와 중간 산출물은 `_local/`에만 두었다.
- Word 생성기가 모든 그림을 폭 16.8 cm로 넣어 Figure 3도 높이 23.84 cm가 되는 기존
  문제를 발견했다(본문 영역 높이 22.90 cm). 로컬 재생성 스크립트
  `_local/docx/rebuild_v24.py`에서 Figure 3만 원래 1단 규격인 **8.6 × 12.2 cm**로 넣도록
  하고 두 언어를 다시 생성했다. PNG/SVG의 픽셀·수치나 영문·한글 원문은 바꾸지 않았다.
- 확인 못 함: 이 환경에는 패키지의 문서 렌더러가 요구하는 `soffice.exe`가 없어
  `render_docx.py`가 `FileNotFoundError`로 중단됐다. 따라서 v24의 실제 페이지 배치와
  그림·캡션의 페이지 나눔은 아직 눈으로 확인하지 못했으며 최종 제출본으로 확정하지 않았다.
  구조 검사 결과는 `_local/docx/qa_v24/structural_checks.json`에 보관했다.
- 다음 작업: 저자의 Figure 2 (a) 수정 배치를 생성기에 반영한 뒤 지정 검증과 두 언어의
  Word 재생성·페이지 검토를 마친다. 공개/상용 결정은 인수인계 §8의 회의 안건으로 유지한다.
  GitHub·Zenodo 업로드와 배포·외부 연락은 하지 않았다.

### H13. Figure 2 (a) 배치 결정과 캡션 동기화 (2026-09-12)

- H12의 수정본 요청에 대해 사용자가 직접 판단해 우선 진행하라고 지시했다. 별도 PPT 수정본을
  기다리지 않고 `_cost_model_panel()`에서 이번 배치를 정했다.
- **입력과 계산 경로**: 조성·가격 기준을 재료비로, 제조 경로·주문량을 가공비로 연결했다.
  기존 그림은 가격 기준이 가공비에만 들어가는 것처럼 보였다. 주문량은 가공비뿐 아니라
  판매 마진율도 정하므로, `calculate_step_method()`의 실제 계산 관계에 맞춰 아래쪽에
  주문량 → m → 판매 단가 경로를 표시했다. 연결선은 모두 수평·수직이며 교차하지 않는다.
- **도식 구성**: 입력 네 개, 병렬 재료비·가공비, 판매 단가의 세 열로 정리했다. 별도 원가 내역
  상자와 설명 줄들을 없애고 그 정보는 캡션에 남겼다. 판매 단가 상자를 47 → 62 mm 좌표 폭으로
  넓히고 세 핵심 수식을 11 pt로 맞췄다. 수식은 Arial, 한글 라벨은 Malgun Gothic을 유지했다.
  전체 그림 규격 178 × 225 mm와 다른 패널의 배치는 그대로다.
- **캡션**: `build_application_note.py`에서 입력 연결, 주문량의 마진 영향, G&A·S&ARD의 순차
  가산과 판매 단가 기준 마진을 설명했다. 선택적 전구체 질량식 a = w/(f p y)는 캡션으로 옮기고
  f·p·y의 의미를 본문과 맞췄다. 과거 단일 니켈 예시의 잔여 문장인 “The example in b used
  the nickel quote of 2026-09-10.”은 현재의 기준월 23개 반응군 패널에 해당하지 않아 제거했다.
  한글 원고의 Figure 2 캡션에도 같은 설명을 반영했다.
- **재생성·검증**: 영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts ruff를
  지정 순서로 실행해 모두 통과했다. **4,997/5,000 word-equivalent**, 그림 4개·표 0개,
  수치 키 참조 57개, pytest **2 passed**. 캡션만 바뀌어 본문과 분량 기록은 그대로다.
- **그림 검사**: 두 언어의 (a) 출력과 영문 전체 그림을 직접 확인했고, 렌더러 좌표 검사에서도
  모든 상자 안 글자와 수식이 경계를 넘지 않는다. 기존 PNG와의 차이는 2803 × 3543 px 중
  (a) 영역의 `(61, 20, 2774, 680)` 범위에만 있으며 (b)~(d)는 픽셀 단위로 동일하다.
  동결 JSON 6개는 Git의 체크아웃 줄바꿈 처리를 반영해 기존 객체와 일치함을 확인했다.
  첫 원시 바이트 비교는 기존 CRLF/LF 차이 때문에 실패했으며 파일은 수정하지 않았다.
  소스·Markdown의 `git diff --check`도 통과했다. SVG에는 Matplotlib이 원래 출력하는
  path 행 끝 공백이 있어 전체 diff 공백 검사는 경고를 냈으며 생성물을 수작업 정리하지 않았다.
- **Word**: `_local/docx/rebuild_v24.py`로 두 언어를 다시 생성했다. v23과 비교해 바뀐 텍스트는
  Figure 2 캡션 한 문단뿐이고, 각 언어의 최신 그림 네 개와 검토 메모 6개를 확인했다.
  Figure 3의 1단 폭 8.6 cm도 유지했다. H12의 문서 렌더러 부재는 해소되지 않아 v24의 실제
  페이지 검토는 아직 미완료다. 기존 편집용 PPT는 H11 배치이므로 현재 도식과 혼동하지 않도록
  로컬 인수인계에 표시했다.
- Figure 1, 데이터·엔진·버전·라이선스·공개 방식은 변경하지 않았다. 공개/상용 결정은 회의
  안건으로 유지하며, 이번 변경도 로컬 커밋에만 남긴다.

### H14. 학술 문체·주장 범위·도판 표현의 전반 개정 (2026-09-12)

- 사용자는 처음 표현을 정정하여 **SCI 논문답지 않은 부분을 전반적으로 고치라**고 지시했다.
  이를 초록·본문·캡션의 학술 문체, 주장과 근거의 일치, 도판의 정확성과 가독성 개선으로
  적용했다. 영문은 `build_application_note.py`를 수정해 재생성하고 한글 원문을 동기화했다.
- **서술**: “what a buyer pays”, “COMET lands”, “a cheaper catalyst is not a better one”과 같은
  구어체·격언형 표현을 제거했다. 도입부는 비교 시 필요한 입력과 COMET의 구현 기여를,
  방법 절은 계산·가격 출처·점수 정의를, 적용 사례는 입력과 순위 변화의 관계를 설명하도록
  정리했다. 도구 간 차이를 근거 없이 단정하는 표현과 시점에 따라 달라지는 테스트 개수도
  제거했다. 채택한 방법의 귀속은 유지했다.
- **검증 범위**: 문헌 계산 재현, 문헌 시장 가격 3건과의 비교, 산업 원가 검증을 구분했다.
  시장 가격 잔차의 원인이 입증된 것처럼 쓰던 설명을 삭제했다. 범주별 수입 단가와의 비교를
  조성 일치 검증으로 해석하지 않도록 고쳤다. 기존의 “원가가 수입 단가 아래에 머문다”는
  취지의 문장은 동결 데이터와 맞지 않는다. 실제 Figure 2 (d)의 비율 범위는 니켈계 약
  0.508–2.450, 귀금속계 0.472–111.287, 기타 활성 물질 0.158–12.558이다. 본문에는 이 범위를
  새 정확도 지표로 넣지 않고 범주·시점별로 비율이 달라진다는 해석을 썼다.
- **분석 정의**: 점수 regret을 시나리오 최고 점수 대비 손실로 정의하고, 시나리오 빈도와 미래
  확률, 가정한 몬테카를로 변동 범위와 통계적 신뢰구간을 구분했다. 최소-최대 정규화와 원가가
  같을 때의 처리도 실제 `decision_engine.py`와 맞췄다. 초록의 116개 후보를 모두 문헌 후보로
  부르던 표현을 스크리닝 후보로 고쳤다. 83개 문헌 구조 대리와 29개 공학적 대리는 전체 분류의
  일부임을 표시했다(나머지 네 기록에는 별도 근거 분류가 있음).
- **Figure 2**: (b)는 최저 원가 후보, (d)는 기준 순위의 1위 후보라는 선택 차이를 캡션에
  명시했다. (c)의 인접 수치 라벨을 분리하고 (d)의 범례를 해당 패널 가까이 옮겼다. 반응군 수는
  그림 내부 설명에서 캡션으로 이동했다. H13의 (a) 배치와 모든 원가 계산값은 유지했다.
- **결측 표시 오류 수정**: 기존 (d)는 무역 관측이 없는 월을 목록에서 제거하여 양옆 관측을
  선으로 연결했다. 모든 월을 유지하고 결측 비율을 NaN으로 표시해 선을 끊도록 생성기를
  고쳤다. 회귀 테스트는 수정 전 실패했고 수정 후 통과했다. 기존 유한 후보-월 비율값
  **1,771개는 모두 동일**하며, 23개 후보 선에 걸친 결측 월 **276개**를 명시적으로 표시했다.
  수치 보간이나 동결 입력 수정은 하지 않았다. 새 테스트는 Matplotlib이 있는 환경에서
  수행하며, 해당 선택 의존성이 없는 환경에서는 건너뛴다.
- **Figure 3·4**: 금속 시계열에 구분되는 색과 마지막 관측점 연결선을 적용하고, 패널 문자와
  가격 축 단위를 명시했다. Figure 4의 긴 라벨을 위한 패널 간격을 확보했으며, 후보 제거
  전후의 거의 같은 원가를 빈 원·채운 원으로 구분했다. “Runner-up”은 실제 선택 기준에 맞춰
  시나리오 1위 빈도가 가장 높은 대안 후보로 정의했고, “과반”은 실제 집계 기준인 ≥50%로
  정정했다. 두 그림의 선·막대에 들어가는 수치와 후보 선택은 이전 커밋과 모두 일치한다.
  설명은 캡션에 두고 영문·한글 PNG 여섯 장을 직접 확인했다.
- **검증**: 영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts ruff를 지정
  순서로 통과했다. pytest **3 passed**. 추가로 수정 테스트 파일의 ruff와 소스·Markdown
  공백 검사도 통과했다. 초록 160 + 본문 2,381 + 그림 2,100 = **4,641/5,000 word-equivalent**다.
  그림 4개·표 0개·참고문헌 14개·수치 키 참조 57개를 유지했다. 생성기의 모든 수치 삽입식과
  57개 참조는 이전 커밋과 같고, 동결 입력 7개는 Git 줄바꿈 처리를 반영한 해시가 일치한다.
  비교 기록은 `_local/note-figures/academic_revision_checks_2026-09-12.json`에 보관했다.
  SVG는 생성기 출력 그대로이며, H13에 기록한 Matplotlib path 끝 공백을 수작업 정리하지 않았다.
- **Word·한글 동기화**: `_local/docx/rebuild_v25.py`로 기존 V8 생성기에서 영문·한글 v25
  검토 초안을 만들었다. 각 언어에 최신 그림 4개와 기존 검토 메모 6개를 유지했다. 수정된 시장
  비교 문단의 메모 앵커는 대응 문단으로 옮겼고, 메모 내용·작성자 정보는 동일하다. 한글 원문의
  저자 블록과 두 언어의 참고문헌은 그대로다. 구조 검사 기록은 `_local/docx/qa_v25/`에 있다.
  H12의 `soffice.exe` 부재로 실제 Word 페이지 배치는 **확인 못 함**이며 최종 제출본으로
  확정하지 않았다. 개인정보를 포함한 문서와 검사는 `_local/`에만 저장했다.
- 새 문헌·DOI·외부 가격 자료를 추가하지 않았다. Figure 1의 기존 저자 선택과 AI 사용 고지는
  유지했다. 버전·라이선스·배포 방식과 저자 선언은 회의 결정 전 상태로 남겼다. 공개/상용 결정,
  실제 저자 선언 확정과 Word 페이지 검토는 여전히 필요하다. 외부 업로드·연락 없이 로컬
  커밋으로만 보관한다.

### H15. 기준 조건의 순위 표현 명확화 (2026-09-12)

- 사용자가 “Reference leader”라는 표현을 지적했다. H14에서 라벨을 줄이기 위해 사용했지만,
  기준 조건에서 1위인 후보라는 뜻이 직접 드러나지 않는다는 편집 판단에 따라 수정했다.
  이 표현을 분야의 확립된 용어로 확인한 것은 아니다.
- 그림의 `Reference leader`는 `Top-ranked at baseline`, 본문과 캡션의
  `reference-leading candidate`는 `candidate ranked first at baseline`으로 통일했다.
  후보 제거 후의 표기도 `Top-ranked after removal`로 맞췄다. 기준 조건은 **2026년 5월 가격,
  균형 가중치, 각 반응군의 전체 후보군**이라고 본문과 캡션에 정의했다. 이는 동결 분석의
  `reference_winner` 선택 조건이며 새 후보 선택이나 계산 변경이 아니다.
- 영문·한글 원문을 함께 고치고 생성기를 통해 원고와 그림을 갱신했다. Figure 2·4의 영문
  범례가 바뀌었고, 한글 그림은 이미 같은 의미의 라벨을 사용하므로 출력이 이전과 같다.
  새 영문 Figure 4를 직접 확인해 범례의 겹침·잘림이 없음을 확인했다.
- 영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts ruff를 지정 순서로
  통과했다. **4,664/5,000 word-equivalent**, 수치 키 57개, pytest **3 passed**다.
  원고의 수치 삽입식과 키 참조는 이전 커밋과 같으며 동결 입력은 수정하지 않았다.
- 두 언어의 Word v26 검토 초안은 `_local/docx/rebuild_v26.py`로 생성했다. 각 문서의 최신
  그림 4개와 기존 메모 6개를 검사했으며, 메모 앵커 변경은 없다. 실제 페이지 배치 검토는
  H12의 렌더러 부재로 여전히 미완료다. 이 변경은 로컬에만 보관하며 외부 업로드는 하지 않았다.

### H16. 제목부터 참고문헌까지 문장·용어 전수 검토 (2026-09-12)

- 사용자는 H15의 한 표현 수정에 그치지 말고 논문답지 않은 표현을 하나하나 검토해 모두
  고치라고 지시했다. `f880c2f`의 제목·절 제목·본문·네 캡션·저자 선언·참고문헌 등 48개 블록을
  순서대로 검토하여 35개 블록을 수정했다. 각 블록과 그림 라벨의 판단 근거는 별도 기록
  [Application Note 문장·용어 검토 기록](application-note-language-review-2026-09-12.md)에
  남겼다. 실제로 통용되는 전문용어인지 확인하지 않은 명칭을 학술 용어라고 제시하지 않고,
  대상과 계산 동작을 직접 설명하는 문장으로 바꿨다.
- **서술과 제목**: 제목은 `COMET: Software for Catalyst Manufacturing Cost Estimation and
  Sensitivity Analysis`로 정리했다. `literature-architecture proxies`, `engineering proxies`,
  `retained-component yield`, `historical repricing`, `least favourable corner`, `cobalt composite`,
  `unestimated` 등 축약·추상 표현을 실제 조성의 근거, 성분 보존 비율, 재계산과 점수 변화의
  설명으로 바꿨다. 초록·도입·방법·사례·한계를 완전한 문장으로 연결하고 모든 캡션을 동기화했다.
  생성 Markdown을 직접 수정하지 않고 영문 생성기를 고쳐 재생성했다. 한글 원문도 함께 고쳤다.
- **계산 의미 대조**: `evidence`는 재료비 기여분으로 가중한 가격 출처 신뢰도이며 촉매 성능의
  근거 수준이 아님을 명시했다. 경로 점수는 세 평가의 평균이라는 구현을 설명했다. 환경 목록
  반영률은 검증된 재료 계수가 있는 촉매 질량의 비율이며 총 환경 영향의 반영 비율이 아님을
  구분했다. 후보 제외는 기준 조건의 1위 이외 후보를 하나씩 제외하는 검사로, 점수 변화는
  기준 후보의 경로·성능을 낮추고 다른 후보의 두 점수를 높이는 검사로 설명했다. 결합 분석의
  1위 빈도 중앙값은 해당 분석 설명 바로 뒤에 배치했다. 결정론적 열거와 난수 표본 추출,
  시나리오 빈도와 미래 확률, 구현 검증과 산업 원가 검증을 구분했다.
- **원문과 DOI**: [Baddour 등의 무료 공개 원문](https://www.osti.gov/servlets/purl/1477947)의
  3쪽 본문·6쪽 표 주석에서 sales, administrative, research, and distribution costs를 확인해
  `S&ARD`를 `SARD`로 바로잡았다. USY의 풀어쓴 말은 같은 원문 2쪽에서 확인했다. 참고문헌의
  DOI 10개는 무료 Crossref API로 제목·서지 정보를 재조회했다. 두 건의 최초 HTTP 429는
  순차 재조회로 해소됐다. 사용자 안내서의 새 다운로드는 DNS 오류로 **확인 못 함**이었고,
  이를 성공한 조회로 기록하지 않았다. 참고문헌 14개와 인용 순서는 그대로이며 새 문헌이나
  유료 출처를 추가하지 않았다. 원문과 조회 응답은 `_local/language-review-2026-09-12/`에 있다.
- **그림**: Figure 1을 `figure1_workflow()`로 다시 그렸다. 다섯 단계와 분석 기록 라벨만
  남기고 `Electrode per cm²`, `grade per line`, `partial LCA`, `Leave-one-out test` 등 설명
  조각을 본문·캡션의 완전한 설명으로 옮겼다. 현재 그림 네 개 모두 같은 생성기로 PNG·SVG를
  출력한다. 기존 AI 그림의 배치를 참고한 이력과 원본 파일은 보존하고 캡션·AI 고지·provenance를
  실제 작업에 맞췄다. 이미지 생성 도구를 새로 사용하거나 PNG/SVG를 수작업 편집하지 않았다.
  Figure 2는 비교 문헌과 비율 축을 구체화했고, Figure 3 한글의 `일반 금속`을 `비귀금속`으로
  바꿨다. Figure 4의 `Leading alternative`, `Joint share` 등은 후보·빈도·검사 기준을 직접
  나타내는 라벨로 바꿨다. H13의 Figure 2 (a) 연결과 H14의 결측 처리는 유지했다.
- **미확정 선언**: 버전 1.4.0과 분석 파일이 이미 외부에 공개된 것처럼 쓰던 Availability를
  프로젝트 정보와 버전별 접근 방법의 미확정 상태로 구분했다. 공개/상용 배포 방식이나
  이해상충을 대신 결정하지 않았다. 내부 상용화 계획은 로컬 기록에 보존하고 논문의 이해상충
  문단은 저자 진술 자리표시자로 정리했다. 소프트웨어 라이선스와 제3자 데이터의 이용 조건을
  별도로 명시했다. 저자 개인정보는 커밋 파일에 넣지 않았다.
- **검증**: 영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts ruff를 지정
  순서로 통과했다. pytest **3 passed**, 수정한 테스트 파일의 ruff와 소스·Markdown 공백 검사도
  통과했다. 초록 151 + 본문 2,692 + 그림 2,100 = **4,943/5,000 word-equivalent**다.
  그림 4개·표 0개·참고문헌 14개를 유지했다. 분량 메타데이터의 설명을 실제 집계 방식에 맞췄으며
  집계 로직은 바꾸지 않았다. 저자 선언 확정 시 분량을 다시 확인해야 한다.
- **수치와 렌더 검사**: 원고의 모든 수치 삽입식과 JSON 참조 57개, 동결 입력 7개의 Git 해시가
  H15와 같다. Figure 2–4의 영어·한글 선 데이터·막대 및 도형 좌표·축 범위도 모두 같다.
  현재 영어·한글 그림 8장을 직접 확인했고, Figure 1의 라벨 14개씩이 상자 안에 들어가는지
  렌더러 좌표로도 검사했다. 결과는 `_local/language-review-2026-09-12/revision_checks.json`이다.
- **Word**: 기존 V8 생성기로 영문·한글 **v27 검토 초안**을 만들었다. 각 문서에 최신 그림
  4개와 기존 메모 6개를 넣고 문구·작성자 정보가 유지되는지 확인했다. 공개 안내 문단에 메모
  두 개가 함께 있어 기존 CLI의 중복 앵커 처리가 중단됐다. 로컬 `rebuild_v27.py`에서 기존
  메모 읽기 함수를 사용하되 각 메모를 대응 문단에 따로 붙여 해결했다. Figure 3은 폭 8.6 cm,
  나머지는 16.8 cm다. 구조 검사 기록은 `_local/docx/qa_v27/`에 있다. `soffice.exe` 부재로
  실제 Word 페이지 배치는 **확인 못 함**이며 제출본으로 확정하지 않았다.
- 소프트웨어 엔진·버전·라이선스·동결 데이터는 변경하지 않았다. 공개/상용 결정과 실제 저자
  선언 확정은 인수인계 §8의 회의 안건이다. 이번 작업도 외부 업로드·연락 없이 로컬 커밋으로만
  보관한다.

### H17. v27 도판 주석 반영과 패널 재배치 (2026-09-12)

- 저자는 v27 Word에서 Figure 1의 단계별 아이콘, `(a)` 형식의 패널 문자, Figure 2 (d)의
  삭제 검토, Figure 4 (c)의 겹친 점과 (a)의 범례 배치 개선을 요청했다. 기존 그림 생성기를
  수정하고 영문·한글 본문과 캡션을 동기화했다. 생성 PNG/SVG와 영문 Markdown은 직접
  편집하지 않았다. 설계·검사 자료는 `_local/figure-review-v28/`에 보관했다.
- **Figure 1**: 데이터베이스·달력·계산기·원가 구성 막대·순위 단상 아이콘을 직접 정의한
  벡터 도형으로 추가했다. 같은 크기와 선 체계를 사용하고 단계명을 아이콘 옆에서 왼쪽 정렬했다.
  그림에 설명 문구를 추가하지 않았다. 외부 아이콘 파일이나 이미지 생성 도구를 사용하지
  않았으며, 기존 AI 그림을 배치 참고 자료로 사용한 이력은 provenance와 원고에 유지했다.
- **Figure 2**: (d)는 본 그림에서 제외했다. Figure 3과 동일한 자료는 아니지만, 두 시계열
  표현을 함께 싣는 부담에 비해 조성별 검증에 주는 정보가 제한적이라고 판단했다. 원가 모델,
  23개 반응군 원가 구성, 문헌 사례 3건의 비교를 (a)–(c)에 남겼다. 그림 높이는 225 → 164 mm,
  폭은 178 mm로 유지했다. 아래 두 패널의 상단·범례를 맞추고 (b)의 긴 반응명 왼쪽 여백을
  늘렸다. (a)의 계산 관계와 수식은 그대로다. 무역 비교의 동결 데이터와 `_market_panel()`
  감사용 함수·결측 회귀 검사는 보존했다. 본문에는 분석 파일의 비교 결과와 해석 한계만
  간략히 남겼고, Figure 2 (d)를 가리키는 문장과 캡션은 제거했다.
- **패널 문자**: Figure 2–4에서 `(a)`, `(b)`, `(c)`로 통일하고 본문 교차 참조에도 괄호를
  반영했다. Figure 3의 금속 시계열·색·범례 역할의 원소 기호는 바꾸지 않았다.
- **Figure 4 (a)·(b)**: (a) 범례를 세 줄로 나누어 해당 패널 안에 배치하고 두 위쪽 축의
  상단을 맞췄다. 그림 크기는 178 × 164 mm다. 기존 30개 반응군의 빈도·후보 분류, 다섯 검사와
  집계값은 그대로다. (b)·(c)에는 각각 라벨을 위한 왼쪽 공간과 패널 간 간격을 확보했다.
- **Figure 4 (c)**: 로그 축에서 거의 겹치던 두 점 대신, 아홉 반응군의 두 1위 후보 사이
  원가 차이를 선형 백분율 막대로 표시했다. 식은 100 × (C₁ − C₀)/C₀이며, C₁은 제외 후
  선택된 후보, C₀는 기준 조건에서 선택된 후보의 원가다. 두 값 모두 같은 가격·제조 가정의
  제외 전 원가 기록에서 읽는다. **같은 후보의 원가 감소나 재계산 결과가 아니다.** 캡션에
  두 후보의 비교라는 점, 음수의 뜻과 정규화 범위의 변화를 명시했다. 아홉 반응군을 모두
  유지하고 소수점 한 자리 수치를 붙였다. 예를 들어 암모니아 분해는 4.7411과 4.3573 USD/lb의
  차이인 −8.095...%를 −8.1로 표시한다. 알려진 C01의 잘못된 제외 후 점수는 사용하지 않았다.
- **검증**: 영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts ruff를 지정
  순서로 통과했다. 첫 실행에서 새 import 형식이 ruff I001에 걸려 해당 import만 정리한 뒤
  전체 순서를 다시 통과했다. pytest **4 passed**다. 새 검사는 별도 `methods_study.json`의
  암모니아 원가 사례로 (c)의 백분율을 확인하며, 이전 점 그래프에서는 실패하고 새 그림에서
  통과했다. 기존 무역 통계 결측 검사도 유지했다. 수정 테스트 파일의 ruff와 소스·Markdown
  공백 검사도 통과했다.
- **보존·도판 확인**: 동결 입력 7개의 Git 해시, 원고 수치 삽입식·참조 57개와 참고문헌 14개는
  `8fb5528`과 같다. Figure 2의 남은 패널·Figure 3·Figure 4 (a)·(b)의 수치는 같고, (c)의
  아홉 백분율은 기존 점 그래프의 각 원가 쌍과 일치한다. 영어·한글 PNG 8장을 직접 확인하고
  실제 그려지는 문자들의 캔버스 경계와 (a) 범례의 영역 내 배치도 검사했다. 분량은 초록 151 +
  본문 2,676 + 그림 2,100 = **4,927/5,000 word-equivalent**, 그림 4개·표 0개다. 패널 제거는
  그림 수나 단 너비를 바꾸지 않으므로 그림 분량 2,100은 그대로다.
- **Word**: 기존 생성기로 영문·한글 **v28 검토 초안**을 만들었다. 최신 PNG 네 장과 기존
  메모 6개씩, C₀·C₁ 표기와 제거한 패널의 교차 참조 부재를 확인했다. 한글 무역 비교 문단의
  메모 앵커만 대응 문단으로 옮겼으며 메모 본문·작성자 정보는 그대로다. Figure 3 폭 8.6 cm,
  나머지 폭 16.8 cm를 유지했다. 실제 페이지 렌더는 `soffice.exe` 부재로 **확인 못 함**이다.
  시도 로그와 구조 검사는 `_local/docx/qa_v28/`에 있다. 연속 스크롤 미리보기나 XML 검사로
  실제 Word 페이지 검토를 대신했다고 주장하지 않는다.
- 엔진·버전·라이선스·공개 방식은 바꾸지 않았다. 외부 업로드·연락 없이 로컬 커밋으로 보관한다.

### H18. Figure 1의 기존 일러스트 아이콘 재사용 (2026-09-12)

- 저자는 H17에서 새로 그린 기하학 아이콘의 외관을 거부하고 이전 Figure 1의 아이콘을
  사용하도록 요청했다. 원본의 가격표 묶음·달력·플라스크와 가격표·원가 명세서·저울을
  `draw_application_note_figures.py`의 `_workflow_icon()`에서 고정 좌표로 추출하도록 바꿨다.
  H17의 새 도형 정의와 그에만 쓰인 import는 제거했다. 원본 PNG는 수정하지 않았다.
- 추출 영역의 바깥과 연결된 옅은 배경만 제거하고 단계 상자의 색 위에 합성한 다음 크기를
  조정한다. 투명 이미지를 바로 보간했을 때 윤곽선에 생기던 흰 테두리는 배경 합성으로 해결했다.
  다섯 아이콘은 원래 비율과 내부 디테일을 보존하고 높이를 11.5 mm로 맞췄으며, 단계명의
  왼쪽 정렬 위치를 조정해 아이콘과의 간격을 확보했다. 두 언어에서 같은 원본 아이콘을 쓴다.
  그림 안 설명 문구를 되살리지는 않았다.
- 현재 SVG는 래스터 아이콘과 벡터 라벨·상자·연결선의 조합이다. 원고 생성기의 Figure 1
  캡션과 AI 사용 문구, 한글 원고와 provenance를 실제 아이콘 재사용에 맞춰 고쳤다.
  새 이미지 생성 호출은 없었다. 생성 PNG/SVG와 영문 Markdown은 정식 생성기로만 갱신했다.
- 영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts ruff를 지정 순서로
  통과했다. pytest **4 passed**, 분량은 초록 151 + 본문 2,677 + 그림 2,100 =
  **4,928/5,000 word-equivalent**다. 그림 4개·표 0개·수치 참조 57개·참고문헌 14개를 유지했다.
  두 언어의 Figure 1을 직접 보고 아이콘·단계명이 겹치지 않고 상자 안에 들어가는지도 검사했다.
- `ba06b2d`와 비교해 원본 아이콘 이미지·동결 입력 7개·Figure 2–4의 PNG/SVG가 그대로임을
  확인했다. 검사 코드와 결과는 `_local/figure-review-v29/`에 있다.
- 영문·한글 **v29 Word 검토 초안**을 재생성했다. 각 문서의 최신 그림 4개, 기존 메모 6개와
  메모 위치, 그림 폭을 확인했다. 구조 검사 결과는 `_local/docx/qa_v29/`에 보관했다.
  H17의 로그로 확인한 `soffice.exe` 부재가 해결되지 않아 실제 Word 페이지 배치는
  **확인 못 함**이다. 도판 확인과 문서 구조 검사를 실제 페이지 렌더 검증으로 간주하지 않는다.
- 공개 방식과 저자 선언은 여전히 미확정이다. 외부 업로드 없이 로컬 커밋으로만 보관한다.

### H19. 비수치 도식의 PowerPoint 원본 전환 (2026-09-12)

- 저자는 Figure 2(a)를 PowerPoint에서 구조화하고, Python 수치 결과를 제외한 도식은 PPT에서
  이미지로 내보내 원고에 사용하도록 요청했다. 이 새 지시에 따라 Figure 1과 Figure 2(a)의
  편집 원본을 `docs/paper/diagram-sources-2026-09-12/`의 두 PPTX로 전환했다. 각 파일은
  영문·한글 두 슬라이드이며, 예전 H11 편집용 PPT를 현재 원본으로 사용하지 않았다.
- **Figure 2(a)**: 위에 조성·가격 기준·제조 경로·주문량, 가운데 재료비·가공비, 아래에 판매
  단가를 배치했다. 입력 쌍은 해당 원가 항목 위에서 합쳐지고, 두 원가 항목은 별도 경로로
  판매 단가에 연결된다. 주문량에서 마진율 m으로 가는 경로는 오른쪽 바깥으로 돌려 교차를
  피했다. 기존 수식과 인과 관계를 유지하고 설명 문구를 그림 안에 추가하지 않았다.
- 도식 높이를 76 mm로 확보하고 Figure 2 전체를 178 × 194 mm로 조정했다. 아래 (b)·(c)는
  기존 물리적 크기·글자 크기·수치·축 범위를 유지했다. 그림 수와 단 너비는 그대로여서
  그림 분량은 2,100 word-equivalent다. **Figure 1**은 H18의 다섯 아이콘과 배치를 유지하며
  글자·상자·연결선을 PowerPoint 객체로 옮겼다.
- PPT는 번들 슬라이드 라이브러리로 작성하고 패키지·폰트·슬라이드 크기·재가져오기를
  검증했다. Word나 PowerPoint의 문서 속성에 저자 정보를 넣지 않은 PPT 원본만 추적한다.
  Figure 1에는 슬라이드마다 편집 가능한 도형 38개와 기존 아이콘 이미지 5개,
  Figure 2(a)에는 도형 44개와 이미지 0개가 있다. 수식은 아래 첨자 텍스트와 분수선 등의
  편집 가능한 객체이며 Office 수식 객체는 아니다. 그룹 편집을 막던 생성기 기본 잠금도 제거했다.
- `scripts/export_note_diagram_slides.ps1`는 설치된 Microsoft PowerPoint에서 새 이름 없는
  사본을 창 없이 열어 PNG·SVG를 내보낸다. 원본 PPT를 저장하거나 덮어쓰지 않는다.
  `exports.json`에 원본과 출력 SHA-256을 기록하며, 그림 생성기는 PPT나 출력이 변경된 채
  재내보내기를 하지 않으면 오류를 낸다. PPT 원본은 직접 편집하고, 내보낸 PNG/SVG는
  생성기로만 갱신한다. 새 프로젝트 의존성·프레임워크·빌드 도구는 도입하지 않았다.
- 그림 생성기는 Figure 1 출력을 그대로 복사하고 Figure 2(a)를 Python 수치 패널과 조합한다.
  최종 Figure 2 SVG는 도식의 벡터 글자·선을 유지한다. Figure 1 캡션·AI 고지와 한글 원고,
  provenance도 PPT 구성으로 동기화했다. 기존 아이콘의 AI 생성 이력을 유지하며 새 이미지
  생성 호출은 없었다. 재생성 안내는 도식 원본 폴더의 README에 있다.
- 지정 다섯 검증을 순서대로 통과했고 pytest는 **6 passed**다. 새 두 사례는 PPT 원본 또는
  PNG가 내보내기 이후 바뀌었을 때 옛 결과를 조용히 사용하지 않고 실패하는지 검사한다.
  별도 검사로 `6a9b3a3` 대비 Figure 2(b,c)의 수치와 물리적 크기, Figure 3·4의 파일,
  동결 입력 7개와 원고 수치 삽입식이 그대로임을 확인했다. 원본 아이콘 이미지도 그대로다.
  두 언어의 PowerPoint 내보내기 네 장, 조합된 PNG와 벡터 SVG를 확인했다.
- 분량은 초록 151 + 본문 2,676 + 그림 2,100 = **4,927/5,000**, 그림 4개·표 0개·참고문헌
  14개·수치 참조 57개다. 원고 수치나 학술 주장을 바꾸지 않았다.
- **Word v30** 영문·한글 검토본을 재생성해 최신 그림 4개와 기존 메모 6개씩을 보존했다.
  이번에는 설치된 Microsoft Word에서 PDF를 내보내고 PDFium으로 페이지를 렌더하여
  영문 18쪽·한글 21쪽을 모두 확인했다. 그림이 잘리거나 글자가 겹치지 않으며, 긴 Figure 2·4
  캡션은 기존 검토용 서식에 따라 다음 페이지로 이어진다. 기존 LibreOffice 부재는 그대로지만
  실제 Word 렌더라는 대체 검증 경로를 확보했다. 문서의 개인 정보와 페이지 이미지는
  `_local/docx/qa_v30/`에만 보관한다. 슬라이드 작성·검사 자료는 `_local/note-figures/ppt-diagrams/`.
- 공개/상용 결정과 저자 선언은 미확정으로 유지했다. 외부 업로드·연락 없이 로컬 커밋만 한다.

### H20. 네 도판의 정보 계층과 원고 배치 재설계 (2026-09-13)

- 저자는 특히 Figure 2(a)의 구조를 거부하고 네 도판 모두를 학술지 수준으로 다시 구성하되,
  그림에는 핵심만 남기고 자세한 설명은 본문·캡션에 두도록 요청했다. 그림 수·단 너비·동결
  수치를 유지하면서 도식과 비교 패널의 공간 배분을 바꿨다. 새로운 학술 주장이나 출처는
  추가하지 않았으며 채택한 Step Method의 출처와 계산 조건을 보존했다.
- **Figure 1**: 기존 다섯 일러스트 아이콘을 가로로 배열하고 공통 분석 기록을 아래 한 줄로
  묶었다. 출처·가정·재현 정보의 세부 항목은 캡션에 명시했다. 크기는 178 × 64 mm이며
  아이콘 높이는 15 mm다. PPT에 들어간 이미지 파일은 v30과 바이트 단위로 같다. 이전 단계
  배경색만 PowerPoint의 네이티브 색상 변경 효과로 투명하게 표시한다. 생성 PNG나 원본
  이미지를 직접 고치지 않았고 새 이미지 생성 호출도 없었다. AI 사용 이력과 고지를 유지했다.
- **Figure 2(a)**: 입력 두 갈래 → 재료비·가공비 → 합산 → 간접비·마진 적용 → 판매 단가의
  흐름으로 간소화했다. 중복 상자와 외곽 마진 연결선을 없애고 수식·기호 정의·주문량과 마진의
  관계는 캡션과 기존 원가 절에서 설명한다. 도식 높이는 76에서 36 mm로 줄였다.
  **(b)**의 23개 반응군 막대는 폭 112 mm로 넓혔고, **(c)**는 공통 가로축을 쓰는 사례 세 개의
  가로 막대 비교로 재배치했다. 위·아래 막대의 의미를 캡션에 명시했다. 전체는 178 × 183 mm다.
- **Figure 3**: 원래의 두 로그 축과 단위를 유지하고 선 모양·색·끝 라벨로 금속을 구분한다.
  제목과 패널 문자의 위치를 맞추고 옅은 가로 보조선을 추가했다. 금속 14종 각각의 월평균
  관측값 89개, 총 1,246개는 그대로이며 평활화나 가격 지수 변환을 하지 않았다. 86 × 122 mm다.
- **Figure 4**: (a)의 30개 반응군을 위쪽 전체 폭으로 펼치고 범례를 같은 기준선에 맞췄다.
  (b)의 검사 다섯 개와 (c)의 순위 역전 아홉 사례를 아래에 나란히 배치했다. 설명 대상이나
  후보를 생략하지 않았으며 막대 너비·값·순서는 v30과 같다. (c)는 계속 같은 가격 조건에서
  서로 다른 두 후보의 원가를 비교한다. C01의 잘못된 제거 후 점수를 사용하지 않는다.
  전체는 178 × 203 mm이며 주 라벨은 7.5 pt다. 닫힌 축과 괄호 패널 문자를 유지했다.
- 현재 편집 원본은 **`docs/paper/diagram-sources-2026-09-13/`의 PPTX 두 개**다. 각 파일에
  영문·한글 두 슬라이드가 있고 슬라이드마다 편집 가능한 도형 23개가 있다. Figure 1에만
  원본 아이콘 다섯 개가 포함된다. 기존 Figure 1 PPT가 열려 있어 덮어쓸 수 없었으므로
  9월 12일 원본은 보존하고 새 폴더를 사용했다. 내보내기 스크립트와 그림 생성기를 새 경로에
  연결했다. 원본·내보내기 해시 검사를 유지하고 실제 PowerPoint에서 두 언어를 내보냈다.
  Figure 2 SVG의 도식은 래스터로 평탄화하지 않았다. 재생성 안내와 provenance를 갱신했다.
- 영문 원고 생성기와 한글 원고에서 네 캡션 및 Figure 1 설명을 동기화했다. 캡션으로 옮긴
  수식에는 기호의 단위와 G&A·SARD 정의를 포함한다. 전구체 요구량의 식과 조건은 기존 본문에
  그대로 있다. 중복된 설명을 줄이되 가격 비교의 제외 항목·생산 속도·순위 역전 해석은 보존했다.
- 지정 검증을 **영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts ruff**
  순서로 통과했다. pytest **6 passed**, 분량은 초록 151 + 본문 2,693 + 그림 2,100 =
  **4,944/5,000 word-equivalent**다. 그림 4개·표 0개·참고문헌 14개·수치 참조 57개를 유지했다.
  Matplotlib SVG의 줄 끝 공백은 생성기에서 정리한다. `git diff --check`도 통과했다.
- `_local/note-figures/ppt-diagrams/build/check_h20.py`는 `386eebc`와 비교해 모든 수치 삽입식,
  동결 입력 7개, 원본 아이콘 및 수치 마크를 확인한다. JSON은 Git의 줄바꿈 변환을 정규화해
  비교한다. 두 언어의 캔버스 밖 라벨, PPT 편집성·중립 메타데이터, SVG 벡터 보존도 검사했다.
  작성 파일·설계 기준·검사 결과는 해당 `_local/` 폴더에 남겼다.
- **Word v31** 영문·한글 검토본을 재생성해 각 문서의 최신 그림 네 개와 검토 메모 여섯 개를
  보존했다. 그림과 캡션 시작이 갈라지지 않도록 그림 문단의 다음 문단 연결을 설정했다.
  설치된 Word에서 PDF를 내보내고 PDFium으로 렌더한 영문 18쪽·한글 21쪽 전체를 확인했다.
  그림·수식·라벨의 잘림이나 겹침은 없으며, 긴 Figure 2·4 캡션은 기존 검토 서식에서 다음
  페이지로 이어진다. 문서와 저자 정보·페이지 검토 기록은 `_local/docx/`에만 있다.
- 버전·라이선스·공개 방식과 저자 선언은 변경하지 않았다. 외부 업로드나 연락 없이 로컬에만
  보관하며, 공개/상용 결정은 여전히 저자의 미확정 안건이다.

### H21. GPT·Gemini 도식 생성과 비교 시안 (2026-09-13)

- 저자는 v31의 도식 품질을 다시 지적하고 프롬프트를 작성하여 GPT와 Gemini에서 실제 이미지를
  생성하도록 요청했다. 이전의 Python 수치 결과 제외 지시에 따라 **Figure 1과 Figure 2(a)**를
  생성했다. Figure 2(b,c)·3·4의 수치 그래프는 이미지 모델에 다시 그리게 하지 않았다.
- 두 모델에 같은 최초 프롬프트를 사용했다. Figure 1은 다섯 단계의 과학 일러스트와 공통 분석
  기록을, Figure 2(a)는 재료비·가공비의 합산과 간접비·마진 조정을 통한 판매 단가 추정을
  보여 준다. 수식·설명 문단은 도식에서 제외했다. 혼합·건조·소성 장면은 대표적 준비 작업의
  개념 그림이며 모든 촉매에 공통인 공정이나 실험 관측 결과라는 뜻이 아니다.
- OpenAI 내장 이미지 생성 도구에서 4장, Gemini 웹 인터페이스에서 7장, **총 11장**을 실제
  생성하고 원본 PNG를 보존했다. Gemini 대화 모드는 `3.1 Pro`/`Pro`였으나 양쪽 서비스의
  정확한 이미지 모델 버전은 확인 못 함으로 기록했다. 별도 유료 API·결제는 사용하지 않았다.
  저자 정보·원고 전체·동결 수치 파일·CatCost 원자료는 보내지 않았다. 명시적으로 요청된
  모델 생성에 필요한 도식 프롬프트와 Gemini의 기존 생성 도식 1장만 전송했다.
- 시각 검사 후 GPT v2 두 장을 추천 시안으로, Gemini Figure 1 v4와 Figure 2(a) v3을 비교안으로
  남겼다. GPT 수정본은 불필요한 화학구조·작은 자료 곡선을 제거하고 연결선·기록 연결을
  정리했다. 초기 Gemini 그림의 중복 라벨 및 수정 중 발생한 글자 겹침은 비채택 중간본으로
  명시하고 새로 생성했다. Gemini Figure 2(a) v3에는 요청 목록 밖의 작은 `Price-record`
  라벨이 남아 있어 비교 화면에도 표시했다. 생성 그림을 투고용 완성본이라고 판정하지 않았다.
- 최초 공통 프롬프트와 생성 범위는 `docs/paper/figure-generation-prompts-2026-09-13.md`에,
  프롬프트 9개·원본 11장·모델/버전 대응·해시·검토 의견·확대 가능한 HTML 비교 화면은
  `_local/note-figures/ai-candidates-2026-09-13/`에 보관했다. 원본 다운로드와 작업 폴더의
  PNG 11개가 모두 SHA-256 기준으로 일치한다. 이미지의 수작업 수정이나 사후 업스케일은
  없었다. 실제 픽셀 크기를 기록했으며 벡터 파일이나 400 dpi라고 주장하지 않는다.
- 이번 결과는 원고 반영 전 시안이다. 정식 PPT·원고 생성기·두 언어 원고·Word v31을 바꾸지
  않았다. 채택 시 생성 파이프라인을 통해 통합하고 영문·한글 캡션과 AI 사용 고지를 함께
  고친 뒤 Word를 재생성해야 한다. 정식 생성 PNG/SVG를 직접 덮어쓰지 않는다.
- 지정한 다섯 검증을 영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts ruff
  순서대로 다시 통과했다. **6 passed**, **4,944/5,000**, 그림 4·표 0을 유지하며 재생성 후
  정식 그림과 원고에는 Git 차이가 없다. 비교 화면의 그림 전환·원본 확대·표시를 실제
  브라우저에서 확인했다. GitHub·Zenodo 게시, 푸시, 외부 연락, 결제 없이 로컬 커밋만 한다.

### H22. GPT v2 도식 채택과 Word v32 반영 (2026-09-13)

- 저자가 두 그림 모두 GPT 쪽이 낫다고 선택하여 **Figure 1과 Figure 2(a)의 GPT v2**를
  정식 원고에 반영했다. 선택된 영문 PNG는 원본 바이트 그대로 보존했다. OpenAI 내장 이미지
  생성 도구를 두 번 더 호출해 각각의 영문 이미지를 참조한 한글 라벨판을 만들었다.
  한글판의 구도와 기호를 확인했으며, 라벨 외 픽셀까지 영문과 동일하다고 주장하지 않는다.
  정확한 이미지 모델 버전은 도구가 공개하지 않아 **확인 못 함**이다.
- 현재 소스는 `docs/paper/diagram-sources-2026-09-13-gpt/`다. 원본 PNG 네 개, 두 언어
  슬라이드를 담은 PPTX 두 개, 실제 PowerPoint의 PNG/SVG 내보내기, SHA-256 목록과
  프롬프트를 함께 보관했다. 이전 PPT와 열린 파일은 보존했다. 도식은 이번에 선택한
  래스터 이미지이며 글자·연결선이 개별 편집 가능한 벡터 도형이라는 주장은 하지 않는다.
  PPTX는 이미지와 흰 바탕으로 구성되고, 포함된 이미지 바이트는 원본과 일치한다.
- Figure 1의 원본은 **2060 × 763**, Figure 2(a)는 **2172 × 724** 픽셀이다. 폭 178 mm에서
  각각 **293.96 dpi**, **309.94 dpi**에 해당한다. PowerPoint의 400 dpi 내보내기는 캔버스
  해상도이며 원본에 없는 세부 묘사를 추가하지 않는다. 수작업 이미지 편집·업스케일은 없었다.
  SVG 도식에도 래스터 원본이 포함되며, 결합된 Figure 2(b,c)의 수치 그래프는 벡터를 유지한다.
- Figure 1은 178 × 65.930 mm, Figure 2(a)는 178 × 59.333 mm의 원래 비율을 유지한다.
  Figure 2 전체 높이를 183에서 **207 mm**로 늘려 (b,c)를 아래로 옮기되 수치 축의 물리적
  크기를 보존했다. 원본에 포함된 (a)와 중복되지 않도록 생성기의 (a) 라벨을 제거했다.
  내보내기 스크립트와 그림 생성기가 새 소스를 사용하며 원본·출력 해시 검사는 그대로다.
- 영문 생성기와 한글 원고의 Figure 1·2 캡션 및 AI 사용 고지를 함께 갱신했다. 장비·촉매
  모습은 개념도이고 제조 장면은 공통 필수 공정이 아닌 예시임을 명시했다. 비용 식·단위·
  기호 정의는 캡션과 본문에 유지했다. 새 원고는 생성기로 재생성했으며 생성물을 직접
  편집하지 않았다. 그림 4개·표 0개·참고문헌 14개·수치 참조 57개를 유지한다.
- 지정한 다섯 검증을 **영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts
  ruff** 순서로 통과했다. pytest **6 passed**. 분량은 초록 151 + 본문 2,691 + 그림 2,100 =
  **4,942/5,000 word-equivalent**다. `check_h22.py`는 `abf9304`와 비교하여 수치 삽입식,
  Figure 2의 구성값 69개와 검증값 6개 및 축 크기, 동결 JSON 7개를 확인했다. Figure 3·4의
  PNG 바이트와 SVG 내용은 그대로다. 텍스트 파일은 Git의 CRLF/LF 차이를 정규화해 비교했다.
- **Word v32** 영문·한글 검토본을 재생성하고 기존 메모 여섯 개씩과 현재 그림 네 개씩을
  보존했다. 설치된 Word에서 PDF로 내보낸 뒤 PDFium으로 렌더한 영문 **18쪽**, 한글 **22쪽**,
  총 **40쪽을 개별 이미지로 확인**했다. 그림·라벨·수식의 잘림은 없고 그림과 캡션 시작은
  같은 페이지에 있다. 긴 Figure 2·4 캡션은 기존 검토 서식에서 다음 페이지로 이어진다.
- 작성·검사 자료는 `_local/note-figures/ppt-diagrams/build/`의 `build_h22.mjs`,
  `patch_h22.py`, `check_h22.py`, `h22_checks.json`에, Word 재생성과 검사는
  `_local/docx/rebuild_v32.py`, `_local/docx/qa_v32/`에 있다. 저자 정보와 Word 검토본은
  모두 `_local/`에만 둔다. 라이선스·버전·공개/상용 결정과 저자 선언은 바꾸지 않았으며,
  GitHub·Zenodo 게시·푸시·연락·결제 없이 로컬 커밋만 한다.

### H23. 제목에 COMET 정식 명칭 사용 (2026-09-13)

- 저자가 제목에 COMET의 이름을 풀어 써야 하지 않느냐고 지적하여 제목을
  **COMET: Catalyst Overall Manufacturing Estimation Tool**로 변경했다. 프로젝트의
  `AGENTS.md`와 초록에 이미 사용된 정식 명칭이며, 새 이름을 만든 것이 아니다.
  학술지의 의무 형식이라는 주장은 하지 않고 저자가 요청한 명명 방식으로 통일했다.
- `scripts/build_application_note.py`의 제목을 수정해 영문 원고를 재생성했다. 한글 원고의
  제목에도 동일한 정식 영문 명칭을 사용한다. 제목 외 본문·캡션·참고문헌은 그대로다.
- 지정한 다섯 검증을 영문 그림 → 한글 그림 → 원고 `--check` → 노트 pytest → scripts ruff
  순서로 통과했다. **6 passed**, **4,942/5,000**이며 그림·수치·분량 검사 결과는 바뀌지 않았다.
- Word **v33**을 만들고 메모 여섯 개씩과 최신 그림 네 개씩을 보존했다. 실제 Word/PDFium
  렌더는 영문 18쪽·한글 22쪽이다. 제목은 두 언어 모두 한 줄에 들어간다. 바뀐 영문 1쪽과
  한글 1–5쪽을 개별 확인했고, 나머지 34쪽은 이미 확인한 v32 렌더와 픽셀 단위로 일치한다.
  한글 Figure 1은 3쪽으로 이동했으며 캡션 시작도 같은 페이지에 있고 나머지는 4쪽에 이어진다.
- `_local/docx/rebuild_v33.py`와 `qa_v33/`에 재생성·문단 비교·페이지 확인 기록을 남겼다.
  두 문서 모두 변경된 문단은 제목 하나뿐이다. 저자 정보와 Word는 `_local/`에만 두며,
  외부 업로드 없이 로컬 커밋한다.

### H24. 그림 글자 확대와 짧은 제목·본문 중심 설명 (2026-09-13)

- 저자는 그림 네 장을 Nature 논문처럼 정돈하고 글자를 조금 키우며, 긴 그림 제목·설명은
  본문으로 옮기도록 요청했다. 정렬·간결한 서체 원칙을 참고하되 JCIM 원고이며 Nature의
  세부 도판 규격을 준수한다는 주장은 하지 않는다. 기존의 사방 테두리와 괄호 패널 표기를
  유지했다. 새 프레임워크·자료 수집·수치 분석은 추가하지 않았다.
- Figure 1·2(a)는 채택된 GPT v2 영문 그림을 입력으로 OpenAI 이미지 생성 도구에서 글자를
  제거한 뒤, 반환된 PNG를 수정 없이 PPT에 넣고 영어·한국어 라벨을 편집 가능한 텍스트로
  추가했다. 두 언어가 같은 그림을 사용한다. 새 생성 결과의 비문자 픽셀이 이전 이미지와
  같다는 주장은 하지 않는다. 도구가 정확한 모델 버전을 노출하지 않아 **확인 못 함**으로
  기록했다. 원본·입력 해시·정확한 프롬프트·출처는
  `docs/paper/diagram-sources-2026-09-13-h24/`에 있다. 이전 도식은 보존한다.
- Figure 1 단계 이름은 9.5 pt, 기록 항목은 8.5 pt다. Figure 2(a)의 항목은 8.5–9.5 pt,
  원가 기호는 12 pt와 아래첨자이며 텍스트 상자는 슬라이드당 9개·13개다. 실제 PowerPoint
  내보내기를 확인하여 노드 안의 글자와 판매 단가의 줄바꿈을 조정했다. 그림·연결선은
  래스터이고 텍스트는 벡터이므로 완전한 벡터 도식이라고 표현하지 않는다.
- 수치 패널의 축·범례·값·반응군 이름은 주로 7–8 pt에서 **8.5–9 pt**로 키우고 패널 문자는
  10 pt로 맞췄다. Figure 2(b)·4(a)의 왼쪽 여백을 51에서 59 mm로 늘리고 범례를 축 시작에
  정렬했다. Figure 3의 선을 0.9에서 1.05 pt로 키우고 원소 라벨 간격을 새 글자 크기에 맞췄다.
  값 라벨을 위한 Figure 2(c)·4(c)의 가로축 여유 범위만 넓혔다. 음의 값이나 작은 막대도
  생략하지 않았다. 출력 크기·패널 수·모든 값·분모·행 순서·로그 축은 유지했다.
- 캡션 첫 문장은 **COMET workflow / Cost estimation / Metal price history /
  Ranking sensitivity**로 단순화했다. 캡션 단어 수는 같은 로컬 어휘 계수로
  **104/279/96/231 → 18/35/29/47**(총 710 → 129)이다. 비용 식과 변수 정의, 가격 변동 비율,
  순위 빈도·후보 제거 검사·원가 차이의 해석, Pt/C 금속 가치 제외 및 USY 정의를 본문에
  배치했다. 이미 본문에 있던 설명은 중복해서 옮기지 않고 덜어냈다. 패널·단위·약어 정의와
  이미지 생성 고지는 짧게 남겼다. 생성기를 수정해 영문을 재생성하고 한글 원고도 동기화했다.
- 초록 151 + 본문 2,723 + 그림 2,100 = **4,974/5,000 word-equivalent**. 그림 4개·표 0개·
  참고문헌 14개·JSON 수치 참조 57개다. `check_h24.py`는 `5126423` 대비 삽입식 AST,
  동결 JSON 7개, Figure 2의 막대 69+6개, Figure 3의 관측 1,246개, Figure 4의 막대
  90+10+9개와 척도의 동일성을 확인했다. 영문·한글의 현재 라벨 크기는 최소 8.5 pt이며
  텍스트 경계와 소스·내보내기 해시 검사도 통과했다.
- 필수 검증을 **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff**
  순서로 통과했다. **6 passed**, ruff 통과. 생성된 원고나 그림 파일을 직접 수정하지 않았다.
- Word **v34** 영문 16쪽·한글 19쪽을 실제 Word에서 PDF로 내보내 PDFium으로 렌더하고,
  **총 35쪽을 개별 확인**했다. 캡션은 짧은 제목만 굵게, 본문 설명은 보통 굵기·1.15줄로
  조정해 **그림 네 장과 각 캡션 전체가 같은 쪽**에 들어간다. 본문 서식은 기존 검토본을
  유지했다. 음수 부호가 숫자와 다른 줄에 놓인 곳은 Word 작성기에서 줄바꿈을 막고
  바뀐 쪽을 다시 확인했다. 댓글 여섯 개씩과 최신 그림 네 개씩을 보존했다.
- 작성·검사 파일은 `_local/note-figures/ppt-diagrams/build/`의 `build_h24.mjs`,
  `patch_h24.py`, `check_h24.py`, `h24-checks.json`과 `_local/docx/rebuild_v34.py`,
  `qa_v34/`에 있다. 저자 정보와 Word·PDF·페이지 검토 자료는 모두 `_local/`에만 둔다.
  버전·라이선스·공개/상용 결정은 그대로이며 외부 게시·푸시·연락·결제 없이 로컬 커밋한다.

### H25. 초록과 서론에서 COMET의 기여를 중심으로 재구성 (2026-09-13)

- 저자는 초록의 CatCost 언급이 선행 소프트웨어를 따라 구현한 도구라는 인상을 준다고
  지적했다. 초록에서 CatCost와 Step Method의 명칭·구현 중심 설명을 덜어내고, COMET이
  가격 자료 관리·제조 원가 추정·후보 순위 분석을 재현 가능한 과정으로 통합한다는 기여를
  먼저 제시했다. 입력 출처, 민감도 변수, 문헌 계산 검증과 산업 원가 검증의 한계는 남겼다.
- 서론 세 문단을 선행 연구의 성과 → 후보 선택에서 검토할 조건 → COMET이 제공하는
  통합 기능 순서로 다시 썼다. CatCost의 원가·환경 평가 및 합성 방법·규모 분석은 선행
  성과로 인용하고, COMET의 가격 갱신·과거 가격 재계산·순위 민감도 분석을 구체적으로
  설명한다. CatCost에 특정 기능이 없었다거나 모든 한계를 해결했다는 주장은 하지 않는다.
  본문에서 CatCost라는 명칭은 서론과 참고문헌에만 남는다. 기존 계산법의 출처는 유지한다.
- CatCost의 범위는 [연구기관의 공식 초록](https://research-hub.nlr.gov/en/publications/early-stage-evaluation-of-catalyst-manufacturing-cost-and-environ-2/)으로 확인했다.
  유료 전문을 확인했다는 주장은 하지 않는다. 기존 DOI `10.1038/s41929-022-00759-6`은
  Crossref에서 재확인했다. Step Method DOI `10.1021/acs.oprd.8b00245`의 이번 Crossref
  요청은 HTTP 429로 **확인 못 함**이며 기존 서지 정보는 바꾸지 않았다. 공개된
  [DOE 수록 원고](https://www.osti.gov/servlets/purl/1477947)에서 방법의 설명을 확인했다.
- 영문 생성기의 초록 하나와 서론 세 문단을 수정하고 한글 원고를 동기화했다. 영문은
  생성기로 재생성했다. H24 `fb4bc1d` 대비 Software implementation 이후의 내용,
  모든 수치 삽입식, 그림·캡션·참고문헌을 보존했다. 그림 4개·표 0개·참고문헌 14개,
  JSON 참조 57개이며 초록 134 + 본문 2,716 + 그림 2,100 = **4,950/5,000**이다.
- 필수 검증을 **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff**
  순서로 통과했다. **6 passed**, ruff 통과. 중간 수정 후 재생성이 누락된 원고를
  `--check`가 감지했으며, 생성기로 갱신한 뒤 다섯 검사를 위 순서로 모두 다시 통과했다.
- Word **v35** 영문 16쪽·한글 19쪽을 실제 Word/PDFium으로 렌더했다. 서론 중복 설명을
  줄여 Figure 2 앞에 두 줄만 남던 중간안의 페이지를 없앴다. 최종본의 영문 7쪽·한글 2쪽을
  개별 확인했고 나머지 26쪽은 검증된 v34 페이지 PNG와 바이트 단위로 일치한다.
  네 그림과 완전한 캡션은 각각 같은 페이지에 있으며 댓글 여섯 개씩을 보존했다.
- 재생성·검사 자료는 `_local/docx/rebuild_v35.py`와 `qa_v35/`에 있다. 저자 정보와 Word는
  `_local/`에만 두고, 공개/상용 결정·버전·라이선스는 유지하며 외부 게시 없이 로컬 커밋한다.

### H26. Figure 1 하단 기록 항목 확대 (2026-09-13)

- 저자는 Figure 1의 위쪽은 좋지만 아래 네 항목이 너무 작다고 지적했다. 위쪽 다섯 단계의
  그림·크기·라벨 위치를 보존하고 하단을 큰 개념도 네 개와 아래쪽 제목으로 구성했다.
  분석 기록은 데이터베이스와 저장 문서, 데이터 출처는 날짜·연결을 나타낸 자료 묶음,
  계산 가정은 톱니바퀴와 조절 항목, 재현 정보는 반복 계산을 나타낸 두 문서로 표현한다.
  문서 안의 막대와 선은 개념 표현이며 실제 계산 결과나 실험 자료가 아니다.
- 새 하단 그림은 H24의 글자 없는 Figure 1을 스타일 참고로 제공하여 OpenAI 내장 이미지
  생성 도구로 생성했다. 정확한 모델 버전은 **확인 못 함**이다. 도구의 PNG 원본 바이트를
  그대로 PPT에 포함하고 PowerPoint의 네이티브 그림 자르기 기능으로 바깥 여백을 정리했다.
  기존 위쪽 PNG도 원본 바이트를 포함하며 옛 하단 띠만 네이티브 자르기로 가렸다.
  생성 도판·이미지를 직접 편집하지 않았고 원고·저자 정보·동결 데이터는 전송하지 않았다.
- 하단 라벨은 **8.5 → 10.5 pt, 굵게** 바꾸고 그림 아래에 배치했다. 위쪽 라벨은 9.5 pt로
  유지한다. 새 연결선은 편집 가능한 PPT 도형이며 한글·영문은 같은 그림 원본을 사용한다.
  Figure 1 크기는 **178 × 102 mm**로 늘었다. 원본은 위쪽 2060 × 763, 새 하단 2172 × 724
  픽셀이고 PPT에 배치한 폭에서 각각 약 294·332 dpi다. 400 dpi 출력은 새 세부 묘사를
  추가하지 않는다. SVG도 래스터 그림과 벡터 글자·연결선을 함께 포함한다.
- 현재 도식 소스는 `docs/paper/diagram-sources-2026-09-13-h26/`다. PPT, 내보내기, 원본,
  정확한 프롬프트와 SHA-256을 보관했다. 이전 소스는 유지하고 Figure 2(a) PPT는 H24와
  바이트 단위로 같다. 작성 도구가 비대칭 자르기를 중앙 자르기로 내보낸 중간안은 소스
  OOXML의 자르기 좌표를 바로잡아 다시 내보냈다. 영어·한글 슬라이드를 각각 확인했다.
- 원고 생성기와 한글 원고에는 새 기록 그림의 AI 생성 고지 한 문장만 추가했다. 짧은 캡션,
  초록·서론과 연구 내용은 유지한다. **초록 134 + 본문 2,730 + 그림 2,100 = 4,964/5,000**,
  그림 4개·표 0개·참고문헌 14개·JSON 참조 57개다. 모든 수치 삽입식은 그대로이며
  Figure 2·3·4의 PNG 바이트와 SVG 내용도 동일하다.
- 필수 검증을 **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff**
  순서로 통과했다. **6 passed**, ruff 통과. 원본·내보내기 해시, 원본 이미지 포함 여부,
  라벨 개수와 글자 크기, 문서의 현재 그림·댓글을 확인했다. 위쪽은 원본·배치가 유지되지만
  내보내기 재표본화 때문에 출력 PNG 픽셀까지 같다고 주장하지 않는다.
- Word **v36**은 영문 16쪽·한글 19쪽이다. 커진 Figure 1로 생긴 공백을 없애기 위해
  영문 Word에서만 Figure 2와 캡션을 재료비·가공비 설명 두 문단 뒤에 배치했다. 본문
  문장이나 그림 순서는 바꾸지 않았다. 실제 Word/PDFium 렌더의 바뀐 영문 11쪽·한글
  5쪽을 개별 확인했고 나머지 19쪽은 검증된 v35 페이지와 바이트 단위로 같다.
  네 그림과 완전한 캡션은 각각 같은 페이지에 들어가며 댓글 여섯 개씩을 보존했다.
- 작성·검사 기록은 `_local/note-figures/ppt-diagrams/build/build_h26.mjs`, `patch_h26.py`,
  `_local/docx/rebuild_v36.py`, `qa_v36/`에 있다. 저자 정보는 `_local/`에만 두며 공개/상용
  결정·버전·라이선스를 유지하고 외부 게시·푸시·결제 없이 로컬 커밋한다.

### H27. 관측 가격에 따른 전 반응군 원가·추천 역전 분석 (2026-09-13)

- 저자는 일부 사례에 머물렀던 그림을 넘어 에너지 전환 반응군 전체에서 가격에 따른
  후보 역전과 해석 가능한 결과를 요청했다. **30개 반응군·116개 후보·168개 후보쌍**을
  전수 계산했다. 기존 89개월(2019-01~2026-05)과 새 일별 공통 176일
  (2026-01-02~2026-09-11), 총 **30,740 후보-상태**다. 후보·조성·주문량·공정·지지체·
  기준 출처 표기와 반응군별 균형 가중치를 고정하며 무작위 추출·후보 제거는 하지 않았다.
- 월별은 기존 14개 금속 가격, 일별은 JM 뉴욕 Pt/Pd/Rh/Ir/Ru와 Westmetall LME 현물
  Al/Cu/Ni/Sn/Zn을 바꾼다. 일별에서 **Co/Mo/Au/Ag 등 나머지 가격은 2026-05 기준값**이다.
  결측일 보간이나 관측일의 검색일 대체는 없다. 436개 JM 날짜와 176개 LME 날짜의
  정확한 교집합을 사용한다. 모든 성분의 실시간 원가나 과거 제조 조건의 재현이라고
  주장하지 않으며, 현재 2026년 모델에 관측 금속 가격만 바꾼 조건부 재계산이다.
- 수집 중 두 문제를 확인했다. 기존 `fetch_johnson_matthey_history`의 설명과 달리 긴
  기본 차트 요청은 월평균을 반환한다. 또한 역순 금속 요청의 DAILY CSV는 제목과 값의
  순서가 맞지 않았다. 두 탐색 응답은 제외했다. 새 수집기는 공식 페이지의 명시적
  DAILY/USA 다운로드를 Pt/Pd/Rh/Ir/Ru 순서로 사용하고, 마지막 다섯 값을 별도 현재 시세와
  각각 대조한다. 생산용 수집 함수나 기존 월별 자료는 변경하지 않았다. 무료 공개 경로만
  사용했고 원자료·제외 응답·최종 `daily_prices_final.json`은 `_local/price-crossovers-2026-09-13/`
  에 보관한다. 공개 접근과 재배포 권리는 구분하며 새 원자료를 추적 파일로 옮기지 않았다.
- `scripts/run_price_crossovers.py`는 메모리 DB에서 계산하며 기존 기준 후보 116개와
  2,670개 반응군-월 원장을 현재 엔진으로 재현해 일치를 확인한다. 새 결과는
  `docs/paper/price-crossovers-2026-09-13/`에 별도로 동결했다. 기존 논문 JSON은 불변이다.
  원가·앱 총점·비가격 점수 고정·반올림 제거·기준 정규화 범위 고정을 구분한다.
  원가 허용치는 출력 자릿수에 맞춰 **0.0002 USD/lb, 0.000002 USD/cm²**다. 초기 면적
  허용치를 교정하면서 AEM 비우승 후보쌍의 근소한 역전 구간은 넓어졌지만 원가·점수·
  첫 순위 원장과 반응군 집계는 동일했다. 1% 차이 기준은 모델 불확실성 범위가 아니다.
- 월별 최저 원가 변경은 6개 반응군, 어떤 후보쌍의 원가 변경은 10개 반응군·14/168쌍이다.
  암모니아 분해 **8회**, 건식개질 **9회**, 수성가스 전환 **11회**가 대표 열촉매 결과다.
  2025-09→10 Co 가격 15.1872→19.5706 USD/lb 변화로 암모니아 Co/Mg–La와 Ni/알루미나,
  건식개질 Ni–Co/Al–Mg와 Ni/제올라이트의 원가 우위가 각각 역전된다. Co만 바꾼 재계산이
  후보 원가 차이 변화 0.3310 중 0.3300, 0.3638 중 0.3631 USD/lb를 설명한다.
  세 열촉매 반응군의 균형 추천 1위는 유지된다. 최저 원가와 종합 추천을 혼용하지 않는다.
- 일별 최저 원가 변경은 질소 환원군 한 곳이나 수계 Cu 쪽 최대 우위가 0.70%이고,
  플라스마 등 서로 다른 경로의 분말 원가 비교이므로 주된 촉매 발견으로 채택하지 않는다.
  비가격 점수 고정·반올림 제거 후 일별 1위 변경은 광촉매군 4회, CO 선택 산화 6회,
  질소 환원 14회다. 광촉매 Pt/TiO₂의 1월 19→20일 조건부 점수 경계는 Pt 약
  2,419 USD/troy oz(Rh 10,100 고정)다. 20일 앱 총점은 동점, 엄격한 차이는 21일에 있다.
  작은 점수 차이·미선택 Rh 후보의 정규화 영향·실제 반응 성능 비동등성을 명시했다.
- CO₂ 메탄화의 일별 앱 1위 변경 7회는 비가격 점수를 고정하면 사라져, 재료비 비중으로
  가중한 출처 점수의 영향으로 분리했다. PEM 면적 원가 네 후보와 AEM 세 후보는 고정
  라이브러리/기본 가격 때문에 월별 원가가 일정하다. 이들의 0을 시장 가격 강건성 증거로
  해석하지 않는다. Co/Mg–La 조성 근사, WGS 운전 구간, 전기촉매 제품·전극 면적/질량
  경계 차이도 영문·한글 보고서에 적었다. 새로운 문헌이나 DOI는 추가하지 않았다.
- `scripts/analyze_price_crossover_cases.py`는 단일 금속 효과와 51개 Ni 가격의 Co 경계를
  직접 재계산한다. 도판은 기존 **draw_application_note_figures.py의 --crossovers** 옵션으로만
  만든다. 대표 원가·경계 4패널, 일별 점수 2패널, 30반응군 전수 집계의 세 도판을
  EN/KO PNG·SVG·PDF로 만들고, 후보 전부를 담은 30쪽 PDF를 언어별로 만들었다.
  세부 PDF는 반올림 조성의 `0.0% Pd`나 중복 IrO₂ 이름 대신 고유 후보 식별자를 쓴다.
  실제 계산 그림에는 생성형 이미지 도구나 이미지 편집을 사용하지 않았다.
- **영문 그림 → 한글 그림 → 원고 --check → 기존 노트 pytest → scripts ruff** 순서 통과.
  기존 노트 **6 passed**, 새 교집합·집계 주기·단위·동점·점수·독립 Co 효과·경계 검사
  **6 passed**다. 30,740 CSV 행을 JSON과 대조했고 입력·계산 소스 해시가 일치한다.
  대표 EN/KO PNG 여섯 장과 PDFium의 여섯 쪽 모음 열 장(총 60쪽)을 시각 확인했으며,
  제목·축 제목·범례의 영역 검사 66건을 통과했다. `verification.json`에 결과와 해시를 기록했다.
- 이번 요청은 새 결과의 전수 분석·도판화로 완료했다. 현재 원고 생성기·영문/한글 본문·
  Word v36·기존 네 그림은 바꾸지 않아 **4,964/5,000**, 그림 4개·표 0개·참고문헌 14개다.
  새 연구 도판을 원고에 넣을 때는 기존 그림과 교체하고 본문·캡션을 생성기 및 한글판에서
  함께 편집해야 한다. 저자 정보·공개/상용 결정·버전·라이선스는 유지하며 로컬 커밋만 한다.

### H28. 논문 및 가격 역전 도판의 질량 단위 통일 (2026-09-14)

- 저자의 요청에 따라 영문·한글 본문, 수식의 질량 정의, 캡션, 그림의 수치·축, 가격 역전
  보고서와 CSV의 질량 기준 가격·원가를 모두 **USD/kg**으로 통일했다. 주문량은 kg,
  유효 생산 속도는 kg/day다. 전극 면적 기준 AEM/PEM 비용은 **USD/cm²**를 유지한다.
  면적 비용을 질량 비용으로 바꾸려면 별도의 질량·면적 대응 조건이 필요하다.
- `scripts/paper_units.py`에 정확한 환산 상수 **1 lb = 0.45359237 kg**, **1 troy oz =
  0.0311034768 kg**, **1 short ton = 907.18474 kg**을 두었다. 반올림된 이전 문구를
  다시 환산하지 않고 동결 JSON의 저장 정밀도에서 계산한 뒤 표시 단계에서 반올림한다.
  원고 생성기는 17개 변환의 원본 JSON 키·원값·계수·결과를 검사 JSON에 남긴다.
- 본문의 주문량은 18,143.7 kg, Ni 예시 판매 단가는 11.49 USD/kg이다. 문헌 예시와 시장
  가격도 같은 기준으로 환산했다. 정규화 범위와 후보 간 차이는 고정 문구 대신 원본
  수치에서 계산한다. 생성기가 영문 MD를 만들고 한글 원고와 Word도 함께 갱신했다.
- Figure 2(b)의 23개 판매 단가, Figure 3의 14금속 × 89개월 = **1,246개 관측값**,
  새 역전 도판의 원가 곡선과 Ni–Co 경계를 생성기에서 환산했다. 귀금속 가격 축은
  커진 값에 맞춰 10의 거듭제곱으로 표시한다. 두 가격 축의 로그 척도·날짜·관측값은 유지한다.
  Figure 1·4와 역전 연구의 점수·횟수 그림은 변하지 않았다. PNG/PDF는 이전과 바이트가
  같고 SVG 내용은 CRLF/LF를 정규화하면 같다. 생성 이미지나 SVG를 직접 편집하지 않았다.
- `scripts/export_price_crossovers_kg.py`가 동결 연구 JSON에서 **30,740행** 후보 CSV,
  60행 반응군 집계 CSV, `publication_mechanisms_kg.json`을 재생성한다. 질량 단위만
  바꾸며 점수, 동점·순위·역전 이벤트, 면적 기준 비용은 그대로다. Pt 경계는 원본의 정밀한
  값에서 약 **77,786 USD/kg**으로 환산했다. 점수 차이와 가격 경계의 단위를 구분했다.
- 동결 JSON·시장 관측·계산 엔진·원본 소스 해시는 그대로다. 공개 가격을 새로 수집하거나
  원자료를 재배포하지 않았다. 기존 비용 경계와 간접비·판매 마진·경로별 추가비용을
  제거하지 않았으며 단위 환산을 새로운 제조원가 계산이나 새로운 발견으로 해석하지 않는다.
- 최종 검증은 **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff**
  순서로 모두 통과했다. 노트 **6 passed**, 추가 환산·역전 검사 **10 passed**다. CSV 전 행의
  환산값·점수·우승 후보, 원본 해시, 1,246개 가격 관측값과 원고 참조를 대조했다.
  새 도판의 영문·한글 30쪽 PDF를 모두 시각 확인했고 레이아웃 검사 66건을 통과했다.
  최종 결과와 해시는 역전 연구 `verification.json`에 갱신했다.
- Word **v37**은 영문 **16쪽**, 한글 **19쪽**이며 댓글 여섯 개씩과 현재 그림 네 개씩을
  보존했다. 숫자와 질량 단위 사이에는 줄 바꿈 없는 공백을 사용한다. 번들 LibreOffice
  실행 파일이 없어 정식 렌더러 시도 로그를 남기고 기존 Microsoft Word → PDFium 경로로
  렌더했다. 바뀐 16쪽은 개별 확인했고 나머지 19쪽은 검증된 v36 페이지 해시와 같다.
  네 그림과 완전한 캡션은 각각 같은 쪽에 있다. 최종 QA와 재생성 도구는 `_local/` 전용이다.
- 최종 분량은 **초록 134 + 본문 2,731 + 그림 2,100 = 4,965/5,000**이다. 그림 4개·표 0개·
  참고문헌 14개·JSON 참조 57개를 유지한다. 새 역전 연구의 결과는 여전히 별도 패키지이며
  본문에 추가하지 않았다. 저자 정보·공개/상용 결정·버전·라이선스를 유지하고 로컬 커밋만 한다.

### H29. 검토 원고의 그림 제작 도구 설명 삭제 (2026-09-14)

- 저자는 Figure 1 캡션의 OpenAI·PowerPoint 제작 설명을 지적하며 같은 종류의 문구를
  모두 삭제하도록 요청했다. 영문 생성기와 한글 원고에서 Figure 1·2 캡션의 제작 도구 설명,
  감사의 글의 AI 지원·이미지 제작·라벨 편집 과정 문단을 삭제했다. Figure 1은 계산 흐름이라는
  짧은 제목만, Figure 2는 패널의 내용·단위·약어 풀이만 남긴다. 생성 MD를 직접 고치지 않았다.
- 기존 인수인계 §6의 고지 유지 지시와 최신 저자 요청이 달라 ACS 공식
  [AI 사용 지침](https://researcher-resources.acs.org/publish/aipolicy)을 이날 다시 확인했다.
  ACS는 AI 텍스트·이미지 생성에 대한 감사의 글 고지와 AI 그림의 간단한 캡션 고지를 요구한다.
  이번 삭제는 로컬 검토본에 적용한 편집 결정이며, 고지가 빠진 상태를 ACS 투고 완료본으로
  취급하지 않는다. 원래 제작 이력은 보존하고 투고용 최소 문안은 `_local/`에 별도로 남겼다.
  실제 투고 전 고지를 반영해야 한다는 점을 저자에게 설명했다. 출판사에 연락하지 않았다.
- 그림 생성기를 영문·한글 순서로 다시 실행했다. 네 그림과 별도 역전 연구 패키지는 이전
  커밋과 같으며 kg 단위 변환 17건·JSON 참조 57건·모든 과학적 수치·참고문헌을 유지한다.
  최종 분량은 **초록 134 + 본문 2,626 + 그림 2,100 = 4,860/5,000**이다. 그림 4·표 0·문헌 14개다.
- 지정 다섯 검사 **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff**를
  순서대로 통과했다. **6 passed**, ruff 통과다. 단순 문구 삭제이므로 새 회귀 테스트는 추가하지 않았다.
- Word **v38** 영문 16쪽·한글 19쪽을 생성하고 Microsoft Word/PDFium으로 렌더했다.
  정식 렌더러는 번들 LibreOffice 실행 파일 부재로 실패하여 로그를 보존한 뒤 기존 경로를
  사용했다. 바뀐 열 쪽을 개별 확인했고 나머지 25쪽은 검증된 v37 PNG 해시와 일치한다.
  네 그림과 완전한 캡션은 각각 같은 페이지이며, 참고문헌 한 항목이 페이지 사이에서
  분리되지 않도록 Word 문단 설정을 적용했다. 문헌 내용과 줄 간격은 바꾸지 않았다.
- 삭제 문단에 붙은 기존 댓글 한 개씩은 `_local/`의 별도 JSON에 보존했고 나머지 댓글
  다섯 개씩은 v38에 유지했다. 이전 v37은 보존한다. 모든 저자 정보·댓글·Word·투고 고지
  메모는 `_local/` 전용이며 공개/상용 결정·버전·라이선스·푸시 보류는 유지한다.

### H30. JCIM Application Note 제출 형식 재점검 (2026-09-14)

- 저자의 요청에 따라 [JCIM 공식 지침](https://researcher-resources.acs.org/publish/author_guidelines?coden=jcisd8)
  (2026-08-27 갱신)을 대조했다. 초기 투고의 Fast Format은 출판본 2단 조판을 요구하지 않는다.
  기존 Word는 일반 논문 서식이며 공식 Word 템플릿을 그대로 적용한 파일은 아니다.
  템플릿 다운로드가 HTTP 403으로 실패하여 템플릿 자체와의 정확한 대조는 **확인 못 함**이다.
- 초록을 8문장에서 4문장으로 정리하고 반복되는 소개·구현·환경 목록·재현성 설명을 줄였다.
  Figure 1 캡션에는 그림의 계산 흐름과 공통 기록을 설명하는 내용만 보완했다.
  영문 생성기와 한글 원고를 함께 수정했으며 MD 생성물을 직접 편집하지 않았다.
- 분량은 **초록 84 + 본문 2,515 + 본문 그림 2,100 = 4,699**다. TOC 포함 여부는
  Application Note 규정에 명시되어 있지 않아 300을 별도 여유분으로 더한 **4,999/5,000**도
  기록하고 생성기 상한 검사에 반영했다. 이 300을 출판사가 명시한 TOC 산식이라고 주장하지 않는다.
  본문 그림 4·표 0·문헌 14개다. 고지나 저자 확정 문안을 추가할 때 다시 감축·검사해야 한다.
- 누락되어 있던 Word 마지막 TOC 페이지를 추가했다. 기존 TOC의 USD/lb·시장 범위 수치를
  제거하고 코드 생성기로 조성·원가·순위의 개념도와 USD/kg 표기를 만들었다.
  [TOC 규격](https://pubsapp.acs.org/paragonplus/submission/toc_abstract_graphics_guidelines.pdf)에
  맞춰 3.25 × 1.75 in, RGB TIFF 300 dpi, 최소 6 pt로 저장했다. 새 생성형 이미지 출력은 쓰지 않았다.
- Figure 3 폭은 86에서 84 mm로, 수치 도판의 0.25/0.45 pt 선은 0.5 pt로 조정했다.
  Word의 나머지 본문 그림 폭은 168 mm다. 과학적 값·17개 질량 환산·JSON 참조 57개와
  별도 가격 역전 연구 패키지는 그대로다. 동결 JSON·계산 엔진·PPT 도식 원본은 수정하지 않았다.
- 문헌 DOI 10건을 무료 Crossref에서 확인했다. 세 건은 최초 HTTP 429 이후 재시도에서
  확인되었다. 문헌 13의 온라인 연도 2023과 권호 발행 연도 2024를 구분해 기존 서지를 유지했다.
  DOI 없는 네 웹 출처에 DOI를 새로 부여하지 않았다. 전체 문헌 내용은 바꾸지 않았다.
- **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff** 순서로 통과했다.
  노트 **6 passed**, 별도 질량 변환·가격 관측 검사 **4 passed**다. TOC도 생성기로 양 언어 재생성했다.
- Word **v39**는 영문 17쪽·한글 20쪽, 각 본문 그림 네 개와 TOC 한 개, 댓글 0개다.
  v38 댓글 다섯 개씩은 로컬 JSON에 보관했다. 정식 렌더러는 LibreOffice 실행 파일 부재로
  실패 로그를 남기고 기존 Word/PDFium으로 렌더했다. 바뀐 31쪽은 개별 시각 확인했고
  나머지 6쪽은 검증된 v38 페이지 해시와 같다. 그림·캡션의 같은 쪽 배치와 참고문헌을 확인했다.
- 오래된 로컬 체크리스트를 폐기 표시하고 실제 원고·분량·접근 미정 상태로 새 대조표를 작성했다.
  이전 투고·사전 공개 여부, 업로드 완료, v1.4.0 공개 접근을 확인된 사실로 쓰지 않는다.
  SI 구성·제출 문구, 연구비·이해상충·저자 선언과 실제 심사자 접근 방법은 아직 확정이 필요하다.
  AI 고지는 H29의 저자 편집 요청대로 복원하지 않았으며, [ACS 정책](https://researcher-resources.acs.org/publish/aipolicy)
  충족을 위한 실제 원고 반영이 남아 있다. **v39를 투고 준비 완료본으로 판정하지 않는다.**
  Word·개인정보·댓글·제출 초안과 상세 QA는 `_local/` 전용이며 로컬 커밋만 한다.

### H31. Figure 2 패널별 범례 색상 구분 (2026-09-14)

- 저자가 (b)의 원가 항목과 (c)의 추정 방법이 같은 색으로 표시되어 혼동된다고 지적했다.
  그림 생성기의 `_validation_panel`에 전용 색을 지정해 (c)의 COMET은 보라색 `#7762A7`,
  Baddour 등의 문헌 추정값은 주황색 `#D99545`로 구분했다. 범례는 실제 막대에서 생성하므로
  같은 색으로 함께 바뀐다. (b)의 재료비·가공비·간접비와 마진 색은 그대로다.
- 영문·한글 그림을 생성기로 재생성했다. 각 SVG의 변경은 (c)의 막대 여섯 개와 범례 두 개의
  채움색뿐임을 이전 커밋과 대조했다. 배치·문자·수치·축·(a)·(b)와 다른 그림은 유지했다.
  본문·캡션 변경이 없어 영문 생성 MD와 한글 MD는 수정하지 않았다. PNG/SVG 직접 편집 없음.
- **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff** 순서로 통과했다.
  노트 **6 passed**, ruff 통과다. 단순 색 변경으로 새 테스트는 추가하지 않았다.
- Word **v40** 영문 17쪽·한글 20쪽에 새 그림을 반영했다. v39 패키지에서 Figure 2 PNG만
  교체하는 로컬 재생성기로 문서 XML·본문·캡션·서식·다른 그림을 바이트 그대로 보존했다.
  번들 LibreOffice 부재로 정식 렌더러의 실패 로그를 남기고 Word/PDFium으로 검증했다.
  두 언어의 5쪽을 개별 시각 확인했고 나머지 35쪽은 검증된 v39 페이지 해시와 일치한다.
- **4,699**, TOC 여유분을 더한 **4,999/5,000**과 본문 그림 4·TOC 1·문헌 14개를 유지한다.
  저자 정보·Word·QA는 `_local/` 전용이다. H30의 투고 전 미확정 사항과 외부 게시 보류는 유지한다.

### H32. Figure 2(c) 편차 부호와 문헌 번호 명시 (2026-09-14)

- 저자가 음의 deviation의 의미를 묻고 Baddour 논문의 인용 번호를 요청했다. 영문 범례를
  `Baddour et al. [1]`, 한글 범례를 `Baddour 등 [1]`로 바꿨다. Figure 2 캡션에 원고의 문헌
  1번을 인용하고 **100 × (추정 가격 − 시장 가격)/시장 가격** 및 음수의 의미를 명시했다.
  영문 생성기를 편집해 MD를 재생성하고 한글 캡션도 함께 수정했다.
- 동결 JSON의 추정값과 시장 가격을 다시 계산했다. COMET 편차는 Pt/C −19.7%,
  Ni/Al₂O₃ −9.9%, FCC −10.7%다. 값이 음수인 이유는 추정 가격이 시장 가격보다 낮기 때문이다.
  절댓값으로 바꾸거나 제조원가 자체가 음수라고 해석하지 않는다. 원문 Table 2의 difference는
  차이의 크기를 양수로 제시하며, 현재 그림은 차이의 방향도 보여준다.
- 문헌 1번 DOI **10.1021/acs.oprd.8b00245**를 무료 Crossref에서 재확인했다. 원문 온라인
  재조회는 OSTI 시간 초과로 확인 못 했으며, 앞서 확보한 무료 공개 원문의 로컬 Table 2에서
  시장 가격과 문헌 추정값을 대조했다. 새 참고문헌을 추가하거나 번호를 재배열하지 않았다.
- 기존 보라·주황 색을 유지했다. SVG의 여섯 비교 막대는 좌표와 색이 이전과 같고 범례의
  번호 및 그에 따른 범례 위치만 바뀐다. 본문·문헌·동결 데이터·다른 그림은 그대로다.
  캡션은 분량 산정에서 제외되어 **4,699**, TOC 여유분 포함 **4,999/5,000**을 유지한다.
- **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff** 순서로 통과했다.
  노트 **6 passed**, ruff 통과다. Word **v41** 영문 17쪽·한글 20쪽을 전체 빌더로 재생성했다.
  LO 실행 파일 부재 로그를 보존하고 Word/PDFium으로 검증했다. 변경된 네 쪽은 개별 시각
  확인했고 나머지 33쪽은 검증된 v40 PNG 해시와 같다. 두 문서의 텍스트 변경은 Figure 2
  캡션 한 문단씩뿐이다. 그림과 완전한 캡션은 같은 페이지다. 로컬 커밋만 한다.

### H33. 실제 소프트웨어 흐름에 근거한 그림 해석과 기능 설명 보완 (2026-09-14)

- 저자가 네 그림의 본문 설명을 검토하고 소프트웨어를 다시 실행하여 빠진 설명을
  보완하도록 요청했다. 지정 체크아웃의 v1.4.0을 별도 SQLite DB·Electron 프로필로
  실행했다. 기존 TypeScript/Vite 빌드는 통과했다. 네이티브 시작 화면을 확인한 뒤
  같은 빌드·백엔드의 localhost 브라우저에서 주요 작업 흐름을 점검했다. 새 설치본의
  패키징 시험이나 모든 조합에 대한 GUI 전수 검사로 보고하지 않는다.
- 열촉매 입력의 조성 검증, 제조 절차 선택, 계산·저장·복원, 규모 변경, 공통 조건 비교,
  전극 조립체 계산, 현재 사례의 Monte Carlo, 문헌 후보·출처 상세, 금속 가격 이력,
  자료 라이브러리, 별도 설비투자·운영비, kg/lb·언어 전환과 CSV 내보내기를 확인했다.
  같은 Ni/알루미나 조성의 두 규모를 비교하면 가격 차이가 공통 운전 조건에서 사라졌다.
  검증용 최신 가격과 사례는 논문의 동결된 2026년 5월 데이터에 반영하지 않았다.
- **Figure 1:** 실제 시작점인 열촉매/전극 선택, 조성 입력 또는 라이브러리 불러오기,
  제조 경로·규모 조정, 결과의 원가·출처·산정 범위 연결과 저장·내보내기를 설명했다.
  인터페이스의 기능과 재현용 분석 스크립트를 구분했다. 사용자 정의 가중치와 전수
  민감도 분석을 모두 GUI 기능인 것처럼 읽히지 않게 했다.
- **Figure 2:** (b)의 막대 합계 100%와 옆의 USD/kg 값, 재료비 비율순 정렬 및 반응군 간
  성능 비교가 아니라는 점을 명시했다. 계산 코드에서 회색 잔여분에 경로별 추가 비용도
  포함됨을 확인하여 범례를 `Other costs`/`기타 비용`으로 바로잡고 캡션에 간접비·마진·
  경로별 추가 비용을 정의했다. 스크리닝 합계가 Step Method 가격에 경로별 비용을 더함을
  본문에 명시했다. (a)와 (c)의 계산 구조·시장 편차 설명은 유지했다.
- **Figure 3:** 귀금속·비귀금속 로그 축에서 같은 간격이 같은 가격 비율을 뜻함과 과거
  월별 자료가 민감도 입력이며 예측값은 아니라는 점을 설명했다.
- **Figure 4:** 기준 후보 비율 50% 미만의 의미, 서로 다른 검사에서 평가하는 취약성,
  후보 확보 가능성·가중치·성능 근거를 검토하는 용도를 보완했다. 후보 제거에 따른
  정규화 범위 변화와 실제 촉매 가격 변화는 계속 구분한다.
- 전극의 면적당 원가는 제조 시나리오를 선택하지 않으면 재료비만 포함하며 분말 경로와
  전체 스택 조립 비용은 별개임을 명시했다. 설비투자·연간 운영비 모듈 역시 Step Method
  가격에 자동 합산되지 않는다. 계산 화면의 재료 환경지표와 후보 분석의 공정 에너지를
  구분하고, 원소 계수의 화합물 대응은 근사이므로 질량 반영률 100%도 완전한 LCI가 아님을
  설명했다. 실제 UI의 반영률 0%/GWP 0.00 표시는 후속 개선 사항으로 별도 기록했으며,
  이번 논문 수정에서 소프트웨어가 이를 해결했다고 주장하지 않는다.
- 본문 그림은 네 장을 유지했다. 추가 UI 그림은 Figure 1과 중복되고 새 검증 결과를
  제시하지 않아 넣지 않았다. 반복 설명을 줄여 본문 **4,662**, TOC 보수적 여유분 포함
  **4,962/5,000**이다. 표 0·문헌 14·동결 JSON 참조 57·질량 환산 17개를 유지했다.
  영문은 생성기를 수정해 MD를 재생성했고 한글 원고도 함께 수정했다. 수치·동결 JSON·
  계산 엔진·라이선스·버전은 변경하지 않았다. 그림은 생성기로 재생성했다.
- **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff** 순서로 통과했다.
  노트 **6 passed**, ruff 통과. 추가로 원가 엔진·저장 비교·환경·설비/운영비·후보 가격·
  순위 안정성 관련 회귀 **80 passed**다. 세 Step Method 검증 사례도 포함한다.
- Word **v42** 영문 17쪽·한글 20쪽을 전체 빌더로 생성했다. 번들 LO 부재 로그를 남기고
  Word/PDFium으로 확인했다. Figure 2 문단의 불필요한 줄 간격을 제거하고 한글 캡션은
  글자 크기를 유지한 16pt 줄 간격으로 조정하여 그림과 전체 캡션을 같은 페이지에 배치했다.
  변경된 **23쪽**을 개별 시각 검토했고 나머지 **14쪽**은 검증된 v41 PNG와 동일하다.
  본문 그림·캡션의 동일 페이지 배치와 댓글 0개를 확인했다.
- 상세 UI 범위·한계와 CSV·검증 결과·Word·개인정보는 `_local/`에만 보존한다. 검증용
  브라우저와 백엔드를 종료했다. 외부 게시 보류와 H30의 투고 전 미정 사항은 유지한다.

## H34 — 상세 제조 조건과 배치 운전 원가 연결 (2026-09-14)

- 저자가 실험 절차의 건조·소성·환원 시간과 온도 등 세부 제조 변수를 소프트웨어에
  반영하도록 요청했다. 기존 Step Method는 선택한 장치와 규모의 경험식으로 가공비를
  산정하므로 개별 유지 시간·승온 속도·환원 가스 소비를 직접 구분하지 못했다.
- 열촉매 계산에 선택형 상세 제조 조건을 추가했다. 순서가 있는 단계의 추가·복제·이동·반복,
  장비·분위기·절대압·교반 속도·pH·용매량·투입/회수 메모, 여러 목표 온도·승강온 속도·
  유지 시간, 환원·퍼지 가스의 유량·시간·가격·기준 상태를 보존한다. 첨부 합성 자료는
  공개 데이터나 기본 원가 자료로 재배포하지 않고 _local에서만 대조했다.
- `record_only`는 불완전한 조건을 기존 Step Method 결과와 함께 기록한다. `batch_cost`는
  최종 건조 배치 수득량, 전력/인건비 단가, 출처·가정 및 단계별 운전 자료가 완전할 때
  상세 배치 가공비로 경험식 가공비를 대체한다. 두 가공비를 중복 합산하지 않는다.
  빈칸을 비용 0으로 취급하지 않고, 제외하는 비용만 명시적인 0으로 입력한다.
- 승강온 시간은 온도 변화/속도, 전력량은 측정 kWh 또는 구간별 평균 입력 kW×시간,
  가스량은 유량×사용 시간으로 계산한다. 가스 유량과 구매 단가의 기준 온도·압력은
  일치해야 한다. 직접 작업 인시와 무인 유지 시간을 구분하고, 장비 시간당 단가에서
  별도 계산하는 전기·가스·인건비를 제외한다. 장비 전력이나 열손실을 임의로 추정하지 않는다.
- 재료비+가공비와 G&A/SARD·판매 마진을 구분한다. 배치 모드의 판매 마진은 명시적 입력
  (기본 0)이며 산업 규모 상관식을 소량 배치에 적용하지 않는다. kg 단가의 분모는 최종
  건조 수득량이다. 용매 부피는 기록이며 구매 비용은 기존 소모품 입력에서 반영한다.
  주문 총액은 배치 비용의 선형 반복으로, 산업 규모 확대·정수 배치 계획·수율 예측이 아니다.
- 조건 기록·원가 결과를 입력 초안, 저장·복원, CSV(전체 protocol JSON 포함)에 연결했다.
  배치 사례끼리 비교할 때 각 조건·수득량·장비/가스 단가를 유지하고 공통 조건 열에서
  기준 사례의 전력 단가·인건비·마진을 공유한다. 배치와 Step Method의 혼합 비교는 거부한다.
  소량 배치의 주문량·저장 목록·비교 입력은 kg로 표시한다.
- Monte Carlo의 기준 계산과 각 표본에 선택한 제조 모델을 전달한다. 조건·전력·가스·
  수득량·운전 단가는 현재 고정되어 있으며 그 불확실성을 샘플링하지 않음을 표시한다.
  배치 모드의 환경 계산은 재료만 포함한다. 온도·pH·압력·rpm으로 성능·수율을 예측하거나
  실험실 자료로 산업 원가 정확성을 검증했다고 주장하지 않는다.
- 별도 DB와 localhost 실행에서 한글/영문 입력·결과, 다단 온도 표, 저장·복원·CSV와 비교를
  확인했다. 합성 검증값에서 8.6 h, 9.2 kWh, 가공비 31.72 USD/배치가 손계산과 일치했다.
  마지막 유지 시간을 1 h 늘리면 9.6 h, 10.2 kWh, 34.82 USD/배치로 변했다. 이는 가정값의
  산술·기능 검증으로 실측 촉매 제조 원가가 아니다. 첨부 파일의 세 흐름은 각각 7·15·6단계로
  기록 가능함을 대조했으며, 별도 피독 실험을 기본 제조에 자동 합산하지 않았다.
- 관련 회귀 **82 passed**(새 제조 조건, 원료 구매·가공비, 저장 비교, 원가 엔진, Step Method),
  수정 백엔드 ruff 통과. 프런트 TypeScript/Vite build·ESLint·i18n 검사 통과. 전체 backend
  pytest는 장시간 진행 정체 후 중단하여 완료 확인 못 함; 전체 통과로 보고하지 않는다.
- 지정한 **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff** 순서로
  통과했다. 노트 6 passed. 본문 수치·동결 JSON·도판·영한 원고·Word는 변경하지 않았다.
  원고 4,662, TOC 보수적 여유분 포함 4,962/5,000, Word v42를 유지한다. 이 기능은 아직
  원고의 검증된 기여에 추가하지 않았다. 사용법과 계산 범위는 docs/manufacturing-protocol.md에
  설명했다. 버전 1.4.0·라이선스 유지, 새 의존성 없음. 외부 게시·푸시 보류를 유지한다.

## H35 — 전체 후보의 제조 문헌 감사와 시료별 제조 기록 (2026-09-14)

- SCR을 특정 기능의 기본값으로 삼는 대신, **30개 반응군·116개 후보·34개 공정 템플릿**을
  전수 목록화해 제조 근거를 재검토했다. 기존 인용 DOI 344개와 추가 일차 문헌 DOI 24개,
  총 **368개**의 문헌정보를 Crossref에서 확인했다. DOI 등록 확인은 제조법·성능·원가의
  검증이 아니다. 무료 공개 원문과 보충자료만 사용했으며 접근 불가 자료는 미확인으로 남겼다.
- 공개 일차 문헌 **40편의 특정 시료 41개**에 대해 단계 순서, 온도·유지 시간·승온 속도,
  분위기, 명시된 전구체·농도·작업 조건과 원문 위치를 정리했다. 후보 46개에 관련 기록을
  연결했으나 연결된 문헌 시료가 기존 스크리닝 조성과 일치한다는 뜻은 아니다. **70개 후보에는
  아직 채택한 제조 기록이 없다.** 전체 문헌의 체계적 고찰이나 116개 제조법의 완전 검증을
  완료했다고 주장하지 않는다.
- 후보 상태는 출처/시료 불일치 **24개**, 그 불일치 표시 없이 문헌 변형 시료를 연결한
  **30개**, 채택된 제조 기록이 없는 스크리닝 가정 **62개**로 구분했다. 불일치 24개 중
  8개에도 채택 기록이 없다. 모든 후보에서 정확한 조성·완전한 제조 절차·운전 원가 자료가
  함께 검증된 상태는 아니다. 불일치에는 이원 CoCr/NiCr/FeCr을 삼원 Cr-NiFe로 해석한 경우,
  Ni-CeO2-x/CNTs를 Ni-MgO/CeO2로 대응한 경우, 상이한 Pt 합금·담체를 연결한 경우 등이 있다.
- `backend/data/manufacturing_literature.json`에 직접 작성한 사실 요약과 불확실성을 보존한다.
  원문/SI 파일, 저자 제공 자료와 비공개 작업 자료는 배포하지 않는다. overnight·상온·범위·
  하한값·미보고 승온 속도를 단일 숫자로 만들지 않았다. K→°C, 명시된 분/초→h만 환산했다.
  핫플레이트 설정과 시료 온도, 명목/측정 담지량, 몰비/질량분율, 투입량/회수 수득량,
  동시 가열 구역/순차 공정, 분말 제조/전극 제조/별도 활성화를 구분했다.
- API와 후보 상세 화면에 문헌 제목·DOI·원문 위치·시료별 조건·불일치/미확인 상태를
  연결했다. 검증되지 않은 기존 문헌 설명 대신 Crossref의 등록 제목을 표시한다. 기존
  제조 경로는 스크리닝 가정, 온도 범위는 반응 온도로 명시했다. 후보를 계산기로 불러올 때
  근거 상태를 유지하며, 공급사 재료가 해당 문헌 촉매와 다를 수 있음을 전극 조성 화면에 표시한다.
- 제조 기록 가져오기는 `record_only`로 시작하며 조성·기존 가격·배치 수득량·전력·원가를
  자동으로 바꾸지 않는다. H34의 상세 조건 편집·저장·복원과 연결했다. 전극 제조 기록도
  저장할 수 있지만 건조 분말의 kg 분모를 적용한 배치 원가는 API와 UI에서 차단한다.
  분말 배치 원가는 실제 수득량과 완전한 운전 비용을 사용자가 입력해야만 적용한다.
- 영문 생성기와 한글 원고에 문헌 감사 방법·범위·실측 운전 자료의 배치 원가 연결·미확인
  조건과 전극 경계를 함께 설명했다. 기존 수치 결과와 순위는 원래 조성/제조 가정에 따른
  스크리닝임을 본문 및 Figure 2/4 캡션에서 명확히 했다. 실측 자료 없이 116개 산업 원가를
  새로 계산하거나 검증했다고 주장하지 않는다. Monte Carlo에서 제조 조건은 고정이다.
- 보충자료 `docs/paper/manufacturing-literature-2026-09-14.md`는 공개 생성기로 JSON에서
  재생성한다. 116개 후보 평가, 41개 시료별 조건과 출처, 34개 템플릿 및 368개 DOI 목록을
  제공한다. 원고는 **4,697 + TOC 300 = 4,997/5,000**, 본문 그림 4·표 0·참고문헌 14,
  JSON 참조 62·질량 환산 17개다. 기존 동결 수치와 도판 이미지는 변경하지 않았다.
  제조 근거 JSON과 요약의 바이트 해시가 Git의 줄바꿈 변환으로 달라지지 않도록 속성을 지정했다.
- 관련 backend 회귀 **106 passed**: 문헌 목록과 동결 카탈로그의 대응, 출처 불일치,
  미보고 조건, 전극/분말 원가 경계, API·저장/복원, 기존 Step Method 세 검증 사례 등을
  포함한다. 수정 backend ruff, 보충자료 생성기 `--check`, 프런트 build/lint/i18n 통과.
  전체 backend pytest 통과로 확대해 보고하지 않는다.
- 지정한 **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff**를
  마지막 수정 후 순서대로 모두 통과했다. 노트 **6 passed**. 독립 DB의 localhost 화면에서
  문헌 검색·조건 표시·기록 가져오기·미확인 값 보존·전극 배치 차단·후보 근거 전달을 확인했다.
  GUI의 116개 경로를 전부 수동 조작했다고 주장하지 않는다.
- Word **v43** 영문 17쪽·한글 21쪽을 전체 빌더로 생성했다. LO 부재를 기록하고 Word/PDFium을
  사용했다. 변경된 영문 15쪽·한글 19쪽을 개별 시각 검토했고 나머지 4쪽은 검증된 v42 PNG와
  동일하다. 도판 크기를 유지하면서 Figure 2/3/4의 문서 내 위치를 조정했다. 본문 도판과
  캡션의 동일 페이지 배치, 최신 그림 5개(TOC 포함), 댓글 0개를 확인했다.
- 버전 1.4.0과 PolyForm Noncommercial 라이선스 유지, 새 의존성 없음. 개인정보와 Word는
  `_local/` 전용이다. 다른 체크아웃에 접근하지 않았으며 외부 게시·푸시 보류를 유지한다.

## H36 — Figure 2 비용 범례 명확화 (2026-09-15)

- 저자가 Figure 2(b)의 `Other costs`/`기타 비용`이 모호하다고 지적했다. 그림 생성기의
  범례를 `Overheads + profit margin + route allowances` / `간접비·판매 마진·경로별 추가 비용`으로
  변경하고 영문·한글 PNG/SVG를 재생성했다. 수치·색상·막대 비율·도판 크기·글자 크기는 유지했다.
- 영문 원고 생성기와 한글 원고의 캡션을 함께 고쳤다. 일반관리비(G&A), 판매·관리·연구·
  유통비(SARD), 판매 마진, 품질관리·활성화·추가 경로 간접비의 가정액을 회색 영역에 포함한다고
  명시했다. 판매 단가의 구성임을 유지하고 (a)는 Step Method로 특정했다. 본문에 있는 편차
  공식을 캡션에서 반복하지 않아 그림과 캡션이 한 페이지에 들어가도록 했다. 음수의 의미와
  Baddour 등 문헌 [1]은 캡션에 유지했다. 엔진·동결 JSON·추정 금액은 변경하지 않았다.
- 원고 **4,697 + TOC300 = 4,997/5,000**, 그림4·표0·참고문헌14 유지.
  지정 **영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff** 순서로
  모두 통과했다(노트 6 passed). Word **v44 EN17쪽/KO21쪽**을 기존 빌더로 생성했다.
- LO 부재 로그를 보존하고 Word/PDFium으로 렌더했다. 변경된 EN6/11/13/14쪽·KO6쪽을
  개별 시각 검토했으며 나머지33쪽은 검증된v43 PNG와 동일하다. 두 언어의 Figure2와 전체
  캡션은 모두6쪽에 배치된다. 최신 그림5개·댓글0개 확인. Word·개인정보·QA는 _local 전용이며
  기존v43은 보존했다. 외부 게시·푸시 보류 유지.

## H37 — 제조 입력 근거와 배치 구매비 추적 기반 (2026-09-15)

- 저자의 장기 GOAL을 시작했다. 이번 항목은 기능 기반의 중간 검증 기록이며, 제조 문헌의
  추가 전수 조사·새 수치 연구·도판·본문·제출용 SI의 완성을 의미하지 않는다.
- 제조 조건의 개별 값에 문헌/실측/공급사/가정 유형, 인용, 원문 위치, URL/DOI, 날짜,
  저장 당시 값과 메모를 연결한다. 편집 후 원래 값과의 차이를 표시하며 복제·저장·복원과
  JSON/CSV 내보내기에 이를 보존한다. 해시는 정규화된 조건을 식별하고, 출처 등록을
  독립 검증으로 표시하지 않는다. pH·교반·압력 등 현재 계산식에 없는 조건은 기록 전용이다.
- 가스 사용 시간은 직접 입력하거나 전체 공정/온도 유지 시간에 연결할 수 있다. 승·강온,
  유지, 추가 시간 및 반복을 반영하며 이중 시간 입력과 미확인 시간을 0으로 처리하는 것을
  차단한다. 전력량은 입력 전력×시간 또는 실측 kWh로 계산하고, 후자는 조건 변경 시
  자동으로 새 실측값을 추정하지 않는다. 계산 경로와 항목별 USD/kg 기여분을 제공한다.
- 배치 구매량 모드를 추가했다. 각 단계의 전구체·담체·용매·소모품 순 구매량과 같은 단위의
  가격을 입력하고 반복 횟수와 건조 수득량으로 kg당 재료비를 계산한다. 선택 시 기존 조성
  가격·마크업·kg/kg 소모품 비용을 모두 대체한다. 용매 구매량은 해당 단계의 mL 값에
  연결할 수 있다. 밀도·순도·수율·용매 회수량을 임의로 환산하거나 추정하지 않는다.
- 비용 명세는 재료, 전기, 장비, 직접 작업 인건비, 가스, 별도 입력 비용, G&A, SARD,
  판매 마진을 분리한다. 선택한 사용 후 금속 회수 가치는 제조 지출과 분리한 사후 공제로
  추적한다. SARD 표시를 본문 정의와 같은 sales, administration, research and distribution
  (판매·관리·연구·유통비)로 맞췄다. 기존 Step Method의 수식·상관식·동결 수치는 그대로다.
- 실제 localhost UI에서 배치 구매비가 원가 도표에서 누락되고 재료 0종/시세 기반으로 보이던
  새 모드 연동 문제를 고쳤다. 입력 단가의 근거 수를 표시하며 배치 모드 환경 지표는 최종
  조성의 재료 영향으로 특정한다. 결과 하위 화면에서 계산기로 돌아가기 버튼이 브라우저
  이력을 따라 다른 결과 탭으로 돌아가던 문제도 계산기 경로로 직접 연결했다.
- 합성 회귀 사례로 계산 경로를 검증했다. 0.03 kg, 2 h 가정에서 재료비 5 USD/배치,
  가공비 12.4 USD/배치, 재료+가공 580 USD/kg, G&A/SARD 각 5%, 판매 마진 0%를 적용하면
  판매 단가는 639.45 USD/kg이다. 시간 3 h·수득량 0.06 kg로 바꾼 경우 전력 3 kWh,
  가스 시간 3 h, 가공비 16.1 USD/배치, 판매 단가 387.7125 USD/kg을 실제 UI에서 확인했다.
  이 값은 소프트웨어 검증용 가정으로, 문헌·실측 촉매 비용 결과가 아니다.
- 관련 backend 회귀 235 passed 후 구매 API/저장/비교/고정조건 불확실성 및 회수 공제
  검증을 추가했다(최종 구매 테스트 파일 12 passed). 수정 backend ruff와 frontend
  build/lint/i18n 통과. 전체 backend 테스트 통과로 확대해 보고하지 않는다. 기존 3개
  Step Method 검증 사례를 포함했다. Monte Carlo의 제조 입력은 아직 고정이며, 제조
  조건별 불확실성 및 공통 구매가격 비교 확장은 GOAL의 후속 범위다.
- 지정한 영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff를 순서대로
  통과했다(노트 6 passed). 이 단계에서는 원고 본문·도판·문헌 라이브러리·Word를 아직
  개정하지 않았으므로 v44와 4,997/5,000을 유지한다. 최종 EN/KO·SI 동시 개정은 새 문헌
  조사와 재현 가능한 제조 연구 결과를 확정한 뒤 수행한다.
- 새 의존성·버전 변경 없음. 1.4.0 및 PolyForm Noncommercial 유지. 독립 검토 DB만 사용하고
  개인정보·GUI 사례·작업 기록은 _local/에 보존한다. 외부 업로드·푸시·배포·유료 호출 없음.

## H38 — 제조 조건의 원문 값 보존과 운영비 근거 (2026-09-15)

- 기존 41개 제조 기록에 앞선 검토에서 옮긴 수치의 DOI·원문 위치·검토일·원래 값을
  연결했다. 출처 등록은 실측이나 독립적인 재현 검증을 뜻하지 않는다. 기록을 가져온 뒤
  투입량을 변경해 저장하더라도 원래 문헌값과 변경 표시가 보존되는 것을 검증했다.
- Petel 등의 Ni/SiO2 Gen 1/4와 Pt/SrTiO3의 제조 절차를 추가하여 **44개 기록·42개 출처**가
  됐다. 원문에 명시된 투입 질량·부피·시간을 구조화된 구매 항목과 조작으로 보존한다.
  단가·실측 평균전력·최종 건조 수득량은 채우지 않는다. Gen 1의 TOP 당량 표기 불일치,
  Gen 4의 약 5 mL 용매량, Pt/SrTiO3의 승온/유지 시간 구분 및 sccm 기준 상태의 불명확성을
  그대로 기록했다. 정성적·근사 값을 정확한 수치로 바꾸지 않는다. 두 DOI의 Crossref 등록과
  공개 원문 PDF를 확인했으며 원문 파일은 재배포하지 않는다.
- NiFe seed-assisted 후보의 연결 논문은 Raney Ni 전극을 다루며, Cu/ZrOx-MgO 후보에
  연결된 접근 가능한 실험법은 다른 산화물 조성이다. 불일치를 추가하여 후보 **26개**에
  표시했다. 등록 DOI는 **370개**다. 새 비용 사례 제조법은 해당 스크리닝 후보를 검증하는
  자료로 자동 연결하지 않았다. 기존 116개 후보 중 제조 기록이 연결된 수는 여전히 46개다.
- EIA 2025년 미국 산업용/상업용 평균 전력 단가(잠정치), BLS 2023년 화학 실험 기술직 임금,
  Nabertherm 특정 모델의 웹 사양/2024년 설명서 등 운영 근거 5건을 추가했다. 전력 단가는
  시나리오로 선택 적용하고 출처를 보존한다. 복리후생이 제외된 과거 임금과 정격 연결 부하는
  계산값으로 자동 입력하지 않는다. 같은 장비명에 웹 3.7 kW/설명서 3.4 kW의 차이가 있음을
  명시하며, 어느 값도 제조 조건별 평균 소비전력으로 간주하지 않는다.
- 독립 검토 UI에서 합성 회귀 사례의 단가를 0.1에서 0.0862 USD/kWh로 바꾸면 판매 단가가
  639.45에서 **638.4357 USD/kg**로 바뀌고 EIA 원래 값·표 위치·열람일이 보존됨을 확인했다.
  정격전력 자료에는 적용 버튼이 없음을 확인했다. 화면의 숫자는 실제 촉매 제조원가를
  검증한 결과가 아니라 명시적인 입력 가정을 이용한 기능 회귀다.
- 관련 backend 39 passed, frontend 원문 보존/단가 적용/장비 정격 제외 회귀 3 passed.
  frontend build/lint/i18n 및 수정 backend ruff 통과. 원문 수치와 입력 스키마의 일치,
  미확인 가격·수득량의 비어 있음, 저장 후 변경 표시를 검증했다.
- EN 생성기와 KO 원고에 입력별 근거, 배치 구매비 대체, 가스 시간 연결, 계산식과 결과
  내보내기를 반영했다. 생성된 제조법 보충자료는 구매량과 운영 근거를 포함하며 파일 해시를
  갱신했다. 원고 **4,700 + TOC300 = 5,000/5,000**, 그림4·표0·참고문헌14다. 참고문헌13은
  이미 Petel, 2024, 8(10), 2300030으로 올바르게 기재되어 있어 다시 바꾸지 않았다.
- 지정한 영문 그림 → 한글 그림 → 원고 --check → 노트 pytest → scripts ruff를 순서대로
  통과했다(노트6 passed). 동결 수치와 도판 구성은 변경하지 않았다. 최신 Word는 v44이며
  이번 본문 개정의 Word/PDF 반영은 후속 원문 검토·새 분석·제출용 SI 통합 단계에서 수행한다.
- 제조 기록이 없던 후보70개에 대한 추가 공개 검색은 모두 수행했고, 검색 결과가 있는
  후보는37개다. 선정한 1차 논문18편의 Crossref DOI와 공개 원문을 확보했으며 실험법 검토가
  남아 있다. 검색 결과나 원문 확보를 제조법 검증으로 집계하지 않았다. 전수 제조법 보완,
  조건별 불확실성·공통 구매가격 비교, 새 연구 도판·EN/KO·제출용 SI의 완성은 진행 중이다.
  GOAL은 active로 유지한다. 외부 게시·푸시·유료 이용·새 의존성·버전 변경 없음.

## H39 — 중간 생성물 분취와 원가 배분 (2026-09-15)

- 제조 원문에서 합성한 지지체 배치의 일부만 후속 단계에 사용한 사례를 확인했다. 전체
  상류 배치 지출을 소량의 분취 시료에 무조건 붙이지 않도록 중간 배치와 제조 단계 연결,
  회수 질량·사용 질량·비용 배분 기준을 추가했다. 구매비·전기·가스·장비·직접 인건비·
  추가 비용에 동일한 사용량/회수량 비율을 적용하며 원래 지출·시간·전력량은 보존한다.
- 질량 배분은 미사용 회수 가능 재고가 비용을 보유한다는 명시적인 가정이다. 재고 공제
  없이 실험 한 건에 모든 지출을 부담시키는 전체 배치 방식도 제공한다. 이 선택은 실제
  회수량을 추정하지 않는다. 질량 배분에서 미확인 수득량, 사용량 초과, 중복 식별자와
  정의되지 않은 배치 연결은 계산을 막는다. 내부 이동을 구매로 재입력하지 않도록 안내한다.
  현재는 독립 중간 배치가 최종 배치에 직접 투입되는 구조이며, 연속 중간 배치 간 분취·
  공동생산물·재고 일정은 모델링하지 않는다. 이 경계를 원고·사용 안내·보충자료에 명시한다.
- 결과에서 전체 중간 배치 비용과 최종 촉매에 배분된 비용을 나란히 표시한다. CSV/JSON에
  원래 구매량·실제 배치 지출·배분 비율·비용을 보존한다. 계산 경로에 중간 배분에서 재료비,
  가공비, G&A, SARD와 마진을 거쳐 최종 판매 단가에 이르는 합계 노드를 연결했다.
  시간의 배분 값은 비용 환산용이며 생산 일정 또는 물리적으로 단축된 운전 시간이 아니다.
- 합성 회귀: 중간 배치 재료20 USD·운전13.6 USD, 회수0.01 kg 중0.001 kg 사용 시
  최종 배치 부담3.36 USD. 최종 단계 재료3 USD·운전4.6 USD·건조 수득0.002 kg와
  G&A/SARD 각5%·마진0%를 적용하면 **6041.7 USD/kg**이다. 회수량0.02 kg 시
  **5115.6 USD/kg**, 전체 배치 지출 적용 시 **22711.5 USD/kg**이다. 실제 localhost
  UI에서 세 결과, 미확인 회수량 차단, 편집 영역과 비용 표 배치를 확인했다. 다운로드한
  CSV의 원래 질량·배분·정확한 판매 단가도 검증했다. 실제 촉매 원가의 검증값이 아니다.
- 관련 backend69 passed, frontend 원문 가져오기·운영자료·중간 분취 보존4 passed.
  frontend build/lint/i18n와 수정 backend ruff 통과. 마지막 표시/식 문구 조정 후 build/lint와
  trace/분취21 tests를 재검사했다. 기존 조건에는 배분계수1을 사용하여 기존 원가를 유지한다.
- EN 생성기·KO 원고를 함께 수정하고 보충자료를 생성기로 재생성했다. 본문은
  **4695+TOC300=4995/5000**, 그림4·표0·참고문헌14 유지. 지정한 영문 그림 → 한글 그림
  → 원고 --check → 노트 pytest → scripts ruff를 순서대로 통과했다(노트6 passed).
  동결 연구 수치는 변경하지 않았다. Word는 v44이며 신규 문헌·연구의 통합 개정이 남았다.
- H38은 로컬 커밋 e78b261로 기록했다. GOAL은 계속 진행 중이며, 추가18편의 제조법 검토,
  조건별 불확실성·공통 가격 비교, 새로운 도판·본문·제출용 SI/Word/PDF가 남아 있다.
  외부 게시·푸시·유료 호출·새 의존성·버전 변경 없음.

## H40 — 연속 분취와 추가 1차 제조법 대조 (2026-09-15)

- H39의 직접 분취를 중간 배치 간 연속 분취로 확장했다. 사용량/회수량 비율을 최종
  배치까지 곱하고, 각 배치에 직접 연결한 구매·운전비를 한 번만 배분한다. 순환 경로와
  미정의 연결은 거부하며, 후속 회수량이 미확인이면 상류 배분도 미완료로 남긴다.
  각 중간 배치는 한 대상에만 연결한다. 분기·공동생산물·재고 일정은 범위 밖이다.
- 합성 회귀에서 10%와 50%의 연속 분취는 상류 지출33.6 USD의 5%=1.68 USD를 최종
  배치에 배분한다. 중간 성형비2 USD 중1 USD, 최종 단계7.6 USD, 건조 수득0.002 kg,
  G&A/SARD 각5%·마진0% 조건의 판매 단가는 **5666.85 USD/kg**이다. 실제 localhost
  UI에서 저장 사례를 불러와 재계산하고 배치 연결·질량·배분 표를 확인했다. 이는 실제
  촉매 원가 검증값이 아니다. 실제 공정시간4 h와 비용 환산시간1.6 h를 구분한다.
- 추가로 확보한 18편의 Crossref 등록과 공개 1차 본문을 대조하여 15개 출처의 시료별
  제조 기록26개를 추가했다. 총 **70기록·57제조출처·388 DOI**, 후보 연결61개,
  제조 기록 미연결55개, 기존 출처/조성 불일치26개다. 연결된 시료가 원래 스크리닝
  조성이나 완전한 운전비를 검증한다는 뜻은 아니다. 원문·SI 파일은 재배포하지 않는다.
- PtSn의 분말 혼합물→성형체→Pt 담지 과정에서 각각3.750 g와3.000 g을 분취한다.
  투입 질량 합계를 회수 수득량으로 쓰지 않았다. Ni/ceria의 약35 mL는 용기 용량이며
  투입량으로 입력하지 않았다. 전자레인지800 W, 램프9 W, 아크2000 A를 실측 전력으로
  바꾸지 않았다. SAPO-34의 최초 분리와4회 세척은 별도 조작으로 구분했다. overnight,
  반복 횟수 미상, 습식 보관 MoS2와 미확인 수득량은 숫자를 만들어 채우지 않았다.
- Ag 중공섬유 전극은 Europe PMC의 공개 보충파일 API로 SI를 확보하고 제조·조립·
  전기화학 활성화 절차와 원문 쪽을 대조했다. 80 g 합성량을 단일 전극 사용량으로
  간주하지 않았다. 전극 기록은 건조 분말 배치 원가에 적용되지 않는다. PtZn의 SI는
  확인 못 함(공개 API503); Ni-Fe/탄소는 대상 NiCo2O4와 다르고, 철 분석 시료 전처리는
  산업 제조법 전체가 아니므로 세 출처는 제조 기록으로 채택하지 않았다. 70개 검색의
  질의·날짜·검색 건수와18편의 채택 판단을 JSON과 생성 보충자료에 보존했다.
- 관련 backend93 passed(기존 Step Method 검증 포함), frontend 원문·단가·분취 가져오기
  5 passed, build/lint/i18n와 수정 backend ruff 및 SI --check 통과. 중간 배치의 저장·
  복원·원래 출처 값 보존은 직접 및 연속 분취 양쪽 API 회귀로 확인했다.
- EN 생성기·KO 원고를 함께 개정했다. 본문 **4693+TOC300=4993/5000**, 그림4·표0·
  참고문헌14다. 영문 그림→한글 그림→원고 --check→노트 pytest→scripts ruff 지정 순서
  통과(노트6 passed). 기존 동결 연구 수치는 그대로이며 Word는 아직v44다. 새로운
  제조 분석·도판·본문·SI/Word/PDF 통합과 남은 후보 조사는 GOAL 후속 작업이다.
- H39는2d09df6으로 로컬 커밋했다. GOAL active 유지. 외부 게시·푸시·유료 호출·
  의존성·버전 변경 없음. 검토 사례와 서버는 _local의 별도 DB로 격리했다.
