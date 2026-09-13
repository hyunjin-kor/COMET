"""Export publication tables in USD/kg without rewriting frozen engine ledgers."""

import argparse
import csv
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.paper_units import (  # noqa: E402
    KG_PER_LB,
    KG_PER_TROY_OZ,
    PER_LB_TO_PER_KG,
    publication_cost,
    publication_unit,
)


def mechanisms_in_kg(source):
    result = deepcopy(source)
    for case in result["cases"]:
        case["cost_unit"] = "$/kg"
        for key in ("costs_before", "costs_after"):
            case[key] = {slug: publication_cost(value, "$/lb") for slug, value in case[key].items()}
        for key in ("gap_before", "gap_after", "additivity_residual"):
            case[key] *= PER_LB_TO_PER_KG
        for effect in case["metal_effects"].values():
            for key in ("price_before", "price_after"):
                effect[key] = publication_cost(effect[key], effect["unit"])
            effect["unit"] = "$/kg"
            effect["gap_change_usd_kg"] = effect.pop("gap_change_usd_lb") * PER_LB_TO_PER_KG
    boundary = result["ammonia_boundary"]
    boundary["unit"] = "$/kg"
    for point in [*boundary["points"], *boundary["observations"]]:
        for key in ("Ni", "Co", "Co_threshold"):
            if key in point:
                point[key] *= PER_LB_TO_PER_KG
    photo = result["photo_daily"]
    for key in ("Pt_before", "Pt_after", "Rh_fixed", "Pt_threshold"):
        photo[key] = publication_cost(photo[key], "$/troy_oz")
    for key in ("low", "high"):
        photo["threshold_bracket"][key] = publication_cost(photo["threshold_bracket"][key], "$/troy_oz")
    photo["unit"] = "$/kg"
    for quote in photo["daily_prices"]:
        for symbol in ("Pt", "Rh"):
            quote[symbol] = publication_cost(quote[symbol], "$/troy_oz")
    result["publication_conversion"] = {"kg_per_lb": KG_PER_LB, "kg_per_troy_oz": KG_PER_TROY_OZ,
        "note": "Display conversion only; original units, engine rounding, scores, and crossing events remain frozen."}
    return result


def export(directory):
    study_path = directory / "price_crossovers.json"
    mechanism_path = directory / "crossover_mechanisms.json"
    study = json.loads(study_path.read_text(encoding="utf-8"))
    mechanisms = json.loads(mechanism_path.read_text(encoding="utf-8"))
    if hashlib.sha256(study_path.read_bytes()).hexdigest() != mechanisms["study_sha256"]:
        raise ValueError("Frozen study and mechanisms do not match")
    with (directory / "candidate_costs.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["family", "period", "date", "candidate", "unit", "modeled_cost", "application_score",
                         "frozen_nonprice_continuous_score", "lowest_cost", "application_first"])
        for family in study["families"]:
            for name, period in family["periods"].items():
                for row in period["records"]:
                    for slug, cost in row["costs"].items():
                        writer.writerow([family["family"], name, row["date"], slug, publication_unit(family["unit"]),
                            publication_cost(cost, family["unit"]), row["scores"][slug]["total"],
                            row["continuous_scores"][slug], slug == row["cost_winner"], slug == row["app_winner"]])
    with (directory / "family_summary.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["family", "period", "unit", "candidates", "observations", "cost_changes", "cost_changes_one_percent",
                         "app_changes", "app_strict_changes", "continuous_changes", "fixed_scale_changes", "pairs_crossing"])
        for family in study["families"]:
            for name, period in family["periods"].items():
                summary = period["summary"]
                transitions = summary["transitions"]
                writer.writerow([family["family"], name, publication_unit(family["unit"]), len(family["candidates"]),
                    summary["observations"], *[len(transitions[k]) for k in ("cost_winner", "cost_winner_one_percent",
                        "app_winner", "app_strict_winner", "continuous_winner", "fixed_scale_winner")],
                    len(summary["pair_crossings"])])
    converted = mechanisms_in_kg(mechanisms)
    converted["source_mechanisms_sha256"] = hashlib.sha256(mechanism_path.read_bytes()).hexdigest()
    converted["publication_export_script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (directory / "publication_mechanisms_kg.json").write_text(json.dumps(converted, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    export(parser.parse_args().directory)
