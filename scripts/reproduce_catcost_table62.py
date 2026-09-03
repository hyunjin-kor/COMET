"""Reproduce CatCost User Guide Table 6.2 with COMET's Step Method, line by line.

Inputs are the *published* values from Table 6.2 (mid-2017 basis): per-case
materials cost, the exact step list with multiplicities, and order size. No
input is tuned to hit the target. Every intermediate the table prints is
compared against COMET's value so a deviation can be traced to its cause.

Source: CatCost v1.1.0 User Guide, Section 6.4, Table 6.2 (NREL, public).

Run:  python scripts/reproduce_catcost_table62.py [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.core.step_method import calculate_step_method, selling_margin_pct  # noqa: E402

# Table 6.2, verbatim. Materials totals are the published sums of the
# per-material rows; step lists are the published rows with their multiplicities.
CASES = [
    {
        "name": "2 wt% Pt/C",
        "order_size_tons": 2.0,
        "materials_cost_per_lb": 10.70,
        "materials_rows": [
            ("H2PtCl6 (Pt value excluded, pool account)", 10.00, 0.053),
            ("Carbon support", 9.09, 1.0),
            ("N2H4", 0.68, 0.26),
            ("NaOH", 0.18, 0.025),
            ("NaCl disposal", 0.09, 10.0),
        ],
        "steps": [
            "incipient_wetness",
            "reactor_multistep",
            "scrubber_nox",
            "filter_plate_frame",
            "reactor_simple",
            "dryer_rotary_40_100C",
        ],
        "published": {
            "scale": "small",
            "step_cost_per_hr": 390.0,
            "campaign_days": 2.5,
            "campaign_cost": 23400.0,
            "processing_cost_per_lb": 5.85,
            "subtotal_per_lb": 16.55,
            "ga_per_lb": 0.83,
            "sard_per_lb": 0.87,
            "margin_per_lb": 9.12,
            "margin_pct_of_premargin": 50.0,
            "estimated_price_per_lb": 27.37,
            "market_price_per_lb": 34.09,
        },
    },
    {
        "name": "21 wt% Ni/Al2O3",
        "order_size_tons": 20.0,
        "materials_cost_per_lb": 11.88,
        "materials_rows": [
            ("Ni(NO3)2*6H2O", 2.50, 1.04),
            ("Alumina (trilobes)", 11.00, 0.79),
            ("NaOH 50%", 0.20, 0.28),
            ("H2O2 50%", 0.34, 0.12),
            ("NaNO3 landfill", 0.50, 0.02),
            ("H2 forming gas", 1.10, 0.45),
        ],
        "steps": [
            "incipient_wetness",
            "dryer_rotary_40_100C",
            "kiln_continuous_indirect",
            "scrubber_nox",
            "crystallizer",
            "filter_rotary_vacuum",
            "dryer_rotary_40_100C",
            "kiln_continuous_indirect",
            "kiln_continuous_indirect",
        ],
        "published": {
            "scale": "medium",
            "step_cost_per_hr": 1200.0,
            "campaign_days": 3.0,
            "campaign_cost": 86400.0,
            "processing_cost_per_lb": 2.16,
            "subtotal_per_lb": 14.04,
            "ga_per_lb": 0.70,
            "sard_per_lb": 0.74,
            "margin_per_lb": 5.11,
            "margin_pct_of_premargin": 33.0,
            "estimated_price_per_lb": 20.59,
            "market_price_per_lb": 21.33,
        },
    },
    {
        "name": "USY-based FCC (with RE)",
        "order_size_tons": 200.0,
        "materials_cost_per_lb": 0.352,
        "materials_rows": [
            ("Ludox sodium silicate", 0.25, 0.819),
            ("Al(OH)3", 0.30, 0.14),
            ("NaOH 50%", 0.20, 0.074),
            ("H2SO4 98%", 0.05, 0.22),
            ("Clay", 0.05, 0.376),
            ("La2O3", 1.50, 0.035),
            ("HCl 31%", 0.07, 0.036),
            ("NH4OH 28%", 0.10, 0.06),
        ],
        "steps": (
            ["reactor_simple", "crystallizer"]
            + ["filter_rotary_vacuum"] * 2
            + ["reactor_simple"] * 3
            + ["kiln_continuous_indirect", "reactor_multistep", "filter_rotary_vacuum", "reactor_multistep"]
            + ["reactor_simple"] * 2
            + ["dryer_spray"] * 2
            + ["reactor_simple"] * 4
            + ["filter_rotary_vacuum"] * 2
            + ["dryer_rotary_100_300C"]
        ),
        # Footnote b: zeolite ramp-up/down gives an actual rate of 67 ton/day,
        # so the published campaign is 4 days rather than 200/150 + 1.
        "published_effective_rate_ton_per_day": 67.0,
        "published": {
            "scale": "large",
            "step_cost_per_hr": 6725.0,
            "campaign_days": 4.0,
            "campaign_cost": 645600.0,
            "processing_cost_per_lb": 1.61,
            "subtotal_per_lb": 1.97,
            "ga_per_lb": 0.10,
            "sard_per_lb": 0.10,
            "margin_per_lb": 0.24,
            "margin_pct_of_premargin": 11.0,
            "estimated_price_per_lb": 2.41,
            "market_price_per_lb": 2.73,
        },
    },
]

COMPARE_KEYS = [
    "step_cost_per_hr",
    "campaign_days",
    "campaign_cost",
    "processing_cost_per_lb",
    "subtotal_per_lb",
    "ga_per_lb",
    "sard_per_lb",
    "margin_per_lb",
    "estimated_price_per_lb",
]


def pct(a: float, b: float) -> float:
    return (a - b) / b * 100.0 if b else float("nan")


def run_case(case: dict) -> dict:
    pub = case["published"]
    materials_sum = sum(p * q for _, p, q in case["materials_rows"])
    result = calculate_step_method(
        materials_cost_per_lb=case["materials_cost_per_lb"],
        steps=case["steps"],
        order_size_tons=case["order_size_tons"],
        chemppi_escalation=1.0,
    )
    rows = []
    for key in COMPARE_KEYS:
        got = float(result[key])
        exp = float(pub[key])
        rows.append({"key": key, "comet": got, "published": exp, "dev_pct": pct(got, exp)})

    # Margin: COMET applies Figure 6.3 (% of selling price). The table footnotes
    # instead quote a % of pre-margin cost. Report both so the gap is explicit.
    m_sell = selling_margin_pct(case["order_size_tons"])
    margin_of_premargin_from_corr = m_sell / (1 - m_sell) * 100.0

    out = {
        "name": case["name"],
        "order_size_tons": case["order_size_tons"],
        "materials_rows_sum": round(materials_sum, 4),
        "materials_published_total": case["materials_cost_per_lb"],
        "rows": rows,
        "margin": {
            "comet_pct_of_selling_price": round(m_sell * 100, 2),
            "comet_pct_of_premargin": round(margin_of_premargin_from_corr, 2),
            "table_footnote_pct_of_premargin": pub["margin_pct_of_premargin"],
        },
        "market": {
            "market_price_per_lb": pub["market_price_per_lb"],
            "comet_vs_market_pct": pct(float(result["estimated_price_per_lb"]), pub["market_price_per_lb"]),
            "published_vs_market_pct": pct(pub["estimated_price_per_lb"], pub["market_price_per_lb"]),
        },
    }

    # Isolate the campaign-length effect where the table overrode the rate.
    eff = case.get("published_effective_rate_ton_per_day")
    if eff:
        from backend.core.constants import CLEANING_TIME, HOURS_PER_DAY, LB_PER_TON

        days = case["order_size_tons"] / eff + CLEANING_TIME[result["scale"]]
        campaign = float(result["step_cost_per_hr"]) * HOURS_PER_DAY * days
        proc = campaign / (case["order_size_tons"] * LB_PER_TON)
        sub = case["materials_cost_per_lb"] + proc
        ga = sub * 0.05
        sard = (sub + ga) * 0.05
        pre = sub + ga + sard
        margin = pre * m_sell / (1 - m_sell)
        out["with_published_rate"] = {
            "effective_rate_ton_per_day": eff,
            "campaign_days": round(days, 3),
            "processing_cost_per_lb": round(proc, 4),
            "estimated_price_per_lb": round(pre + margin, 4),
            "dev_pct_vs_published": round(pct(pre + margin, pub["estimated_price_per_lb"]), 2),
        }
    return out


def print_report(results: list[dict]) -> None:
    for r in results:
        print(f"\n## {r['name']}  (order {r['order_size_tons']:g} ton)")
        print(f"materials: published total {r['materials_published_total']}  |  sum of rows {r['materials_rows_sum']}")
        print(f"{'':<26}{'COMET':>12}{'Table 6.2':>12}{'dev %':>9}")
        for row in r["rows"]:
            print(f"{row['key']:<26}{row['comet']:>12.4f}{row['published']:>12.4f}{row['dev_pct']:>+9.2f}")
        m = r["margin"]
        print(
            f"margin basis: COMET {m['comet_pct_of_selling_price']}% of selling price "
            f"= {m['comet_pct_of_premargin']}% of pre-margin  |  table footnote {m['table_footnote_pct_of_premargin']}% of pre-margin"
        )
        mk = r["market"]
        print(
            f"vs market ${mk['market_price_per_lb']}: COMET {mk['comet_vs_market_pct']:+.1f}%  |  "
            f"CatCost published {mk['published_vs_market_pct']:+.1f}%"
        )
        if "with_published_rate" in r:
            w = r["with_published_rate"]
            print(
                f"with footnote-b rate {w['effective_rate_ton_per_day']:g} t/d: campaign {w['campaign_days']} d, "
                f"processing {w['processing_cost_per_lb']:.4f}, price {w['estimated_price_per_lb']:.4f} "
                f"({w['dev_pct_vs_published']:+.2f}% vs published)"
            )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, help="write full results to this path")
    args = ap.parse_args()
    results = [run_case(c) for c in CASES]
    print_report(results)
    if args.json:
        args.json.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
