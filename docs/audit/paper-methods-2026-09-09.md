# Paper methods and evidence audit — 2026-09-09

Base commit: `3296218a0a81220a4d327eb2bf2dcc37af2ee395`; branch `autonomous/2026-09-06`; existing PR112. Scope: complete methods/SI and evidence review, explain candidate-set normalization without changing the current engine.

| ID | 상태 | 커밋 | 근거 명령 출력 요약 | 메모 |
|---|---|---|---|---|
| J01 | 완료 | `d9495fd` | 86건 재현, 상대 기준 9건·고정 기준 0건 역전; JSON/PNG 2회 동일 | 실제 코드로 종합 점수 재계산 |
| J02 | 완료 | `d9495fd` | 선정 8개 DOI Crossref 200; 공개 Ni 수율 표·각주 확인 | 산업 실측 관측/참여자 결과는 확보 못 함 |
| J03 | 완료 | `d9495fd` | 본문118/SI1353개 키, 고정 산출물27개 검사 | 본문 및 SI S9–S12·그림 S3 |
| J04 | 완료 | `2e16f74` 및 본 보고 커밋 | 로컬906 passed; CI34303202556 backend/frontend/desktop 성공 | 최종 보고 HEAD CI도 PR 인계 전 확인 |
| J05 | 완료 | `2e16f74` | 루트/프론트 npm audit 0건; 프론트/Node 재검사 통과 | CI가 발견한 기존 도구 의존성 패치 |

## Assumptions

The latest request authorizes the previously identified manuscript and research-evidence improvements. It does not authorize silently replacing the ranking method, inventing factory observations, contacting participants, or buying data. Current September 8 manuscript/SI are living submission drafts; frozen September 8 analytical packages remain unchanged. New explanatory evidence is dated September 9. Existing human-dependent validation and rights gaps are retained.

## Implementation and scientific interpretation

- Added `scripts/reproduce_paper_methods.py` and its six regression tests. It reuses actual pricing/ranking and structured uncertainty code in an isolated in-memory database. It does not change product formulas or library data.
- Updated the manuscript generator with explicit `--methods-study` and matched-study/seed/output/input checks. Current living September 8 manuscript/SI now include purchased-input mass balance, adopted thermal overhead and selling-margin equations, shared/independent Monte Carlo factor groups, fixed assumptions, failed-trial interpretation and candidate-set normalization.
- SI S9–S12 and Figure S3 contain a synthetic purchase closure, thermal/area uncertainty verification, actual ammonia-cracking candidate scores and narrowly extracted public experimental yield context. Existing main/controlled/robustness numerical packages remain unchanged.
- The new normalization result is 86 removal cases, 9 recomputed-range reversals and zero fixed-reference reversals. Co/MgO-La₂O₃ stays at 4.7411 USD/lb but its composite changes 89.3→77.4; Ni/Al₂O₃ stays at 4.3573 USD/lb and 87.3 points. No catalyst cost changed. Historical removal ledgers contain a carried-forward `scores.total` that the original weighted ranking did not use; the new supplement recomputes totals explicitly and leaves frozen records intact.
- The [eight-work comparison](../sources/paper-methods-prior-work-2026-09-09.md) does not claim that unverified capabilities are absent from prior tools. Rank reversal and cost-responsive synthesis have precedents. COMET's contribution remains the specified catalyst evidence/boundary/decision workflow and its conditional diagnostics, not invention of known formulas or proof of industrial accuracy.

## Evidence and reproducibility

- [Methods study](../paper/methods-2026-09-09/methods_study.json) SHA-256: `3e0334cae853187259e65d147375c1e2b68361b42b8cd9a75dd6682bbf9725ca`.
- JSON and PNG are byte-identical on two local runs. [Manifest](../paper/methods-2026-09-09/provenance.json) includes input/output/code hashes and Python/package versions. [Primary access record](../sources/paper-methods-access-2026-09-09.json) distinguishes DOI identity, HTTP status, challenge HTML and actually readable documents.
- DOI checks initially received three 429 responses; sequential retries returned 200 for all eight. Some publisher requests returned 403 or 200 challenge HTML. The web reader supplied accessible publisher text where noted. Official NLR/DOE PDFs were directly retrieved, and the Ni table was rendered and visually checked. No access controls were bypassed.
- Public Ni yield observations add synthesis context. Their adjacent cost values are published model estimates, not new independent industrial ledgers. No new eligible full-cost observation, empirical MAPE, measured lifetime or actual participant result was fabricated.
- Core formulas, library data, UI/Electron source, LICENSE and frozen analytical packages are unchanged against the base commit. The two dependency lockfiles changed only for the disclosed CI security repair; new hashed evidence files have explicit byte-preserving Git attributes. No UI changed, so new app screenshots were not required; the new scientific figure was visually inspected. The original installed app and database were not replaced.

## Critic pass

The methods text initially omitted a detailed purchased-input/Monte Carlo explanation; it is now present. The new figure count initially missed an older figure whose alt text had no figure number; the generator now counts actual image entries. New-file import-order lint findings were corrected. Source-access failures were classified explicitly. Frontend build retains a non-fatal Tailwind source-map warning; no UI code changed; compatible dependency patches are recorded below. No required truth signal failed three times consecutively.

Current approximate manuscript length is 197 abstract words and 3,771 main-text words by the existing checker. There are six main figures, three SI figures, two main tables and twelve SI tables. This is not a claim that journal eligibility, fees, author approval, commercial rights or industrial validation are resolved.

## Local verification

[Command/time/log manifest](paper-methods-checks-2026-09-09.json): full backend **906 passed in 559.15s**, wrapper 563.221s. Additional six tests were rerun after the final citation-numbering edit (**6 passed in 0.77s**). Final Ruff, manuscript check and first-citation bibliography order passed. Frontend lint 11.698s, build 7.564s, i18n 0.618s; missing keys and untranslated UI labels remain zero. Current local links checked:112, missing:0.

Table 6.2 is unchanged: Pt/C **27.3695 USD/lb** (published cent match); Ni/Al₂O₃ **19.2206 USD/lb, −6.65%**; FCC at footnote-b effective throughput **2.4380 USD/lb, +1.16%**. The nominal FCC throughput diagnostic remains separate. No new performance improvement is claimed: API, MC and costing-engine code did not change. Windows packaging/smoke passed in the existing same-PR CI; no local installer or user database was replaced.

The ten references now follow their first appearance in the manuscript, including the corresponding SI reference. The study's original reference set and price snapshots remain fixed. Source commit `d9495fd`, repair commit `2e16f74` and successful remote CI are recorded below.

## CI repair discovered during final verification

The first source CI [34302629928](https://github.com/hyunjin-kor/COMET/actions/runs/34302629928) failed the unchanged frontend audit gate on `js-yaml`4.3.1. This is not a manuscript or calculator regression. Local `npm audit` reproduced the high-severity finding and the `@humanfs/node` moderate finding. Root audit additionally identified existing Joi low-severity advisories. All referenced GitHub advisories were read; no audit threshold was relaxed.

[Exact lockfile/audit record](paper-methods-ci-repair-2026-09-09.json): `js-yaml`4.3.1→4.3.2 in both locks; frontend `@humanfs/node`0.16.7→0.16.8 with required `@humanfs/core`0.19.2 and its new indirect development-only `@humanfs/types`0.15.0; root Joi18.2.3→18.2.8. No direct dependency, framework or application version was added. The automatic root-license metadata rewrite was reverted, preserving the scope of the patch. `npm ci` installed both exact locks, and audits now report zero findings in both trees.

Patched frontend lint/build/i18n and Node calculator/range/scientific-text/session/About checks pass. Backend code and Python dependencies are unchanged from the 906-test run. The subsequent exact-head CI rechecks all tests and Windows packaging. The earlier statement of no frontend change describes the research-source commit; the sole subsequent frontend change is its dependency lockfile.

The default Git whitespace diagnostic flags byte-preserved CRLF evidence JSON and terminal trailing blank lines in raw logs. A CRLF-aware check of all other changed files passes. Evidence hashes and raw command output were preserved rather than reformatted.

## Final report

이번 방법론·근거 보완 범위는 **완료 5건 / 보류 0건 / 부분 완료 0건**이다. 이는 원고 보완·재현·선정 문헌 검토·검증·의존성 패치의 완료이며, 산업 실측 검증이나 상용 출시의 완료를 뜻하지 않는다. J01–J05 상태·커밋·근거는 위 표에 기록했다. 최초 [T01–T19 실행 기록](autonomous-run-2026-09-06.md)은 보존했다.

소스 `d9495fd`에 이어 보안 패치 `2e16f74`의 [CI34303202556](https://github.com/hyunjin-kor/COMET/actions/runs/34303202556)이 backend·frontend·Windows desktop 모두 성공했다. [CI 증거](paper-methods-ci-2026-09-09.json)에 정확한 SHA, 작업별 시각과 pytest 출력이 있다. 이 보고만 추가한 커밋도 같은 PR에서 CI를 재확인한 뒤 최종 PR 본문에 결과를 기록한다. 최초 CI의 frontend audit 실패와 이후 작업 취소 이력은 숨기지 않았다.

계산 결과: 원가·라이브러리 가격·추천식·고정 분석 27개는 바뀌지 않았다. 새 보충 분석은 현재 코드로 종합 점수를 다시 계산하여 후보 범위의 효과를 설명한다. 86개 후보 제외 사례에서 상대 기준 9건, 원래 점수를 유지한 대조 0건의 순위 역전을 재현했다. 고정 기준의 0건은 해당 대조의 성질이며 새 알고리즘의 우월성 증거가 아니다. Table 6.2는 Pt/C 센트 일치, Ni/Al₂O₃ −6.65%, FCC 각주 b +1.16%로 기존 합격 범위다.

| 검증·성능 항목 | 직전 상태 | 이번 확인 | 해석 |
|---|---|---|---|
| 백엔드 테스트 | 900개 통과 | 906개 통과, 로컬559.15초 | 방법·재현 검사6개 추가; 속도 비교 아님 |
| API·MC·전체 반응군 분석 | 기존 측정 유지 | 해당 코드 불변, 이번 재측정 없음 | 새 성능 향상 주장 없음 |
| 추가 방법 분석 | 없었음 | JSON·PNG 두 번 바이트 동일 | 고정 가격·seed20260906 |
| 프론트 보안 감사 | 신규 공지된 취약점으로 CI 실패 | 루트·프론트 각0건 | 수정 버전 잠금 및 재설치·검증 |
| Windows 패키지 | 이전 검사 통과 | 패치 SHA 빌드·격리 실행 성공 | 사용자 설치 앱 교체 없음 |

사람이 해야 할 일: 조건이 맞는 실제 제조 비용과 연구자 사용 평가를 확보하고, 저자·기관/회사 권리 및 재배포 가능한 자료 범위를 확인한다. 투고 저널의 적합성·최신 지표·비용과 저자 정보를 최종 확정한다. 검토 뒤 예정 태그 v1.4.0 푸시·릴리스 결과·Zenodo DOI를 확인한다. 이번에는 병합·태그·릴리스·Zenodo 게시·서비스 배포·구매·외부 연락을 수행하지 않았다.

가정: 9월8일 원고/SI는 보완 가능한 현재 초안으로 취급하고, 당시 고정 분석 패키지는 보존했다. 비교 기준 선택은 임의로 바꾸지 않았다. 새 문헌 대조는 선정한8건에 한정하며 체계적 전수 고찰로 소개하지 않았다. 새 CI 보안 실패는 기존 범위 안의 수정 버전으로 해결했으며 필요한 간접 개발 의존성을 기록했다.

확인 못 한 것: 독립 산업 전체 원가에 대한 MAPE, 같은 반응 조건의 성능·수명과 비용의 대응, 실제 외부 참여자 결과, 상용 권리 계약, 최종 투고·게재 적합성. MAPE 미산정은 오차0%가 아니다. 일부 출판사 직접 HTTP 접근 실패는 접근 기록에 남겼고, 읽을 수 있는 공개 자료의 범위만 사용했다. 이전 실행의 사람·외부 자료 의존 보류 항목은 이 작업의 완료로 해소되지 않는다.
