# Screens

Every screen in the app, roughly in the order a session visits them. The
[README](../README.md#screens) shows one of them.

## Cost estimate

<img src="assets/screen-cost-estimate-composition.png" alt="Composition input" width="100%" />

Set active metals, promoters, and support balance. Each price shows where it came from.

<img src="assets/screen-cost-estimate-preparation.png" alt="Preparation route" width="100%" />

Build the preparation route from unit operations and pick the campaign scale.

## Live metal prices

<img src="assets/screen-live-metal-prices-overview.png" alt="Price overview" width="100%" />

Every tracked metal with its current quote basis, source, and freshness.

<img src="assets/screen-live-metal-prices-trend.png" alt="Price trend" width="100%" />

Daily history for a single metal, with the quote basis behind each point.

## Literature benchmarks

<img src="assets/screen-literature-benchmarks-routes.png" alt="Benchmark comparison" width="100%" />

Published routes for one reaction family, side by side.

<img src="assets/screen-literature-benchmarks-detail.png" alt="Benchmark detail" width="100%" />

A single benchmark in full, loadable into the calculator as a starting point.

## Result and uncertainty

<img src="assets/screen-result.png" alt="Result screen" width="100%" />

The full cost ledger, with the price evidence behind every line.

<img src="assets/screen-estimate-range.png" alt="Monte Carlo range" width="100%" />

Monte Carlo uncertainty analysis, giving a cost range instead of a single number.

## Source library

<img src="assets/screen-source-library.png" alt="Source library" width="100%" />

Every price the calculator can use in one place: materials, step rates and route
templates, each with its quote basis, source and freshness. Filter by category,
catalyst domain or application, and open the public source behind any row.

---

These images are regenerated from the running app with `scripts/capture_readme_screens.mjs`.
