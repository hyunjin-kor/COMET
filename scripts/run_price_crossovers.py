"""Replay all catalyst families with observed prices; no network or user DB writes.

Raw daily quotations stay in _local. The result records model costs and ranks,
input hashes, and explicit observation windows, not a forecast or trading signal.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from copy import deepcopy
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from backend.core.breakeven import feed_symbols  # noqa: E402
from backend.core.decision_engine import (  # noqa: E402
    _load_catalogs,
    evaluate_benchmark_family,
    rank_candidates,
)
from backend.database import sync_material_library  # noqa: E402
from backend.paths import data_dir  # noqa: E402
from scripts.run_decision_robustness import historical_states, ledger  # noqa: E402

FROZEN = ROOT / "docs/paper/submission-2026-09-08"
OLD_STUDY = ROOT / "docs/paper/robustness-2026-09-08/decision_robustness.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def daily_states(snapshot, baseline):
    """Exact date intersection, never monthly aggregates or forward-filled quotes."""
    columns = {}
    for symbol, entry in snapshot["series"].items():
        if entry.get("cadence") != "daily" or entry["unit"] != baseline[symbol]["unit"]:
            raise ValueError(f"{symbol}: daily observations in the baseline unit required")
        column = {}
        for point in entry["points"]:
            day, price = point["date"], float(point["price"])
            if day in column or not 0 < price < float("inf"):
                raise ValueError(f"{symbol}: duplicate date or invalid price")
            column[day] = price
        columns[symbol] = column
    days = sorted(set.intersection(*(set(column) for column in columns.values())))
    if not days:
        raise ValueError("No common observation dates")
    states = []
    for day in days:
        prices = deepcopy(baseline)
        for symbol, column in columns.items():
            prices[symbol]["price"] = column[day]
        states.append((day, prices))
    return states, sorted(columns)


def cost_values(candidates):
    units = {c["summary"]["economics_basis_unit"] for c in candidates}
    if len(units) != 1:
        raise ValueError("Mixed functional units within a family")
    costs = {c["slug"]: float(c["summary"]["economics_basis_value"]) for c in candidates}
    if any(not 0 < value < float("inf") for value in costs.values()):
        raise ValueError("Invalid cost")
    return costs


def continuous_scores(costs, reference, weights, *, fixed_scale=False):
    """Unrounded economics with frozen nonprice scores; optional fixed cost scale.

    The reference-scale sensitivity is deliberately unclipped, so it cannot
    create ties by saturating at 0 or 100. It is not an application score.
    """
    endpoints = cost_values(reference).values() if fixed_scale else costs.values()
    low, high = min(endpoints), max(endpoints)
    return {c["slug"]: weights["economics"] * (100 * (high - costs[c["slug"]]) / (high - low)
                                               if high - low > 1e-9 else 100)
            + sum(weights[d] * c["scores"][d] for d in ("evidence", "route", "performance"))
            for c in reference}


def strict_winner(values, *, lower=False, tolerance=1e-9):
    order = sorted(values, key=lambda slug: (values[slug] if lower else -values[slug], slug))
    margin = abs(values[order[0]] - values[order[1]])
    return order[0] if margin > tolerance else None


def transitions(records, key):
    """Bracket changes between strict winners; ties are retained as a gap."""
    previous = None
    result = []
    for row in records:
        if row[key] is None:
            continue
        if previous and row[key] != previous[key]:
            result.append({"from": previous["date"], "to": row["date"],
                           "before": previous[key], "after": row[key]})
        previous = row
    return result


def pair_crossings(records, slugs, tolerance):
    pairs = []
    for a, b in combinations(sorted(slugs), 2):
        previous = None
        events, gaps = [], []
        for row in records:
            ca, cb = row["costs"][a], row["costs"][b]
            delta = ca - cb
            gaps.append(100 * delta / min(ca, cb))
            if abs(delta) <= tolerance:
                continue
            sign = 1 if delta > 0 else -1
            if previous and sign != previous[1]:
                events.append({"from": previous[0], "to": row["date"]})
            previous = row["date"], sign
        if events:
            pairs.append({"a": a, "b": b, "events": events, "min_gap_pct": min(gaps),
                          "max_gap_pct": max(gaps), "exceeds_one_percent_both_sides": min(gaps) < -1 and max(gaps) > 1})
    return pairs


def record(day, candidates, reference, weights):
    costs = cost_values(candidates)
    frozen = deepcopy(candidates)
    ref = {c["slug"]: c for c in reference}
    for candidate in frozen:
        for dim in ("evidence", "route", "performance"):
            candidate["scores"][dim] = ref[candidate["slug"]]["scores"][dim]
    continuous = continuous_scores(costs, reference, weights)
    fixed_scale = continuous_scores(costs, reference, weights, fixed_scale=True)
    unit = candidates[0]["summary"]["economics_basis_unit"]
    tolerance = 2e-4 if unit == "$/lb" else 2e-6
    cost_winner = strict_winner(costs, lower=True, tolerance=tolerance)
    sorted_costs = sorted(costs.values())
    lead = 100 * (sorted_costs[1] - sorted_costs[0]) / sorted_costs[0]
    app = rank_candidates(candidates, weights)
    app_margin = app[0]["scores"]["total"] - app[1]["scores"]["total"]
    return {"date": day, "costs": costs,
            "scores": {c["slug"]: c["scores"] for c in candidates},
            "cost_winner": cost_winner, "cost_lead_pct": lead,
            "cost_winner_one_percent": cost_winner if lead > 1 else None,
            "app_winner": app[0]["slug"], "app_margin": app_margin,
            "app_strict_winner": app[0]["slug"] if app_margin > 0 else None,
            "frozen_rounded_winner": rank_candidates(frozen, weights)[0]["slug"],
            "continuous_scores": continuous, "continuous_winner": strict_winner(continuous),
            "fixed_scale_scores": fixed_scale, "fixed_scale_winner": strict_winner(fixed_scale)}


def period_summary(records, slugs, unit):
    keys = ("cost_winner", "cost_winner_one_percent", "app_winner", "app_strict_winner",
            "frozen_rounded_winner", "continuous_winner", "fixed_scale_winner")
    return {"observations": len(records), "first": records[0]["date"], "last": records[-1]["date"],
            "transitions": {key: transitions(records, key) for key in keys},
            "winner_counts": {key: {slug: sum(r[key] == slug for r in records)
                                    for slug in slugs if any(r[key] == slug for r in records)} for key in keys},
            "cost_tie_observations": sum(r["cost_winner"] is None for r in records),
            "app_tie_observations": sum(r["app_margin"] == 0 for r in records),
            "pair_crossings": pair_crossings(records, slugs, 2e-4 if unit == "$/lb" else 2e-6)}


def run(daily_path, frozen=FROZEN, old_study=OLD_STUDY):
    if data_dir().resolve() != (ROOT / "backend/data").resolve():
        raise ValueError("Refusing a data directory outside this checkout")
    run_date = frozen.name.removeprefix("submission-")
    baseline_path = frozen / f"reference_basis_{run_date}.json"
    monthly_path = frozen / f"monthly_history_{run_date}.json"
    basis_month = read(baseline_path)["basis_month"]
    baseline = read(baseline_path)["price_basis"]
    old = {f["family"]: f for f in read(old_study)["families"]}
    periods = {"monthly": historical_states(read(monthly_path), baseline),
               "daily": daily_states(read(daily_path), baseline)}
    db = create_engine("sqlite://")
    SQLModel.metadata.create_all(db)
    families = []
    try:
        with Session(db) as session:
            sync_material_library(session, force=True)
            for family in sorted(_load_catalogs()):
                ref = evaluate_benchmark_family(session=session, family=family, prices=baseline, basis="reference")
                candidates = ref["candidates"]
                reference = ledger(candidates)
                if reference != old[family]["reference_candidates"]:
                    raise ValueError(f"{family}: engine no longer reproduces frozen baseline")
                weights = ref["decision_profile"]["weights"]
                unit = candidates[0]["summary"]["economics_basis_unit"]
                row = {"family": family, "title": ref["title"], "domain": ref["catalyst_domain"],
                       "unit": unit, "weights": weights, "reference": reference,
                       "candidates": {c["slug"]: {"title": c["title"], "feeds_wt_pct": feed_symbols(family, c["slug"]),
                                                   "composition": c["estimate"]["input_summary"]["composition"],
                                                   "order_size_tons": c["estimate"]["input_summary"]["order_size_tons"],
                                                   "screening_basis": c["screening_basis"],
                                                   "decision_notes": c["decision_notes"]} for c in candidates},
                       "periods": {}}
                for name, (states, _symbols) in periods.items():
                    records = []
                    for day, prices in states:
                        evaluated = evaluate_benchmark_family(session=session, family=family, prices=prices, basis="reference")
                        if name == "monthly":
                            expected = next(m["candidates"] for m in old[family]["monthly_ledgers"] if m["month"] == day)
                            if ledger(evaluated["candidates"]) != expected:
                                raise ValueError(f"{family}/{day}: frozen monthly ledger mismatch")
                        records.append(record(day, evaluated["candidates"], reference, weights))
                    row["periods"][name] = {"records": records,
                                            "summary": period_summary(records, row["candidates"], unit)}
                families.append(row)
                print(f"{family}: " + "; ".join(f"{p}: cost {len(v['summary']['transitions']['cost_winner'])}, "
                                                  f"score {len(v['summary']['transitions']['continuous_winner'])}"
                                                  for p, v in row["periods"].items()), flush=True)
    finally:
        db.dispose()
    result = {"schema_version": 1, "kind": "conditional_observed_price_replay",
              "method": "All candidates and balanced weights retained; formulations, supports, route costs, order size, price annotations and rubric scores fixed. Monthly: 14 observed metal prices. Daily: 10 observed metal prices; all remaining prices at the " + basis_month + " reference. Exact date intersection; no interpolation. Prices vary, but not output, activity, durability or process revenue. Historical replay of the current model, not a historical recommendation backtest or observed industrial catalyst prices.",
              "score_controls": "Application: rounded score and cost tie-break; frozen rounded: nonprice scores fixed; continuous: additionally remove economics and total score rounding; fixed scale: additionally use the reference-month min/max without clipping. Evidence scores in the application depend on material cost shares. Reference-scale scores are diagnostic and can leave 0–100.",
              "tolerances": {"cost_usd_lb": 0.0002, "cost_usd_cm2": 0.000002,
                             "materiality": "1% of the cheaper modeled cost is a descriptive screen, not an uncertainty bound"},
              "baseline_verified_candidates": sum(len(f["candidates"]) for f in families),
              "monthly_ledgers_verified": sum(len(f["periods"]["monthly"]["records"]) for f in families),
              "inputs": {"baseline": {"path": str(baseline_path.relative_to(ROOT)), "sha256": sha256(baseline_path)},
                         "monthly": {"path": str(monthly_path.relative_to(ROOT)), "sha256": sha256(monthly_path)},
                         "daily": {"path": str(daily_path.resolve().relative_to(ROOT)), "sha256": sha256(daily_path)}},
              "periods": {name: {"observations": len(states), "first": states[0][0], "last": states[-1][0],
                                 "varying_symbols": symbols, "fixed_symbols": sorted(set(baseline) - set(symbols))}
                          for name, (states, symbols) in periods.items()},
              "families": families,
              "source_hashes": {str(p.relative_to(ROOT)): sha256(p) for p in sorted([
                  *list((ROOT / "backend/core").glob("*.py")), *list((ROOT / "backend/data").glob("*.json")),
                  ROOT / "backend/database.py", Path(__file__).resolve()])}}
    result["summary"] = {name: {"families": len(families), "candidates": result["baseline_verified_candidates"],
                               "candidate_pairs": sum(len(f["candidates"]) * (len(f["candidates"]) - 1) // 2 for f in families),
                               **{key: sum(bool(f["periods"][name]["summary"]["transitions"][key]) for f in families)
                                  for key in families[0]["periods"][name]["summary"]["transitions"]},
                               "any_pair_crossing": sum(bool(f["periods"][name]["summary"]["pair_crossings"]) for f in families),
                               "pairs_crossing": sum(len(f["periods"][name]["summary"]["pair_crossings"]) for f in families)}
                         for name in periods}
    return result


def export(result, out):
    out.mkdir(parents=True, exist_ok=True)
    (out / "price_crossovers.json").write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":"),
                                                         allow_nan=False) + "\n", encoding="utf-8")
    with (out / "family_summary.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        fields = ["family", "period", "unit", "candidates", "observations", "cost_changes", "cost_changes_one_percent",
                  "app_changes", "app_strict_changes", "continuous_changes", "fixed_scale_changes", "pairs_crossing"]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for family in result["families"]:
            for name, period in family["periods"].items():
                s = period["summary"]
                t = s["transitions"]
                writer.writerow(dict(zip(fields, [family["family"], name, family["unit"], len(family["candidates"]),
                    s["observations"], len(t["cost_winner"]), len(t["cost_winner_one_percent"]), len(t["app_winner"]),
                    len(t["app_strict_winner"]), len(t["continuous_winner"]), len(t["fixed_scale_winner"]),
                    len(s["pair_crossings"])], strict=True)))
    with (out / "candidate_costs.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["family", "period", "date", "candidate", "unit", "modeled_cost", "application_score",
                         "frozen_nonprice_continuous_score", "lowest_cost", "application_first"])
        for family in result["families"]:
            for name, period in family["periods"].items():
                for row in period["records"]:
                    for slug, cost in row["costs"].items():
                        writer.writerow([family["family"], name, row["date"], slug, family["unit"], cost,
                                         row["scores"][slug]["total"], row["continuous_scores"][slug],
                                         slug == row["cost_winner"], slug == row["app_winner"]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daily", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--frozen-dir", type=Path, default=FROZEN, help="submission-<date> run directory")
    parser.add_argument("--robustness", type=Path, default=OLD_STUDY, help="decision_robustness.json of the same run")
    args = parser.parse_args()
    if (args.out_dir / "price_crossovers.json").exists():
        parser.error("Use a new output directory to preserve the previous replay")
    result = run(args.daily, args.frozen_dir.resolve(), args.robustness)
    export(result, args.out_dir)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
