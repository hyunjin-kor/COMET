"""What-if analyses of the Application Note, run through the calculator API on the frozen reference basis.

Every case is a request a user can enter in the calculator: a supported-metal
catalyst, a preparation template, an order size and the reference-month metal
price. The study varies one input at a time (metal loading, order size,
preparation template) and derives the metal price at which two catalysts cost
the same per kilogram. Catalytic performance is not evaluated.

    python scripts/note_whatif_study.py          # write the JSON
    python scripts/note_whatif_study.py --check  # recompute and compare
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402

from backend.core.decision_engine import _normalize_price_per_lb  # noqa: E402
from backend.database import get_session, sync_material_library  # noqa: E402
from backend.main import app  # noqa: E402

RUN = "docs/paper/submission-2026-09-21"
REFERENCE = f"{RUN}/reference_basis_2026-09-21.json"
HISTORY = f"{RUN}/monthly_history_2026-09-21.json"
OUTPUT = ROOT / "docs/paper/whatif-2026-09-21/whatif_study.json"
ALUMINA = "lit:comtrade-calcined-alumina-2024"
IMPREGNATION = "wet_impregnation_metal_oxide"
ORDER_TONS = 20
CATALYSTS = {
    "ni": {"label": "Ni/Al2O3", "metal": "Ni", "loading_wt_pct": 20, "sweep_wt_pct": [5, 10, 15, 20, 25, 30]},
    "ru": {"label": "Ru/Al2O3", "metal": "Ru", "loading_wt_pct": 2, "sweep_wt_pct": [0.5, 1, 2, 3, 4, 5]},
}
ORDER_SIZES = [1, 2, 5, 10, 20, 50, 70, 100, 200, 500, 1000]
TEMPLATES = ["wet_impregnation_metal_oxide", "excess_solution_impregnation_metal_oxide",
             "deposition_precipitation_metal_oxide", "coprecipitation_metal_oxide", "sol_gel_metal_oxide"]


def sha256(path):
    """Checksum of a text input with LF line endings, so Windows and Linux checkouts agree."""
    return hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def study():
    basis = json.loads((ROOT / REFERENCE).read_text(encoding="utf-8"))
    history = json.loads((ROOT / HISTORY).read_text(encoding="utf-8"))["series"]
    quotes = {key: basis["price_basis"][spec["metal"]] for key, spec in CATALYSTS.items()}
    price_lb = {key: _normalize_price_per_lb(quote["price"], quote["unit"]) for key, quote in quotes.items()}
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        sync_material_library(session, force=True)

        def override():
            yield session

        app.dependency_overrides[get_session] = override
        try:
            # Used without a context manager, TestClient does not run the lifespan price collection.
            client = TestClient(app)
            fitted = {}

            def route(template, order):
                """Template operations fitted to the scale of the order, as the calculator applies them."""
                if order not in fitted:
                    response = client.get(f"/api/templates/costs?order_size_tons={order}&catalyst_domain=thermal")
                    response.raise_for_status()
                    fitted[order] = {row["id"]: row for row in response.json()["templates"]}
                return fitted[order][template]

            def estimate(key, *, loading=None, order=ORDER_TONS, template=IMPREGNATION, metal_price=None):
                spec = CATALYSTS[key]
                loading = spec["loading_wt_pct"] if loading is None else loading
                request = {
                    "catalyst_domain": "thermal", "application_family": "general", "template_id": template,
                    "order_size_tons": order, "steps": route(template, order)["steps_fitted"],
                    "components": [
                        {"role": "active_metal", "name": spec["metal"], "wt_pct": loading,
                         "price_per_lb": price_lb[key] if metal_price is None else metal_price},
                        {"role": "support", "name": "Al2O3", "wt_pct": 100 - loading, "material_key": ALUMINA},
                    ],
                }
                response = client.post("/api/calculate", json=request)
                response.raise_for_status()
                method = response.json()["step_method"]
                return {"selling_price_per_lb": method["estimated_price_per_lb"],
                        "materials_per_lb": method["materials_cost_per_lb"],
                        "processing_per_lb": method["processing_cost_per_lb"],
                        "ga_per_lb": method["ga_per_lb"], "sard_per_lb": method["sard_per_lb"],
                        "margin_per_lb": method["margin_per_lb"],
                        "margin_pct": method["margin_pct"], "scale": method["scale"],
                        "campaign_days": method["campaign_days"],
                        "substitutions": route(template, order)["substitutions"]}

            base = {key: estimate(key) for key in CATALYSTS}
            loading = {key: [{"loading_wt_pct": value, **estimate(key, loading=value)} for value in spec["sweep_wt_pct"]]
                       for key, spec in CATALYSTS.items()}
            order = {key: [{"order_size_tons": tons, **estimate(key, order=tons)} for tons in ORDER_SIZES] for key in CATALYSTS}
            preparation = [{"template_id": template, "template_name": route(template, ORDER_TONS)["name"],
                            "operations": len(route(template, ORDER_TONS)["steps_fitted"]),
                            "uncosted_operations": route(template, ORDER_TONS)["uncosted_operations"],
                            **estimate("ni", template=template)} for template in TEMPLATES]
            # The selling price is affine in the metal price, so two evaluations give the equal-cost price exactly.
            without_metal = estimate("ru", metal_price=0)
            slope = (base["ru"]["selling_price_per_lb"] - without_metal["selling_price_per_lb"]) / price_lb["ru"]
            equal_price_lb = (base["ni"]["selling_price_per_lb"] - without_metal["selling_price_per_lb"]) / slope
            estimate_check = estimate("ru", metal_price=equal_price_lb)["selling_price_per_lb"]
        finally:
            app.dependency_overrides.clear()
    if abs(estimate_check - base["ni"]["selling_price_per_lb"]) > 5e-4:
        raise ValueError("The equal-cost ruthenium price does not reproduce the nickel catalyst price")
    ru_history = [_normalize_price_per_lb(point["price"], history["Ru"]["unit"]) for point in history["Ru"]["points"]]
    return {
        "basis_month": basis["basis_month"],
        "inputs": {"reference_basis": REFERENCE, "reference_basis_sha256": sha256(REFERENCE),
                   "monthly_history": HISTORY, "monthly_history_sha256": sha256(HISTORY),
                   "materials_library_sha256": sha256("backend/data/materials_library.json")},
        "scope": "Calculator requests on the reference basis; one input varied at a time. Precious-metal value is part of the "
                 "materials cost and carries overheads and margin; no spent-catalyst credit is applied. Catalytic performance is not evaluated.",
        "catalysts": {key: {**spec, "support": "Al2O3", "support_material_key": ALUMINA, "template_id": IMPREGNATION,
                            "order_size_tons": ORDER_TONS, "metal_quote": quotes[key], "metal_price_per_lb": price_lb[key],
                            "baseline": base[key]} for key, spec in CATALYSTS.items()},
        "loading": loading,
        "order_size": order,
        "preparation": preparation,
        "equal_cost": {
            "comparison": "Ru/Al2O3 at its baseline loading against Ni/Al2O3 at its baseline loading, same support, template and order size",
            "ru_selling_price_without_metal_per_lb": without_metal["selling_price_per_lb"],
            "selling_price_slope_per_metal_price": slope,
            "equal_cost_ru_price_per_lb": equal_price_lb,
            "equal_cost_over_reference": equal_price_lb / price_lb["ru"],
            "price_ratio_ru_over_ni_catalyst": base["ru"]["selling_price_per_lb"] / base["ni"]["selling_price_per_lb"],
            "ru_history_months": len(ru_history),
            "ru_history_min_per_lb": min(ru_history), "ru_history_max_per_lb": max(ru_history),
            "months_below_equal_cost": sum(price <= equal_price_lb for price in ru_history),
            "verified_selling_price_per_lb": estimate_check,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(study(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != content:
            raise ValueError("The what-if study differs from a fresh calculation")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(content, encoding="utf-8", newline="\n")
    data = json.loads(content)
    print(json.dumps({"baseline": {k: v["baseline"]["selling_price_per_lb"] for k, v in data["catalysts"].items()},
                      "equal_cost": data["equal_cost"]}, indent=1))


if __name__ == "__main__":
    main()
