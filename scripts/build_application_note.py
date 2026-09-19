"""Render the JCIM Application Note draft from the frozen paper runs.

The note reuses the 2026-09-08 submission run, the combined robustness study and
the 2026-09-09 methods supplement, so every computed number carries the same
file/key reference as the full manuscript. --check compares the committed note
and its count record with a fresh render. No calculation code runs here.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import build_submission_manuscript as paper  # noqa: E402
from scripts.paper_labels import CANDIDATE_LABELS  # noqa: E402
from scripts.paper_units import KG_PER_SHORT_TON, PER_LB_TO_PER_KG  # noqa: E402

DATE = "2026-09-09"
RUN_DATE = "2026-09-08"
ROBUSTNESS = "robustness-2026-09-08/decision_robustness.json"
METHODS = "methods-2026-09-09/methods_study.json"
EXAMPLE = "figures-note-2026-09-09/reference_example_ni_al2o3.json"
MARKET = "submission-2026-09-08/table62_reproduction_2026-09-08.json"
LIVE_FAMILIES = "submission-2026-09-08/all_families_live_2026-09-08.json"
LIVE_BASIS = "submission-2026-09-08/live_basis_2026-09-08.json"
PREPARATION = "manufacturing-2026-09-14/review_summary.json"
MANUFACTURING = "manufacturing-study-2026-09-15/manufacturing_study.json"
CROSSOVER_STUDY = "price-crossovers-2026-09-13/price_crossovers.json"
CROSSOVER_MECHANISMS = "price-crossovers-2026-09-13/crossover_mechanisms.json"
LITERATURE = "backend/data/manufacturing_literature.json"
POWER_FIELDS = ("ramp_power_kw", "hold_power_kw", "average_power_kw", "additional_power_kw", "measured_energy_kwh")
WORD_LIMIT = 5000
GRAPHICS = [
    {"figure": 1, "width": "double", "word_equivalent": 600},
    {"figure": 2, "width": "double", "word_equivalent": 600},
    {"figure": 3, "width": "double", "word_equivalent": 600},
    {"figure": 4, "width": "double", "word_equivalent": 600},
]


def load_run():
    """Build the 2026-09-08 run without leaving the shared module pointed at it."""
    saved = {name: getattr(paper, name) for name in ("DATE", "META_NAME", "CONTROLLED_NAME", "CONTROLLED_PROVENANCE")}
    paper.DATE = RUN_DATE
    paper.META_NAME = f"submission_metadata_{RUN_DATE}.json"
    paper.CONTROLLED_NAME = f"controlled-{RUN_DATE}/controlled_cases.json"
    paper.CONTROLLED_PROVENANCE = f"controlled-{RUN_DATE}/provenance.json"
    try:
        run = paper.PaperRun(paper.PAPER / f"submission-{RUN_DATE}")
    finally:
        for name, value in saved.items():
            setattr(paper, name, value)
    for name in (ROBUSTNESS, METHODS, EXAMPLE, MARKET, PREPARATION, MANUFACTURING, CROSSOVER_STUDY, CROSSOVER_MECHANISMS,
                 LIVE_FAMILIES, LIVE_BASIS):
        run.data[name] = paper.load(paper.PAPER / name)
    if run.data[ROBUSTNESS]["seed"] != run.manifest["seed"] or run.data[METHODS]["seed"] != run.manifest["seed"]:
        raise ValueError("Robustness study, methods supplement and primary run must share one seed")
    return run


def note(run):
    r = run.ref
    run.publication_conversions = []
    run.derived_values = []

    def derived(value, spec, source, rule):
        """A number computed here from bound records; the check file keeps its source and rule."""
        shown = format(value, spec)
        run.derived_values.append({"display": shown, "source": source, "rule": rule})
        return shown

    def kg(alias, key, spec=".4f", factor=PER_LB_TO_PER_KG):
        source = r(alias, key)
        value = paper.key_value(run.data[run.names.get(alias, alias)], key)
        converted = value * factor
        run.publication_conversions.append({"source": run.names.get(alias, alias), "key": key,
                                           "source_value": value, "factor": factor,
                                           "converted_value": converted, "display": format(converted, spec)})
        return format(converted, spec) + "<!--" + source.split("<!--", 1)[1]
    def rb(key, spec=None):
        return r(ROBUSTNESS, key, spec)

    def cs(key, spec=None):
        return r(CROSSOVER_STUDY, key, spec)

    ammonia = next(index for index, family in enumerate(run.data[CROSSOVER_STUDY]["families"]) if family["family"] == "ammonia-cracking")
    monthly = f"families[{ammonia}].periods.monthly.summary"

    def ms(key, spec=None):
        return r(METHODS, key, spec)

    def mk(key, spec=None):
        return r(MARKET, key, spec)

    example = run.data[METHODS]["normalization"]["example"]
    retained = [row["cost"] for row in example["rows"]]
    full_range = derived((max(*retained, example["removed_cost"]) - min(retained)) * PER_LB_TO_PER_KG, ",.0f", METHODS,
                         "normalization.example: (max of retained and removed cost - min retained cost) converted to USD/kg")
    retained_range = derived((max(retained) - min(retained)) * PER_LB_TO_PER_KG, ".1f", METHODS,
                             "normalization.example: max - min of retained costs converted to USD/kg")
    pair_gap = derived(abs(retained[0] - retained[2]) * PER_LB_TO_PER_KG, ".2f", METHODS,
                       "normalization.example: |rows[0].cost - rows[2].cost| converted to USD/kg")

    def minus(text):
        """Typeset a leading negative sign as a minus sign; the binding comment is unchanged."""
        return "−" + text[1:] if text.startswith("-") else text

    def magnitude(text):
        """Drop the sign of a bound value; the binding comment is unchanged."""
        return text.lstrip("+-−")

    names = CANDIDATE_LABELS["ammonia-cracking"]
    co, ni_mgo, ni_al, ru = (names[slug] for slug in ("co-mgo-la2o3", "ni-mgo-ceo2-interface", "ni-alumina-baseline", "ru-mgo-premium"))
    if [row["slug"] for row in example["rows"]] != ["co-mgo-la2o3", "ni-mgo-ceo2-interface", "ni-alumina-baseline"] \
            or example["removed"] != "ru-mgo-premium":
        raise ValueError("The normalization example no longer lists the ammonia-cracking candidates in the stated order")

    basis_counts = run.summary["screening_basis_counts"]
    other_bases = derived(sum(value for key, value in basis_counts.items() if key not in ("literature_architecture_proxy", "engineering_proxy")),
                          "d", run.names["s"], "screening_basis_counts: sum of bases other than literature-architecture and engineering proxies")
    if sum(basis_counts.values()) != run.data[ROBUSTNESS]["summary"]["candidates"]:
        raise ValueError("Screening-basis counts do not cover every candidate")

    # The abstract and conclusions quote the largest of the three published-example residuals.
    residuals = [abs(row["residual_pct"]) for row in run.summary["table62"]]
    if max(residuals) != residuals[1]:
        raise ValueError("The Ni/Al2O3 residual is no longer the largest published-example difference")
    largest_residual = magnitude(r("s", "table62[1].residual_pct", "+.2f"))

    # Stored live quotations versus the May 2026 reference: the text names the ammonia-cracking change and its cause.
    live_rows = run.summary["live_reference_comparison"]["rows"]
    ammonia_live = next(row for row in live_rows if row["family"] == "ammonia-cracking" and row["profile"] == "balanced")
    if (ammonia_live["reference_winner"], ammonia_live["live_winner"]) != ("co-mgo-la2o3", "ni-mgo-ceo2-interface"):
        raise ValueError("The live-quotation leader change stated for ammonia cracking no longer holds")
    if run.data[LIVE_BASIS]["price_basis"]["Co"].get("fetched_at") is not None:
        raise ValueError("The text states that cobalt has no stored live quotation")
    reference_families = run.data[run.names["a"]]["families"]
    live_families = run.data[LIVE_FAMILIES]["families"]
    fam = next(index for index, row in enumerate(reference_families) if row["family"] == "ammonia-cracking")
    if live_families[fam]["family"] != "ammonia-cracking":
        raise ValueError("Reference and live family order differ")

    def score(families, name, slug, key):
        slot = next(index for index, row in enumerate(families[fam]["candidates"]) if row["slug"] == slug)
        return r(name, f"families[{fam}].candidates[{slot}].scores.{key}", ".1f")

    observed = datetime.fromisoformat(run.data[LIVE_BASIS]["observation_started_at_utc"])
    live_date = f"{observed:%B} {observed.day}, {observed.year}<!-- {LIVE_BASIS}:observation_started_at_utc -->"
    fcc = run.data[MARKET][2]
    fcc_market_pct = derived(100 * (fcc["with_published_rate"]["estimated_price_per_lb"] / fcc["market"]["market_price_per_lb"] - 1), ".1f",
                             MARKET, "[2]: 100 * (with_published_rate.estimated_price_per_lb / market.market_price_per_lb - 1)")

    # Figure 2(b): price shares of the lowest-cost candidate in each thermal family (same rule as the figure).
    shares = []
    for family in reference_families:
        if family["catalyst_domain"] != "thermal":
            continue
        best = min(family["candidates"], key=lambda c: c["landed_cost_per_lb"])
        total = best["landed_cost_per_lb"]
        shares.append((100 * best["materials_cost_per_lb"] / total, 100 * best["processing_cost_per_lb"] / total,
                       100 * (total - best["materials_cost_per_lb"] - best["processing_cost_per_lb"]) / total))
    structure_source = run.names["a"]
    thermal = derived(len(shares), "d", structure_source, "families with catalyst_domain thermal")
    materials_majority = derived(sum(m > 50 for m, _p, _o in shares), "d", structure_source,
                                 "thermal lowest-cost candidates with materials_cost_per_lb above 50% of landed_cost_per_lb")
    processing_over = derived(sum(p > m for m, p, _o in shares), "d", structure_source,
                              "thermal lowest-cost candidates with processing_cost_per_lb above materials_cost_per_lb")
    other_low = derived(min(o for *_mp, o in shares), ".0f", structure_source,
                        "minimum share of landed cost outside materials and processing among thermal lowest-cost candidates")
    other_high = derived(max(o for *_mp, o in shares), ".0f", structure_source,
                         "maximum share of landed cost outside materials and processing among thermal lowest-cost candidates")

    # Preparation records: which heating inputs the sources state.
    literature = json.loads((ROOT / LITERATURE).read_text(encoding="utf-8"))
    segments = [s for p in literature["profiles"] for o in p["operations"] for s in o.get("temperature_profile") or []]
    if any(o.get(key) is not None for p in literature["profiles"] for o in p["operations"] for key in POWER_FIELDS) \
            or any(s.get(key) is not None for s in segments for key in POWER_FIELDS):
        raise ValueError("A preparation record now states an electrical input; revise the preparation-evidence sentence")
    if any(s.get("target_c") is None for s in segments):
        raise ValueError("The text states that every heating segment has a target temperature")
    n_segments = derived(len(segments), ",", LITERATURE, "temperature_profile segments across all profiles")
    n_hold = derived(sum(s.get("hold_h") is not None for s in segments), ",", LITERATURE, "segments with hold_h")
    n_ramp = derived(sum(s.get("ramp_c_per_min") is not None for s in segments), ",", LITERATURE, "segments with ramp_c_per_min")
    n_mass = derived(sum(p.get("finished_batch_mass_kg") is not None for p in literature["profiles"]), "d", LITERATURE,
                     "profiles with finished_batch_mass_kg")

    # Manufacturing sensitivity: the text names these three inputs and the exact doubling at half output.
    sensitivity = run.data[MANUFACTURING]["sensitivity"]
    if [sensitivity[i]["label"] for i in (0, 4, 5)] != ["Dry output", "Calcination hold", "Calcination power"]:
        raise ValueError("The manufacturing sensitivity rows no longer match the inputs named in the text")
    baseline_price = run.data[MANUFACTURING]["baseline"]["summary"]["estimated_price_per_kg"]
    if sensitivity[0]["low"] * 2 != sensitivity[0]["value"] or abs(sensitivity[0]["low_usd_kg"] - 2 * baseline_price) > 0.005:
        raise ValueError("Halving the dry output no longer doubles the selling price")

    def sn(key, spec):
        return r(MANUFACTURING, f"sensitivity{key}", spec)

    # Monthly repricing of ammonia cracking: the balanced leader holds because Ru/MgO fixes the top of the cost scale.
    records = run.data[CROSSOVER_STUDY]["families"][ammonia]["periods"]["monthly"]["records"]
    if any(row["scores"]["ru-mgo-premium"]["economics"] != 0 for row in records):
        raise ValueError("Ru/MgO no longer sets the upper end of the ammonia-cracking cost scale in every month")
    compressed = derived(min(row["scores"][slug]["economics"] for row in records for slug in ("co-mgo-la2o3", "ni-alumina-baseline")),
                         ".1f", CROSSOVER_STUDY, "ammonia-cracking monthly records: minimum economics score of co-mgo-la2o3 and ni-alumina-baseline")

    return f"""# COMET: Catalyst Overall Manufacturing Estimation Tool

Authors, affiliations and corresponding-author contact: [to be supplied by the authors].

## Abstract

Early-stage catalyst cost estimates depend on operating inputs that preparation reports seldom state and on metal prices that change over time. COMET (Catalyst Overall Manufacturing Estimation Tool) links source-traceable preparation records, batch costing from declared operating inputs, dated price histories, and ranking diagnostics for {rb('summary.candidates')} catalyst formulations in {rb('summary.families')} reaction families. It reproduces three published Step Method estimates within {largest_residual}%, and an illustrative batch shows how treatment duration and recovered mass set the cost per kilogram. Across {rb('summary.months')} monthly metal-price states, the lowest-cost candidate changes in {cs('summary.monthly.cost_winner')} of {cs('summary.monthly.families')} families, and recommendations also shift with price-source reliability and the candidate set. Cost comparisons should therefore state price basis, date, candidate set, and assumed inputs.

Keywords: catalyst manufacturing cost; preparation provenance; sensitivity analysis; multicriteria decision analysis; software.

## Introduction

Catalyst development decisions depend on manufacturing cost as well as on activity, selectivity, and stability. In biomass-conversion design reports summarized by Baddour et al., catalyst cost accounted for 3–9% of installed equipment cost and moved the minimum fuel selling price by up to ±10%, yet researchers outside catalyst companies have few resources for estimating the manufacturing cost of their materials.<sup>1</sup>

Published methods address parts of this problem. The Step Method maps a laboratory synthesis onto priced industrial processing steps at an order-size-dependent scale and margin; for three commercial catalysts, its estimates agreed with market prices within ±20%.<sup>1</sup> CatCost combined manufacturing cost with environmental impact across synthesis methods and scales.<sup>2</sup> Route-specific studies have costed laboratory metal-oxide syntheses<sup>3</sup> and a scaled-up platinum–strontium titanate synthesis,<sup>4</sup> and BioSTEAM propagates parameter uncertainty through techno-economic analyses.<sup>5</sup>

Applying these methods to literature candidates raises three problems. First, reported conditions do not map onto cost inputs: a furnace temperature does not specify electricity use, a precursor charge does not establish recovered mass, and treatment time differs from attended labor; estimates that fill such gaps silently cannot be audited. Second, metal prices move, so a cost ordering obtained at one date may not hold at another, and quotations differ in reliability. Third, when cost is combined with other criteria, min–max normalized scores depend on which candidates are compared.<sup>6,7</sup>

COMET was developed to make these conditions explicit. It extends Step Method and CatCost accounting with source-linked preparation records, batch costing from declared operating inputs, dated prices, and ranking diagnostics. We verify it against the published Step Method examples and apply it to {rb('summary.candidates')} formulations in {rb('summary.families')} reaction families to examine how operating inputs, price movements, price sources, and candidate sets affect estimates and recommendations.

## Implementation

### Software design

In the workflow of Figure 1, a user enters a formulation, edits its route and scale, selects a price basis, and obtains an estimate listing its sources and missing inputs; saved estimates can be recalculated, compared, and ranked. A FastAPI (Python) backend stores prices and estimates in SQLite, and a bilingual React/TypeScript interface is packaged for Windows with Electron and PyInstaller; Linux backend and interface builds were also tested. Exports and analysis records keep provenance, checksums, software versions, and seeds.

![Figure 1. COMET workflow. Sources and assumptions accompany formulation, price selection, cost estimation, and ranking. Conceptual artwork used OpenAI's image-generation tool.](figures-note-2026-09-09/fig1_workflow_stack.png)

### Cost models

Screening estimates follow the Step Method (Figure 2a).<sup>1</sup> Materials cost is Cₘ = Σ<sub>i</sub>w<sub>i</sub>c<sub>i</sub>, with component mass fraction w<sub>i</sub> and price c<sub>i</sub> per kg; a precursor requires $w/(f\\,p\\,y)$ kg per kg of catalyst (component fraction $w$, fraction in the pure precursor $f$, purity $p$, retention $y$). Processing cost is Cₚ = 24TIH/M, with campaign duration T in days, price-index factor I, summed hourly cost H of the selected operations, and catalyst mass M in kg. Order size sets the scale, rate, and cleaning time; documented effective rates can replace nominal ones. Hourly rates use the published 2017 basis escalated by a producer price index; {r('s', 'manufacturing.20.template_count')} editable procedures are provided, with substituted or uncosted steps flagged. The selling price is P = (Cₘ + Cₚ)(1 + g)(1 + s)/(1 − m), with general and administrative (G&A) fraction g, sales, administrative, research, and distribution (SARD) fraction s, and margin m from the published order-size correlation. In rankings, cost denotes P per kilogram.

For a laboratory preparation, batch costing replaces these terms with purchases and operating inputs (Supporting Information, eqs S1–S6): electricity from measured kWh or mean power over ramp and hold times, equipment occupancy, attended labor, gases, and transfers allocated by recovered mass or solution volume. Costs are divided by the dry output mass before overheads and margin, and a missing required input stops the calculation.

![Figure 2. Cost estimation. (a) Step Method. (b) Selling-price shares and prices (USD/kg). Gray includes G&A, SARD, margin, and assumed route allowances for quality assurance, activation, and additional overhead. (c) Deviations from market prices reported by Baddour et al.<sup>1</sup>; negative values denote lower estimates. SCR, selective catalytic reduction; RWGS, reverse water–gas shift. Conceptual artwork in (a) used OpenAI's image-generation tool.](figures-note-2026-09-09/fig2_cost_model.png)

### Preparation records

Preparation records trace these inputs to their sources. An audit of the {r(PREPARATION, 'candidates')} candidates verified {r(PREPARATION, 'crossref_dois')} digital object identifiers (DOIs) with Crossref and transcribed {r(PREPARATION, 'profiles')} specimen-specific records from {r(PREPARATION, 'primary_sources')} sources, linked to {r(PREPARATION, 'candidates_with_profile')} candidates; {r(PREPARATION, 'source_mismatches')} candidates carry composition or source discrepancies. Each value keeps its DOI, locator, and original value, user edits are stored separately, and unreported conditions stay blank. A linked specimen does not validate the catalog formulation (Supporting Information, Section S6).

### Prices and ranking

Each price keeps its source, date, and retrieval time. Current quotations include Johnson Matthey platinum and palladium<sup>8</sup> and Westmetall copper and aluminum;<sup>9</sup> historical metal prices come from the International Monetary Fund (IMF) Primary Commodity Price System<sup>10</sup> and Johnson Matthey monthly averages, and support prices from U.S. import unit values<sup>11</sup>. A price-source grade, weighted by each price's share of materials cost, rates provenance only. Environmental screening uses cradle-to-gate metal factors.<sup>12</sup>

The library comprises {r('s', 'screening_basis_counts.literature_architecture_proxy')} literature-architecture proxies, {r('s', 'screening_basis_counts.engineering_proxy')} engineering proxies, and {other_bases} candidates with documented vendor or market bases. Rankings combine cost, price-data reliability, and author-assigned route and performance scores; within each family, cost scores run from 100 (least expensive) to 0 (most expensive), and lower cost breaks ties. Baseline rankings use May 2026 prices, balanced weights, and all candidates; electrochemical families lacking electrode data are compared on powder cost.

## Results and Discussion

### Verification

The three Step Method examples, which report estimates and market prices, serve as an external reference; inputs were entered unadjusted.<sup>1</sup> COMET gives {kg('s', 'table62[0].comet_usd_per_lb', '.4f')} USD/kg for Pt/C against {kg('s', 'table62[0].published_usd_per_lb', '.3f')} USD/kg reported, both excluding platinum value. For Ni/Al₂O₃, the {minus(r('s', 'table62[1].residual_pct', '+.2f'))}% difference ({kg('s', 'table62[1].comet_usd_per_lb', '.4f')} versus {kg('s', 'table62[1].published_usd_per_lb', '.3f')} USD/kg) arises because COMET applies the published margin correlation instead of the table's fixed margin. For a fluid catalytic cracking (FCC) catalyst based on ultrastable zeolite Y, COMET gives {kg('s', 'table62[2].comet_usd_per_lb', '.4f')} versus {kg('s', 'table62[2].published_usd_per_lb', '.3f')} USD/kg ({r('s', 'table62[2].residual_pct', '+.2f')}%) at the reported effective rate of {kg('s', 'table62[2].effective_rate_ton_per_day', ',.1f', KG_PER_SHORT_TON)} kg/day. Values convert the published per-pound prices; intermediate values agree at the reported precision. Relative to the source's market prices (Figure 2c), 100 × (estimate − market price)/market price is {minus(mk('[0].market.comet_vs_market_pct', '.1f'))}% for Pt/C, {minus(mk('[1].market.comet_vs_market_pct', '.1f'))}% for Ni/Al₂O₃, and {minus(fcc_market_pct)}% for FCC ({kg(MARKET, '[2].with_published_rate.estimated_price_per_lb', '.4f')} versus {kg(MARKET, '[2].market.market_price_per_lb', '.2f')} USD/kg). Like the published estimates, all three lie below market and within the original ±20% agreement. The agreement covers three catalysts at mid-2017 prices.

### Screening cost structure

Figure 2(b) decomposes the selling price of the lowest-cost candidate in each of the {thermal} thermal families at May 2026 prices. Materials exceed half of the price in only {materials_majority} families, processing exceeds materials in {processing_over}, and G&A, SARD, margin, and assumed route allowances take {other_low}–{other_high}%. For base-metal catalysts, the estimate thus depends as much on processing and overhead assumptions as on materials prices. A 20 wt% Ni/Al₂O₃ catalyst prepared by incipient wetness impregnation and ordered at {kg(EXAMPLE, 'request.order_size_tons', ',.1f', KG_PER_SHORT_TON)} kg sells for {kg(EXAMPLE, 'step_method.estimated_price_per_lb', '.2f')} USD/kg, of which nickel, alumina (import unit value), and processing contribute {kg(EXAMPLE, 'materials.components[0].cost_per_lb_cat', '.2f')}, {kg(EXAMPLE, 'materials.components[1].cost_per_lb_cat', '.2f')}, and {kg(EXAMPLE, 'step_method.processing_cost_per_lb', '.2f')} USD/kg. Cross-reaction comparisons do not imply equal performance.

### Laboratory batch costs

Processing costs rest on operating inputs that published preparations rarely report: in the records, all {n_segments} heating segments state a target temperature, {n_hold} a hold time, and {n_ramp} a ramp rate, but none states the electrical input, and only {n_mass} of {r(PREPARATION, 'profiles')} records reports the recovered batch mass. Figure 3 follows such inputs through an illustrative {sn('[0].value', '.3f')} kg dry batch (impregnation, drying, calcination, reduction) whose inputs are all declared assumptions. Of the baseline selling price of {r(MANUFACTURING, 'baseline.summary.estimated_price_per_kg', ',.2f')} USD/kg, operating contributions (Figure 3b) account for {r(MANUFACTURING, 'baseline.summary.processing_pct', '.1f')}% and purchases for {r(MANUFACTURING, 'baseline.summary.materials_pct', '.1f')}%. Each additional calcination hour adds {r(MANUFACTURING, 'marginal_calcination_hour_usd_kg', '.2f')} USD/kg through electricity and equipment occupancy; attendance is entered separately, so labor is unchanged. Under the assumed tariff and occupancy rate, duration outweighs power: {sn('[4].low', '.0f')}–{sn('[4].high', '.0f')} h holds span {sn('[4].low_usd_kg', ',.2f')}–{sn('[4].high_usd_kg', ',.2f')} USD/kg, whereas hold powers of {sn('[5].low', '.1f')}–{sn('[5].high', '.1f')} kW span {sn('[5].low_usd_kg', ',.2f')}–{sn('[5].high_usd_kg', ',.2f')} USD/kg (Table S5). Recovered mass scales every cost (Figure 3c): halving the dry output doubles the price to {sn('[0].low_usd_kg', ',.2f')} USD/kg at unchanged batch expenditure. The curves allocate cost and predict neither yields nor scale-up. Supporting Information adds {r(MANUFACTURING, 'monte_carlo.n_simulations', ',')} seeded Monte Carlo trials and arithmetic checks.

![Figure 3. Manufacturing conditions. (a) Illustrative preparation sequence. (b) Operating contributions per kg of dry product, excluding purchases, overheads, and margin. (c) Selling price versus calcination hold for 0.015, 0.030, and 0.045 kg dry outputs; the point marks the baseline. Quantities, prices, and operating inputs are hypothetical. Panel (a) artwork used OpenAI's image-generation tool.](manufacturing-study-2026-09-15/figures/fig_manufacturing.png)

### Observed price crossovers

To test whether screening orderings persist beyond one price date, every family was recalculated for {cs(monthly + '.observations')} monthly metal-price states with formulations, order sizes, route assumptions, support prices, and non-cost scores fixed. The lowest-cost candidate changes in {cs('summary.monthly.cost_winner')} of {cs('summary.monthly.families')} families, and the balanced leader in {cs('summary.monthly.app_winner')}. In ammonia cracking (ammonia decomposition; Figure 4a), {co} is least expensive in {cs(monthly + '.winner_counts.cost_winner.co-mgo-la2o3')} states and {ni_al} in {cs(monthly + '.winner_counts.cost_winner.ni-alumina-baseline')}. Between September and October 2025, cobalt rose from {kg(CROSSOVER_MECHANISMS, 'cases[0].metal_effects.Co.price_before', '.2f')} to {kg(CROSSOVER_MECHANISMS, 'cases[0].metal_effects.Co.price_after', '.2f')} USD/kg with nickel nearly unchanged, and {ni_al} ({kg(CROSSOVER_MECHANISMS, 'cases[0].costs_after.ni-alumina-baseline', '.2f')} USD/kg) became cheaper than {co} ({kg(CROSSOVER_MECHANISMS, 'cases[0].costs_after.co-mgo-la2o3', '.2f')} USD/kg). Monthly states cluster near the conditional equal-cost boundary in the nickel–cobalt price plane (Figure 4b), so modest cobalt movements change the cost leader. The balanced recommendation nevertheless stays {co} in all {cs(monthly + '.winner_counts.app_winner.co-mgo-la2o3')} states: the far costlier {ru} fixes the top of the cost scale, so the two cost leaders keep cost scores of at least {compressed}. A cost crossover therefore need not change the recommendation.

### Recommendation sensitivity

Recommendations also respond to factors other than cost. Replacing the May 2026 reference with stored live quotations collected on {live_date} changes the balanced leader in {r('s', 'live_reference_comparison.changed_by_profile.balanced')} of {cs('summary.monthly.families')} families (Table S7). In ammonia cracking, cobalt lacks a live quotation and falls back to an annual reference price; the price-reliability score of {co} drops from {score(reference_families, run.names['a'], 'co-mgo-la2o3', 'evidence')} to {score(live_families, LIVE_FAMILIES, 'co-mgo-la2o3', 'evidence')}, cost scores stay near 100, and the {ni_mgo} leads.

Varying {rb('summary.months')} monthly price datasets jointly with {rb('summary.weight_points["0.05"]', ',')} weight combinations gives {rb('summary.joint_scenarios_all_families["0.05"]', ',')} scenarios. In Figure 4(c), the baseline candidate ranks first with a median frequency of {rb('summary.reference_winner_joint_share_median_pct', '.2f')}%, and {rb('summary.rubric_robust_family_counts["5"]')} families keep their leader under 5-point changes in route and performance scores. These frequencies describe stability over stated scenarios, not future probabilities.

The candidate set acts through normalization. Baseline ammonia-cracking costs are {kg(METHODS, 'normalization.example.rows[0].cost', '.2f')} USD/kg for {co}, {kg(METHODS, 'normalization.example.rows[1].cost', '.2f')} for the {ni_mgo}, {kg(METHODS, 'normalization.example.rows[2].cost', '.2f')} for {ni_al}, and {kg(METHODS, 'normalization.example.removed_cost', ',.2f')} for {ru}; {co} leads with {ms('normalization.example.rows[0].total_before', '.1f')} against {ms('normalization.example.rows[2].total_before', '.1f')} for {ni_al}. Removing {ru} undoes the compression noted above: costs are unchanged, but their range contracts from about {full_range} to {retained_range} USD/kg. Renormalization magnifies the {pair_gap} USD/kg difference, changes the scores to {ms('normalization.example.rows[0].total_after', '.1f')} and {ms('normalization.example.rows[2].total_after', '.1f')}, and reverses the ranking; retaining the original range prevents this.<sup>6,7</sup> Across families, removal changes the leader in {rb('summary.candidate_removal_winner_changes')} of {rb('summary.candidate_removal_cases')} tests; Figure 4(d) gives 100 × (C₁ − C₀)/C₀ for the leaders' costs before (C₀) and after (C₁) removal.

![Figure 4. Observed-price crossovers and ranking sensitivity. (a) Costs (modeled selling prices) of the ammonia-cracking candidates that attain the lowest cost under 89 monthly price states; lines connect observed states. (b) Conditional equal-cost boundary between {co} and {ni_al} in the nickel–cobalt price plane; points are monthly states, diamonds mark September and October 2025, and shading identifies the cheaper candidate. (c) First-rank frequencies; dashed line, 50%. (d) Cost differences between leaders before and after candidate removal; negative values indicate less expensive replacements. PEM, proton exchange membrane; AEM, anion exchange membrane; OER, oxygen evolution reaction; ORR, oxygen reduction reaction; SCR, selective catalytic reduction.](figures-note-2026-09-09/fig4_decision_diagnostics.png)

### Limitations

Results are conditional on declared inputs and screening judgments. Industrial accuracy remains unvalidated because observations did not jointly match formulation, grade, scale, date, and boundary; mean absolute percentage error was not calculated. Environmental coverage averages {r('s', 'lca.coverage_mean_pct', '.2f')}% of catalyst mass ({r('s', 'lca.candidates_coverage_below_50_pct')} candidates below 50%) and excludes solvents, wastewater treatment, and equipment manufacture. Activity, deactivation, and use-phase impacts are outside scope.

## Conclusions

COMET makes explicit the conditions behind early-stage catalyst cost estimates: input sources and completeness, price dates and origins, and the candidates and weights behind a ranking. Its arithmetic reproduces the published Step Method examples within {largest_residual}%. Published preparations seldom state recovered mass, which, with treatment duration, changed the laboratory batch cost far more than calcination power did. Observed prices changed the lowest-cost candidate in {cs('summary.monthly.cost_winner')} of {cs('summary.monthly.families')} families, and price sources and candidate sets changed recommendations. Comparisons should therefore report price basis, date, candidate set, and assumed inputs. Next steps are validation against condition-matched industrial prices and links to cost-responsive synthesis optimization<sup>13</sup> and catalyst lifetime.<sup>14</sup>

## Supporting Information

Calculation methods, declared inputs, arithmetic verification, sensitivity analyses, price histories, cost crossovers, live-quotation leaders, candidate prices, preparation evidence, and application views (PDF); data and reproduction files (ZIP).

## Data and Software Availability

COMET version {r('m', 'project_version')} uses the PolyForm Noncommercial License 1.0.0; commercial use requires a separate license. [Authors must state how a commercial license can be obtained.] Repository: https://github.com/hyunjin-kor/COMET. Concept DOI: 10.5281/zenodo.21451931. [Authors must confirm access to this version and analysis files before submission.] Selected analysis inputs, outputs, checksums, and reproduction instructions accompany the study; the final distribution scope remains subject to author confirmation. Third-party data retain their source terms.

## Acknowledgments

OpenAI Codex and GPT tools and Anthropic Claude assisted software development, analysis scripts, and manuscript drafting and editing. OpenAI's image-generation tool produced conceptual artwork in Figures 1–3, and Google Gemini produced conceptual artwork in Supporting Information Figures S1 and S8, in September 2026. Numerical plots were generated from the reported calculations. The authors reviewed all AI-assisted content and are responsible for the final content. [Authors must confirm the tools, versions, and periods of AI assistance.] Funding: [author statement required].

## Competing interests

Competing interests: [author declaration required].


## References

1. Baddour, F. G.; Snowden-Swan, L.; Super, J. D.; Van Allsburg, K. M. Estimating Precommercial Heterogeneous Catalyst Price: A Simple Step-Based Method. *Organic Process Research & Development* **2018**, *22* (12), 1599–1605. [DOI](https://doi.org/10.1021/acs.oprd.8b00245).
2. Van Allsburg, K. M.; Tan, E. C. D.; Super, J. D.; Schaidle, J. A.; Baddour, F. G. Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. *Nature Catalysis* **2022**, *5* (4), 342–353. [DOI](https://doi.org/10.1038/s41929-022-00759-6).
3. Gkika, D. A.; Kyzas, G. Z. Cost Evidence Yields the Viability of Metal Oxides Synthesis Routes. *ACS Sustainable Chemistry & Engineering* **2025**, *13* (41), 17370–17379. [DOI](https://doi.org/10.1021/acssuschemeng.5c06752).
4. Ferdous, S.; Gracida-Alvarez, U. R.; Ferrandon, M.; Delferro, M.; Benavides, P. T.; Urgun-Demirtas, M. Techno-economic and life cycle analyses of the synthesis of a platinum–strontium titanate catalyst. *Catalysis Science & Technology* **2025**, *15* (15), 4419–4429. [DOI](https://doi.org/10.1039/d5cy00189g).
5. Cortes-Peña, Y.; Kumar, D.; Singh, V.; Guest, J. S. BioSTEAM: A Fast and Flexible Platform for the Design, Simulation, and Techno-Economic Analysis of Biorefineries under Uncertainty. *ACS Sustainable Chemistry & Engineering* **2020**, *8* (8), 3302–3310. [DOI](https://doi.org/10.1021/acssuschemeng.9b07040).
6. Mohammadi, M.; Rezaei, J. Ratio product model: A rank-preserving normalization-agnostic multi-criteria decision-making method. *Journal of Multi-Criteria Decision Analysis* **2023**, *30* (5–6), 163–172. [DOI](https://doi.org/10.1002/mcda.1806).
7. OECD; European Union; Joint Research Centre - European Commission. *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD, 2008. [DOI](https://doi.org/10.1787/9789264043466-en).
8. Johnson Matthey. PGM Prices and Trading. https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management (accessed September 11, 2026).
9. Westmetall. Market Data: Prices and LME Stocks. https://www.westmetall.com/en/markdaten.php (accessed September 11, 2026).
10. International Monetary Fund. Primary Commodity Price System (PCPS), SDMX 2.1 data service. https://api.imf.org/external/sdmx/2.1/dataflow/IMF.RES/PCPS (accessed September 11, 2026).
11. United Nations. UN Comtrade Database. https://comtradeplus.un.org (accessed September 11, 2026).
12. Nuss, P.; Eckelman, M. J. Life Cycle Assessment of Metals: A Scientific Synthesis. *PLoS ONE* **2014**, *9* (7), e101298. [DOI](https://doi.org/10.1371/journal.pone.0101298).
13. Petel, B. E.; Van Allsburg, K. M.; Baddour, F. G. Cost-Responsive Optimization of Nickel Nanoparticle Synthesis. *Advanced Sustainable Systems* **2024**, *8* (10), 2300030. [DOI](https://doi.org/10.1002/adsu.202300030).
14. Mendoza Suarez, F.; Tatarchuk, B. Comparative economic analysis of batch vs. continuous manufacturing in catalytic heterogeneous processes: impact of catalyst activity maintenance and materials costs on total costs of manufacturing in the production of fine chemicals and pharmaceuticals. *Journal of Flow Chemistry* **2025**, *15* (1), 21–38. [DOI](https://doi.org/10.1007/s41981-024-00342-z).
"""


def counts(text, run):
    abstract = text.split("## Abstract\n\n", 1)[1].split("\n\nKeywords:", 1)[0]
    body = text.split("## Introduction", 1)[1].split("## References", 1)[0]
    body = re.sub(r"^!\[.*$", "", body, flags=re.M)
    figures = len(re.findall(r"^!\[", text, flags=re.M))
    if figures != len(GRAPHICS):
        raise ValueError("Figure count differs from the declared graphics budget")
    graphics = sum(g["word_equivalent"] for g in GRAPHICS)
    abstract_words = paper.word_count(abstract)
    body_words = paper.word_count(body)
    total = abstract_words + body_words + graphics
    total_with_toc = total + 300
    if total_with_toc > WORD_LIMIT:
        raise ValueError(f"Word equivalents including the conservative TOC allowance {total_with_toc} exceed {WORD_LIMIT}")
    return {
        "target": "Journal of Chemical Information and Modeling, Application Note",
        "word_limit_abstract_text_graphics": WORD_LIMIT,
        "abstract_words": abstract_words,
        "text_words_excluding_references": body_words,
        "graphics": GRAPHICS,
        "graphics_word_equivalent": graphics,
        "total_word_equivalent": total,
        "toc_word_equivalent_allowance": 300,
        "total_word_equivalent_with_toc": total_with_toc,
        "toc_count_note": "A conservative 300-word allowance is tracked separately because the Application Note rule does not explicitly resolve TOC inclusion.",
        "figure_count": figures,
        "table_count": 0,
        "software_named_in_title": text.startswith("# COMET:"),
        "json_key_references": paper.verify_references(text, run),
        "publication_mass_unit": "kg",
        "publication_conversions": run.publication_conversions,
        "derived_values": run.derived_values,
        "primary_run": run.prefix,
        "basis_month": run.summary["basis_month"],
        "seed": run.manifest["seed"],
        "count_note": "Lexical count of the abstract and text from Introduction through Competing interests, including headings and placeholders. Figure captions and references are excluded; graphics add 300/600 word equivalents for single/double-column figures.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    run = load_run()
    text = note(run)
    record = counts(text, run)
    outputs = {
        f"application-note-{DATE}.md": text,
        f"application_note_checks_{DATE}.json": json.dumps(record, ensure_ascii=False, indent=2) + "\n",
    }
    for name, content in outputs.items():
        path = paper.PAPER / name
        if args.check:
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Generated file differs: {name}")
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
    print(json.dumps(record, ensure_ascii=False))


if __name__ == "__main__":
    main()
