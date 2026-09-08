"""Render the joint robustness experiment into the dated manuscript and SI."""

import hashlib
import json
import re


def extend_manuscript(draft, si, run, directory, date):
    from scripts.build_submission_manuscript import (
        PAPER,
        ROOT,
        key_value,
        reference_snapshot_equivalent,
    )

    prefix = directory.resolve().relative_to(PAPER).as_posix()
    name = f"{prefix}/decision_robustness.json"
    study = json.loads((PAPER / name).read_text(encoding="utf-8"))
    manifest = json.loads((directory / "provenance.json").read_text(encoding="utf-8"))
    if manifest["status"] != "complete" or study["seed"] != run.manifest["seed"]:
        raise ValueError("Robustness run incomplete or seed mismatch")
    for file, digest in manifest["output_sha256"].items():
        if hashlib.sha256((directory / file).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Robustness output changed: {file}")
    reference_file, reference_hash = next((file, digest) for file, digest in manifest["input_source_sha256"].items()
                                         if "/reference_basis_" in file)
    original = ROOT / reference_file
    if hashlib.sha256(original.read_bytes()).hexdigest() != reference_hash:
        raise ValueError("Robustness reference input changed")
    if not reference_snapshot_equivalent(json.loads(original.read_text(encoding="utf-8")),
                                         json.loads((run.directory / f"reference_basis_{date}.json").read_text(encoding="utf-8"))):
        raise ValueError("Robustness and manuscript reference snapshots differ")
    run.data[name] = study

    def r(key, spec=None):
        value = key_value(study, key)
        return f"{format(value, spec) if spec else value}<!-- {name}:{key} -->"

    draft = draft.replace("Ties resolve by lower mass cost and then candidate slug.",
                          "Composite totals are rounded to one decimal before ranking; ties resolve by lower cost in the family's priced functional unit, then candidate slug.")
    draft = draft.replace("their powder cost is labelled separately.",
                          "families with incomplete electrode-assembly inputs explicitly compare catalyst powder costs for every candidate. Complete assembly families retain the area basis. Neither basis establishes equal activity or lifetime.")
    methods = f"""### Joint and structural decision robustness

The OECD/JRC handbook motivates sensitivity to normalization, weights and index assumptions.<sup>7</sup> We extend the separate weight and price screens with their full Cartesian product: {r('summary.months')} synchronous monthly metal states and {r('summary.weight_points["0.05"]')} weight vectors at a {0.05:g} increment. All weight vectors are nonnegative and sum to unity. Reference source annotations, support prices, anchors, compositions and routes remain fixed; cost-weighted evidence is recalculated. We count first ranks and mean/worst regret, defined as the maximum rounded composite minus a candidate's rounded composite in each scenario. Regret has score-point units, not monetary or measured catalytic utility. Equal scenario counts are not future probabilities, and reference metadata in historical counterfactuals preclude a forecast-backtest interpretation.

We repeat the enumeration on the coarser weight grid, delete each nonwinning candidate with and without re-normalization, and stress author-assigned route and performance scores in clipped additive boxes. For each bound, the reference winner moves down while all rivals move up; nonnegative additive weights make this corner the simultaneous worst case against every rival. Bounds are analyst-selected scenarios, not measured score uncertainty. Source data and score definitions are retained in SI so the tests can be independently recomputed.

"""
    draft = draft.replace("## Results and discussion", methods + "## Results and discussion")
    results = f"""### Joint robustness and structural dependence

The finer grid evaluates {r('summary.joint_scenarios_all_families["0.05"]', ',')} family–month–weight scenarios. The reference balanced winner's first-rank share has a median of {r('summary.reference_winner_joint_share_median_pct', '.2f')}%, ranging from {r('summary.reference_winner_joint_share_min_pct', '.2f')}% to {r('summary.reference_winner_joint_share_max_pct', '.2f')}%. It falls below half the enumerated scenarios in {r('summary.families_reference_winner_below_half_joint')} families. This quantifies conditional preference sensitivity; the high end is not a probability of future superiority.

Removing one nonwinning alternative changes the selected winner in {r('summary.candidate_removal_winner_changes')} of {r('summary.candidate_removal_cases')} cases, affecting {r('summary.candidate_removal_families_changed')} families. Holding the original economic scale fixed preserves the reference winner. The reversals therefore expose candidate-set dependence of min–max normalization, not changed chemistry or prices. Candidate rankings should be interpreted within their stated comparison set.

Only {r('summary.rubric_robust_family_counts["2"]')}, {r('summary.rubric_robust_family_counts["5"]')} and {r('summary.rubric_robust_family_counts["10"]')} families retain the balanced choice against every route/performance perturbation in the respective ±2, ±5 and ±10 score-point boxes. Eliciting or experimentally validating these rubric scores could therefore change decisions even when market inputs are precisely known. The largest candidate first-rank-share difference between the two weight grids is {r('summary.grid_refinement_max_share_change_pp', '.2f')} percentage points; these results describe finite grids and do not establish convergence to a continuous preference distribution. SI Figure S2 and Table S8 retain every family's diagnostic, rather than selecting only stable examples.

"""
    draft = draft.replace("## Limitations", results + "## Limitations")
    # Give the new study its place in the abstract without claiming empirical accuracy.
    abstract_start = draft.index("## Abstract\n\n") + len("## Abstract\n\n")
    abstract_end = draft.index("\n\nKeywords:", abstract_start)
    draft = draft[:abstract_start] + f"""Catalyst recommendations depend on prices, manufacturing assumptions and the evidence attached to their inputs. We present the Catalyst Overall Manufacturing Estimation Tool (COMET), an independent implementation of published Step Method costing with frozen inputs and reproducible screening analysis. Published CatCost cases are reproduced without fitting material inputs; platinum on carbon agrees to the cent. The library connects {r('summary.candidates')} candidates across {r('summary.families')} reaction families to traceable price states. Joint enumeration of {r('summary.months')} monthly metal states and {r('summary.weight_points["0.05"]')} preference vectors gives a median reference-winner retention of {r('summary.reference_winner_joint_share_median_pct', '.2f')}%. Removing a nonwinning candidate reverses the selected winner in {r('summary.candidate_removal_families_changed')} families through economic re-normalization. Only {r('summary.rubric_robust_family_counts["5"]')} families remain robust to all route/performance score perturbations within an analyst-selected ±5-point box. These are conditional model results, not future winning probabilities. Controlled price/evidence comparisons and fixed-composition manufacturing scenarios distinguish source annotations and discrete scale assumptions from measured economic advantage. Environmental results remain partial inventories, while electrode assemblies retain their area boundary where input completeness permits it. Public procurement evidence is unmatched for independent full-cost validation, so empirical predictive accuracy remains unestimated. The study provides inspectable decision robustness and identifies which evidence is needed for stronger manufacturing claims.""" + draft[abstract_end:]
    availability = f"""The joint robustness output and its input/source hashes are retained in [{prefix}/provenance.json]({prefix}/provenance.json). Reproduce it with `python scripts/run_decision_robustness.py --out-dir _local/robustness-replay-new --seed 20260906`. Rebuild this manuscript and SI with `python scripts/build_submission_manuscript.py --date {date} --directory docs/paper/submission-{date} --robustness docs/paper/{prefix}`; append `--check` for content/hash verification. Earlier dated packages remain historical evidence; the current package includes the corrected rounded-score and functional-unit tie policy.

"""
    draft = draft.replace("## Supporting information", availability + "## Supporting information")
    draft = draft.replace(f"python scripts/build_submission_manuscript.py --directory docs/paper/submission-{date}`",
                          f"python scripts/build_submission_manuscript.py --date {date} --directory docs/paper/submission-{date} --robustness docs/paper/{prefix}`")
    draft = draft.replace("## TOC graphic", "7. OECD; European Union; Joint Research Centre - European Commission. *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD, 2008. [DOI](https://doi.org/10.1787/9789264043466-en). Crossref and JRC bibliographic identity checked; the handbook provides methodological context, not catalyst-specific validation.\n\n## TOC graphic")
    rows = []
    for i, family in enumerate(study["families"]):
        base = f"families[{i}]"
        win = family["reference_winner"]
        key = f'{base}.joint_grids["0.05"].candidates["{win}"]'
        rows.append(f"| {family['family']} | {family['unit']} | {win} | {r(key + '.first_rank_share_pct', '.2f')} | {r(key + '.mean_regret_score_points', '.3f')} | {r(key + '.worst_regret_score_points', '.1f')} |")
    si += f"""\n## Table S8. Joint historical-price and preference robustness

First-rank frequencies use the finer finite grid. Regret is a composite-score gap, not money. Complete candidate-level ranks, removal ledgers, adverse rubric corners and both weight grids are in [{prefix}/decision_robustness.json]({prefix}/decision_robustness.json); CSV provides all candidates' aggregates.

| Family | Cost unit | Reference balanced choice | First-rank share (%) | Mean regret (points) | Worst regret (points) |
|---|---|---|---:|---:|---:|
{chr(10).join(rows)}

![Figure S2. Finite-grid joint retention and structural diagnostics. Removal bars count families whose selected winner changes; rubric bars count families whose winner survives every stated box perturbation.]({prefix}/decision_robustness.png)
"""
    # External source/rights/journal reviews retain their real verification dates.
    for stem in ("rights-register", "journal-targets", "external-cost-validation",
                 "external-cost-evidence", "independent-evidence-extension"):
        draft = draft.replace(f"{stem}-{date}.md", f"{stem}-2026-09-07.md")
        si = si.replace(f"{stem}-{date}.md", f"{stem}-2026-09-07.md")
    draft = re.sub(r"\nRebuild the manuscript and SI with .*?All computed claims carry file/key references in HTML comments\.",
                   "\nAll computed claims carry file/key references in HTML comments.", draft)
    return draft, si
