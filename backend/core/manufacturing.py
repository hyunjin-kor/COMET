"""Batch arithmetic from explicit measurements/assumptions, not a furnace model.

Electricity is measured kWh or sum(mean input kW * h). Gas volumes and prices
must use the same stated reference conditions. Step Method rates are not added.
"""

from math import isfinite

from backend.core.constants import LB_PER_KG, LB_PER_TON
from backend.schemas.manufacturing import ManufacturingProtocol


def evaluate_protocol(protocol: ManufacturingProtocol) -> dict:
    missing: list[str] = []
    if protocol.product_basis == "electrode":
        missing.append("Electrode preparation is record-only; dry-powder batch costing is not applicable")

    def need(value, label):
        if value is None:
            missing.append(label)
            return 0.0
        return value

    mass = need(protocol.finished_batch_mass_kg, "Finished dry batch mass (kg)")
    tariff = need(protocol.electricity_usd_kwh, "Electricity tariff (USD/kWh)")
    wage = need(protocol.labor_usd_h, "Labor rate (USD/h)")
    if not protocol.source_note.strip():
        missing.append("Source or assumption note")
    rows = []
    for index, op in enumerate(protocol.operations, 1):
        prefix = f"{index}. {op.name}: "
        before = len(missing)
        hours = energy = 0.0
        segments = []
        time_known = op.additional_time_h is not None
        measured = op.energy_basis == "measured" or op.measured_energy_kwh is not None
        if op.temperature_profile:
            time_known &= op.start_temperature_c is not None
            previous = need(op.start_temperature_c, prefix + "start temperature")
            for n, segment in enumerate(op.temperature_profile, 1):
                target = need(segment.target_c, prefix + f"segment {n} target temperature")
                delta = abs(target - previous)
                time_known &= segment.target_c is not None and segment.hold_h is not None and (not delta or segment.ramp_c_per_min is not None)
                rate = need(segment.ramp_c_per_min, prefix + f"segment {n} ramp rate") if delta else 1
                ramp_h = delta / rate / 60 if rate else 0
                hold_h = need(segment.hold_h, prefix + f"segment {n} hold time")
                hours += ramp_h + hold_h
                if not measured:
                    if ramp_h:
                        energy += ramp_h * need(segment.ramp_power_kw, prefix + f"segment {n} ramp power")
                    if hold_h:
                        energy += hold_h * need(segment.hold_power_kw, prefix + f"segment {n} hold power")
                segments.append({"target_c": segment.target_c, "ramp_h": ramp_h, "hold_h": hold_h})
                previous = target
        else:
            time_known &= op.duration_h is not None
            hours = need(op.duration_h, prefix + "duration")
            if not measured and hours:
                energy = hours * need(op.average_power_kw, prefix + "mean input power")
        additional = need(op.additional_time_h, prefix + "setup/cleaning/cooling time (enter 0 if excluded)")
        if not measured and additional:
            energy += additional * need(op.additional_power_kw, prefix + "setup/cleaning/cooling power")
        hours += additional
        if measured:
            energy = need(op.measured_energy_kwh, prefix + "measured electricity (kWh)")
        equipment_rate = need(op.equipment_usd_h, prefix + "equipment-only hourly rate")
        labor_h = need(op.attended_labor_h, prefix + "attended labor time")
        other = need(op.other_cost_usd, prefix + "other cost (enter 0 if excluded)")
        gas_cost = 0.0
        gas_rows = []
        for gas in op.gases:
            flow = need(gas.flow_l_per_min, prefix + gas.name + " gas flow")
            duration = need(gas.duration_h, prefix + gas.name + " gas duration")
            price = need(gas.price_usd_per_m3, prefix + gas.name + " gas price")
            if not gas.name.strip() or not gas.volume_basis.strip():
                missing.append(prefix + "gas name and shared flow/price volume basis")
            volume = flow * duration * 60 / 1000
            gas_cost += volume * price
            gas_rows.append({"name": gas.name, "volume_m3": volume * op.repetitions,
                             "cost_usd": volume * price * op.repetitions, "volume_basis": gas.volume_basis})
        count = op.repetitions
        costs = {"electricity": energy * tariff * count, "equipment": equipment_rate * hours * count,
                 "labor": labor_h * wage * count, "gas": gas_cost * count, "other": other * count}
        rows.append({"index": index, "name": op.name, "repetitions": count,
                     "duration_h": hours * count if time_known else None,
                     "electricity_kwh": energy * count, "gases": gas_rows, "segments": segments if time_known else None,
                     "costs_usd": costs, "cost_usd": sum(costs.values()),
                     "complete": len(missing) == before})
    complete = not missing
    if protocol.mode == "batch_cost" and not complete:
        raise ValueError("Complete batch costing inputs: " + "; ".join(missing))
    # Partial records never expose a spurious zero or subtotal as a completed cost.
    total = sum(r["cost_usd"] for r in rows) if complete else None
    return {"mode": protocol.mode, "protocol": protocol.model_dump(), "complete": complete,
            "missing_inputs": missing, "operations": rows if complete else [
                {**r, "electricity_kwh": None, "costs_usd": None, "cost_usd": None,
                 "gases": [{**g, "volume_m3": None, "cost_usd": None} for g in r["gases"]]} for r in rows],
            "serial_operation_hours": sum(r["duration_h"] for r in rows) if all(r["duration_h"] is not None for r in rows) else None,
            "batch_processing_cost_usd": total,
            "processing_cost_usd_kg": total / mass if complete else None,
            "electricity_kwh_per_kg": sum(r["electricity_kwh"] for r in rows) / mass if complete else None,
            "boundary": "User-defined batch operations; no inferred industrial scale-up, catalyst activity, or process LCA. "
                        "Solvent quantities are records; purchases are costed only through the materials/consumables inputs. "
                        "Equipment rates exclude separately entered electricity, gas and labor. "
                        "Times are summed serial operation-hours, not a parallel production schedule."}


def batch_cost_result(report: dict, materials_per_lb: float, order_tons: float,
                      ga_fraction: float, sard_fraction: float) -> dict:
    if not isfinite(order_tons) or order_tons <= 0:
        raise ValueError("Production quantity must be finite and positive")
    processing = report["processing_cost_usd_kg"] / LB_PER_KG
    subtotal = materials_per_lb + processing
    ga = subtotal * ga_fraction
    sard = (subtotal + ga) * sard_fraction
    pre_margin = subtotal + ga + sard
    fraction = report["protocol"]["selling_margin_fraction"]
    margin = pre_margin * fraction / (1 - fraction)
    price = pre_margin + margin
    batch_kg = report["protocol"]["finished_batch_mass_kg"]
    batch_equivalents = order_tons * LB_PER_TON / LB_PER_KG / batch_kg
    report["batch_equivalents"] = batch_equivalents
    report["manufacturing_cost_usd_kg"] = subtotal * LB_PER_KG
    report["boundary"] += " Order totals repeat the same batch costs linearly, including fractional batch equivalents; no scale economy is assumed."
    return {"model": "user_batch", "scale": "user batch", "order_size_tons": order_tons,
            "campaign_days": report["serial_operation_hours"] * batch_equivalents / 24,
            "step_cost_per_hr": 0.0, "chemppi_escalation": 1.0,
            "campaign_cost": processing * order_tons * LB_PER_TON,
            "total_production_lb": order_tons * LB_PER_TON,
            "materials_cost_per_lb": materials_per_lb, "processing_cost_per_lb": processing,
            "subtotal_per_lb": subtotal, "ga_per_lb": ga, "sard_per_lb": sard,
            "pre_margin_per_lb": pre_margin, "margin_pct": fraction * 100,
            "margin_per_lb": margin, "estimated_price_per_lb": round(price, 4),
            "estimated_price_per_kg": round(price * LB_PER_KG, 4), "step_details": []}
