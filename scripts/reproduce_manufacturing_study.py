"""Reproduce declared manufacturing scenarios; these are not experimental costs."""

import argparse
import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.core.cost_engine import estimate_catalyst_cost  # noqa: E402
from backend.core.manufacturing_analysis import (  # noqa: E402
    prepare_manufacturing_ranges,
    varied_manufacturing_protocol,
)
from backend.schemas.manufacturing import ManufacturingProtocol  # noqa: E402
from backend.schemas.manufacturing_analysis import ManufacturingRange  # noqa: E402

OUTPUT = ROOT / "docs/paper/manufacturing-study-2026-09-15"
SEED = 20260915


def evidence(value, locator):
    return dict(kind="assumption", citation="COMET illustrative manufacturing scenario, 2026-09-15",
                locator=locator, recorded_value=value,
                note="Declared software demonstration input, not an experimental measurement, supplier quote or literature value.")


def scenario():
    """Simple explicit boundary: precursor/support/solvent through dry catalyst powder."""
    def operation(name, duration, power, equipment, labor):
        return dict(name=name, repetitions=1, duration_h=duration, additional_time_h=0, average_power_kw=power,
                    equipment_usd_h=equipment, attended_labor_h=labor, other_cost_usd=0)

    mix = operation("Impregnation", 2, .05, 1, .25)
    mix["purchases"] = [dict(name="Specified precursor solution (illustrative)", quantity=5, unit="mL", price_usd_per_unit=2),
                        dict(name="Support (illustrative)", quantity=24, unit="g", price_usd_per_unit=.05),
                        dict(name="Solvent (illustrative)", quantity=100, unit="mL", price_usd_per_unit=.01)]

    def thermal(name, temperature, hold, ramp_power, hold_power, equipment, labor):
        return dict(name=name, repetitions=1, start_temperature_c=20,
                    temperature_profile=[dict(target_c=temperature, ramp_c_per_min=5, hold_h=hold,
                                              ramp_power_kw=ramp_power, hold_power_kw=hold_power)],
                    additional_time_h=1, additional_power_kw=0, equipment_usd_h=equipment,
                    attended_labor_h=labor, other_cost_usd=0,
                    notes="One additional hour of passive cooling/handling occupies equipment. Zero additional electricity is an explicit scenario assumption.")

    drying = thermal("Drying", 120, 4, .4, .25, .8, .1)
    calcination = thermal("Calcination", 500, 3, 2, 1.2, 3, .1)
    reduction = thermal("Reduction", 400, 2, 1.5, .6, 2, .25)
    reduction["gases"] = [dict(name="Specified reducing gas (illustrative)", flow_l_per_min=.1,
                               duration_basis="operation", price_usd_per_m3=10,
                               volume_basis="Flow and price both at 0 C and 1 atm")]
    protocol = dict(mode="batch_cost", materials_basis="purchases", finished_batch_mass_kg=.03,
                    electricity_usd_kwh=.1, labor_usd_h=10, selling_margin_fraction=.1,
                    operations=[mix, drying, calcination, reduction],
                    source_note="Illustrative powder batch. All numerical inputs are declared assumptions. No specific catalyst recipe, performance or yield is validated. Precursor stoichiometry is outside this arithmetic test; dry output is independently specified. No scale economy, waste credit or spent-metal recovery.")

    def annotate(record, prefix):
        for key, value in list(record.items()):
            if isinstance(value, (int, float)):
                record.setdefault("input_evidence", {})[key] = evidence(value, prefix + key)
            elif key in {"operations", "temperature_profile", "purchases", "gases"}:
                for i, item in enumerate(value):
                    annotate(item, prefix + f"{key}.{i}.")
    annotate(protocol, "manufacturing_protocol.")
    return dict(components=[dict(role="active_metal", name="Illustrative active component", wt_pct=20, price_per_lb=1),
                            dict(role="support", name="Illustrative support", wt_pct=80, price_per_lb=1)],
                steps=["mixer_slurry"], order_size_tons=.03 / 907.18474,
                basis_year=2025, target_year=2025, ga_overhead_pct=.05, sard_pct=.05,
                manufacturing_protocol=protocol)


def independent_balance():
    """Hand-derived balance, independent of engine functions or result fields."""
    hours = [2, 100 / 300 + 4 + 1, 480 / 300 + 3 + 1, 380 / 300 + 2 + 1]
    kwh = [.05 * 2, .4 * (100 / 300) + .25 * 4,
           2 * (480 / 300) + 1.2 * 3, 1.5 * (380 / 300) + .6 * 2]
    materials = 5 * 2 + 24 * .05 + 100 * .01
    electricity = sum(kwh) * .1
    equipment = sum(h * rate for h, rate in zip(hours, [1, .8, 3, 2]))
    labor = (.25 + .1 + .1 + .25) * 10
    gas = .1 * hours[-1] * 60 / 1000 * 10
    subtotal = materials + electricity + equipment + labor + gas
    ga = subtotal * .05
    sard = (subtotal + ga) * .05
    price = (subtotal + ga + sard) / .9
    return dict(hours=hours, kwh=kwh, materials_usd=materials, electricity_usd=electricity,
                equipment_usd=equipment, labor_usd=labor, gas_usd=gas, ga_usd=ga, sard_usd=sard,
                margin_usd=price - subtotal - ga - sard, manufacturing_usd_kg=subtotal / .03,
                selling_price_usd_kg=price / .03)


def calculate(request):
    return estimate_catalyst_cost(**request)


def varied(request, values):
    protocol = ManufacturingProtocol.model_validate(request["manufacturing_protocol"])
    return {**request, "manufacturing_protocol": varied_manufacturing_protocol(protocol, values).model_dump()}


def run():
    request = scenario()
    baseline = calculate(request)
    hand = independent_balance()
    assert abs(baseline["summary"]["estimated_price_per_kg"] - hand["selling_price_usd_kg"]) < .0001
    report = baseline["manufacturing"]
    assert abs(report["manufacturing_cost_usd_kg"] - hand["manufacturing_usd_kg"]) < .0001
    assert [row["duration_h"] for row in report["operations"]] == hand["hours"]
    ranges = [
        ("Dry output", "finished_batch_mass_kg", .015, .045),
        ("Precursor price", "operations.0.purchases.0.price_usd_per_unit", 1, 3),
        ("Impregnation time", "operations.0.duration_h", 1, 4),
        ("Drying hold", "operations.1.temperature_profile.0.hold_h", 2, 8),
        ("Calcination hold", "operations.2.temperature_profile.0.hold_h", 1, 6),
        ("Calcination power", "operations.2.temperature_profile.0.hold_power_kw", .6, 2.4),
        ("Reduction hold", "operations.3.temperature_profile.0.hold_h", 1, 4),
        ("Electricity tariff", "electricity_usd_kwh", .05, .2),
    ]
    prepared = prepare_manufacturing_ranges(report, [ManufacturingRange(path=path, low=lo, high=hi) for _, path, lo, hi in ranges])
    sensitivity = []
    for (label, path, low, high), variable in zip(ranges, prepared["variables"]):
        sensitivity.append({**variable, "label": label,
                            "low_usd_kg": calculate(varied(request, {path: low}))["summary"]["estimated_price_per_kg"],
                            "high_usd_kg": calculate(varied(request, {path: high}))["summary"]["estimated_price_per_kg"]})
    sweep = []
    for hold in np.linspace(1, 6, 21):
        for mass in (.015, .03, .045):
            result = calculate(varied(request, {"operations.2.temperature_profile.0.hold_h": float(hold), "finished_batch_mass_kg": mass}))
            sweep.append(dict(hold_h=float(hold), mass_kg=mass, selling_price_usd_kg=result["summary"]["estimated_price_per_kg"]))
    # Independently test the marginal hour, including both overheads and margin.
    extra = calculate(varied(request, {"operations.2.temperature_profile.0.hold_h": 4}))
    marginal = (1.2 * .1 + 3) / .03 * 1.05**2 / .9
    assert abs(extra["summary"]["estimated_price_per_kg"] - baseline["summary"]["estimated_price_per_kg"] - marginal) < .0002
    mc_ranges = [ManufacturingRange(path="finished_batch_mass_kg", low=.024, high=.036),
                 ManufacturingRange(path="operations.2.temperature_profile.0.hold_h", low=2, high=4),
                 ManufacturingRange(path="operations.2.temperature_profile.0.hold_power_kw", low=.9, high=1.5),
                 ManufacturingRange(path="electricity_usd_kwh", low=.06, high=.12)]
    mc = prepare_manufacturing_ranges(report, mc_ranges)
    rng = np.random.default_rng(SEED)
    # Match the application API's five fixed price/order factor columns before
    # drawing manufacturing inputs. Their multipliers are exactly one here.
    rng.uniform(1.0, 1.0, size=(1000, 5))
    samples = []
    for _ in range(1000):
        values = {item.path: float(rng.uniform(item.low, item.high)) for item in mc_ranges}
        result = calculate(varied(request, values))
        samples.append(dict(inputs=values, selling_price_usd_kg=result["summary"]["estimated_price_per_kg"]))
    costs = np.array([row["selling_price_usd_kg"] for row in samples])
    counts, bins = np.histogram(costs, bins=10)
    mc.update(seed=SEED, n_simulations=len(samples), n_successful=len(samples), n_failed=0,
              mean_usd_kg=float(costs.mean()), p5_usd_kg=float(np.percentile(costs, 5)), p95_usd_kg=float(np.percentile(costs, 95)),
              histogram=[dict(low=float(lo), high=float(hi), count=int(count)) for lo, hi, count in zip(bins[:-1], bins[1:], counts)], samples=samples)
    unknown = deepcopy(request)
    unknown["manufacturing_protocol"]["finished_batch_mass_kg"] = None
    try:
        calculate(unknown)
    except ValueError as exc:
        missing_error = str(exc)
    else:
        raise AssertionError("An unknown dry output was accepted")
    return dict(date="2026-09-15", scope="Illustrative software scenarios, not measured catalyst costs or industrial predictions.",
                request=request, baseline=baseline, independent_balance=hand, sensitivity=sensitivity,
                sweep=sweep, monte_carlo=mc, marginal_calcination_hour_usd_kg=marginal,
                unknown_output_error=missing_error,
                assumptions="Each variation holds all other quantities, inputs and catalytic performance assumptions fixed. No performance equivalence, synthesis feasibility, temperature-to-power relation or scale economy is established. Uniform independent bounds are scenarios, not confidence intervals.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = run()
    paths = ["scripts/reproduce_manufacturing_study.py", "backend/core/manufacturing.py", "backend/core/manufacturing_trace.py", "backend/core/cost_engine.py", "backend/core/uncertainty.py", "backend/schemas/manufacturing.py"]
    data["code_sha256"] = {name: hashlib.sha256((ROOT / name).read_text(encoding="utf-8").encode()).hexdigest() for name in paths}
    data["code_hash_normalization"] = "UTF-8 text with LF line endings"
    content = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    output = OUTPUT / "manufacturing_study.json"
    if args.check:
        if output.read_text(encoding="utf-8") != content:
            raise ValueError("Manufacturing study differs from the frozen run")
    else:
        OUTPUT.mkdir(exist_ok=True)
        output.write_text(content, encoding="utf-8", newline="\n")
    print(json.dumps(dict(selling_price_usd_kg=data["baseline"]["summary"]["estimated_price_per_kg"],
                          marginal_calcination_hour_usd_kg=data["marginal_calcination_hour_usd_kg"],
                          n_simulations=data["monte_carlo"]["n_simulations"])))


if __name__ == "__main__":
    main()
