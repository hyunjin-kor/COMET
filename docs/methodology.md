# Methodology

CatTEA implements the catalyst cost estimation methodology from the CatCost framework (Baddour et al. 2018, Van Allsburg et al. 2022).

## Current Scope

CatTEA currently exposes four research-facing layers in the shipped product:

1. `materials and live price basis`
   Material rows can resolve against live feeds, indexed references, literature rows, or vendor rows.
2. `preparation-step costing`
   The Step Method remains the core plant-style processing estimate.
3. `electrocatalyst layer costing`
   Electrocatalyst workflows can add area-based catalyst, ionomer, membrane, and substrate costs.
4. `spent catalyst recovery proxy`
   Thermocatalyst workflows can optionally include end-of-life recovery value as a screening adjustment.

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

In the CatTEA UI this is exposed as an optional `recovery scenario` for thermocatalyst cases. It is intended for early screening only.

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
