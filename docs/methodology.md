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

The live tier is what the desktop app shows. Yahoo Finance futures for gold, silver, platinum, palladium, copper and aluminium, Johnson Matthey daily base prices for the platinum-group metals, Westmetall's LME settlements for nickel, zinc and tin, and USGS annual averages where nothing trades. Every price carries its source, quote time and evidence tier.

The reference tier is the academic basis. The sidebar switch moves the whole app between the two: on the academic basis the price screen, the calculator and the benchmark rankings all price from the latest published month. The paper analysis prices from the same tier. Monthly averages from the IMF Primary Commodity Price System (aluminium, copper, nickel, zinc, tin, cobalt, molybdenum, gold, silver) and Johnson Matthey base prices averaged by month (platinum, palladium, rhodium, ruthenium, iridium), cut at the latest month both publish. Tungsten, rhenium, vanadium and iron have no published series and keep their USGS or CatCost anchors. `scripts/fetch_price_history.py` freezes the series, `scripts/build_reference_basis.py` turns one month into a price map, and the analysis scripts take that map through `--price-basis`. Every number in the paper then re-costs from a committed file rather than from whatever the app fetched that day.

## Step Method (Chapter 6)

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

Campaign days = order size ÷ production rate + cleaning time (0.5 d Small, 1 d Medium/Large). The nominal rates are 1 / 10 / 150 t/d. `calculate_step_method` accepts `production_rate_ton_per_day` to override the nominal rate for routes whose effective throughput is lower — CatCost Table 6.2 footnote b applies 67 t/d to the zeolite FCC campaign for ramp-up and ramp-down.

### Reproduction of CatCost Table 6.2

`scripts/reproduce_catcost_table62.py` feeds the published Table 6.2 inputs (mid-2017 basis) through the Step Method and prints each intermediate next to the table's value. Hourly step cost, campaign length, processing cost, subtotal, G&A and SARD match to the cent on all three cases; Pt/C reproduces the published $27.37/lb exactly. Two residuals remain and both trace to the table rather than the implementation:

| Case | COMET | Table 6.2 | Residual | Cause |
|------|------:|----------:|---------:|-------|
| 2 wt% Pt/C, 2 t | $27.37 | $27.37 | 0.00% | — |
| 21 wt% Ni/Al₂O₃, 20 t | $19.22 | $20.59 | −6.65% | Footnote f applies 33% of pre-margin; the Figure 6.3 correlation gives 24% at 20 t |
| USY-FCC, 200 t, 67 t/d | $2.44 | $2.41 | +1.16% | Footnote b effective rate; nominal 150 t/d would land 33% low |

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
