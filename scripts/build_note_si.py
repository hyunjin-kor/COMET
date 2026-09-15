"""Render submission SI from the frozen screening and manufacturing records."""

import argparse
import json
from collections import Counter
from pathlib import Path

from scripts.paper_labels import CANDIDATE_LABELS, FAMILY_LABELS, STATUS_LABELS
from scripts.paper_units import PER_LB_TO_PER_KG

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper"
OUTPUT = PAPER / "supporting-information-2026-09-15.md"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def cell(value):
    return str(value).replace("|", "/").replace("\n", " ")


def render():
    sources = {
        "study": "docs/paper/manufacturing-study-2026-09-15/manufacturing_study.json",
        "library": "backend/data/manufacturing_literature.json",
        "operating": "backend/data/manufacturing_operating_references.json",
        "screening": "docs/paper/submission-2026-09-08/all_families_2026-09-08.json",
        "robustness": "docs/paper/robustness-2026-09-08/decision_robustness.json",
        "methods": "docs/paper/methods-2026-09-09/methods_study.json",
    }
    data = {key: load(path) for key, path in sources.items()}
    study, library = data["study"], data["library"]
    request, hand = study["request"], study["independent_balance"]
    protocol = request["manufacturing_protocol"]
    mc = study["monte_carlo"]
    lines = ["# Supporting Information", "", "COMET: Catalyst Overall Manufacturing Estimation Tool", "",
             "## S1. Calculation methods and boundaries", "",
             "This Supporting Information describes the manufacturing calculation, declared inputs, numerical verification, screening results and preparation-evidence coverage. "
             "The May 2026 screening results retain their original formulations and assumptions. "
             "The later preparation review does not retrospectively validate those formulations. The new manufacturing example is a hypothetical software demonstration, "
             "not an experimental catalyst cost or a comparison of matched catalytic performance.", "",
             "The screening calculations use the published Step Method and its cost-accounting framework.<sup>1,2</sup> "
             "In the batch calculation, purchases replace composition-based materials costs and operation costs replace Step Method processing costs. "
             "For each operation, electricity is measured kWh or the sum of mean power multiplied by ramp, hold and additional durations. "
             "For temperatures in °C and a ramp rate in °C/min, eq S1 gives the ramp duration in hours. Equipment occupancy is charged for the full entered operation duration; "
             "attended labor is a separate input. Gas volume is flow multiplied by its selected duration, using matching reference conditions for flow and price. "
             "Temperature, stirring speed and pressure are retained as preparation conditions; they do not infer equipment power, staffing, chemical yield or performance.", "",
             "Intermediate charges are allocated by used/recovered mass or used/prepared volume of a homogeneous solution, with successive fractions multiplied along a chain. "
             "An explicit whole-batch option assigns the full incurred expenditure to its destination before subsequent transfers. "
             "Actual operation times and incurred expenditures remain distinct from their allocated shares. Unknown recovery prevents proportional allocation. "
             "Branching transfers, co-products and density-based conversions are not inferred.", "",
             "Equations S1–S6 define the calculation. General and administrative (G&A) and sales, administrative, research and distribution (SARD) overheads "
             "are applied sequentially before the selling margin. The example excludes disposal, analytical testing, "
             "waste credits, catalyst use, tax, freight and any equipment cost not represented in the stated occupancy rate. "
             "Occupancy rates are assumed aggregate charges, not measured depreciation or purchase prices. Unknown required inputs are not treated as zero. "
             "Dry powder mass is not an electrode-area denominator.", "",
             "tᵣ = |T₁ − T₀|/(60r)    (S1)", "",
             "Eᵢ = Σⱼ Pᵢⱼtᵢⱼ    (S2)", "",
             "Vᵢ = 60Fᵢtᵍᵢ/1000    (S3)", "",
             "Bᵢ = Bᵖᵢ + pₑEᵢ + qᵢtᵢ + wℓᵢ + pᵍᵢVᵢ + Aᵢ    (S4)", "",
             "C = (Σᵢ aᵢBᵢ)/M    (S5)", "",
             "P = C(1 + g)(1 + s)/(1 − m)    (S6)", "",
             "In eq S1, T₀ and T₁ are the initial and target temperatures and r is the ramp rate. In eq S2, Eᵢ is operation electricity (kWh), "
             "Pᵢⱼ is mean power (kW), and tᵢⱼ is the duration (h) of phase j, including any explicitly powered additional period. "
             "Measured electricity can replace eq S2. In eq S3, Fᵢ is gas flow (L/min), tᵍᵢ is its selected duration (h), and Vᵢ is volume (m³); "
             "flow and price must refer to the same temperature and pressure.", "",
             "In eq S4, Bᵢ is incurred expenditure (USD), Bᵖᵢ is purchases assigned to the operation (USD), pₑ is electricity price (USD/kWh), "
             "qᵢ is equipment occupancy rate (USD/h), tᵢ is full occupancy (h), w is labor rate (USD/person-hour), ℓᵢ is attendance (person-hour), "
             "pᵍᵢ is gas price (USD/m³), and Aᵢ is an explicit additional charge (USD). Sums over multiple gases or purchases are implicit. "
             "Repeated operations contribute their incurred expenditure for each repetition. In eq S5, aᵢ is the dimensionless share allocated to the final batch "
             "and M is its recovered dry mass (kg); direct final-batch operations have aᵢ = 1. For proportional transfers, aᵢ is the product of used/recovered "
             "mass fractions or used/prepared solution-volume fractions along the transfer chain. Whole-batch charging contributes a factor of one at that transfer. "
             "In eq S6, C is manufacturing cost (USD/kg), P is selling price (USD/kg), and g, s and m are dimensionless G&A, SARD and selling-margin fractions.", "",
             "## S2. Declared manufacturing inputs", "",
             "Every numerical input below is an assumption chosen for arithmetic verification. The example does not identify a specific active phase or precursor chemistry. "
             "Dry output is independently specified; precursor stoichiometry and material yield are not inferred. The composition fields retained by the application "
             "are inactive for the purchase-based materials calculation.", "",
             "Tables S1 and S2 specify the operating conditions and purchases used in eqs S1–S6. "
             f"Final dry output: {protocol['finished_batch_mass_kg']:.3f} kg. Electricity: {protocol['electricity_usd_kwh']:.2f} USD/kWh. "
             f"Labor: {protocol['labor_usd_h']:.2f} USD/person-hour. G&A and SARD: {request['ga_overhead_pct']:.2f} and {request['sard_pct']:.2f}; "
             f"selling margin: {protocol['selling_margin_fraction']:.2f}. One batch is evaluated. The 2025 price-basis fields do not apply an index escalation to this direct batch calculation.", "",
             "All thermal operations start at 20 °C and ramp at 5 °C/min. Each includes one additional hour of passive cooling/handling with explicitly zero additional electricity "
             "but continued equipment occupancy. Cooling is a declared duration, not a heat-transfer calculation. Reduction gas flows throughout ramp, hold and additional time "
             "at 0.1 L/min and costs 10 USD/m³; both flow and price refer to 0 °C and 1 atm. Its chemical composition is unspecified because this is an arithmetic scenario.", "",
             "Table S1. Assumed operating conditions for the 0.030 kg manufacturing example.", "",
             "| Operation | Hold target (°C) | Hold or mixing (h) | Ramp / hold power (kW) | Equipment (USD/h) | Attendance (person-h) |",
             "|---|---:|---:|---|---:|---:|"]
    for op in protocol["operations"]:
        thermal = op.get("temperature_profile")
        target = thermal[0]["target_c"] if thermal else "Not assigned"
        hours = thermal[0]["hold_h"] if thermal else op["duration_h"]
        power = f"{thermal[0]['ramp_power_kw']} / {thermal[0]['hold_power_kw']}" if thermal else f"Constant {op['average_power_kw']}"
        lines.append(f"| {op['name']} | {target} | {hours} | {power} | {op['equipment_usd_h']} | {op['attended_labor_h']} |")
    lines += ["", "Table S2. Assumed purchases charged at impregnation.", "", "| Purchase at impregnation | Quantity | Unit price | Batch expenditure (USD) |", "|---|---:|---:|---:|"]
    for item in protocol["operations"][0]["purchases"]:
        lines.append(f"| {item['name']} | {item['quantity']} {item['unit']} | {item['price_usd_per_unit']} USD/{item['unit']} | {item['quantity']*item['price_usd_per_unit']:.4f} |")
    lines += ["", "## S3. Independent arithmetic verification", "",
              "Tables S3 and S4 report an independent scalar evaluation of eqs S1–S6. Thermal durations include ramp, hold and the additional hour. "
              "The application programming interface (API) produces the same baseline and endpoint results. The regression also checks the application's seeded Monte Carlo summary and histogram counts.", "",
              "Table S3. Calculated operation durations and electricity consumption.", "",
              "| Operation | Occupancy (h) | Electricity (kWh) |", "|---|---:|---:|"]
    for op, hours, energy in zip(protocol["operations"], hand["hours"], hand["kwh"], strict=True):
        lines.append(f"| {op['name']} | {hours:.6f} | {energy:.6f} |")
    lines += ["", "Table S4. Manufacturing-cost contributions, overheads and selling margin.", "", "| Cost component | Contribution per batch (USD) | Per dry product (USD/kg) |", "|---|---:|---:|"]
    for key, label in [("materials_usd", "Purchases"), ("electricity_usd", "Electricity"), ("equipment_usd", "Equipment occupancy"),
                       ("labor_usd", "Attended labor"), ("gas_usd", "Gas"), ("ga_usd", "G&A"), ("sard_usd", "SARD"), ("margin_usd", "Margin")]:
        lines.append(f"| {label} | {hand[key]:.6f} | {hand[key]/protocol['finished_batch_mass_kg']:.6f} |")
        if key == "gas_usd":
            lines.append(f"| Manufacturing cost | {hand['manufacturing_usd_kg']*protocol['finished_batch_mass_kg']:.6f} | {hand['manufacturing_usd_kg']:.6f} |")
    lines.append(f"| Selling price | {hand['selling_price_usd_kg']*protocol['finished_batch_mass_kg']:.6f} | {hand['selling_price_usd_kg']:.6f} |")
    lines += ["", f"Manufacturing cost before overheads and margin is {hand['manufacturing_usd_kg']:.6f} USD/kg; "
              f"selling price is {hand['selling_price_usd_kg']:.6f} USD/kg. "
              "One extra calcination hour costs (1.2 kW × 0.1 USD/kWh + 3 USD/h)/0.030 kg × 1.05 × 1.05/0.90 "
              f"= {study['marginal_calcination_hour_usd_kg']:.2f} USD/kg. Attendance does not change in this scenario.", "",
              "## S4. Manufacturing sensitivity and uncertainty", "",
              "Table S5 changes only the named input at each endpoint; all other batch inputs remain fixed. Temperature does not determine an assumed power change. "
              "The dry-output endpoints therefore assess cost allocation, not predicted chemical yields or scale economies.", "",
              "Table S5. One-at-a-time sensitivity endpoints for the manufacturing example.", "",
              "| Varied input | Low | High | Selling price at low (USD/kg) | Selling price at high (USD/kg) |", "|---|---:|---:|---:|---:|"]
    for row in study["sensitivity"]:
        lines.append(f"| {row['label']} | {row['low']} {row['unit']} | {row['high']} {row['unit']} | {row['low_usd_kg']:.4f} | {row['high_usd_kg']:.4f} |")
    lines += ["", "Figure 3(c) evaluates 21 calcination-hold values from 1 to 6 h at each of three dry masses (0.015, 0.030 and 0.045 kg), giving 63 scenarios. "
              "The machine-readable manufacturing data retain all 63 input–output pairs.", "",
              f"Monte Carlo uses seed {mc['seed']} and {mc['n_simulations']} trials. Independent uniform bounds are 0.024–0.036 kg dry output, "
              "2–4 h calcination hold, 0.9–1.5 kW hold power and 0.06–0.12 USD/kWh. All other inputs are fixed. "
              f"Successful/failed trials: {mc['n_successful']}/{mc['n_failed']}. Mean selling price is {mc['mean_usd_kg']:.4f} USD/kg; "
              f"the 5th and 95th percentiles are {mc['p5_usd_kg']:.4f} and {mc['p95_usd_kg']:.4f} USD/kg. "
              "These are scenario percentiles, not statistical confidence bounds. Individual sampled inputs and results are retained in the JavaScript Object Notation (JSON) data. "
              "The application ordinarily excludes and counts invalid combinations without clamping; this example has none. "
              "The accompanying reproduction instructions specify the random-number implementation and call sequence.", "",
              "## S5. Frozen price and screening basis", "",
              "The following May 2026 costs use the original screening formulations and route assumptions, not the subsequently curated preparation records. "
              "Table S6 reports estimated selling prices for 116 screening candidates; it does not report measured manufacturing costs. "
              "Powder values are converted from the stored legacy USD/lb fields using 1 lb = 0.45359237 kg. "
              "An electrode candidate's powder price is distinct from assembly cost per area. These observations do not establish equivalent activity or commercial quotation validity.", "",
              "Figure S1 summarizes historical metal-price inputs from Johnson Matthey and the International Monetary Fund (IMF).<sup>3,5</sup> Westmetall supplies additional current metal quotations.<sup>4</sup> "
              "Environmental mass coverage is the fraction assigned a screening inventory factor, including compound proxies; it is not a measure of inventory accuracy.<sup>6</sup>", "",
              "![Figure S1. Metal price history. Monthly averages from January 2019 to May 2026: (a) precious metals; (b) base metals. Prices are USD/kg; both price axes use logarithmic scales. Histories are unsmoothed observations, not forecasts.](figures-note-2026-09-09/fig3_metal_prices.png)", "",
              "Table S6. Estimated powder selling prices and environmental mass coverage at May 2026 prices.", "",
              "| Reaction family | Candidate model | Selling price (USD/kg) | Mass coverage (%) |", "|---|---|---:|---:|"]
    for family in data["screening"]["families"]:
        for c in family["candidates"]:
            lines.append(f"| {FAMILY_LABELS[family['family']]} | {CANDIDATE_LABELS[family['family']][c['slug']]} | {c['landed_cost_per_lb']*PER_LB_TO_PER_KG:.4f} | {c['lca']['coverage_pct']:.2f} |")
    lines += ["", "Names identify the original screening models, not experimentally verified compositions or performance-equivalent catalysts. "
              "Family membership follows the original screening catalog, including related reaction variants; it does not imply identical reaction conditions. "
              "g-C₃N₄ denotes graphitic carbon nitride; h-BN, hexagonal boron nitride; SAPO, silicoaluminophosphate. "
              "MIL-101, ZSM-5 and SSZ-13 retain their established material identifiers.", "",
              "Ranking calculations use the original four criterion weights and assigned route/performance scores retained in the frozen methods and robustness files. "
              "The complete 0.05 weight grid contains 1,771 nonnegative combinations summing to one. With 89 months and 30 families, it defines 4,728,570 scenarios. "
              "Support prices remain at baseline in monthly metal-price tests. Candidate removal is tested both with recomputed and retained cost normalization ranges. "
              "Score tests lower the baseline candidate and raise alternatives by 2, 5 or 10 points, bounded by 0 and 100. "
              "Frequencies are conditional on these enumerated scenarios. No probability distribution for future market prices or catalyst performance is inferred.", "",
              "## S6. Preparation evidence and unresolved inputs", "",
              f"The library has {len(library['profiles'])} source-specific preparations from {len({p['doi'] for p in library['profiles']})} primary sources. "
              f"Of {len(library['candidates'])} screening candidates, {sum(bool(c['profile_ids']) for c in library['candidates'])} link to at least one preparation; "
              f"{sum(not c['profile_ids'] for c in library['candidates'])} have no curated preparation. Bibliographic verification covers {len(library['sources'])} digital object identifiers (DOIs). "
              "Links may describe variants. No candidate has jointly verified catalog composition, complete preparation, utilities, recovered output and prices. "
              "Table S7 counts source/formulation discrepancies even where a related preparation is available.", "",
              "Table S7. Preparation-evidence coverage and unresolved source/formulation discrepancies.", "",
              "| Reaction family | Candidates | With preparation | Source mismatch flagged |", "|---|---:|---:|---:|"]
    for family in sorted({c["family"] for c in library["candidates"]}):
        rows = [c for c in library["candidates"] if c["family"] == family]
        lines.append(f"| {FAMILY_LABELS[family]} | {len(rows)} | {sum(bool(c['profile_ids']) for c in rows)} | {sum(c['status']=='source_mismatch' for c in rows)} |")
    statuses = Counter(c["status"] for c in library["candidates"])
    lines += ["", "Mutually exclusive catalog assessment counts: " + "; ".join(f"{STATUS_LABELS[key]}: {value}" for key, value in sorted(statuses.items())) + ".", "",
              "The companion preparation-evidence document and JSON contain all candidate assessments, source titles and DOIs, section locators, "
              "reported operation inputs, per-field evidence, transfer boundaries and unresolved values. The final targeted lookup rechecked 101 existing citations "
              "for 42 then-unlinked candidates; nine accessible texts were assessed. A failed public-copy lookup does not establish that no free source exists elsewhere. "
              "Kelvin-to-Celsius and time conversions are explicit. Overnight, room temperature, approximate values and unspecified recovery remain unquantified. "
              "Primary articles, third-party SI files and private author attachments are not redistributed.", "",
              "Operating references preserve geography, period and basis. U.S. Energy Information Administration (EIA) electricity averages can be selected as explicit scenarios; "
              "U.S. Bureau of Labor Statistics (BLS) wage statistics and manufacturer connected-load ratings remain references, not measured batch costs or average operating power. "
              "Actual staffing, utility consumption and supplier prices require separate evidence.", "",
              "## S7. References", "",
              "[1] Baddour, F. G.; Snowden-Swan, L.; Super, J. D.; Van Allsburg, K. M. Estimating Precommercial Heterogeneous Catalyst Price: A Simple Step-Based Method. *Organic Process Research & Development* **2018**, *22* (12), 1599–1605. https://doi.org/10.1021/acs.oprd.8b00245.", "",
              "[2] Van Allsburg, K. M.; Tan, E. C. D.; Super, J. D.; Schaidle, J. A.; Baddour, F. G. Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. *Nature Catalysis* **2022**, *5* (4), 342–353. https://doi.org/10.1038/s41929-022-00759-6.", "",
              "[3] Johnson Matthey. PGM Prices and Trading. https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management (accessed September 11, 2026).", "",
              "[4] Westmetall. Market Data: Prices and LME Stocks. https://www.westmetall.com/en/markdaten.php (accessed September 11, 2026).", "",
              "[5] International Monetary Fund. Primary Commodity Price System (PCPS), SDMX 2.1 data service. https://api.imf.org/external/sdmx/2.1/dataflow/IMF.RES/PCPS (accessed September 11, 2026).", "",
              "[6] Nuss, P.; Eckelman, M. J. Life Cycle Assessment of Metals: A Scientific Synthesis. *PLoS ONE* **2014**, *9* (7), e101298. https://doi.org/10.1371/journal.pone.0101298.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render()
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != content:
            raise ValueError("Supporting Information differs from its sources")
    else:
        OUTPUT.write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
