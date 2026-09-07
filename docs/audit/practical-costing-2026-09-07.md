# Practical costing update — 2026-09-07

User authorization: “다음 개선 사항들 다 진행해”. Same branch `autonomous/2026-09-06`, same [PR112](https://github.com/hyunjin-kor/COMET/pull/112), no merge/release.

## Verified starting point

Clean `ff6155e1b56d1e400438fbcb5a4f40dea06e605e`. Prior completed run: local **710 passed / 459.11 s**, final-head CI **710 passed / 594.59 s**, frontend passed; Windows build + smoke **197.81 s**. These are previous-run results, not a new test run. Table 6.2: Pt/C 27.3695 USD/lb (27.37 rounded); Ni/Al2O3 19.2206 (−6.65%); FCC at 67 short ton/day 2.4380 (+1.16%). Evidence: `validation-submission-2026-09-07.md` and its check JSON.

## Tasks

| ID | 상태 | 커밋 | 근거 명령 출력 요약 | 메모 |
|---|---|---|---|---|
| P01 | 완료 | integration commit (recorded below after commit) | 8 scope tests; API save/load scope; real Chrome costed/partial display and $0.1573 single-line; pie denominator fixed | 계산 범위 표시와 확인된 결과 문구·가격 줄바꿈 수정 |
| P02 | 완료 | integration commit (recorded below after commit) | 13 combined practical tests; 20 short tons at5/day →5days; default10/day →3days; actual UI persistence/CSV | 실제 생산 속도 및 생산 기간 근거 |
| P03 | 완료 | integration commit (recorded below after commit) | Purchased precursor fixture2kg/kg and10USD/kg; CSV+reload; zero-price/markup/invalid inputs; LCA boundary explicit | 전구체 함량·순도·수율 및 소모재 투입량 |
| P04 | 완료 | integration commit (recorded below after commit) | 17 comparison tests; Chrome2saved estimates and common production rate; historical/same-price/common-condition columns | 저장한 추정의 동일 조건 비교 |
| P05 | 완료 | integration commit (recorded below after commit) | 32 evidence tests; supplier/date JSON roundtrip; Chrome unmatched quote stays excluded/MAPEnull after reload | 로컬 구매 근거와 실제 비용 관측 |
| P06 | 진행 | integration commit (recorded below after commit) | 780 passed423.66s; frontend lint/build/i18n0+Node12 + range rules6; frozen30families116candidates unchanged; desktop/CI pending; range UI1000/1000 and matching baseline passed | 전체 검증·화면·로그·동일 PR 최종화 |

## Conservative assumptions

- Optional effective production rate is expressed in **short ton/day**, consistent with the existing engine. Production duration includes the existing cleaning allowance and is derived, avoiding conflicting independent duration inputs.
- Recipe mode requires explicit purchased-precursor price and retained-component fraction, purity, and retention yield. The same component cannot also apply a precursor markup. Solvent/wash additions are net purchased consumables per kg of finished catalyst; no automatic recovery credit or invented default consumption.
- New production/recipe inputs apply to thermal manufacture. Electrode manufacturing scenarios retain their published area-based boundary.
- Purchase evidence is user supplied local metadata, not an independently verified source. Actual observations only produce an error when matching requirements are satisfied; unmatched records remain visible with reasons.
- No paid data, new factors, or new processing rates; old frozen paper outputs preserved.

## Verification and numerical effects

- Full backend: **780 passed in423.66s** (wall426.933s); 70 new tests. Node calculator rules12passed. Frontend0missing/0untranslated, lint/buildpassed; ruffpassed. See `practical-checks-2026-09-07.json` and commandlogs.
- Table6.2 unchanged: Pt/C27.3695→27.37USD/lb; Ni19.2206 (−6.65%); FCCfootnote-b2.4380 (+1.16%).
- `practical-default-regression-2026-09-07.json`: archivedff6155e vs current vs frozenMaypaper all-family JSON difference0; currenttworunsbyte-identical; 30families116candidates90profile rankings30performance-excludedrankings. Seeded MC1000/10000 JSONexactlyequal.
- Synthetic optional-input arithmetic (not an empirical observation):20wt% finishedNi /25%pure-precursorcontent /80%purity /50%retention =2kgprecursor/kgcatalyst. At5USD/kgprecursor thischarges10USD/kgcatalyst. Net wash3kg/kg×0.5USD/kg adds1.5USD/kg; supportretainsits80wt%×1USD/lb contribution. The previous component metal-price contribution is replaced, not added.20shorttons at5/day +1cleaningday =5days rather than nominal3days; processing increases5/3whilemarginfractionandmaterialcoststayconstant.
- Existing thermal pie mixed material-only percentages with selling-price percentages. Synthetic20USD/lb sale,10materials,5processing previouslysummed150%; corrected20+30+25+25=100%. New consumables have their own slice. This is a display correction, not an engine change.
- Real Chrome152,1440×1100: five flows verified; eight finalscreens in `practical-ui-2026-09-07.json`. Manualpurchase metadata, precursor/rate/consumables, partialscope, CSV, save/load, comparisonand area-onlyelectrodeheadline passed. Optional range integration anddesktop are final-check items.

## Observed performance

| Measurement | ff6155e baseline | Current | Context |
|---|---:|---:|---|
| calculate20-requestmedian | 2.539ms | 2.591ms | In-process FastAPI TestClient after3warmups |
| MC1000 | 0.0730s | 0.0794s | Same syntheticinputs,seed20260906 |
| MC10000 two-runmedian | 0.4362s | 0.5542s | +27.1%; no optimization claim |
| run_all_families | 1.907s | 1.774s | Same frozenMayinput |

These are workstation observations during other verification, not a controlled performance improvement experiment. The cause of the MC increase was not separately isolated.

## Critic findings and bounded corrections

- Added charged-price checks after a critic demonstrated that a nonzero precursor cost could incorrectly warn about a zero retained-metal reference price, and viceversa.
- Library-name aliases and unrecognized/missing costing scopes now prevent false eligibility in localactual-cost comparisons. Newcountertests pass.
- Manualprice harmonization moves its supplier/date evidence together; unknown grades and different library IDs are explicitly not assumed equivalent.
- Browser harness corrections: localized language-button label, opening collapsed observation details, and a select label containing option text. These were selector/wait mistakes in three separate UI subchecks, not application exceptions. Full/backend/focused checks passed between corrections; finalbrowserflows passed with0pageerrors. The intermediatefailure screenshot is retained as audit evidence; no data wasdeleted.
- Check-output wrapper initially failed to print Nodecheckmarkcharacters undercp949 after Node12 + range rules6passed. UTF-8 stdoutcorrected; Node12 + range rules6rerunpassed.
- Finalreview found the range page rebuilt inputs without optional recipe/throughput fields. They are now propagated, including pricebasis/template/MEA scenario, and fixed recipe/solvent assumptions are explicitly displayed/exported. FinalrangeUIcheckrecord follows.

## Limits and human follow-up

- Local observed-cost comparison is limited to matched, documented mass-basedthermalfullcost. Electrode and recipe-consumption observations may be stored but remain excluded until their observedinputboundaries can be matched. This is an explicit conservative scope, not a claim of industrialvalidation.
- No actual independent fullmanufacturing-cost observations were added. No new free-source collection was needed for these input/features; no paid data/API/key/purchase wasused.
- Precursoryieldlosses, solvent/wastewaterimpacts and new processingunitrates are notinvented. Frozenpaperartifacts and licenses unchanged.
- Human: review/mergePR112; then tagv1.4.0, verifyrelease/updaterassets, Zenodo versionDOI andfinaljournal/authorshiprequirements. Publishedrelease wasrechecked asv1.3.24;1.4.0 stays preparedsource.
