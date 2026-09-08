# Methodology

COMET implements the catalyst cost estimation methodology from the CatCost framework (Baddour et al. 2018, Van Allsburg et al. 2022).

## Current Scope

The shipped product has four research-facing layers:

1. `materials and live price basis`
   Material rows can resolve against live feeds, indexed references, literature rows, or vendor rows.
2. `preparation-step costing`
   The Step Method remains the core plant-style processing estimate.
3. `electrocatalyst layer costing`
   Electrocatalyst workflows can add area-based catalyst, ionomer, membrane, and substrate costs.
4. `spent catalyst recovery proxy`
   Thermocatalyst workflows can optionally include end-of-life recovery value as a screening adjustment.

## Price basis

Two tiers, kept apart on purpose.

The live tier is what the desktop app shows. Direct Johnson Matthey base prices take priority for platinum and palladium, and Westmetall LME settlements for copper and aluminium. Yahoo futures remain their fallback and the first source for gold and silver. Every price carries its source, quote time and evidence tier.

The selector tries the following fallbacks in order. An asterisk marks an optional configured API key. Yahoo-only polling preserves a stored primary JM/Westmetall quote; a full refresh can choose the fallback when the primary is unavailable. Both in-page polling intervals are five minutes (Yahoo increased from one minute); reference history is collected at most daily.

| Metals | Live source order |
|---|---|
| Pt, Pd | Johnson Matthey → Yahoo → Metals.Dev* → Kitco → MetalpriceAPI* → CatCost anchor |
| Cu, Al | Westmetall → Yahoo → Metals.Dev* → CatCost anchor |
| Au, Ag | Yahoo → Metals.Dev* → Kitco → MetalpriceAPI* → CatCost anchor |
| Rh | Kitco → Metals.Dev* → Johnson Matthey → CatCost anchor |
| Ru, Ir | Johnson Matthey → Metals.Dev* → CatCost anchor |
| Ni | Metals.Dev* → Markets Insider → Westmetall → CatCost anchor |
| Zn, Sn | Westmetall → USGS anchor |
| Co, Mo, W | Metals.Dev* → USGS anchor |
| V, Re | USGS anchor |
| Fe | CatCost anchor |

The [source-priority audit](audit/t09-t10-notes.md) records actual public-feed responses and offline fallback tests. Missing sources retain the documented anchor; no additional rate is inferred.

COMET uses library prices for supports on the live basis (USGS annual averages, public trade unit values and supplier quotes, escalated with ChemPPI). On the reference basis, eleven support definitions (calcined and alpha alumina, titania, silica, activated carbon, carbon black, synthetic zeolites, magnesia, cerium compounds, manganese dioxide, chromium oxide) can take monthly U.S. import unit values for the HS codes in `backend/data/support_series.json`. Verified observations shipped in `backend/data/support_price_history.json` are loaded offline at startup, without an API key; definitions with no observation retain their library prices. A unit value is customs value over net weight with every grade and partner combined, so it is a bulk market level, not a catalyst-grade quote; the evidence tier says so.

The free public preview permits one period per request. `scripts/fetch_support_history.py --start 2026-04 --end 2026-07 --out support_history.json` requests at most twelve completed months per definition, uses no credentials, spaces requests by twelve seconds and stops on HTTP429. It retains every request outcome and rejects mismatched filters, duplicate/truncated rows, non-finite values, missing weights and estimated weights. A zero-row response means no published observation, never a zero price. The September6 acquisition accepted three alumina months (April–June), found no July row and stopped at the provider's rate limit. The September7 (Korea time) resumption queried June once for each definition: nine passed, including the unchanged alumina observation, while alpha alumina had estimated weight and carbon black lacked net weight. That earlier snapshot contains nine series and eleven observations and remains frozen. The subsequent free April/May extension accepted nineteen of twenty-two responses and added seventeen unique observations after deduplication. The shipped history now contains ten series and twenty-eight observations. April silica and April/May carbon black failed weight-quality checks. Existing grade limitations and material links are unchanged; artificial corundum and cerium compounds remain unlinked market indicators. See [the extension audit](sources/comtrade-history-extension-2026-09-07.md) and [the earlier responses and policy check](sources/free-comtrade-evidence-2026-09-07.md).

To include a validated support snapshot in the paper, add `--support-history backend/data/support_price_history.json` to `scripts/reproduce_paper.py`. The latest common month includes support publication dates: the combined shipped inputs select May 2026 because artificial corundum lacks a valid June observation. Later requested months fail explicitly. The manifest preserves both raw input hashes. The unified submission run uses May; the original July metal-only run and earlier June support runs are preserved. Short support series are held at the selected May baseline in the long metal-history replay and identified as incomplete series. They are not interpolated through missing years. The app independently displays the latest accepted quote per series; those dates can differ from the paper's common cutoff.

The reference tier is the academic basis. The sidebar switch moves the whole app between the two: on the academic basis the price screen, the calculator and the benchmark rankings all price from the latest published month. The paper analysis prices from the same tier. Monthly averages from the IMF Primary Commodity Price System (aluminium, copper, nickel, zinc, tin, cobalt, molybdenum, gold, silver) and Johnson Matthey base prices averaged by month (platinum, palladium, rhodium, ruthenium, iridium), cut at the latest month both publish. Tungsten, rhenium, vanadium and iron have no published series and keep their USGS or CatCost anchors. `scripts/fetch_price_history.py` freezes the series, `scripts/build_reference_basis.py` turns one month into a price map, and the analysis scripts take that map through `--price-basis`. Every number in the paper then re-costs from a committed file rather than from whatever the app fetched that day.

## Step Method (Chapter 6)

### Reproducing the paper

From the repository root, with the project's Python packages and Matplotlib available:

```bash
python scripts/reproduce_paper.py --price-basis reference --month 2026-07 --seed 20260906
```

Omit `--month` to choose the latest common completed publication month. The command collects institutional history, freezes the reference basis, evaluates the library, replays price states, sweeps break-even prices and draws six figures. It records input SHA-256 hashes, exact commands, the Python/package environment and source failures in `reproduction_manifest_<date>.json` inside the selected output directory. The deterministic analyses enumerate states; the seed controls the execution environment and is retained for reproducibility. The uncertainty API separately accepts an optional `seed`; omitting it requests independent samples. Both reproduction runners require a new or empty output directory and stop before writing if evidence already exists. Paper output defaults to `_local/paper-<date>`. The manifest hashes the raw supplied live snapshot as well as metal/support history, backend and script sources; a source change during execution marks the run failed.

To repeat the unified May submission evidence without collecting new quotes or overwriting the committed run:

```bash
python scripts/reproduce_paper.py --price-basis reference --month 2026-05 --seed 20260906 --date 2026-09-07 --history docs/paper/submission-2026-09-07/price_history_2026-09-07.json --live-basis docs/paper/submission-2026-09-07/live_basis_2026-09-07.json --support-history docs/paper/submission-2026-09-07/support_history_2026-09-07.json --out-dir _local/submission-replay-2026-09-07
python scripts/build_submission_manuscript.py --directory docs/paper/submission-2026-09-07 --check
```

The builder checks the committed [manuscript](paper/manuscript_2026-09-07.md) and [SI](paper/si_2026-09-07.md) against frozen output hashes and JSON keys. The source-checked ACS format, word-equivalent estimate and TOC graphic are documented in [the formatting audit](paper/submission-format-2026-09-07.md). Actual authorship and final submission remain human decisions.

The [external-cost screen](audit/external-cost-validation-2026-09-07.md) records ten public cases, including one contract schedule and three verified retail pack offers. None matches formulation, production scale, date and cost boundary sufficiently for a full-cost residual. Empirical MAPE remains unestimated. The [four-family literature audit](sources/free-benchmark-expansion-2026-09-07.md) corrects attribution for fifteen candidates without changing compositions, scores, prices or process steps; same-price analysis is byte-identical.

If collection fails, the pipeline preserves the existing archived input and records that fallback. Historical daily observations in an older archive are converted only into a separately labelled monthly derivative; they are never described as IMF observations. Support prices remain library values when no Comtrade quote exists. The published-month freshness check compares monthly metal rows with the latest stored publication month; annual anchors keep their evidence score without a false daily-age warning. Only live-source review uses a seven-day age limit. The more detailed source-specific age status remains visible in the inspector.

The Step Method estimates catalyst selling price by summing:

1. **Materials Cost** - Raw material prices (metals, supports, solvents)
2. **Processing Cost** - Hourly equipment costs for each manufacturing step
3. **G&A Overhead** - General & Administrative (default 5%)
4. **SARD** - Sales, Admin, R&D (default 5%)
5. **Selling Margin** - Scale-dependent margin (Figure 6.3 correlation)

### Scale Classification

| Scale | Order Size | Production Rate |
|-------|-----------|----------------|
| Small | 1-5 tons | 1 ton/day |
| Medium | 5-70 tons | 10 tons/day |
| Large | 70-1000 tons | 150 tons/day |

### Selling Margin Correlation

```
margin% = 39.192 * Q^(-0.23360)
```

where Q is order size in tons.

### Campaign length

CatCost's term for one production run. In the app this appears as the production scale (order size in tons, which sets the Small, Medium or Large equipment basis) and the production time in days. Campaign days = order size ÷ production rate + cleaning time (0.5 d Small, 1 d Medium/Large). The nominal rates are 1 / 10 / 150 t/d. `calculate_step_method` accepts `production_rate_ton_per_day` to override the nominal rate for routes whose effective throughput is lower — CatCost Table 6.2 footnote b applies 67 t/d to the zeolite FCC campaign for ramp-up and ramp-down.

### Reproduction of CatCost Table 6.2

`scripts/reproduce_catcost_table62.py` feeds the published Table 6.2 inputs (mid-2017 basis) through the Step Method and prints each intermediate next to the table's value. Hourly step cost, campaign length, processing cost, subtotal, G&A and SARD match to the cent on all three cases; Pt/C reproduces the published $27.37/lb exactly. Two residuals remain and both trace to the table rather than the implementation:

| Case | COMET | Table 6.2 | Residual | Cause |
|------|------:|----------:|---------:|-------|
| 2 wt% Pt/C, 2 t | $27.37 | $27.37 | 0.00% | — |
| 21 wt% Ni/Al₂O₃, 20 t | $19.22 | $20.59 | −6.65% | Footnote f applies 33% of pre-margin; the Figure 6.3 correlation gives 24% at 20 t |
| USY-FCC, 200 t, 67 t/d | $2.44 | $2.41 | +1.16% | Footnote b effective rate; nominal 150 t/d would land 33% low |

### Preparation methods

The calculator's Preparation Method step offers 28 named thermal methods on top of the unit operations: impregnation (incipient wetness and excess solution), co-precipitation, deposition-precipitation, sol-gel, hydrothermal synthesis, ion exchange, oxide-melt fusion, solid-state and mechanochemical synthesis, colloidal nanoparticle deposition, solution combustion, zeolite and FCC routes, shaping into extrudates and pellets, washcoating on monoliths, sulfidation and gas-phase reduction. The catalog also contains one empty custom route and five electrode routes. Each `process_templates/*.json` file maps its method to Step Library operations. Modern entries carry source links; some legacy entries have only a source label and no public permalink. The method cards show the processing cost of the route alone at the current production scale, from `GET /api/templates/costs`. The [catalog audit](audit/manufacturing-catalog-2026-09-06.md) records every thermal route's steps, source fields, uncosted operations and processing costs at 2, 20 and 200 tons. Selecting a card preserves its ID and repeated operations, including when its equipment is refitted to another scale. The [electrode default rules](audit/electrode-defaults-2026-09-06.md) document material selection by application and template.

Two rules keep those costs honest. Steps are fitted to the production scale before pricing: Table 6.1 lists batch equipment at Small only and continuous equipment at Medium and Large only, so a batch kiln stands in for the continuous kiln at 2 tons and the reverse at 20 and 200 tons (`SCALE_EQUIVALENTS` in `backend/core/step_method.py`). And an operation the Step Library has no rate for (a pressure autoclave, a fusion furnace, a washcoat coating line, a hydrogen reduction furnace, gas-phase sulfiding) is either costed at the nearest listed rate and named as such, or left out and listed under `uncosted_operations`; the card shows a "partly costed" flag either way. No hourly rate is invented for them.

## CapEx/OpEx Factors Method (Chapter 7)

For detailed capital and operating cost estimation using factored approaches.

### Capital Cost Factors (Peters & Timmerhaus)

Equipment cost scaling uses the six-tenths rule:

```
Cost_target = Cost_base * (Size_target / Size_base)^0.6
```

## Price Escalation

Costs are adjusted between years using:

- **ChemPPI** - Chemical Producer Price Index (operating costs)
- **CEPCI** - Chemical Engineering Plant Cost Index (capital costs)

## Spent Catalyst Recovery (Chapter 9)

Net reclaimed value accounts for:

- Metal losses during use (varies by support and reactor type)
- Metal losses during refining
- Recovery processing costs (thermal oxidation, incoming inspection, refining charges)

In the COMET UI this is exposed as an optional `recovery scenario` for thermocatalyst cases. It is intended for early screening only.

## Life Cycle Assessment

The LCA block reports GWP (kg CO₂-eq) and CED (MJ) per kg of finished catalyst as two terms with separate provenance, and states its `system_boundary` in every result.

**Materials term** — wt%-weighted sum of per-element cradle-to-gate factors from Nuss & Eckelman (2014, PLOS ONE, CC BY). Oxide supports map to their dominant element; supports without a verified factor (silica, carbons, zeolites) are reported as `data_gap_pct`, never estimated.

**Process term** — added when the Step Method route is known. Each step is converted to fuel or electricity per kg of catalyst and then to impact with public factors (`backend/data/process_energy_factors.json`):

- Calcination: sensible heat of the dry solid from ambient to the kiln temperature (default 500 °C, cp 0.95 kJ/kg·K), divided by a 0.40 kiln thermal efficiency, as natural gas.
- Drying: latent plus sensible heat of the water load (0.7 kg/kg for impregnated supports, 1.7 kg/kg for spray-dried slurries), divided by a 0.55 dryer efficiency, as natural gas.
- Mechanical steps (mixing, milling, filtration, extrusion): order-of-magnitude specific energies from Perry's, as grid electricity.
- Emission factors: EPA GHG Emission Factors Hub (Jan 2025) — natural gas 53.06 kg CO₂/mmBtu, US-average grid 771.5 lb CO₂/MWh (eGRID2023), AR5 GWP100.
- Electrocatalyst coating-line steps are area-based and listed as `unmodeled_steps` rather than estimated.

Not in the boundary: precursor decomposition enthalpy, NOx and flare process emissions, solvent and water supply, wastewater, and equipment embodied impacts. Each occurrence of a step in a route is counted in full.

For a 21 wt% Ni/Al₂O₃ impregnation route the process term is 0.24 kg CO₂-eq/kg against 7.84 for materials (3%). Across the 54 benchmark candidates with at least 50% materials coverage the route share is 2.4% (median), 5.5% (p90) and 15.2% (max), consistent with the CatCost paper's observation that raw materials dominate catalyst manufacturing GHG (`docs/paper/results_2026-09-02.md`). The two terms are kept separate in the output so that finding can be checked per candidate rather than assumed. Lab-scale catalyst LCIs in the literature (muffle furnaces, kWh per gram) were not used as inputs because they overstate industrial energy intensity by orders of magnitude.

## Error budget and screening limits

These contributions are reported separately. COMET does not combine them into a validated total error bar: several are correlated, and missing process/impact models cannot be represented by a small symmetric uncertainty band.

| Contribution | Quantitative basis and effect | Evidence / interpretation |
|---|---|---|
| Metal and support prices | Structured Monte Carlo defaults use active-component factors 0.70–1.30, promoter/support 0.80–1.20, electrode-adjunct 0.85–1.15 and order-size 0.80–1.20. All are uniform scenario bounds, not fitted confidence intervals. | `backend/core/uncertainty.py`; observed monthly ranges and ranking transitions are in `docs/paper/monthly_history_2026-09-06.json` and `price_volatility_2026-09-06.json`. Comtrade unit values mix grades and partners; no support series means the fixed library price remains. |
| Inflation indices | The operating-rate basis starts in 2017; escalation is exactly target-index / base-index. Unsupported years raise an error. Selecting a newer target year is not proof that a final annual index has been published. | `backend/data/chemppi.json`, `backend/data/cepci.json`, `backend/core/price_escalation.py`. The reproduction manifest hashes the exact indices used. |
| Scale and effective throughput | Nominal Small/Medium/Large rates are 1/10/150 tons/day; the FCC acceptance case uses 67 tons/day. Nominal FCC gives 1.6090 USD/lb versus 2.4380 at the effective rate, showing that throughput assumptions can dominate the residual. | `docs/audit/baseline-table62.txt`, `docs/paper/table62_reproduction_2026-09-06.json`; the 28-method, three-scale audit records every equipment substitution and rate. |
| Recovery value | The recovered-metal multiplier is (1 − use loss) × (1 − refining loss). For missing support/metal mappings, existing defaults are 5% metal-use loss, 2% support loss and 10% refining loss; these are screening assumptions, not measured recovery guarantees. | `backend/core/spent_catalyst.py`, `backend/core/constants.py`, `backend/data/spent_catalyst.json`. Iron uses a scrap basis; recovery is optional and is excluded from electrode assembly output. |
| Materials LCA coverage | Coverage is reported by matched mass, with unmatched mass retained as a gap. The library has 47 candidates below 50% materials coverage; the route-share analysis includes only the eligible 54 candidates. | `docs/paper/paper_summary_2026-09-06.json:lca` and `all_families_2026-09-06.json`. No new carbon, silica or zeolite factors were supplied. Low coverage cannot support an overall environmental ranking. |
| Uncosted operations and process energy | There is no new price for autoclaves, reduction furnaces, centrifugation, sieving, coaters, freeze-drying, CVD or ALD. Per-route omissions and modelled rates remain explicit. Electrode coating steps have no inferred process-energy model. | `docs/audit/manufacturing-catalog-2026-09-06.md`, `docs/paper/manufacturing_costs_2026-09-06.json`, `backend/data/process_energy_factors.json`; omitted rates make route prices partial screening estimates, not complete quotations. |

The Table 6.2 residuals test reproduction of the published method. They do not bound the error of a new catalyst's source prices, throughput, chemistry or omitted operations. The 7% Ni and 2% FCC acceptance tolerances are software regression limits, not predictive accuracy claims.

## Research Extensions Already Implemented

- Distinct `Thermocatalyst` and `Electrocatalyst` workflows
- Source-linked material normalization in the result screen
- Monte Carlo uncertainty analysis
- ChemPPI / CEPCI escalation
- Electrode stack costing for PEMFC / electrolyzer style workflows

## Research Extensions Not Yet Implemented

The repository does **not** currently claim the following as complete:

- chemical structure editor integration such as Ketcher or JSME
- RDKit or ChemPy-backed structure / stoichiometry validation
- SCScore-style synthesis complexity penalties
- explicit catalyst deactivation kinetics
- regeneration-cycle and reuse loop economics

Those are valid next-stage research features, but they remain roadmap items until the engine and tests support them directly.

## Practical costing inputs and saved-case comparisons

These optional inputs retain the existing calculation when omitted. They do not
add literature prices, infer missing equipment rates, or establish empirical
accuracy. The implementation is in `backend/schemas/recipe_input.py`,
`backend/core/recipe_costing.py`, `backend/core/costing_scope.py`,
`backend/routers/estimate_comparison.py` and `backend/core/cost_evidence.py`.

### Manufacturing boundary and effective production rate

Each result preserves `costing_scope`: the charged operations, their published or
proxy status, scale substitutions, dropped and omitted steps, and declared
uncosted operations. `modeled_steps` means that the selected Step Method operations
have prices; it does not assert complete plant coverage. `proxy` identifies proxy
rates or equipment substitutions, and `partial` identifies omissions. These fields
travel with saved results and exports. For electrode assemblies, the powder-route
Step Method cost is a separate mass-based calculation and is not added to the
electrode-area total.

Thermal requests can supply `production_rate_ton_per_day` with a required
`production_rate_note`. The rate is finished-catalyst **short tons per day**. The
campaign duration is order quantity divided by the effective rate, plus the
existing scale-dependent cleaning allowance. Omitting the override uses the
existing scale rate. This does not provide a new equipment-capacity model or
change the existing hourly rates. Electrode requests reject this mass-based
override.

The displayed recovery-adjusted price is the selling price **including selling
margin**, less the optional recovery value, floored at zero. It is not a
manufacturing cost before margin.

### Purchased precursor and auxiliary consumption

For a thermal component, an optional `recipe_consumption` replaces its material
cost contribution with a purchase-based mass balance. Let `w` be its normalized
mass fraction in the finished catalyst, `f` the retained component fraction of
the pure precursor, `p` precursor purity, `y` retained-component yield and `P`
the purchased precursor price in USD/kg:

```text
purchased precursor kg / finished catalyst kg = w / (f × p × y)
precursor cost USD / finished catalyst kg = w × P / (f × p × y)
```

All fractions must be supplied in `(0, 1]`, with a precursor name and source or
assumption note. COMET does not derive a chemical formula, precursor content,
purity or yield. `f` describes the pure compound; `p` describes the purchased
material's purity, so the same impurity must not be counted in both. A recipe
cannot also use a precursor markup other than one. Components without a recipe
retain their existing weight-fraction, unit-price and markup calculation.

The original component `price_per_lb` remains a retained-material reference price
and, when applicable, the existing recovery-screening price. It is not added a
second time to recipe material cost. Each `consumables` entry adds net purchased
kg per kg of finished catalyst multiplied by its explicit USD/kg price. Solvent
recycling, wash-water recovery and waste disposal are not inferred; the stated
consumption and its note must explain any netting already performed.

Recipe and auxiliary inputs change material cost only. The existing LCA still
uses finished composition and its existing process-energy assumptions; it does
not acquire precursor-specific, solvent, wastewater or yield-loss inventories.
The result therefore flags the boundary difference rather than presenting the
new recipe as a complete life-cycle inventory.

### Comparing saved formulations under common conditions

`POST /api/estimates/compare` compares two to four saved complete requests within
one catalyst domain and resolved application family. The user chooses the price
basis, common order quantity and a reference estimate. The reference supplies the
target and base years, G&A/SARD, recovery assumptions and effective production
rate. Electrode comparisons also share its area, loading, ionomer-to-catalyst
ratio and manufacturing scenario. Full component lists, precursor yields and
consumption amounts, and manufacturing routes remain individual.

The response separates the saved historical result, a recalculation using shared
prices at each original operating condition, and a recalculation using both shared
prices and common conditions. The historical-to-repriced difference can include a
model-version change; it is not automatically a pure market-price effect.
Differences between formulations, yields and routes are not attributed solely to
the manufacturing method. Thermal headline values are selling price less recovery
per mass; electrode values are assembly cost per area.

Library identities are matched by material key. Manual identities require the
same normalized name and stated grade; unknown grades are not merged with known
ones. For conflicting matched prices, the explicit reference wins; materials
absent there use the lowest selected estimate ID. Precursor and auxiliary prices
are matched separately by their names, which must distinguish grades. Manual
ionomer concentration, density and pricing form are also kept distinct. Different
library identities or grades with the same chemical name remain separate and
produce a warning. Every harmonized price records its source estimate and the
prices it replaced. Common-scale equipment substitutions and unavailable steps
are disclosed. Original saved inputs, outputs and purchase evidence remain intact.

### Local purchase and actual-cost evidence

`purchase_evidence` records supplier, quote date, quantity and unit, grade, price
boundary, reference and notes for a manually entered component price. These are
local user-supplied records; COMET does not verify a supplier or convert a quotation
into an independently observed cost.

Actual observations attach to a saved estimate without replacing its calculation.
The initial error assessment supports mass-based thermal catalysts only. It
requires user-confirmed invoice, production-record or literature evidence; USD;
a matching price month and observation date; matching normalized composition and
known grades; production quantity and effective rate; template and repeated
manufacturing steps; and documented cost inclusions and production conditions.
The selected cost boundary distinguishes pre-margin manufacturing cost, selling
price and selling price after recovery. Incomplete costing scopes, unobserved
recipe/auxiliary consumption, missing fields, supplier quotes and electrode
observations remain stored but do not contribute an error value.

Eligible observations report signed percentage error and absolute percentage
error. The displayed MAPE averages only eligible observations for that saved
estimate and is `null` when none qualify. It is a local comparison of
user-confirmed evidence, not independent empirical validation of COMET.

## Monte Carlo outcome and input boundaries

The structured uncertainty API repeats the current calculator case. For a thermal case it reports selling price in $/lb, or selling price less recovery credit when that option is selected. For an electrode assembly it reports the assembly cost in $/cm², including catalyst powder and selected adjuncts. Changing kg/lb display units does not convert area costs. Area, loading and any declared electrode manufacturing scenario stay fixed; only powder and adjunct prices vary. Bulk order-size bounds do not apply to this area model. The legacy flat API remains a bulk selling-price model.

When a sampled thermal order crosses a Small/Medium/Large boundary, the declared operations use the same documented scale substitutions as the point estimate. A sample that would lose a required operation is counted as failed instead of silently calculating a cheaper route. Responses and exports retain the number and reasons for failed runs; percentiles describe successful runs only. These are uniform scenario intervals, not validated confidence intervals. An explicit empty uncertainty map fixes all factors at one, whereas an omitted map uses the documented defaults.

All numeric request values must be finite. The published selling-margin correlation is unchanged; an order for which it predicts a margin of 100% or more is rejected because a positive finite selling price cannot be calculated from that expression. COMET does not invent a small-batch extrapolation or clamp the margin. Omitted template steps resolve to that template at the requested scale, and saved inputs preserve the operations actually calculated. See the [prepublication audit](audit/prepublication-run-2026-09-08.md) for regression cases and unchanged Table 6.2/paper results.


## Joint decision robustness (2026-09-08)

Run `python scripts/run_decision_robustness.py --out-dir _local/robustness-replay-new --seed 20260906`. This offline runner reads the preserved May 2026 reference and normalized monthly history, uses an isolated in-memory database, and writes numerical ledgers, candidate CSV, PNG/SVG and a hash/environment manifest. Existing output directories must be empty.

The full synchronous metal-price history is crossed with nonnegative four-criterion weight simplices at increments 0.1 and 0.05. Source annotations, support unit values, anchors, routes and author rubrics are held at the reference state; evidence cost shares are recomputed. It is a retrospective numeric-price counterfactual, not a forecast using only information available at each historical date. Equal counts define finite-grid frequencies, not a future probability model. The complete data and measured grid-resolution difference are in the [study package](paper/robustness-2026-09-08/README.md).

Ranking uses the application's one-decimal composite score, then lower cost in the priced functional unit, then candidate slug. Complete electrode families use area cost. CO2 electroreduction, glycerol electrooxidation, HER and NRR include candidates lacking assembly inputs, so their existing powder-cost comparison is now explicitly displayed for every candidate. No assembly inputs are invented. Individual electrode ledgers remain available but are not mixed with mass cost in a family score.

Deleting each nonwinner tests min–max economics normalization against a fixed-normalization control. Route/performance scores are also stressed within clipped ±2, ±5 and ±10 point boxes; nonnegative additive weights permit an exact adverse corner for the baseline winner. Neither diagnostic calibrates subjective rubrics. Regret is a rounded composite-score gap. The [claim map](paper/research-claims-2026-09-08.ko.md) identifies supported statements and external evidence still needed; the [source check](sources/robustness-methods-2026-09-08.md) records the OECD/JRC methodological reference.
