"""Build the submission manuscript and SI from one completed, frozen paper run.

No network access or calculation-engine changes. --check compares the complete
rendered documents and validates their JSON-key references and frozen outputs.
"""

import argparse
import hashlib
import io
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper"
DATE = "2026-09-07"
META_NAME = f"submission_metadata_{DATE}.json"
EXTERNAL_NAME = f"../audit/external-cost-validation-{DATE}.json"
REGISTRY_NAME = f"../sources/external-cost-evidence-{DATE}.json"
CONTROLLED_NAME = f"controlled-{DATE}/controlled_cases.json"
CONTROLLED_PROVENANCE = f"controlled-{DATE}/provenance.json"
EVIDENCE_EXTENSION = f"../sources/independent-evidence-access-{DATE}.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matches_snapshot_line_endings(data, expected_sha256):
    """Allow Git's LF/CRLF conversion without relaxing any other source bytes."""
    lf = data.replace(b"\r\n", b"\n")
    return any(hashlib.sha256(value).hexdigest() == expected_sha256
               for value in (data, lf, lf.replace(b"\n", b"\r\n")))


def cell(value):
    return str(value).replace("|", "/").replace("\n", " ")


def key_value(document, key):
    for match in re.finditer(r'([^.[\]]+)|\[(\d+)\]|\["([^"]+)"\]', key):
        plain, index, quoted = match.groups()
        document = document[int(index)] if index is not None else document[quoted or plain]
    return document


class PaperRun:
    def __init__(self, directory):
        self.directory = directory.resolve()
        self.prefix = self.directory.relative_to(PAPER).as_posix()
        self.data = {}
        self.names = {}
        for alias, stem in (("s", "paper_summary"), ("m", "reproduction_manifest"),
                            ("a", "all_families"), ("c", "manufacturing_costs"),
                            ("h", "support_history"), ("t", "table62_reproduction")):
            name = f"{self.prefix}/{stem}_{DATE}.json"
            self.names[alias] = name
            self.data[name] = load(PAPER / name)
        self.summary = self.data[self.names["s"]]
        self.manifest = self.data[self.names["m"]]
        if self.manifest["status"] != "complete" or self.manifest["code_changed_during_run"]:
            raise ValueError("The manuscript requires a complete run with unchanged calculation code")
        if self.manifest["price_basis"] != "reference":
            raise ValueError("The submission uses the reference basis")
        if self.summary["basis_month"] != self.manifest["basis_month"]:
            raise ValueError("Summary and manifest price months differ")
        for output in self.manifest["outputs"]:
            if digest(self.directory / output["file"]) != output["sha256"]:
                raise ValueError(f"Frozen output changed: {output['file']}")
        for kind in ("history", "support_history"):
            entry = self.manifest[kind]
            if digest(self.directory / entry["file"]) != entry["sha256"]:
                raise ValueError(f"Frozen {kind} changed")
        for entry in self.manifest["inputs"]:
            if entry["file"].startswith("backend/data/process_templates/"):
                if not matches_snapshot_line_endings((ROOT / entry["file"]).read_bytes(), entry["sha256"]):
                    raise ValueError(f"SI template source changed: {entry['file']}")
        history = self.data[self.names["h"]]
        series = history["series"]
        dates = sorted({p["date"] for row in series.values() for p in row["points"]})
        self.metadata = {
            "run_directory": self.prefix,
            "basis_month": self.summary["basis_month"],
            "support_series": len(series),
            "support_observations": sum(len(row["points"]) for row in series.values()),
            "support_first_month": dates[0][:7],
            "support_last_month": dates[-1][:7],
            "support_month_count": len(dates),
            "support_counts": {key: len(row["points"]) for key, row in sorted(series.items())},
            "unit_note": "Model conversion constants, not newly measured data",
            "kg_per_lb": 0.453592,
            "kg_per_short_ton": 907.184,
            "source_manifest_sha256": digest(PAPER / self.names["m"]),
        }
        self.data[META_NAME] = self.metadata
        self.names["meta"] = META_NAME
        self.names["e"] = EXTERNAL_NAME
        self.names["er"] = REGISTRY_NAME
        self.data[EXTERNAL_NAME] = load(PAPER / EXTERNAL_NAME)
        self.data[REGISTRY_NAME] = load(PAPER / REGISTRY_NAME)
        if digest(PAPER / REGISTRY_NAME) != self.data[EXTERNAL_NAME]["registry_sha256"]:
            raise ValueError("External evidence registry changed after its comparison audit")
        self.metadata["external_audit_sha256"] = digest(PAPER / EXTERNAL_NAME)
        controlled = load(PAPER / CONTROLLED_NAME)
        provenance = load(PAPER / CONTROLLED_PROVENANCE)
        if digest(PAPER / CONTROLLED_NAME) != provenance['numerical_output_sha256']:
            raise ValueError('Controlled numerical output changed after its recorded run')
        for entry in provenance['input_hashes'][:2]:
            if digest(ROOT / entry['file']) != entry['sha256']:
                raise ValueError('Controlled price snapshot changed')
            if digest(self.directory / Path(entry['file']).name) != entry['sha256']:
                raise ValueError('Controlled study does not use the selected manuscript price snapshots')
        if controlled['seed'] != self.manifest['seed']:
            raise ValueError('Controlled and primary seeds differ')
        self.names['ctrl'] = CONTROLLED_NAME
        self.data[CONTROLLED_NAME] = controlled
        extension = load(PAPER / EVIDENCE_EXTENSION)
        self.names['ext'] = EVIDENCE_EXTENSION
        self.data[EVIDENCE_EXTENSION] = extension
        additional = [row['crossref'] for row in extension['sources'] if 'crossref' in row]
        self.metadata.update(controlled_output_sha256=digest(PAPER / CONTROLLED_NAME),
                             controlled_provenance_sha256=digest(PAPER / CONTROLLED_PROVENANCE),
                             controlled_manufacturing_cases=len(controlled['manufacturing']['rows']),
                             controlled_electrode_cases=len(controlled['electrode']['rows']),
                             additional_primary_papers=len(additional),
                             screened_evidence_total=self.data[EXTERNAL_NAME]['summary']['candidate_case_count'] + len(additional),
                             additional_evidence_sha256=digest(PAPER / EVIDENCE_EXTENSION))

    def ref(self, alias, key, spec=None):
        name = self.names.get(alias, alias)
        if name not in self.data:
            self.data[name] = load(PAPER / name)
        value = key_value(self.data[name], key)
        if spec == "join":
            shown = ", ".join(map(str, value))
        elif value is None:
            shown = "Not estimated"
        else:
            shown = format(value, spec) if spec else str(value)
        return f"{cell(shown)}<!-- {name}:{key} -->"

    def figure(self, number, stem, caption):
        path = f"{self.prefix}/figures/figure{number}_{stem}_{DATE}.png"
        if not (PAPER / path).is_file():
            raise ValueError(f"Missing figure: {path}")
        return f"![Figure {number}. {caption}]({path})"

    def reproduction_command(self):
        prefix = f"docs/paper/{self.prefix}"
        return (
            "python scripts/reproduce_paper.py --price-basis reference "
            f"--month {self.summary['basis_month']} --seed {self.manifest['seed']} "
            f"--date {DATE} --out-dir {prefix} "
            f"--history {prefix}/{self.manifest['history']['file']} "
            f"--support-history {prefix}/{self.manifest['support_history']['file']} "
            f"--live-basis {prefix}/live_basis_{DATE}.json"
        )


def manuscript(run):
    r = run.ref
    f = run.figure
    rows = []
    for i, label in enumerate(("Pt/C", "Ni/Al2O3", "USY-FCC, effective throughput")):
        rows.append(f"| {label} | {r('s', f'table62[{i}].comet_usd_per_lb', '.4f')} | {r('s', f'table62[{i}].published_usd_per_lb', '.2f')} | {r('s', f'table62[{i}].residual_pct', '+.5f' if i == 0 else '+.2f')} |")
    scale_rows = []
    for size in ("2", "20", "200"):
        scale_rows.append(f"| {r('c', f'scales.{size}.order_size_tons')} | {r('s', f'manufacturing.{size}.min_processing_cost_per_lb', '.4f')}–{r('s', f'manufacturing.{size}.max_processing_cost_per_lb', '.4f')} |")
    return f"""# Catalyst manufacturing costs and environmental screening across traceable price states

Authors, affiliations and corresponding-author contact: [to be supplied by the authors].

## Abstract

Catalyst recommendations depend on prices, manufacturing assumptions and the evidence attached to their inputs. We present the Catalyst Overall Manufacturing Estimation Tool (COMET), an independent implementation of published Step Method costing with frozen inputs and reproducible screening analysis. Published CatCost cases are reproduced without fitting material inputs; platinum on carbon agrees to the cent. The reference library connects {r('s', 'candidates')} candidates across {r('s', 'families')} reaction families to declared metal and support-price states. In a controlled balanced-profile comparison, changing source-confidence annotations alone changes {r('ctrl', 'summary.changed_winner_counts.evidence_only')} winners, changing numeric prices alone changes {r('ctrl', 'summary.changed_winner_counts.price_only')}, and changing both changes {r('ctrl', 'summary.changed_winner_counts.combined')}. Combined recommendation changes therefore cannot all be attributed to market movement. Fixed-composition manufacturing scenarios expose discrete scale-class boundaries, while electrode scenarios preserve the distinct area-based cost boundary. Among candidates meeting inventory-coverage conditions, preparation energy contributes a median {r('s', 'lca.route_share_median_pct', '.2f')}% of reported global warming potential. This is a partial inventory result, not complete environmental superiority. Public procurement evidence remains unmatched for independent full-cost validation, so empirical predictive accuracy is unestimated. The study establishes inspectable, conditional screening decisions and identifies which evidence is needed to support stronger manufacturing or sustainability claims.

Keywords: techno-economic analysis; preparation routes; commodity prices; life cycle assessment; multicriteria decision analysis; reproducibility.

## Introduction

Catalyst selection combines composition and preparation with quantities rarely measured on the same basis: manufacturing cost, activity and environmental impact. A literature formulation does not specify its industrial procurement cost. Scale, material grade, delivery terms and the price state can change its apparent economic advantage. A composite recommendation also depends on preferences that must be distinguished from observed catalyst properties.

Published Step Method costing estimates precommercial catalyst prices from materials and unit operations.<sup>1</sup> CatCost subsequently connected early-stage manufacturing cost and environmental assessment.<sup>2</sup> COMET implements this methodology independently, without distributing the original workbook or claiming NREL endorsement. Uncertainty-aware process platforms such as BioSTEAM provide related prior art.<sup>3</sup> The contribution here is a reproducible comparison of catalyst choices under explicit price, route and coverage assumptions, rather than a claim to the first integrated cost-and-environmental model.

We examine whether recommendation changes arise from weighting, historical price states or single-metal cost crossings. An accompanying evidence audit asks which public purchasing observations are actually comparable to the model. Environmental findings concern manufacturing inputs; reaction productivity, lifetime and use-phase benefits remain outside the comparison.

## Methods

### Manufacturing and environmental boundaries

COMET combines materials, scale-appropriate preparation steps, overhead and the published selling-margin correlation. Repeated operations remain repeated; scale fitting substitutes listed equipment without deriving missing hourly rates. Thermal outputs use mass-based catalyst costs. Electrode assemblies use area-based catalyst, ionomer, membrane and substrate ledgers; their powder cost is labelled separately. Figure 1 connects frozen observations to resolved inputs and analysis outputs.

{f(1, 'architecture', 'Frozen source observations, resolved model inputs and research outputs.')}

The published-case calculations retain the original units: one pound corresponds to {r('meta', 'kg_per_lb')} kg and one short ton to {r('meta', 'kg_per_short_ton')} kg under the model's conversion constants. Published materials totals, multiplicities and order sizes are used without target fitting. The FCC effective rate is {r('s', 'table62[2].effective_rate_ton_per_day', '.0f')} short tons/day, following the validation table's footnote. Materials global warming potential (GWP) and cumulative energy demand use the documented metal factors;<sup>4</sup> oxide mappings remain approximations. Modelled route energy is added separately. Missing support factors, solvent supply, wastewater, equipment manufacture and unmodelled coating energy prevent treating these totals as complete inventories.

### Frozen prices and evidence rules

All primary results use reference month {r('s', 'basis_month')}, the latest common completed month among the combined retained series, not an assertion about the latest observation available anywhere upstream. IMF monthly observations and Johnson Matthey daily-to-monthly averages provide the institutional metal history. Uncovered metals retain labelled anchors. The support snapshot contains {r('meta', 'support_series')} HS-code series and {r('meta', 'support_observations')} observations over {r('meta', 'support_first_month')}–{r('meta', 'support_last_month')}. These U.S. import unit values combine all grades and are not catalyst-grade quotations. Only positively weighted, exactly matched public records are accepted; missing observations are neither zero-filled nor interpolated. SI reports each series' availability.

The live comparison reuses a frozen collection made at {r('m', 'live_snapshot.observation_finished_at_utc')}, including its original source times and anchors. It is not a contemporaneous exchange settlement. Changing price basis can change both nominal costs and cost-weighted price-evidence scores. Literature architecture, author-assigned performance/readiness judgements and price-source confidence are distinct inputs. DOI identity or URL reachability alone does not validate a formulation, grade premium or measured performance.

### Sensitivity and external comparison

Balanced, cost-first and evidence-first profiles are accompanied by a composite with performance weight removed. Evidence and route rubrics remain in that composite; it is not a purely measured-cost ranking. The weighting grid contains {r('s', 'weight_sensitivity.grid_points')} combinations. Ties resolve by lower mass cost and then candidate slug. The historical replay spans {r('s', 'volatility.window.first')}–{r('s', 'volatility.window.last')}; series-covered metals move together by calendar month, while short support histories remain fixed at the reference baseline. It therefore measures metal-price sensitivity conditional on the stated support prices.

Single-metal sweeps hold all other prices fixed and identify cost and composite crossings separately. Seed {r('m', 'seed')} is recorded for reproducibility; these analyses use deterministic enumeration, not Monte Carlo sampling. Public procurement and manufacturing evidence is screened for material identity, grade, currency/date, quantity and cost boundary. Ineligible records remain evidence gaps instead of being forced into an error metric.

A controlled follow-up crosses numeric reference/live costs with independently selected reference/live source-confidence annotations for the balanced profile. Composition, route/performance rubrics and decision weights remain fixed. The source-evidence score is recomputed using the selected cost shares. These hybrid states are counterfactual model inputs, not newly observed quotations. Averaging each channel's marginal score change across the other channel's states allocates their interaction and reproduces the endpoint score change; winner counts are not additive causal effects. Further controlled scenarios hold the finished Ni/alumina composition fixed across manufacturing routes and scale boundaries, and vary loading and a hypothetical powder-price multiplier in a catalog-resolved iridium-oxide electrode stack (SI Figure S1).

## Results and discussion

### Published-method reproduction and external validity

Table 1. Published Step Method cases; costs in USD/lb and residuals relative to the published value.

| Case | COMET | Published | Residual (%) |
|---|---:|---:|---:|
{chr(10).join(rows)}

Pt/C rounds to the published cent. The Ni residual follows the published size-dependent margin correlation rather than the validation table's exceptional margin treatment. FCC uses the declared effective throughput. These checks validate reproduction of the method, not manufacturing-price accuracy for a new formulation.

{f(2, 'table62', 'Reproduction of the published cases using declared materials and effective-throughput assumptions.')}

The separate [external evidence audit](../audit/external-cost-validation-{DATE}.md) screened {r('e', 'summary.candidate_case_count')} cases, including {r('e', 'summary.contract_price_count')} signed contract-price schedule and {r('e', 'summary.catalog_pack_price_count')} verified catalog pack offers. The contract states {r('er', 'cases[0].observation.price', '.2f')} EUR/kg on a {r('er', 'cases[0].observation.basis_month')} basis, but does not disclose a matched formulation, catalyst order mass or settled invoice. Catalog pack prices are not bulk quotes. The number of eligible full-cost matches is {r('e', 'summary.matched_full_cost_case_count')}; empirical mean absolute percentage error remains unestimated. These findings distinguish accessible purchasing evidence from validated manufacturing accuracy (SI Table S5).

An extension screened {r('meta', 'additional_primary_papers')} further primary papers, bringing the bounded evidence inventory to {r('meta', 'screened_evidence_total')}. Laboratory activity-based costing of oxide synthesis provides independent methodological context;<sup>5</sup> a separate platinum–strontium titanate TEA explicitly applies CatCost.<sup>6</sup> Neither supplies a matched, independently observed industrial full-cost ledger. The [source review](../sources/independent-evidence-extension-{DATE}.md) records Crossref identity checks, the retrieved DOE author copy and publisher/SI access limitations. No new prices or empirical error estimate were imported.

### Environmental contribution and coverage

Among {r('s', 'lca.route_share_eligible_candidates')} eligible candidates with positive reported GWP, modelled route energy contributes a median {r('s', 'lca.route_share_median_pct', '.2f')}%, an upper-decile value of {r('s', 'lca.route_share_p90_pct', '.2f')}% and a maximum of {r('s', 'lca.route_share_max_pct', '.2f')}%. Eligibility requires at least half the materials mass to have factors and a reported process contribution. This finding supports inspecting raw materials first within that covered subset; it cannot be transferred to support-dominated cases with missing factors.

Mean materials coverage is {r('s', 'lca.coverage_mean_pct', '.2f')}%, median coverage is {r('s', 'lca.coverage_median_pct', '.2f')}%, and {r('s', 'lca.candidates_coverage_below_50_pct')} candidates fall below half coverage. Figure 3 marks this divided completeness and uses thermal mass costs. It does not define a complete environmental Pareto frontier.

{f(3, 'gwp_cost', 'Reported GWP versus thermal catalyst cost, with incomplete materials coverage identified.')}

### Weight sensitivity

The balanced winner remains first on a median {r('s', 'weight_sensitivity.median_balanced_winner_share_pct', '.2f')}% of grid points, ranging from {r('s', 'weight_sensitivity.min_balanced_winner_share_pct', '.2f')}% to {r('s', 'weight_sensitivity.max_balanced_winner_share_pct', '.2f')}%. In {r('s', 'weight_sensitivity.families_below_50_pct')} families retention is below half. Removing performance weight changes {r('s', 'weight_sensitivity.performance_zero_changes')} reference-state winners. These results quantify sensitivity to declared preferences, not experimentally estimated utility or catalyst activity.

{f(4, 'weight_sensitivity', 'Retention of the balanced-profile winner across the declared weighting grid.')}

### Historical and live-versus-reference changes

Across {r('s', 'volatility.window.states')} monthly states, the balanced recommendation changes in {r('s', 'volatility.families_flipping_balanced')} families and the performance-free composite in {r('s', 'volatility.families_flipping_performance_zero')}. The latter families are {r('s', 'volatility.flipping_families_performance_zero', 'join')}. Composition, route and author-assigned screening judgements remain fixed; the monthly sequence is a response to price states, not evidence of changes in catalyst performance or availability.

Switching from the monthly reference state to the frozen live tier changes {r('s', 'live_reference_comparison.changed_by_profile.balanced')} balanced, {r('s', 'live_reference_comparison.changed_by_profile.cost-first')} cost-first, {r('s', 'live_reference_comparison.changed_by_profile.evidence-first')} evidence-first and {r('s', 'live_reference_comparison.changed_by_profile.performance_zero')} performance-free winners. The evidence-first changes include the effect of source-confidence categories and cost weighting. Consequently, these counts cannot be attributed solely to metal-price movement.

The controlled balanced-profile comparison identifies {r('ctrl', 'summary.changed_winner_counts.evidence_only')} changed winners when only source annotations change, {r('ctrl', 'summary.changed_winner_counts.price_only')} when only numeric prices change, and {r('ctrl', 'summary.changed_winner_counts.combined')} when both change. Evidence-only changes occur in {r('ctrl', 'summary.changed_winners.evidence_only', 'join')}; the price-only change occurs in {r('ctrl', 'summary.changed_winners.price_only', 'join')}. This decomposition separates the two channels within the model. The reference and live states differ in dates and support-price basis, so it is not a same-date causal estimate of market movement. These counts are distinct from the historical metal-series replay above.

{f(5, 'live_reference', 'Winner changes by decision profile between the frozen live and monthly reference inputs.')}

### Cost and composite-score break-even

The analysis evaluates {r('s', 'breakeven.contests')} distinguishing-metal contests. Of {r('s', 'breakeven.precious_vs_base_sweeps')} precious-versus-base sweeps, {r('s', 'breakeven.precious_cost_crossings')} contain a cost crossing; the median multiplier is {r('s', 'breakeven.precious_cost_crossing_median_factor', '.5f')} relative to the reference metal price. Only {r('s', 'breakeven.precious_cost_crossings_between_0_1_and_10')} crossings lie within the one-tenth-to-tenfold interval; {r('s', 'breakeven.precious_without_cost_crossing_in_scan')} have no crossing within the recorded scan. Absence within a finite scan is not universal dominance.

Composite crossings describe when cost outweighs other normalized criteria. They can occur without changing cost ordering, or remain absent after cost ordering changes. Activity, selectivity and lifetime may justify a manufacturing premium, but this model does not predict them. Figure 6 and the complete sweep ledger distinguish these questions.

{f(6, 'breakeven_sweeps', 'Representative distinguishing-metal cost sweeps; full scan bounds and crossings are retained in JSON.')}

### Manufacturing-method processing ranges

The catalog contains {r('s', 'manufacturing.20.template_count')} thermal methods evaluated at target year {r('s', 'manufacturing.20.target_year')}. Table 2 reports processing-only catalog extremes, excluding materials, overhead, selling margin and omitted operations. These ranges are not confidence intervals for an individual route.

Table 2. Scale-specific processing-cost ranges.

| Order size (short tons) | Processing cost (USD/lb) |
|---|---:|
{chr(10).join(scale_rows)}

Fusion, hydrothermal synthesis, hydrogen reduction, sulfiding and washcoating retain explicit equipment-proxy or missing-operation notes. No new autoclave, reduction-furnace, centrifuge, sieve, coating, freeze-drying, CVD or ALD rate was derived. SI preserves method sources, repeated operations and scale-specific costs.

The controlled route/scale study contains {r('meta', 'controlled_manufacturing_cases')} scenarios. Incipient-wetness selling price changes from {r('ctrl', 'manufacturing.rows[1].selling_usd_per_lb', '.4f')} to {r('ctrl', 'manufacturing.rows[2].selling_usd_per_lb', '.4f')} USD/lb between {r('ctrl', 'manufacturing.rows[1].order_short_tons')} and {r('ctrl', 'manufacturing.rows[2].order_short_tons')} short tons with the finished-material cost held fixed. This step arises from discrete scale classes and nominal production rates, not a measured factory discount or an independently validated economy of scale. Equal activity, precursor retention and yield across routes are not demonstrated.

The {r('meta', 'controlled_electrode_cases')} controlled electrode scenarios retain their area unit. At the baseline powder price, catalog-resolved costs increase from {r('ctrl', 'electrode.rows[3].cost_usd_per_m2', '.2f')} to {r('ctrl', 'electrode.rows[5].cost_usd_per_m2', '.2f')} USD/m² as loading increases from {r('ctrl', 'electrode.rows[3].loading_mg_cm2')} to {r('ctrl', 'electrode.rows[5].loading_mg_cm2')} mg/cm². These are mixed catalog material-stack scenarios, not industrial assembly quotations or designs matched for activity, lifetime or plant throughput. They illustrate the boundary required when interpreting high electrode-area costs alongside powder mass costs.

## Limitations

The library contains {r('s', 'screening_basis_counts.literature_architecture_proxy')} literature-architecture proxies and {r('s', 'screening_basis_counts.engineering_proxy')} engineering proxies, alongside explicitly labelled specialised bases. Source verification is not uniform validation of all compositions. Public contract or catalog observations do not automatically match the model's grade, order size and delivery boundary. All-grade support unit values can differ substantially from catalyst-grade purchases; their short history cannot establish long-run support volatility.

No generic carbon, silica or zeolite LCA factor was inferred from a chemically or geographically different inventory. Missing impacts, scale substitution, throughput, partial inflation indices and recovery scenarios are reported separately rather than combined into an unsupported universal error bar. The analysis excludes deactivation, regeneration, lifetime productivity and use-phase impacts. Monte Carlo bounds elsewhere in the software are user-defined scenarios; deterministic repetition does not establish their empirical distributions.

Controlled model scenarios do not replace independent observations. A prepared external-researcher evaluation protocol has not yet produced participant results; automated browser checks establish software behavior only. Commercial access controls, test counts and repeatable calculations do not establish customer adoption or an empirical accuracy bound. Source-data reuse permissions remain separate from scientific citation and code licensing.

## Conclusions

COMET enables inspectable catalyst screening under fixed sources, preparation assumptions and decision profiles. Materials dominate reported GWP in the sufficiently covered subset, while weights and price basis can change recommendations. Cost crossings require separate interpretation from composite-score crossings. Publishing the selected candidate together with its snapshot, coverage and uncosted operations makes those conclusions reproducible without overstating environmental or procurement accuracy.

## Data and code availability

The [COMET repository](https://github.com/hyunjin-kor/COMET) uses PolyForm Noncommercial 1.0.0, which is not an OSI-approved open-source license. The prepared version is {r('m', 'project_version')}; tag `v1.4.0` is planned, not asserted as published. The project concept DOI [10.5281/zenodo.21451931](https://doi.org/10.5281/zenodo.21451931) identifies the existing deposit, not a newly deposited submission version. No original CatCost workbook or commercial life-cycle database is redistributed.

The existing library nevertheless includes legacy records declaring CatCost workbook/sheet origins. Their presence is disclosed in the [rights register](../commercial/rights-register-{DATE}.md); exclusion of the original workbook does not clear derived-record redistribution. A new release and commercial hosted startup remain gated on data-origin review. Free access to IMF, Comtrade or market websites does not itself confer commercial reuse permission. The retained research artifacts are not a blanket license to redistribute source data or a claim that the proposed company has acquired rights.

The metal-history SHA-256 is {r('m', 'history.sha256')}; the support-history SHA-256 is {r('m', 'support_history.sha256')}. The [manifest]({run.names['m']}) records source snapshots, code/data hashes, package versions and commands. Reproduce this price month and all six analysis figures offline with:

```bash
{run.reproduction_command()}
```

Rebuild the manuscript and SI with `python scripts/build_submission_manuscript.py --directory docs/paper/{run.prefix}`; append `--check` to verify retained documents against their JSON inputs. All computed claims carry file/key references in HTML comments. The original earlier-month manuscript remains a historical artifact; this manuscript, SI and figure set consistently use the run above.

The controlled numerical output SHA-256 is {r('meta', 'controlled_output_sha256')}; its [provenance]({CONTROLLED_PROVENANCE}) records the original analysis code/data hashes and environment. Re-run its additional SI figure using the same frozen states:

```bash
python scripts/run_controlled_cases.py --reference-basis docs/paper/{run.prefix}/reference_basis_{DATE}.json --live-basis docs/paper/{run.prefix}/live_basis_{DATE}.json --out-dir _local/controlled-replay --seed {run.manifest['seed']}
```

The publication format follows the provisional journal review in [the target record](journal-targets-{DATE}.md). Exact JIF year, JCR category/quartile, publication-cost coverage and author approval remain unconfirmed; no submission has occurred.

## Supporting information

Candidate formulations and screening bases, manufacturing methods and scale-specific costs, source/reuse register and support observation availability, error-budget evidence, external procurement comparison eligibility (Markdown); complete analytical outputs, input hashes and environment manifest (JSON); vector and raster analysis figures (SVG and PNG).

## Acknowledgments

Funding, contributions and acknowledgments: [to be supplied by the authors].

OpenAI Codex assisted with software development, source-audit organization and manuscript drafting. Human authors retain responsibility for reviewing the evidence, calculations and submitted text; no AI system is listed as an author.

## Competing interests

Subscription commercialization through a professor-associated company is proposed. The authors must confirm the actual company relationship, ownership, financial interests, institutional permissions and disclosure wording before submission. This draft does not assert an executed license, commercial revenue or an absence of competing interests.

## References

1. Baddour, F. G.; Snowden-Swan, L.; Super, J. D.; Van Allsburg, K. M. Estimating Precommercial Heterogeneous Catalyst Price: A Simple Step-Based Method. *Organic Process Research & Development* **2018**, *22* (12), 1599–1605. [DOI](https://doi.org/10.1021/acs.oprd.8b00245).
2. Van Allsburg, K. M.; Tan, E. C. D.; Super, J. D.; Schaidle, J. A.; Baddour, F. G. Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. *Nature Catalysis* **2022**, *5* (4), 342–353. [DOI](https://doi.org/10.1038/s41929-022-00759-6).
3. Cortes-Peña, Y.; Kumar, D.; Singh, V.; Guest, J. S. BioSTEAM: A Fast and Flexible Platform for the Design, Simulation, and Techno-Economic Analysis of Biorefineries under Uncertainty. *ACS Sustainable Chemistry & Engineering* **2020**, *8* (8), 3302–3310. [DOI](https://doi.org/10.1021/acssuschemeng.9b07040).
4. Nuss, P.; Eckelman, M. J. Life Cycle Assessment of Metals: A Scientific Synthesis. *PLoS ONE* **2014**, *9* (7), e101298. [DOI](https://doi.org/10.1371/journal.pone.0101298).
5. Gkika, D. A.; Kyzas, G. Z. Cost Evidence Yields the Viability of Metal Oxides Synthesis Routes. *ACS Sustainable Chemistry & Engineering* **2025**, *13* (41), 17370–17379. [DOI](https://doi.org/10.1021/acssuschemeng.5c06752).
6. Ferdous, S.; Gracida-Alvarez, U. R.; Ferrandon, M.; Delferro, M.; Benavides, P. T.; Urgun-Demirtas, M. Techno-economic and life cycle analyses of the synthesis of a platinum–strontium titanate catalyst. *Catalysis Science & Technology* **2025**, *15* (15), 4419–4429. [DOI](https://doi.org/10.1039/d5cy00189g).

## TOC graphic

For Table of Contents Only. The editable preview below has a companion RGB TIFF at the specified submission size.

![Traceable price inputs and preparation routes lead to qualified catalyst screening.](submission_toc_{DATE}.svg)
"""


def supporting_information(run):
    r = run.ref
    library = run.data[run.names["a"]]
    catalog = run.data[run.names["c"]]
    lines = [
        "# Supporting information — COMET", "",
        f"Reference month {r('s', 'basis_month')}; seed {r('m', 'seed')}. All tables use the same frozen run as `manuscript_{DATE}.md`.", "",
        "## Table S1. Reaction families and representative candidates", "",
        "These are literature architectures and engineering proxies, not matched activity measurements or commercial quotations. Electrode entries' powder mass costs are distinct from assembly costs per area. Materials coverage denotes matched mass; missing factors do not mean zero environmental impact.", "",
        "| Family | Candidate/domain | Screening basis | Route | Catalyst cost (USD/lb) | Reported GWP (kg CO2-eq/kg) | Materials coverage (%) |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for fi, family in enumerate(library["families"]):
        for ci, candidate in enumerate(family["candidates"]):
            base = f"families[{fi}].candidates[{ci}]"
            fields = [r("a", f"families[{fi}].family"), r("a", base + ".title") + f" (`{candidate['slug']}`; {family['catalyst_domain']})", r("a", base + ".screening_basis"), r("a", base + ".route"), r("a", base + ".landed_cost_per_lb", ".4f"), r("a", base + ".lca.total_gwp", ".4f"), r("a", base + ".lca.coverage_pct", ".2f")]
            lines.append("| " + " | ".join(fields) + " |")
    lines += ["", "## Table S2. Manufacturing methods and processing costs", "",
              "Original steps retain repeats. The frozen JSON also supplies `steps_fitted` and `substitutions`. Costs exclude materials, overhead, selling margin and missing operations. Source labels are transcribed, not newly verified literature recipes. Legacy workbook-origin declarations require a separate rights review; excluding the original workbook does not clear derived-record redistribution.", "",
              "| Method | Original steps | Source and public links | Small (USD/lb) | Medium (USD/lb) | Large (USD/lb) | Proxy/uncosted operations |", "|---|---|---|---:|---:|---:|---|"]
    for i, template in enumerate(catalog["scales"]["20"]["templates"]):
        raw = load(ROOT / f"backend/data/process_templates/{template['id']}.json")
        source = raw.get("source", "Not supplied")
        if source.startswith("CatCost_v"):
            source = "Legacy template label; no public permalink supplied"
        source += "; " + ", ".join(raw.get("reference_urls", []))
        fields = [f"{cell(template['name'])} (`{template['id']}`)", r("c", f"scales.20.templates[{i}].steps", "join"), cell(source)]
        for size in ("2", "20", "200"):
            index = next(j for j, row in enumerate(catalog["scales"][size]["templates"]) if row["id"] == template["id"])
            fields.append(r("c", f"scales.{size}.templates[{index}].processing_cost_per_lb", ".4f"))
        fields.append(r("c", f"scales.20.templates[{i}].uncosted_operations", "join") or "None listed")
        lines.append("| " + " | ".join(fields) + " |")
    lines += ["", "## Table S3. Sources, reuse limits and support series", "",
              "Free access does not imply unrestricted republication. Identifier and HTTP checks establish identity/reachability, not accuracy or a provider-wide license. No paid acquisition, full source article, proprietary workbook or commercial inventory is included.", "",
              "| Source | Role | Reuse and interpretation limit |", "|---|---|---|",
              "| COMET | Independent code and generated analysis | PolyForm Noncommercial 1.0.0; not OSI-approved; commercial use requires separate permission. |",
              "| CatCost publications and User Guide | Method and published regression cases | Academic citation; original workbook excluded; no NREL endorsement. |",
              "| Legacy workbook-origin records | Existing materials/equipment and other retained values | Declared origins remain visible; public-release and commercial-use review unresolved. See the [rights register](../commercial/rights-register-2026-09-07.md). No new blanket redistribution permission. |",
              "| IMF PCPS / Johnson Matthey | Institutional metal history | Retained source labels and dates; provider-wide redistribution permission not inferred. |",
              "| UN Comtrade | HS-code import unit values | Public preview, no credentials. Small analytical record excerpts retain United Nations source attribution; see [source policy](https://uncomtrade.org/docs/policy-on-use-and-re-dissemination/). All-grade indicators are not catalyst-grade quotes. |",
              "| USGS / historical anchors | Metals without monthly series | Source-specific notes retained; anchors are not observed monthly volatility. |",
              "| Public live feeds | Frozen source-priority comparison | Source-specific timestamps and terms retained; no simultaneous settlement claim. |",
              "| Nuss–Eckelman factors | Materials GWP/CED | Publication is CC BY 4.0; underlying third-party inventory rights are not conveyed. Unmatched materials remain gaps. |",
              "| Literature and supplier evidence | Candidate architecture and procurement audit | Record-specific licenses, boundaries and confidence; no inferred performance from price-source confidence. |", "",
              f"Full original link/DOI audit: `../sources/provenance-2026-09-06.json`. Focused free-source corrections: `../sources/free-benchmark-validation-2026-09-06.md`; expanded primary-source checks: `../sources/free-benchmark-expansion-{DATE}.md`; qualified LCA evidence: `../sources/free-lca-evidence-2026-09-06.md`. These scopes do not imply full primary verification of the entire library.", "",
              "| Support series | Retained observations | First month | Last month | Reference-month USD/kg | Grade/boundary |", "|---|---:|---|---|---:|---|"]
    history = run.data[run.names["h"]]
    for symbol, row in sorted(history["series"].items()):
        key = f"price_ranges.{symbol}"
        last = len(row["points"]) - 1
        fields = [symbol, r("meta", "support_counts." + symbol), r("h", f"series.{symbol}.points[0].date"), r("h", f"series.{symbol}.points[{last}].date"), r("s", key + ".basis_month_price", ".4f"), cell(row.get("grade_note", "All-grade U.S. import unit value"))]
        lines.append("| " + " | ".join(fields) + " |")
    lines += ["", "The historical metal replay holds the support symbols at their reference baseline because the available support window is shorter than the metal window. Retained support ranges describe only their observed months, not a long-run volatility estimate.", "",
              "## Table S4. Error budget and interpretation limits", "",
              "Contributions below are not independent, fitted error distributions and must not be summed into a universal confidence interval.", "",
              "| Contribution | Quantitative evidence or assumption | Interpretation |", "|---|---|---|",
              f"| Prices | Nickel {r('s', 'price_ranges.Ni.min', '.4f')}–{r('s', 'price_ranges.Ni.max', '.4f')} USD/lb over {r('s', 'price_ranges.Ni.first')}–{r('s', 'price_ranges.Ni.last')}; support window {r('meta', 'support_first_month')}–{r('meta', 'support_last_month')}. | Date-aligned metals preserve co-movement; support trade grades and fixed missing series limit procurement interpretation. |",
              f"| Inflation | Hourly rate multiplier {r('c', 'scales.20.chemppi_escalation')} from basis year {r('c', 'scales.20.basis_year')} to target {r('c', 'scales.20.target_year')}. | Bundled annual indices may be partial observations; hashes identify the actual inputs. |",
              f"| Throughput and scale | Effective FCC rate {r('s', 'table62[2].effective_rate_ton_per_day', '.0f')} short tons/day; cost {r('s', 'table62[2].comet_usd_per_lb', '.4f')} USD/lb. | Nominal and effective operation differ. Equipment substitution is not calibration of industrial utilization. |",
              "| Recovery value | Optional use loss, refining loss and treatment-charge scenario; no new recovery credit in the paper comparison. | Scenario assumptions do not establish real recovery yield; assembly outputs exclude powder recovery credits. |",
              f"| LCA | Mean materials coverage {r('s', 'lca.coverage_mean_pct', '.2f')}%; {r('s', 'lca.candidates_coverage_below_50_pct')} candidates below half. | Carbon, silica and zeolite gaps remain. Missing mass can dominate the actual footprint. |",
              "| Uncosted operations | Table S2 records equipment proxies and missing operations. | No new autoclave, reduction, centrifugation, sieving, coating, freeze-drying, CVD or ALD rate. |",
              "| External validation | Table S5 records comparability and exclusions. | Published method residuals are not empirical accuracy bounds for new purchases. |", "",
              "## Table S5. External cost-evidence eligibility", "",
              f"The [evidence register](../sources/external-cost-evidence-{DATE}.md) retains source locations and original boundaries. Eligible full-cost comparisons: {r('e', 'summary.matched_full_cost_case_count')}; empirical MAPE: {r('e', 'summary.empirical_mape_pct')}. Normalized catalog prices remain arithmetic conversions of small retail packs, not offers for bulk orders. The historical EUR contract amount is not converted to current USD.", "",
              "| Case | Evidence kind | Original price / unit | Catalog normalization (USD/kg) | Exclusion reasons |", "|---|---|---|---:|---|"]
    registry = run.data[REGISTRY_NAME]
    for i, case in enumerate(run.data[EXTERNAL_NAME]["cases"]):
        original_index, original = next((j, row) for j, row in enumerate(registry["cases"]) if row["id"] == case["id"])
        observation = original.get("observation") or {}
        original_price = "No standalone comparable price"
        if "price" in observation:
            original_price = r("er", f"cases[{original_index}].observation.price", ".2f") + " " + r("er", f"cases[{original_index}].observation.unit")
        fields = [r("er", f"cases[{original_index}].title"), r("e", f"cases[{i}].evidence_kind"), original_price, r("e", f"cases[{i}].catalog_price_usd_per_kg", ".2f"), r("e", f"cases[{i}].exclusion_reasons", "join")]
        lines.append("| " + " | ".join(fields) + " |")
    lines += ["", f"A further {r('meta', 'additional_primary_papers')} papers are screened in the [extension](../sources/independent-evidence-extension-{DATE}.md). Laboratory ABC/TCO modelling and a separate CatCost-based TEA add context, not matched industrial observations. Full source articles and proprietary inputs were not imported.", "",
              "## Figure S1. Controlled price/evidence, route/scale and electrode scenarios", "",
              f"![Controlled scenario analysis; not empirical manufacturing validation.](controlled-{DATE}/controlled_cases.png)", "",
              f"The crossed balanced-profile design changes {r('ctrl', 'summary.changed_winner_counts.evidence_only')} winners through source annotations alone, {r('ctrl', 'summary.changed_winner_counts.price_only')} through numeric prices alone and {r('ctrl', 'summary.changed_winner_counts.combined')} through both. Each candidate's score decomposition allocates the interaction between the two channels; winner counts are not additive causal effects. Exact weights, rankings, component-cost/evidence state and contributions are retained in the controlled JSON. This is distinct from historical monthly replay.", "",
              "## Table S6. Fixed-composition manufacturing scenarios", "",
              "Finished composition and material-price basis stay fixed. Scale steps are discrete model classes, not measured plant discounts. Equal activity and route-dependent yields are not established.", "",
              "| Route | Order (short tons) | Scale | Materials (USD/lb) | Processing (USD/lb) | Selling (USD/lb) |", "|---|---:|---|---:|---:|---:|"]
    for i, row in enumerate(run.data[CONTROLLED_NAME]['manufacturing']['rows']):
        base = f'manufacturing.rows[{i}]'
        fields = [r('ctrl', f'{base}.{key}', '.4f' if key.endswith('usd_per_lb') else None) for key in
                  ('route_id', 'order_short_tons', 'scale', 'materials_usd_per_lb', 'processing_usd_per_lb', 'selling_usd_per_lb')]
        lines.append('| ' + ' | '.join(fields) + ' |')
    lines += ["", "## Table S7. Electrode material-stack scenarios", "",
              "Retained catalog inputs are not bulk manufacturing quotations. A hypothetical powder-price multiplier and loading vary while other selected inputs remain fixed. These designs are not matched for activity or lifetime and do not add complete industrial assembly costs.", "",
              "| Loading (mg/cm²) | Powder-price multiplier | Cost (USD/m²) |", "|---:|---:|---:|"]
    for i, row in enumerate(run.data[CONTROLLED_NAME]['electrode']['rows']):
        base = f'electrode.rows[{i}]'
        fields = [r('ctrl', f'{base}.{key}', '.2f' if key == 'cost_usd_per_m2' else None) for key in
                  ('loading_mg_cm2', 'powder_price_multiplier', 'cost_usd_per_m2')]
        lines.append('| ' + ' | '.join(fields) + ' |')
    lines += ["", f"Controlled numerical SHA-256: {r('meta', 'controlled_output_sha256')}. The [provenance]({CONTROLLED_PROVENANCE}) records the original input/code hashes and environment; the original frozen primary run remains preserved.", ""]
    return "\n".join(lines)


def toc_graphics():
    """Use the same plotting runtime as the paper, with no new dependency."""
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "comet-submission-toc-2026-09-07"
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    from PIL import Image

    fig, ax = plt.subplots(figsize=(3.25, 1.75), dpi=300)
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set(xlim=(0, 3.25), ylim=(0, 1.75))
    ax.axis("off")
    ax.text(1.625, 1.54, "Traceable catalyst screening", ha="center", fontsize=10, color="#153746")
    for x, title, note, color in ((0.07, "Frozen prices", "Sources\nGrades", "#e5f2f1"), (1.17, "Preparation", "Scale\nOperations", "#eef1f7"), (2.27, "Selection", "Weights\nCoverage", "#fbefd9")):
        ax.add_patch(FancyBboxPatch((x, 0.52), 0.9, 0.77, boxstyle="round,pad=0.015", fc=color, ec="#536d76", lw=0.7))
        ax.text(x + 0.45, 1.08, title, ha="center", fontsize=8, color="#153746")
        ax.text(x + 0.45, 0.72, note, ha="center", fontsize=7, linespacing=1.6, color="#153746")
    for x in (0.98, 2.08):
        ax.annotate("", xy=(x + 0.17, 0.9), xytext=(x, 0.9), arrowprops={"arrowstyle": "->", "lw": 1, "color": "#207c78"})
    ax.text(1.625, 0.28, "Repeatable analysis; qualified conclusions", ha="center", fontsize=7, color="#153746")
    png = io.BytesIO()
    fig.savefig(png, format="png", dpi=300, facecolor="white")
    svg = io.BytesIO()
    fig.savefig(svg, format="svg", metadata={"Date": None}, facecolor="white")
    plt.close(fig)
    output = io.BytesIO()
    Image.open(png).convert("RGB").save(output, format="TIFF", dpi=(300, 300), compression="tiff_lzw")
    return svg.getvalue().decode("utf-8"), output.getvalue()


def verify_references(text, run):
    references = re.findall(r"<!-- ([^<>]+\.json):([^<>]+) -->", text)
    for name, key in references:
        document = run.data.get(name)
        if document is None:
            document = load(PAPER / name)
        key_value(document, key)
    for path in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        if path != f"submission_toc_{DATE}.svg" and not (PAPER / path).is_file():
            raise ValueError(f"Missing image: {path}")
    return len(references)


def word_count(text):
    return len(re.findall(r"\b[\w]+(?:[-–'][\w]+)*\b", re.sub(r"<!--.*?-->", "", text, flags=re.S)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=PAPER / f"submission-{DATE}")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    run = PaperRun(args.directory)
    draft = manuscript(run)
    si = supporting_information(run)
    abstract = draft.split("## Abstract\n\n", 1)[1].split("\n\nKeywords:", 1)[0]
    abstract_words = word_count(abstract)
    if not 150 <= abstract_words <= 300:
        raise ValueError(f"Abstract length {abstract_words} exceeds the provisional Article preparation range")
    text = draft.split("## Abstract\n\n", 1)[1].split("## References", 1)[0]
    text = re.sub(r"^!\[.*$|^\|.*$|^Table [12]\. .*$", "", text, flags=re.M)
    count = word_count(text)
    checks = {
        "basis_month": run.summary["basis_month"],
        "abstract_words": abstract_words,
        "text_words_excluding_tables_figures_references": count,
        "figure_count": 6,
        "table_count": 2,
        "supporting_figure_count": 1,
        "supporting_table_count": 7,
        "target_journal": "ACS Engineering Au (provisional; JCR year/category eligibility unresolved)",
        "abstract_limit": 300,
        "article_limit": None,
        "word_count_note": "Approximate lexical count. No fixed Article main-text/figure cap confirmed in inspected Engineering Au guidance. Six main figures are an editorial choice; the 2200-word Letters rule is not applied.",
        "manuscript_json_key_references": verify_references(draft, run),
        "si_json_key_references": verify_references(si, run),
        "frozen_outputs_verified": len(run.manifest["outputs"]),
        "reproduction_command": run.reproduction_command(),
    }
    toc_svg, tiff = toc_graphics()
    outputs = {
        f"manuscript_{DATE}.md": draft,
        f"si_{DATE}.md": si,
        f"submission_toc_{DATE}.svg": toc_svg,
        META_NAME: json.dumps(run.metadata, ensure_ascii=False, indent=2) + "\n",
        f"submission_manuscript_checks_{DATE}.json": json.dumps(checks, ensure_ascii=False, indent=2) + "\n",
    }
    for name, content in outputs.items():
        path = PAPER / name
        if args.check:
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Generated submission file differs: {name}")
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
    target = PAPER / f"submission_toc_{DATE}.tif"
    if args.check:
        if target.read_bytes() != tiff:
            raise ValueError("Generated TOC TIFF differs")
    else:
        target.write_bytes(tiff)
    print(json.dumps(checks, ensure_ascii=False))


if __name__ == "__main__":
    main()
