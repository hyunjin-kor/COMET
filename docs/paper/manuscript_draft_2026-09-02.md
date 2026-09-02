# Manuscript draft — 2026-09-02

**Status: draft skeleton.** Every number below traces to `results_2026-09-02.md`
and the three frozen JSON files beside it. Nothing here is an estimate written
to fill a gap; where a number is not yet available the text says so.

**Not yet settled** (needs 노인수 교수님):
author list and order, affiliations, funding acknowledgement, target journal.
Written for **ACS Sustainable Chemistry & Engineering** because BioSTEAM
(2020, 8, 3302) and BioSTEAM-LCA (2020, 8, 18903) both landed there, so the
reviewer pool already knows this genre. Green Chemistry is the stretch target.

**Still missing:** reference list, figures, SI. Figure slots are marked inline.

---

## Title

*Working:* Route-resolved cost and cradle-to-gate impact for catalyst
screening, and when the recommendation depends on the metal price

The title has to carry the finding, not the tool. BioSTEAM-LCA's does
("... under Uncertainty") and that is the half reviewers remember.

## Abstract

Catalyst screening studies report a preferred formulation, but the cost that
justifies the preference is computed at whatever metal prices held when the
work was done, and the environmental term is usually drawn around a different
system boundary than the cost term. We present COMET, which estimates catalyst
manufacturing cost from a decomposed synthesis route and computes the
cradle-to-gate impact of that same route, so the two halves share one boundary.
The Step Method implementation reproduces the three published CatCost Table 6.2
cases from their published inputs, with no input tuned to the target, to 0.00%,
−6.65% and +1.16%. Applied to 116 candidate formulations across 30 reaction
families, route energy contributes a median 2.4% of cradle-to-gate GWP
(p90 5.5%, maximum 15.2%), confirming across a library what has been reported
for single cases: raw materials dominate. We then re-rank every family at 61
monthly metal-price states spanning 2021–2026. The recommended catalyst changes
in 4 of 30 families, in sustained runs rather than isolated months, and always
under the same condition — the candidates depend on different metals whose
prices decouple. In photocatalytic water splitting, where the two candidates
are the same oxide and differ only by a 1 wt% Pt co-catalyst, the Pt-loaded
candidate was the recommendation for 19 consecutive months. A screening result
of this kind is not portable without the price basis that produced it.

> *Check before submission:* the 2.4% / 4-of-30 / 19-month figures are the three
> load-bearing numbers. Each must survive a regeneration run.

## 1. Introduction

**The gap, stated as a number.** [TODO: the equivalent of BioSTEAM-LCA's
"<1 to >100 g-CO₂eq·MJ⁻¹" opener. We do not yet have a literature spread for
catalyst manufacturing cost estimates of the same formulation. This is the one
piece of the argument that is missing and it is the first thing to go and find:
a handful of published cost estimates for, say, Ni/Al₂O₃ or Pt/C, showing how
far apart they sit. Without it the introduction has no wound to point at.]

What we can state now:

- Early-stage catalyst evaluation needs cost and environmental impact together,
  because a formulation that is cheap and carbon-intensive and one that is the
  reverse cannot be ranked on either axis alone.
- CatCost (Van Allsburg et al., *Nat. Catal.* 2022) established route-decomposed
  catalyst cost estimation and is the reference this work builds on. It is a
  free tool, widely used, and its Step Method is the costing basis here.
- Tools that couple process cost and life-cycle impact in one model exist for
  biorefineries — BioSTEAM-LCA is the clearest — but catalyst *manufacturing*
  has not had the equivalent, and the two halves are typically computed on
  separate platforms with separate boundaries.
- Metal prices enter every catalyst cost estimate as a point value. No screening
  study we are aware of reports how its ranking behaves across the range those
  prices actually took.

**What is left after the existing work.** Following BioSTEAM-LCA's own framing:
naming the prior art and then saying precisely what remains. Two things remain
for catalyst manufacturing. (i) A cost model and an impact model drawn around
the *same* decomposed route, so a change to the synthesis shows up in both.
(ii) A way to ask whether a screening recommendation survives the price basis
it was computed on.

**Objective.** To introduce COMET, a desktop implementation of route-resolved
catalyst cost and cradle-to-gate impact with a live metal-price basis, and to
use it to characterise how far catalyst screening rankings depend on that basis.

## 2. Methods

### 2.1 Cost

Step Method costing over a decomposed synthesis route, following the CatCost
methodology. Materials cost is computed per component from a priced library;
processing cost is accumulated per route step with campaign length, G&A and
SARD applied as in the published method.

Price basis at the run reported here: 18 metal symbols resolved from the local
price table. Across the 116 candidates, component pricing splits 88 live-feed,
20 indexed, 143 fixed public quotes.

### 2.2 Cradle-to-gate impact

Two terms, reported separately and summed:

- **Materials** — wt%-weighted per-element cradle-to-gate factors from Nuss &
  Eckelman (2014).
- **Process** — fuel and electricity of the same Step Method route.

The coupling is the point: `compute_catalyst_lca()` receives the identical
`steps` list that drives the cost calculation, so a route change moves both
numbers. Components without a verified factor contribute to a reported
`data_gap_pct` rather than being silently zeroed, and route steps with no
energy model are listed rather than assumed free.

### 2.3 Validation

The three CatCost User Guide Table 6.2 cases, reproduced from the *published*
inputs — per-case materials cost, the exact step list with multiplicities,
order size. No input is fitted to the published total, and every intermediate
the table prints is compared, so a residual can be attributed.

> This replaces an earlier internal check that was circular: it supplied
> materials costs chosen to land on the published totals and then confirmed a
> ±20% match. That check could not fail and is not reported.

### 2.4 Price-state replay

One price state per period, taking each symbol's last observation in that
period. Real date slices, not independent per-metal percentiles, so
co-movement between metals is preserved and every state is a set of prices
that occurred together. A symbol not covering the whole window holds a
constant value rather than being spliced in partway, which would enter the
series as a step change.

Only live market feeds are replayed. Seeded reference values, CatCost
escalation and USGS annual averages are point estimates, not observations;
2,169 such rows were excluded. This matters to the result: including them
makes 7 of 30 families appear to flip, and six of those are artefacts of the
seeded first day, which alone reads as Au 2000 → 4404 and Pt 950 → 1891
overnight. A further 25 rows were dropped as outliers — aluminium quoted per
metric ton, and a rhodium parse failure pinned at 1001.0.

## 3. Results and discussion

### 3.1 The Step Method reproduces CatCost Table 6.2

| Case | COMET | Table 6.2 | Residual |
|------|------:|----------:|---------:|
| 2 wt% Pt/C, 2 t | $27.37 | $27.37 | 0.00% |
| 21 wt% Ni/Al₂O₃, 20 t | $19.22 | $20.59 | −6.65% |
| USY-FCC, 200 t @ 67 t/d | $2.44 | $2.41 | +1.16% |

Hourly step cost, campaign length, processing cost, subtotal, G&A and SARD
match to the cent on all three. The Ni/Al₂O₃ residual is attributable: the
table's footnote f applies 33% of pre-margin where the Fig. 6.3 correlation
gives 24%.

### 3.2 Materials dominate cradle-to-gate GWP, across a library

Among the 54 candidates with ≥50% materials coverage and a modelled route,
the route-energy share of GWP has median 2.4%, p90 5.5% and maximum 15.2%
(Fe-Cr HTS, precipitation plus pelletising). No candidate exceeds 20%.

This is the single-case observation in the CatCost paper, now shown across 54
catalysts. The route term matters most for cheap iron and copper precipitation
catalysts, precisely because their materials term is small
(1.3–3.9 kg CO₂-eq·kg⁻¹).

*[Figure 1: route-energy share against materials GWP, 54 candidates.]*

### 3.3 Rankings are sensitive to weighting before they are sensitive to price

Scores are linear in the four MCDA weights, so one evaluation per family gives
the ranking at every point of a 286-point simplex grid. The balanced-profile
winner holds rank 1 on a median 58.0% of the grid (min 20.6%, max 92.7%), and
**8 of 30 families fall below 50%**.

Setting the performance weight to zero — ranking on priced quantities only —
changes the winner in 5 of 30 families. `performance_index`,
`manufacturing_readiness`, `screening_exactness` and `route_confidence` are
author-assigned 0–100 screening scores, not measured quantities. **The
performance-zero ranking is the one reported as primary throughout**, and the
weight sensitivity is reported before the price sensitivity so a reader does
not mistake the second for the larger effect. It is not.

### 3.4 The recommendation changes with the price basis in 4 of 30 families

61 monthly states, 2021-09 to 2026-09. Nine metals vary (Ag, Al, Au, Cu, Ir,
Pd, Pt, Rh, Ru); Ni, Sn and Zn have no long feed and are held constant.

| Family | Winners (states) | Distinguishing metal | Minority run |
|---|---|---|---|
| photocatalytic water splitting | TiO₂ 42 / Pt-TiO₂ 19 | Pt 1 wt% vs none | 19 consecutive months, 2021-09 – 2023-03 |
| CO₂-to-formate | PdAg/N-C 37 / Ru-SA-LDH 24 | Pd+Ag 5 wt% vs Ru 0.5 wt% | 24 months, 3 runs |
| CO-PROX | CuO-CeO₂ 52 / Pt-Fe-Al₂O₃ 9 | Cu 5.6 wt% vs Pt 0.5 wt% | 9 consecutive months, 2024-09 – 2025-05 |
| N₂ reduction | Li-mediated (Cu) 53 / plasma (Ni) 8 | Cu vs Ni | 8 months, 2 runs |

All four are sustained runs. The clearest is photocatalytic water splitting:
the candidates are the same anatase TiO₂ and differ only by a 1 wt% Pt
co-catalyst, so the question "is the Pt loading worth its cost" is answered
differently in different years. Across the 19 months the Pt-loaded candidate
won, platinum sat between $878 and $1069/oz, against $1796 at the last state.

The separation is not on platinum alone — platinum revisits $902 later in the
window without the ranking returning — so this is a composite crossing, not a
single price threshold. Nitrogen reduction gives the cleaner threshold, because
its two candidates are single-metal: over the shorter window where nickel also
varies, the Cu candidate wins at Cu/Ni 0.685–0.763 and the Ni candidate at
0.830–0.890, with no overlap.

*[Figure 2: winner by month for the four families, against the driving price
ratio.]*

**The condition.** The 26 stable families are those whose candidates share a
metal, or whose loadings are too small to move the composite. The four that
flip all satisfy one condition: their candidates depend on **different metals
whose prices decouple** — a platinum-group metal against a base metal, one PGM
against another, or a metal loading against none. That is a statable rule for
when a screening ranking needs its price basis quoted alongside it.

## 4. Conclusion

Route-resolved cost and cradle-to-gate impact on one boundary let the same
model answer both halves of an early-stage screening question, and the Step
Method half reproduces the published CatCost cases without tuning. Across 116
candidates, raw materials dominate manufacturing GWP, so route energy is a
second-order term except for cheap base-metal precipitation catalysts.

The screening ranking itself is less stable than the numbers behind it. MCDA
weighting moves the winner in 8 of 30 families; the metal price basis moves it
in 4 of 30, whenever the candidates rest on different metals. Neither is a
reason to distrust screening — 26 of 30 families are robust to five years of
observed price movement — but both are reasons to publish the basis with the
result.

## 5. Limitations

To be stated in the manuscript, not buried:

1. **The candidate set is a screening library, not measured data.**
   `screening_basis` across the 116: 83 literature-architecture proxies, 29 engineering proxies, and 4 one-off bases (`market_plus_vendor_anchor`, `vendor_stack_anchor`, `literature_low_loading_plus_vendor_stack`, `ru_based_cost_pressure_relief`, one each).
2. **LCA coverage is bimodal.** Mean 62.8%, median 99.8%; 64 candidates ≥90%,
   47 below 50%. The low group is carbon supports, silica, zeolites, MOFs and
   g-C₃N₄, none covered by Nuss & Eckelman (2014). Unmatched mass is dominated
   by carbon forms.
3. **Electrocatalyst coating-line steps have no energy model** and are reported
   as unmodelled, so those families carry a materials-only route term.
4. **Nickel has no long price feed.** In the 61-month window it is held
   constant, so the N₂-reduction result there is copper-driven; the Cu/Ni
   threshold comes from the shorter 24-state window.
5. **The recorded series has a gap** between 2026-05-04 and 2026-07-20, so the
   Cu/Ni crossing is bracketed, not observed.
6. **MCDA scores are author-assigned.** Reported, and the reason the
   performance-zero ranking is primary.

## 6. Data and code availability

COMET is at github.com/hyunjin-kor/COMET under PolyForm Noncommercial 1.0.0
(free for research, teaching and use by public research institutions;
commercial use requires a separate licence). Releases are archived on Zenodo,
concept DOI 10.5281/zenodo.21451931.

Every number in this manuscript regenerates from:

```bash
python scripts/reproduce_catcost_table62.py --json docs/paper/table62_reproduction_<date>.json
python scripts/run_all_families.py --out docs/paper/all_families_<date>.json
python scripts/fetch_price_history.py --out docs/paper/price_history_<date>.json
python scripts/price_volatility_screen.py --history docs/paper/price_history_<date>.json \
    --since 2021-09 --out docs/paper/price_volatility_5y_<date>.json
python scripts/price_volatility_screen.py --out docs/paper/price_volatility_<date>.json
```

The frozen outputs of the run reported here are committed beside this file, so
a reader can check a quoted number without re-running anything.

> *Open item:* Zenodo records v1.3.10–v1.3.24 were published under CC BY 4.0
> before the licence was settled. Their metadata needs correcting by hand, and
> those grants cannot be withdrawn.

---

## Next actions

1. **Find the literature spread for §1.** Without it the introduction has no
   quantified gap and the paper reads as a tool description.
2. Draw Figures 1 and 2.
3. Assemble the reference list.
4. Settle authorship, affiliations, funding and target journal with 노인수 교수님.
