"""Matrix harness for thermal composition choices and preparation routes."""

from __future__ import annotations

import json
import math
from itertools import combinations, product

from sqlmodel import Session, select

from backend.core.constants import STEP_COSTS, TROY_OZ_PER_LB
from backend.models.material import Material
from backend.paths import data_dir

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


def _thermal_option_bank(client) -> tuple[list[dict], list[dict], list[dict], int]:
    """Load the shipped thermal option bank from the live API surface."""

    prices_response = client.get("/api/prices")
    assert prices_response.status_code == 200
    live_rows = prices_response.json()
    live_options = [
        {
            "kind": "live",
            "name": row["symbol"],
            "label": row["symbol"],
            "price_per_lb": _price_to_per_lb(row),
        }
        for row in live_rows
        if row["source_type"] in {"live", "indexed"}
    ]

    options_response = client.get("/api/materials/composition-options?catalyst_domain=thermal")
    assert options_response.status_code == 200
    payload = options_response.json()

    def library_option(row: dict) -> dict:
        return {
            "kind": "library",
            "material_key": row["material_key"],
            "name": row["display_name"],
            "label": row["label"],
            "price_per_lb": float(row["price_per_lb"]),
        }

    active_options = [*live_options, *[library_option(row) for row in payload["active_metal_options"]]]
    promoter_options = [*live_options, *[library_option(row) for row in payload["promoter_options"]]]
    support_options = [library_option(row) for row in payload["support_options"]]

    assert active_options, "thermal option bank did not expose active options"
    assert promoter_options, "thermal option bank did not expose promoter options"
    assert support_options, "thermal option bank did not expose support options"
    return active_options, promoter_options, support_options, int(payload["max_components"])


def _component(role: str, option: dict, wt_pct: float) -> dict:
    """Convert one thermal option into a calculation payload component."""

    component = {"role": role, "wt_pct": wt_pct}
    if option["kind"] == "library":
        component["material_key"] = option["material_key"]
        return component
    component["name"] = option["name"]
    component["price_per_lb"] = option["price_per_lb"]
    return component


def _default_support(supports: list[dict]) -> dict:
    """Choose a stable support default for generic thermal calculations."""

    for support in supports:
        if support["name"] == "Al2O3":
            return support
    for support in supports:
        if "alumina" in support["label"].lower():
            return support
    return supports[0]


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
    missing = [
        key
        for key in (
            "catalyst_material_key",
            "ionomer_material_key",
            "membrane_material_key",
            "substrate_material_key",
        )
        if not _material_exists(session, defaults[key])
    ]
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


def test_thermal_option_bank_active_support_matrix(client) -> None:
    """Every thermal active option and support option should produce a valid estimate."""

    active_options, _, support_options, max_components = _thermal_option_bank(client)
    assert max_components == 4

    executed = 0
    failures: list[str] = []
    for active_option, support_option in product(active_options, support_options):
        payload = _thermal_payload(
            components=[
                _component("active_metal", active_option, 20.0),
                _component("support", support_option, 80.0),
            ],
            steps=THERMAL_BASE_STEPS,
            order_size_tons=20.0,
        )
        executed += 1
        failure = _post_and_capture_failure(
            client,
            payload,
            f"active={active_option['label']} support={support_option['label']}",
        )
        if failure:
            failures.append(failure)

    assert executed == len(active_options) * len(support_options)
    _assert_matrix_success("thermal active/support option bank", executed, failures)


def test_thermal_promoter_and_quaternary_support_matrices(client) -> None:
    """Exercise promoter-heavy and promoted-support thermal formulations up to four components."""

    active_options, promoter_options, support_options, _ = _thermal_option_bank(client)
    live_active_options = [option for option in active_options if option["kind"] == "live"]
    default_support = _default_support(support_options)

    promoter_executed = 0
    promoter_failures: list[str] = []
    for active_option, promoter_option, support_option in product(
        live_active_options,
        promoter_options,
        support_options,
    ):
        payload = _thermal_payload(
            components=[
                _component("active_metal", active_option, 15.0),
                _component("promoter", promoter_option, 5.0),
                _component("support", support_option, 80.0),
            ],
            steps=THERMAL_BASE_STEPS,
            order_size_tons=20.0,
        )
        promoter_executed += 1
        failure = _post_and_capture_failure(
            client,
            payload,
            f"active={active_option['label']} promoter={promoter_option['label']} support={support_option['label']}",
        )
        if failure:
            promoter_failures.append(failure)

    _assert_matrix_success("thermal active/promoter/support matrix", promoter_executed, promoter_failures)

    quaternary_executed = 0
    quaternary_failures: list[str] = []
    for active_option, promoter_option in product(live_active_options, live_active_options):
        for support_a, support_b in combinations(support_options, 2):
            payload = _thermal_payload(
                components=[
                    _component("active_metal", active_option, 15.0),
                    _component("promoter", promoter_option, 5.0),
                    _component("support", support_a, 40.0),
                    _component("support", support_b, 40.0),
                ],
                steps=THERMAL_BASE_STEPS,
                order_size_tons=20.0,
            )
            quaternary_executed += 1
            failure = _post_and_capture_failure(
                client,
                payload,
                f"quaternary active={active_option['label']} promoter={promoter_option['label']} supports={support_a['label']}+{support_b['label']}",
            )
            if failure:
                quaternary_failures.append(failure)

    _assert_matrix_success("thermal quaternary promoted-support matrix", quaternary_executed, quaternary_failures)

    bimetallic_executed = 0
    bimetallic_failures: list[str] = []
    for active_a, active_b in combinations(live_active_options, 2):
        payload = _thermal_payload(
            components=[
                _component("active_metal", active_a, 10.0),
                _component("active_metal", active_b, 10.0),
                _component("support", default_support, 80.0),
            ],
            steps=THERMAL_BASE_STEPS,
            order_size_tons=20.0,
        )
        bimetallic_executed += 1
        failure = _post_and_capture_failure(
            client,
            payload,
            f"bimetallic={active_a['label']}+{active_b['label']}",
        )
        if failure:
            bimetallic_failures.append(failure)

    assert bimetallic_executed == math.comb(len(live_active_options), 2)
    _assert_matrix_success("thermal bimetallic matrix", bimetallic_executed, bimetallic_failures)


def test_step_singletons_pairs_and_saved_templates(client, session: Session) -> None:
    """Run every valid step, every valid step pair, and every saved template."""

    active_options, _, support_options, _ = _thermal_option_bank(client)
    default_active = next(option for option in active_options if option["kind"] == "live" and option["name"] == "Ni")
    default_support = _default_support(support_options)

    single_executed = 0
    single_failures: list[str] = []
    for scale, order_size in ORDER_SIZE_BY_SCALE.items():
        for step, costs in STEP_COSTS.items():
            if costs[scale] is None:
                continue
            payload = _thermal_payload(
                components=[
                    _component("active_metal", default_active, 20.0),
                    _component("support", default_support, 80.0),
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
                    _component("active_metal", default_active, 20.0),
                    _component("support", default_support, 80.0),
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
                        _component("active_metal", default_active, 20.0),
                        _component("support", default_support, 80.0),
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
