"""Matrix harness for frontend composition choices and preparation routes."""

from __future__ import annotations

import ast
import json
import math
import re
from itertools import combinations, product

from sqlmodel import Session, select

from backend.core.constants import STEP_COSTS, TROY_OZ_PER_LB
from backend.models.material import Material
from backend.paths import app_root, data_dir

CALCULATOR_PAGE = app_root() / "frontend" / "src" / "pages" / "Calculator.tsx"
THERMAL_BASE_STEPS = ["mixer_slurry", "incipient_wetness", "dryer_rotary_100_300C"]
ORDER_SIZE_BY_SCALE = {"small": 2.0, "medium": 20.0, "large": 200.0}
ELECTRO_TEMPLATE_DEFAULTS = {
    "pem_fuel_cell_ccm": {
        "application_family": "fuel_cell",
        "catalyst_material_key": "fcs:xt-pt20-vulcan-s",
        "ionomer_material_key": "fcs:pfsa-d5",
        "membrane_material_key": "fcs:pfsa-d50u",
        "substrate_material_key": "fcs:w1s1011",
        "active_area_cm2": 25.0,
        "catalyst_loading_mg_cm2": 0.4,
        "ionomer_to_catalyst_ratio": 0.8,
    },
    "pem_electrolyzer_ccm": {
        "application_family": "electrolyzer",
        "catalyst_material_key": "fcs:xt-iridium-oxide-s",
        "ionomer_material_key": "fcs:pfsa-d5",
        "membrane_material_key": "fcs:pfsa-d50r",
        "substrate_material_key": "fcs:ti-ptl-ultrathin",
        "active_area_cm2": 25.0,
        "catalyst_loading_mg_cm2": 1.5,
        "ionomer_to_catalyst_ratio": 0.2,
    },
    "dmfc_gde_route": {
        "application_family": "direct_methanol_fuel_cell",
        "catalyst_material_key": "fcs:ptru60-vulcan-xc72r",
        "ionomer_material_key": "fcs:pfsa-d5",
        "membrane_material_key": "fcs:pfsa-d50u",
        "substrate_material_key": "fcs:ct-gds250",
        "active_area_cm2": 25.0,
        "catalyst_loading_mg_cm2": 1.0,
        "ionomer_to_catalyst_ratio": 0.6,
    },
    "aem_fuel_cell_ccm": {
        "application_family": "fuel_cell",
        "catalyst_material_key": "fcs:ag20-vulcan",
        "ionomer_material_key": "fcs:piperion-dispersion-5wt-20ml",
        "membrane_material_key": "fcs:piperion-aem40",
        "substrate_material_key": "fcs:ct-gds250",
        "active_area_cm2": 25.0,
        "catalyst_loading_mg_cm2": 0.7,
        "ionomer_to_catalyst_ratio": 0.6,
    },
    "alkaline_electrolyzer_gde": {
        "application_family": "electrolyzer",
        "catalyst_material_key": "fcs:xt-iridium-oxide-s",
        "ionomer_material_key": "fcs:sustainion-xa9-25ml",
        "membrane_material_key": "fcs:sustainion-x37-50-rt",
        "substrate_material_key": "fcs:nickel-fiber-felt",
        "active_area_cm2": 25.0,
        "catalyst_loading_mg_cm2": 1.0,
        "ionomer_to_catalyst_ratio": 0.3,
    },
}


def _load_frontend_thermal_choices() -> tuple[list[str], list[tuple[str, float]]]:
    """Read the live frontend option lists so the harness follows the shipped UI."""

    text = CALCULATOR_PAGE.read_text(encoding="utf-8")
    metals_match = re.search(r"const KNOWN_METALS = \[(.*?)\];", text, re.S)
    assert metals_match, "KNOWN_METALS was not found in Calculator.tsx"
    known_metals = ast.literal_eval(f"[{metals_match.group(1)}]")

    support_matches = re.findall(
        r"\{ name: '([^']+)', price: ([0-9.]+), note: '[^']+' \}",
        text,
    )
    assert support_matches, "SUPPORT_OPTIONS was not found in Calculator.tsx"
    supports = [(name, float(price)) for name, price in support_matches]
    return known_metals, supports


def _price_to_per_lb(price_row: dict) -> float:
    """Normalize the API response into USD per pound for the calculator payload."""

    unit = price_row.get("unit") or price_row.get("price_unit")
    price = float(price_row["price"])
    if unit == "$/lb":
        return price
    if unit == "$/kg":
        return price / 2.20462
    if unit == "$/troy_oz":
        return price * TROY_OZ_PER_LB
    raise AssertionError(f"Unsupported price unit in /api/prices: {unit}")


def _live_price_map(client, known_metals: list[str]) -> dict[str, float]:
    """Fetch current API prices and make sure every frontend metal has coverage."""

    response = client.get("/api/prices")
    assert response.status_code == 200
    rows = response.json()
    price_map = {row["symbol"]: _price_to_per_lb(row) for row in rows}
    missing = [symbol for symbol in known_metals if symbol not in price_map]
    assert not missing, f"Frontend known metals missing /api/prices coverage: {missing}"
    return price_map


def _post_and_capture_failure(client, payload: dict, label: str) -> str | None:
    """Run one matrix case and return a compact failure string when it breaks."""

    response = client.post("/api/calculate", json=payload)
    if response.status_code != 200:
        return f"{label}: status={response.status_code} body={response.text[:260]}"

    body = response.json()
    if body["summary"]["estimated_price_per_lb"] <= 0:
        return f"{label}: non-positive estimate returned"
    if len(body["step_method"]["step_details"]) != len(payload["steps"]):
        return f"{label}: step detail count did not match request"
    return None


def _assert_matrix_success(matrix_name: str, executed: int, failures: list[str]) -> None:
    """Fail with a readable matrix summary instead of stopping at the first broken case."""

    assert executed > 0, f"{matrix_name}: no cases executed"
    assert not failures, (
        f"{matrix_name}: {len(failures)} failures across {executed} executed cases.\n"
        + "\n".join(failures[:10])
    )


def _thermal_payload(components: list[dict], steps: list[str], order_size_tons: float) -> dict:
    """Build a thermal calculation payload with stable defaults."""

    return {
        "components": components,
        "steps": steps,
        "order_size_tons": order_size_tons,
        "catalyst_domain": "thermal",
    }


def _valid_order_size_for_steps(steps: list[str]) -> float:
    """Choose a valid order size for a given step list by intersecting supported scales."""

    for scale in ("medium", "small", "large"):
        if all(STEP_COSTS[step][scale] is not None for step in steps):
            return ORDER_SIZE_BY_SCALE[scale]
    raise AssertionError(f"No valid scale found for steps: {steps}")


def _material_exists(session: Session, library_key: str) -> bool:
    """Check whether a seeded library row exists for a preferred key."""

    stmt = select(Material.id).where(Material.library_key == library_key)
    return session.exec(stmt).first() is not None


def _electro_payload_for_template(session: Session, template_id: str, steps: list[str]) -> dict:
    """Return a valid electrocatalyst request payload for a saved process template."""

    defaults = ELECTRO_TEMPLATE_DEFAULTS.get(template_id)
    assert defaults is not None, f"Add electrocatalyst defaults for template '{template_id}'"
    missing = [key for key in ("catalyst_material_key", "ionomer_material_key", "membrane_material_key", "substrate_material_key") if not _material_exists(session, defaults[key])]
    assert not missing, f"{template_id}: missing seeded electrocatalyst material keys for {missing}"

    return {
        "catalyst_domain": "electrocatalyst",
        "application_family": defaults["application_family"],
        "template_id": template_id,
        "steps": steps,
        "order_size_tons": _valid_order_size_for_steps(steps),
        "components": [
            {
                "role": "active_catalyst",
                "material_key": defaults["catalyst_material_key"],
                "wt_pct": 100.0,
            }
        ],
        "electrode_input": defaults,
    }


def test_frontend_active_support_matrix(client) -> None:
    """Every active metal x support choice from the thermal UI should calculate."""

    known_metals, supports = _load_frontend_thermal_choices()
    price_map = _live_price_map(client, known_metals)

    executed = 0
    failures: list[str] = []
    for metal, (support_name, support_price) in product(known_metals, supports):
        payload = _thermal_payload(
            components=[
                {"role": "active_metal", "name": metal, "wt_pct": 20.0, "price_per_lb": price_map[metal]},
                {"role": "support", "name": support_name, "wt_pct": 80.0, "price_per_lb": support_price},
            ],
            steps=THERMAL_BASE_STEPS,
            order_size_tons=20.0,
        )
        executed += 1
        failure = _post_and_capture_failure(client, payload, f"active={metal} support={support_name}")
        if failure:
            failures.append(failure)

    assert executed == len(known_metals) * len(supports)
    _assert_matrix_success("frontend active/support matrix", executed, failures)


def test_frontend_bimetallic_and_promoter_matrices(client) -> None:
    """Exercise mixed-active and promoter-heavy thermal compositions from the UI choices."""

    known_metals, supports = _load_frontend_thermal_choices()
    price_map = _live_price_map(client, known_metals)

    bimetallic_executed = 0
    bimetallic_failures: list[str] = []
    for active_a, active_b in combinations(known_metals, 2):
        for support_name, support_price in supports:
            payload = _thermal_payload(
                components=[
                    {"role": "active_metal", "name": active_a, "wt_pct": 10.0, "price_per_lb": price_map[active_a]},
                    {"role": "active_metal", "name": active_b, "wt_pct": 10.0, "price_per_lb": price_map[active_b]},
                    {"role": "support", "name": support_name, "wt_pct": 80.0, "price_per_lb": support_price},
                ],
                steps=THERMAL_BASE_STEPS,
                order_size_tons=20.0,
            )
            bimetallic_executed += 1
            failure = _post_and_capture_failure(
                client,
                payload,
                f"active_pair={active_a}+{active_b} support={support_name}",
            )
            if failure:
                bimetallic_failures.append(failure)

    assert bimetallic_executed == math.comb(len(known_metals), 2) * len(supports)
    _assert_matrix_success("frontend bimetallic matrix", bimetallic_executed, bimetallic_failures)

    single_promoter_executed = 0
    single_promoter_failures: list[str] = []
    for active_metal, promoter, (support_name, support_price) in product(known_metals, known_metals, supports):
        payload = _thermal_payload(
            components=[
                {"role": "active_metal", "name": active_metal, "wt_pct": 15.0, "price_per_lb": price_map[active_metal]},
                {"role": "promoter", "name": promoter, "wt_pct": 5.0, "price_per_lb": price_map[promoter]},
                {"role": "support", "name": support_name, "wt_pct": 80.0, "price_per_lb": support_price},
            ],
            steps=THERMAL_BASE_STEPS,
            order_size_tons=20.0,
        )
        single_promoter_executed += 1
        failure = _post_and_capture_failure(
            client,
            payload,
            f"active={active_metal} promoter={promoter} support={support_name}",
        )
        if failure:
            single_promoter_failures.append(failure)

    assert single_promoter_executed == len(known_metals) * len(known_metals) * len(supports)
    _assert_matrix_success(
        "frontend active/promoter/support matrix",
        single_promoter_executed,
        single_promoter_failures,
    )

    dual_promoter_executed = 0
    dual_promoter_failures: list[str] = []
    for support_name, support_price in supports:
        for promoter_a, promoter_b in combinations(known_metals, 2):
            payload = _thermal_payload(
                components=[
                    {"role": "active_metal", "name": "Ni", "wt_pct": 12.0, "price_per_lb": price_map["Ni"]},
                    {"role": "promoter", "name": promoter_a, "wt_pct": 4.0, "price_per_lb": price_map[promoter_a]},
                    {"role": "promoter", "name": promoter_b, "wt_pct": 4.0, "price_per_lb": price_map[promoter_b]},
                    {"role": "support", "name": support_name, "wt_pct": 80.0, "price_per_lb": support_price},
                ],
                steps=THERMAL_BASE_STEPS,
                order_size_tons=20.0,
            )
            dual_promoter_executed += 1
            failure = _post_and_capture_failure(
                client,
                payload,
                f"active=Ni promoters={promoter_a}+{promoter_b} support={support_name}",
            )
            if failure:
                dual_promoter_failures.append(failure)

    assert dual_promoter_executed == math.comb(len(known_metals), 2) * len(supports)
    _assert_matrix_success("frontend two-promoter matrix", dual_promoter_executed, dual_promoter_failures)


def test_step_singletons_pairs_and_saved_templates(client, session: Session) -> None:
    """Run every valid step, every valid step pair, and every saved template."""

    known_metals, _ = _load_frontend_thermal_choices()
    price_map = _live_price_map(client, known_metals)
    ni_price = price_map["Ni"]

    single_executed = 0
    single_failures: list[str] = []
    for scale, order_size in ORDER_SIZE_BY_SCALE.items():
        for step, costs in STEP_COSTS.items():
            if costs[scale] is None:
                continue
            payload = _thermal_payload(
                components=[
                    {"role": "active_metal", "name": "Ni", "wt_pct": 20.0, "price_per_lb": ni_price},
                    {"role": "support", "name": "Al2O3", "wt_pct": 80.0, "price_per_lb": 0.5},
                ],
                steps=[step],
                order_size_tons=order_size,
            )
            single_executed += 1
            failure = _post_and_capture_failure(client, payload, f"single-step scale={scale} step={step}")
            if failure:
                single_failures.append(failure)

    _assert_matrix_success("single-step matrix", single_executed, single_failures)

    pair_executed = 0
    pair_failures: list[str] = []
    for scale, order_size in ORDER_SIZE_BY_SCALE.items():
        supported_steps = [step for step, costs in STEP_COSTS.items() if costs[scale] is not None]
        for first, second in combinations(supported_steps, 2):
            payload = _thermal_payload(
                components=[
                    {"role": "active_metal", "name": "Ni", "wt_pct": 20.0, "price_per_lb": ni_price},
                    {"role": "support", "name": "Al2O3", "wt_pct": 80.0, "price_per_lb": 0.5},
                ],
                steps=[first, second],
                order_size_tons=order_size,
            )
            pair_executed += 1
            failure = _post_and_capture_failure(
                client,
                payload,
                f"step-pair scale={scale} steps={first}+{second}",
            )
            if failure:
                pair_failures.append(failure)

    _assert_matrix_success("step-pair matrix", pair_executed, pair_failures)

    template_executed = 0
    template_failures: list[str] = []
    for template_path in sorted((data_dir() / "process_templates").glob("*.json")):
        template = json.loads(template_path.read_text(encoding="utf-8"))
        steps = template["steps"]
        if template.get("catalyst_domain") == "electrocatalyst":
            payload = _electro_payload_for_template(session, template_path.stem, steps)
        else:
            payload = {
                **_thermal_payload(
                    components=[
                        {"role": "active_metal", "name": "Ni", "wt_pct": 20.0, "price_per_lb": ni_price},
                        {"role": "support", "name": "Al2O3", "wt_pct": 80.0, "price_per_lb": 0.5},
                    ],
                    steps=steps,
                    order_size_tons=_valid_order_size_for_steps(steps),
                ),
                "template_id": template_path.stem,
            }

        template_executed += 1
        response = client.post("/api/calculate", json=payload)
        if response.status_code != 200:
            template_failures.append(
                f"template={template_path.stem}: status={response.status_code} body={response.text[:260]}"
            )
            continue

        body = response.json()
        if body["summary"]["estimated_price_per_lb"] <= 0:
            template_failures.append(f"template={template_path.stem}: non-positive estimate returned")
        elif body["route_summary"]["template_id"] != template_path.stem:
            template_failures.append(
                f"template={template_path.stem}: route_summary returned {body['route_summary']['template_id']}"
            )
        elif template.get("catalyst_domain") == "electrocatalyst" and body["electrode_model"] is None:
            template_failures.append(f"template={template_path.stem}: electrocatalyst route returned no electrode_model")

    _assert_matrix_success("process-template matrix", template_executed, template_failures)
