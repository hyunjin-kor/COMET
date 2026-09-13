# Observed-price catalyst crossover study

Local research results, 13 September 2026. These figures are separate from the four figures currently embedded in the Application Note; the v36 manuscript has not been revised by this study. [Korean interpretation](report.ko.md).

## Finding

Observed metal-price changes can reverse the modeled cost ordering of catalyst candidates without changing the highest-ranked candidate under the catalog's balanced decision weights. The clearest common mechanism is cobalt exposure: the September–October 2025 price change reverses the lowest-cost candidate in both ammonia cracking and methane dry reforming.

| Modeled delivered cost, USD/lb | September 2025 prices | October 2025 prices |
|---|---:|---:|
| Ammonia: Co/Mg–La proxy | 3.9770 | 4.3070 |
| Ammonia: Ni/alumina proxy | 4.0329 | 4.0319 |
| Dry reforming: Ni–Co/Al–Mg proxy | 5.0329 | 5.3957 |
| Dry reforming: Ni/zeolite proxy | 5.1535 | 5.1525 |

Cobalt rises from 15.1872 to 19.5706 USD/lb while nickel changes from 6.8507 to 6.8457 USD/lb. Changing cobalt alone accounts for 0.3300 of the 0.3310 USD/lb change in the ammonia pair's cost difference, and 0.3631 of the 0.3638 USD/lb change in the dry-reforming pair's difference. Other inputs remain fixed. In October, the nickel alternative costs approximately 6.4% less than the cobalt alternative for ammonia cracking and 4.5% less for dry reforming. These are conditional model comparisons, not contemporaneous supplier quotations. The underlying full-family calculation retains all four candidates in each case.

Across the 89 monthly states, the lowest-cost candidate changes eight times for ammonia cracking, nine times for dry reforming, and eleven times for water-gas shift. The balanced application winner does not change in any of these three families. A price alert should therefore distinguish a cost crossover from a change in the composite recommendation.

## Complete scope and controls

All **30 families, 116 candidates, and 168 within-family pairs** were included: 23 thermal families and seven electrochemical families. There are 30,740 candidate-state evaluations: 116 × (89 + 176). No candidates or weights were selected to force a crossover. Representative panels were chosen after the full scan for interpretable metal exposure; all results, including null results, remain available.

| Quantity | Monthly replay | Daily replay |
|---|---:|---:|
| Common observations | 89 | 176 |
| Observation window | 2019-01 to 2026-05 | 2026-01-02 to 2026-09-11 |
| Metal prices varied | 14 | 10 |
| Families with a lowest-cost change | 6 | 1 |
| Families with a lowest-cost change between states having >1% leads | 5 | 0 |
| Families with any pairwise cost crossover | 10 | 4 |
| Pairs with a cost crossover | 14 / 168 | 4 / 168 |
| Families with an application first-rank change | 6 | 4 |
| Families with a change after fixing nonprice scores and removing score rounding | 6 | 3 |

The two periods use different observation frequencies and sets of varying prices; their event counts are not comparable rates or probabilities. The six monthly cost-changing families are ammonia cracking, dry reforming, water-gas shift, CO2 electroreduction, hydrogen evolution, and electrochemical nitrogen reduction. The latter three require particular care over products, electrolytes, and cost boundaries.

- **Monthly:** the preserved paper inputs contain 14 synchronous metal-price series: Ag, Al, Au, Co, Cu, Ir, Mo, Ni, Pd, Pt, Rh, Ru, Sn, and Zn. All other prices, including supports and engineering anchors, remain at the May 2026 reference values.
- **Daily:** dated New York JM base prices for Pt, Pd, Rh, Ir, and Ru and Westmetall LME cash settlements for Al, Cu, Ni, Sn, and Zn. The full PGM download has 436 dates beginning in January 2025; the available base-metal tables begin in January 2026. The exact intersection contains 176 dates. **Ag, Au, Co, Mo and all other non-daily inputs remain at the May 2026 reference.** This is not a complete real-time market valuation of every component.
- Formulations, order sizes, manufacturing steps, route premiums, support prices, price-source annotations, and family-specific balanced weights are fixed. `feeds_wt_pct` records catalog inputs before any engine normalization; plotted costs are calculated by the engine. Thermal costs include the estimated selling price, overheads and margin, and route extras. The calculation uses the current 2026 engineering assumptions with historical metal prices, not historical manufacturing conditions.
- Each family uses one unit throughout: USD/cm2 for AEM and PEM OER, and USD/lb for the remaining 28 families. Powder mass is not an equivalent electrode-area or product-output basis. No cross-family cost ranking is performed. All four PEM area-cost series and three of four AEM area-cost series are constant in the monthly replay: their fixed electrode-library/default prices limit propagation of the varied metal feeds into this cost boundary. Their zero crossover counts therefore do not establish insensitivity of real electrode costs to metal markets.
- Baseline candidate ledgers and all 2,670 family-month ledgers were independently rerun through the current engine and matched the earlier frozen study exactly. The application database was not opened for writes; material records were seeded in an in-memory database.

**Rank definitions.** `Cost` uses strict minimum cost, with an absolute tie tolerance of 0.0002 USD/lb or 0.000002 USD/cm2. Transitions are bracketed by the last and next strict winning observations; ties are not invented observations. `App` uses the application score rounded to one decimal and its functional-unit cost tie-break. `Fixed` freezes May-reference evidence, route, and performance scores and computes economics and the weighted total without score rounding. Economics is still normalized over the same full candidate set at each date. A further diagnostic in the JSON freezes the cost normalization endpoints as well; it is unclipped and is not an application score. The >1% screen uses the lead over the second-cheapest candidate at both endpoint states. It is a descriptive margin, **not a model-uncertainty interval or proof of robustness**.

## Daily result and its limits

For photocatalytic water splitting, the fixed-nonprice score difference between Pt/TiO2 and TiO2 changes from +0.1418 on 19 January 2026 to −0.0274 on 20 January as Pt increases from 2,375 to 2,428 USD/troy oz. With the other 19 January prices fixed, including Rh at 10,100 USD/troy oz, the conditional Pt threshold is approximately **2,419 USD/troy oz**. The application totals tie at 82.0 on 20 January; a strict application reversal is present by 21 January (81.9 versus 82.0). The January episode reverses again on 30 January. Across the full daily window, the unrounded fixed-nonprice winner changes four times for this family and six times for preferential CO oxidation. The exact crossings depend on normalization and small score margins; they do not demonstrate a change in photocatalytic activity, hydrogen productivity, or industrial suitability. In particular, the Rh-containing fourth candidate influences the economics scale even when it never ranks first.

CO2 methanation has seven application first-rank changes but none after nonprice scores are frozen. Its price-evidence score is weighted by material-cost share, so this is a mediated score change rather than a lowest-cost crossover. Electrochemical nitrogen reduction has two daily lowest-cost changes, but the aqueous-Cu route's largest cost advantage over the plasma comparator is only 0.70%. There is no lowest-cost change between states with >1% leads. A plasma process, a lithium-mediated process, and an aqueous electrode proxy are not validated interchangeable catalysts on a common product-output basis; this is not a headline discovery of an optimal nitrogen-reduction catalyst.

The thermal candidates are screening archetypes, not equivalently tested industrial replacements. The Co/Mg–La support split is an authored approximation rather than the exact literature composition. High- and low-temperature WGS candidates serve different operating windows. Photocatalytic hydrogen-evolution examples also do not all establish the same overall-water-splitting function. Activity, selectivity, lifetime, regeneration, precursor procurement, and plant integration are not re-estimated here. The valuable result is a transparent, reproducible **price-triggered re-evaluation**, not an experimentally discovered catalyst.

## Figures and captions

**Figure R1. Cost crossovers.** [PNG](figures/fig_price_crossovers.png), [SVG](figures/fig_price_crossovers.svg), [PDF](figures/fig_price_crossovers.pdf). Modeled delivered catalyst costs under the 89 preserved monthly price states for (a) ammonia cracking, (b) methane dry reforming, and (c) water-gas shift. Only candidates that attain the lowest modeled cost during this window are shown; the complete candidate set was retained for all calculations and is plotted in the full atlas below. Lines connect observed price states and do not establish an exact within-month crossover date. (d) Conditional equal-cost boundary between the Co/Mg–La and Ni/alumina ammonia proxies, computed by direct engine recosting and bisection at 51 nickel prices. Regions identify the cheaper of these two candidates. Points are monthly Ni–Co price states; diamonds and the arrow identify September–October 2025. Other prices and all engineering assumptions remain at reference values. Costs are conditional model estimates, and the line is not a statistical confidence boundary.

**Figure R2. Daily rank changes.** [PNG](figures/fig_daily_rank_changes.png), [SVG](figures/fig_daily_rank_changes.svg), [PDF](figures/fig_daily_rank_changes.pdf). Pairwise score differences for (a) photocatalytic water-splitting candidates and (b) preferential CO oxidation, using the 176 common daily dates. Positive values favor the first candidate named above each panel. Solid lines fix nonprice scores and remove score rounding; dashed lines use the application totals. Zero is the equal-score boundary; shaded regions mark negative solid-line differences. All family candidates and balanced weights remain fixed. The cheapest candidate does not change in either family. Small score crossings are not evidence of equivalent reaction performance or robust industrial substitution.

**Figure R3. Crossover census.** [PNG](figures/fig_crossover_atlas.png), [SVG](figures/fig_crossover_atlas.svg), [PDF](figures/fig_crossover_atlas.pdf). Counts of first-place changes for all 30 families under the monthly and daily replays. Column definitions are `Cost`, `App`, and `Fixed` above. Zero is an observed null result for the specified replay, not missing data. The horizontal rule separates 23 thermal families from seven electrochemical families. The daily and monthly counts have different observation windows and price coverage.

**Complete cost atlas.** [All 30 families, 30-page PDF](figures/all_candidate_costs.pdf). Each page shows every candidate under monthly and daily price inputs, with unique catalog candidate identifiers. Both y axes use a log scale and the family-specific cost unit; identifiers and page order correspond to the JSON. These pages preserve expensive and nonwinning alternatives that would obscure the detailed R1 panels. `candidate_costs.csv` contains all 30,740 values and scores; `family_summary.csv` contains the census. The JSON additionally contains complete pairwise event brackets, ties, scores, controls, candidate identities, and source hashes. Korean figures have `.ko` suffixes.

## Sources, collection, and reproduction

Daily observations were downloaded on 13 September 2026 from the public [JM price page](https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management) and [Westmetall market data](https://www.westmetall.com/en/markdaten.php). The latest common observation is 11 September, not the retrieval date. The five PGM CSV columns were checked against that day's separate current quotations. No paid or authenticated API was used. The raw daily CSV, quotation series, and rejected exploratory responses remain in `_local/price-crossovers-2026-09-13/`; public access is not a grant of redistribution rights. The committed files contain derived model results and limited explanatory price points. Existing monthly inputs and their source records remain unchanged.

The default JM chart request returned monthly aggregates for the long requested interval even though the existing backend helper describes daily output. The new fetcher instead uses the site's explicit DAILY CSV and New York region control. A CSV request in reverse metal order produced mismatched headers; that response was rejected. The final request uses Pt, Pd, Rh, Ir, Ru order and rejects a mismatch against all five current quotes. Neither rejected response enters these results. This study does not change the production fetcher.

Run from the autonomous checkout, using a new output directory for each analysis freeze:

```powershell
python scripts/fetch_crossover_prices.py --start 2025-01-01 --end 2026-09-13 --out _local/new-daily-prices.json
python scripts/run_price_crossovers.py --daily _local/price-crossovers-2026-09-13/daily_prices_final.json --out-dir _local/new-replay
python -m scripts.analyze_price_crossover_cases --study _local/new-replay/price_crossovers.json --daily _local/price-crossovers-2026-09-13/daily_prices_final.json --out _local/new-replay/crossover_mechanisms.json
python scripts/draw_application_note_figures.py --crossovers _local/new-replay --out-dir _local/new-replay/figures
python scripts/draw_application_note_figures.py --lang ko --crossovers _local/new-replay --out-dir _local/new-replay/figures
python -m pytest backend/tests/test_price_crossovers.py -q
```

The first command is only for a new retrieval; replaying this freeze requires the original private snapshot and its recorded SHA-256. Retrieval metadata and source attribution are separate from the deliberately fixed evidence annotations used in the model. No catalyst literature or DOI was added or changed by this analysis.
