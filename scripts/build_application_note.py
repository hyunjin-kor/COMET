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

    return f"""# COMET: Software for Traceable Catalyst Manufacturing-Cost Screening with Reproducible Sensitivity Analysis

Authors, affiliations and corresponding-author contact: [to be supplied by the authors].

## Abstract

COMET (Catalyst Overall Manufacturing Estimation Tool) estimates catalyst manufacturing costs from composition, preparation route and production scale. The software combines the published Step Method and CatCost cost basis with price-source records and reproducible sensitivity analysis. Implementation checks use three published reference cases without fitting their inputs; the platinum-on-carbon estimate agrees to the reported cent. Price records distinguish current spot quotes from fixed monthly averages and retain their source, date and reliability grade. A library of {rb('summary.candidates')} screening candidates in {rb('summary.families')} reaction families supports comparisons under common cost boundaries and functional units. Seeded Monte Carlo sampling, historical repricing, weighting analysis and candidate-removal tests quantify how specified assumptions affect costs and rankings. Partial environmental inventories report their coverage. Frozen inputs, checksums and recorded software versions support reproduction of the numerical analyses. COMET is implemented as desktop and browser software for preliminary catalyst screening. Agreement with reference calculations establishes implementation consistency; industrial cost accuracy and predictive validity of the candidate rankings remain unvalidated.

Keywords: catalyst manufacturing cost; techno-economic screening; price traceability; multicriteria decision analysis; reproducible software.

## Introduction

Catalyst manufacturing-cost estimates depend on material prices, preparation steps and production scale. The Step Method estimates precommercial catalyst selling prices from material requirements and unit operations.<sup>1</sup> CatCost implements this methodology together with environmental assessment in spreadsheet and web applications.<sup>2</sup> Studies of individual synthesis routes provide complementary cost analyses,<sup>3,4</sup> while BioSTEAM integrates process design, techno-economic analysis and uncertainty assessment in a programmable environment.<sup>5</sup>

Comparing catalyst estimates requires consistent price dates, functional units and manufacturing boundaries. Price-source quality, uncosted operations and subjective scoring criteria introduce additional differences that cannot be represented by a cost value alone. COMET records these inputs alongside each estimate and evaluates their influence on candidate rankings. The software distinguishes spot quotes from fixed monthly averages, reports whether manufacturing operations are priced, substituted or uncosted, and separates mass-based catalyst costs from area-based electrode costs. Environmental results include inventory-coverage measures.

The contribution of COMET is the integration of price provenance, itemized cost calculation and reproducible sensitivity analysis in an installable research tool. The cost equations retain their published attribution. Historical repricing, weighting analysis, candidate-removal tests and criterion-score sensitivity evaluate the dependence of screening results on explicitly specified inputs. These analyses characterize the supplied candidate library and scoring assumptions rather than establish a universally preferred catalyst.

## Software implementation

Figure 1 presents the software organization. Price collection and reference-month selection supply the cost model, which produces itemized estimates for candidate comparison. Price provenance, calculation boundaries and analysis settings are retained with the results.

![Figure 1. Software organization and provenance records in COMET. Price collection, price-basis selection, cost calculation and candidate analysis are linked to the metadata listed in the right-hand panel. The illustration was generated with ChatGPT image generation (OpenAI) from the authors' specification of layers, labels and pictograms. The authors redrew the connector lines by script and verified all labels.](figures-note-2026-09-09/fig1_workflow_stack.png)

COMET runs locally without a user account. A FastAPI backend on Python 3.11 or newer stores prices, estimates and supporting records in SQLite. The React 19 and TypeScript interface supports English and Korean. For Windows distribution, Electron packages the interface with a PyInstaller-built backend; the browser interface can also be launched from source. Backend tests and interface builds run on Linux in continuous integration, whereas complete browser-mode testing has been performed only on Windows. Documented index-adjusted or user-entered prices support operation without API keys and offline use.

The cost model and its outputs are summarized in Figure 2. Each cost entry records the price, source, quote date, reliability grade and price basis, together with the status of the associated manufacturing operation. In the recorded spot-price example, a 20 wt% Ni/Al₂O₃ catalyst prepared by incipient-wetness impregnation at an order size of {ex('request.order_size_tons', '.0f')} short tons has an estimated selling price of {ex('step_method.estimated_price_per_lb', '.2f')} USD/lb. Nickel and processing contribute {ex('materials.components[0].cost_per_lb_cat', '.2f')} and {ex('step_method.processing_cost_per_lb', '.2f')} USD/lb, respectively. This result is specific to the retained price snapshot. Across the thermal families, the lowest-cost candidates differ in their materials, processing and overhead contributions (Figure 2b). CSV exports retain the price evidence and optional Monte Carlo ranges.

![Figure 2. Cost calculation and reference comparisons. (a) Materials and Step Method processing costs are combined with sequential G&A and S&ARD additions and a selling-price-based margin. Order size determines both processing scale and margin. (b) Selling-price contributions of the lowest-cost candidate in each of 23 thermal reaction families at the 2026-05 reference month; values beside the bars are estimated selling prices in USD/lb. (c) Relative deviation, 100 × (estimate − market price)/market price, for the three catalysts in Table 2 of the method paper. The platinum market value excludes platinum content as specified in that table. The zeolite calculation uses the footnoted effective throughput of 67 short tons per day. (d) Historical cost of the reference-leading candidate in each thermal family divided by the corresponding U.S. import unit value for HS 3815 catalytic preparations. These candidates are selected by the reference ranking and need not be the lowest-cost candidates in (b). The nickel, precious-metal and other-active-substance categories contain 4, 3 and 16 families, respectively. The ratio axes are logarithmic. Gaps indicate missing trade observations; no interpolation is applied. Import unit values aggregate catalyst grades, loadings and order sizes and are not formulation-matched validation data. Symbols: w, mass fraction; c, component price per lb; H, summed hourly operation rates at the production scale; T, campaign days; I, index escalation; M, production mass; g, s and m, G&A, S&ARD and selling-margin fractions. The optional purchased-input recipe uses a = w/(f p y), where a is precursor mass per mass of finished catalyst, f is component fraction in the pure precursor, p is purchased purity and y is retained-component yield.](figures-note-2026-09-09/fig2_cost_model.png)

## Cost estimation and environmental screening

Materials cost is the mass-weighted sum of component prices per pound of finished catalyst. An optional purchased-input recipe replaces reference component pricing with an explicit mass balance. For finished-component mass fraction $w$, component fraction $f$ in the pure precursor, purchased purity $p$ and retained-component yield $y$, the precursor requirement is $w/(f\\,p\\,y)$ kilograms per kilogram of catalyst. The entered purchase price is applied to this requirement, and purchased auxiliaries are added from their quantities and prices. Each fraction requires a source note. Stoichiometry, losses and recycling are not inferred automatically.

Processing cost follows the Step Method. The {r('s', 'manufacturing.20.template_count')} thermal preparation templates specify unit operations from the published equipment table, including repeated steps; users may edit the sequence or define a custom route. Order size determines the production class, daily rate and cleaning allowance. An effective production rate may replace the nominal rate when accompanied by a justification. Equipment substitutions use listed equivalents, while unavailable operations use a disclosed proxy rate or remain uncosted. Hourly rates are adjusted from the published 2017 basis using the chemical producer price index. Sequential G&A and S&ARD additions and the published order-size-dependent selling-margin correlation yield the estimated selling price. Electrode-assembly costs use an area basis and include loading, ionomer, membrane and substrate inputs. Powder costs are reported separately to avoid adding costs with different functional units. An optional recovery scenario credits the specified spent-metal value.

Environmental screening reports global warming potential and cumulative energy demand per kilogram of catalyst as materials and process contributions. The materials term uses published cradle-to-gate metal factors;<sup>6</sup> supports without a verified factor are identified as inventory gaps. The process term estimates fuel and electricity requirements for calcination, drying and mechanical operations and applies public emission factors. Results state the system boundary and materials coverage, which must be considered when comparing partial inventories.

## Price sources and provenance

The spot-price basis uses Johnson Matthey base prices for platinum and palladium,<sup>7</sup> Westmetall settlements for copper and aluminium,<sup>8</sup> and exchange futures, public quote pages or documented reference values according to a defined source priority. Records retain retrieval times. The reference basis uses IMF Primary Commodity Price System monthly prices<sup>9</sup> and monthly averages of Johnson Matthey daily quotes at a common reference month. U.S. import unit values<sup>10</sup> provide {r('meta', 'support_series')} support-material HS series with {r('meta', 'support_observations')} verified observations. The selected basis applies to both cost calculations and library rankings. Figure 3 presents the retained monthly metal-price series.

Source-reliability grades are mapped to numeric confidence scores. A candidate's evidence score is the cost-weighted average of its input-price confidence scores; changing the price basis can therefore affect both cost and the evidence criterion. Users may attach purchase records to manual prices and compare saved estimates with observed costs. An observation contributes to the reported error only when currency, month, composition, grade, order size, production rate, operations and cost boundary match. Mean absolute percentage error is reported as unavailable when no observation meets these conditions.

![Figure 3. Monthly metal prices from January 2019 to the May 2026 reference month. (a) Precious metals in USD per troy ounce. (b) Base metals in USD per pound. Both price axes are logarithmic. Element labels are connected to the final observations. Maximum-to-minimum monthly price ratios over the record are 2.3 for zinc, 2.9 for nickel, 6.8 for ruthenium and 11.6 for rhodium. The series are the frozen inputs used for historical repricing.](figures-note-2026-09-09/fig3_metal_prices.png)

## Candidate ranking and sensitivity analysis

The library contains {rb('summary.candidates')} candidates across {rb('summary.families')} reaction families. Records include composition, preparation route, citations, screening basis (including {r('s', 'screening_basis_counts.literature_architecture_proxy')} literature-architecture proxies and {r('s', 'screening_basis_counts.engineering_proxy')} engineering proxies), and author-assigned route-readiness and performance scores. Ranking uses a weighted sum of economics, evidence, route-readiness and performance scores. Within each reaction family, min-max normalization assigns an economics score of 100 to the lowest cost and 0 to the highest cost; all candidates receive 100 when their costs coincide. Balanced, cost-prioritized, evidence-prioritized or user-defined weights determine the composite score. Ties are resolved by cost on the family's functional unit. Families with incomplete electrode inputs are compared on powder cost. The route-readiness and performance scores represent screening assumptions, not experimentally measured performance.

Weighting sensitivity evaluates {r('s', 'weight_sensitivity.grid_points')} weight vectors on a simplex grid. The candidate ranked first under balanced weights retains first rank in a median {r('s', 'weight_sensitivity.median_balanced_winner_share_pct', '.2f')}% of these scenarios across families. Historical repricing evaluates {r('s', 'volatility.window.states')} monthly metal-price states from {r('s', 'volatility.window.first')} to {r('s', 'volatility.window.last')}, with support prices fixed at the reference state, and identifies single-metal break-even prices. Monte Carlo sampling applies uniform multipliers to component prices and order size within specified bounds, including 0.70 to 1.30 for active components by default. Components with the same role share a multiplier. Failed trials and their causes are reported. A specified random seed supports repeatability; omitting it produces independent samples. These ranges describe assumed input variation rather than statistical confidence intervals.

The combined analysis enumerates {rb('summary.months')} monthly price states and {rb('summary.weight_points["0.05"]')} weight vectors at increments of 0.05, yielding {rb('summary.joint_scenarios_all_families["0.05"]', ',')} family-month-weight scenarios (Figure 4a,b). Outputs include first-rank frequency and mean and maximum score regret, defined as the score deficit relative to the highest-scoring candidate in each scenario. Candidate-removal tests exclude each nonleading candidate with and without recalculating the economics range. Criterion-score tests evaluate the least favourable corner of bounds of 2, 5 and 10 points. The reference leader retains first rank in a median {rb('summary.reference_winner_joint_share_median_pct', '.2f')}% of combined scenarios. Removal changes the leader in {rb('summary.candidate_removal_winner_changes')} of {rb('summary.candidate_removal_cases')} tests, and {rb('summary.rubric_robust_family_counts["5"]')} families retain the leader throughout the 5-point score bounds. Scenario frequencies are conditional on this enumeration and are not probabilities of future outcomes.

Saved estimates support comparisons of two to four cases using the stored results, a common price basis, or common prices and manufacturing conditions. These comparisons distinguish price changes from differences in formulation, route and production scale.

## Validation and reproducibility

Implementation verification uses the materials totals, operation lists and order sizes of three published reference cases without fitting the inputs. For platinum on carbon, COMET gives {r('s', 'table62[0].comet_usd_per_lb', '.4f')} versus {r('s', 'table62[0].published_usd_per_lb', '.2f')} USD/lb. For nickel on alumina, the result is {r('s', 'table62[1].comet_usd_per_lb', '.4f')} versus {r('s', 'table62[1].published_usd_per_lb', '.2f')} USD/lb ({r('s', 'table62[1].residual_pct', '+.2f')}%). The latter difference arises from applying the published size-dependent margin correlation instead of the fixed margin specified in the table footnote. The zeolite cracking catalyst gives {r('s', 'table62[2].comet_usd_per_lb', '.4f')} versus {r('s', 'table62[2].published_usd_per_lb', '.2f')} USD/lb ({r('s', 'table62[2].residual_pct', '+.2f')}%) at the footnote's effective production rate of {r('s', 'table62[2].effective_rate_ton_per_day', '.0f')} short tons per day. Intermediate processing and overhead calculations reproduce the tabulated values at the reported precision.

The method paper also reports market prices for these reference catalysts.<sup>1</sup> COMET deviates from the reported prices by {mk('[0].market.comet_vs_market_pct', '.1f')}% for platinum on carbon and {mk('[1].market.comet_vs_market_pct', '.1f')}% for nickel on alumina. For the cracking catalyst, the estimate is {mk('[2].with_published_rate.estimated_price_per_lb', '.4f')} versus a reported price of {mk('[2].market.market_price_per_lb', '.2f')} USD/lb (Figure 2c). Both COMET and the published method estimates are below the three market values. The original study reported agreement within ±20% using prices obtained through personal communications with industry experts. The COMET results fall within that interval, but these observations do not establish the cause of the residuals or the accuracy of estimates for other formulations. Category-level trade statistics provide a separate comparison. U.S. monthly import unit values for HS 3815 subheadings aggregate catalytic preparations by active substance.<sup>10</sup> Figure 2d compares these unit values with historical costs of the reference-leading candidate in each thermal family. The ratios vary across families and months and can differ substantially from unity. Differences in catalyst grade, loading, formulation and order size prevent interpretation of these ratios as formulation-matched validation errors.

The reference cases assess implementation consistency and deviations from three published market prices. The trade comparison provides category-level context. Neither comparison bounds the error of a new formulation, for which no condition-matched industrial observation was identified.

Automated tests cover the calculation engine, API, price collectors and candidate library, and continuous integration tests the packaged Windows application. The research analyses use deterministic enumerations and write SHA-256 manifests for input, code and output files together with package versions. Repeated analyses under the recorded environment reproduce the numerical outputs. The reference calculations in this note use price month {r('s', 'basis_month')} and random seed {r('m', 'seed')}.

## Application to ammonia cracking

Ammonia cracking provides a case study of candidate-set sensitivity. At the reference price month, the estimated costs are {ms('normalization.example.rows[0].cost', '.4f')} USD/lb for Co/MgO-La₂O₃, {ms('normalization.example.rows[1].cost', '.4f')} for Ni-MgO/CeO₂, {ms('normalization.example.rows[2].cost', '.4f')} for Ni/Al₂O₃ and {ms('normalization.example.removed_cost', '.4f')} for Ru/MgO. With balanced weights of {ms('normalization.example.weights.economics')} for economics, {ms('normalization.example.weights.evidence')} for evidence, {ms('normalization.example.weights.route')} for route readiness and {ms('normalization.example.weights.performance')} for performance, Co/MgO-La₂O₃ ranks first with a composite score of {ms('normalization.example.rows[0].total_before', '.1f')}, compared with {ms('normalization.example.rows[2].total_before', '.1f')} for Ni/Al₂O₃. The cobalt candidate retains first rank in {rb(joint + '.first_rank_share_pct', '.2f')}% of the combined price-weight scenarios, with a maximum score regret of {rb(joint + '.worst_regret_score_points', '.1f')} points.

Removing Ru/MgO leaves all surviving candidate costs unchanged but reduces the cost range from approximately 1,262 to 1.5 USD/lb. Recomputing min-max normalization therefore increases the economic-score difference associated with the 0.38 USD/lb cost difference between the cobalt candidate and Ni/Al₂O₃. The cobalt composite decreases to {ms('normalization.example.rows[0].total_after', '.1f')}, whereas the Ni/Al₂O₃ score remains {ms('normalization.example.rows[2].total_after', '.1f')}, reversing their ranking (Figure 4c). Retaining the original normalization range preserves the cobalt candidate's first rank. This behaviour is consistent with known rank reversal in normalized weighted-sum methods.<sup>11,12</sup> The example identifies a dependence on candidate-set normalization without a change in the underlying cost estimates.

![Figure 4. Sensitivity of candidate rankings to price, weighting, candidate-set and criterion-score assumptions. (a) First-rank frequencies across the enumerated price-weight scenarios for the reference leader, the alternative with the highest first-rank frequency, and all other candidates combined. The leading alternative is not necessarily second-ranked at the reference conditions. (b) Number of the 30 reaction families retaining the reference leader under each criterion: first-rank frequency ≥50% in the combined scenarios, removal of any single nonleading candidate, or the least favourable corner of the indicated criterion-score bounds. (c) Reference-price costs of the original leader (open circles) and the leader after candidate removal (filled circles) for the nine families with a rank reversal. Costs are shown on a logarithmic axis. All surviving candidates retain their original costs; removal changes the range used for economic-score normalization. Nearly coincident markers indicate that small cost differences can accompany a change in the highest-ranked candidate. Ammonia cracking is examined in the text.](figures-note-2026-09-09/fig4_decision_diagnostics.png)

## Limitations

COMET estimates preliminary manufacturing costs using an adopted empirical method. No public observation matched a library candidate in composition, grade, order size, date and cost boundary sufficiently to calculate an industrial validation error; mean absolute percentage error is therefore unestimated. Library structures and engineering proxies, together with author-assigned readiness and performance scores, limit the external validity of rankings. Environmental inventories are incomplete: mean materials coverage is {r('s', 'lca.coverage_mean_pct', '.2f')}%, and {r('s', 'lca.candidates_coverage_below_50_pct')} candidates have coverage below 50%. Solvent supply, wastewater and equipment manufacture are excluded from the process term. Processing rates rely on the published 2017 equipment basis, with explicit reporting of substitutions and uncosted operations. Catalyst activity, deactivation and use-phase impacts are outside the model, although cost-responsive synthesis and lifetime economics have been investigated in related work.<sup>13,14</sup> Manufacturing-cost rankings must consequently be interpreted within the stated functional and process boundaries.

## Data and Software Availability

Source code, the Windows installer and the portable archive are at https://github.com/hyunjin-kor/COMET under the PolyForm Noncommercial License 1.0.0, which permits noncommercial use; the license is not OSI-approved, and commercial licences are available on request from the corresponding author. The repository is archived under the concept DOI 10.5281/zenodo.21451931, and this note describes version {r('m', 'project_version')}; beyond Windows it runs in a browser from source with Python 3.11 and Node.js 22 or newer, with the platform caveat above. The frozen price snapshots, the analysis outputs behind every number and figure, their SHA-256 manifests and the regeneration commands are in the repository's paper directory. Metal prices and trade statistics come from the public sources cited in the text and can be re-extracted with the collection scripts in the same repository.

## Acknowledgments

Funding, contributions and acknowledgments: [to be supplied by the authors].

OpenAI Codex and Anthropic Claude assisted with software development, source-audit organization, manuscript drafting and editing. ChatGPT image generation (OpenAI) produced the Figure 1 illustration on 2026-09-10 from a specification written by the authors, who edited its connector lines and verified every label; the tool was not used for any other figure or for the graphical abstract. Human authors retain responsibility for reviewing the evidence, calculations and submitted text; no AI system is listed as an author.

## Competing interests

Subscription commercialization through a professor-associated company is proposed. The authors must confirm the actual company relationship, ownership, financial interests, institutional permissions and disclosure wording before submission.

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
        "count_note": "Lexical count by the shared manuscript checker; graphics use the ACS 300/600 word-equivalent rule. References and the two placeholder lines are excluded from the limit only where the journal excludes them.",
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
