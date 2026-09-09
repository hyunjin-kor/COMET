"""Replay paper-method examples without changing prices, formulas or frozen studies."""

import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from backend.core.constants import LB_PER_KG  # noqa: E402
from backend.core.decision_engine import (  # noqa: E402
    _apply_total_scores,
    _economic_scores,
    rank_candidates,
)
from backend.core.recipe_costing import calculate_recipe_materials  # noqa: E402
from backend.core.uncertainty import run_cost_request_monte_carlo  # noqa: E402
from backend.routers.calculator import _prepare_calculation_context  # noqa: E402
from backend.schemas.cost_input import CostCalculationRequest  # noqa: E402

STUDY = ROOT / "docs/paper/robustness-2026-09-08/decision_robustness.json"
EVIDENCE = ROOT / "docs/sources/paper-methods-evidence-2026-09-09.json"
SEED = 20260906


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalization_examples(study):
    rows = []
    example = None
    for family in study["families"]:
        original = deepcopy(family["reference_candidates"])
        weights = family["balanced_weights"]
        _economic_scores(original)
        _apply_total_scores(original, weights)
        winner = rank_candidates(original)[0]["slug"]
        if winner != family["reference_winner"]:
            raise ValueError("Frozen reference winner no longer reproduces")
        for saved in family["candidate_removal"]:
            before = [c for c in original if c["slug"] != saved["removed"]]
            fixed_winner = rank_candidates(before)[0]["slug"]
            after = deepcopy(before)
            _economic_scores(after)
            _apply_total_scores(after, weights)
            new_winner = rank_candidates(after)[0]["slug"]
            if fixed_winner != saved["fixed_scale_winner"] or new_winner != saved["renormalized_winner"]:
                raise ValueError("Frozen removal result no longer reproduces")
            if any(a["summary"] != b["summary"] for a, b in zip(after, before, strict=True)):
                raise ValueError("Normalization changed a cost")
            rows.append({"family": family["family"], "removed": saved["removed"],
                         "reference_winner": winner, "fixed_winner": fixed_winner,
                         "renormalized_winner": new_winner, "changed": new_winner != winner})
            if family["family"] == "ammonia-cracking" and saved["removed"] == "ru-mgo-premium":
                example = {"family": family["family"], "weights": weights,
                           "removed": saved["removed"], "unit": family["unit"],
                           "reference_winner": winner, "renormalized_winner": new_winner,
                           "fixed_winner": fixed_winner,
                           "removed_cost": next(c["summary"]["economics_basis_value"] for c in original
                                                if c["slug"] == saved["removed"]),
                           "rows": [{"slug": a["slug"], "cost": a["summary"]["economics_basis_value"],
                                     "economics_before": b["scores"]["economics"],
                                     "economics_after": a["scores"]["economics"],
                                     "total_before": b["scores"]["total"], "total_after": a["scores"]["total"]}
                                    for a, b in zip(after, before, strict=True)]}
    return {"cases": len(rows), "changed": sum(r["changed"] for r in rows),
            "fixed_changed": sum(r["fixed_winner"] != r["reference_winner"] for r in rows),
            "example": example, "removals": rows,
            "ledger_note": "Totals are recomputed with application rounding; historical removal ledgers retain a carried-forward total field that the original weighted ranking did not use."}


def recipe_example():
    recipe = {"precursor_name": "Synthetic arithmetic precursor", "retained_component_fraction": .25,
              "purity_fraction": .8, "yield_fraction": .5, "price_per_kg": 5,
              "source_note": "Illustrative assumptions, not a supplier quotation or measured synthesis"}
    components = [{"role": "active_metal", "name": "Ni", "wt_pct": 20, "price_per_lb": 10,
                   "recipe_consumption": recipe},
                  {"role": "support", "name": "Al2O3", "wt_pct": 80, "price_per_lb": 2 / LB_PER_KG}]
    consumables = [{"name": "Synthetic net wash consumption", "kg_per_kg_catalyst": 3,
                    "price_per_kg": .5, "source_note": "Illustrative net purchase; no inferred recycling"}]
    result = calculate_recipe_materials(components, consumables)
    expected = .2 / (.25 * .8 * .5) * 5 + .8 * 2 + 3 * .5
    if abs(result["total_materials_cost_per_lb"] * LB_PER_KG - expected) > 3e-6:
        raise ValueError("Purchased mass balance does not close")
    return {"classification": "Synthetic arithmetic demonstration", "components": components,
            "consumables": consumables, "purchased_precursor_kg_per_kg": 2,
            "precursor_usd_per_kg": 10, "support_usd_per_kg": 1.6,
            "consumables_usd_per_kg": 1.5, "total_usd_per_kg": expected, "engine_result": result}


def uncertainty_examples(recipe):
    thermal = {"components": recipe["components"], "consumables": recipe["consumables"],
               "steps": ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"],
               "order_size_tons": 20, "basis_year": 2017, "target_year": 2017}
    electrode = {"catalyst_domain": "electrocatalyst", "application_family": "fuel_cell",
                 "components": [{"role": "active_catalyst", "name": "Pt/C", "wt_pct": 100, "price_per_lb": 100}],
                 "steps": ["membrane_pretreatment"], "order_size_tons": 2,
                 "basis_year": 2017, "target_year": 2017,
                 "electrode_input": {"active_area_cm2": 25, "catalyst_loading_mg_cm2": .5,
                                     "substrate_cost_per_cm2": .1, "membrane_cost_per_cm2": .2}}
    db = create_engine("sqlite://")
    SQLModel.metadata.create_all(db)
    rows = []
    try:
        with Session(db) as session:
            for label, payload, ranges in [
                ("thermal_recipe", thermal, {"active_component_price": (.8, 1.2)}),
                ("electrode_assembly", electrode, {"electrode_adjunct_price": (.8, 1.2)}),
            ]:
                req = CostCalculationRequest.model_validate(payload)
                context = _prepare_calculation_context(req, session)
                args = {"req": req, "context": context, "uncertainties": ranges,
                        "n_simulations": 1000, "seed": SEED}
                first = run_cost_request_monte_carlo(**args)
                if first != run_cost_request_monte_carlo(**args):
                    raise ValueError("Same seed differs")
                fixed = run_cost_request_monte_carlo(**{**args, "uncertainties": {}, "n_simulations": 100})
                if fixed["min"] != fixed["max"] or fixed["mean"] != fixed["baseline"]:
                    raise ValueError("Fixed-input range does not collapse to the point estimate")
                rows.append({"name": label, "classification": "Synthetic scenario; no calibrated distribution",
                             "input": payload, "ranges": ranges, "result": first,
                             "same_seed_equal": True, "fixed_input_point_equal": True})
    finally:
        db.dispose()
    return rows


def build_study():
    source = json.loads(STUDY.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    recipe = recipe_example()
    reported = evidence["nickel_case"]["rows"]
    baseline_yield = reported[0]["yield_pct"]
    yield_case = [{"generation": row["generation"], "yield_pct": row["yield_pct"],
                   "charged_ni_per_recovered_ni": 100 / row["yield_pct"],
                   "fixed_input_yield_cost_ratio_to_gen1": baseline_yield / row["yield_pct"],
                   "reported_materials_cost_usd_per_kg": row["materials_cost_usd_per_kg"]}
                  for row in reported]
    return {"schema_version": 1, "seed": SEED,
            "classification": "Additional method verification; not new industrial accuracy or a changed recommendation model",
            "inputs": {p.relative_to(ROOT).as_posix(): sha(p) for p in (STUDY, EVIDENCE)},
            "normalization": normalization_examples(source), "recipe": recipe,
            "uncertainty": uncertainty_examples(recipe), "published_yield_case": yield_case,
            "yield_case_note": "Published yields are experimental, reported costs are modeled with CatCost. Inverse-yield arithmetic holds all other inputs fixed and does not reproduce their changed-reagent estimates or measure prediction error."}


def figure(study, target):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = study["normalization"]["example"]["rows"]
    labels = ["Co/MgO-La₂O₃", "Ni/MgO-CeO₂", "Ni/Al₂O₃"]
    with plt.rc_context({"font.family": "DejaVu Sans", "svg.hashsalt": "comet-methods-2026-09-09"}):
        fig, ax = plt.subplots(figsize=(8, 4.4), layout="constrained")
        x = list(range(len(rows)))
        ax.bar([v - .2 for v in x], [r["total_before"] for r in rows], .38, label="Original set / fixed reference", color="#37648b")
        ax.bar([v + .2 for v in x], [r["total_after"] for r in rows], .38, label="Ru removed, range recalculated", color="#b66438")
        ax.set_xticks(x, [f"{label}\n${r['cost']:.4f}/lb (unchanged)" for label, r in zip(labels, rows, strict=True)])
        ax.set(ylabel="Composite screening score", ylim=(0, 105), title="The comparison range changes; catalyst costs do not")
        for bar in ax.containers:
            ax.bar_label(bar, fmt="%.1f", padding=3)
        ax.legend(loc="upper center", frameon=False, fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        fig.savefig(target, dpi=170, metadata={"Software": "COMET"})
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        parser.error("Output directory must be new or empty")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    result = build_study()
    output = args.out_dir / "methods_study.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    figure(result, args.out_dir / "normalization_example.png")
    files = [Path(__file__), ROOT / "backend/core/decision_engine.py", ROOT / "backend/core/recipe_costing.py",
             ROOT / "backend/core/uncertainty.py", ROOT / "backend/core/cost_engine.py",
             ROOT / "backend/routers/calculator.py", ROOT / "backend/schemas/cost_input.py"]
    manifest = {"status": "complete", "input_sha256": result["inputs"],
                "code_sha256": {p.relative_to(ROOT).as_posix(): sha(p) for p in files},
                "output_sha256": {p.name: sha(p) for p in sorted(args.out_dir.iterdir())},
                "environment": {"python": platform.python_version(), "packages": {
                    name: importlib.metadata.version(name) for name in ("numpy", "pydantic", "sqlmodel", "matplotlib")}},
                "command": "python scripts/reproduce_paper_methods.py --out-dir <new-empty-directory>"}
    (args.out_dir / "provenance.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "sha256": sha(output),
                      "removal_cases": result["normalization"]["cases"],
                      "changes": result["normalization"]["changed"], "fixed_changes": result["normalization"]["fixed_changed"]}))


if __name__ == "__main__":
    main()
