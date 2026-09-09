# Paper methods and evidence audit — 2026-09-09

Base commit: `3296218a0a81220a4d327eb2bf2dcc37af2ee395`; branch `autonomous/2026-09-06`; existing PR112. Scope: complete methods/SI and evidence review, explain candidate-set normalization without changing the current engine.

| ID | 상태 | 커밋 | 근거 명령 출력 요약 | 메모 |
|---|---|---|---|---|
| J01 | 완료 | `d9495fd` | 86건 재현, 상대 기준 9건·고정 기준 0건 역전; JSON/PNG 2회 동일 | 실제 코드로 종합 점수 재계산 |
| J02 | 완료 | `d9495fd` | 선정 8개 DOI Crossref 200; 공개 Ni 수율 표·각주 확인 | 산업 실측 관측/참여자 결과는 확보 못 함 |
| J03 | 완료 | `d9495fd` | 본문118/SI1353개 키, 고정 산출물27개 검사 | 본문 및 SI S9–S12·그림 S3 |
| J04 | 진행 | — | 906 passed; 원고·수치 검증 통과; 새 CI 대기 | 기존 CI audit 실패는 J05에서 수정 |
| J05 | 완료 | 보안 패치 커밋 | 루트/프론트 npm audit 0건; 프론트/Node 재검사 통과 | CI가 발견한 기존 도구 의존성 패치 |

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
- Source/data/license/frontend/Electron/frozen-package diff against the base commit is empty. No UI changed, so new app screenshots were not required; the new scientific figure was visually inspected. The original installed app and database were not replaced.

## Critic pass

The methods text initially omitted a detailed purchased-input/Monte Carlo explanation; it is now present. The new figure count initially missed an older figure whose alt text had no figure number; the generator now counts actual image entries. New-file import-order lint findings were corrected. Source-access failures were classified explicitly. Frontend build retains a non-fatal Tailwind source-map warning; no frontend dependency or code changed. No required truth signal failed three times consecutively.

Current approximate manuscript length is 197 abstract words and 3,771 main-text words by the existing checker. There are six main figures, three SI figures, two main tables and twelve SI tables. This is not a claim that journal eligibility, fees, author approval, commercial rights or industrial validation are resolved.

## Local verification

[Command/time/log manifest](paper-methods-checks-2026-09-09.json): full backend **906 passed in 559.15s**, wrapper 563.221s. Additional six tests were rerun after the final citation-numbering edit (**6 passed in 0.77s**). Final Ruff, manuscript check and first-citation bibliography order passed. Frontend lint 11.698s, build 7.564s, i18n 0.618s; missing keys and untranslated UI labels remain zero. Current local links checked:112, missing:0.

Table 6.2 is unchanged: Pt/C **27.3695 USD/lb** (published cent match); Ni/Al₂O₃ **19.2206 USD/lb, −6.65%**; FCC at footnote-b effective throughput **2.4380 USD/lb, +1.16%**. The nominal FCC throughput diagnostic remains separate. No new performance improvement is claimed: API, MC and costing-engine code did not change. Windows packaging/smoke will be checked by the existing same-PR CI; no local installer or user database was replaced.

The ten references now follow their first appearance in the manuscript, including the corresponding SI reference. The study's original reference set and price snapshots remain fixed. Source commit and remote CI will be recorded in the final report after push.

## CI repair discovered during final verification

The first source CI [34302629928](https://github.com/hyunjin-kor/COMET/actions/runs/34302629928) failed the unchanged frontend audit gate on `js-yaml`4.3.1. This is not a manuscript or calculator regression. Local `npm audit` reproduced the high-severity finding and the `@humanfs/node` moderate finding. Root audit additionally identified existing Joi low-severity advisories. All referenced GitHub advisories were read; no audit threshold was relaxed.

[Exact lockfile/audit record](paper-methods-ci-repair-2026-09-09.json): `js-yaml`4.3.1→4.3.2 in both locks; frontend `@humanfs/node`0.16.7→0.16.8 with required `@humanfs/core`0.19.2 and its new indirect development-only `@humanfs/types`0.15.0; root Joi18.2.3→18.2.8. No direct dependency, framework or application version was added. The automatic root-license metadata rewrite was reverted, preserving the scope of the patch. `npm ci` installed both exact locks, and audits now report zero findings in both trees.

Patched frontend lint/build/i18n and Node calculator/range/scientific-text/session/About checks pass. Backend code and Python dependencies are unchanged from the 906-test run. The subsequent exact-head CI rechecks all tests and Windows packaging. The earlier statement of no frontend change describes the research-source commit; the sole subsequent frontend change is its dependency lockfile.
