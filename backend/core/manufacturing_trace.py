"""Input provenance and calculation paths for explicit manufacturing records."""

import hashlib
import json
from collections import Counter

from backend.schemas.manufacturing import ManufacturingProtocol

UNITS = {
    "finished_batch_mass_kg": "kg/batch", "electricity_usd_kwh": "USD/kWh",
    "labor_usd_h": "USD/person-hour", "selling_margin_fraction": "fraction",
    "target_c": "degC", "start_temperature_c": "degC", "ramp_c_per_min": "degC/min",
    "hold_h": "h", "duration_h": "h", "additional_time_h": "h",
    "ramp_power_kw": "kW", "hold_power_kw": "kW", "average_power_kw": "kW", "additional_power_kw": "kW",
    "measured_energy_kwh": "kWh", "equipment_usd_h": "USD/h", "attended_labor_h": "person-hour",
    "other_cost_usd": "USD/repetition", "flow_l_per_min": "L/min", "price_usd_per_m3": "USD/m3",
    "repetitions": "count", "pressure_bar_abs": "bar absolute", "stirring_rpm": "rpm",
    "ph": "pH", "solvent_volume_ml": "mL/batch",
    "produced_mass_kg": "kg/intermediate batch", "used_mass_kg": "kg/destination batch",
}
CONTEXT = {"name", "equipment", "atmosphere", "pressure_bar_abs", "stirring_rpm", "ph",
           "solvent", "solvent_volume_ml", "notes", "source_note", "source_record_id", "volume_basis", "id",
           "comparison_key", "equipment_comparison_key"}
COLLECTIONS = {"input_evidence", "operations", "temperature_profile", "gases", "purchases", "intermediate_batches"}


def build_manufacturing_trace(protocol: ManufacturingProtocol, report: dict) -> dict:
    inputs = []

    def collect(record, prefix="", measured=False, has_profile=False, linked_solvent=False):
        values = record.model_dump()
        for key, value in values.items():
            if key in COLLECTIONS:
                continue
            effect = "record_only" if key in CONTEXT else "cost_input"
            if key in {"produced_mass_kg", "used_mass_kg"} and getattr(record, "allocation_basis", "mass_used") == "whole_batch":
                effect = "record_only"
            if key == "start_temperature_c" and not has_profile:
                effect = "record_only"
            if key == "solvent_volume_ml" and linked_solvent:
                effect = "cost_input"
            if key == "duration_h" and (has_profile or getattr(record, "duration_basis", "entered") != "entered"):
                effect = "inactive"
            if key == "quantity" and getattr(record, "quantity_basis", "entered") != "entered":
                effect = "inactive"
            if key == "additional_power_kw" and getattr(record, "additional_time_h", None) == 0:
                effect = "inactive"
            if key == "average_power_kw" and (has_profile or getattr(record, "duration_h", None) == 0):
                effect = "inactive"
            if key == "hold_power_kw" and getattr(record, "hold_h", None) == 0:
                effect = "inactive"
            if measured and key in {"ramp_power_kw", "hold_power_kw", "average_power_kw", "additional_power_kw"}:
                effect = "inactive"
            if not measured and key == "measured_energy_kwh":
                effect = "inactive"
            source = record.input_evidence.get(key)
            evidence = source.model_dump() if source else None
            provided = value is not None and value != ""
            if source:
                status = "matches_record" if value == source.recorded_value else "modified"
            elif not provided:
                status = "missing"
            elif value == type(record).model_fields[key].default:
                status = "default"
            else:
                status = "unattributed"
            unit = getattr(record, "unit", "") if key == "quantity" else (
                "USD/" + record.unit if key == "price_usd_per_unit" else UNITS.get(key, ""))
            inputs.append({"path": prefix + key, "value": value, "unit": unit,
                           "effect": effect, "source_status": status, "evidence": evidence})

    collect(protocol)
    calculations = []

    def calculation(identifier, formula, paths, value, unit, operation=None):
        calculations.append({"id": identifier, "formula": formula, "input_paths": paths,
                             "value": value, "unit": unit, "operation": operation})

    allocation_paths = {batch.id: f"intermediate_batches.{i}.allocation_fraction" for i, batch in enumerate(protocol.intermediate_batches)}
    for index, batch in enumerate(protocol.intermediate_batches):
        prefix = f"intermediate_batches.{index}."
        collect(batch, prefix)
        whole = batch.allocation_basis == "whole_batch"
        calculation(prefix + "transfer_fraction", "1 (whole batch charged; no inventory credit)" if whole else "used_mass_kg / produced_mass_kg",
                    [prefix + "allocation_basis", *([] if whole else [prefix + "used_mass_kg", prefix + "produced_mass_kg"])],
                    report["intermediate_batches"][index]["transfer_fraction"], "fraction")
        downstream = allocation_paths.get(batch.destination_batch_id)
        calculation(prefix + "allocation_fraction", "transfer_fraction * destination_allocation_fraction" if downstream else "transfer_fraction",
                    [prefix + "transfer_fraction", prefix + "destination_batch_id", *([downstream] if downstream else [])],
                    report["intermediate_batches"][index]["allocation_fraction"], "fraction")
    for index, (op, result) in enumerate(zip(protocol.operations, report["operations"], strict=True)):
        prefix = f"operations.{index}."
        allocation_path = allocation_paths.get(op.intermediate_batch_id)
        allocation_inputs = [allocation_path, prefix + "intermediate_batch_id"] if allocation_path else []
        allocation_formula = " * allocation_fraction" if allocation_path else ""
        measured = op.energy_basis == "measured" or op.measured_energy_kwh is not None
        collect(op, prefix, measured, bool(op.temperature_profile),
                protocol.materials_basis == "purchases" and any(p.quantity_basis == "solvent_volume" for p in op.purchases))
        times = [prefix + "additional_time_h", prefix + "repetitions"]
        energy = []
        for n, segment in enumerate(op.temperature_profile):
            path = prefix + f"temperature_profile.{n}."
            collect(segment, path, measured, True)
            start = prefix + "start_temperature_c" if n == 0 else prefix + f"temperature_profile.{n-1}.target_c"
            times.extend([start, path + "target_c", path + "ramp_c_per_min", path + "hold_h"])
            energy.extend([path + "ramp_power_kw", path + "hold_power_kw"])
        if not op.temperature_profile:
            times.append(prefix + "duration_h")
            energy.append(prefix + "average_power_kw")
        time_formula = ("sum(abs(T_next - T_previous) / ramp / 60 + hold)" if op.temperature_profile else "duration")
        calculation(prefix + "time", f"repetitions * ({time_formula} + additional_time)",
                    list(dict.fromkeys(times)), result["duration_h"], "h", index)
        energy_paths = [prefix + "measured_energy_kwh", prefix + "repetitions"] if measured else [*times, *energy, prefix + "additional_power_kw"]
        calculation(prefix + "energy", "repetitions * measured_kWh" if measured else "repetitions * sum(input_kW * elapsed_h)",
                    list(dict.fromkeys(energy_paths)), result["electricity_kwh"], "kWh", index)
        for n, gas in enumerate(op.gases):
            path = prefix + f"gases.{n}."
            collect(gas, path)
            gas_time_paths = ([path + "duration_h"] if gas.duration_basis == "entered" else
                              [prefix + f"temperature_profile.{j}.hold_h" for j in range(len(op.temperature_profile))]
                              if gas.duration_basis == "holds" else times)
            calculation(path + "volume", "repetitions * flow_L_min * selected_duration_h * 60 / 1000",
                        list(dict.fromkeys([path + "flow_l_per_min", path + "duration_basis", prefix + "repetitions", *gas_time_paths])),
                        result["gases"][n]["volume_m3"], "m3", index)
        purchases = [r for r in report["purchases"] if r["operation"] == index + 1]
        for n, purchase in enumerate(op.purchases):
            path = prefix + f"purchases.{n}."
            collect(purchase, path)
            quantity_path = prefix + "solvent_volume_ml" if purchase.quantity_basis == "solvent_volume" else path + "quantity"
            calculation(path + "cost", "selected_quantity * price_USD_per_matching_unit * repetitions" + allocation_formula,
                        [quantity_path, path + "price_usd_per_unit", path + "unit", prefix + "repetitions", *allocation_inputs],
                        purchases[n]["cost_usd"], "USD", index)
        dependencies = {
            "electricity": ([prefix + "energy", "electricity_usd_kwh"], "energy_kWh * electricity_USD_kWh"),
            "equipment": ([prefix + "time", prefix + "equipment_usd_h"], "operation_h * equipment_USD_h"),
            "labor": ([prefix + "attended_labor_h", "labor_usd_h", prefix + "repetitions"], "attended_person_h * wage * repetitions"),
            "gas": ([v for n in range(len(op.gases)) for v in (prefix + f"gases.{n}.volume", prefix + f"gases.{n}.price_usd_per_m3")], "sum(gas_m3 * price_USD_m3)"),
            "other": ([prefix + "other_cost_usd", prefix + "repetitions"], "entered_charge * repetitions"),
        }
        for category, (paths, formula) in dependencies.items():
            calculation(prefix + category, "(" + formula + ")" + allocation_formula, [*paths, *allocation_inputs],
                        result["costs_usd"][category] if result["costs_usd"] is not None else None, "USD", index)
    counts = Counter(r["source_status"] for r in inputs if r["effect"] == "cost_input" and r["unit"])
    return {"protocol_sha256": hashlib.sha256(json.dumps(protocol.model_dump(), sort_keys=True, ensure_ascii=False,
                                                         separators=(",", ":"), allow_nan=False).encode()).hexdigest(),
            "inputs": inputs, "calculations": calculations, "coverage": dict(counts),
            "headline_uses_protocol": protocol.mode == "batch_cost", "cost_ledger": [],
            "note": "Evidence is a declared source record, not independent validation. Modified values retain their original source snapshot. Record-only conditions do not predict power, yield or performance."}


def append_selling_price_trace(report: dict, materials_usd_kg: float, ga: float, sard: float, margin: float):
    mass = report["protocol"]["finished_batch_mass_kg"]
    ledger = [{"category": "materials", "value": materials_usd_kg, "unit": "USD/kg", "basis":
               "Sum of allocated batch purchases / finished dry mass" if report["protocol"]["materials_basis"] == "purchases" else
               "materials.total_materials_cost_per_lb converted to USD/kg"}]
    for category in ("electricity", "equipment", "labor", "gas", "other"):
        ledger.append({"category": category, "value": sum(op["costs_usd"][category] for op in report["operations"]) / mass,
                       "unit": "USD/kg", "basis": "Sum of allocated repeated operation charges / finished dry batch mass"})
    for category, value, formula in (("ga", ga, "(materials + processing) * G&A fraction"),
                                     ("sard", sard, "(materials + processing + G&A) * SARD fraction"),
                                     ("margin", margin, "pre-margin price * margin fraction / (1 - margin fraction)")):
        ledger.append({"category": category, "value": value, "unit": "USD/kg", "basis": formula})
    report["trace"]["cost_ledger"] = ledger
    calculations = report["trace"]["calculations"]
    purchase_paths = [r["id"] for r in calculations if ".purchases." in r["id"] and r["id"].endswith(".cost")]
    for row in ledger:
        category = row["category"]
        if category == "materials":
            paths = [*purchase_paths, "finished_batch_mass_kg"] if report["protocol"]["materials_basis"] == "purchases" else ["materials.total_materials_cost_per_lb"]
        elif category == "ga":
            paths = ["total.materials", "total.processing", "overhead_inputs.ga_fraction"]
        elif category == "sard":
            paths = ["total.materials", "total.processing", "total.ga", "overhead_inputs.sard_fraction"]
        elif category == "margin":
            paths = ["total.materials", "total.processing", "total.ga", "total.sard", "selling_margin_fraction"]
        else:
            paths = [*[f"operations.{i}.{category}" for i in range(len(report["operations"]))], "finished_batch_mass_kg"]
        calculations.append({"id": "total." + category, "formula": row["basis"], "input_paths": paths,
                             "value": row["value"], "unit": "USD/kg", "operation": None})
    processing_keys = ["electricity", "equipment", "labor", "gas", "other"]
    calculations.append({"id": "total.processing", "formula": "electricity + equipment + labor + gas + additional charges (USD/kg)",
                         "input_paths": ["total." + k for k in processing_keys], "value": report["processing_cost_usd_kg"],
                         "unit": "USD/kg", "operation": None})
    calculations.append({"id": "total.selling_price", "formula": "materials + processing + G&A + SARD + profit margin",
                         "input_paths": ["total." + k for k in ("materials", "processing", "ga", "sard", "margin")],
                         "value": sum(row["value"] for row in ledger), "unit": "USD/kg", "operation": None})
    report["trace"]["cost_ledger_basis"] = "Estimated selling price before spent-catalyst recovery credit; unrounded USD/kg contributions."
