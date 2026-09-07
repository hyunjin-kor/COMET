# Release Notes

## 1.4.0 — prepared, not published (2026-09-06)

The package versions are 1.4.0. The latest verified public release remains v1.3.24. No tag, GitHub release, Zenodo deposit or deployment was created in this run.

- Choose live quotes or a common published month throughout the calculator, prices and literature comparison. The monthly reference uses IMF and Johnson Matthey averages; optional UN Comtrade support values retain explicit bulk-proxy provenance ([#104](https://github.com/hyunjin-kor/COMET/pull/104), [#105](https://github.com/hyunjin-kor/COMET/pull/105), [#106](https://github.com/hyunjin-kor/COMET/pull/106)).
- Compare 28 named thermal preparation methods with processing costs at the chosen production scale. Card identity and repeated operations now survive scale fitting ([#107](https://github.com/hyunjin-kor/COMET/pull/107)).
- Unchecking and rechecking a manufacturing operation restores its repeated steps and keeps the selected method. A searchable method list, separate details and fixed-size operation rows keep the preparation screen steady while editing; saved edits survive scale changes and reloading ([audit](audit/manufacturing-selection-2026-09-07.md)).
- Researcher-facing terms, clearer Korean labels and walkthrough fixes from [#108](https://github.com/hyunjin-kor/COMET/pull/108), [#109](https://github.com/hyunjin-kor/COMET/pull/109) and [#110](https://github.com/hyunjin-kor/COMET/pull/110) are included; the Korean getting-started guide explains the two workflows.
- Monthly quotes are reviewed against their publication month. Annual anchors retain their lower evidence confidence without being mislabelled as stale monthly observations.
- An optional uncertainty `seed` reproduces a run; omitting it produces independent samples. Benchmark ties resolve consistently.
- Electrode headline, ledger and chart use the same area-based assembly cost. Thermal campaign and margin values are excluded from the electrode result.
- Direct Johnson Matthey and Westmetall sources take priority for the specified metals, with slower Yahoo polling and documented fallbacks.
- The paper reproduction command freezes input hashes and the execution environment, runs all analyses and generates six figures. Source audits distinguish verified DOI registrations, restricted URLs and observed missing pages.
- Verified free import observations for ten support series (28 observations over April–June) now work offline on the reference basis; estimated or missing weights are excluded. A keyless snapshot collector records missing months and stops at provider limits; the paper can explicitly include this snapshot and select a shared publication month.
- Changing production scale waits for the selected method's fitted steps before calculation, preventing a stale large-scale kiln from causing a small-scale validation error. Loading failures show recovery guidance.
- The CO2-to-methanol and HER source audit corrects reaction attribution and DOI links, adds a freely available direct NiMo study and identifies model assumptions. Benchmark scores now label price evidence explicitly. Source-specific carbon/zeolite LCA pairs are documented without filling generic-material gaps with assumed factors.

- Additional primary-literature checks clarify grade, formulation and manufacturing assumptions for fifteen candidates across ammonia cracking, olefin metathesis, hydrodeoxygenation and NH3-SCR, without changing their numerical inputs.
- A unified May 2026 manuscript, SI and six figures share frozen source hashes. A separate public-contract/catalog audit keeps unmatched purchase evidence out of manufacturing-accuracy metrics.
- Results and CSV now preserve the actual costing scope, proxy rates, scale substitutions and declared omissions. Missing operations remain uncosted.
- Thermal estimates accept an optional effective production rate with a source/assumption note. An explicit purchased-precursor recipe can account for component content, purity, retention yield and net solvent/wash consumption; default estimates are unchanged, and additional recipe inputs do not silently expand LCA coverage.
- Compare 2–4 saved estimates under a shared price snapshot and reference operating conditions, alongside historical and price-only results. Composition and manufacturing differences remain visible.
- Store supplier, quote date, quantity, grade and source evidence with manual inputs. Local actual-cost records retain exclusion reasons and only report errors for documented matching thermal full-cost conditions; they are not independent validation data.
- Headline prices fit narrow cards on one line. Net-price wording now states that selling margin is included before recovery credit, and the cost pie uses a consistent selling-price denominator with consumable slices.

The [practical costing audit](audit/practical-costing-2026-09-07.md) records these changes, synthetic test boundaries, default-result regression and performance observations.

Validation and remaining checks are recorded in the [run audit](audit/autonomous-run-2026-09-06.md) and [release checklist](release-checklist.md). The published Table 6.2 acceptance cases remain Pt/C to the cent, Ni within 7%, and FCC within 2% using its footnote-b rate. Pricing-input changes and display corrections are documented individually; no new rate was invented for uncosted operations.

The [free-data update audit](audit/free-data-update-2026-09-06.md) and [September7 resumption](audit/free-data-resume-2026-09-07.md) record historical verification, numerical effects and source gaps. The [validation/submission update](audit/validation-submission-2026-09-07.md) records the latest checks and common-month analysis. Data acquisition remains free; no paid purchase, subscription or billable API was used.

The authoritative release log for COMET lives on GitHub:

**https://github.com/hyunjin-kor/COMET/releases**

Every tagged release (`vX.Y.Z`) carries the changelog, validation results,
and download links for that version. The latest release also redirects via
the repository's homepage URL:

**https://github.com/hyunjin-kor/COMET/releases/latest**

This file used to mirror release entries by hand and stopped at v1.1.13;
it has been replaced by the GitHub Releases feed so there is exactly one
source of truth. To find a specific version's notes, browse the
[Releases page](https://github.com/hyunjin-kor/COMET/releases) or run:

```bash
gh release view <tag> --repo hyunjin-kor/COMET
```
