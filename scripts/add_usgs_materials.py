"""Append USGS-verified commodity proxy materials to materials_curated.json.

Run once to seed the curated library with metals that were previously
absent. Each row carries an explicit USGS Mineral Commodity Summaries
2025 reference URL and the exact basis (LME cash, US spot, MTU, etc.).
"""

from __future__ import annotations

import json
from pathlib import Path

CURATED_PATH = Path(__file__).resolve().parent.parent / "backend" / "data" / "materials_curated.json"
USGS_BASE_URL = "https://pubs.usgs.gov/periodicals/mcs2025/mcs2025-{slug}.pdf"
SOURCE = "USGS Mineral Commodity Summaries 2025"

NEW_ENTRIES = [
    # ── Precious / PGM commodity proxies (per troy oz, USGS MCS 2025 = 2024 data) ──
    ("lit:usgs-platinum-bullion-2025", "Refined platinum bullion, commodity proxy (USGS 2025)",
     "Pt", "Precious Metal / PGM", "Pt", 950.0, "$/troy_oz",
     "USGS MCS 2025 platinum-group chapter reports an estimated 2024 annual average price of $950/troy_oz for platinum. "
     "Use as a fixed bulk-metal proxy for Pt-content thermal screening; for Sigma-grade chloroplatinic acid precursor pricing use sigma:520896.",
     "annual_average_us_market_price_2024", "platinum-group"),
    ("lit:usgs-palladium-bullion-2025", "Refined palladium bullion, commodity proxy (USGS 2025)",
     "Pd", "Precious Metal / PGM", "Pd", 980.0, "$/troy_oz",
     "USGS MCS 2025 platinum-group chapter reports an estimated 2024 annual average price of $980/troy_oz for palladium.",
     "annual_average_us_market_price_2024", "platinum-group"),
    ("lit:usgs-rhodium-bullion-2025", "Refined rhodium bullion, commodity proxy (USGS 2025)",
     "Rh", "Precious Metal / PGM", "Rh", 4600.0, "$/troy_oz",
     "USGS MCS 2025 platinum-group chapter reports an estimated 2024 annual average price of $4,600/troy_oz for rhodium (down 31% from 2023).",
     "annual_average_us_market_price_2024", "platinum-group"),
    ("lit:usgs-iridium-bullion-2025", "Refined iridium bullion, commodity proxy (USGS 2025)",
     "Ir", "Precious Metal / PGM", "Ir", 4800.0, "$/troy_oz",
     "USGS MCS 2025 platinum-group chapter reports an estimated 2024 annual average price of $4,800/troy_oz for iridium (up 3% from 2023).",
     "annual_average_us_market_price_2024", "platinum-group"),
    ("lit:usgs-ruthenium-bullion-2025", "Refined ruthenium bullion, commodity proxy (USGS 2025)",
     "Ru", "Precious Metal / PGM", "Ru", 440.0, "$/troy_oz",
     "USGS MCS 2025 platinum-group chapter reports an estimated 2024 annual average price of $440/troy_oz for ruthenium (down 6% from 2023).",
     "annual_average_us_market_price_2024", "platinum-group"),
    ("lit:usgs-gold-bullion-2025", "Refined gold bullion, commodity proxy (USGS 2025)",
     "Au", "Precious Metal", "Au", 2400.0, "$/troy_oz",
     "USGS MCS 2025 gold chapter reports an estimated 2024 annual average price of $2,400/troy_oz for gold.",
     "annual_average_us_market_price_2024", "gold"),
    ("lit:usgs-silver-bullion-2025", "Refined silver bullion, commodity proxy (USGS 2025)",
     "Ag", "Precious Metal", "Ag", 27.70, "$/troy_oz",
     "USGS MCS 2025 silver chapter reports an estimated 2024 annual average bullion price of $27.70/troy_oz (18% higher than 2023).",
     "annual_average_us_market_price_2024", "silver"),

    # ── Base metal commodity proxies ──
    ("lit:usgs-copper-cathode-2025", "Refined copper cathode, commodity proxy (USGS 2025)",
     "Cu", "Base Metal", "Cu", 4.20, "$/lb",
     "USGS MCS 2025 copper chapter reports an estimated 2024 LME grade A cash price of 420 cents/lb (=$4.20/lb).",
     "annual_average_lme_cash_price_2024", "copper"),
    ("lit:usgs-nickel-cathode-2025", "Refined nickel cathode, commodity proxy (USGS 2025)",
     "Ni", "Base Metal", "Ni", 7.70, "$/lb",
     "USGS MCS 2025 nickel chapter reports an estimated 2024 LME cash price of $7.70/lb (=$17,000/metric ton).",
     "annual_average_lme_cash_price_2024", "nickel"),
    ("lit:usgs-cobalt-cathode-2025", "Refined cobalt cathode, commodity proxy (USGS 2025)",
     "Co", "Base Metal", "Co", 17.0, "$/lb",
     "USGS MCS 2025 cobalt chapter reports an estimated 2024 U.S. spot cathode price of $17/lb (LME cash $12/lb).",
     "annual_average_us_spot_cathode_price_2024", "cobalt"),
    ("lit:usgs-zinc-cathode-2025", "Refined zinc, commodity proxy (USGS 2025)",
     "Zn", "Base Metal", "Zn", 1.26, "$/lb",
     "USGS MCS 2025 zinc chapter reports an estimated 2024 LME cash price of 126 cents/lb (=$1.26/lb).",
     "annual_average_lme_cash_price_2024", "zinc"),
    ("lit:usgs-tin-2025", "Refined tin, commodity proxy (USGS 2025)",
     "Sn", "Base Metal", "Sn", 14.00, "$/lb",
     "USGS MCS 2025 tin chapter reports an estimated 2024 LME cash price of 1,400 cents/lb (=$14.00/lb).",
     "annual_average_lme_cash_price_2024", "tin"),
    ("lit:usgs-lead-2025", "Refined lead, commodity proxy (USGS 2025)",
     "Pb", "Base Metal", "Pb", 1.10, "$/lb",
     "USGS MCS 2025 lead chapter reports an estimated 2024 North American average price of 110 cents/lb (=$1.10/lb).",
     "annual_average_north_american_price_2024", "lead"),
    ("lit:usgs-aluminum-ingot-2025", "Refined aluminum ingot, commodity proxy (USGS 2025)",
     "Al", "Base Metal", "Al", 1.30, "$/lb",
     "USGS MCS 2025 aluminum chapter reports an estimated 2024 U.S. market spot ingot price of 130 cents/lb (=$1.30/lb). Distinct from the Al2O3 support proxy at lit:usgs-alumina-2025.",
     "annual_average_us_market_spot_price_2024", "aluminum"),
    ("lit:usgs-antimony-metal-2025", "Refined antimony metal, commodity proxy (USGS 2025)",
     "Sb", "Base Metal", "Sb", 9.50, "$/lb",
     "USGS MCS 2025 antimony chapter reports an estimated 2024 metal price of $9.50/lb (up 73% from 2023 due to supply constraints).",
     "annual_average_metal_price_2024", "antimony"),
    ("lit:usgs-chromium-metal-2025", "Chromium metal, commodity proxy (USGS 2025)",
     "Cr", "Base Metal", "Cr", 5.60, "$/lb",
     "USGS MCS 2025 chromium chapter reports an estimated 2024 chromium metal (gross weight) price of $5.60/lb. Ferrochromium (Cr content) is $1.80/lb separately at lit:usgs-ferrochrome-2025.",
     "annual_average_chromium_metal_gross_weight_price_2024", "chromium"),
    ("lit:usgs-ferrochrome-2025", "Ferrochromium, commodity proxy (USGS 2025)",
     "FeCr", "Base Metal", "Cr", 1.80, "$/lb",
     "USGS MCS 2025 chromium chapter reports an estimated 2024 ferrochromium price of $1.80/lb of Cr content. Use when a Cr-promoter row would price a finished alloy form rather than purified Cr metal.",
     "annual_average_ferrochrome_cr_content_price_2024", "chromium"),
    ("lit:usgs-vanadium-pentoxide-2025", "Vanadium pentoxide, commodity proxy (USGS 2025)",
     "V2O5", "Base Metal", "V", 5.45, "$/lb",
     "USGS MCS 2025 vanadium chapter reports an estimated 2024 vanadium pentoxide (V2O5) price of $5.45/lb of V2O5. Stored against symbol V; engine treats this as an active-metal precursor row priced per pound of V2O5 (not pure V; multiply mass by V/V2O5 mass fraction 0.5602 if the recipe is normalized to pure V).",
     "annual_average_v2o5_price_2024", "vanadium"),
    ("lit:usgs-rhenium-metal-2025", "Rhenium metal pellets, commodity proxy (USGS 2025)",
     "Re", "Base Metal / Refractory Metal", "Re", 1370.0, "$/kg",
     "USGS MCS 2025 rhenium chapter reports an estimated 2024 metal pellets (99.99% pure) price of $1,370/kg.",
     "annual_average_metal_pellet_price_2024", "rhenium"),
    ("lit:usgs-tungsten-trioxide-2025", "Tungsten trioxide concentrate, commodity proxy (USGS 2025)",
     "WO3", "Base Metal / Refractory Metal", "W", 25.00, "$/kg",
     "USGS MCS 2025 tungsten chapter reports an estimated 2024 in-warehouse Rotterdam price of $250 per dry metric ton unit of WO3, which equals $25/kg of WO3 (not W metal; WO3 is 79.3% W by mass).",
     "annual_average_wo3_concentrate_price_2024", "tungsten"),
    ("lit:usgs-manganese-2025", "Manganese, commodity proxy (USGS 2025)",
     "Mn", "Base Metal", "Mn", 0.58, "$/kg",
     "USGS MCS 2025 manganese chapter reports an estimated 2024 manganese-content CIF China price of $5.80 per metric ton unit (= per 1% of a metric ton = per 10 kg of Mn), giving $0.58/kg of Mn.",
     "annual_average_mn_content_cif_china_2024", "manganese"),
    ("lit:usgs-silicon-metal-2025", "Silicon metal, commodity proxy (USGS 2025)",
     "Si", "Base Metal", "Si", 1.80, "$/lb",
     "USGS MCS 2025 silicon chapter reports an estimated 2024 silicon metal price of 180 cents/lb (=$1.80/lb of Si). This is a metallurgical-grade silicon proxy, not a SiO2 catalyst-support precursor.",
     "annual_average_silicon_metal_price_2024", "silicon"),
]


def main() -> None:
    data = json.loads(CURATED_PATH.read_text(encoding="utf-8"))
    existing = {m["library_key"] for m in data["materials"]}

    added: list[str] = []
    skipped: list[str] = []
    for (key, name, formula, cat, sym, price, unit,
         notes, pricing_basis, slug) in NEW_ENTRIES:
        if key in existing:
            skipped.append(key)
            continue
        data["materials"].append({
            "library_key": key,
            "name": name,
            "formula": formula,
            "category": cat,
            "symbol": sym,
            "price": price,
            "price_unit": unit,
            "price_scope": "literature_high_volume",
            "source": SOURCE,
            "quote_year": 2024,
            "notes": notes,
            "has_lab_data": False,
            "catalyst_domain": "general",
            "application_family": "general",
            "pricing_basis": pricing_basis,
            "reference_url": USGS_BASE_URL.format(slug=slug),
        })
        added.append(key)

    data["version"] = "2026-05-04"
    data["source"] = (
        "Sigma-Aldrich US product pages plus U.S. Geological Survey "
        "Mineral Commodity Summaries 2025/2026"
    )
    CURATED_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"ADDED ({len(added)}):")
    for k in added:
        print(f"  + {k}")
    if skipped:
        print(f"\nSKIPPED (already exist): {skipped}")
    print(f"\nTotal materials now: {len(data['materials'])}")


if __name__ == "__main__":
    main()
