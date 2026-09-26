# Research evidence upgrade — 2026-09-08

Baseline: clean 16ca12f, prepared 1.4.0, PR112; previous full suite 883 passed. Existing frozen submission/controlled packages remain preserved. Matched independent industrial observations remain absent.

| ID | Status | Commit | Evidence | Notes |
|---|---|---|---|---|
| S01 | Complete | 24d95b1 | Code/manuscript/evidence audit | Fixed design for joint and structural sensitivity |
| S02 | Complete | 24d95b1 | Regression oracles first | App/paper rounding and cost-unit mismatch repaired |
| S03 | Complete | 24d95b1 | 4,728,570 scenarios; identical repeat | Frozen JSON/CSV/figures |
| S04 | Complete | 24d95b1 | 109/1,307 claim keys; manuscript/SI | Partial inventory and empirical limits retained |
| S05 | Complete | 24d95b1 | 900 CI tests; frontend/desktop CI pass | Same PR, no release/merge |

## Design fixed before execution
1. Cross complete synchronous monthly metal states with four-criterion simplex increments 0.1 and 0.05. Equal weighting is an enumerated scenario convention, not a population probability. Hold reference source annotations, anchors, support prices, composition, routes and rubric scores fixed. Recompute evidence cost shares. Historical counterfactuals are not as-of forecasts.
2. Report reference balanced choice retention, candidate first-rank frequencies and mean/worst composite-score regret. Regret is the gap to the maximum rounded score, neither money nor measured performance.
3. Delete each nonwinning candidate at reference prices/balanced weights. Compare re-normalization against the same survivors retaining original normalization. Record changed winners and both score ledgers.
4. Adversarially vary each candidate route/performance score within +/-2, +/-5 and +/-10 points clipped to [0,100]. Fixed weights, prices and evidence. Report survival of the original winner at relevant pairwise worst-case box corners. Bounds are analyst scenarios, not elicited uncertainty.
5. Preserve per-state score/cost ledgers, CSV and figures; input/source SHA-256 and runtime versions. Repeat execution and hand-computable synthetic oracles. No optimized weights or empirical validation claim.

## Assumptions and limits
Free data only. Finite retrospective scenarios support conditional robustness. Industrial accuracy, activity/lifetime equivalence, real user evaluation, company rights and journal eligibility need actual external evidence. C14 remains blocked. Initial state-update helper hit the Windows default text encoding before any writes; rerun with UTF-8.


## Verified changes and results

- Reproduced 2 rounding/functional-unit tie failures and 4 mixed-unit display failures before repair. Focused regressions pass. The full suite passed **898 tests in 522.51 s**; two subsequently added study-integrity/equivalence tests are included in the **30 passing focused tests**. Final CI will test the complete 900-test source.
- New study: 89 synchronous months × 1,771 fine-grid weights × 30 families = **4,728,570** enumerated scenarios. Median reference-choice first-rank share **60.50%**; **11/30** below half. Nonwinner removal changes **9/86** cases across 9 families. Score boxes ±2/±5/±10 leave **20/10/7** families robust. Coarse/fine grid maximum candidate-share difference **7.59 percentage points**; no continuous convergence claim.
- First successful study **39.374 s**, repeat **41.407 s**. JSON/CSV/PNG/SVG/provenance all byte-identical. Numerical SHA-256 `1b3cf44a148cf2b95435d6148b75d4f12f915c1c58c8743ef106821c9bd28059`. The added README is documentation, outside the original numerical-output hash list.
- Primary paper replay **26.282 s**; all-families reference **1.660 s**, history replay **7.435 s**, break-even **9.793 s**. Controlled replay **2.524 s**. These are new research-run timings, not claims of runtime optimization; hardware load differs from prior runs.
- Correcting paper/app score rounding changes the single-reference simplex median retention from **56.9930% to 57.1678%**, below-half families **10 to 11**. Shipped-profile rankings in the all-families reference dataset are unchanged. The four incomplete electrode families now expose consistent powder-cost values to break-even analysis: precious/base cost crossings **12 to 11**, median crossing multiplier **0.0038 to 0.0026**, crossings within 0.1–10 **3 to 1**. These are repaired comparison boundaries, not new prices or changed cost formulas. Full before/after family ledgers: `research-numerical-delta-2026-09-08.json`.
- Table 6.2 unchanged: Pt/C **27.3695 USD/lb**, cents match; Ni/alumina **19.2206**, **−6.65%**; FCC at published footnote-b 67 short tons/day **2.4380**, **+1.16%**. Nominal 150 short tons/day remains a separate diagnostic.
- Frontend lint/build pass (**4.937/4.269 s**); i18n missing/untranslated labels **0**; Ruff pass; **34 Node tests** pass. Browser verifies CO2RR cards use catalyst powder cost uniformly in Korean/kg and English/lb; fully specified AEM overview retains area cost. Screens: `screens/research-co2rr-powder-*-2026-09-08.png`.
- New manuscript **3,051 approximate main-text words**, abstract **192**, **109** keyed numerical references; SI **1,307**, **8 tables / 2 figures**. Primary 27 outputs and both dated manuscript renderings verify. Earlier frozen files are untouched.

## Failures and conservative decisions

Initial study validation rejected support HS unit-value series; the prespecified metal-only variation now explicitly holds those series fixed. A second study run exposed mixed powder/area labels in four actual families; focused regressions reproduced the issue and the existing powder comparison was made explicit before the successful run. No assembly data were invented. Windows state-writing needed explicit UTF-8. Import-order lint findings were corrected surgically.

The first packaging command was stopped before Electron packaging after noticing an unnecessary code-signing auto-discovery override; the process tree ended and subsequent commands contain no signing override. A later build failed because one npm separator caused `never` to become a build target. The prior verified nested-npm form uses two separators to deliver `--publish never` to electron-builder; this passed with normal signing behavior. No tag, release, publish or signature bypass was completed.

The manuscript initially rejected differently named reference snapshots. Exact comparison showed only `generated_at` and `history_file` differed; all other metadata, values, units and sources match. The equivalence check excludes precisely these two run metadata fields, with regressions rejecting changed prices, units and sources. Source/JSON hashes remain recorded separately.

## External evidence

Crossref HTTP 200 verifies the OECD/JRC handbook DOI `10.1787/9789264043466-en`; JRC repository HTTP 200. The JRC sensitivity guide is readable by web retrieval but direct httpx returns 403; status is recorded honestly. No paid source or account used. Existing matched industrial observations, real user participants, company/data rights, author approvals and requested journal eligibility remain unresolved C14 facts. None were substituted with model output.


## Final local verification

Windows build passed in **167.572 s** with the existing Python 3.11 runtime and normal signing behavior. The exact command is `npm run build -- -- --publish never`; both npm separators are needed by the nested scripts. Desktop smoke passed in **17.311 s**, version 1.4.0, one window, price/calculate HTTP 200, isolated temporary profile. The local installer is prepared; the user's installed application was not replaced.

| Measurement | First run | Repeat / final | Interpretation |
|---|---:|---:|---|
| Joint robustness | 39.374 s | 41.407 s | Same JSON, CSV, PNG, SVG and provenance bytes |
| Primary paper pipeline | — | 26.282 s | Corrected scientific package regenerated |
| Reference all-families | — | 1.660 s | Part of the primary pipeline |
| Windows full build | prior review 173.711 s | 167.572 s | Different host load; no optimization claim |
| Desktop smoke | prior review 16.614 s | 17.311 s | Isolated profile and successful startup/calculation |

The new dated analytical files total approximately 10.9 MB. Existing `backend/data`, LICENSE, 2026-09-07 submission/controlled artifacts, manuscript and SI have **no Git diff** from 16ca12f. New manuscripts/claim-map local links all resolve. Source and prose whitespace checks pass. Generated JSON/CSV retain their recorded CRLF byte hashes and Matplotlib SVG retains renderer whitespace; raw artifacts were not reformatted to silence whitespace diagnostics.

Source commit **24d95b19d670631bd4820c3d3787d316c37a3fea** is pushed to the existing PR112. Source CI: https://github.com/hyunjin-kor/COMET/actions/runs/34183748797 (all three jobs passed; exact source commit verified). Latest public release reverified with `gh release list -L 1`: **v1.3.24**; prepared versions remain **1.4.0**. No tag, release, merge, installation, deployment, Zenodo action, subscription payment or external participant message was performed.

Direct DOI resolution for the newly cited handbook redirects to OECD and returns 403; Crossref/JRC identity remains verified. Direct publisher retrieval is not claimed. The final source-check JSON retains all response statuses.


## Final report

**Completed 5 / deferred 0 / partial 0** for this bounded research upgrade (S01–S05). Existing C14 human-dependent prerequisites remain unresolved and are not counted as newly completed work. The task table above identifies the source commit and evidence for each item.

Source CI **34183748797** passed all three jobs for **24d95b19d670631bd4820c3d3787d316c37a3fea**: backend 10m3s, desktop 3m36s, frontend 24s. The backend result was **900 passed**. The precise warning count and elapsed test time are retained in `research-source-ci-2026-09-08.json`. The final audit-only commit receives the normal CI rerun; its status and exact commit/run link are verified in PR112 before the user-facing final handoff.

The work adds a joint price/preference experiment, candidate-removal controls and adverse rubric scenarios; repairs app/paper rank and functional-unit mismatches; regenerates the primary/controlled research package and manuscript/SI; preserves original inputs and earlier results. Model costs and Table 6.2 remain unchanged; corrected weight and break-even comparisons and the timing table are documented above.

**Human work remaining:** obtain matched independent cost observations and actual user-study participants if claiming empirical accuracy/usability; confirm authors/affiliations/contributions/conflicts, company and data rights, requested journal year/category/quartile and publication-cost coverage. Resolve existing rights gates before a person pushes v1.4.0 and verifies a release, Zenodo DOI and eventual journal submission. No task outcome is an authorization or guarantee of those actions.

**Conservative assumptions:** use the preserved May 2026 free snapshots; hold support/anchor/source metadata fixed for the metal-only historical experiment; use stated finite preference grids and analyst score boxes, not fitted distributions; use powder comparisons where assembly inputs are incomplete; keep existing min–max normalization and report its candidate-set dependence; preserve all unmodeled processes and LCA gaps. The two metadata-only reference-snapshot differences are explicitly checked.

**Not confirmed:** independent matched industrial manufacturing accuracy, real user-evaluation outcomes, commercial data/company rights, final author approvals, journal eligibility/acceptance, continuous-grid convergence or any future winning probability. OECD/JRC bibliographic identity is verified; direct OECD and direct JRC-guide HTTP retrieval returned 403. No paid source was used. All limitations remain visible in the manuscript and claim map.
