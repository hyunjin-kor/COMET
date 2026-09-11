"""Offline controlled price/evidence, manufacturing-scale and electrode analyses.

All outputs are model scenarios, not independent manufacturing observations.
Existing frozen inputs are read without copying them or using the application DB.
"""

from __future__ import annotations

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

from backend.core.cost_engine import estimate_catalyst_cost  # noqa: E402
from backend.core.decision_engine import (  # noqa: E402
    _apply_total_scores,
    _load_catalogs,
    _resolve_component_pricing,
    _weighted_evidence_score,
    evaluate_benchmark_family,
    rank_candidates,
)
from backend.core.electrocatalyst import calculate_electrode_layer_cost  # noqa: E402
from backend.core.material_pricing import resolve_electrode_materials  # noqa: E402
from backend.core.step_method import determine_scale, fit_steps_to_scale  # noqa: E402
from backend.database import sync_material_library  # noqa: E402
from backend.paths import data_dir  # noqa: E402

ORDERS = (2, 4.99, 5, 20, 69.99, 70, 200)
ROUTES = ("wet_impregnation_metal_oxide", "excess_solution_impregnation_metal_oxide",
          "deposition_precipitation_metal_oxide")


def _rank(candidates):
    # Match the application's rounded composite and deterministic tie breaks.
    return rank_candidates(candidates)


def cross_price_evidence(reference, live):
    """Cross numeric cost states and component confidence labels in a 2x2 design."""
    endpoints = {"reference": reference, "live": live}
    by_slug = {key: {c["slug"]: c for c in value["candidates"]} for key, value in endpoints.items()}
    if set(by_slug["reference"]) != set(by_slug["live"]):
        raise ValueError("Candidate sets differ")
    weights = reference["decision_profile"]["weights"]
    if live["decision_profile"]["weights"] != weights or live["family"] != reference["family"]:
        raise ValueError("Family or decision weights differ")
    for slug, ref in by_slug["reference"].items():
        other = by_slug["live"][slug]
        signature = lambda c: [(r["name"], r.get("role"), r.get("wt_pct")) for r in c["components"]]  # noqa: E731
        if signature(ref) != signature(other):
            raise ValueError("Component identities, order or composition differ")
        if any(ref["scores"][key] != other["scores"][key] for key in ("route", "performance")):
            raise ValueError("Non-price screening scores differ")
        if ref["summary"]["economics_basis_unit"] != other["summary"]["economics_basis_unit"]:
            raise ValueError("Economic units differ")

    states = {}
    for price_state in endpoints:
        for evidence_state in endpoints:
            candidates = deepcopy(list(by_slug[price_state].values()))
            for candidate in candidates:
                evidence_components = by_slug[evidence_state][candidate["slug"]]["components"]
                for component, evidence_component in zip(candidate["components"], evidence_components, strict=True):
                    component["evidence"] = evidence_component["evidence"]
                candidate["scores"]["evidence"] = _weighted_evidence_score(candidate["components"])
            _apply_total_scores(candidates, weights)
            ranked = _rank(candidates)
            state = {
                "ranking": [c["slug"] for c in ranked],
                "candidates": {c["slug"]: {"scores": c["scores"],
                    "cost": c["summary"]["economics_basis_value"],
                    "unit": c["summary"]["economics_basis_unit"]} for c in sorted(candidates, key=lambda c: c["slug"])},
            }
            if price_state == evidence_state:
                expected = _rank(endpoints[price_state]["candidates"])
                if state["ranking"] != [c["slug"] for c in expected] or any(
                    state["candidates"][c["slug"]]["scores"] != c["scores"] for c in expected
                ):
                    raise ValueError("Crossed design does not reproduce an application endpoint")
            states[f"{price_state}/{evidence_state}"] = state

    contributions = []
    for slug in sorted(by_slug["reference"]):
        rr, rl, lr, ll = [states[key]["candidates"][slug]["scores"]["total"] for key in (
            "reference/reference", "reference/live", "live/reference", "live/live")]
        price_effect = ((lr - rr) + (ll - rl)) / 2
        evidence_effect = ((rl - rr) + (ll - lr)) / 2
        if abs(price_effect + evidence_effect - (ll - rr)) > 1e-9:
            raise ValueError("Effect decomposition does not sum to the endpoint change")
        contributions.append({"slug": slug, "price_effect_score_points": round(price_effect, 6),
                              "evidence_effect_score_points": round(evidence_effect, 6),
                              "total_change_score_points": round(ll - rr, 6)})
    return {"family": reference["family"], "weights": weights, "states": states, "contributions": contributions}


def manufacturing_cases(reference_prices):
    catalog = _load_catalogs()["ammonia-cracking"]
    candidate = next(c for c in catalog["candidates"] if c["slug"] == "ni-alumina-baseline")
    components = [_resolve_component_pricing(c, reference_prices, "reference")[0] for c in candidate["components"]]
    rows = []
    for route_id in ROUTES:
        template = json.loads((ROOT / f"backend/data/process_templates/{route_id}.json").read_text(encoding="utf-8"))
        for order in ORDERS:
            fitted, substitutions, dropped = fit_steps_to_scale(template["steps"], determine_scale(order))
            result = estimate_catalyst_cost(components=components, steps=fitted,
                                           order_size_tons=order, target_year=2026, route_summary=template)
            rows.append({"route_id": route_id, "order_short_tons": order,
                         "scale": result["step_method"]["scale"],
                         "materials_usd_per_lb": result["materials"]["total_materials_cost_per_lb"],
                         "processing_usd_per_lb": result["step_method"]["processing_cost_per_lb"],
                         "selling_usd_per_lb": result["summary"]["estimated_price_per_lb"],
                         "campaign_days": result["step_method"]["campaign_days"],
                         "substitutions": substitutions, "dropped_steps": dropped,
                         "uncosted_operations": template.get("uncosted_operations", []),
                         "gwp_kg_co2eq_per_kg": result["summary"]["gwp_kg_co2eq_per_kg_catalyst"],
                         "lca_coverage_pct": result["summary"]["lca_coverage_pct"]})
    return {"candidate": candidate["slug"], "composition": [
        {key: c[key] for key in ("name", "wt_pct", "precursor_markup")} for c in components],
        "note": "Same finished composition/prices; route and scale vary. No proof of equal activity, yield, or precursor consumption. Threshold jumps are model scale-class effects. USD per pound of powder, not electrode area.", "rows": rows}


def electrode_cases(session):
    candidate = next(c for c in _load_catalogs()["pem-electrolyzer-oer"]["candidates"] if c["slug"] == "pem-irox-baseline")
    baseline, _ = resolve_electrode_materials(session, candidate["electrode_defaults"])
    rows = []
    for multiplier in (0.5, 1.0, 1.5):
        for loading in (0.2, 0.5, 1.5):
            result = calculate_electrode_layer_cost(
                catalyst_price_per_lb=baseline["catalyst_price_per_lb"] * multiplier,
                active_area_cm2=baseline["active_area_cm2"], catalyst_loading_mg_cm2=loading,
                **{key: baseline[key] for key in ("ionomer_to_catalyst_ratio", "ionomer_price_per_ml", "ionomer_price_per_kg_solids",
                    "ionomer_density_g_ml", "ionomer_solids_fraction", "substrate_cost_per_cm2",
                    "membrane_cost_per_cm2", "application_family") if key in baseline},
            )
            rows.append({"powder_price_multiplier": multiplier, "loading_mg_cm2": loading,
                         "area_cm2": result["active_area_cm2"], "cost_usd_per_m2": result["cost_per_m2_usd"],
                         "total_usd": result["total_cost_usd"], "breakdown": result["breakdown"]})
    return {"candidate": candidate["slug"], "note": "Hypothetical price/loading sensitivity of the catalog-priced material stack. No powder-route processing, complete-stack cost, activity/lifetime equivalence or area economies of scale is asserted. Price multipliers are scenario inputs, not collected quotations.", "rows": rows}


def run(reference_prices, live_prices, seed):
    isolated_engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(isolated_engine)
    with Session(isolated_engine) as session:
        sync_material_library(session, force=True)
        families = []
        for family in sorted(_load_catalogs()):
            ref = evaluate_benchmark_family(session=session, family=family, prices=reference_prices, basis="reference")
            live = evaluate_benchmark_family(session=session, family=family, prices=live_prices, basis="live")
            families.append(cross_price_evidence(ref, live))
        electrode = electrode_cases(session)
    isolated_engine.dispose()
    changed = {label: [f["family"] for f in families if f["states"][key]["ranking"][0]
                      != f["states"]["reference/reference"]["ranking"][0]]
               for label, key in (("evidence_only", "reference/live"), ("price_only", "live/reference"), ("combined", "live/live"))}
    return {"kind": "controlled_model_scenarios", "seed": seed,
            "summary": {"family_count": len(families), "changed_winners": changed,
                        "changed_winner_counts": {key: len(value) for key, value in changed.items()}},
            "note": "Deterministic enumeration; seed retained for the paper contract, no random samples. Crossed price/evidence states are counterfactuals, not observed quotes. Price effect includes cost-share weighting and source/basis level differences, not a same-date temporal causal claim. Route/performance scores remain author-assigned.",
            "families": families, "manufacturing": manufacturing_cases(reference_prices), "electrode": electrode}


def draw(result, out_dir):
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "COMET-controlled-cases"
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), layout="constrained")
    families = result["families"]
    labels = ("Reference prices,\nlive evidence", "Live prices,\nreference evidence", "Live prices\nand evidence")
    keys = ("reference/live", "live/reference", "live/live")
    changed = [sum(f["states"][key]["ranking"][0] != f["states"]["reference/reference"]["ranking"][0]
                   for f in families) for key in keys]
    axes[0].bar(range(3), changed, color=("#287b8e", "#b87932", "#354c72"))
    axes[0].set(xticks=range(3), xticklabels=labels, ylabel="Families with a different top candidate", title="A  Controlled price / evidence states")
    for i, count in enumerate(changed):
        axes[0].text(i, count + 0.15, str(count), ha="center")
    axes[0].set_ylim(0, max(changed) + 2)
    for route, label in zip(ROUTES, ("Incipient wetness", "Excess solution", "Deposition precipitation"), strict=True):
        rows = [r for r in result["manufacturing"]["rows"] if r["route_id"] == route]
        axes[1].plot([r["order_short_tons"] for r in rows], [r["selling_usd_per_lb"] for r in rows], marker="o", ms=3, label=label)
    for boundary in (5, 70):
        axes[1].axvline(boundary, color="#777777", linestyle=":", linewidth=0.8)
    axes[1].set(xscale="log", xlabel="Production quantity (short tons)", ylabel="Estimated selling price (USD/lb)", title="B  Fixed Ni/alumina composition")
    axes[1].legend(fontsize=7)
    for multiplier in (0.5, 1.0, 1.5):
        rows = [r for r in result["electrode"]["rows"] if r["powder_price_multiplier"] == multiplier]
        axes[2].plot([r["loading_mg_cm2"] for r in rows], [r["cost_usd_per_m2"] for r in rows], marker="o", label=f"Powder price {multiplier:g}x")
    axes[2].set(xlabel=r"Loading (mg cm$^{-2}$)", ylabel=r"Material-stack cost (USD m$^{-2}$)", title="C  Iridium oxide electrode scenario")
    axes[2].legend(fontsize=8)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    for suffix in ("png", "svg"):
        fig.savefig(out_dir / f"controlled_cases.{suffix}", dpi=300,
                    metadata={"Date": None} if suffix == "svg" else None)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-basis", type=Path, required=True)
    parser.add_argument("--live-basis", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260906)
    args = parser.parse_args()
    args.out_dir = args.out_dir.resolve()
    if args.out_dir.exists() and (not args.out_dir.is_dir() or any(args.out_dir.iterdir())):
        parser.error("Output directory must be new or empty; choose a different --out-dir to preserve existing evidence")
    if data_dir().resolve() != (ROOT / "backend/data").resolve():
        raise ValueError("Controlled cases require the repository data directory whose hashes are recorded")
    basis = [json.loads(path.read_text(encoding="utf-8"))["price_basis"] for path in (args.reference_basis, args.live_basis)]
    result = run(*basis, args.seed)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    output = args.out_dir / "controlled_cases.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    draw(result, args.out_dir)
    inputs = [args.reference_basis, args.live_basis, Path(__file__), ROOT / "backend/database.py",
              ROOT / "backend/paths.py", *sorted((ROOT / "backend/models").glob("*.py")),
              *sorted((ROOT / "backend/core").glob("*.py")), *sorted((ROOT / "backend/data").rglob("*.json"))]
    provenance = {"python": platform.python_version(), "packages": {
        name: importlib.metadata.version(name) for name in ("sqlmodel", "numpy", "matplotlib")},
        "input_hashes": [{"file": p.resolve().relative_to(ROOT).as_posix() if p.resolve().is_relative_to(ROOT) else p.name,
                          "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs],
        "numerical_output_sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
    (args.out_dir / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"families": len(result["families"]), "manufacturing_cases": len(result["manufacturing"]["rows"]),
                      "electrode_cases": len(result["electrode"]["rows"]), "numerical_output_sha256": provenance["numerical_output_sha256"]}))


if __name__ == "__main__":
    main()
