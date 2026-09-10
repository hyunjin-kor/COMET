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
WORD_LIMIT = 5000
GRAPHICS = [
    {"figure": 1, "width": "double", "word_equivalent": 600},
    {"figure": 2, "width": "double", "word_equivalent": 600},
    {"figure": 3, "width": "double", "word_equivalent": 600},
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
    for name in (ROBUSTNESS, METHODS, EXAMPLE):
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

    return f"""# COMET: Software for Traceable Catalyst Manufacturing-Cost Screening with Reproducible Sensitivity Analysis

Authors, affiliations and corresponding-author contact: [to be supplied by the authors].

## Abstract

COMET (Catalyst Overall Manufacturing Estimation Tool) is free desktop and browser software that estimates catalyst manufacturing cost from composition, preparation route and production scale, and shows how a recommendation depends on the price basis, the cost boundary, the comparison set and the weighting. It adopts the published Step Method and CatCost cost basis and reproduces the three published reference cases from their stated inputs; platinum on carbon agrees to the cent. Every price carries its source, quote date and reliability grade, quoted either on a spot basis for current screening or on a fixed monthly average for citable research. The software ships a library of {rb('summary.candidates')} literature candidates across {rb('summary.families')} reaction families, Monte Carlo ranges from a fixed random seed, partial environmental inventories with stated coverage, saved-case comparisons under shared conditions, and a combined enumeration of historical monthly prices and weightings. Analysis scripts record input checksums and the software environment so every reported number can be regenerated. Industrial cost accuracy is not validated; the contribution is that the assumptions behind a screening decision become inspectable.

Keywords: catalyst manufacturing cost; techno-economic screening; price traceability; multicriteria decision analysis; reproducible software.

## Introduction

A catalyst from the literature comes with a composition and a recipe, but not with a manufacturing cost. The published Step Method estimates a precommercial catalyst price from materials and unit operations,<sup>1</sup> and CatCost packages that method with environmental factors in a spreadsheet and web application.<sup>2</sup> Platforms such as BioSTEAM show how process design, techno-economic analysis and uncertainty can be handled in one programmable environment.<sup>3</sup>

What these tools leave to the user is the bookkeeping that decides whether a comparison is fair: which price was used and when it was quoted, whether two candidates were costed on the same functional unit, which operations were never priced, and how much of a composite score comes from a preference rather than a measurement. COMET was written to carry that bookkeeping inside the software. It records the origin and date of every price, keeps spot quotes and fixed monthly averages apart, labels each manufacturing step as priced, substituted or omitted, separates mass-based thermal costs from area-based electrode assemblies, and reports the coverage of every environmental figure. On top of the costing it adds sensitivity analyses: weighting sensitivity, repricing over the historical price record, leave-one-out tests on the comparison set and score sensitivity tests, all of which run from committed input files with recorded hashes.

The cost equations are adopted from the published method and are not claimed as new. The software contribution is the connected workflow, its source traceability and the reproducible analysis layer, delivered as an installable application for researchers who do not maintain a process-simulation environment.

## Implementation

Figure 1 summarises how the software is organised. Price sources feed the two price bases, the cost model turns composition, route and scale into an itemised cost breakdown, and the screening layer ranks the candidate library; the panel on the right lists what is recorded with every value.

![Figure 1. Structure of COMET from price sources to screening; the panel on the right lists what is recorded with every value. The illustration was generated with ChatGPT image generation (OpenAI) from a written specification of the layers, labels and pictograms supplied by the authors, who then redrew the connector lines by script and checked every label.](figures-note-2026-09-09/fig1_workflow_stack.png)

COMET is a local application with no account. The backend is a FastAPI service on Python 3.11 or newer, using SQLModel over a single SQLite file for prices, saved estimates, purchase evidence and actual-cost observations. The user interface is a React 19 and TypeScript single-page application with a Korean and English interface and scientific notation for formulas and units. On Windows an Electron shell bundles the backend with PyInstaller and installs as `COMET.Setup.<version>.exe`, with a portable archive as an alternative. The same application can be served to a browser from source: the interface is built once and the backend serves it on a local port (`npm run web` on Windows, or the equivalent build and `uvicorn` commands elsewhere). The backend tests and the interface build run on Linux in continuous integration, but the authors have exercised the complete browser mode only on Windows. Prices refresh on start-up and once a day, and the price screen can query a fast source while it is open; without API keys the software uses index-adjusted and user-entered prices and works offline.

Figure 2 summarises the cost model. Materials cost is the price-weighted mass of each component, or a purchased-input recipe when the precursor is specified; processing cost follows the Step Method, in which the hourly rates of the selected operations at the fitted scale class, escalated by the chemical producer price index, are multiplied by the campaign time and divided by the mass produced; general and administrative overhead, the sales and R&D uplift and the selling margin are applied as in the published method. Every line of the cost breakdown carries the price used, its source, quote date and reliability grade, the price basis, and whether the operation was priced, substituted or left uncosted. For a 20 wt% Ni/Al₂O₃ catalyst prepared by incipient-wetness impregnation at a {ex('request.order_size_tons', '.0f')} t order on spot prices, the estimate is {ex('step_method.estimated_price_per_lb', '.2f')} USD/lb, of which nickel contributes {ex('materials.components[0].cost_per_lb_cat', '.2f')} USD/lb and processing {ex('step_method.processing_cost_per_lb', '.2f')} USD/lb (Figure 2b); the reference month would price the same nickel at its monthly average instead of the spot quote (Figure 2c). Results export to CSV together with the price evidence and, when requested, the Monte Carlo range.

![Figure 2. Cost model and worked example. (a) Inputs, the three costing stages with their equations, and the cost breakdown that carries the source record of every value. (b) Build-up of the selling price for a 20 wt% Ni/Al₂O₃ catalyst prepared by incipient-wetness impregnation (six operations) at a 20 t order on spot prices, quoted 2026-09-10. (c) Monthly average prices of the platinum-group metals, gold, silver and nickel (Johnson Matthey and IMF PCPS, 2019-01 to 2026-07) with the 2026-05 monthly average used as the reference basis (teal) and the spot quote held in the fixed price package (orange, observed 2026-09-04 to 2026-09-06); the shaded span is the 89-month record repriced in Figure 3. The example in b used the nickel quote of 2026-09-10. Symbols: w mass fraction; c price per lb; f, p, y retained fraction, purity and yield of a purchased input; H hourly rate; T campaign days; I index escalation; M mass produced; g, s, m the overhead, S&ARD and margin fractions.](figures-note-2026-09-09/fig2_cost_model.png)

## Costing model

Materials cost is the mass-weighted sum of component prices in USD per pound of finished catalyst. An optional purchased-input recipe replaces a component's reference price with a mass balance: for a finished mass fraction $w$, a represented-component fraction $f$ in the pure precursor, a purchased purity $p$ and a retained-component yield $y$, the purchased precursor is $w/(f\\,p\\,y)$ kilograms per kilogram of catalyst, priced at the entered purchase price. Net purchased auxiliaries such as solvents and wash liquids add their entered quantity and price. Every fraction requires a source or assumption note; the software infers no stoichiometry, loss or recycling.

Processing cost follows the Step Method. The user picks one of {r('s', 'manufacturing.20.template_count')} named thermal preparation methods (impregnation, coprecipitation, deposition-precipitation, sol-gel, hydrothermal synthesis, ion exchange, fusion, solid-state synthesis, colloidal deposition, combustion synthesis, zeolite and FCC routes, shaping, washcoating, sulfidation and reduction, plus a custom route) or edits the underlying unit operations. Each method is a list of operations from the published equipment table, with repeats preserved. The order size selects a Small, Medium or Large production class with its nominal daily rate and cleaning allowance; an optional effective production rate overrides the nominal rate with a required note, as the published validation table does for a zeolite campaign. Where the equipment table lists a batch or continuous unit at one scale only, the software substitutes the listed equivalent and records the substitution. An operation with no published rate, such as a pressure autoclave or a coating line, is either priced at the nearest listed rate and named as a proxy or left out and listed as uncosted. No hourly rate is invented. Hourly rates are escalated from the published 2017 basis with the chemical producer price index, and general overhead, sales and research fractions and the published size-dependent selling-margin correlation complete the selling price. Electrode assemblies are costed per square centimetre from catalyst loading, ionomer, membrane and substrate inputs with an optional manufacturing scenario; their powder cost is reported separately and never added to the area total. An optional recovery scenario credits spent-metal value under stated use and refining losses.

The environmental block reports global warming potential and cumulative energy demand per kilogram of catalyst as two terms. The materials term uses published cradle-to-gate metal factors;<sup>4</sup> supports without a verified factor are reported as a coverage gap, never estimated. The process term converts the selected route's calcination, drying and mechanical steps to fuel and electricity with public emission factors. Every result states its system boundary and its materials coverage, so a low footprint with low coverage cannot be read as a complete inventory.

## Price evidence

Prices are held on two bases. The spot basis is what the desktop shows for current screening: Johnson Matthey base prices for platinum and palladium, Westmetall settlements for copper and aluminium, exchange futures and public quote pages as fallbacks, and documented anchors for metals without a feed. Each source has a fixed position in the order of preference, and every quote carries its retrieval time. The reference basis is for research: monthly averages from the IMF Primary Commodity Price System and Johnson Matthey daily quotes averaged by month, cut at the latest month both publish, plus U.S. import unit values for {r('meta', 'support_series')} support-material HS codes with {r('meta', 'support_observations')} verified observations. One switch moves the whole application, including the calculator and the library rankings, between the two bases.

Each price also carries a reliability grade with a numeric confidence score, so a candidate's evidence score is the cost-weighted average of its inputs' confidence. Changing the price basis can therefore change both the nominal cost and the evidence score, and the software keeps the two effects visible. Users may attach purchase evidence (supplier, date, quantity, grade, boundary) to a manual price and record actual cost observations against a saved estimate; an observation contributes an error value only when its currency, month, composition, grade, scale, production rate, steps and cost boundary match, and the displayed mean absolute percentage error is null when none qualifies.

## Screening library and decision analysis

The bundled library holds {rb('summary.candidates')} candidates in {rb('summary.families')} reaction families, from ammonia cracking and synthesis to fuel-cell oxygen reduction and electrolyzer oxygen evolution. Each candidate has a composition, a route, a screening basis label ({r('s', 'screening_basis_counts.literature_architecture_proxy')} literature-architecture proxies and {r('s', 'screening_basis_counts.engineering_proxy')} engineering proxies), literature citations and author-assigned route-readiness and performance scores that are explicitly not measurements. A composite score combines four criteria: an economics score that maps the cheapest candidate in the family to 100 and the dearest to 0, the cost-weighted evidence score, the route score and the performance score, under balanced, cost-first and evidence-first weight profiles or user weights. Ties resolve by lower cost in the family's priced functional unit; families with incomplete electrode-assembly inputs compare powder cost for every candidate rather than mixing units.

Three sensitivity analyses accompany a ranking. The weighting analysis evaluates every family on a simplex grid of {r('s', 'weight_sensitivity.grid_points')} weight vectors and reports how often the candidate ranked first under balanced weights keeps that rank (median {r('s', 'weight_sensitivity.median_balanced_winner_share_pct', '.2f')}% across families). A historical repricing re-costs every candidate at each of {r('s', 'volatility.window.states')} monthly metal prices from {r('s', 'volatility.window.first')} to {r('s', 'volatility.window.last')}, with support prices and source annotations held at the reference state, and identifies single-metal break-even prices. A seeded Monte Carlo range multiplies component prices and order size by uniform factors within declared bounds (by default 0.70 to 1.30 for active components, 0.80 to 1.20 for promoters, supports and order size, and 0.85 to 1.15 for electrode adjuncts); components in one role share a draw, failed trials are counted with their reasons, and an omitted seed yields independent samples.

The combined robustness study extends these analyses to the full product of {rb('summary.months')} monthly prices and {rb('summary.weight_points["0.05"]')} weight vectors at a 0.05 increment, or {rb('summary.joint_scenarios_all_families["0.05"]', ',')} family-month-weight cases (Figure 3a,b). It reports how often each candidate ranks first and its mean and worst regret in score points, removes each candidate that does not rank first with and without recomputing the economics range, and moves the author-assigned scores to the least favourable corner of 2, 5 and 10-point bounds. Across the library the candidate ranked first at the reference conditions keeps that rank in a median {rb('summary.reference_winner_joint_share_median_pct', '.2f')}% of cases, removing one candidate changes the leader in {rb('summary.candidate_removal_winner_changes')} of {rb('summary.candidate_removal_cases')} cases, and only {rb('summary.rubric_robust_family_counts["5"]')} families keep the same leader under every 5-point score change. These are properties of the library and its scoring criteria, not forecasts.

Saved estimates can be compared two to four at a time under a shared price basis, order quantity and reference conditions. The comparison reports three values for each estimate: the saved historical result, the same inputs repriced under the shared basis, and the repriced result under the common conditions, so a difference caused by a price update is not confused with a difference caused by the formulation or route.

## Validation and reproducibility

The Step Method implementation is checked against the three published reference cases from their published materials totals, step lists and order sizes, with no input tuned to the target. The platinum on carbon case gives {r('s', 'table62[0].comet_usd_per_lb', '.4f')} against the published {r('s', 'table62[0].published_usd_per_lb', '.2f')} USD/lb. The nickel on alumina case gives {r('s', 'table62[1].comet_usd_per_lb', '.4f')} against {r('s', 'table62[1].published_usd_per_lb', '.2f')} USD/lb ({r('s', 'table62[1].residual_pct', '+.2f')}%), because the software applies the published size-dependent margin correlation where the table's footnote applies a fixed margin. The zeolite cracking catalyst gives {r('s', 'table62[2].comet_usd_per_lb', '.4f')} against {r('s', 'table62[2].published_usd_per_lb', '.2f')} USD/lb ({r('s', 'table62[2].residual_pct', '+.2f')}%) at the table's effective throughput of {r('s', 'table62[2].effective_rate_ton_per_day', '.0f')} short tons per day. Hourly rates, campaign lengths, processing costs, overhead and sales fractions match the table to the cent in all three cases. These checks establish that the method is reproduced; they do not bound the error of a new formulation, for which no condition-matched industrial observation has been found.

The repository carries more than 900 automated tests (907 at the time of writing) covering the engine, the API, the price collectors, the library and the paper scripts, and continuous integration builds and tests the packaged Windows application. The research analyses are deterministic enumerations; repeated runs on one machine produce byte-identical JSON and figures, and each run writes a manifest with SHA-256 checksums of every input, code file and output together with package versions. The reference analyses in this note use price month {r('s', 'basis_month')} and seed {r('m', 'seed')}; the commands, hashes and snapshots are committed with the repository so the numbers here can be regenerated offline.

## Example: ammonia cracking

The ammonia-cracking family illustrates what these analyses add to a cost table. At the reference price month the four candidates cost {ms('normalization.example.rows[0].cost', '.4f')} USD/lb for Co/MgO-La₂O₃, {ms('normalization.example.rows[1].cost', '.4f')} for Ni-MgO/CeO₂, {ms('normalization.example.rows[2].cost', '.4f')} for Ni/Al₂O₃ and {ms('normalization.example.removed_cost', '.4f')} for Ru/MgO. Under the balanced profile (economics {ms('normalization.example.weights.economics')}, evidence {ms('normalization.example.weights.evidence')}, route {ms('normalization.example.weights.route')}, performance {ms('normalization.example.weights.performance')}) the cobalt candidate ranks first with a composite of {ms('normalization.example.rows[0].total_before', '.1f')} against {ms('normalization.example.rows[2].total_before', '.1f')} for Ni/Al₂O₃, and it keeps first rank in {rb(joint + '.first_rank_share_pct', '.2f')}% of the combined price and weighting cases with a worst regret of {rb(joint + '.worst_regret_score_points', '.1f')} points.

Removing the ruthenium candidate changes nothing about the remaining costs, but the economics range shrinks from about 1,262 to about 1.5 USD/lb, so the same 0.38 USD/lb gap between cobalt and nickel now separates the scores. The cobalt composite falls to {ms('normalization.example.rows[0].total_after', '.1f')} while Ni/Al₂O₃ stays at {ms('normalization.example.rows[2].total_after', '.1f')}, and the recommendation reverses (Figure 3c). Holding the original range fixed keeps the cobalt choice. Rank reversal under min-max normalization is a known property of weighted-sum ranking;<sup>5,6</sup> the software's role is to show the user, with the retained prices and scores, that this particular recommendation depends on which alternatives were in the list.

![Figure 3. Sensitivity of the screening ranking, from the fixed analysis package. (a) For each reaction family, the share of the combined price and weighting cases in which the candidate ranked first at the reference conditions, its closest competitor and the remaining candidates rank first. (b) Number of families that keep the same leading candidate under each test: a majority of the combined cases, removal of any one of the other candidates, and score changes of 2, 5 and 10 points in the least favourable direction. (c) Ammonia-cracking composite scores with the full candidate set and after removing the ruthenium candidate; every surviving cost is unchanged and the first-ranked candidate changes.](figures-note-2026-09-09/fig3_decision_diagnostics.png)

## Limitations

COMET estimates costs with an adopted method; it does not measure them. No public observation matched a candidate's composition, grade, order size, date and cost boundary closely enough to compute an empirical error, so the mean absolute percentage error of the model against industrial purchases is unestimated, which is not the same as zero. The library candidates are literature architectures and engineering proxies with author-assigned readiness and performance scores; those scores are inputs to be questioned, and the score sensitivity tests exist for that purpose. Environmental figures are partial inventories: mean materials coverage across the library is {r('s', 'lca.coverage_mean_pct', '.2f')}% and {r('s', 'lca.candidates_coverage_below_50_pct')} candidates fall below half coverage, while solvent supply, wastewater and equipment manufacture are outside the process term. Manufacturing rates come from a 2017 equipment table; operations absent from that table stay uncosted. Cost-responsive synthesis and lifetime economics have been studied elsewhere;<sup>7,8</sup> the software does not model activity, deactivation or use-phase impacts, and a cheaper catalyst is not a better one.

## Availability

Source code, the Windows installer and the portable archive are at https://github.com/hyunjin-kor/COMET under the PolyForm Noncommercial License 1.0.0, which permits free noncommercial use; the license is not OSI-approved, and commercial licenses are available on request from [contact to be supplied by the authors]. The repository is archived under the concept DOI 10.5281/zenodo.21451931. The prepared version is {r('m', 'project_version')}. Windows users run the installer; on other systems the application is served to a browser from source with Python 3.11 or newer and Node.js 22 or newer, as described in the README, with the platform caveat stated above. The backend test suite runs with `python -m pytest backend/tests -q`, and the analyses in this note are regenerated with the commands recorded in the repository's paper index.

## Acknowledgments

Funding, contributions and acknowledgments: [to be supplied by the authors].

OpenAI Codex and Anthropic Claude assisted with software development, source-audit organization, manuscript drafting and editing. ChatGPT image generation (OpenAI) produced the Figure 1 illustration on 2026-09-10 from a specification written by the authors, who edited its connector lines and verified every label; the tool was not used for any other figure or for the graphical abstract. Human authors retain responsibility for reviewing the evidence, calculations and submitted text; no AI system is listed as an author.

## Competing interests

Subscription commercialization through a professor-associated company is proposed. The authors must confirm the actual company relationship, ownership, financial interests, institutional permissions and disclosure wording before submission.

## References

1. Baddour, F. G.; Snowden-Swan, L.; Super, J. D.; Van Allsburg, K. M. Estimating Precommercial Heterogeneous Catalyst Price: A Simple Step-Based Method. *Organic Process Research & Development* **2018**, *22* (12), 1599–1605. [DOI](https://doi.org/10.1021/acs.oprd.8b00245).
2. Van Allsburg, K. M.; Tan, E. C. D.; Super, J. D.; Schaidle, J. A.; Baddour, F. G. Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. *Nature Catalysis* **2022**, *5* (4), 342–353. [DOI](https://doi.org/10.1038/s41929-022-00759-6).
3. Cortes-Peña, Y.; Kumar, D.; Singh, V.; Guest, J. S. BioSTEAM: A Fast and Flexible Platform for the Design, Simulation, and Techno-Economic Analysis of Biorefineries under Uncertainty. *ACS Sustainable Chemistry & Engineering* **2020**, *8* (8), 3302–3310. [DOI](https://doi.org/10.1021/acssuschemeng.9b07040).
4. Nuss, P.; Eckelman, M. J. Life Cycle Assessment of Metals: A Scientific Synthesis. *PLoS ONE* **2014**, *9* (7), e101298. [DOI](https://doi.org/10.1371/journal.pone.0101298).
5. Mohammadi, M.; Rezaei, J. Ratio product model: A rank-preserving normalization-agnostic multi-criteria decision-making method. *Journal of Multi-Criteria Decision Analysis* **2023**, *30*, 163–172. [DOI](https://doi.org/10.1002/mcda.1806).
6. OECD; European Union; Joint Research Centre - European Commission. *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD, 2008. [DOI](https://doi.org/10.1787/9789264043466-en).
7. Petel, B. E.; Van Allsburg, K. M.; Baddour, F. G. Cost-Responsive Optimization of Nickel Nanoparticle Synthesis. *Advanced Sustainable Systems* **2024**, *8* (10), 2300030. [DOI](https://doi.org/10.1002/adsu.202300030).
8. Mendoza Suarez, F.; Tatarchuk, B. Comparative economic analysis of batch vs. continuous manufacturing in catalytic heterogeneous processes: impact of catalyst activity maintenance and materials costs on total costs of manufacturing in the production of fine chemicals and pharmaceuticals. *Journal of Flow Chemistry* **2025**, *15*, 21–38. [DOI](https://doi.org/10.1007/s41981-024-00342-z).
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
