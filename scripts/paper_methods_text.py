"""Attach verified methods examples to the current manuscript and SI."""

import hashlib
import json
import re


def order_references(draft, si):
    body, tail = draft.split("## References\n\n", 1)
    bibliography, toc = tail.split("## TOC graphic", 1)
    entries = dict(re.findall(r"^(\d+)\. (.+)$", bibliography, flags=re.M))
    cited = list(dict.fromkeys(re.findall(r"<sup>(\d+)</sup>", body)))
    if set(cited) != set(entries):
        raise ValueError("Citations and bibliography entries differ")
    mapping = {old: str(i + 1) for i, old in enumerate(cited)}
    body = re.sub(r"<sup>(\d+)</sup>", lambda m: f"<sup>{mapping[m[1]]}</sup>", body)
    bibliography = "\n".join(f"{mapping[old]}. {entries[old]}" for old in cited)
    si = re.sub(r"main reference (\d+)", lambda m: f"main reference {mapping[m[1]]}", si)
    return body + "## References\n\n" + bibliography + "\n\n## TOC graphic" + toc, si


def extend_methods(draft, si, run, study_path):
    from scripts.build_submission_manuscript import PAPER, ROOT, key_value

    name = study_path.resolve().relative_to(PAPER).as_posix()
    study = json.loads(study_path.read_text(encoding="utf-8"))
    manifest = json.loads((study_path.parent / "provenance.json").read_text(encoding="utf-8"))
    if manifest["status"] != "complete" or study["seed"] != run.manifest["seed"]:
        raise ValueError("Methods supplement is incomplete or its seed differs")
    ranking_source = next(file.removeprefix("docs/paper/") for file in study["inputs"]
                          if file.endswith("/decision_robustness.json"))
    if ranking_source not in run.data:
        raise ValueError("Methods supplement requires its matching robustness study")
    for file, digest in manifest["output_sha256"].items():
        if hashlib.sha256((study_path.parent / file).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Methods supplement output changed: {file}")
    for file, digest in study["inputs"].items():
        if hashlib.sha256((ROOT / file).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Methods supplement input changed: {file}")
    run.data[name] = study
    run.metadata["methods_study_sha256"] = hashlib.sha256(study_path.read_bytes()).hexdigest()
    run.metadata["methods_study_file"] = name

    def r(key, spec=None):
        value = key_value(study, key)
        return f"{format(value, spec) if spec else value}<!-- {name}:{key} -->"

    methods = r"""### Purchased inputs and stochastic scenario boundaries

For a finished component mass fraction $w_i$, the optional purchased-input ledger uses $a_i=w_i/(f_i p_i y_i)$ kg precursor per kg finished catalyst, where $f_i$ is the represented component fraction in the pure precursor, $p_i$ its purchased purity and $y_i$ the retained-component yield. Its cost contribution is $a_i P_i$. Net purchased auxiliaries add $\sum_j q_j P_j$. The ledger replaces the component's reference-price contribution and cannot also apply a precursor markup. Fractions and prices require explicit inputs and a source or assumption note; precursor stoichiometry, losses and recycling are not inferred. These changes affect materials cost, not the currently incomplete environmental inventory (SI Section S9).

The separate uncertainty API multiplies selected inputs by uniform factors within declared bounds. Factors for different parameter groups are sampled independently; components in the same group share a factor. Thermal trials vary role-based prices and order size. Electrode trials vary powder and adjunct prices while area, loading and manufacturing assumptions remain fixed. Precursor content, purity, yield and auxiliary quantities/prices are fixed in this API. Failed trials and their reasons are reported; percentiles cover successful trials only. A seed reproduces these scenarios, not empirical confidence. The main historical/weight analyses remain deterministic enumeration; the synthetic API examples in SI Table S10 are an additional implementation check.

### Economic normalization and comparison-set dependence

For a candidate cost $c_i$ in a common functional unit, the economics score is $E_i=100(c_{\max}-c_i)/(c_{\max}-c_{\min})$, rounded to one decimal. Equal costs receive the same maximum economics score. The composite is the one-decimal rounded weighted sum of economics, evidence, route and performance scores. Consequently the effective sensitivity to a dollar of cost depends on the candidate-set price range, even at unchanged weights. Fixed-reference removal controls retain the original scores. They preserve the ordering of surviving candidates but do not establish an objectively correct preference scale or calibrate the other rubrics. Normalization-dependent rank reversal is established prior methodology;<sup>8</sup> COMET's contribution here is a catalyst-specific diagnosis with retained prices, scores and controls (SI Table S11).

"""
    draft = draft.replace("### Frozen prices and evidence rules", methods + "### Frozen prices and evidence rules", 1)
    intro = ("Cost-responsive experimental synthesis has also been demonstrated for nickel nanoparticles;<sup>9</sup> "
             "process-economic studies explicitly examine catalyst lifetime.<sup>10</sup> Thus neither cost-guided synthesis "
             "nor lifetime sensitivity is claimed as new. The present contribution concerns the linked evidence, boundary "
             "and decision diagnostics tested here. A bounded primary-work comparison, including overlaps and unverified "
             "capabilities, is provided in SI Section S12.\n\n")
    draft = draft.replace("We examine whether recommendation changes", intro + "We examine whether recommendation changes", 1)
    b = "normalization.example.rows"
    example = f"""For ammonia cracking, the Co/MgO-La₂O₃ and Ni/Al₂O₃ candidates retain respective costs of {r(b+'[0].cost', '.4f')} and {r(b+'[2].cost', '.4f')} USD/lb when the expensive Ru alternative is removed. Recomputing the comparison range changes their composite scores from {r(b+'[0].total_before', '.1f')}/{r(b+'[2].total_before', '.1f')} to {r(b+'[0].total_after', '.1f')}/{r(b+'[2].total_after', '.1f')}. Holding the original range fixed retains the Co choice. These are library screening scenarios, not measured relative activities or a change in either catalyst's calculated cost (SI Figure S3).

"""
    draft = draft.replace("## Limitations", example + "## Limitations", 1)
    external = f"""A further accessible experimental synthesis study reports Ni nanoparticle yields of {r('published_yield_case[0].yield_pct', '.1f')}%, {r('published_yield_case[1].yield_pct', '.1f')}% and {r('published_yield_case[2].yield_pct', '.1f')}% for its Gen 1, Gen 2 and Gen 4 procedures.<sup>9</sup> The authors' material costs are modeled, and reagents also change. SI Section S12 therefore uses the yields only to illustrate the inverse-yield term and keeps their reported costs separate. This observation adds experimental synthesis context, not an independent manufacturing-cost validation or a measured lifetime comparison.

"""
    draft = draft.replace("### Environmental contribution and coverage", external + "### Environmental contribution and coverage", 1)
    command = "python scripts/reproduce_paper_methods.py --out-dir _local/methods-replay-new"
    draft = draft.replace("## Supporting information", f"The methods supplement is reproduced offline with `{command}`. Its [manifest]({study_path.parent.name}/provenance.json) records input/output hashes and the execution environment. Pass `--methods-study docs/paper/{name}` when rebuilding or checking this manuscript.\n\n## Supporting information", 1)

    references = """8. Mohammadi, M.; Rezaei, J. Ratio product model: A rank-preserving normalization-agnostic multi-criteria decision-making method. *Journal of Multi-Criteria Decision Analysis* **2023**, *30*, 163–172. [DOI](https://doi.org/10.1002/mcda.1806).
9. Petel, B. E.; Van Allsburg, K. M.; Baddour, F. G. Cost-Responsive Optimization of Nickel Nanoparticle Synthesis. *Advanced Sustainable Systems* **2024**, *8*, 2300030 (published online 2023). [DOI](https://doi.org/10.1002/adsu.202300030).
10. Mendoza Suarez, F.; Tatarchuk, B. Comparative economic analysis of batch vs. continuous manufacturing in catalytic heterogeneous processes: impact of catalyst activity maintenance and materials costs on total costs of manufacturing in the production of fine chemicals and pharmaceuticals. *Journal of Flow Chemistry* **2025**, *15*, 21–38. [DOI](https://doi.org/10.1007/s41981-024-00342-z).

"""
    draft = draft.replace("## TOC graphic", references + "## TOC graphic", 1)
    si += r"""
## Section S9. Purchased-input and thermal price equations

All quantities below refer to finished catalyst mass. With explicit precursor data,

$$a_i=\frac{w_i}{f_i p_i y_i},\qquad C_{\rm materials}=\sum_i a_iP_i+\sum_jq_jP_j.$$

Components without a purchased-input recipe retain their mass-fraction/reference-price calculation. Each purity or retention correction is applied once. The reference metal price is not added again. The optional recipe requires nonzero fractions at most unity, nonnegative prices, and a source/assumption note. Net auxiliary quantities must already reflect any declared recycling; the engine infers none.

For the adopted thermal model, let $H$ be the sum of repeated scale-specific hourly rates, $I$ the ChemPPI ratio relative to the published rate basis, $T$ the synthesis-plus-cleaning campaign time in hours and $M$ the produced mass. Then $C_{\rm processing}=HIT/M$ and $P_{\rm selling}=(C_{\rm materials}+C_{\rm processing})(1+g)(1+s)/(1-m)$, where $g$ is general overhead, $s$ the sales/administration/R&D fraction and $m$ the margin fraction of selling price. These are adopted costing rules, not newly measured coefficients. Missing-operation rates remain unestimated. The optional recovery scenario is reported separately; none is added to the paper's reference comparisons. It does not model repeated regeneration, lifetime output or deactivation.

Environmental coefficients remain attached to finished composition and modeled route energy. The recipe adds no precursor-loss, solvent or wastewater inventory. Electrode assembly uses its area ledger, not the thermal selling-price equation.

### Table S9. Synthetic purchased-input closure

The values are arithmetic assumptions, not market observations: finished Ni fraction 0.20, precursor retained-component fraction 0.25, purity 0.80, yield 0.50 and purchase price USD 5/kg; support fraction 0.80 at USD 2/kg; net auxiliary consumption 3 kg/kg at USD 0.50/kg. Exact inputs are retained in the methods study JSON.

| Quantity | Value |
|---|---:|
"""
    for label, key in [("Purchased precursor (kg/kg catalyst)", "purchased_precursor_kg_per_kg"),
                       ("Precursor cost (USD/kg catalyst)", "precursor_usd_per_kg"),
                       ("Support cost (USD/kg catalyst)", "support_usd_per_kg"),
                       ("Net auxiliary cost (USD/kg catalyst)", "consumables_usd_per_kg"),
                       ("Total materials cost (USD/kg catalyst)", "total_usd_per_kg")]:
        si += f"| {label} | {r('recipe.'+key, '.2f')} |\n"
    si += """
## Table S10. Monte Carlo API verification and scope

These synthetic cases use the declared seed and independent uniform group factors. Only precursor purchase price varies in the thermal example; only adjunct prices vary in the electrode example. All other inputs are fixed. Each case is executed twice with the same seed and once with an empty uncertainty map, which must collapse to its point estimate. Intervals are scenario percentiles, not validated confidence intervals.

| Case | Unit | Successful / failed | Point estimate | p5 | p95 |
|---|---|---:|---:|---:|---:|
"""
    for i, row in enumerate(study["uncertainty"]):
        key = f"uncertainty[{i}].result"
        si += f"| {row['name']} | {r(key+'.unit')} | {r(key+'.n_successful')} / {r(key+'.n_failed')} | {r(key+'.baseline')} | {r(key+'.p5')} | {r(key+'.p95')} |\n"
    si += """

The structured API defaults are active-component price 0.70–1.30, promoter/support prices 0.80–1.20, adjunct prices 0.85–1.15 and thermal order size 0.80–1.20 times baseline. Explicit maps fix omitted factors at unity; an empty map fixes all factors. Within-group prices share a draw. Content, purity, retained-component yield, effective production rate and auxiliary quantities/prices stay fixed. In electrode cases, area, loading and assembly manufacturing assumptions also stay fixed. Invalid trials are counted with reasons; an all-failed run is rejected. A sampled scale change applies the same declared equipment substitution as the point estimate; a required operation cannot silently disappear. The legacy flat-input API is a separate bulk-price calculation.

## Table S11. Candidate-set effect at unchanged prices

The fixed-reference control keeps the original cost range. The recalculated-range case removes Ru/MgO and recalculates only economics scores, followed by composite scores. All non-economic scores and weights stay fixed. Costs retain their original mass basis. Displayed totals below are recomputed from the four score components, rather than copied from historical diagnostic ledger fields.

| Candidate | Cost (USD/lb) | Economics before | Economics after | Total before / fixed | Total after |
|---|---:|---:|---:|---:|---:|
"""
    for i, row in enumerate(study["normalization"]["example"]["rows"]):
        key = f"normalization.example.rows[{i}]"
        si += f"| {row['slug']} | {r(key+'.cost', '.4f')} | {r(key+'.economics_before', '.1f')} | {r(key+'.economics_after', '.1f')} | {r(key+'.total_before', '.1f')} | {r(key+'.total_after', '.1f')} |\n"
    si += f"\nReplayed removals: {r('normalization.cases')}; recalculated-range reversals: {r('normalization.changed')}; fixed-reference reversals: {r('normalization.fixed_changed')}. The finite-set comparison exposes a normalization assumption; it does not choose a uniquely valid preference model.\n\n![Figure S3. Original and recomputed scores after removing the Ru alternative; every surviving cost remains unchanged.]({study_path.parent.name}/normalization_example.png)\n"
    si += """
## Section S12. Primary-work overlap and external-evidence boundaries

The [bounded primary-work review](../sources/paper-methods-prior-work-2026-09-09.md) compares eight selected works/tools. It records overlap as well as the specific COMET experiments; an unreported feature is not marked absent. This is not a systematic review or a proof of worldwide priority. DOI identities were checked with Crossref; direct response status and readable access are distinguished in the access record.

### Table S12. Experimental yield context, separate from modeled price

Petel et al., Table 1 (main reference 9), report ICP-OES Ni yields and modeled material costs including support and workup. Their price basis is 2016 USD. The inverse-yield column below computes the charged-Ni requirement per recovered-Ni mass; it does not assume a precursor purity, reconstruct their proprietary price inputs, or reproduce their changed-reagent cost estimates. Gen 3 lacks a reported yield/cost and is excluded. These values do not establish equal catalyst activity or lifetime.

| Published generation | Measured Ni yield (%) | Charged / recovered Ni mass | Reported modeled materials cost (USD/kg catalyst) |
|---|---:|---:|---:|
"""
    for i, row in enumerate(study["published_yield_case"]):
        key = f"published_yield_case[{i}]"
        si += f"| {row['generation']} | {r(key+'.yield_pct', '.1f')} | {r(key+'.charged_ni_per_recovered_ni', '.4f')} | {r(key+'.reported_materials_cost_usd_per_kg', '.2f')} |\n"
    si += "\nThe cited lifetime study is a process-economic scenario with assumed turnover lifetimes; it supplies no matched COMET lifetime measurement. This extension contributes no eligible industrial full-cost match and no participant evaluation. Empirical manufacturing-cost MAPE remains unestimated.\n"
    si = si.replace("Exact inputs are retained in the methods study JSON.",
                    f"Exact inputs are retained in the methods study JSON.<!-- {name}:recipe.components --><!-- {name}:recipe.consumables -->")
    return order_references(draft, si)
