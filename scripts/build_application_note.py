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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import build_submission_manuscript as paper  # noqa: E402
from scripts.paper_units import KG_PER_SHORT_TON, PER_LB_TO_PER_KG  # noqa: E402

DATE = "2026-09-09"
RUN_DATE = "2026-09-08"
ROBUSTNESS = "robustness-2026-09-08/decision_robustness.json"
METHODS = "methods-2026-09-09/methods_study.json"
EXAMPLE = "figures-note-2026-09-09/screen_result_ni_al2o3.json"
MARKET = "submission-2026-09-08/table62_reproduction_2026-09-08.json"
PREPARATION = "manufacturing-2026-09-14/review_summary.json"
MANUFACTURING = "manufacturing-study-2026-09-15/manufacturing_study.json"
CROSSOVER_STUDY = "price-crossovers-2026-09-13/price_crossovers.json"
CROSSOVER_MECHANISMS = "price-crossovers-2026-09-13/crossover_mechanisms.json"
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
    for name in (ROBUSTNESS, METHODS, EXAMPLE, MARKET, PREPARATION, MANUFACTURING, CROSSOVER_STUDY, CROSSOVER_MECHANISMS):
        run.data[name] = paper.load(paper.PAPER / name)
    if run.data[ROBUSTNESS]["seed"] != run.manifest["seed"] or run.data[METHODS]["seed"] != run.manifest["seed"]:
        raise ValueError("Robustness study, methods supplement and primary run must share one seed")
    return run


def note(run):
    r = run.ref
    run.publication_conversions = []

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
    full_range = (max(*retained, example["removed_cost"]) - min(retained)) * PER_LB_TO_PER_KG
    retained_range = (max(retained) - min(retained)) * PER_LB_TO_PER_KG
    pair_gap = abs(retained[0] - retained[2]) * PER_LB_TO_PER_KG

    return f"""# COMET: Catalyst Overall Manufacturing Estimation Tool

Authors, affiliations and corresponding-author contact: [to be supplied by the authors].

## Abstract

COMET (Catalyst Overall Manufacturing Estimation Tool) integrates manufacturing cost estimation, preparation records, price management, and ranking for {rb('summary.candidates')} catalyst formulations in {rb('summary.families')} reaction families. Source-linked records distinguish published conditions from user modifications, while batch calculations trace purchases, utilities, labor, equipment occupancy, and intermediate transfers to cost per kilogram of dry product. Saved inputs support sensitivity analysis and reproducible price updates; published examples verify the Step Method implementation, an illustrative batch demonstrates the effects of treatment duration and recovered mass, and observed metal-price changes are shown to reverse cost ordering without changing a balanced recommendation. Comparisons depend on declared assumptions, and independent industrial validation remains necessary.

Keywords: catalyst manufacturing cost; preparation provenance; sensitivity analysis; multicriteria decision analysis; software.

## Introduction

Catalyst selection requires evaluating manufacturing cost alongside performance and environmental impacts. The Step Method estimates precommercial catalyst selling prices from materials, unit operations, overheads, and margin.<sup>1</sup> CatCost integrated cost and environmental assessment and demonstrated the effects of synthesis methods and scale.<sup>2</sup> Individual route studies provide further cost analyses,<sup>3,4</sup> while BioSTEAM integrates process design and techno-economic analysis under uncertainty.<sup>5</sup>

Applying such estimates requires consistent price dates, process boundaries, and functional units. Laboratory preparation adds further distinctions: furnace temperature does not specify electrical consumption, precursor charge does not establish recovered mass, and elapsed treatment time differs from attended labor. COMET connects preparation evidence and operating inputs to cost contributions, then evaluates sensitivity to manufacturing conditions, prices, and ranking assumptions.

## Software implementation

Figure 1 links formulation, price selection, calculation, and ranking. Users enter or load a formulation, edit its route and scale, and inspect costs alongside sources and missing inputs. Saved estimates support recalculation and comparison; JavaScript Object Notation (JSON) and comma-separated values (CSV) exports retain results and provenance. Analysis records preserve boundaries, checksums, software versions, and seeds.

![Figure 1. COMET workflow. Sources and assumptions accompany formulation, price selection, cost estimation, and ranking. Conceptual artwork used OpenAI's image-generation tool.](figures-note-2026-09-09/fig1_workflow_stack.png)

SQLite stores prices and estimates. The bilingual React/TypeScript interface connects to FastAPI; Electron and PyInstaller package Windows builds. Windows workflows and Linux backend/interface builds were tested. Stored or user-supplied prices enable offline calculation.

The preparation audit covers {r(PREPARATION, 'candidates')} candidates and flags {r(PREPARATION, 'source_mismatches')} composition/source discrepancies. Crossref verified {r(PREPARATION, 'crossref_dois')} digital object identifiers (DOIs); public Methods and supplements yielded {r(PREPARATION, 'profiles')} specimen-specific records from {r(PREPARATION, 'primary_sources')} sources, linked to {r(PREPARATION, 'candidates_with_profile')} candidates. Records preserve operations, temperature programs, atmosphere, pressure, mixing, and separation conditions. Numeric inputs retain their DOI, locator, and original value; edits are identified separately. Unreported conditions remain blank. Imports distinguish powder preparation, activation, and electrode fabrication. A linked specimen does not validate the catalog formulation or establish complete manufacturing costs; candidate assessments and unresolved inputs are provided in Supporting Information.

## Cost estimation and environmental screening

In Figure 2(a), composition-based materials cost is Cₘ = Σ<sub>i</sub>w<sub>i</sub>c<sub>i</sub>, with component mass fraction w<sub>i</sub> and price c<sub>i</sub> per kg. Alternatively, precursor requirements are $w/(f\\,p\\,y)$ kg per kg of catalyst: $w$ is the product component fraction, $f$ its fraction in pure precursor, $p$ purity, and $y$ retention. Quantities, losses, and purchase prices require explicit inputs.

Step Method processing cost is Cₚ = 24TIH/M: campaign duration T in days, price-index factor I, summed hourly operation costs H, and catalyst mass M in kg. The {r('s', 'manufacturing.20.template_count')} editable procedures retain repeated operations. Order size determines scale, production rate, and cleaning allowance; documented effective rates can replace nominal rates. Hourly rates use the 2017 equipment basis adjusted by a chemical-manufacturing producer price index. Substituted and uncosted operations are identified. Selling price is P = (Cₘ + Cₚ)(1 + g)(1 + s)/(1 − m), with general and administrative (G&A) fraction g, sales, administrative, research, and distribution (SARD) fraction s, and margin m from the published order-size correlation. Separate capital and annual operating estimates are not automatically added.

Figure 2(b) shows the lowest-cost screening candidate in each of 23 thermal families at May 2026 prices, including assumed route allowances. Bars total 100%, follow materials share, and include absolute prices; comparisons across reactions do not establish equivalent performance. For a saved 20 wt% Ni/Al₂O₃ scenario at {kg(EXAMPLE, 'request.order_size_tons', ',.1f', KG_PER_SHORT_TON)} kg, selling price is {kg(EXAMPLE, 'step_method.estimated_price_per_lb', '.2f')} USD/kg, including nickel and processing contributions of {kg(EXAMPLE, 'materials.components[0].cost_per_lb_cat', '.2f')} and {kg(EXAMPLE, 'step_method.processing_cost_per_lb', '.2f')} USD/kg.

![Figure 2. Cost estimation. (a) Step Method. (b) Selling-price shares and prices (USD/kg). Gray includes G&A, SARD, margin, and assumed route allowances for quality assurance, activation, and additional overhead. (c) Deviations from market prices reported by Baddour et al.<sup>1</sup>; negative values denote lower estimates. SCR, selective catalytic reduction; RWGS, reverse water–gas shift. Conceptual artwork in (a) used OpenAI's image-generation tool.](figures-note-2026-09-09/fig2_cost_model.png)

Batch costing instead replaces composition-based materials and Step Method processing with purchases and operating inputs. Electricity uses measured kWh or mean power multiplied by ramp/hold time; equipment occupancy, attended labor, and gases are costed separately. Gas duration can follow the operation or its holds; flow and price require matching volume reference conditions. Intermediate charges follow successive used/recovered mass fractions, homogeneous-solution volume fractions, or explicit whole-batch allocation. Unknown recovery blocks proportional allocation. Final costs are divided by dry output mass before overheads and explicit margin. Required missing inputs block calculation; temperature alone predicts neither power nor yield. Repeated batches assume no scale economy.

Electrode estimates use catalyst, ionomer, membrane, and substrate costs per area, with optional manufacturing scenarios. Electrode records cannot use powder batch costing. Environmental screening uses cradle-to-gate metal factors per kg.<sup>6</sup> Calculator results cover materials; benchmark analyses additionally model route energy. Compound mappings are approximations, and mass coverage does not establish a complete life-cycle inventory.

## Manufacturing conditions and cost contributions

Figure 3 demonstrates an illustrative 0.030 kg dry batch with impregnation, drying, calcination, and reduction. All operating and price inputs are declared assumptions, not measurements of a particular catalyst. At the baseline, selling price is {r(MANUFACTURING, 'baseline.summary.estimated_price_per_kg', ',.2f')} USD/kg. Panel (b) separates each operation's electricity, equipment, labor, and gas contributions. Extending calcination by one hour adds {r(MANUFACTURING, 'marginal_calcination_hour_usd_kg', '.2f')} USD/kg to selling price: additional electricity and equipment occupancy propagate through overheads and margin. Labor remains fixed because attendance is entered independently.

Panel (c) varies calcination time and recovered dry mass while holding other batch inputs fixed. Lower recovery increases cost per kilogram without increasing incurred batch expenditure; it does not represent a tested synthesis yield or scale-up relationship. Endpoint tests cover eight inputs. A seeded {r(MANUFACTURING, 'monte_carlo.n_simulations', ',')} trial analysis varies dry output, calcination hold, hold power, and electricity tariff within independent uniform bounds. These bounds describe scenarios, not confidence intervals. Independent arithmetic and application programming interface (API) calculations agree; inputs, samples, and checksums accompany the study.

![Figure 3. Manufacturing conditions. (a) Illustrative preparation sequence. (b) Operating contributions per kg of dry product, excluding purchases, overheads, and margin. (c) Selling price versus calcination hold for 0.015, 0.030, and 0.045 kg dry outputs; the point marks the baseline. Quantities, prices, and operating inputs are hypothetical. Panel (a) artwork used OpenAI's image-generation tool.](manufacturing-study-2026-09-15/figures/fig_manufacturing.png)

## Prices and ranking sensitivity

Current quotations include Johnson Matthey platinum and palladium prices<sup>7</sup> and Westmetall copper and aluminum settlements.<sup>8</sup> Historical inputs use International Monetary Fund (IMF) Primary Commodity Price System data<sup>9</sup> and monthly Johnson Matthey averages. Support proxies use U.S. import unit values<sup>10</sup> for {r('meta', 'support_series')} commodity codes and {r('meta', 'support_observations')} verified observations. Retrieval times and source hierarchies are retained. Supporting Information plots the unsmoothed metal histories; these are observations, not forecasts. Price-source grades are weighted by materials-cost contributions and assess pricing provenance, not preparation or performance verification.

The screening library includes {r('s', 'screening_basis_counts.literature_architecture_proxy')} literature-architecture and {r('s', 'screening_basis_counts.engineering_proxy')} engineering proxies. Rankings combine cost, price-data reliability, route, and performance. Within each family, cost scores span 100 for the least expensive candidate to 0 for the most expensive; equal costs receive 100. Route and performance scores are author-assigned screening judgments. Baseline rankings use May 2026 prices, balanced weights, and the full candidate set; lower cost resolves ties. Incomplete electrode cases use powder costs.

Observed prices can reverse cost ordering. Figure 4(a) recalculates the ammonia-cracking candidates under {cs(monthly + '.observations')} monthly metal-price states with formulations, order sizes, route assumptions, and support prices fixed: Co/MgO-La₂O₃ is least expensive in {cs(monthly + '.winner_counts.cost_winner.co-mgo-la2o3')} states and Ni/Al₂O₃ in {cs(monthly + '.winner_counts.cost_winner.ni-alumina-baseline')}, while the balanced-weight recommendation does not change. Across all {cs('summary.monthly.families')} families, the lowest-cost candidate changes in {cs('summary.monthly.cost_winner')} within this window. Between September and October 2025, cobalt rose from {kg(CROSSOVER_MECHANISMS, 'cases[0].metal_effects.Co.price_before', '.2f')} to {kg(CROSSOVER_MECHANISMS, 'cases[0].metal_effects.Co.price_after', '.2f')} USD/kg with nickel nearly unchanged, and the Ni/Al₂O₃ cost of {kg(CROSSOVER_MECHANISMS, 'cases[0].costs_after.ni-alumina-baseline', '.2f')} USD/kg fell below the Co/MgO-La₂O₃ cost of {kg(CROSSOVER_MECHANISMS, 'cases[0].costs_after.co-mgo-la2o3', '.2f')} USD/kg. Figure 4(b) shows the conditional equal-cost boundary in the nickel–cobalt price plane; monthly states cluster near it, so modest cobalt movements change the cost leader. These are model comparisons under fixed formulations, not performance comparisons, and a cost crossover is distinct from a change in the composite recommendation.

The combined analysis evaluates {rb('summary.months')} monthly price datasets and {rb('summary.weight_points["0.05"]', ',')} weight combinations, giving {rb('summary.joint_scenarios_all_families["0.05"]', ',')} scenarios across families. Figure 4(c) separates first-rank frequencies of the baseline candidate, its most frequent alternative, and others. The median baseline frequency is {rb('summary.reference_winner_joint_share_median_pct', '.2f')}%. These frequencies measure scenario stability, not future probabilities. Candidate removal changes the leader in {rb('summary.candidate_removal_winner_changes')} of {rb('summary.candidate_removal_cases')} tests; {rb('summary.rubric_robust_family_counts["5"]')} families retain their leader under 5-point route/performance-score changes.

Saved batch comparisons share prices only through explicit specification identifiers with matching units and gas reference conditions. Common operating assumptions include electricity, labor, overheads, and margin. Quantities, sequences, and yields remain case-specific; original records are preserved.

## Verification and application

Three published examples verify Step Method calculations without adjusting materials totals, sequences, or order sizes. COMET estimates {kg('s', 'table62[0].comet_usd_per_lb', '.4f')} USD/kg for Pt/C versus {kg('s', 'table62[0].published_usd_per_lb', '.2f')} USD/kg reported; both exclude platinum metal value. For Ni/Al₂O₃, {kg('s', 'table62[1].comet_usd_per_lb', '.4f')} versus {kg('s', 'table62[1].published_usd_per_lb', '.2f')} USD/kg differs by {r('s', 'table62[1].residual_pct', '+.2f')}% because COMET uses the published margin correlation instead of the table's fixed margin. For ultrastable zeolite Y in fluid catalytic cracking, {kg('s', 'table62[2].comet_usd_per_lb', '.4f')} versus {kg('s', 'table62[2].published_usd_per_lb', '.2f')} USD/kg differs by {r('s', 'table62[2].residual_pct', '+.2f')}% at the reported effective rate of {kg('s', 'table62[2].effective_rate_ton_per_day', ',.1f', KG_PER_SHORT_TON)} kg/day. Intermediate processing and overhead calculations agree at the reported precision.

Figure 2(c) compares estimates with the same source's market prices using 100 × (estimate − market price)/market price.<sup>1</sup> COMET deviations are {mk('[0].market.comet_vs_market_pct', '.1f')}% for Pt/C and {mk('[1].market.comet_vs_market_pct', '.1f')}% for Ni/Al₂O₃. The FCC estimate is {kg(MARKET, '[2].with_published_rate.estimated_price_per_lb', '.4f')} USD/kg versus {kg(MARKET, '[2].market.market_price_per_lb', '.2f')} USD/kg reported. All are below the reported prices and within the original study's ±20% range; this does not validate other formulations. Automated checks additionally cover manufacturing arithmetic, incomplete records, transfers, API persistence, and sensitivity calculations.

Ammonia cracking illustrates candidate-set sensitivity. Baseline costs are {kg(METHODS, 'normalization.example.rows[0].cost', '.4f')} USD/kg for Co/MgO-La₂O₃, {kg(METHODS, 'normalization.example.rows[1].cost', '.4f')} for Ni-MgO/CeO₂, {kg(METHODS, 'normalization.example.rows[2].cost', '.4f')} for Ni/Al₂O₃, and {kg(METHODS, 'normalization.example.removed_cost', '.4f')} for Ru/MgO. Co/MgO-La₂O₃ initially leads, with score {ms('normalization.example.rows[0].total_before', '.1f')} versus {ms('normalization.example.rows[2].total_before', '.1f')} for Ni/Al₂O₃. Removing Ru/MgO leaves remaining costs unchanged but contracts their range from approximately {full_range:,.0f} to {retained_range:.1f} USD/kg. Renormalization magnifies the {pair_gap:.2f} USD/kg cost difference, changing the scores to {ms('normalization.example.rows[0].total_after', '.1f')} and {ms('normalization.example.rows[2].total_after', '.1f')}, respectively, and reversing the ranking. Retaining the original range prevents this reversal.<sup>11,12</sup> Figure 4(d) reports 100 × (C₁ − C₀)/C₀ for nine affected families, where C₀ and C₁ are costs of the leaders before and after removal under unchanged manufacturing assumptions.

![Figure 4. Observed-price crossovers and ranking sensitivity. (a) Costs of the ammonia-cracking candidates that attain the lowest cost under 89 monthly price states; lines connect observed states. (b) Conditional equal-cost boundary between Co/MgO-La₂O₃ and Ni/Al₂O₃ in the nickel–cobalt price plane; points are monthly states, diamonds mark September and October 2025, and shading identifies the cheaper candidate. (c) First-rank frequencies; dashed line, 50%. (d) Cost differences between leaders before and after candidate removal; negative values indicate less expensive replacements. PEM, proton exchange membrane; AEM, anion exchange membrane; OER, oxygen evolution reaction; ORR, oxygen reduction reaction; SCR, selective catalytic reduction.](figures-note-2026-09-09/fig4_decision_diagnostics.png)

## Limitations

Industrial accuracy remains unvalidated because observations did not jointly match formulation, grade, scale, date, and boundary; mean absolute percentage error was not calculated. Preparation evidence does not supply unreported utilities, yields, or prices. Environmental coverage averages {r('s', 'lca.coverage_mean_pct', '.2f')}% of catalyst mass, with {r('s', 'lca.candidates_coverage_below_50_pct')} candidates below 50%; solvent supply, wastewater treatment, and equipment manufacture are excluded. Activity, deactivation, and use-phase impacts remain outside scope. Related studies address synthesis-cost optimization and catalyst lifetime.<sup>13,14</sup> COMET supports comparisons within declared assumptions, not overall performance or experimentally optimal preparation conditions.

## Supporting Information

Calculation methods and equations, transfer allocation, assumed manufacturing inputs, arithmetic verification, sensitivity and uncertainty analyses, historical metal prices and observed-price cost crossovers, candidate selling prices, preparation-evidence coverage, and application views (PDF). Preparation evidence, operating references, frozen calculation inputs and results, screening and ranking records, and reproduction instructions (ZIP).

## Data and Software Availability

COMET version {r('m', 'project_version')} uses the PolyForm Noncommercial License 1.0.0; commercial use requires a separate license. Repository: https://github.com/hyunjin-kor/COMET. Concept DOI: 10.5281/zenodo.21451931. [Authors must confirm access to this version and analysis files before submission.] Selected analysis inputs, outputs, checksums, and reproduction instructions accompany the study; the final distribution scope remains subject to author confirmation. Third-party data retain their source terms.

## Acknowledgments

OpenAI GPT tools assisted manuscript editing and conceptual artwork in Figures 1–3, and Google Gemini generated conceptual artwork in Supporting Information Figures S1 and S7, in September 2026. Numerical plots were generated from the reported calculations. The authors are responsible for the final content. Funding: [author statement required].

## Competing interests

Competing interests: [author declaration required].


## References

1. Baddour, F. G.; Snowden-Swan, L.; Super, J. D.; Van Allsburg, K. M. Estimating Precommercial Heterogeneous Catalyst Price: A Simple Step-Based Method. *Organic Process Research & Development* **2018**, *22* (12), 1599–1605. [DOI](https://doi.org/10.1021/acs.oprd.8b00245).
2. Van Allsburg, K. M.; Tan, E. C. D.; Super, J. D.; Schaidle, J. A.; Baddour, F. G. Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. *Nature Catalysis* **2022**, *5* (4), 342–353. [DOI](https://doi.org/10.1038/s41929-022-00759-6).
3. Gkika, D. A.; Kyzas, G. Z. Cost Evidence Yields the Viability of Metal Oxides Synthesis Routes. *ACS Sustainable Chemistry & Engineering* **2025**, *13* (41), 17370–17379. [DOI](https://doi.org/10.1021/acssuschemeng.5c06752).
4. Ferdous, S.; Gracida-Alvarez, U. R.; Ferrandon, M.; Delferro, M.; Benavides, P. T.; Urgun-Demirtas, M. Techno-economic and life cycle analyses of the synthesis of a platinum–strontium titanate catalyst. *Catalysis Science & Technology* **2025**, *15* (15), 4419–4429. [DOI](https://doi.org/10.1039/d5cy00189g).
5. Cortes-Peña, Y.; Kumar, D.; Singh, V.; Guest, J. S. BioSTEAM: A Fast and Flexible Platform for the Design, Simulation, and Techno-Economic Analysis of Biorefineries under Uncertainty. *ACS Sustainable Chemistry & Engineering* **2020**, *8* (8), 3302–3310. [DOI](https://doi.org/10.1021/acssuschemeng.9b07040).
6. Nuss, P.; Eckelman, M. J. Life Cycle Assessment of Metals: A Scientific Synthesis. *PLoS ONE* **2014**, *9* (7), e101298. [DOI](https://doi.org/10.1371/journal.pone.0101298).
7. Johnson Matthey. PGM Prices and Trading. https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management (accessed September 11, 2026).
8. Westmetall. Market Data: Prices and LME Stocks. https://www.westmetall.com/en/markdaten.php (accessed September 11, 2026).
9. International Monetary Fund. Primary Commodity Price System (PCPS), SDMX 2.1 data service. https://api.imf.org/external/sdmx/2.1/dataflow/IMF.RES/PCPS (accessed September 11, 2026).
10. United Nations. UN Comtrade Database. https://comtradeplus.un.org (accessed September 11, 2026).
11. Mohammadi, M.; Rezaei, J. Ratio product model: A rank-preserving normalization-agnostic multi-criteria decision-making method. *Journal of Multi-Criteria Decision Analysis* **2023**, *30*, 163–172. [DOI](https://doi.org/10.1002/mcda.1806).
12. OECD; European Union; Joint Research Centre - European Commission. *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD, 2008. [DOI](https://doi.org/10.1787/9789264043466-en).
13. Petel, B. E.; Van Allsburg, K. M.; Baddour, F. G. Cost-Responsive Optimization of Nickel Nanoparticle Synthesis. *Advanced Sustainable Systems* **2024**, *8* (10), 2300030. [DOI](https://doi.org/10.1002/adsu.202300030).
14. Mendoza Suarez, F.; Tatarchuk, B. Comparative economic analysis of batch vs. continuous manufacturing in catalytic heterogeneous processes: impact of catalyst activity maintenance and materials costs on total costs of manufacturing in the production of fine chemicals and pharmaceuticals. *Journal of Flow Chemistry* **2025**, *15*, 21–38. [DOI](https://doi.org/10.1007/s41981-024-00342-z).
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
