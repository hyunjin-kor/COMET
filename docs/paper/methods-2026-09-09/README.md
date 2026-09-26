# Additional methods verification — 2026-09-09

This supplement adds a purchased-input arithmetic example, synthetic Monte Carlo API checks, a replay of all frozen candidate removals, and narrowly extracted experimental yield context. It changes no product formulas, price library, original reference winners or frozen study outputs.

- [Numerical results](methods_study.json)
- [Input/output hashes and environment](provenance.json)
- [Normalization figure](normalization_example.png)
- [Primary-work review](../../sources/paper-methods-prior-work-2026-09-09.md)
- [Korean explanation](../normalization-explained-2026-09-09.ko.md)

```bash
python scripts/reproduce_paper_methods.py --out-dir _local/methods-replay-new
python scripts/build_submission_manuscript.py --date 2026-09-08 --directory docs/paper/submission-2026-09-08 --robustness docs/paper/robustness-2026-09-08 --methods-study docs/paper/methods-2026-09-09/methods_study.json --check
```

Use a new or empty output directory. The runner uses an isolated in-memory database and explicit synthetic prices for the API checks; it does not collect market prices or touch the user's database. The paired seed checks and fixed-input collapse checks are executable assertions. Six regression tests cover input immutability, the actual reversal, related-study/seed requirements and functional units.

The numerical JSON and PNG were byte-identical on two local runs. The environment manifest records package versions; identical seeds alone do not guarantee cross-version binary reproducibility. The normalization replay reuses original economics, evidence, route and performance scores and recomputes composite totals after removal. Some historical diagnostic ledgers carry an old `scores.total`; their ranking used explicitly weighted component scores. Those frozen records are preserved, and this supplement does not treat the carried-forward value as the post-removal score.

Published Ni yields are experimental synthesis observations; the adjacent published costs are modeled materials costs. No industrial cost error, empirical confidence interval, calibrated lifetime, participant result or new source-data commercial permission is inferred.
