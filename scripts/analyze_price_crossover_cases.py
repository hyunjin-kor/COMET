"""Derive explanatory price thresholds and counterfactuals for replay cases."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path

from scripts.run_price_crossovers import (
    FROZEN,
    Session,
    SQLModel,
    continuous_scores,
    cost_values,
    create_engine,
    daily_states,
    evaluate_benchmark_family,
    historical_states,
    read,
    sha256,
    sync_material_library,
)


def bisect_bracket(function, low, high):
    """Retain a sign-changing bracket, including plateaus due to cost rounding."""
    f_low, f_high = function(low), function(high)
    if f_low * f_high >= 0:
        raise ValueError("Threshold is not bracketed")
    for _ in range(50):
        middle = (low + high) / 2
        value = function(middle)
        if (value > 0) == (f_low > 0):
            low, f_low = middle, value
        else:
            high, f_high = middle, value
        if high - low < 1e-5:
            break
    return {"low": low, "high": high, "gap_low": f_low, "gap_high": f_high}


def analyze(study_path, daily_path):
    study = read(study_path)
    families = {f["family"]: f for f in study["families"]}
    baseline = read(FROZEN / "reference_basis_2026-09-08.json")["price_basis"]
    monthly, _ = historical_states(read(FROZEN / "monthly_history_2026-09-08.json"), baseline)
    daily, _ = daily_states(read(daily_path), baseline)
    states = {"monthly": dict(monthly), "daily": dict(daily)}
    db = create_engine("sqlite://")
    SQLModel.metadata.create_all(db)
    result = {"study_sha256": sha256(study_path), "daily_sha256": sha256(daily_path),
              "script_sha256": sha256(Path(__file__)),
              "method": "Exact engine recosting in an in-memory database. Other prices and all nonprice assumptions held fixed for each single-metal counterfactual. Thresholds are conditional model values, not forecasts or empirical uncertainty bounds.",
              "cases": []}
    try:
        with Session(db) as session:
            sync_material_library(session, force=True)

            def evaluate(family, prices):
                return evaluate_benchmark_family(session=session, family=family, prices=prices,
                                                 basis="reference")["candidates"]

            for family, before, after, a, b in [
                ("ammonia-cracking", "2025-09", "2025-10", "co-mgo-la2o3", "ni-alumina-baseline"),
                ("dry-reforming", "2025-09", "2025-10", "ni-co-almgo", "ni-zeolite-stable"),
                ("water-gas-shift", "2025-05", "2025-06", "cu-zno-baseline", "fe-cr-hts"),
            ]:
                p0, p1 = states["monthly"][before], states["monthly"][after]
                c0, c1 = cost_values(evaluate(family, p0)), cost_values(evaluate(family, p1))
                gap0, gap1 = c0[a] - c0[b], c1[a] - c1[b]
                effects = {}
                for symbol in study["periods"]["monthly"]["varying_symbols"]:
                    p = deepcopy(p0)
                    p[symbol]["price"] = p1[symbol]["price"]
                    costs = cost_values(evaluate(family, p))
                    effect = costs[a] - costs[b] - gap0
                    if abs(effect) > 1e-5:
                        effects[symbol] = {"price_before": p0[symbol]["price"], "price_after": p1[symbol]["price"],
                                           "unit": p0[symbol]["unit"], "gap_change_usd_lb": effect}
                residual = gap1 - gap0 - sum(e["gap_change_usd_lb"] for e in effects.values())
                if abs(residual) > 0.0005:
                    raise ValueError("Single-price effects fail to reconstruct the observed pair gap")
                result["cases"].append({"family": family, "a": a, "b": b, "before": before, "after": after,
                                        "costs_before": c0, "costs_after": c1, "gap_before": gap0,
                                        "gap_after": gap1, "metal_effects": effects, "additivity_residual": residual})

            family = "ammonia-cracking"
            a, b = "co-mgo-la2o3", "ni-alumina-baseline"
            boundary = []
            for i in range(51):
                ni = 4 + i * 0.24

                def gap(co):
                    p = deepcopy(baseline)
                    p["Ni"]["price"], p["Co"]["price"] = ni, co
                    costs = cost_values(evaluate(family, p))
                    return costs[a] - costs[b]

                bracket = bisect_bracket(gap, 1, 100)
                boundary.append({"Ni": ni, "Co_threshold": (bracket["low"] + bracket["high"]) / 2,
                                 "bracket": bracket})
            result["ammonia_boundary"] = {"a": a, "b": b, "unit": "$/lb of metal", "points": boundary,
                                          "observations": [{"date": d, "Ni": p["Ni"]["price"], "Co": p["Co"]["price"]}
                                                           for d, p in monthly]}
            family = "photocatalytic-water-splitting"
            ref, weights = families[family]["reference"], families[family]["weights"]
            a, b = "pt-tio2-cocatalyst", "tio2-anatase-baseline"
            p0, p1 = states["daily"]["2026-01-19"], states["daily"]["2026-01-20"]

            def score_gap(pt):
                p = deepcopy(p0)
                p["Pt"]["price"] = pt
                scores = continuous_scores(cost_values(evaluate(family, p)), ref, weights)
                return scores[a] - scores[b]

            bracket = bisect_bracket(score_gap, 500, 5000)
            threshold = (bracket["low"] + bracket["high"]) / 2
            result["photo_daily"] = {"a": a, "b": b, "before": "2026-01-19", "after": "2026-01-20",
                                     "Pt_before": p0["Pt"]["price"], "Pt_after": p1["Pt"]["price"],
                                     "Rh_fixed": p0["Rh"]["price"], "Pt_threshold": threshold,
                                     "unit": "$/troy_oz", "threshold_bracket": bracket,
                                     "gap_at_Pt_before": score_gap(p0["Pt"]["price"]),
                                     "gap_at_Pt_after": score_gap(p1["Pt"]["price"]),
                                     "daily_prices": [{"date": d, "Pt": p["Pt"]["price"], "Rh": p["Rh"]["price"]} for d, p in daily]}
    finally:
        db.dispose()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--daily", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("Preserve the previous analysis: use a new output path")
    result = analyze(args.study, args.daily)
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"cases": result["cases"], "photo": {k: v for k, v in result["photo_daily"].items() if k != "daily_prices"}}, indent=2))


if __name__ == "__main__":
    main()
