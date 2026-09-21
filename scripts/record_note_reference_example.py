"""Record the worked Ni/Al2O3 example of the Application Note on the frozen reference basis.

The example uses the same inputs as the calculator: the incipient-wetness template, a
20 short-ton order, 20 wt% nickel priced at the IMF monthly average of the basis month stored in the
frozen reference basis, and 80 wt% alumina resolved from the public UN Comtrade 2024
import-unit-value row of the materials library (escalated by the application's ChemPPI rule).
The calculation runs through the FastAPI /api/calculate endpoint against an in-memory
database synchronised from the bundled library; no external price service is contacted.

    python scripts/record_note_reference_example.py          # write the JSON
    python scripts/record_note_reference_example.py --check  # recompute and compare
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

from backend.database import get_session, sync_material_library  # noqa: E402
from backend.main import app  # noqa: E402

REFERENCE = "docs/paper/submission-2026-09-21/reference_basis_2026-09-21.json"
OUTPUT = ROOT / "docs/paper/figures-note-2026-09-09/reference_example_ni_al2o3.json"
TEMPLATE = "wet_impregnation_metal_oxide"
ALUMINA_KEY = "lit:comtrade-calcined-alumina-2024"
ORDER_TONS = 20
NI_WT, AL2O3_WT = 20, 80


def sha256(path):
    """Checksum of a text input with LF line endings, so Windows and Linux checkouts agree."""
    return hashlib.sha256((ROOT / path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def record():
    reference = json.loads((ROOT / REFERENCE).read_text(encoding="utf-8"))
    nickel = reference["price_basis"]["Ni"]
    if nickel["unit"] != "$/lb":
        raise ValueError("The reference nickel price is expected in $/lb")
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
            template = client.get(f"/api/materials/templates/{TEMPLATE}").json()
            options = client.get("/api/materials/composition-options?catalyst_domain=thermal").json()
            alumina = next(row for row in options["support_options"] if row.get("material_key") == ALUMINA_KEY)
            request = {
                "catalyst_domain": "thermal",
                "application_family": "general",
                "template_id": TEMPLATE,
                "order_size_tons": ORDER_TONS,
                "steps": template["steps"],
                "components": [
                    {"role": "active_metal", "name": "Ni", "wt_pct": NI_WT, "price_per_lb": nickel["price"]},
                    {"role": "support", "name": "Al2O3", "wt_pct": AL2O3_WT, "material_key": ALUMINA_KEY},
                ],
            }
            response = client.post("/api/calculate", json=request)
            response.raise_for_status()
            result = response.json()
        finally:
            app.dependency_overrides.clear()
    components = result["materials"]["components"]
    if [c["name"] for c in components][:1] != ["Ni"]:
        raise ValueError("Unexpected component order in the calculation result")
    return {
        "basis": f"{reference['basis_month']} reference prices",
        "inputs": {"reference_basis": REFERENCE, "reference_basis_sha256": sha256(REFERENCE),
                   "materials_library_sha256": sha256("backend/data/materials_library.json")},
        "request": request,
        "nickel_quote": nickel,
        "alumina_row": {k: alumina.get(k) for k in ("material_key", "name", "display_name", "price_per_lb", "price_unit",
                                                   "quote_source", "quote_year", "source_type", "reference_url")},
        "template_name": template["name"],
        "summary": result.get("summary"),
        "materials": result.get("materials"),
        "step_method": result.get("step_method"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(record(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != content:
            raise ValueError("The reference example differs from a fresh calculation")
    else:
        OUTPUT.write_text(content, encoding="utf-8", newline="\n")
    data = json.loads(content)
    print({"price_per_lb": data["step_method"]["estimated_price_per_lb"],
           "components": [(c["name"], c.get("price_per_lb"), c.get("cost_per_lb_cat")) for c in data["materials"]["components"]],
           "processing_per_lb": data["step_method"]["processing_cost_per_lb"]})


if __name__ == "__main__":
    main()
