# Scientific notation audit — 2026-09-07

앱 전반의 화학식·전하·동위원소·단위 지수를 표시 단계에서 통일했습니다. 기준 커밋은 `c963bbd`, 구현 커밋은 `a7f2d56`이며 같은 PR112에서 검토합니다. 계산식과 원본 데이터는 바꾸지 않았습니다.

| ID | 상태 | 커밋 | 근거 | 메모 |
|---|---|---|---|---|
| S01 | 완료 | `a7f2d56` | `node scripts/test_scientific_text.mjs`: 6개 통과 | 화학식·단위·검색·CSV 표시 |
| S02 | 완료 | `a7f2d56` | 전체 pytest 780개, 브라우저 11개 화면과 제조 회귀 6개 흐름 통과 | 아래 검증 표와 JSON 참조 |
| S03 | 완료 | 이 감사 기록의 커밋 | Windows build 198.068초, smoke 17.604초, 설치 종료 0 | 해시 일치·DB 무결성 ok·실행 확인 |

## 표기 규칙과 범위

| 종류 | 표시 예 | 유지하는 구분 |
|---|---|---|
| 원자·괄호 내 그룹 개수 | Al₂O₃, Ni(NO₃)₂, MoO₂(acac)₂ | 분수 조성의 소수점도 아래첨자 영역에 포함 |
| 수화물 | Ni(NO₃)₂·6H₂O, H₂PtCl₆·xH₂O | 수화 계수 6과 x는 기준선에 유지 |
| 분수·가변 조성 | Ba₀.₅Sr₀.₅Co₀.₈Fe₀.₂O₃, CeO₂₋ₓ | 원자수와 수치의 거듭제곱을 구별 |
| 전하·영가 금속 | Ni³⁺, NH₄⁺, OH⁻, Co⁰ | C₅+ 탄화수소의 +는 기준선에 유지 |
| 명시된 동위원소 | ¹⁵N₂ | 질량수는 왼쪽 위, 원자수는 오른쪽 아래 |
| 면적·부피·역수 단위 | cm², ft³, m² g⁻¹, mA cm⁻² | 금액·배율·연도는 원래 수치 유지 |
| 수식·궤도 표기 | 설비 규모식의 지수, e<sub>g</sub> occupancy | 궤도 표기는 해당 문구만 처리; CSV는 `e_g` |
| 첨자가 아닌 표기 | 2H₂의 앞 2, Pt₃Ni(111)의 (111), ZSM-5, P5/P95, Table S1 | 반응 계수·결정면·제품 코드·백분위·자료 번호 보호 |

화학식의 오른쪽 아래 원자수, 오른쪽 위 전하, 왼쪽 위 동위원소 질량수는 실제 열어 확인한 [IUPAC Green Book, §2.10.1, 인쇄 50쪽 부근](https://iupac.org/wp-content/uploads/2019/05/IUPAC-GB3-2012-2ndPrinting-PDFsearchable.pdf)의 관례를 따릅니다. 단위 지수는 [BIPM SI Brochure](https://www.bipm.org/en/publications/si-brochure)의 단위 곱·거듭제곱 표기를 참고했습니다. 두 공식 문서의 페이지/PDF 응답을 확인했습니다. 먼저 시도한 IUPAC Analytical Compendium의 별도 PDF는 HTTP 403이어서 근거 문서로 사용하지 않았습니다. 새로운 인용 DOI나 가격·성능 자료는 추가하지 않았습니다.

공통 문자열 포매터와 실제 HTML `<sub>`·`<sup>` 렌더러를 사용합니다. 계산기, 제조법, 결과, 추정 범위, 시세, 문헌 비교, 자료 라이브러리, 설비 비용, 저장 결과 비교와 출처 패널에 적용했습니다. 네이티브 선택 목록·툴팁·접근성 라벨·차트·CSV에는 Unicode 표기를 사용합니다. 라이브러리는 원소 기호만 보이던 보조 행에서 전체 분자식을 우선 표시합니다. 첨자를 붙인 검색어도 기존 ASCII 검색어로 정규화합니다.

입력 필드의 편집 중인 값, 선택 목록의 `value`, JSON 내보내기, 요청 payload, 데이터 파일, URL/DOI/식별자, DB 저장값을 표시용 문자열로 치환하지 않습니다. 수치·단가·LCA 계수·회귀식·제조 단계 순서도 그대로입니다. 이 포매터는 현재 앱 자료에 등장하는 표기를 다루며 임의의 모든 화학 명명법을 해석하는 범용 파서는 아닙니다.

## 검증

| 검사 | 결과 | 원문 |
|---|---|---|
| `python -m pytest backend/tests -q` | 780 passed, pytest 444.01초 / 명령 전체 448.599초 | [pytest](scientific-pytest-2026-09-07.log) |
| `npm --prefix frontend run lint` | 통과, 4.683초 | [lint](scientific-frontend-lint-2026-09-07.log) |
| `npm --prefix frontend run build` | tsc + Vite 통과, 3.691초 | [build](scientific-frontend-build-2026-09-07.log) |
| `npm --prefix frontend run check:i18n` | 누락 키 0, 미번역 UI 라벨 0 | [i18n](scientific-i18n-2026-09-07.log) |
| `node scripts/test_scientific_text.mjs` | 6개 통과; 표기·보호 항목·검색·멱등성 | [notation](scientific-scientific-text-2026-09-07.log) |
| `node scripts/test_calculator_rules.mjs` | 17개 통과 | [calculator](scientific-calculator-rules-2026-09-07.log) |
| `node scripts/test_practical_range.mjs` | 6개 통과 | [range](scientific-practical-range-2026-09-07.log) |
| `python -m ruff check backend scripts` | 통과 | [Ruff](scientific-ruff-2026-09-07.log) |
| `python scripts/reproduce_catcost_table62.py` | Pt/C 센트 일치, Ni −6.65%, FCC 각주 b +1.16% | [Table 6.2](scientific-table62-2026-09-07.log) |

Table 6.2 결과는 Pt/C **27.3695 → 27.37**, Ni/Al₂O₃ **19.2206**, FCC의 각주 b 속도 **2.4380 USD/lb**입니다. 명목 생산 속도의 FCC 1.6090 USD/lb를 합격 결과로 쓰지 않습니다. 이번 변경에 따른 계산 결과 차이는 없습니다. API 실행 성능 개선을 주장하거나 새 성능 측정값을 만들지 않았습니다.

별도 포트 8787, 임시 SQLite DB, 외부 가격 수집을 끈 앱을 실제 Chrome으로 실행했습니다. 사용자 DB에는 시험 항목을 쓰지 않았습니다. [표기 브라우저 기록](scientific-ui-2026-09-07.json)은 11개 화면, 실제 계산 요청, 첨자 검색, CSV 다운로드, 아래첨자의 CSS 위치와 소수 조성의 DOM을 확인합니다. [제조 회귀 기록](scientific-manufacturing-regression-2026-09-07.json)은 25 → 16 → 25 단계 복원, 저장·재로딩, 지연 응답 중 편집, 빈 단계 목록, 한/영·모바일, 전극 결과 분리를 확인합니다. 두 실행 모두 브라우저 오류 0건입니다.

텍스트 노드 검사는 동일 포매터를 사용하므로 독립적인 화학 검증이라고 부르지 않습니다. 별도의 기대값을 둔 단위 테스트와 화면의 실제 첨자 위치를 함께 확인했습니다. 보조 브라우저 실행기는 `_local/scientific_ui_check.cjs`, `_local/scientific_manufacturing_regression.cjs`이며 이 작업 공간의 외부 Playwright 런타임을 사용합니다. 새로운 의존성을 설치하지 않았고, 새 체크아웃에서 그대로 재실행되는 저장소 스크립트라고 주장하지 않습니다. CI에는 영구 회귀 검사 `scripts/test_scientific_text.mjs`를 추가했습니다.

초기 검증 중 일반 단어 `Run`을 Ru의 가변 조성처럼 처리한 문제를 발견해 고치고 보호 회귀 검사를 추가했습니다. 수화물의 전체 분자식이 원소 기호에 가려진 라이브러리 표시도 고쳤습니다. 잘못된 반응군 URL과 추정 범위 탭을 사용한 브라우저 보조 검사는 실제 경로로 바로잡았습니다. 최종 전체 화면 검사를 다시 통과했으며 중간 실패 화면은 `screens/scientific-failure-2026-09-07.png`에 보존했습니다. 이 중간 화면은 완성 화면의 증거로 쓰지 않습니다.

## 화면 근거

- [소수 조성과 궤도](screens/scientific-fractional-composition-2026-09-07.png)
- [수화물](screens/scientific-hydrate-library-2026-09-07.png)
- [이온 전하](screens/scientific-ionic-charge-2026-09-07.png)
- [동위원소](screens/scientific-isotope-2026-09-07.png)
- [설비 규모식의 지수](screens/scientific-capital-exponent-2026-09-07.png)
- [한국어 라이브러리](screens/scientific-korean-library-2026-09-07.png)
- [제조법](screens/scientific-manufacturing-2026-09-07.png), [열촉매 결과](screens/scientific-thermal-result-2026-09-07.png)

## 확인하지 못한 원문과 보수적인 결정

자료 라이브러리의 오래된 황산알루미늄 이름 5개에 `Al23`, `Al203`, `A1203`라는 모호한 원문 철자가 있습니다. `backend/data/materials_library.json`의 `materials[37]`, `[41]`, `[42]`, `[43]`, `[44]`입니다. 정확한 원출처를 확인하지 못했으므로 Al₂O₃라고 추정해 바꾸지 않았습니다. 이 예외를 일반적인 첨자 수정 완료와 구별합니다. 가격·출처·조성 자체의 정확성을 새로 검증했다고 주장하지 않습니다.

## 데스크톱 반영

`npm run build`는 **198.068초**, `npm run smoke:desktop`은 **17.604초**에 통과했습니다. [빌드 로그](scientific-desktop-build-2026-09-07.log)와 [스모크 로그](scientific-desktop-smoke-2026-09-07.log)에 패키지 실행·단일 창 재실행·시세 HTTP 200·계산 HTTP 200을 기록했습니다. 기존 Tailwind sourcemap 및 PyInstaller 경고는 원문에 보존했습니다.

설치 전 SQLite 온라인 백업을 만들었고 백업 무결성은 `ok`입니다. 메모리에만 있는 미저장 입력까지 백업했다고 주장하지 않습니다. 기존 사용자 설치 경로의 COMET을 갱신했으며 설치 프로그램 종료 코드는 **0**입니다. 설치된 `app.asar`와 백엔드 실행 파일의 SHA-256이 검증한 패키지와 일치합니다. DB 무결성은 `ok`, 설치 직후와 앱 재실행 전 항목 수는 계산 0·재료 733·가격 5424·장비 0으로 설치 전과 동일했습니다. 앱 재실행 뒤에는 가격 항목이 5442개로 늘었으며 다른 표의 항목 수는 같았습니다. 이것은 켜져 있는 앱의 자동 수집과 함께 관찰한 변화이며 새 가격의 원출처 정확성을 이번 표기 검사에서 검증했다고 주장하지 않습니다. 바로가기 경로를 읽어 확인했고 직접 다시 쓰지 않았습니다.

앱을 정상 모드로 다시 열어 버전 **1.4.0**, 건강 상태 **ok**, 주 창 **1개**를 확인했습니다. 설치 경로의 프론트 파일과 패키지 백엔드가 실행됐습니다. 별도 시험 서버는 검사 후 종료했습니다. 명령·시간·소스/패키지 해시·설치 검증은 [검증 명세](scientific-checks-2026-09-07.json)에 있습니다. 제품 버전은 기존의 미릴리스 1.4.0을 유지합니다.

이번 S01–S03은 **완료 3개·보류 0개·부분 완료 0개**입니다. 원문 철자 예외 5개와 기존 자료 공백은 위에 구분했습니다. 최종 감사 커밋까지 포함한 CI 링크와 결과는 PR112 본문에 기록합니다. 사람은 PR·master 머지 여부, v1.4.0 태그·실제 릴리스/자동 업데이트, Zenodo DOI, 저널·저자 정보·투고, 이전 D03·V01 보완을 결정해야 합니다. 이번 실행은 master 머지·태그·릴리스·외부 게시를 하지 않았고 유료 자료를 사용하지 않았습니다.
