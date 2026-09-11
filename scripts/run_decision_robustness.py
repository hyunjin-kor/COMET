"""Enumerate conditional price/preference robustness from preserved paper inputs.

No network, user database, resampling, fitted utility or empirical accuracy claim.
Run: python scripts/run_decision_robustness.py --out-dir <new-directory>
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import sys
from copy import deepcopy
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from backend.core.decision_engine import (  # noqa: E402
    _apply_total_scores,
    _economic_scores,
    _load_catalogs,
    evaluate_benchmark_family,
    rank_candidates,
)
from backend.database import sync_material_library  # noqa: E402
from backend.paths import data_dir  # noqa: E402
from scripts.run_all_families import DIMS, simplex_grid  # noqa: E402

FROZEN = ROOT / "docs/paper/submission-2026-09-07"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                               allow_nan=False) + "\n", encoding="utf-8")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def historical_states(history, baseline):
    """Complete synchronous metal states; preserve baseline source annotations.

    Reject daily/ambiguous input and unit changes rather than claiming monthly
    means. Missing months are not interpolated and future months are excluded.
    """
    cutoff = history["basis_month"]
    series = history["series"]
    if not series:
        raise ValueError("No historical series")
    monthly = {}
    for symbol, entry in sorted(series.items()):
        if symbol.startswith("HS") and entry.get("cadence") == "monthly_unit_value":
            continue  # The prespecified study holds support unit values fixed.
        if entry.get("cadence", history.get("cadence")) != "monthly_average":
            raise ValueError(f"{symbol}: published/normalized monthly averages required")
        if symbol not in baseline or entry["unit"] != baseline[symbol]["unit"]:
            raise ValueError(f"{symbol}: missing baseline or incompatible unit")
        points = {}
        for point in entry["points"]:
            month = point["date"][:7]
            price = float(point["price"])
            if not 0 < price < float("inf"):
                raise ValueError(f"{symbol}: finite positive price required")
            if month in points:
                raise ValueError(f"{symbol}: duplicate month {month}")
            if month <= cutoff:
                points[month] = price
        monthly[symbol] = points
    if not monthly:
        raise ValueError("No monthly metal series")
    months = sorted(set.intersection(*(set(points) for points in monthly.values())))
    if not months or months[-1] != cutoff:
        raise ValueError("No complete monthly window through basis_month")
    states = []
    for month in months:
        prices = deepcopy(baseline)
        for symbol, points in monthly.items():
            prices[symbol]["price"] = points[month]
        states.append((month, prices))
    return states, sorted(monthly)


def ledger(candidates):
    return [{"slug": c["slug"], "scores": dict(c["scores"]),
             "summary": {key: c["summary"][key] for key in (
                 "landed_cost_per_lb", "economics_basis_value", "economics_basis_unit")}}
            for c in candidates]


def joint_grid(states, weights):
    """Exact enumeration; rank counts conserve scenarios for each candidate."""
    ids = sorted(c["slug"] for c in states[0])
    accum = {slug: {"rank_counts": [0] * len(ids), "regret_sum": 0.0,
                    "worst_regret_score_points": 0.0} for slug in ids}
    for candidates in states:
        if sorted(c["slug"] for c in candidates) != ids:
            raise ValueError("Candidate identities differ across states")
        # A family has a single priced functional unit; never mix mass and area.
        if len({c["summary"]["economics_basis_unit"] for c in candidates}) != 1:
            raise ValueError("Mixed functional units within a decision family")
        for w in weights:
            totals = {c["slug"]: round(sum(c["scores"][d] * w[d] for d in DIMS), 1)
                      for c in candidates}
            ranked = rank_candidates(candidates, w)
            best = max(totals.values())
            for pos, c in enumerate(ranked):
                value = accum[c["slug"]]
                value["rank_counts"][pos] += 1
                regret = round(best - totals[c["slug"]], 10)
                value["regret_sum"] += regret
                value["worst_regret_score_points"] = max(value["worst_regret_score_points"], regret)
    count = len(states) * len(weights)
    for value in accum.values():
        value["first_rank_count"] = value["rank_counts"][0]
        value["first_rank_share_pct"] = round(100 * value["first_rank_count"] / count, 6)
        value["mean_regret_score_points"] = round(value.pop("regret_sum") / count, 6)
        value["mean_rank"] = round(sum((i + 1) * n for i, n in enumerate(value["rank_counts"])) / count, 6)
    return {"scenarios": count, "candidates": accum}


def removal_audit(candidates, weights):
    winner = rank_candidates(candidates, weights)[0]["slug"]
    rows = []
    for removed in sorted(c["slug"] for c in candidates if c["slug"] != winner):
        survivors = deepcopy([c for c in candidates if c["slug"] != removed])
        fixed = rank_candidates(survivors, weights)[0]["slug"]
        before = ledger(survivors)
        _economic_scores(survivors)
        _apply_total_scores(survivors, weights)
        recomputed = rank_candidates(survivors, weights)[0]["slug"]
        rows.append({"removed": removed, "fixed_scale_winner": fixed,
                     "renormalized_winner": recomputed, "winner_changed": recomputed != winner,
                     "before": before, "after": ledger(survivors)})
    return rows


def rubric_audit(candidates, weights, bound):
    """Worst case for baseline winner: it moves down, all rivals move up.

    With nonnegative additive weights these box extremes test every pairwise
    challenger simultaneously, including clipping, rounding and cost ties.
    """
    if any(v < 0 for v in weights.values()) or bound < 0:
        raise ValueError("Nonnegative weights and rubric bound required")
    winner = rank_candidates(candidates, weights)[0]["slug"]
    corner = deepcopy(candidates)
    for c in corner:
        for dim in ("route", "performance"):
            c["scores"][dim] = max(0, min(100, c["scores"][dim] + (-bound if c["slug"] == winner else bound)))
    challenger = rank_candidates(corner, weights)[0]["slug"]
    return {"bound_points": bound, "reference_winner": winner,
            "survives_all_box_perturbations": challenger == winner,
            "adverse_corner_winner": challenger, "corner": ledger(corner)}


def run(history, baseline, seed):
    states, varying = historical_states(history, baseline)
    grids = {str(step): simplex_grid(step) for step in (0.1, 0.05)}
    db = create_engine("sqlite://")
    SQLModel.metadata.create_all(db)
    families = []
    try:
        with Session(db) as session:
            sync_material_library(session, force=True)
            for family in sorted(_load_catalogs()):
                reference = evaluate_benchmark_family(session=session, family=family, prices=baseline, basis="reference")
                candidates = reference["candidates"]
                w = reference["decision_profile"]["weights"]
                winner = reference["winner"]["slug"]
                monthly = []
                for month, prices in states:
                    result = evaluate_benchmark_family(session=session, family=family, prices=prices, basis="reference")
                    monthly.append({"month": month, "candidates": ledger(result["candidates"])})
                joints = {step: joint_grid([m["candidates"] for m in monthly], grid)
                          for step, grid in grids.items()}
                reference_grid = joint_grid([ledger(candidates)], grids["0.1"])
                max_difference = max(abs(joints["0.1"]["candidates"][slug]["first_rank_share_pct"]
                                         - joints["0.05"]["candidates"][slug]["first_rank_share_pct"])
                                     for slug in joints["0.1"]["candidates"])
                families.append({"family": family, "domain": reference["catalyst_domain"],
                                 "unit": candidates[0]["summary"]["economics_basis_unit"],
                                 "reference_winner": winner, "balanced_weights": w,
                                 "reference_candidates": ledger(candidates), "monthly_ledgers": monthly,
                                 "reference_price_grid": reference_grid, "joint_grids": joints,
                                 "grid_refinement_max_share_change_pp": round(max_difference, 6),
                                 "candidate_removal": removal_audit(candidates, w),
                                 "rubric_stress": [rubric_audit(candidates, w, b) for b in (2, 5, 10)]})
                print(f"{family}: {len(states)} months, joint retention "
                      f"{joints['0.05']['candidates'][winner]['first_rank_share_pct']:.2f}%", flush=True)
    finally:
        db.dispose()
    shares = [f["joint_grids"]["0.05"]["candidates"][f["reference_winner"]]["first_rank_share_pct"] for f in families]
    removal = [r for f in families for r in f["candidate_removal"]]
    return {"schema_version": 1, "kind": "conditional_model_robustness", "seed": seed,
            "seed_note": "No random draws; exhaustive deterministic enumeration.",
            "method": "Historical numeric metal prices only; fixed reference annotations, support/anchor prices, routes and rubrics; evidence cost shares recomputed. Rounded app scores and functional-unit cost ties. Equal scenario counts are not future probabilities; regret is in score points, not dollars. This is not a forecast backtest or independent industrial validation.",
            "weights": grids, "varying_symbols": varying,
            "fixed_price_symbols": sorted(set(baseline) - set(varying)),
            "price_states": [{"month": month, "prices": {s: p[s]["price"] for s in varying}} for month, p in states],
            "summary": {"families": len(families), "candidates": sum(len(f["reference_candidates"]) for f in families),
                        "months": len(states), "first_month": states[0][0], "last_month": states[-1][0],
                        "weight_points": {step: len(grid) for step, grid in grids.items()},
                        "joint_scenarios_all_families": {step: len(states) * len(grid) * len(families) for step, grid in grids.items()},
                        "reference_winner_joint_share_median_pct": median(shares),
                        "reference_winner_joint_share_min_pct": min(shares),
                        "reference_winner_joint_share_max_pct": max(shares),
                        "families_reference_winner_below_half_joint": sum(s < 50 for s in shares),
                        "candidate_removal_cases": len(removal),
                        "candidate_removal_winner_changes": sum(r["winner_changed"] for r in removal),
                        "candidate_removal_families_changed": sum(any(r["winner_changed"] for r in f["candidate_removal"]) for f in families),
                        "rubric_robust_family_counts": {str(b): sum(next(r for r in f["rubric_stress"] if r["bound_points"] == b)["survives_all_box_perturbations"] for f in families) for b in (2, 5, 10)},
                        "grid_refinement_max_share_change_pp": max(f["grid_refinement_max_share_change_pp"] for f in families)},
            "families": families}


def export(result, out):
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "COMET-decision-robustness"
    import matplotlib.pyplot as plt

    with (out / "candidate_robustness.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["family", "candidate", "functional_unit", "reference_balanced_winner", "joint_scenarios",
                         "first_rank_share_pct", "mean_rank", "mean_regret_score_points", "worst_regret_score_points"])
        for f in result["families"]:
            grid = f["joint_grids"]["0.05"]
            for slug, c in grid["candidates"].items():
                writer.writerow([f["family"], slug, f["unit"], slug == f["reference_winner"], grid["scenarios"],
                                 *[c[k] for k in ("first_rank_share_pct", "mean_rank", "mean_regret_score_points", "worst_regret_score_points")]])
    families = sorted(result["families"], key=lambda f: f["joint_grids"]["0.05"]["candidates"][f["reference_winner"]]["first_rank_share_pct"])
    fig, axes = plt.subplots(1, 2, figsize=(13, 10), layout="constrained")
    positions = list(range(len(families)))
    for step, color, marker in (("0.1", "#b97731", "x"), ("0.05", "#246b80", "o")):
        axes[0].scatter([f["joint_grids"][step]["candidates"][f["reference_winner"]]["first_rank_share_pct"] for f in families], positions,
                        label=f"Weight increment {step}", color=color, marker=marker, s=24)
    axes[0].set(yticks=positions, yticklabels=[f["family"] for f in families], xlim=(0, 101),
                xlabel="Reference balanced winner: first-rank scenario share (%)",
                title="A  Joint historical prices and preferences")
    axes[0].axvline(50, color="#999999", ls=":", lw=0.8)
    axes[0].tick_params(axis="y", labelsize=8)
    axes[0].legend(fontsize=8)
    labels = ["Removal changes winner", "Robust to ±2 points", "Robust to ±5 points", "Robust to ±10 points"]
    counts = [result["summary"]["candidate_removal_families_changed"], *result["summary"]["rubric_robust_family_counts"].values()]
    axes[1].barh(labels, counts, color=["#b97731", "#246b80", "#246b80", "#246b80"])
    axes[1].set(xlim=(0, 32), xlabel="Families (out of 30)", title="B  Candidate set and author-score stress")
    for pos, count in enumerate(counts):
        axes[1].text(count + 0.2, pos, str(count), va="center")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    for suffix in ("png", "svg"):
        fig.savefig(out / f"decision_robustness.{suffix}", dpi=300,
                    metadata={"Date": None} if suffix == "svg" else None)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", type=Path, default=FROZEN / "monthly_history_2026-09-07.json")
    parser.add_argument("--reference-basis", type=Path, default=FROZEN / "reference_basis_2026-09-07.json")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260906)
    args = parser.parse_args()
    if args.out_dir.exists() and (not args.out_dir.is_dir() or any(args.out_dir.iterdir())):
        parser.error("Output directory must be new or empty; preserve existing evidence")
    if data_dir().resolve() != (ROOT / "backend/data").resolve():
        parser.error("Study requires the repository data directory whose hashes are recorded")
    sources = [args.history, args.reference_basis, Path(__file__), ROOT / "scripts/run_all_families.py",
               ROOT / "backend/database.py", ROOT / "backend/paths.py", ROOT / "backend/config.py",
               *sorted((ROOT / "backend/models").glob("*.py")),
               *sorted((ROOT / "backend/core").glob("*.py")), *sorted((ROOT / "backend/data").rglob("*.json"))]
    hashes = {p.resolve().relative_to(ROOT).as_posix() if p.resolve().is_relative_to(ROOT) else p.name: sha256(p) for p in sources}
    history = json.loads(args.history.read_text(encoding="utf-8"))
    baseline = json.loads(args.reference_basis.read_text(encoding="utf-8"))["price_basis"]
    result = run(history, baseline, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "decision_robustness.json", result)
    export(result, args.out_dir)
    after = {p.resolve().relative_to(ROOT).as_posix() if p.resolve().is_relative_to(ROOT) else p.name: sha256(p) for p in sources}
    valid = hashes == after
    write_json(args.out_dir / "provenance.json", {
        "status": "complete" if valid else "failed_source_changed", "python": platform.python_version(),
        "packages": {n: importlib.metadata.version(n) for n in ("sqlmodel", "numpy", "matplotlib")},
        "input_source_sha256": hashes,
        "output_sha256": {p.name: sha256(p) for p in sorted(args.out_dir.iterdir()) if p.is_file()},
    })
    if not valid:
        raise RuntimeError("Input/source changed during execution; outputs invalid")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
