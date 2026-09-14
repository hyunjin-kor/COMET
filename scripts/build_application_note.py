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
WORD_LIMIT = 5000
GRAPHICS = [
    {"figure": 1, "width": "double", "word_equivalent": 600},
    {"figure": 2, "width": "double", "word_equivalent": 600},
    {"figure": 3, "width": "single", "word_equivalent": 300},
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
    for name in (ROBUSTNESS, METHODS, EXAMPLE, MARKET, PREPARATION):
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
    study = run.data[ROBUSTNESS]
    ammonia = next(i for i, f in enumerate(study["families"]) if f["family"] == "ammonia-cracking")
    joint = f'families[{ammonia}].joint_grids["0.05"].candidates["co-mgo-la2o3"]'

    def rb(key, spec=None):
        return r(ROBUSTNESS, key, spec)

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

COMET (Catalyst Overall Manufacturing Estimation Tool) integrates catalyst manufacturing cost estimation, price-data management, and candidate ranking through desktop and browser interfaces. A library of {rb('summary.candidates')} formulations in {rb('summary.families')} reaction families supports comparisons of cost contributions and selected environmental impacts under consistent assumptions. Source-linked current and historical prices, saved inputs, and software records support reproducible sensitivity analyses of prices, production scale, weights, scores, and candidate availability. Three literature examples verify the cost calculations without adjusting reported inputs; independent validation against industrial cost data remains necessary.

Keywords: catalyst manufacturing cost; cost estimation; sensitivity analysis; multicriteria decision analysis; software.

## Introduction

Catalyst selection requires evaluating manufacturing cost alongside performance and environmental impacts. The Step Method estimates precommercial catalyst selling prices from material requirements, unit operations, overheads, and a profit margin.<sup>1</sup> CatCost integrated manufacturing cost estimation with environmental impact assessment and demonstrated how synthesis methods and production scale affect catalyst costs.<sup>2</sup> Studies of individual synthesis routes provide further cost analyses,<sup>3,4</sup> while BioSTEAM integrates process design, techno-economic analysis, and uncertainty analysis in a programmable environment.<sup>5</sup>

Applying cost estimates to candidate selection also requires consistent price dates, process boundaries, and functional units. A preferred candidate can change with market prices, criterion weights, assigned scores, or the alternatives included in a comparison.

COMET links price updates and historical recalculation to multicriteria sensitivity analysis. Records identify price sources, calculation assumptions, uncosted operations, and environmental inventory gaps. Comparisons use catalyst mass or electrode area and vary prices, weights, scores, and candidate sets. Published examples verify the implementation; ammonia cracking illustrates candidate-set sensitivity.

## Software implementation

Figure 1 connects formulation, prices, cost estimation, and ranking. Users select a thermal catalyst or electrode assembly, enter or load a formulation, and edit its route and scale. Results link costs to operation coverage, inventory gaps, and sources. Saved inputs support recalculation; CSV exports preserve results and sources. Analysis files retain boundaries, functional units, checksums, software versions, and random seeds.

![Figure 1. COMET workflow. Inputs, price selection, cost estimation, and candidate ranking share a record of data sources, assumptions, and reproduction details.](figures-note-2026-09-09/fig1_workflow_stack.png)

SQLite stores prices, estimates, and preparation records. The bilingual React/TypeScript interface connects to FastAPI; source builds require Python 3.11 and Node.js 22 or later. Electron packages Windows builds with PyInstaller. Windows workflows and Linux backend/interface builds were tested. Stored or user-supplied prices enable offline calculation.

A preparation audit covers all {r(PREPARATION, 'candidates')} candidates, distinguishing bibliographic identity from specimen agreement. Crossref checks confirmed {r(PREPARATION, 'crossref_dois')} DOIs; accessible primary Methods and supplements yielded {r(PREPARATION, 'profiles')} named preparation records from {r(PREPARATION, 'primary_sources')} sources. Records preserve ordered operations, temperature ramps and holds, atmosphere, pressure, mixing, washing, drying, and source locations. Unreported conditions remain blank; qualitative durations are not assigned numbers. Imports are editable records, with powder synthesis, activation and electrode fabrication distinguished. Supporting Information gives every candidate's assessment and the source-specific procedures. Linked-source discrepancies were flagged for {r(PREPARATION, 'source_mismatches')} candidates, including mismatched supports, metals and loadings. Frozen screening calculations retain their declared assumptions and are not validated experimental recipes.

For a saved 20 wt% Ni/Al₂O₃ impregnation scenario at {kg(EXAMPLE, 'request.order_size_tons', ',.1f', KG_PER_SHORT_TON)} kg, the estimated selling price is {kg(EXAMPLE, 'step_method.estimated_price_per_lb', '.2f')} USD/kg; nickel and processing contribute {kg(EXAMPLE, 'materials.components[0].cost_per_lb_cat', '.2f')} and {kg(EXAMPLE, 'step_method.processing_cost_per_lb', '.2f')} USD/kg. Figure 2(b) shows the least expensive screening candidate in each of 23 thermal families at May 2026 prices, including route allowances. Bars total 100%, are ordered by materials share, and show absolute prices alongside. They distinguish cost contributions without implying equivalent catalytic performance across reactions.

![Figure 2. Cost estimation. (a) Calculation scheme. (b) Screening cost shares and selling prices in USD/kg under the declared formulation and route assumptions. Other costs comprise overheads, margin, and route-specific allowances. (c) COMET and literature estimates relative to market prices reported by Baddour et al.<sup>1</sup> Deviation = 100 × (estimated price − market price)/market price; negative values indicate estimates below market prices. SCR, selective catalytic reduction.](figures-note-2026-09-09/fig2_cost_model.png)

## Cost estimation and environmental screening

In Figure 2(a), materials cost is Cₘ = Σ<sub>i</sub>w<sub>i</sub>c<sub>i</sub>, where w<sub>i</sub> is component mass fraction and c<sub>i</sub> is price per kg. Alternatively, purchased precursor requirements are $w/(f\\,p\\,y)$ kg per kg of catalyst: $w$ is the component fraction in the product, $f$ its fraction in pure precursor, $p$ precursor purity, and $y$ retention in the product. Precursor and consumable costs use purchase prices and required quantities. Users supply these quantities and sources; stoichiometry, losses, and recycling are not inferred.

Processing cost follows the Step Method, Cₚ = 24TIH/M: campaign duration T in days, price-index factor I, summed hourly operation costs H, and catalyst mass M in kg. The {r('s', 'manufacturing.20.template_count')} editable procedures retain repeated operations. Order size determines equipment scale, production rate, and cleaning allowance; a documented effective rate can replace the nominal rate. Substituted and uncosted operations are identified. Hourly rates use the 2017 equipment basis adjusted by a chemical-manufacturing producer price index. Selling price is P = (Cₘ + Cₚ)(1 + g)(1 + s)/(1 − m), where g and s are general and administrative (G&A) and sales, administrative, research, and distribution (SARD) fractions. Margin m follows the published order-size correlation. Figure 2(a) illustrates operations rather than prescribing a route. Optional recovery subtracts the specified spent-metal value. A separate module estimates capital investment and annual operating costs; these are not automatically added to the Step Method price.

Alternatively, explicit batch operating inputs replace Step Method processing cost. Electricity is measured kWh or input power multiplied by ramp and hold durations; gas consumption, attended labor and equipment occupancy are costed separately. Processing cost is divided by actual dry output in kg. Missing costs prevent batch calculation. Overheads and an explicit margin are then applied; batch repetition implies no scale economy. Record-only imports preserve the selected cost model. Electrode recipes remain records; dry-powder batch costing does not apply to them.

Electrode estimates combine catalyst, ionomer, membrane, and substrate costs per area. Optional manufacturing scenarios add equipment, labor, and facility costs. Powder routes and complete stack assembly remain separate.

Environmental screening estimates global warming potential and cumulative energy demand per kg using cradle-to-gate metal factors.<sup>6</sup> Calculator and batch results cover materials; benchmark analyses additionally model route fuel and electricity. Missing impacts remain unknown. Element-based mappings for compounds are approximations; mass coverage, even 100%, does not establish a complete life-cycle inventory.

## Price data and sources

Current quotations include Johnson Matthey base prices for platinum and palladium<sup>7</sup> and Westmetall settlement prices for copper and aluminum.<sup>8</sup> Other prices follow a documented source hierarchy, with retrieval times recorded. The monthly price basis uses the International Monetary Fund (IMF) Primary Commodity Price System (PCPS)<sup>9</sup> and monthly averages of Johnson Matthey daily quotations. Support prices use U.S. import unit values<sup>10</sup> for {r('meta', 'support_series')} Harmonized System (HS) commodity codes, comprising {r('meta', 'support_observations')} verified observations. Figure 3 separates precious and base metals on logarithmic axes: equal vertical intervals represent equal price ratios. The unsmoothed monthly series provide historical inputs for sensitivity analysis, not forecasts. From January 2019 to May 2026, maximum-to-minimum price ratios are 2.3 for zinc, 2.9 for nickel, 6.8 for ruthenium, and 11.6 for rhodium.

Price-source grades are weighted by materials-cost contributions. This criterion, termed evidence in COMET, concerns pricing provenance, not performance or preparation verification; prices can change both cost and reliability scores. Cost observations require matched currency, date, composition, grade, scale, operations, and boundary.

![Figure 3. Metal price history. Monthly averages from January 2019 to May 2026: (a) precious metals; (b) base metals. Prices are in USD/kg. Both price axes are logarithmic.](figures-note-2026-09-09/fig3_metal_prices.png)

## Candidate ranking and sensitivity analysis

The library contains {rb('summary.candidates')} screening formulations in {rb('summary.families')} reaction families, including {r('s', 'screening_basis_counts.literature_architecture_proxy')} literature-architecture proxies and {r('s', 'screening_basis_counts.engineering_proxy')} engineering proxies. These labels do not establish exact experimental compositions. Candidates are ranked by a weighted sum of four criteria: cost, reliability of price data, preparation route, and performance. The cost criterion is scaled from 100 for the lowest cost to 0 for the highest cost within each family; all candidates receive 100 when their costs are equal. Route scores average preparation, manufacturing readiness, and agreement between formulation and supporting evidence. Route and performance scores are assigned by the authors for screening; they are not experimental measurements. The interface offers balanced, cost-first, and reliability-first profiles; analysis scripts support custom weights. Baseline rankings use May 2026 prices, balanced weights, and the complete candidate set. Ties are resolved by lower cost using a common functional unit. Families with incomplete electrode inputs are compared using catalyst powder costs.

Companion scripts evaluate weight sensitivity using {r('s', 'weight_sensitivity.grid_points')} nonnegative weight combinations summing to one. Across reaction families, the median frequency with which the candidate ranked first at baseline remains first is {r('s', 'weight_sensitivity.median_balanced_winner_share_pct', '.2f')}%. They also recalculate costs and rankings for {r('s', 'volatility.window.states')} monthly sets of metal prices from {r('s', 'volatility.window.first')} to {r('s', 'volatility.window.last')}, with support prices held at their baseline values. Individual-metal thresholds identify where the highest-ranked candidate changes. The interface runs Monte Carlo analysis on the current formulation, sampling uniform price and order-size multipliers; detailed preparation conditions remain fixed. The default range for active components is 0.70–1.30 times the input price, and components with the same role share a multiplier in each trial. Analysis outputs retain failed trials and sampling seeds for reproducibility. These ranges describe assumed input variation, not statistical confidence intervals for industrial costs.

The combined sensitivity analysis evaluates {rb('summary.months')} monthly price datasets and {rb('summary.weight_points["0.05"]')} weight combinations at increments of 0.05, giving {rb('summary.joint_scenarios_all_families["0.05"]', ',')} scenarios across all reaction families (Figure 4(a,b)). First-rank frequency measures ranking stability; regret measures the score-point deficit from the highest score in each scenario. Figure 4(a) separates the baseline candidate, the most frequently first-ranked alternative, and others. Baseline shares below 50% indicate that alternatives collectively rank first more often than the baseline candidate. Across families, the median frequency of retaining the baseline candidate at rank 1 is {rb('summary.reference_winner_joint_share_median_pct', '.2f')}%. Each nonleading candidate is removed in turn, with the cost normalization range recalculated or retained. Score tests lower the baseline candidate’s route and performance scores and raise those of alternatives by 2, 5, or 10 points within the 0–100 scale. Candidate removal changes the highest-ranked candidate in {rb('summary.candidate_removal_winner_changes')} of {rb('summary.candidate_removal_cases')} tests, and {rb('summary.rubric_robust_family_counts["5"]')} families retain the same candidate under the 5-point score variation. Figure 4(b) counts families retaining the baseline candidate in at least half the combined scenarios, after every single-candidate removal, or under each score variation. These tests address different vulnerabilities; passing one does not establish robustness to the others. Scenario frequencies are not future probabilities.

Two to four saved cases can be compared as recorded, at common prices, and at common prices and operating conditions. Each retains its formulation and operation sequence. The latter comparison controls order size and overhead assumptions, helping separate price and scale effects from formulation and route differences. Changes in software versions can also affect recalculation, so historical differences are not necessarily market effects alone.

## Verification and reproducibility

The implementation was checked against three published examples using their reported materials costs, operation sequences, and order sizes without adjustment. COMET estimates {kg('s', 'table62[0].comet_usd_per_lb', '.4f')} USD/kg for Pt/C, compared with the published value of {kg('s', 'table62[0].published_usd_per_lb', '.2f')} USD/kg; both exclude platinum metal value as specified in the source. For Ni/Al₂O₃, the estimate is {kg('s', 'table62[1].comet_usd_per_lb', '.4f')} versus {kg('s', 'table62[1].published_usd_per_lb', '.2f')} USD/kg, a difference of {r('s', 'table62[1].residual_pct', '+.2f')}%. This difference results from using the published correlation between order size and margin instead of the fixed margin in the table footnote. For the ultrastable zeolite Y (USY) catalyst used in fluid catalytic cracking (FCC), the estimate is {kg('s', 'table62[2].comet_usd_per_lb', '.4f')} versus {kg('s', 'table62[2].published_usd_per_lb', '.2f')} USD/kg, a difference of {r('s', 'table62[2].residual_pct', '+.2f')}%, at the effective production rate of {kg('s', 'table62[2].effective_rate_ton_per_day', ',.1f', KG_PER_SHORT_TON)} kg/day specified in the footnote. Intermediate processing and overhead calculations agree with the tabulated values at the reported precision.

The same study reports market prices for the three catalysts.<sup>1</sup> Using 100 × (estimated price − market price)/market price, COMET estimates differ by {mk('[0].market.comet_vs_market_pct', '.1f')}% for Pt/C and {mk('[1].market.comet_vs_market_pct', '.1f')}% for Ni/Al₂O₃. The estimate for the FCC catalyst is {kg(MARKET, '[2].with_published_rate.estimated_price_per_lb', '.4f')} USD/kg, compared with a reported market price of {kg(MARKET, '[2].market.market_price_per_lb', '.2f')} USD/kg (Figure 2(c)). Both COMET and the published estimates are below the reported market prices. The original study obtained these prices from industry experts and reported agreement within ±20%; COMET also falls within that range. Accuracy for other formulations remains unvalidated. The analysis files also contain a comparison with U.S. import unit values for HS 3815 catalyst categories.<sup>10</sup> These aggregated data combine different grades, loadings, formulations, and order sizes, precluding validation of individual formulations.

Automated tests cover cost arithmetic, incomplete preparation records, electrode boundaries, API, price retrieval, and candidate coverage; Windows packaging was also tested. SHA-256 checksums and software versions document analysis inputs, code, and outputs. Calculations use reference month {r('s', 'basis_month')} and sampling seed {r('m', 'seed')}; exhaustive sensitivity analyses require no sampling.

## Application to ammonia cracking

Four assumed ammonia-cracking formulations illustrate candidate-set sensitivity. At baseline prices, estimated costs are {kg(METHODS, 'normalization.example.rows[0].cost', '.4f')} USD/kg for Co/MgO-La₂O₃, {kg(METHODS, 'normalization.example.rows[1].cost', '.4f')} for Ni-MgO/CeO₂, {kg(METHODS, 'normalization.example.rows[2].cost', '.4f')} for Ni/Al₂O₃, and {kg(METHODS, 'normalization.example.removed_cost', '.4f')} for Ru/MgO. The balanced weights are {ms('normalization.example.weights.economics')} for cost, {ms('normalization.example.weights.evidence')} for reliability of price data, {ms('normalization.example.weights.route')} for preparation route, and {ms('normalization.example.weights.performance')} for performance. Co/MgO-La₂O₃ ranks first with a composite score of {ms('normalization.example.rows[0].total_before', '.1f')}, compared with {ms('normalization.example.rows[2].total_before', '.1f')} for Ni/Al₂O₃. The cobalt formulation ranks first in {rb(joint + '.first_rank_share_pct', '.2f')}% of the combined scenarios and has a maximum regret of {rb(joint + '.worst_regret_score_points', '.1f')} score points.

Removing Ru/MgO leaves the other cost estimates unchanged but reduces their range from approximately {full_range:,.0f} to {retained_range:.1f} USD/kg. With min–max normalization, the {pair_gap:.2f} USD/kg difference between Co/MgO-La₂O₃ and Ni/Al₂O₃ then produces a larger difference in their cost scores. The composite score for Co/MgO-La₂O₃ decreases to {ms('normalization.example.rows[0].total_after', '.1f')}, whereas that for Ni/Al₂O₃ remains {ms('normalization.example.rows[2].total_after', '.1f')}, reversing their ranking. If the original normalization range is retained, Co/MgO-La₂O₃ remains first. This result is consistent with rank reversal in normalized weighted-sum methods.<sup>11,12</sup> Figure 4(c) reports 100 × (C₁ − C₀)/C₀ for the nine affected families. C₀ and C₁ are the costs of the candidates ranked first before and after removal, respectively, under identical prices and manufacturing assumptions. Negative values indicate a less expensive replacement; remaining candidate costs do not change. These diagnostics identify choices requiring further assessment of weights, candidate availability, and performance evidence before experimental prioritization.

![Figure 4. Ranking sensitivity. Formulation and manufacturing assumptions remain fixed. (a) First-rank frequencies; the dashed line marks 50%. (b) Families retaining the baseline candidate under each test. (c) Cost differences after candidate removal. PEM, proton exchange membrane; AEM, anion exchange membrane; OER, oxygen evolution reaction; ORR, oxygen reduction reaction; SCR, selective catalytic reduction.](figures-note-2026-09-09/fig4_decision_diagnostics.png)

## Limitations

COMET estimates manufacturing costs empirically; industrial accuracy remains unvalidated because available observations did not match formulation, grade, order size, date, and process boundary. Consequently, mean absolute percentage error was not calculated. Rankings depend on assumed formulations and assigned route and performance scores. Environmental data cover a mean of {r('s', 'lca.coverage_mean_pct', '.2f')}% of catalyst mass, with coverage below 50% for {r('s', 'lca.candidates_coverage_below_50_pct')} candidates. Solvent supply, wastewater treatment, and equipment manufacture are excluded from the process inventory. Processing costs use the published 2017 equipment basis with index adjustment; substituted and uncosted operations are identified. Catalyst activity, deactivation, and impacts during use are outside the model's scope. Related studies address cost optimization of synthesis and the economic effects of catalyst lifetime.<sup>13,14</sup> The resulting rankings therefore support screening within the stated assumptions and do not establish overall catalyst performance.

## Supporting Information

Candidate-by-candidate preparation assessment, source-specific conditions, DOI and section locators, and unresolved inputs (manufacturing-literature-2026-09-14.md).

## Data and Software Availability

COMET is distributed under the PolyForm Noncommercial License 1.0.0, which permits noncommercial use and requires a separate license for commercial use; it is not an OSI-approved open-source license. The project repository is https://github.com/hyunjin-kor/COMET, and its concept DOI is 10.5281/zenodo.21451931. This study uses version {r('m', 'project_version')}. [Access to this version and its associated analysis files is to be confirmed by the authors before submission.] The analysis files contain the input price datasets, numerical results, checksums, and scripts used to generate the manuscript and figures. Third-party data remain subject to their respective source terms. Instructions for installation, data collection, and regeneration accompany the software and analysis files.

## Acknowledgments

Funding and other acknowledgments: [to be supplied by the authors].

## Competing interests

Competing interests: [declaration to be supplied by the authors before submission].

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
