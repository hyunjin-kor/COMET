# Controlled scenarios — 2026-09-08

Re-run of the documented [controlled design](../controlled-2026-09-07/README.md) with corrected functional-unit comparisons. The original May reference/live snapshots remain the inputs. The selected reference file regenerated in the current primary package differs only in run timestamp and history filename; all other metadata and price values match. These two non-scientific fields are explicitly excluded by the manuscript equivalence check, which rejects changed prices, sources or units.

Reproduce with `python scripts/run_controlled_cases.py --reference-basis docs/paper/submission-2026-09-07/reference_basis_2026-09-07.json --live-basis docs/paper/submission-2026-09-07/live_basis_2026-09-07.json --out-dir _local/controlled-research-replay --seed 20260906`.
