"""Scope reporting must not silently promote missing operations to costed ones."""

from copy import deepcopy

from backend.core.costing_scope import summarize_costing_scope


def test_costed_selection_does_not_claim_full_plant_coverage():
    scope = summarize_costing_scope(None, ["mixer_slurry"], "medium", "thermal")
    assert scope["status"] == "modeled_steps"
    assert scope["costed_steps"][0]["status"] == "costed"
    assert scope["costed_steps"][0]["source"]
    assert "does not establish complete plant coverage" in scope["boundary"]


def test_declared_uncosted_pressure_operation_survives_crystallizer_proxy():
    route = {
        "name": "Hydrothermal",
        "steps": ["crystallizer"],
        "uncosted_operations": ["Pressure autoclave: no pressure-vessel rate"],
    }
    original = deepcopy(route)
    scope = summarize_costing_scope(route, ["crystallizer"], "medium", "thermal")
    assert scope["status"] == "partial"
    assert scope["uncosted_operations"] == route["uncosted_operations"]
    assert scope["route_modified"] is False
    assert route == original


def test_scale_substitutions_describe_the_actual_charged_equipment():
    route = {"steps": ["kiln_batch", "filter_plate_frame"]}
    actual = ["kiln_continuous_indirect", "filter_rotary_vacuum"]
    scope = summarize_costing_scope(route, actual, "medium", "thermal")
    assert scope["status"] == "proxy"
    assert scope["substitutions"] == [
        {"from": "kiln_batch", "to": "kiln_continuous_indirect"},
        {"from": "filter_plate_frame", "to": "filter_rotary_vacuum"},
    ]
    assert scope["actual_steps"] == actual
    assert scope["route_modified"] is False


def test_missing_repeated_operation_is_reported_separately_from_scale_drops():
    route = {"steps": ["mixer_slurry", "mixer_slurry", "pressure_autoclave"]}
    scope = summarize_costing_scope(route, ["mixer_slurry"], "medium", "thermal")
    assert scope["status"] == "partial"
    assert scope["omitted_template_steps"] == ["mixer_slurry"]
    assert scope["dropped_steps"] == ["pressure_autoclave"]
    assert scope["route_modified"] is True


def test_custom_edit_does_not_claim_an_omitted_substitution_was_used():
    route = {"steps": ["kiln_batch", "mixer_slurry"]}
    scope = summarize_costing_scope(route, ["mixer_slurry", "mill"], "medium", "thermal")
    assert scope["substitutions"] == []
    assert scope["omitted_template_steps"] == ["kiln_continuous_indirect"]
    assert scope["added_steps"] == ["mill"]
    assert scope["route_modified"] is True


def test_order_only_change_preserves_template_identity_and_repetitions():
    scope = summarize_costing_scope(
        {"steps": ["mill", "mixer_slurry", "mixer_slurry"]},
        ["mixer_slurry", "mill", "mixer_slurry"], "medium", "thermal",
    )
    assert scope["route_modified"] is False
    assert len(scope["costed_steps"]) == 3


def test_step_library_proxy_and_electrode_area_boundary_remain_distinct():
    scope = summarize_costing_scope(None, ["ccm_coating_pass"], "medium", "electrocatalyst")
    assert scope["status"] == "partial"
    assert scope["costed_steps"][0]["status"] == "proxy"
    assert "not added to the electrode-area total" in scope["boundary"]
    assert "material stack only" in scope["area_cost_boundary"]
    manufacturing_scope = summarize_costing_scope(
        None, ["ccm_coating_pass"], "medium", "electrocatalyst",
        {"manufacturing": {"scenario": "pilot_roll_to_roll"}},
    )
    assert "published manufacturing operating point" in manufacturing_scope["area_cost_boundary"]
    assert "Stage yield losses" in manufacturing_scope["area_cost_boundary"]


def test_unknown_and_unavailable_actual_steps_cannot_be_reported_as_costed():
    scope = summarize_costing_scope(None, ["unknown", "kiln_batch"], "medium", "thermal")
    assert scope["status"] == "partial"
    assert scope["costed_steps"] == []
    assert scope["dropped_steps"] == ["unknown", "kiln_batch"]
