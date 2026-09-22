"""Render submission SI from the frozen screening and manufacturing records."""

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from scripts.paper_labels import CANDIDATE_LABELS, FAMILY_LABELS, STATUS_LABELS
from scripts.paper_units import KG_PER_SHORT_TON, PER_LB_TO_PER_KG

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper"
OUTPUT = PAPER / "supporting-information-2026-09-15.md"
RUN_DATE = "2026-09-21"
RUN = f"docs/paper/submission-{RUN_DATE}"
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
# Readable titles of the screened price-evidence cases (the record's own titles lack spacing).
EVIDENCE_TITLES = {
    "E01": "Axens STR111 commercial catalyst base-price schedule (filed technology-transfer agreement)",
    "E02": "5 wt% Pt on Vulcan XC-72, 1 g public catalog offer",
    "E03": "10 wt% Pt on Vulcan XC-72, 1 g public catalog offer",
    "E04": "20 wt% Ni on Vulcan XC-72R Grade S, 1 g public catalog offer",
    "E05": "Chloroplatinic-acid preparation quote within a DOE catalyst-ink cost model",
    "E06": "Battelle reported bulk XC-72 carbon quote",
    "E07": "Hog et al. 2026 mixed supplier/literature consumable-price regression",
    "E08": "BPCL 2013 VGO hydrodesulfurization catalyst procurement price form",
    "E09": "ESTCP PCB demonstration-informed treatment-cost model",
    "E10": "Mendoza Suarez and Tatarchuk 2025 catalyst-price sensitivity assumptions",
}


def month_label(value):
    """2026-08 -> August 2026."""
    return f"{MONTHS[int(value[5:7]) - 1]} {value[:4]}"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def cell(value):
    return str(value).replace("|", "/").replace("\n", " ")


def formula(name):
    """Digits that follow an element or a closing parenthesis become subscripts (Al2O3 -> Al₂O₃)."""
    return re.sub(r"(?<=[A-Za-z)])\d+", lambda m: m.group().translate(str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")), name)


def active_phase(candidate):
    """Active metals with their loadings, or the active phase of a bulk formulation."""
    metals = [c for c in candidate["components"] if c["role"] == "active_metal"]
    phases = metals or [c for c in candidate["components"] if c["role"] in ("active_catalyst", "co_active_catalyst")]
    return "; ".join(f"{formula(c['name'])} {c['wt_pct']:g}" for c in phases)


def render():
    sources = {
        "study": "docs/paper/manufacturing-study-2026-09-15/manufacturing_study.json",
        "library": "backend/data/manufacturing_literature.json",
        "operating": "backend/data/manufacturing_operating_references.json",
        "screening": f"{RUN}/all_families_{RUN_DATE}.json",
        "live": f"{RUN}/all_families_live_{RUN_DATE}.json",
        "summary": f"{RUN}/paper_summary_{RUN_DATE}.json",
        "live_basis": f"{RUN}/live_basis_{RUN_DATE}.json",
        "reference_basis": f"{RUN}/reference_basis_{RUN_DATE}.json",
        "robustness": f"docs/paper/robustness-{RUN_DATE}/decision_robustness.json",
        "methods": f"docs/paper/methods-{RUN_DATE}/methods_study.json",
        "whatif": f"docs/paper/whatif-{RUN_DATE}/whatif_study.json",
        "examples": f"docs/paper/verification-{RUN_DATE}/step_method_examples.json",
        "table62": f"{RUN}/table62_reproduction_{RUN_DATE}.json",
        "evidence": "docs/sources/external-cost-evidence-2026-09-07.json",
    }
    data = {key: load(path) for key, path in sources.items()}
    study, library = data["study"], data["library"]
    # Library compositions and production scales of the screening candidates (Table S7).
    catalogs = {}
    for path in sorted((ROOT / "backend/data").glob("*_benchmark.json")):
        catalog = json.loads(path.read_text(encoding="utf-8"))
        catalogs[catalog["family"]] = {c["slug"]: c for c in catalog["candidates"]}
    for family in data["screening"]["families"]:
        if {c["slug"] for c in family["candidates"]} != set(catalogs[family["family"]]):
            raise ValueError(f"The library candidates of {family['family']} differ from the frozen screening run")
    crossover = load(f"docs/paper/price-crossovers-{RUN_DATE}/crossover_mechanisms.json")
    with (PAPER / f"price-crossovers-{RUN_DATE}/family_summary.csv").open(encoding="utf-8-sig", newline="") as handle:
        census = {(row["family"], row["period"]): row for row in csv.DictReader(handle)}
    states = {row["date"]: row for row in crossover["ammonia_boundary"]["observations"]}
    changes = {family: int(census[(family, "monthly")]["cost_changes"]) for family in ("ammonia-cracking", "dry-reforming", "water-gas-shift")}
    if any(int(census[(family, "monthly")]["app_changes"]) for family in changes):
        raise ValueError("The SI text states that the balanced recommendation does not change in these families")
    # Families of Figure 4(e): months as the lowest-cost candidate and number of changes, thermal families first.
    replay = load(f"docs/paper/price-crossovers-{RUN_DATE}/price_crossovers.json")
    leaders = []
    for row in sorted(replay["families"], key=lambda row: (row["domain"] != "thermal", row["family"])):
        months = row["periods"]["monthly"]["summary"]["winner_counts"]["cost_winner"]
        if len(months) > 1:
            named = ", ".join(f"{CANDIDATE_LABELS[row['family']][slug]} {count}" for slug, count in sorted(months.items(), key=lambda item: -item[1]))
            name = re.sub(r"^[A-Z]+ \((.+)\)$", r"\1", FAMILY_LABELS[row["family"]])
            count = int(census[(row["family"], "monthly")]["cost_changes"])
            leaders.append(f"{name if name.startswith('CO') else name[0].lower() + name[1:]}: {named} ({count} change{'s' if count != 1 else ''})")
    if len(leaders) != replay["summary"]["monthly"]["cost_winner"]:
        raise ValueError("The families of Figure 4(e) differ from the stored count of lowest-cost changes")
    comparison = data["summary"]["live_reference_comparison"]
    reference_families = {row["family"]: row for row in data["screening"]["families"]}
    live_families = {row["family"]: row for row in data["live"]["families"]}

    def scores(families, family, slug):
        return next(c["scores"] for c in families[family]["candidates"] if c["slug"] == slug)

    live_changes = []
    for row in comparison["rows"]:
        if row["profile"] != "balanced" or not row["changed"]:
            continue
        before = scores(reference_families, row["family"], row["reference_winner"])
        after = scores(live_families, row["family"], row["reference_winner"])
        live_changes.append((row["family"], row["reference_winner"], row["live_winner"], before, after))
    if len(live_changes) != comparison["changed_by_profile"]["balanced"]:
        raise ValueError("Live-quotation leader changes do not match the stored summary")
    observed = data["live_basis"]["observation_started_at_utc"][:10]
    basis = month_label(data["summary"]["basis_month"])
    robust = data["robustness"]["summary"]
    support_months = sorted(q["fetched_at"][:7] for q in data["reference_basis"]["price_basis"].values() if q["source"].startswith("UN Comtrade"))
    example = data["methods"]["normalization"]["example"]
    if example["family"] != "ammonia-cracking" or example["reference_winner"] == example["renormalized_winner"]:
        raise ValueError("The SI describes a ranking reversal in ammonia cracking after candidate removal")
    whatif = data["whatif"]
    labels = CANDIDATE_LABELS["ammonia-cracking"]
    assignment = whatif["route_assignment"]
    spreads = [max(v["selling_price_per_lb"] for v in row["by_template"].values()) - min(v["selling_price_per_lb"] for v in row["by_template"].values())
               for family in assignment["families"] for row in family["candidates"]]
    if max(spreads) - min(spreads) > 2e-4:
        raise ValueError("The SI states one selling-price range of the five methods for every candidate")
    method_spread = spreads[0]
    if len(assignment["templates"]) != 5:
        raise ValueError("The SI names five preparation methods")
    excluded = [(family["family"], row) for family in assignment["families"] for row in family["excluded"]]
    excluded_note = ("Candidates with a component role the calculator request does not accept are excluded: "
                     + "; ".join(f"{CANDIDATE_LABELS[family][row['slug']]} ({', '.join(role.replace('_', ' ') for role in row['roles'])})" for family, row in excluded) + ". ") if excluded else ""
    # Table S1: the stand-alone record adds the effective-rate lines of the FCC case to the frozen primary-run record.
    examples = data["examples"]
    for case, frozen in zip(examples, data["table62"], strict=True):
        if {k: v for k, v in case.items() if k != "with_published_rate"} != {k: v for k, v in frozen.items() if k != "with_published_rate"} \
                or {k: v for k, v in case.get("with_published_rate", {}).items() if k != "rows"} != frozen.get("with_published_rate", {}):
            raise ValueError("The Step Method example record differs from the frozen primary run")
    example_rows = [{row["key"]: row for row in rows} for rows in (examples[0]["rows"], examples[1]["rows"], examples[2]["with_published_rate"]["rows"])]
    nickel_margin = examples[1]["margin"]
    linked = Counter(c["status"] for c in library["candidates"] if c["profile_ids"])
    unlinked = Counter(c["status"] for c in library["candidates"] if not c["profile_ids"])
    if set(linked) != {"variant_available", "source_mismatch"} or set(unlinked) != {"screening_only", "source_mismatch"}:
        raise ValueError("The preparation-link reconciliation sentence no longer describes the library")
    evidence = data["evidence"]
    if evidence["overall_status"].startswith("partial") is False or any(
            all(value == "matched" for value in case["match_requirements"].values()) for case in evidence["cases"]):
        raise ValueError("The SI states that no screened external price case is fully matched")
    request, hand = study["request"], study["independent_balance"]
    protocol = request["manufacturing_protocol"]
    mc = study["monte_carlo"]
    lines = ["# Supporting Information", "", "COMET: Catalyst Overall Manufacturing Estimation Tool", "",
             "## S1. Calculation methods and boundaries", "",
             "This Supporting Information describes the manufacturing calculation, the stated batch conditions, numerical verification, screening results with library loadings and production scales, calculator parametric analyses, observed-price and preparation-method cost crossovers, ranking sensitivity, first-ranked candidates under current quotations, the documentation of literature preparations, the screened published prices and application views. "
             f"The {basis} screening results retain their original formulations and assumptions. "
             "The later preparation review does not retrospectively validate those formulations. The new manufacturing example is a hypothetical software demonstration, "
             "not an experimental catalyst cost or a comparison of matched catalytic performance.", "",
             "The screening calculations use the published Step Method and its cost-accounting framework.<sup>1,2</sup> "
             "A component with mass fraction w in the catalyst, mass fraction f in the pure precursor, precursor purity p and retention y requires w/(f p y) kg of precursor per kg of catalyst. "
             "Table S1 compares every line of the three demonstration cases of the method with the COMET calculation from the published conditions and prices.<sup>1</sup> "
             "The lines before the margin agree within the rounding of the published table. "
             f"For Ni/Al₂O₃ the published table applies a margin of {nickel_margin['table_footnote_pct_of_premargin']:.0f}% of the pre-margin cost, whereas COMET applies the production-scale correlation of the same source, "
             f"which gives {nickel_margin['comet_pct_of_premargin']:.2f}% at this production scale. For the fluid catalytic cracking (FCC) catalyst the source states an effective production rate of "
             f"{examples[2]['with_published_rate']['effective_rate_ton_per_day'] * KG_PER_SHORT_TON:,.1f} kg/day in place of the nominal rate, and Table S1 uses that rate. "
             f"Its margin differs in the same way ({examples[2]['margin']['table_footnote_pct_of_premargin']:.0f}% of the pre-margin cost in the table, {examples[2]['margin']['comet_pct_of_premargin']:.2f}% from the correlation). "
             "Prices are converted from the published values per pound.", "",
             "Table S1. Line-by-line reproduction of the published Step Method examples (published value / COMET).", "",
             "| Line | 2 wt% Pt/C | 21 wt% Ni/Al₂O₃ | FCC catalyst |", "|---|---:|---:|---:|",
             *[f"| {name} | " + " | ".join(f"{rows[key]['published'] * factor:{spec}} / {rows[key]['comet'] * factor:{spec}}" for rows in example_rows) + " |"
               for key, name, factor, spec in (("step_cost_per_hr", "Hourly step cost (USD/h)", 1, ",.0f"), ("campaign_days", "Campaign duration (d)", 1, ".2f"),
                                               ("campaign_cost", "Campaign cost (USD)", 1, ",.0f"), ("processing_cost_per_lb", "Processing cost (USD/kg)", PER_LB_TO_PER_KG, ".2f"),
                                               ("subtotal_per_lb", "Materials and processing (USD/kg)", PER_LB_TO_PER_KG, ".2f"), ("ga_per_lb", "G&A (USD/kg)", PER_LB_TO_PER_KG, ".2f"),
                                               ("sard_per_lb", "SARD (USD/kg)", PER_LB_TO_PER_KG, ".2f"), ("margin_per_lb", "Margin (USD/kg)", PER_LB_TO_PER_KG, ".2f"),
                                               ("estimated_price_per_lb", "Selling price (USD/kg)", PER_LB_TO_PER_KG, ".2f"))],
             "", "G&A, general and administrative; SARD, sales, administrative, research and distribution. The Pt/C prices exclude platinum value.", "",
             "In the batch calculation, purchases replace composition-based materials costs and operation costs replace Step Method processing costs. "
             "For each operation, electricity is measured kWh or the sum of mean power multiplied by ramp, hold and additional durations. "
             "For temperatures in °C and a ramp rate in °C/min, eq S1 gives the ramp duration in hours. Equipment occupancy is charged for the full entered operation duration; "
             "operator labor is entered separately. Gas volume is flow multiplied by its selected duration, using matching reference conditions for flow and price. "
             "Temperature, stirring speed and pressure are retained as preparation conditions; they do not infer equipment power, staffing, chemical yield or performance.", "",
             "Intermediate charges are allocated by used/recovered mass or used/prepared volume of a homogeneous solution, with successive fractions multiplied along a chain. "
             "An explicit whole-batch option assigns the full incurred expenditure to its destination before subsequent transfers. "
             "Actual operation times and incurred expenditures remain distinct from their allocated shares. Unknown recovery prevents proportional allocation. "
             "Branching transfers, co-products and density-based conversions are not inferred. Figure S1 illustrates the allocation chain: a solution aliquot charged by volume fraction, "
             "an intermediate solid transferred by mass fraction, and the final dry batch that carries the allocated shares.", "",
             "![Figure S1. Intermediate transfers. Conceptual sequence of a solution aliquot (volume fraction), an intermediate solid transfer (mass fraction) and the final dry batch used in eq S5. The drawing is conceptual and contains no numerical result. Artwork used Google Gemini's image-generation tool; labels are native.](figures-si-2026-09-16/figS1_allocation.png)", "",
             "Equations S1–S6 define the calculation. General and administrative (G&A) and sales, administrative, research and distribution (SARD) overheads "
             "are applied sequentially before the selling margin. The example excludes disposal, analytical testing, "
             "waste credits, catalyst use, tax, freight and any equipment cost not represented in the stated occupancy rate. "
             "Occupancy rates are assumed aggregate charges, not measured depreciation or purchase prices. Unknown required conditions are not treated as zero. "
             "Dry powder mass is not an electrode-area denominator.", "",
             "tᵣ = |T₁ − T₀|/(60r)    (S1)", "",
             "Eᵢ = Σⱼ Pᵢⱼtᵢⱼ    (S2)", "",
             "Vᵢ = 60Fᵢtᵍᵢ/1000    (S3)", "",
             "Bᵢ = Bᵖᵢ + pₑEᵢ + qᵢtᵢ + pₗℓᵢ + pᵍᵢVᵢ + Aᵢ    (S4)", "",
             "C = (Σᵢ aᵢBᵢ)/M    (S5)", "",
             "P = C(1 + g)(1 + s)/(1 − m)    (S6)", "",
             "In eq S1, T₀ and T₁ are the initial and target temperatures and r is the ramp rate. In eq S2, Eᵢ is operation electricity (kWh), "
             "Pᵢⱼ is mean power (kW), and tᵢⱼ is the duration (h) of phase j, including any explicitly powered additional period. "
             "Measured electricity can replace eq S2. In eq S3, Fᵢ is gas flow (L/min), tᵍᵢ is its selected duration (h), and Vᵢ is volume (m³); "
             "flow and price must refer to the same temperature and pressure.", "",
             "In eq S4, Bᵢ is incurred expenditure (USD), Bᵖᵢ is purchases assigned to the operation (USD), pₑ is electricity price (USD/kWh), "
             "qᵢ is equipment occupancy rate (USD/h), tᵢ is full occupancy (h), pₗ is labor rate (USD/person-hour), ℓᵢ is attendance (person-hour), "
             "pᵍᵢ is gas price (USD/m³), and Aᵢ is an explicit additional charge (USD). Sums over multiple gases or purchases are implicit. "
             "Repeated operations contribute their incurred expenditure for each repetition. In eq S5, aᵢ is the dimensionless share allocated to the final batch "
             "and M is its recovered dry mass (kg); direct final-batch operations have aᵢ = 1. For proportional transfers, aᵢ is the product of used/recovered "
             "mass fractions or used/prepared solution-volume fractions along the transfer chain. Whole-batch charging contributes a factor of one at that transfer. "
             "In eq S6, C is manufacturing cost (USD/kg), P is selling price (USD/kg), and g, s and m are dimensionless G&A, SARD and selling-margin fractions.", "",
             "## S2. Stated batch conditions", "",
             "Every numerical value below is an assumption chosen for arithmetic verification. The example does not identify a specific active phase or precursor chemistry. "
             "The dry product mass is specified independently; precursor stoichiometry and material yield are not inferred. The composition entries of the application "
             "are inactive for the purchase-based materials calculation.", "",
             "Tables S2 and S3 specify the operating conditions and purchases used in eqs S1–S6. "
             f"Final dry product mass: {protocol['finished_batch_mass_kg']:.3f} kg. Electricity: {protocol['electricity_usd_kwh']:.2f} USD/kWh. "
             f"Labor: {protocol['labor_usd_h']:.2f} USD/person-hour. G&A and SARD: {request['ga_overhead_pct']:.2f} and {request['sard_pct']:.2f}; "
             f"selling margin: {protocol['selling_margin_fraction']:.2f}. One batch is evaluated. The 2025 price-basis fields do not apply an index escalation to this direct batch calculation.", "",
             "All thermal operations start at 20 °C and ramp at 5 °C/min. Each includes one additional hour of passive cooling/handling with explicitly zero additional electricity "
             "but continued equipment occupancy. Cooling is a stated duration, not a heat-transfer calculation. Reduction gas flows throughout ramp, hold and additional time "
             "at 0.1 L/min and costs 10 USD/m³; both flow and price refer to 0 °C and 1 atm. Its chemical composition is unspecified because this is an arithmetic scenario.", "",
             "Table S2. Assumed operating conditions for the 0.030 kg manufacturing example.", "",
             "| Operation | Hold target (°C) | Hold or mixing (h) | Ramp / hold power (kW) | Equipment (USD/h) | Attendance (person-h) |",
             "|---|---:|---:|---|---:|---:|"]
    for op in protocol["operations"]:
        thermal = op.get("temperature_profile")
        target = thermal[0]["target_c"] if thermal else "Not assigned"
        hours = thermal[0]["hold_h"] if thermal else op["duration_h"]
        power = f"{thermal[0]['ramp_power_kw']} / {thermal[0]['hold_power_kw']}" if thermal else f"Constant {op['average_power_kw']}"
        lines.append(f"| {op['name']} | {target} | {hours} | {power} | {op['equipment_usd_h']} | {op['attended_labor_h']} |")
    lines += ["", "Table S3. Assumed purchases charged at impregnation.", "", "| Purchase at impregnation | Quantity | Unit price | Batch expenditure (USD) |", "|---|---:|---:|---:|"]
    for item in protocol["operations"][0]["purchases"]:
        lines.append(f"| {item['name']} | {item['quantity']} {item['unit']} | {item['price_usd_per_unit']} USD/{item['unit']} | {item['quantity']*item['price_usd_per_unit']:.4f} |")
    lines += ["", "## S3. Independent arithmetic verification", "",
              "Tables S4 and S5 report an independent scalar evaluation of eqs S1–S6. Thermal durations include ramp, hold and the additional hour. "
              "The application programming interface (API) produces the same baseline and endpoint results. The regression also checks the application's Monte Carlo summary (fixed random seed) and histogram counts.", "",
              "Table S4. Calculated operation durations and electricity consumption.", "",
              "| Operation | Occupancy (h) | Electricity (kWh) |", "|---|---:|---:|"]
    for op, hours, energy in zip(protocol["operations"], hand["hours"], hand["kwh"], strict=True):
        lines.append(f"| {op['name']} | {hours:.6f} | {energy:.6f} |")
    lines += ["", "Table S5. Manufacturing-cost contributions, overheads and selling margin.", "", "| Cost component | Contribution per batch (USD) | Per dry product (USD/kg) |", "|---|---:|---:|"]
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
              "Table S6 changes only the named condition at each endpoint; all other batch conditions remain fixed. Temperature does not determine an assumed power change. "
              "The dry-product-mass endpoints therefore assess cost allocation, not predicted chemical yields or scale economies.", "",
              "Table S6. One-at-a-time sensitivity endpoints for the manufacturing example.", "",
              "| Varied condition | Low | High | Selling price at low (USD/kg) | Selling price at high (USD/kg) |", "|---|---:|---:|---:|---:|"]
    for row in study["sensitivity"]:
        lines.append(f"| {row['label']} | {row['low']} {row['unit']} | {row['high']} {row['unit']} | {row['low_usd_kg']:.4f} | {row['high_usd_kg']:.4f} |")
    lines += ["", "Figure S2 plots the same endpoints as departures from the baseline selling price. Dry product mass dominates because the fixed batch expenditure is divided by the recovered mass; "
              "calcination power changes the price little because electricity is a small part of the assumed operating cost compared with equipment occupancy (Table S5).", "",
              f"![Figure S2. Sensitivity endpoints. Selling price at the low and high value of each condition in Table S6; the vertical line marks the baseline of {hand['selling_price_usd_kg']:.2f} USD/kg. Each bar changes one condition while all other batch conditions remain fixed.](figures-si-2026-09-16/figS2_sensitivity.png)", "",
              "Figure 3(c) evaluates 21 calcination-hold values from 1 to 6 h at each of three dry masses (0.015, 0.030 and 0.045 kg), giving 63 scenarios. "
              "The machine-readable manufacturing data retain all 63 input–output pairs.", "",
              f"Monte Carlo uses seed {mc['seed']} and {mc['n_simulations']} trials. Independent uniform bounds are 0.024–0.036 kg dry product mass, "
              "2–4 h calcination hold, 0.9–1.5 kW hold power and 0.06–0.12 USD/kWh. All other conditions are fixed. "
              f"Successful/failed trials: {mc['n_successful']}/{mc['n_failed']}. Mean selling price is {mc['mean_usd_kg']:.4f} USD/kg; "
              f"the 5th and 95th percentiles are {mc['p5_usd_kg']:.4f} and {mc['p95_usd_kg']:.4f} USD/kg. "
              "These are scenario percentiles, not statistical confidence bounds. Individual sampled values and results are retained in the accompanying data file (JSON). "
              "The application ordinarily excludes and counts invalid combinations without truncation; this example has none. "
              "The accompanying reproduction instructions specify the random-number generator and the sampling order. "
              "Figure S3 shows the distribution of the trial results and the sampled dry product mass against the resulting selling price; the sampled dry product mass accounts for most of the spread.", "",
              f"![Figure S3. Monte Carlo samples. (a) Selling-price histogram of the {mc['n_simulations']} trials (fixed random seed) with the mean (solid line) and the 5th and 95th percentiles (dashed lines). (b) Sampled dry product mass against selling price for the same trials. Bounds are scenario assumptions, not measured variability.](figures-si-2026-09-16/figS3_monte_carlo.png)", "",
              "## S5. Price basis and screening results", "",
              f"The following {basis} costs use the original screening formulations and route assumptions, not the subsequently documented preparation records. "
              "Table S7 reports estimated selling prices for 116 screening candidates with the active-metal loading (or, for bulk formulations, the active phase) and the production scale recorded in the library for each candidate; it does not report measured manufacturing costs. "
              "Each candidate is priced at its own library loading, which follows the cited source where it reports one and is otherwise an engineering assumption noted in the library; loadings are not normalized across candidates. "
              "Powder values are converted from the original USD/lb values using 1 lb = 0.45359237 kg, and production scales from short tons. "
              "An electrode candidate's powder price is distinct from assembly cost per area. These observations do not establish equivalent activity or commercial quotation validity.", "",
              "Johnson Matthey<sup>3</sup> and Westmetall<sup>4</sup> supply current metal quotations. Figure S4 summarizes the monthly price histories from Johnson Matthey and the International Monetary Fund (IMF).<sup>5</sup> "
              "Environmental mass coverage is the fraction assigned a screening inventory factor, including compound proxies; it is not a measure of inventory accuracy.<sup>6</sup>", "",
              f"Reference metal prices are the {basis} monthly averages. U.S. import unit values of support materials are published several months later, so each support uses its latest verified "
              f"monthly value at or before that month ({month_label(support_months[0])} to {month_label(support_months[-1])}); the observation month is recorded with the price and no month is interpolated. "
              "Metals without a published monthly series keep their annual reference values.", "",
              f"![Figure S4. Metal price history. Monthly averages from January 2019 to {basis}: (a) precious metals; (b) base metals. Prices are USD/kg; both price axes use logarithmic scales. Histories are unsmoothed observations, not forecasts.](figures-si-2026-09-16/figS4_metal_prices.png)", "",
              f"Table S7. Library loadings, production scales, estimated powder selling prices and environmental mass coverage at {basis} prices.", "",
              "| Reaction family | Candidate model | Active metal or phase (wt%) | Production scale (kg) | Selling price (USD/kg) | Mass coverage (%) |", "|---|---|---|---:|---:|---:|"]
    for family in data["screening"]["families"]:
        for c in family["candidates"]:
            entry = catalogs[family["family"]][c["slug"]]
            lines.append(f"| {FAMILY_LABELS[family['family']]} | {CANDIDATE_LABELS[family['family']][c['slug']]} | {active_phase(entry)} | "
                         f"{entry['order_size_tons'] * KG_PER_SHORT_TON:,.1f} | {c['landed_cost_per_lb']*PER_LB_TO_PER_KG:.4f} | {c['lca']['coverage_pct']:.2f} |")
    lines += ["", "Names identify the original screening models, not experimentally verified compositions or performance-equivalent catalysts. "
              "Loadings are the library values; a bulk formulation lists its active phase at 100 wt% or the stated split. "
              "Family membership follows the original screening library, including related reactions; it does not imply identical reaction conditions. "
              "g-C₃N₄ denotes graphitic carbon nitride; h-BN, hexagonal boron nitride; SAPO, silicoaluminophosphate. "
              "MIL-101, ZSM-5 and SSZ-13 retain their established material identifiers.", "",
              "Figure 4(a)–(c) of the main article varies one calculator variable at a time for two alumina-supported catalysts prepared by incipient wetness impregnation. "
              f"Table S8 lists the variables and the resulting selling prices at {basis} prices. Production scales (the catalyst mass of one order) are entered in short tons and shown in kilograms; "
              "operations that are unavailable at the production scale of an order are replaced by the application's scale equivalents (a batch kiln for the continuous kiln at the small scale). "
              "Precious-metal value is part of the materials cost and carries overheads and margin; no spent-catalyst credit is applied. "
              "The selling price is linear in the metal price, so the ruthenium price at which the two catalysts cost the same per kilogram follows from two evaluations and was confirmed by a third. "
              "These analyses compare manufacturing cost only; they do not compare catalytic performance.", "",
              f"Table S8. Calculator parametric analyses at {basis} prices.", "",
              "| Catalyst | Varied quantity | Range | Selling price (USD/kg) |", "|---|---|---|---|"]
    for key in ("ni", "ru"):
        spec = whatif["catalysts"][key]
        name = spec["label"].replace("Al2O3", "Al₂O₃")
        loading, order = whatif["loading"][key], whatif["order_size"][key]
        lines.append(f"| {spec['loading_wt_pct']} wt% {name} | Baseline ({spec['order_size_tons'] * KG_PER_SHORT_TON:,.1f} kg order) | — | {spec['baseline']['selling_price_per_lb'] * PER_LB_TO_PER_KG:,.2f} |")
        lines.append(f"| {name} | Metal loading | {loading[0]['loading_wt_pct']:g}–{loading[-1]['loading_wt_pct']:g} wt% | "
                     f"{loading[0]['selling_price_per_lb'] * PER_LB_TO_PER_KG:,.2f}–{loading[-1]['selling_price_per_lb'] * PER_LB_TO_PER_KG:,.2f} |")
        lines.append(f"| {spec['loading_wt_pct']} wt% {name} | Production scale | {order[0]['order_size_tons'] * KG_PER_SHORT_TON:,.1f}–{order[-1]['order_size_tons'] * KG_PER_SHORT_TON:,.1f} kg | "
                     f"{order[0]['selling_price_per_lb'] * PER_LB_TO_PER_KG:,.2f}–{order[-1]['selling_price_per_lb'] * PER_LB_TO_PER_KG:,.2f} |")
    preparation = sorted(whatif["preparation"], key=lambda row: row["selling_price_per_lb"])
    nickel = whatif["catalysts"]["ni"]
    lines.append(f"| {nickel['loading_wt_pct']} wt% Ni/Al₂O₃ | Preparation method | {len(preparation)} methods | "
                 f"{preparation[0]['selling_price_per_lb'] * PER_LB_TO_PER_KG:,.2f}–{preparation[-1]['selling_price_per_lb'] * PER_LB_TO_PER_KG:,.2f} |")
    equal = whatif["equal_cost"]
    lines += ["", f"Nickel is priced at {nickel['metal_price_per_lb'] * PER_LB_TO_PER_KG:,.2f} USD/kg and ruthenium at {whatif['catalysts']['ru']['metal_price_per_lb'] * PER_LB_TO_PER_KG:,.0f} USD/kg. "
              f"The preparation methods are: {'; '.join(row['template_name'].split(' - ')[0] for row in whatif['preparation'])}. "
              f"The two baseline catalysts would cost the same per kilogram at a ruthenium price of {equal['equal_cost_ru_price_per_lb'] * PER_LB_TO_PER_KG:,.0f} USD/kg, "
              f"{100 * equal['equal_cost_over_reference']:.2f}% of the {basis} price; the lowest monthly ruthenium price of the {equal['ru_history_months']}-month record is "
              f"{equal['ru_history_min_per_lb'] * PER_LB_TO_PER_KG:,.0f} USD/kg.", "",
              f"Table S9 prices every supported-metal candidate of the powder-catalyst families (a candidate with an active metal and a support) with its library composition under each of the "
              f"{len(assignment['templates'])} preparation methods at {assignment['order_size_tons'] * KG_PER_SHORT_TON:,.1f} kg, on the {basis} reference basis and without the route allowances of the screening library. "
              "Processing cost depends on the operation sequence and the production scale only, so the five methods span "
              f"{method_spread * PER_LB_TO_PER_KG:.2f} USD/kg of selling price for every candidate, and a candidate can be the least expensive of its family under some assignment of methods "
              "exactly when its lowest price lies below the highest price of every other candidate; with the same method applied to every candidate, the cost order never changes. "
              f"{excluded_note}Figure 4(f) of the main article shows the ammonia-cracking pair for every pair of methods. These are cost orders at equal catalyst mass; catalytic performance is not compared.", "",
              f"Table S9. Cost order under the five preparation methods at {assignment['order_size_tons'] * KG_PER_SHORT_TON:,.1f} kg.", "",
              "| Reaction family | Candidates | Least expensive by materials | Materials difference to the next candidate (USD/kg) | Candidates that can be least expensive |",
              "|---|---:|---|---:|---|"]
    for family in assignment["families"]:
        labels_of = CANDIDATE_LABELS[family["family"]]
        by_materials = sorted(family["candidates"], key=lambda row: row["materials_per_lb"])
        lines.append(f"| {FAMILY_LABELS[family['family']]} | {len(family['candidates'])} | {labels_of[by_materials[0]['slug']]} | "
                     f"{family['materials_gap_per_lb'] * PER_LB_TO_PER_KG:,.2f} | {'; '.join(labels_of[slug] for slug in family['possible_lowest_cost'])} |")
    lines += ["", f"Materials costs are per kilogram of catalyst. In {assignment['summary']['lowest_cost_depends_on_template']} of the {assignment['summary']['families']} families more than one candidate can be the least expensive.", "",
              "Ranking calculations use the original four criterion weights and assigned route/performance scores retained in the archived methods and robustness files. "
              f"The complete 0.05 weight grid contains {robust['weight_points']['0.05']:,} nonnegative combinations summing to one. With {robust['months']} months and {robust['families']} families, "
              f"it defines {robust['joint_scenarios_all_families']['0.05']:,} scenarios. "
              "Support prices remain at baseline in monthly metal-price tests. Candidate removal is tested both with recomputed and retained cost normalization ranges. "
              "Score tests lower the baseline candidate and raise alternatives by 2, 5 or 10 points, bounded by 0 and 100. "
              "Frequencies are conditional on these enumerated scenarios. No probability distribution for future market prices or catalyst performance is inferred. "
              "Route and performance scores are screening judgments assigned from the literature, not measured or predicted activity.", "",
              f"Figure 4(d) of the main article repeats the screening calculation for ammonia cracking under the {robust['months']} monthly metal-price states with formulations, production scales, route assumptions, support prices, price-source grades and route and performance scores fixed.<sup>3,5</sup> "
              f"Figure 4(e) marks the lowest-cost candidate of every month in the {len(leaders)} families where it changes. The numbers of months as the lowest-cost candidate are {'; '.join(leaders)}. "
              f"Figure S5 shows the same recalculation for methane dry reforming and water–gas shift, where the lowest-cost candidate changes {changes['dry-reforming']} and {changes['water-gas-shift']} times "
              f"({changes['ammonia-cracking']} times for ammonia cracking) while the balanced-weight recommendation of these families does not change. "
              "Panel (c) places the monthly states of ammonia cracking in the nickel–cobalt price plane: they cluster near the conditional equal-cost boundary, so modest cobalt moves change the lowest-cost candidate. "
              f"The September–October 2025 cobalt price increase from {states['2025-09']['Co'] * PER_LB_TO_PER_KG:.2f} to {states['2025-10']['Co'] * PER_LB_TO_PER_KG:.2f} USD/kg "
              "also reverses the lowest-cost candidate in methane dry reforming while nickel is nearly unchanged. "
              "These are conditional model comparisons between screening candidates, not contemporaneous supplier quotations or performance comparisons.", "",
              f"![Figure S5. Observed-price cost crossovers. Costs (modeled selling prices) under the {robust['months']} monthly price states for the candidates that attain the lowest cost at any state in (a) methane dry reforming and (b) water–gas shift; lines connect observed states and do not locate a crossover date. (c) Conditional equal-cost boundary between Co/MgO–La₂O₃ (Co/Mg–La) and Ni/γ-Al₂O₃ (Ni/Al₂O₃) in the nickel–cobalt price plane; points are monthly states colored by the cheaper candidate, and the enlarged view names September and October 2025. Ni–Co/Al–Mg denotes Ni–Co/Al–Mg–O; Ni/CeO₂, Ni/CeO₂ single sites; Cu–ZnO, Cu/ZnO/Al₂O₃; Fe–Cr, Fe₂O₃–Cr₂O₃(–CuO) (Table S7). Other prices and engineering assumptions remain at reference values.](figures-si-2026-09-16/figS5_crossovers.png)", "",
              f"![Figure S6. Ranking sensitivity. (a) First-rank frequencies over the joint price and weight scenarios; dashed line, 50%. (b) Number of the {robust['families']} reaction families retaining the baseline candidate under each test. (c) Cost differences between the first-ranked candidates before and after candidate removal; negative values indicate less expensive replacements. PEM, proton exchange membrane; AEM, anion exchange membrane; OER, oxygen evolution reaction; ORR, oxygen reduction reaction; SCR, selective catalytic reduction; RWGS, reverse water–gas shift.](figures-si-2026-09-16/figS6_ranking_tests.png)", "",
              f"Figure S6 summarizes the ranking sensitivity. Panel (a) separates, for every family, how often the baseline candidate, its most frequent alternative and the other candidates rank first over the joint scenarios; "
              f"the median baseline frequency is {robust['reference_winner_joint_share_median_pct']:.2f}%. Panel (b) counts the families whose baseline candidate ranks first in at least half of the joint scenarios "
              "or is retained under candidate removal and under route/performance-score changes of 2, 5 and 10 points; passing one test does not establish robustness to the others. "
              f"Removing one candidate that does not rank first changes the first-ranked candidate in {robust['candidate_removal_winner_changes']} of {robust['candidate_removal_cases']} tests. "
              f"In ammonia cracking, removing {labels[example['removed']]} ({example['removed_cost'] * PER_LB_TO_PER_KG:,.2f} USD/kg) leaves the other costs unchanged but contracts their range, "
              f"so renormalization changes the scores of {labels[example['rows'][0]['slug']]} and {labels[example['rows'][2]['slug']]} from "
              f"{example['rows'][0]['total_before']:.1f} and {example['rows'][2]['total_before']:.1f} to {example['rows'][0]['total_after']:.1f} and {example['rows'][2]['total_after']:.1f} and reverses their order; "
              "retaining the original range prevents every such reversal. Panel (c) gives 100 × (C₁ − C₀)/C₀ for the affected families, where C₀ and C₁ are the costs of the first-ranked candidates before and after removal.", "",
              f"The monthly recalculations hold price-source grades fixed. Replacing the {basis} reference with the current quotations collected on {observed} "
              "also changes these grades: a metal without a current quotation falls back to a reference price, and each candidate's price-reliability score "
              "weights its sources by materials-cost share. With all other conditions unchanged, the first-ranked candidate changes in "
              f"{comparison['changed_by_profile']['balanced']} families with balanced weights, {comparison['changed_by_profile']['cost-first']} with cost-first weights, "
              f"{comparison['changed_by_profile']['evidence-first']} with evidence-first weights and {comparison['changed_by_profile']['performance_zero']} with the performance weight set to zero. "
              "Table S10 lists the balanced-weight changes with the price-reliability and cost scores of the former first-ranked candidate. "
              "The current quotations are a single snapshot taken on that date, not a price history.", "",
              f"Table S10. First-ranked candidates under balanced weighting with the {basis} reference prices and with the current quotations.", "",
              f"| Reaction family | First-ranked, {basis} reference | First-ranked, current quotations | Former first-ranked: price reliability | Former first-ranked: cost score |",
              "|---|---|---|---:|---:|"]
    for family, before, after, reference_scores, live_scores in live_changes:
        lines.append(f"| {FAMILY_LABELS[family]} | {CANDIDATE_LABELS[family][before]} | {CANDIDATE_LABELS[family][after]} | "
                     f"{reference_scores['evidence']:.1f} → {live_scores['evidence']:.1f} | {reference_scores['economics']:.1f} → {live_scores['economics']:.1f} |")
    lines += ["", "Scores are on a 0–100 scale; route and performance scores are unchanged between the two bases.", "",
              "## S6. Literature preparation procedures and missing conditions", "",
              f"The library has {len(library['profiles'])} source-specific preparations from {len({p['doi'] for p in library['profiles']})} primary sources. "
              f"Of {len(library['candidates'])} screening candidates, {sum(bool(c['profile_ids']) for c in library['candidates'])} link to at least one preparation; "
              f"{sum(not c['profile_ids'] for c in library['candidates'])} have no documented preparation. Bibliographic verification covers {len(library['sources'])} digital object identifiers (DOIs). "
              "A linked preparation may be a related variant of the library formulation. No candidate has jointly verified library composition, complete preparation, utilities, recovered mass and prices. "
              "Table S11 counts source/formulation discrepancies even where a related preparation is available.", "",
              "Table S11. Documented preparations and unresolved source/formulation discrepancies.", "",
              "| Reaction family | Candidates | With documented preparation | Source mismatch noted |", "|---|---:|---:|---:|"]
    for family in sorted({c["family"] for c in library["candidates"]}):
        rows = [c for c in library["candidates"] if c["family"] == family]
        lines.append(f"| {FAMILY_LABELS[family]} | {len(rows)} | {sum(bool(c['profile_ids']) for c in rows)} | {sum(c['status']=='source_mismatch' for c in rows)} |")
    statuses = Counter(c["status"] for c in library["candidates"])
    lines += ["", "Mutually exclusive library assessment counts: " + "; ".join(f"{STATUS_LABELS[key]}: {value}" for key, value in sorted(statuses.items())) + ". "
              f"The {sum(linked.values())} candidates linked to a preparation comprise the {linked['variant_available']} with a source-specific preparation "
              f"and {linked['source_mismatch']} of the noted discrepancies; the {sum(unlinked.values())} without a documented preparation comprise the "
              f"{unlinked['screening_only']} unverified candidates and the remaining {unlinked['source_mismatch']} noted discrepancies. "
              "Figure S7 shows these assessments by reaction family.", "",
              "![Figure S7. Documentation status of the preparations. Number of screening candidates in each reaction family with a source-specific preparation, with a noted source/formulation discrepancy, or without a documented preparation. Families are ordered by the number of candidates with a source-specific preparation.](figures-si-2026-09-16/figS7_evidence.png)", "",
              "The companion preparation document and data file contain all candidate assessments, source titles and DOIs, section references, "
              "reported operating conditions, the evidence for each value, transfer boundaries and unresolved values. The final targeted lookup rechecked 101 existing citations "
              "for 42 then-unlinked candidates; nine accessible texts were assessed. A failed public-copy lookup does not establish that no free source exists elsewhere. "
              "Kelvin-to-Celsius and time conversions are explicit. Overnight, room temperature, approximate values and unspecified recovery remain unquantified. "
              "Primary articles, third-party SI files and private author attachments are not redistributed.", "",
              "Operating references preserve geography, period and basis. U.S. Energy Information Administration (EIA) electricity averages can be selected as explicit scenarios; "
              "U.S. Bureau of Labor Statistics (BLS) wage statistics and manufacturer connected-load ratings remain references, not measured batch costs or average operating power. "
              "Actual staffing, utility consumption and supplier prices require separate evidence.", "",
              "Figure S8 illustrates the record structure preserved for each imported preparation: the located source passage, the structured record in which reported values "
              "and later user modifications are distinguished, and the resulting cost contribution with its checksum.", "",
              "![Figure S8. Source-linked record. Conceptual sequence from a located passage in a source, through a structured record that distinguishes reported values from user modifications, to the cost contribution and its checksum. The drawing is conceptual. Artwork used Google Gemini's image-generation tool; labels are native.](figures-si-2026-09-16/figS8_provenance.png)", "",
              "## S7. Published catalyst prices", "",
              f"The main article states that accuracy against industrial prices is not established. Table S12 lists the {len(evidence['cases'])} cases screened on {evidence['audit_date']} "
              "in a bounded search of free public sources (government cost reports, supplier product pages, filed commercial contracts, public procurement and open papers); "
              "a case is matched only when composition and grade, quantity and production scale, price date and currency, manufacturing route and yield, and cost boundary all agree with a library formulation, "
              "and an unknown dimension is not matched. None of the cases is matched. Retail pack prices are arithmetic normalizations, not bulk quotations; a market price is not a manufacturing cost; "
              "and the three demonstration cases of Table S1 are not independent validation. The search is bounded, so a failed match does not establish that no usable price exists elsewhere.", "",
              f"Table S12. Published price cases screened on {evidence['audit_date']}.", "",
              "| Case | Type of source | Observation | Matched dimensions |", "|---|---|---|---|"]
    for case in evidence["cases"]:
        observation = case["observation"] or {}
        if "price" in observation:
            observed = f"{observation['price']:g} {observation['unit']}"
            if observation.get("pack_mass_kg"):
                observed += f" ({observation['pack_mass_kg'] * 1000:g} g pack)"
            observed += f", {observation.get('basis_month') or observation.get('observed_date') or observation.get('signed_date')}"
        elif "scenario_prices" in observation:
            observed = " and ".join(f"{p:g}" for p in observation["scenario_prices"]) + f" {observation['unit']} (assumed scenarios)"
        else:
            observed = "no usable price"
        matched = [key.replace("_", " ") for key, value in case["match_requirements"].items() if value == "matched"]
        lines.append(f"| {EVIDENCE_TITLES[case['id']]} | {case['evidence_kind'].replace('_', ' ')} | {cell(observed)} | {'; '.join(matched) or 'none'} |")
    if [case["id"] for case in evidence["cases"]] != list(EVIDENCE_TITLES):
        raise ValueError("The screened evidence cases differ from the titled list")
    lines += ["", "Cases are identified by the screening record E01–E10; the five dimensions are composition and grade, quantity and production scale, price date and currency, manufacturing route and yield, and cost boundary.", "",
              "## S8. Application interface", "",
              "Figure S9 shows two views of COMET 1.4.0 recorded with a separate test database and without connection to price services. Panel (a) shows the source attached to one imported value: "
              "the purchased quantity of a reagent in the first operation of the PtSn/Al₂O₃ pellet preparation record imported from its Methods section,<sup>7</sup> "
              "with the citation, section, DOI, access date and recorded value. Unreported conditions of imported records remain blank. "
              "Panel (b) shows the evidence section of the result page for the illustrative batch of Tables S2–S5, with the time, electricity and the electricity, equipment, labor and gas costs of each operation.", "",
              "![Figure S9. Application views. (a) Source record of one imported value in the preparation editor. (b) Operation-level time, electricity and cost contributions of the illustrative batch on the result page. Interface text is English; the Korean interface presents the same content.](figures-si-2026-09-16/figS9_interface.png)", "",
              "## S9. References", "",
              "[1] Baddour, F. G.; Snowden-Swan, L.; Super, J. D.; Van Allsburg, K. M. Estimating Precommercial Heterogeneous Catalyst Price: A Simple Step-Based Method. *Organic Process Research & Development* **2018**, *22* (12), 1599–1605. https://doi.org/10.1021/acs.oprd.8b00245.", "",
              "[2] Van Allsburg, K. M.; Tan, E. C. D.; Super, J. D.; Schaidle, J. A.; Baddour, F. G. Early-stage evaluation of catalyst manufacturing cost and environmental impact using CatCost. *Nature Catalysis* **2022**, *5* (4), 342–353. https://doi.org/10.1038/s41929-022-00759-6.", "",
              "[3] Johnson Matthey. PGM Prices and Trading. https://matthey.com/products-and-markets/pgms-and-circularity/pgm-management (accessed September 21, 2026).", "",
              "[4] Westmetall. Market Data: Prices and LME Stocks. https://www.westmetall.com/en/markdaten.php (accessed September 21, 2026).", "",
              "[5] International Monetary Fund. Primary Commodity Price System (PCPS), SDMX 2.1 data service. https://api.imf.org/external/sdmx/2.1/dataflow/IMF.RES/PCPS (accessed September 21, 2026).", "",
              "[6] Nuss, P.; Eckelman, M. J. Life Cycle Assessment of Metals: A Scientific Synthesis. *PLoS ONE* **2014**, *9* (7), e101298. https://doi.org/10.1371/journal.pone.0101298.", "",
              "[7] Niu, H.; Ma, J.; Gan, L.; Li, K. The Acid Roles of PtSn@Al₂O₃ in the Synthesis and Performance of Propane Dehydrogenation. *Molecules* **2024**, *29* (13), 2959. https://doi.org/10.3390/molecules29132959.", ""]
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
