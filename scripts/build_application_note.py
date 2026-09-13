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

DATE = "2026-09-09"
RUN_DATE = "2026-09-08"
ROBUSTNESS = "robustness-2026-09-08/decision_robustness.json"
METHODS = "methods-2026-09-09/methods_study.json"
EXAMPLE = "figures-note-2026-09-09/screen_result_ni_al2o3.json"
MARKET = "submission-2026-09-08/table62_reproduction_2026-09-08.json"
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
    for name in (ROBUSTNESS, METHODS, EXAMPLE, MARKET):
        run.data[name] = paper.load(paper.PAPER / name)
    if run.data[ROBUSTNESS]["seed"] != run.manifest["seed"] or run.data[METHODS]["seed"] != run.manifest["seed"]:
        raise ValueError("Robustness study, methods supplement and primary run must share one seed")
    return run


def note(run):
    r = run.ref
    study = run.data[ROBUSTNESS]
    ammonia = next(i for i, f in enumerate(study["families"]) if f["family"] == "ammonia-cracking")
    joint = f'families[{ammonia}].joint_grids["0.05"].candidates["co-mgo-la2o3"]'

    def rb(key, spec=None):
        return r(ROBUSTNESS, key, spec)

    def ms(key, spec=None):
        return r(METHODS, key, spec)

    def ex(key, spec=None):
        return r(EXAMPLE, key, spec)

    def mk(key, spec=None):
        return r(MARKET, key, spec)

    return f"""# COMET: Catalyst Overall Manufacturing Estimation Tool

Authors, affiliations and corresponding-author contact: [to be supplied by the authors].

## Abstract

COMET (Catalyst Overall Manufacturing Estimation Tool) integrates catalyst manufacturing cost estimation, price-data management, and candidate ranking in a reproducible screening workflow. Current quotations and historical monthly averages are linked to their sources, dates, and reliability assessments. A library of {rb('summary.candidates')} candidate formulations spanning {rb('summary.families')} reaction families supports comparisons under consistent process boundaries and functional units. The software reports cost contributions and selected environmental impacts, while assessing how prices, production scale, criterion weights, assigned scores, and candidate availability affect rankings. Saved input datasets, software version records, and optional random seeds for Monte Carlo sampling support reproducibility. Three literature examples verify the implementation of established cost calculations without adjusting their reported inputs. Independent validation against industrial cost data remains necessary. Desktop and browser interfaces support preliminary catalyst selection and examination of the assumptions underlying each comparison.

Keywords: catalyst manufacturing cost; cost estimation; sensitivity analysis; multicriteria decision analysis; software.

## Introduction

Catalyst selection requires evaluating manufacturing cost alongside performance and environmental impacts. The Step Method estimates precommercial catalyst selling prices from material requirements, unit operations, overheads, and a profit margin.<sup>1</sup> CatCost integrated manufacturing cost estimation with environmental impact assessment and demonstrated how synthesis methods and production scale affect catalyst costs.<sup>2</sup> Studies of individual synthesis routes provide further cost analyses,<sup>3,4</sup> while BioSTEAM integrates process design, techno-economic analysis, and uncertainty analysis in a programmable environment.<sup>5</sup>

Applying cost estimates to candidate selection also requires consistent price dates, process boundaries, and functional units. A preferred candidate can change with market prices, criterion weights, assigned scores, or the alternatives included in a comparison.

COMET addresses these requirements through an integrated workflow for price updates, historical recalculation, and multicriteria sensitivity analysis. It records price sources and calculation assumptions, identifies uncosted operations and environmental inventory gaps, and distinguishes catalyst mass-based costs from electrode area-based costs. Users can examine ranking changes under alternative prices, weights, scores, and candidate sets. We verify the cost calculations against published examples and examine candidate-set sensitivity using ammonia cracking.

## Software implementation

The five-stage workflow links data input and price-basis selection to cost estimation, cost contributions, and candidate ranking (Figure 1). A shared analysis record retains price sources, quotation dates, reliability assessments, calculation assumptions, and reproduction details. These include the system boundary, functional unit, inventory coverage, file checksums, software versions, and any random seed.

![Figure 1. COMET workflow. The conceptual artwork was generated with OpenAI's image-generation tool; labels were added in PowerPoint.](figures-note-2026-09-09/fig1_workflow_stack.png)

Calculations run locally, with prices, estimates, and supporting records stored in SQLite. A FastAPI backend requires Python 3.11 or later; the bilingual interface uses React 19 and TypeScript. Electron packages the Windows application with a PyInstaller-built backend. The browser interface runs from source with Node.js 22 or later. Backend tests and interface builds run on Linux; complete browser operation has been tested only on Windows. Stored or user-supplied prices permit offline calculation without application programming interface (API) keys.

In a saved calculation using spot quotations, a 20 wt% Ni/Al₂O₃ catalyst prepared by incipient-wetness impregnation at an order size of {ex('request.order_size_tons', '.0f')} short tons has an estimated selling price of {ex('step_method.estimated_price_per_lb', '.2f')} USD/lb. Nickel and processing account for {ex('materials.components[0].cost_per_lb_cat', '.2f')} and {ex('step_method.processing_cost_per_lb', '.2f')} USD/lb, respectively. Figure 2(b) compares the least expensive candidate in each of 23 thermal reaction families at May 2026 prices, separating materials, processing, and overheads plus margin as shares of selling price. Results can be exported as comma-separated values (CSV), including price-source information and optional Monte Carlo results.

![Figure 2. Cost estimation. (a) Calculation scheme; artwork generated with OpenAI's image-generation tool and labeled in PowerPoint. (b) Cost shares and selling prices (USD/lb). (c) Deviations from published market prices. SCR, selective catalytic reduction.](figures-note-2026-09-09/fig2_cost_model.png)

## Cost estimation and environmental screening

In Figure 2(a), materials cost is Cₘ = Σ<sub>i</sub>w<sub>i</sub>c<sub>i</sub>, where w<sub>i</sub> is component mass fraction and c<sub>i</sub> is price per lb. Users can instead specify precursor and consumable requirements. For a component with mass fraction $w$ in the finished catalyst, the precursor requirement is $w/(f\\,p\\,y)$ kg per kg of catalyst, where $f$ is the mass fraction of that component in the pure precursor, $p$ is precursor purity, and $y$ is the fraction of the component retained in the product. Precursor and consumable costs are then calculated from their purchase prices and required quantities. The user must supply these inputs and their supporting sources; stoichiometry, material losses, and recycling are not inferred by the software.

Processing cost follows the Step Method, Cₚ = 24TIH/M, with campaign duration T in days, price-index factor I, summed hourly operation costs H, and catalyst mass M in lb. The software provides {r('s', 'manufacturing.20.template_count')} editable preparation procedures from the published equipment table, including repeated operations. Order size determines equipment scale, production rate, and cleaning allowance; a documented effective rate can replace the nominal rate. Missing operations use a disclosed substitute cost or remain uncosted. Hourly rates are adjusted from 2017 using a chemical-manufacturing producer price index. Selling price is P = (Cₘ + Cₚ)(1 + g)(1 + s)/(1 − m), where g and s are the general and administrative (G&A) and sales, administrative, research, and distribution (SARD) fractions, respectively. Margin m is a fraction of selling price from the published order-size correlation. The illustrated operations in Figure 2(a) are examples, not a prescribed route. Electrode costs include catalyst loading, ionomer, membrane, and substrate per unit area; powder costs are reported separately. Optional metal recovery deducts the specified value of recoverable metal in the spent catalyst.

Environmental screening estimates global warming potential and cumulative energy demand per kilogram of catalyst. Material contributions use published cradle-to-gate factors for metals.<sup>6</sup> Components without a verified factor, including some supports, are recorded as missing inventory data. Process contributions are estimated from fuel and electricity requirements for calcination, drying, and mechanical operations using public emission factors. Each result states the system boundary and inventory coverage, defined as the percentage of catalyst mass for which verified material factors are available. This percentage describes data coverage, not the proportion of total environmental impact represented.

## Price data and sources

Current quotations include Johnson Matthey base prices for platinum and palladium<sup>7</sup> and Westmetall settlement prices for copper and aluminum.<sup>8</sup> Exchange futures, public quotation pages, and documented reference values are used according to a predefined source hierarchy; retrieval times are recorded. The monthly price basis uses the International Monetary Fund (IMF) Primary Commodity Price System (PCPS)<sup>9</sup> and monthly averages of Johnson Matthey daily quotations. Support prices use U.S. import unit values<sup>10</sup> for {r('meta', 'support_series')} Harmonized System (HS) commodity codes, comprising {r('meta', 'support_observations')} verified observations. The selected price basis is applied consistently to cost estimation and candidate ranking. Figure 3 shows the recorded monthly averages without smoothing. From January 2019 to May 2026, maximum-to-minimum price ratios are 2.3 for zinc, 2.9 for nickel, 6.8 for ruthenium, and 11.6 for rhodium.

Each price source is assigned a reliability grade and a corresponding numerical score. The criterion called evidence in COMET is the average of these scores, weighted by each input's contribution to materials cost. It therefore represents the reliability of the price data, rather than the strength of evidence for catalytic performance. A change in prices can affect both the cost estimate and this score. Saved estimates can be compared with user-entered cost observations when currency, month, composition, grade, order size, production rate, operations, and process boundary match.

![Figure 3. Metal price history. Monthly averages from January 2019 to May 2026: (a) precious metals (USD/troy oz); (b) base metals (USD/lb). Both price axes are logarithmic.](figures-note-2026-09-09/fig3_metal_prices.png)

## Candidate ranking and sensitivity analysis

The library contains {rb('summary.candidates')} candidate formulations in {rb('summary.families')} reaction families. Each record specifies composition, preparation procedure, references, and the basis for the formulation. These include {r('s', 'screening_basis_counts.literature_architecture_proxy')} formulations based on catalyst structures reported in the literature and {r('s', 'screening_basis_counts.engineering_proxy')} based on engineering assumptions. Candidates are ranked by a weighted sum of four criteria: cost, reliability of price data, preparation route, and performance. The cost criterion is scaled from 100 for the lowest cost to 0 for the highest cost within each family; all candidates receive 100 when their costs are equal. The route score is the mean of assessments of the preparation procedure, manufacturing readiness, and correspondence between the modeled formulation and its supporting evidence. Route and performance scores are assigned by the authors for screening; they are not experimental measurements. Preset weights emphasize balanced criteria, cost, or price-data reliability, and custom weights are supported. Baseline rankings use May 2026 prices, balanced weights, and the complete candidate set. Ties are resolved by lower cost using a common functional unit. Families with incomplete electrode inputs are compared using catalyst powder costs.

Sensitivity to criterion weights is evaluated using {r('s', 'weight_sensitivity.grid_points')} weight combinations on a simplex grid, for which the weights are nonnegative and sum to one. Across reaction families, the median frequency with which the candidate ranked first at baseline remains first is {r('s', 'weight_sensitivity.median_balanced_winner_share_pct', '.2f')}%. Costs and rankings are also recalculated for {r('s', 'volatility.window.states')} monthly sets of metal prices from {r('s', 'volatility.window.first')} to {r('s', 'volatility.window.last')}, with support prices held at their baseline values. The analysis can identify the price of an individual metal at which the highest-ranked candidate changes. Monte Carlo analysis samples uniform multipliers for component prices and order size within specified ranges. The default range for active components is 0.70–1.30 times the input price, and components with the same role share a multiplier in each trial. Failed trials and their causes are reported. A fixed random seed permits repeated sampling with the same results. These calculations describe the effects of assumed input variation; they do not provide statistical confidence intervals for industrial costs.

The combined sensitivity analysis evaluates {rb('summary.months')} monthly price datasets and {rb('summary.weight_points["0.05"]')} weight combinations at increments of 0.05, giving {rb('summary.joint_scenarios_all_families["0.05"]', ',')} scenarios across all reaction families (Figure 4(a,b)). For each candidate, it reports the frequency of ranking first and the mean and maximum difference from the highest composite score in each scenario. This difference, termed regret, is expressed in score points. Figure 4(a) separates the baseline candidate, the most frequently first-ranked alternative, and all others; the alternative need not rank second at baseline. Across families, the median frequency of retaining the baseline candidate at rank 1 is {rb('summary.reference_winner_joint_share_median_pct', '.2f')}%. Each candidate other than the one ranked first at baseline is then removed in turn; rankings are compared with and without recalculating the cost normalization range. Sensitivity to assigned scores is tested by decreasing the route and performance scores of the candidate ranked first at baseline and increasing those of all other candidates by 2, 5, or 10 points, subject to the 0–100 scale. Candidate removal changes the highest-ranked candidate in {rb('summary.candidate_removal_winner_changes')} of {rb('summary.candidate_removal_cases')} tests, and {rb('summary.rubric_robust_family_counts["5"]')} families retain the same candidate under the 5-point score variation. Figure 4(b) counts families retaining the baseline candidate in at least half the combined scenarios, after every single-candidate removal, or under each score variation. Scenario frequencies are not probabilities of future outcomes.

Two to four saved estimates can be compared using their original results, a common set of prices, or common prices and manufacturing assumptions. Recalculation under common assumptions separates the effects of price changes from those of formulation, preparation procedure, and production scale.

## Verification and reproducibility

The implementation was checked against three published examples using their reported materials costs, operation sequences, and order sizes without adjustment. COMET estimates {r('s', 'table62[0].comet_usd_per_lb', '.4f')} USD/lb for Pt/C, compared with the published value of {r('s', 'table62[0].published_usd_per_lb', '.2f')} USD/lb; both exclude platinum metal value as specified in the source. For Ni/Al₂O₃, the estimate is {r('s', 'table62[1].comet_usd_per_lb', '.4f')} versus {r('s', 'table62[1].published_usd_per_lb', '.2f')} USD/lb, a difference of {r('s', 'table62[1].residual_pct', '+.2f')}%. This difference results from using the published correlation between order size and margin instead of the fixed margin in the table footnote. For the ultrastable zeolite Y (USY) catalyst used in fluid catalytic cracking (FCC), the estimate is {r('s', 'table62[2].comet_usd_per_lb', '.4f')} versus {r('s', 'table62[2].published_usd_per_lb', '.2f')} USD/lb, a difference of {r('s', 'table62[2].residual_pct', '+.2f')}%, at the effective production rate of {r('s', 'table62[2].effective_rate_ton_per_day', '.0f')} short tons per day specified in the footnote. Intermediate processing and overhead calculations agree with the tabulated values at the reported precision.

The same study reports market prices for the three catalysts.<sup>1</sup> Using 100 × (estimated price − market price)/market price, COMET estimates differ by {mk('[0].market.comet_vs_market_pct', '.1f')}% for Pt/C and {mk('[1].market.comet_vs_market_pct', '.1f')}% for Ni/Al₂O₃. The estimate for the FCC catalyst is {mk('[2].with_published_rate.estimated_price_per_lb', '.4f')} USD/lb, compared with a reported market price of {mk('[2].market.market_price_per_lb', '.2f')} USD/lb (Figure 2(c)). Both COMET and the published estimates are below the reported market prices. The original study obtained these prices through communication with industry experts and reported agreement within ±20%; COMET's estimates also fall within that range. These comparisons do not establish the source of the residual differences or accuracy for other formulations. The analysis files also contain a comparison with U.S. import unit values for HS 3815 catalyst categories.<sup>10</sup> These aggregated data combine different grades, loadings, formulations, and order sizes, precluding validation of individual formulations.

Agreement with published calculations supports verification of the implementation. Comparisons with reported market prices and import unit values provide additional context, but cannot determine the error for a new formulation without industrial cost observations under comparable conditions.

Automated tests cover the calculation engine, API, price retrieval, and candidate library; continuous integration also tests the packaged Windows application. The analysis scripts save input, code, and output checksums using SHA-256, together with software versions. These records support reproduction of the numerical results in the documented environment. Calculations reported here use the reference month {r('s', 'basis_month')} and, where random sampling is required, seed {r('m', 'seed')}. The exhaustive sensitivity analyses do not use random sampling.

## Application to ammonia cracking

Ammonia cracking illustrates how the candidate set can affect a ranking. At the baseline prices, the estimated costs are {ms('normalization.example.rows[0].cost', '.4f')} USD/lb for Co/MgO-La₂O₃, {ms('normalization.example.rows[1].cost', '.4f')} for Ni-MgO/CeO₂, {ms('normalization.example.rows[2].cost', '.4f')} for Ni/Al₂O₃, and {ms('normalization.example.removed_cost', '.4f')} for Ru/MgO. The balanced weights are {ms('normalization.example.weights.economics')} for cost, {ms('normalization.example.weights.evidence')} for reliability of price data, {ms('normalization.example.weights.route')} for preparation route, and {ms('normalization.example.weights.performance')} for performance. Co/MgO-La₂O₃ ranks first with a composite score of {ms('normalization.example.rows[0].total_before', '.1f')}, compared with {ms('normalization.example.rows[2].total_before', '.1f')} for Ni/Al₂O₃. The cobalt formulation ranks first in {rb(joint + '.first_rank_share_pct', '.2f')}% of the combined scenarios and has a maximum regret of {rb(joint + '.worst_regret_score_points', '.1f')} score points.

Removing Ru/MgO leaves the other cost estimates unchanged but reduces their range from approximately 1,262 to 1.5 USD/lb. With min–max normalization, the 0.38 USD/lb difference between Co/MgO-La₂O₃ and Ni/Al₂O₃ then produces a larger difference in their cost scores. The composite score for Co/MgO-La₂O₃ decreases to {ms('normalization.example.rows[0].total_after', '.1f')}, whereas that for Ni/Al₂O₃ remains {ms('normalization.example.rows[2].total_after', '.1f')}, reversing their ranking. If the original normalization range is retained, Co/MgO-La₂O₃ remains first. This result is consistent with rank reversal in normalized weighted-sum methods.<sup>11,12</sup> Figure 4(c) reports 100 × (C₁ − C₀)/C₀ for the nine affected families. C₀ and C₁ are the costs of the candidates ranked first before and after removal, respectively, under identical prices and manufacturing assumptions. Negative values indicate a less expensive replacement; remaining candidate costs do not change.

![Figure 4. Ranking sensitivity. (a) First-rank frequencies; the dashed line marks 50%. (b) Families retaining the baseline candidate under each test. (c) Cost differences after candidate removal. PEM, proton exchange membrane; AEM, anion exchange membrane; OER, oxygen evolution reaction; ORR, oxygen reduction reaction; SCR, selective catalytic reduction.](figures-note-2026-09-09/fig4_decision_diagnostics.png)

## Limitations

COMET provides preliminary estimates based on an empirical costing method. Independent validation against industrial cost data has not been performed: the public observations identified did not match library formulations sufficiently in composition, grade, order size, date, and process boundary. Consequently, mean absolute percentage error was not calculated. Rankings also depend on assumed formulations and author-assigned route and performance scores. Environmental data cover a mean of {r('s', 'lca.coverage_mean_pct', '.2f')}% of catalyst mass, with coverage below 50% for {r('s', 'lca.candidates_coverage_below_50_pct')} candidates. Solvent supply, wastewater treatment, and equipment manufacture are excluded from the process inventory. Processing costs use the published 2017 equipment basis with index adjustment; substituted and uncosted operations are identified. Catalyst activity, deactivation, and impacts during use are outside the model's scope. Related studies address cost optimization of synthesis and the economic effects of catalyst lifetime.<sup>13,14</sup> The resulting rankings therefore support screening within the stated assumptions and do not establish overall catalyst performance.

## Data and Software Availability

COMET is distributed under the PolyForm Noncommercial License 1.0.0, which permits noncommercial use and requires a separate license for commercial use; it is not an OSI-approved open-source license. The project repository is https://github.com/hyunjin-kor/COMET, and its concept DOI is 10.5281/zenodo.21451931. This study uses version {r('m', 'project_version')}. [Access to this version and its associated analysis files is to be confirmed by the authors before submission.] The analysis files contain the input price datasets, numerical results, checksums, and scripts used to generate the manuscript and figures. Third-party data remain subject to their respective source terms. Instructions for installation, data collection, and regeneration accompany the software and analysis files.

## Acknowledgments

Funding and other acknowledgments: [to be supplied by the authors].

OpenAI Codex and Anthropic Claude assisted with software development, source review, and manuscript drafting and editing. OpenAI's image-generation tool was used on September 13, 2026 to produce the conceptual illustrations in Figures 1 and 2(a) from specifications supplied by the authors and subsequently to remove lettering. English and Korean labels were added as editable PowerPoint text. The numerical panels and graphical abstract were not produced with image-generation tools. The authors are responsible for the final verification of the calculations, source material, text, and figure labels and for the submitted work.

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
    if total > WORD_LIMIT:
        raise ValueError(f"Word equivalents {total} exceed the {WORD_LIMIT} limit")
    return {
        "target": "Journal of Chemical Information and Modeling, Application Note",
        "word_limit_abstract_text_graphics": WORD_LIMIT,
        "abstract_words": abstract_words,
        "text_words_excluding_references": body_words,
        "graphics": GRAPHICS,
        "graphics_word_equivalent": graphics,
        "total_word_equivalent": total,
        "figure_count": figures,
        "table_count": 0,
        "software_named_in_title": text.startswith("# COMET:"),
        "json_key_references": paper.verify_references(text, run),
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
