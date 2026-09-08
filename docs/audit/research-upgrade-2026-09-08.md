# Research evidence upgrade — 2026-09-08

Baseline: clean 16ca12f, prepared 1.4.0, PR112; previous full suite 883 passed. Existing frozen submission/controlled packages remain preserved. Matched independent industrial observations remain absent.

| ID | Status | Commit | Evidence | Notes |
|---|---|---|---|---|
| S01 | Complete | pending | Code/manuscript/evidence audit | Joint robustness missing |
| S02 | Complete | pending | Regression oracles first | Script unrounded totals vs rounded app; electrode tie uses powder cost |
| S03 | Complete | pending | Fixed design below | New output directory |
| S04 | Complete | pending | Generated claims/results | Scientific contribution and limits |
| S05 | In progress | pending | Full verification / PR112 | No release/merge |

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

The first packaging command was stopped before Electron packaging after noticing an unnecessary code-signing auto-discovery override; the process tree ended and subsequent commands contain no signing override. A later build failed because one npm separator caused `never` to become a build target. The prior verified nested-npm form uses two separators to deliver `--publish never` to electron-builder; this is being rerun with normal signing behavior. No tag, release, publish or signature bypass was completed.

The manuscript initially rejected differently named reference snapshots. Exact comparison showed only `generated_at` and `history_file` differed; all other metadata, values, units and sources match. The equivalence check excludes precisely these two run metadata fields, with regressions rejecting changed prices, units and sources. Source/JSON hashes remain recorded separately.

## External evidence

Crossref HTTP 200 verifies the OECD/JRC handbook DOI `10.1787/9789264043466-en`; JRC repository HTTP 200. The JRC sensitivity guide is readable by web retrieval but direct httpx returns 403; status is recorded honestly. No paid source or account used. Existing matched industrial observations, real user participants, company/data rights, author approvals and requested journal eligibility remain unresolved C14 facts. None were substituted with model output.
