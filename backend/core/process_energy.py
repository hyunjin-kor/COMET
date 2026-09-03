"""Process-energy term of the catalyst LCA.

Turns a Step Method route (list of step keys) into fuel and electricity per kg
of finished catalyst, then into GWP and CED with the public emission factors
in backend/data/process_energy_factors.json.

Thermal steps use first-principles duty:
  calcination  Q = cp_solid * (T_calc - T_amb) / kiln_efficiency
  drying       Q = [w * (cp_water * (T_out - T_amb) + latent)] / dryer_efficiency
where w is kg water per kg dry solid. Mechanical steps use a specific energy
in kWh/kg. Steps whose class is "unmodeled" are reported, never estimated.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from backend.paths import data_dir

_FILE = data_dir() / "process_energy_factors.json"


@lru_cache(maxsize=1)
def _load() -> dict:
    with open(_FILE, encoding="utf-8") as handle:
        return json.load(handle)


def _thermal_mj(step_cfg: dict, thermo: dict, calcination_temp_c: float | None) -> tuple[float, dict]:
    amb = float(thermo["ambient_c"])
    if step_cfg["class"] == "thermal_calcination":
        temp = float(calcination_temp_c if calcination_temp_c is not None else step_cfg["default_temp_c"])
        duty_kj = float(thermo["cp_solid_kj_per_kg_k"]) * max(0.0, temp - amb)
        eff = float(thermo["kiln_thermal_efficiency"])
        detail = {"temp_c": temp, "duty_kj_per_kg": round(duty_kj, 1), "efficiency": eff}
    else:
        w = float(step_cfg["water_kg_per_kg_solid"])
        t_out = float(step_cfg["outlet_temp_c"])
        duty_kj = w * (float(thermo["cp_water_kj_per_kg_k"]) * max(0.0, t_out - amb) + float(thermo["latent_heat_water_kj_per_kg"]))
        eff = float(thermo["dryer_thermal_efficiency"])
        detail = {"water_kg_per_kg_solid": w, "outlet_temp_c": t_out, "duty_kj_per_kg": round(duty_kj, 1), "efficiency": eff}
    return duty_kj / eff / 1000.0, detail


def compute_process_energy(
    steps: list[str],
    calcination_temp_c: float | None = None,
) -> dict[str, Any]:
    """Return per-kg process GWP/CED for a route, with every step itemized.

    Unknown or unmodeled steps are listed in ``unmodeled_steps`` and add
    nothing; the caller can see exactly how much of the route is covered.
    """
    data = _load()
    ef = data["emission_factors"]
    thermo = data["thermo"]
    grid = ef["electricity_us_grid"]
    gas = ef["natural_gas"]

    per_step: list[dict[str, Any]] = []
    unmodeled: list[str] = []
    gwp = 0.0
    ced = 0.0
    fuel_mj = 0.0
    kwh = 0.0

    for step in steps:
        cfg = data["steps"].get(step)
        if cfg is None or cfg["class"] == "unmodeled":
            unmodeled.append(step)
            per_step.append({"step": step, "class": cfg["class"] if cfg else "unknown", "modeled": False,
                             "note": cfg.get("note") if cfg else "No entry in process_energy_factors.json."})
            continue

        if cfg["class"] in {"thermal_calcination", "thermal_drying"}:
            mj, detail = _thermal_mj(cfg, thermo, calcination_temp_c)
            g = mj * float(gas["gwp_kg_co2eq_per_mj_hhv"])
            c = mj * float(gas["ced_mj_per_mj"])
            fuel_mj += mj
            per_step.append({"step": step, "class": cfg["class"], "modeled": True, "fuel": "natural_gas",
                             "fuel_mj_per_kg": round(mj, 4), **detail,
                             "gwp_kg_co2eq_per_kg": round(g, 5), "ced_mj_per_kg": round(c, 4)})
        else:
            e = float(cfg["kwh_per_kg"])
            g = e * float(grid["gwp_kg_co2eq_per_kwh_delivered"])
            c = e * float(grid["ced_mj_per_kwh"])
            kwh += e
            per_step.append({"step": step, "class": cfg["class"], "modeled": True, "fuel": "electricity",
                             "kwh_per_kg": e, "gwp_kg_co2eq_per_kg": round(g, 5), "ced_mj_per_kg": round(c, 4)})
        gwp += g
        ced += c

    modeled = len(steps) - len(unmodeled)
    return {
        "gwp_kg_co2eq_per_kg_catalyst": round(gwp, 4),
        "ced_mj_per_kg_catalyst": round(ced, 4),
        "natural_gas_mj_per_kg": round(fuel_mj, 4),
        "electricity_kwh_per_kg": round(kwh, 5),
        "per_step": per_step,
        "modeled_step_count": modeled,
        "total_step_count": len(steps),
        "unmodeled_steps": unmodeled,
        "assumptions": {
            "calcination_temp_c": calcination_temp_c,
            "cp_solid_kj_per_kg_k": thermo["cp_solid_kj_per_kg_k"],
            "kiln_thermal_efficiency": thermo["kiln_thermal_efficiency"],
            "dryer_thermal_efficiency": thermo["dryer_thermal_efficiency"],
            "electricity_gwp_kg_per_kwh": grid["gwp_kg_co2eq_per_kwh_delivered"],
            "natural_gas_gwp_kg_per_mj": gas["gwp_kg_co2eq_per_mj_hhv"],
        },
        "boundary_note": data["boundary_note"],
        "reference": {
            "electricity": grid["source"],
            "natural_gas": gas["source"],
            "thermo": thermo["efficiency_note"],
            "mechanical": data["mechanical_source"],
        },
    }


def list_process_energy_factors() -> dict:
    return _load()
