"""Render the JCIM Application Note draft from the frozen paper runs.

The note reads the 2026-09-21 primary run (August 2026 reference prices), its
robustness, methods, crossover and what-if studies, and the manufacturing and
preparation records, so every computed number carries a file/key reference.
--check compares the committed note and its count record with a fresh render.
No calculation code runs here.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import build_submission_manuscript as paper  # noqa: E402
from scripts.paper_labels import CANDIDATE_LABELS  # noqa: E402
from scripts.paper_units import KG_PER_SHORT_TON, PER_LB_TO_PER_KG  # noqa: E402

DATE = "2026-09-09"
RUN_DATE = "2026-09-21"
RUN = f"submission-{RUN_DATE}"
ROBUSTNESS = f"robustness-{RUN_DATE}/decision_robustness.json"
METHODS = f"methods-{RUN_DATE}/methods_study.json"
EXAMPLE = "figures-note-2026-09-09/reference_example_ni_al2o3.json"
MARKET = f"{RUN}/table62_reproduction_{RUN_DATE}.json"
LIVE_FAMILIES = f"{RUN}/all_families_live_{RUN_DATE}.json"
LIVE_BASIS = f"{RUN}/live_basis_{RUN_DATE}.json"
REFERENCE_BASIS = f"{RUN}/reference_basis_{RUN_DATE}.json"
WHATIF = f"whatif-{RUN_DATE}/whatif_study.json"
PREPARATION = "manufacturing-2026-09-14/review_summary.json"
MANUFACTURING = "manufacturing-study-2026-09-15/manufacturing_study.json"
CROSSOVER_STUDY = f"price-crossovers-{RUN_DATE}/price_crossovers.json"
CROSSOVER_MECHANISMS = f"price-crossovers-{RUN_DATE}/crossover_mechanisms.json"
LITERATURE = "backend/data/manufacturing_literature.json"
POWER_FIELDS = ("ramp_power_kw", "hold_power_kw", "average_power_kw", "additional_power_kw", "measured_energy_kwh")
WORD_LIMIT = 5000
GRAPHICS = [
    {"figure": 1, "width": "double", "word_equivalent": 600},
    {"figure": 2, "width": "double", "word_equivalent": 600},
    {"figure": 3, "width": "double", "word_equivalent": 600},
    {"figure": 4, "width": "double", "word_equivalent": 600},
]


class NoteRun:
    """The frozen primary run with the integrity checks the note relies on."""

    ref = paper.PaperRun.ref

    def __init__(self, directory):
        self.directory = directory.resolve()
        self.prefix = self.directory.relative_to(paper.PAPER).as_posix()
        self.data, self.names = {}, {}
        for alias, stem in (("s", "paper_summary"), ("m", "reproduction_manifest"), ("a", "all_families")):
            name = f"{self.prefix}/{stem}_{RUN_DATE}.json"
            self.names[alias] = name
            self.data[name] = paper.load(paper.PAPER / name)
        self.summary, self.manifest = self.data[self.names["s"]], self.data[self.names["m"]]
        if self.manifest["status"] != "complete" or self.manifest["code_changed_during_run"]:
            raise ValueError("The note requires a complete run with unchanged calculation code")
        if self.manifest["price_basis"] != "reference" or self.summary["basis_month"] != self.manifest["basis_month"]:
            raise ValueError("The note uses the reference basis of one month")
        entries = [*self.manifest["outputs"], self.manifest["history"], self.manifest["support_history"]]
        for entry in entries:
            path = self.directory / entry["file"].replace("\\", "/")
            if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError(f"Frozen file changed: {entry['file']}")


def load_run():
    run = NoteRun(paper.PAPER / RUN)
    for name in (ROBUSTNESS, METHODS, EXAMPLE, MARKET, PREPARATION, MANUFACTURING, CROSSOVER_STUDY, CROSSOVER_MECHANISMS,
                 LIVE_FAMILIES, LIVE_BASIS, REFERENCE_BASIS, WHATIF):
        run.data[name] = paper.load(paper.PAPER / name)
    if run.data[ROBUSTNESS]["seed"] != run.manifest["seed"] or run.data[METHODS]["seed"] != run.manifest["seed"]:
        raise ValueError("Robustness study, methods supplement and primary run must share one seed")
    for study, key in ((CROSSOVER_STUDY, "baseline"), (CROSSOVER_STUDY, "monthly")):
        if not run.data[study]["inputs"][key]["path"].replace("\\", "/").startswith(f"docs/paper/{RUN}/"):
            raise ValueError("The crossover study does not use the primary run")
    if run.data[WHATIF]["inputs"]["reference_basis"] != f"docs/paper/{REFERENCE_BASIS}":
        raise ValueError("The what-if study does not use the primary run")
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
    pair_gap = derived(abs(retained[0] - retained[2]) * PER_LB_TO_PER_KG, ".2f", METHODS,
                       "normalization.example: |rows[0].cost - rows[2].cost| converted to USD/kg")

    def minus(text):
        """Typeset a leading negative sign as a minus sign; the binding comment is unchanged."""
        return "−" + text[1:] if text.startswith("-") else text

    def magnitude(text):
        """Drop the sign of a bound value; the binding comment is unchanged."""
        return text.lstrip("+-−")

    names = CANDIDATE_LABELS["ammonia-cracking"]
    co, ni_al, ru = (names[slug] for slug in ("co-mgo-la2o3", "ni-alumina-baseline", "ru-mgo-premium"))
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

    # Stored live quotations versus the reference month: the text names the ammonia-cracking change and its cause.
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

    def reliability(families):
        return next(row["scores"]["evidence"] for row in families[fam]["candidates"] if row["slug"] == "co-mgo-la2o3")

    if reliability(live_families) >= reliability(reference_families):
        raise ValueError("The cobalt candidate no longer loses price reliability under the live quotations")

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

    # Reference month and the later-published support values that enter at their latest verified month.
    months = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
    basis_month = run.summary["basis_month"]
    basis = f"{months[int(basis_month[5:7]) - 1]} {basis_month[:4]}<!-- {run.names['s']}:basis_month -->"
    if ammonia_live["reference_winner"] != reference_families[fam]["profiles"]["balanced"]["ranking"][0]:
        raise ValueError("Summary and screening leaders of ammonia cracking differ")

    # What-if analyses of the calculator (Figure 4a-c); the worked example is the same request as the nickel baseline.
    whatif = run.data[WHATIF]
    if abs(whatif["catalysts"]["ni"]["baseline"]["selling_price_per_lb"] - run.data[EXAMPLE]["step_method"]["estimated_price_per_lb"]) > 1e-9:
        raise ValueError("The worked example and the nickel what-if baseline differ")
    preparation = [row["selling_price_per_lb"] for row in whatif["preparation"]]
    if (min(preparation), max(preparation)) != (preparation[0], preparation[2]) or whatif["equal_cost"]["months_below_equal_cost"]:
        raise ValueError("The preparation range or the ruthenium equal-cost statement no longer holds")
    if len(preparation) != 5 or whatif["catalysts"]["ni"]["loading_wt_pct"] != 20 or run.data[EXAMPLE]["request"]["components"][0]["wt_pct"] != 20:
        raise ValueError("The text and the Figure 4 caption name five procedures and 20 wt% Ni/Al2O3")
    slopes = {}
    for key in ("ni", "ru"):
        rows = whatif["loading"][key]
        slope = (rows[-1]["selling_price_per_lb"] - rows[0]["selling_price_per_lb"]) * PER_LB_TO_PER_KG / (rows[-1]["loading_wt_pct"] - rows[0]["loading_wt_pct"])
        slopes[key] = derived(slope, ".2f" if slope < 10 else ",.0f", WHATIF, f"loading.{key}: selling-price change per wt% between the first and last loading, USD/kg")
    folds = {key: derived(whatif["order_size"][key][0]["selling_price_per_lb"] / whatif["order_size"][key][-1]["selling_price_per_lb"], ".1f", WHATIF,
                          f"order_size.{key}: selling price at the smallest order divided by that at the largest order") for key in ("ni", "ru")}
    equal_pct = derived(100 * whatif["equal_cost"]["equal_cost_over_reference"], ".2f", WHATIF, "equal_cost.equal_cost_over_reference as a percentage")

    def wi(key, spec=".2f", factor=PER_LB_TO_PER_KG):
        return kg(WHATIF, key, spec, factor)

    # Verification: every published line before the margin, for the two examples costed at nominal step rates.
    lines = [abs(row["dev_pct"]) for case in run.data[MARKET][:2] for row in case["rows"]
             if row["key"] not in ("margin_per_lb", "estimated_price_per_lb")]
    if max(lines) >= 0.5 or len(run.data[MARKET]) != 3:
        raise ValueError("A published line before the margin is no longer reproduced within rounding")
    premargin_dev = derived(max(lines), ".1f", MARKET, "[0] and [1] rows: largest |dev_pct| among the lines before the margin")
    if abs(run.data[MARKET][1]["rows"][-2]["dev_pct"]) < 20 or run.data[MARKET][1]["rows"][-2]["key"] != "margin_per_lb":
        raise ValueError("The Ni/Al2O3 difference is no longer confined to the margin line")

    ptc = run.summary["table62"][0]
    if format(ptc["comet_usd_per_lb"] * PER_LB_TO_PER_KG, ".2f") != format(ptc["published_usd_per_lb"] * PER_LB_TO_PER_KG, ".2f"):
        raise ValueError("COMET and the source no longer give the same Pt/C price to two decimals")

    # Library: family domains and the weight of cost in the balanced profile.
    domains = Counter(family["catalyst_domain"] for family in reference_families)
    if set(domains) != {"thermal", "electrocatalyst"} or domains["thermal"] != int(thermal):
        raise ValueError("The text names powder-catalyst and electrocatalyst families")
    electro = derived(domains["electrocatalyst"], "d", structure_source, "families with catalyst_domain electrocatalyst")
    balanced = [family["profiles"]["balanced"]["weights"] for family in reference_families]
    if any(max(weights, key=weights.get) != "economics" for weights in balanced):
        raise ValueError("Cost no longer carries the largest balanced weight in every family")
    weight_low = derived(min(w["economics"] for w in balanced), ".2f", structure_source, "smallest balanced weight of the cost score")
    weight_high = derived(max(w["economics"] for w in balanced), ".2f", structure_source, "largest balanced weight of the cost score")
    first_month = run.data[ROBUSTNESS]["summary"]["first_month"]
    first = f"{months[int(first_month[5:7]) - 1]} {first_month[:4]}<!-- {ROBUSTNESS}:summary.first_month -->"

    # What-if: the text ranks order size above loading above procedure for the nickel catalyst.
    if n_mass != "1":
        raise ValueError("The text states that one preparation record reports the recovered batch mass")
    ni_order, ni_loading = whatif["order_size"]["ni"], whatif["loading"]["ni"]
    ratios = (ni_order[0]["selling_price_per_lb"] / ni_order[-1]["selling_price_per_lb"],
              ni_loading[-1]["selling_price_per_lb"] / ni_loading[0]["selling_price_per_lb"], max(preparation) / min(preparation))
    if not ratios[0] > ratios[1] > ratios[2]:
        raise ValueError("Order size, loading and procedure no longer rank in the stated order for Ni/Al2O3")

    # Preparation-method crossovers: the library loadings of the two ammonia-cracking candidates and the
    # selling-price range of the five methods, which the Step Method makes identical for every candidate.
    assignment = whatif["route_assignment"]
    ra = next(index for index, row in enumerate(assignment["families"]) if row["family"] == "ammonia-cracking")
    ra_rows = assignment["families"][ra]["candidates"]
    ra_co, ra_ni = (next(index for index, row in enumerate(ra_rows) if row["slug"] == slug) for slug in ("co-mgo-la2o3", "ni-alumina-baseline"))
    co_loading = r(WHATIF, f"route_assignment.families[{ra}].candidates[{ra_co}].active_metal_wt_pct.Co", ".0f")
    ni_loading = r(WHATIF, f"route_assignment.families[{ra}].candidates[{ra_ni}].active_metal_wt_pct.Ni", ".0f")
    spreads = [max(v["selling_price_per_lb"] for v in row["by_template"].values()) - min(v["selling_price_per_lb"] for v in row["by_template"].values())
               for family in assignment["families"] for row in family["candidates"]]
    # Stored prices are rounded to 0.0001 USD/lb, so the ranges agree to that rounding.
    if max(spreads) - min(spreads) > 2e-4 or assignment["order_size_tons"] != run.data[EXAMPLE]["request"]["order_size_tons"]:
        raise ValueError("The text states one selling-price range of the five methods for every candidate at the base-case scale")
    method_spread = derived(spreads[0] * PER_LB_TO_PER_KG, ".2f", WHATIF,
                            "route_assignment: selling-price range over the five templates, identical for every candidate, USD/kg")
    pair = assignment["ammonia_cracking_pair"]
    dp_cell = pair["co_minus_ni_selling_price_per_lb"]["wet_impregnation_metal_oxide"]["deposition_precipitation_metal_oxide"]
    if pair["materials_gap_per_lb"] <= 0 or dp_cell >= 0 or pair["assignments_with_co_cheaper"] != 1:
        raise ValueError("The text names deposition-precipitation against incipient wetness as the one assignment where the cobalt catalyst is cheaper")
    method_gap = kg(WHATIF, "route_assignment.ammonia_cracking_pair.materials_gap_per_lb", ".2f")
    dp_over_iw = derived(-dp_cell * PER_LB_TO_PER_KG, ".2f", WHATIF,
                        "route_assignment.ammonia_cracking_pair: nickel catalyst by deposition-precipitation minus cobalt catalyst by incipient wetness, USD/kg")
    if ra_rows[ra_ni]["library_order_size_tons"] != assignment["order_size_tons"] or ra_rows[ra_co]["library_order_size_tons"] != assignment["order_size_tons"]:
        raise ValueError("The ammonia-cracking candidates are compared at their library production scale")

    return f"""# COMET: Catalyst Overall Manufacturing Estimation Tool

Authors, affiliations and corresponding-author contact: [to be supplied by the authors].

## Abstract

Early-stage catalyst cost estimates depend on operating inputs that synthesis reports seldom state and on metal prices that change, yet estimates rarely record either. COMET is desktop software that implements the Step Method, a published method that prices a synthesis as a sequence of industrial processing steps, and adds source-linked preparation records, batch costing from declared operating inputs, metal price histories, and ranking sensitivity tests. It reproduces the method's three published examples line by line; the largest price difference, {largest_residual}%, arises from the margin rule. Production scale changes the price of Ni/Al₂O₃ {folds['ni']}-fold, metal loading controls that of Ru/Al₂O₃, and recovered mass and treatment duration control laboratory batch cost. Over {rb('summary.months')} months of metal prices, the lowest-cost candidate changes in {cs('summary.monthly.cost_winner')} of {rb('summary.families')} reaction families. COMET estimates cost, not performance; coupling with performance-prediction models is planned.

Keywords: catalyst manufacturing cost; preparation provenance; sensitivity analysis; metal prices; software.

## Introduction

Catalyst manufacturing cost affects process economics alongside activity, selectivity, and stability. In biomass-conversion design reports, it amounted to 3–9% of installed equipment cost and shifted the minimum fuel selling price by up to ±10%, yet researchers outside catalyst companies have few resources for estimating it.<sup>1</sup>

Two published tools address this need. The Step Method estimates the purchase price of a precommercial catalyst by mapping its laboratory synthesis onto industrial processing steps with hourly costs and adding materials, overheads, and a scale-dependent margin; for three commercial catalysts, its estimates fell within ±20% of market prices.<sup>1</sup> CatCost built the method into spreadsheet and web tools and added dedicated-plant costing, spent-catalyst value, sensitivity analysis, and a weighted cost and life-cycle comparison of candidates.<sup>2</sup> Other studies costed individual synthesis routes<sup>3,4</sup> or propagated input uncertainty through techno-economic models.<sup>5</sup>

These tools take their inputs as given, which leaves three problems when candidates come from the literature. First, the inputs behind processing cost are seldom reported, and an estimate that fills such gaps silently cannot be audited. Second, metal prices move, so a cost order obtained on one date need not hold on another. Third, when cost joins other criteria, min–max normalized scores depend on the candidates included, so removing one can reorder the others.<sup>6,7</sup>

COMET records these conditions with every estimate: it implements the Step Method and adds source-linked preparation records and batch costing from declared inputs (first problem), metal price histories (second), and ranking sensitivity tests (third). We ask whether the implementation reproduces the published method, which inputs set the estimated cost at laboratory and production scale, and how often observed metal prices change the cost order and the recommended candidate.

## Implementation

### Software design

COMET is a desktop application (Figure 1): a formulation, preparation method, production scale, and price basis give an estimate that lists its sources, assumed inputs, and missing inputs; saved estimates can be repriced, compared, and ranked. A Python backend (FastAPI, SQLite) serves a React/TypeScript interface in English and Korean, packaged for Windows with Electron.

![Figure 1. COMET workflow. Input data and a price basis with its date give a cost estimate, its breakdown, and a candidate ranking; every stage writes its data sources, model assumptions, and reproduction information to an analysis record. Conceptual artwork used OpenAI's image-generation tool.](figures-note-2026-09-09/fig1_workflow_stack.png)

### Cost models

COMET has two cost models. Production-scale estimates follow the Step Method (Figure 2a).<sup>1</sup> Materials cost is Cₘ = Σ<sub>i</sub>w<sub>i</sub>c<sub>i</sub>, with mass fraction w<sub>i</sub> and price c<sub>i</sub> of component i. Processing cost is Cₚ = 24TIH/M, where H is the summed hourly cost of the selected processing steps (2017 basis), I a producer-price-index factor, T the campaign duration in days, and M the production scale (kg of catalyst per order), which sets equipment size, step rates, and T. The selling price is P = (Cₘ + Cₚ)(1 + g)(1 + s)/(1 − m), with general and administrative (G&A) fraction g, sales, administrative, research, and distribution (SARD) fraction s, and margin m from the published scale correlation. P is the price a buyer would pay; cost below means P per kilogram. COMET provides {r('s', 'manufacturing.20.template_count')} editable preparation methods and flags substituted or uncosted steps.

Laboratory batch costing replaces these terms with declared purchases and operating inputs: electricity, equipment occupancy, attended labor, gases, and transfers between operations (eqs S1–S6). The sum is divided by the recovered dry mass before overheads and margin are applied, and a missing required input stops the calculation instead of taking a default.

![Figure 2. Cost estimation. (a) Step Method. (b) Deviations of the COMET and published estimates from the market prices reported by Baddour et al.<sup>1</sup>; negative values denote estimates below market. (c) Shares of the selling price, with prices in USD/kg, for the lowest-cost candidate of each powder-catalyst family. Gray combines G&A, SARD, margin, and assumed route allowances for quality assurance, activation, and additional overhead. USY, ultrastable zeolite Y; FCC, fluid catalytic cracking; SCR, selective catalytic reduction; RWGS, reverse water–gas shift. Conceptual artwork in (a) used OpenAI's image-generation tool.](figures-note-2026-09-09/fig2_cost_model.png)

### Library and preparation records

The library holds {rb('summary.candidates')} formulations in {rb('summary.families')} reaction families ({thermal} of powder catalysts, {electro} of electrocatalysts), each with a composition, preparation method, production scale, and route and performance scores. Compositions follow a literature catalyst architecture for {r('s', 'screening_basis_counts.literature_architecture_proxy')} candidates, engineering baselines for {r('s', 'screening_basis_counts.engineering_proxy')}, and vendor or market data for {other_bases}; all are screening models, not verified recipes, and their estimates add assumed route allowances (Figure 2c). Each candidate is priced at its library loading, taken from the cited source where reported and otherwise assumed, not at a common loading (Table S7). Preparation records link candidates to what their sources report: an audit verified {r(PREPARATION, 'crossref_dois')} digital object identifiers (DOIs) with Crossref and transcribed {r(PREPARATION, 'profiles')} specimen-specific records from {r(PREPARATION, 'primary_sources')} primary sources for {r(PREPARATION, 'candidates_with_profile')} candidates, flagging composition or source discrepancies in {r(PREPARATION, 'source_mismatches')}. Each value keeps its DOI and locator, unreported conditions stay blank, and a record documents a source without validating the library formulation (Section S6).

### Prices and ranking

The reference basis stores monthly averages from the International Monetary Fund (IMF) Primary Commodity Price System<sup>10</sup> and Johnson Matthey<sup>8</sup> for metals and U.S. import unit values for supports,<sup>11</sup> each with source, date, and retrieval time (Section S5). Results use the {basis} reference basis; the same series give {rb('summary.months')} monthly price states from {first}. The live basis uses current quotations such as Johnson Matthey's<sup>8</sup> and Westmetall's.<sup>9</sup> A price-reliability score averages source grades by share of materials cost; it rates price provenance, not estimate accuracy.

Within a family, candidates are ranked by a weighted sum of four 0–100 scores: cost, price reliability, route, and performance. The cost score is min–max normalized from 100 (least expensive) to 0 (most expensive); route and performance scores are assigned from the literature. The balanced profile used below gives cost the largest weight ({weight_low}–{weight_high}).

## Results and Discussion

### Verification

The source of the Step Method tabulates three demonstration cases (Pt/C, Ni/Al₂O₃, and a fluid catalytic cracking (FCC) catalyst) with every intermediate line and a market price,<sup>1</sup> and their inputs were entered as published. For Pt/C and Ni/Al₂O₃, COMET reproduces every line before the margin within {premargin_dev}%, the rounding of the published table (Table S1), and the Pt/C price matches ({kg('s', 'table62[0].comet_usd_per_lb', '.2f')} USD/kg, platinum value excluded). The Ni/Al₂O₃ price is {kg('s', 'table62[1].comet_usd_per_lb', '.2f')} against {kg('s', 'table62[1].published_usd_per_lb', '.2f')} USD/kg ({minus(r('s', 'table62[1].residual_pct', '+.2f'))}%), and the whole difference lies in the margin: the table applies {r(MARKET, '[1].margin.table_footnote_pct_of_premargin', '.0f')}% of pre-margin cost, whereas the scale correlation of the same source, which COMET applies, gives {r(MARKET, '[1].margin.comet_pct_of_premargin', '.0f')}%. For FCC, costed at the effective production rate the source states ({kg('s', 'table62[2].effective_rate_ton_per_day', ',.1f', KG_PER_SHORT_TON)} kg/day), COMET gives {kg('s', 'table62[2].comet_usd_per_lb', '.2f')} against {kg('s', 'table62[2].published_usd_per_lb', '.2f')} USD/kg ({r('s', 'table62[2].residual_pct', '+.2f')}%). Against the market prices of the source, the estimates deviate by {minus(mk('[0].market.comet_vs_market_pct', '.1f'))}%, {minus(mk('[1].market.comet_vs_market_pct', '.1f'))}%, and {minus(fcc_market_pct)}% (Figure 2b), within the ±20% reported for the method. These results verify the implementation, not new estimates: the market comparison covers three catalysts at mid-2017 prices.

### Production-scale cost structure

Figure 2c divides the selling price of the lowest-cost candidate in each of the {thermal} powder-catalyst families. Materials exceed half of the price in only {materials_majority} families, processing exceeds materials in {processing_over}, and G&A, SARD, margin, and route allowances take {other_low}–{other_high}%. Most estimates thus depend on processing assumptions as much as on materials prices; the Step Method standardizes them, whereas a laboratory preparation must supply its own.

### Laboratory batch costs

Published preparations rarely report the operating inputs batch costing needs. In the {r(PREPARATION, 'profiles')} preparation records, all {n_segments} heating segments state a target temperature, {n_hold} a hold time, and {n_ramp} a ramp rate, but none the electrical input, and only {n_mass} record reports the recovered batch mass. Figure 3 costs an illustrative {sn('[0].value', '.3f')} kg batch from declared, assumed inputs (Tables S2–S5). Operations account for {r(MANUFACTURING, 'baseline.summary.processing_pct', '.1f')}% of the baseline price of {r(MANUFACTURING, 'baseline.summary.estimated_price_per_kg', ',.2f')} USD/kg (Figure 3b). Duration outweighs power: calcination holds of {sn('[4].low', '.0f')}–{sn('[4].high', '.0f')} h span {sn('[4].low_usd_kg', ',.2f')}–{sn('[4].high_usd_kg', ',.2f')} USD/kg, whereas hold powers of {sn('[5].low', '.1f')}–{sn('[5].high', '.1f')} kW span only {sn('[5].low_usd_kg', ',.2f')}–{sn('[5].high_usd_kg', ',.2f')} USD/kg (Table S6). Recovered mass matters most because every cost is divided by it: halving the dry output doubles the price to {sn('[0].low_usd_kg', ',.2f')} USD/kg (Figure 3c).

![Figure 3. Manufacturing conditions. (a) Illustrative preparation sequence. (b) Operating contributions per kg of dry product, excluding purchases, overheads, and margin. (c) Selling price versus calcination hold for 0.015, 0.030, and 0.045 kg dry outputs; the point marks the baseline. Quantities, prices, and operating inputs are hypothetical. Panel (a) artwork used OpenAI's image-generation tool.](manufacturing-study-2026-09-15/figures/fig_manufacturing.png)

### Production-scale what-if analyses

For industrial production, the Step Method derives operating inputs from the preparation method and production scale, so the user chooses composition, method, and scale; each was varied in turn for two alumina-supported catalysts prepared by incipient wetness impregnation (Figure 4a–c; Table S8). The base case, {r(EXAMPLE, 'request.components[0].wt_pct', '.0f')} wt% Ni/Al₂O₃ at {kg(EXAMPLE, 'request.order_size_tons', ',.1f', KG_PER_SHORT_TON)} kg, sells for {kg(EXAMPLE, 'step_method.estimated_price_per_lb', '.2f')} USD/kg. Raising the nickel loading from {r(WHATIF, 'loading.ni[0].loading_wt_pct', '.0f')} to {r(WHATIF, 'loading.ni[5].loading_wt_pct', '.0f')} wt% raises the price from {wi('loading.ni[0].selling_price_per_lb')} to {wi('loading.ni[5].selling_price_per_lb')} USD/kg ({slopes['ni']} USD/kg per wt%), whereas each wt% of ruthenium adds {slopes['ru']} USD/kg. Production scale acts in the opposite direction: from {wi('order_size.ni[0].order_size_tons', ',.1f', KG_PER_SHORT_TON)} to {wi('order_size.ni[10].order_size_tons', ',.1f', KG_PER_SHORT_TON)} kg, the Ni/Al₂O₃ price falls {folds['ni']}-fold, from {wi('order_size.ni[0].selling_price_per_lb')} to {wi('order_size.ni[10].selling_price_per_lb')} USD/kg, because larger scales use larger equipment and carry lower margins; the price of {r(WHATIF, 'catalysts.ru.loading_wt_pct', '.0f')} wt% Ru/Al₂O₃ falls only {folds['ru']}-fold because materials dominate it. Five preparation methods for the same Ni/Al₂O₃ composition span {wi('preparation[0].selling_price_per_lb')}–{wi('preparation[2].selling_price_per_lb')} USD/kg. For the base-metal catalyst, production scale outweighs loading, and loading outweighs preparation method; for the precious-metal catalyst, loading outweighs both.

### Observed price crossovers

Metal prices change without any user decision, so every family was repriced at all {cs(monthly + '.observations')} monthly price states, other inputs fixed. The lowest-cost candidate changes in {cs('summary.monthly.cost_winner')} of {cs('summary.monthly.families')} families (Figure 4e). In ammonia cracking, {co_loading} wt% {co} is the least expensive candidate in {cs(monthly + '.winner_counts.cost_winner.co-mgo-la2o3')} months and {ni_loading} wt% {ni_al} in {cs(monthly + '.winner_counts.cost_winner.ni-alumina-baseline')} (Figure 4d). From September to October 2025, cobalt rose from {kg(CROSSOVER_MECHANISMS, 'cases[0].metal_effects.Co.price_before', '.2f')} to {kg(CROSSOVER_MECHANISMS, 'cases[0].metal_effects.Co.price_after', '.2f')} USD/kg while nickel hardly moved, and {ni_al} ({kg(CROSSOVER_MECHANISMS, 'cases[0].costs_after.ni-alumina-baseline', '.2f')} USD/kg) became cheaper than {co} ({kg(CROSSOVER_MECHANISMS, 'cases[0].costs_after.co-mgo-la2o3', '.2f')} USD/kg). Such reversals recur because the monthly states lie near the equal-cost line in the nickel–cobalt price plane (Figure S5c). A large cost gap is insensitive: {r(WHATIF, 'catalysts.ru.loading_wt_pct', '.0f')} wt% Ru/Al₂O₃ ({wi('catalysts.ru.baseline.selling_price_per_lb', ',.2f')} USD/kg) would match the Ni/Al₂O₃ base case only at {equal_pct}% of the {basis} ruthenium price, below all {r(WHATIF, 'equal_cost.ru_history_months')} months. A cost order between similar-cost candidates should therefore carry its price date.

![Figure 4. What-if analyses and observed-price crossovers. (a) Selling price versus metal loading for Ni/Al₂O₃ and Ru/Al₂O₃ prepared by incipient wetness impregnation; labels give the change per wt%. (b) Selling price versus production scale; dotted lines separate small, medium, and large equipment. (c) Selling price of 20 wt% Ni/Al₂O₃ for five preparation methods, itemized as materials, processing, G&A, SARD, and margin. (d) Costs of the two ammonia-cracking candidates that attain the lowest cost under {cs(monthly + '.observations')} monthly price states, at their library loadings. (e) Lowest-cost candidate of each month in the {cs('summary.monthly.cost_winner')} families where it changes; candidate names carry the color of their months. Ni/CeO₂ denotes Ni/CeO₂ single sites; the electrocatalyst families are compared on powder cost (Table S7). (f) Selling price of {co} minus that of {ni_al} (USD/kg) at {kg(WHATIF, 'route_assignment.order_size_tons', ',.1f', KG_PER_SHORT_TON)} kg for every pair of preparation methods; the color marks the less expensive candidate. IW, incipient wetness; WI, wet impregnation; DP, deposition–precipitation; CP, co-precipitation; SG, sol–gel.](figures-note-2026-09-09/fig4_decision_diagnostics.png)

### Preparation-method crossovers

The preparation method can also reverse a cost order. Step Method processing cost depends on the operation sequence and the scale, not on the composition, so at {kg(WHATIF, 'route_assignment.order_size_tons', ',.1f', KG_PER_SHORT_TON)} kg the five methods shift every supported-metal candidate by up to {method_spread} USD/kg. Where materials costs differ by less, the method decides: {ni_al} costs {method_gap} USD/kg less in materials than {co}, but by deposition–precipitation it costs {dp_over_iw} USD/kg more than the cobalt catalyst by incipient wetness (Figure 4f). Priced under each method, the {r(WHATIF, 'route_assignment.summary.candidates')} supported-metal candidates of {r(WHATIF, 'route_assignment.summary.families')} families change the lowest-cost candidate in {r(WHATIF, 'route_assignment.summary.lowest_cost_depends_on_template')} (Table S9). Equal activity across methods is not assumed.

### Recommendation sensitivity

A change in cost order need not change the recommendation. In ammonia cracking, the balanced-profile leader remains {co} in all {cs(monthly + '.winner_counts.app_winner.co-mgo-la2o3')} months: the cost score is normalized within the family, and {ru}, at {kg(METHODS, 'normalization.example.removed_cost', ',.2f')} USD/kg, fixes the expensive end of the scale, so the two cost leaders keep cost scores of at least {compressed} and the other scores decide their order. Removing {ru} contracts the scale, magnifies the {pair_gap} USD/kg difference between the two, and reverses their ranking, a known property of min–max normalization<sup>6,7</sup> that retaining the original range prevents. Over all families, removing one non-leading candidate changes the leader in {rb('summary.candidate_removal_winner_changes')} of {rb('summary.candidate_removal_cases')} tests (Figure S6). Live quotations collected on {live_date} change the leader in {r('s', 'live_reference_comparison.changed_by_profile.balanced')} of {cs('summary.monthly.families')} families, partly because cobalt, lacking a live quotation, falls back to an annual price with a lower reliability grade (Table S10). A recommendation should therefore carry its candidate set, price basis, and date.

### Limitations

COMET estimates manufacturing cost only, not activity, selectivity, or lifetime, so a more expensive catalyst can still be more economical per unit of product;<sup>12</sup> the route and performance scores are literature-based screening judgments, not measured or predicted activity. Accuracy against industrial prices is not established, because no public price matched a library formulation in grade, scale, date, and delivery boundary (Table S12).

## Conclusions

COMET implements the Step Method, records with each estimate its input sources, price date, and candidate set, and reproduces the three published examples line by line; the largest price difference, {largest_residual}%, arises from the margin rule. Production scale sets the estimated cost of a base-metal catalyst, metal loading that of a precious-metal catalyst, and treatment duration and recovered mass that of a laboratory batch, which only {n_mass} of {r(PREPARATION, 'profiles')} preparation records reports. Observed metal prices changed the lowest-cost candidate in {cs('summary.monthly.cost_winner')} of {cs('summary.monthly.families')} families, the preparation method could change it in {r(WHATIF, 'route_assignment.summary.lowest_cost_depends_on_template')} of {r(WHATIF, 'route_assignment.summary.families')}, and recommendations changed with the candidate set and the price basis. Cost comparisons should therefore state composition, preparation method, production scale, assumed operating inputs, price basis and date, and candidate set. Because COMET does not evaluate performance, we plan to couple it with performance-prediction models, to compare cost per unit of product, and to validate it against industrial prices under matched conditions.

## Supporting Information

Calculation methods, verification, sensitivity analyses, price histories, candidate prices and loadings, what-if and crossover data, preparation and price evidence, application views (PDF); data and reproduction files (ZIP).

## Data and Software Availability

COMET version {r('m', 'project_version')} uses the PolyForm Noncommercial License 1.0.0; commercial use requires a separate license. [Authors must state how a commercial license can be obtained.] Repository: https://github.com/hyunjin-kor/COMET. Concept DOI: 10.5281/zenodo.21451931. [Authors must confirm this version's access and the analysis files' distribution scope before submission.] Analysis inputs, outputs, checksums, and reproduction instructions accompany the study; third-party data retain their source terms.

## Acknowledgments

OpenAI Codex and GPT tools and Anthropic Claude assisted software development, analysis scripts, and manuscript drafting. OpenAI's image-generation tool produced conceptual artwork in Figures 1–3, and Google Gemini produced conceptual artwork in Supporting Information Figures S1 and S8, in September 2026. The authors reviewed all AI-assisted content and are responsible for it. [Authors must confirm the tools, versions, and periods of AI assistance.] Funding: [author statement required].

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
8. Johnson Matthey. PGM Prices and Trading. https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management (accessed September 21, 2026).
9. Westmetall. Market Data: Prices and LME Stocks. https://www.westmetall.com/en/markdaten.php (accessed September 21, 2026).
10. International Monetary Fund. Primary Commodity Price System (PCPS), SDMX 2.1 data service. https://api.imf.org/external/sdmx/2.1/dataflow/IMF.RES/PCPS (accessed September 21, 2026).
11. United Nations. UN Comtrade Database. https://comtradeplus.un.org (accessed September 21, 2026).
12. Mendoza Suarez, F.; Tatarchuk, B. Comparative economic analysis of batch vs. continuous manufacturing in catalytic heterogeneous processes: impact of catalyst activity maintenance and materials costs on total costs of manufacturing in the production of fine chemicals and pharmaceuticals. *Journal of Flow Chemistry* **2025**, *15* (1), 21–38. [DOI](https://doi.org/10.1007/s41981-024-00342-z).
"""


def visible_words(text):
    """Words as a word processor counts them: every token of the typeset text delimited by white space or a dash, symbols included (checked against Word's statistic).

    Provenance comments and sub/superscript markup are not text, and a superscript citation
    number belongs to the word it follows.
    """
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<sup>[\d,–-]+</sup>", "", text)
    text = re.sub(r"</?(?:sub|sup)>", "", text)
    text = re.sub(r"^#+ ", "", text, flags=re.M)
    return len([token for token in re.split(r"[\s–—]+", text) if token])


def counts(text, run):
    abstract = text.split("## Abstract\n\n", 1)[1].split("\n\nKeywords:", 1)[0]
    body = text.split("## Introduction", 1)[1].split("## References", 1)[0]
    body = re.sub(r"^!\[.*$", "", body, flags=re.M)
    figures = len(re.findall(r"^!\[", text, flags=re.M))
    if figures != len(GRAPHICS):
        raise ValueError("Figure count differs from the declared graphics budget")
    graphics = sum(g["word_equivalent"] for g in GRAPHICS)
    abstract_words = visible_words(abstract)
    body_words = visible_words("## Introduction" + body)
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
        "count_note": "Whitespace-delimited words of the typeset abstract and of the text from Introduction through Competing interests, including headings and placeholders; provenance comments and sub/superscript markup are not counted, and a superscript citation number belongs to the preceding word. Figure captions and references are excluded; graphics add 300/600 word equivalents for single/double-column figures.",
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
