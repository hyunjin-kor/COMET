"""Render the preparation evidence supplement from the curated factual catalog."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "backend/data/manufacturing_literature.json"
OPERATING = ROOT / "backend/data/manufacturing_operating_references.json"
OUTPUT = ROOT / "docs/paper/manufacturing-literature-2026-09-14.md"
SUMMARY = ROOT / "docs/paper/manufacturing-2026-09-14/review_summary.json"


def cell(value):
    return str(value).replace("|", "/").replace("\n", " ")


def render(data):
    candidates, profiles = data["candidates"], data["profiles"]
    counts = Counter(c["status"] for c in candidates)
    with_profile = sum(bool(c["profile_ids"]) for c in candidates)
    methods = data["review_methods"]
    lines = ["# Supporting information: catalyst preparation evidence", "",
             "COMET Application Note. Review date: " + data["review_date"] + ".", "",
             "## Scope and source assessment", "",
             f"The audit covers {len(candidates)} screening candidates in {len({c['family'] for c in candidates})} reaction families and {len(data['templates'])} generic process templates. "
             f"Crossref confirmed the bibliographic identity of {len(data['sources'])} distinct DOIs. "
             f"The curated library contains {len(profiles)} named preparation records from {len({p['doi'] for p in profiles})} sources; {with_profile} catalog candidates link to at least one record. "
             "A link may describe a different specimen and does not verify the catalog formulation.", "",
             methods["discovery"], "", methods["selection"], "", methods["limitations"], "",
             "Numeric values were transcribed from the stated primary sections. Kelvin values were converted to Celsius by subtracting 273.15; explicit minutes and seconds were converted to hours. "
             "Overnight, room temperature, ranges, lower bounds and unspecified ramp rates were not assigned invented numeric values. "
             "Nominal loading, measured loading, precursor molar ratio and product mass fraction remain distinct. Input precursor mass is not recovered dry output.", "",
             "## Use in COMET", "",
             "Imports create editable records with the specimen, DOI and section locator. They retain the existing cost model. "
             "Powder batch costing is enabled only after the user supplies complete operating inputs, actual dry output and explicit costs. "
             "It replaces Step Method processing cost and does not add it twice. Electricity is measured kWh or input kW multiplied by time; "
             "gas volume and price require matching reference conditions. Temperature alone does not predict furnace consumption, yield or catalytic performance. "
             "Electrode preparations remain records and cannot use a dry-powder kg denominator. Published procedures are evidence records, not laboratory operating instructions.", "",
             "Batch purchases can replace the entire composition-based materials bill. For intermediate batches, "
             "all preparation charges are allocated by mass transferred divided by mass recovered on the same material basis; "
             "unused recoverable inventory retains its share of cost. Alternatively, explicit whole-batch charging assigns the full expenditure "
             "to the receiving batch before any further transfer. Internal transfers are not purchased twice. Unknown masses block proportional "
             "allocation. Successive transfers multiply their fractions; each intermediate has one destination, and circular paths are rejected. "
             "Branching transfers and co-products require a separately defined boundary. Incurred and allocated costs, input sources "
             "and equations are preserved in the calculation trace and exports.", "",
             "Manufacturing endpoint sensitivity changes one selected numeric cost input at a time. "
             "Monte Carlo uses independent uniform distributions within user-specified absolute bounds, with discrete integer draws for repetitions. "
             "Unselected inputs remain fixed. Linked gas durations follow the sampled operation time; temperature does not infer power or yield. "
             "Invalid combinations are counted and excluded without clamping, so statistics are conditional on successful draws. "
             "Bounds describe declared scenarios, not source-validated distributions or industrial confidence intervals. "
             "JSON exports retain the baseline request, resolved prices, protocol hash, input evidence, seed, bounds and failures.", "",
             "Saved batch comparisons harmonize purchase, gas and equipment prices only for explicit specification identifiers. "
             "These identifiers declare equivalent chemical forms, grades, concentrations and purchasing or cost boundaries; "
             "names alone do not establish equivalence. Matching price units and gas reference conditions are required; no unit or density conversion is inferred. "
             "The reference estimate supplies the shared price and its input evidence; absent items use the lowest selected estimate ID. "
             "Unkeyed items retain their own prices. Common operating assumptions additionally use the reference electricity tariff, labor rate, overheads and margin. "
             "Quantities, yields and sequences remain individual. Original saved cases are preserved, and comparison JSON retains recalculated protocols, evidence and price sources.", "",
             "The frozen May 2026 screening estimates and rankings use the original composition and process assumptions. "
             "The preparation audit does not retrospectively validate these assumptions. No industrial utility use, batch yield or manufacturing cost was inferred from a paper's reaction temperature.", "",
             "## Candidate coverage", "",
             f"Source/formulation discrepancy flagged: {counts['source_mismatch']}; source-specific variant linked without that flag: {counts['variant_available']}; "
             f"exact preparation unverified with no curated variant: {counts['screening_only']}. These are mutually exclusive catalog statuses, not reproducibility grades. "
             "No candidate has jointly verified formulation, complete preparation and operational cost inputs.", "",
             "| Reaction family / candidate | Status | Preparation records | Assessment |",
             "|---|---|---|---|"]
    for c in candidates:
        refs = ", ".join(c["profile_ids"]) or "Not verified / 확인 못 함"
        lines.append(f"| {cell(c['family'] + ' / ' + c['title'])} | {c['status']} | {refs} | {cell(' '.join(c['notes']))} |")
    follow_up = data.get("follow_up_review")
    if follow_up:
        lines += ["", "## Additional primary-source assessment", "", follow_up["limitations"], "",
                  "| Selected DOI | Preparation records | Assessment |", "|---|---|---|"]
        for source in follow_up["selected_sources"]:
            lines.append(f"| [{source['doi']}]({source['primary_url']}) | {cell(', '.join(source['profile_ids']) or 'Not curated')} | {cell(source['assessment'])} |")
        lines += ["", "The accompanying JSON retains each targeted query, database endpoint, search date and hit count. "
                  "Search retrieval and the existence of a preparation record are separate outcomes.", ""]
    lines += ["", "## Source-specific preparations", ""]
    for n, p in enumerate(profiles, 1):
        lines += [f"### S{n}. {p['sample']}", "", f"Record: `{p['id']}`. Boundary: {p['boundary']}.", "",
                  f"Source: [{p['title']}]({p['url']}). [DOI {p['doi']}](https://doi.org/{p['doi']}). "
                  f"Locator: {p['locator']}. Crossref checked: {p['crossref_checked_at'][:10]}.", "",
                  "| Operation | Explicit conditions | Source details |", "|---|---|---|"]
        for op in p["operations"]:
            conditions = []
            for s in op.get("temperature_profile", []):
                conditions.append(f"{s.get('target_c', '?')} °C; hold {s.get('hold_h') if s.get('hold_h') is not None else 'unreported'} h; ramp {s.get('ramp_c_per_min') if s.get('ramp_c_per_min') is not None else 'unreported'} °C/min")
            if op.get("duration_h") is not None:
                conditions.append(f"{op['duration_h']:.6g} h")
            if op.get("atmosphere"):
                conditions.append(op["atmosphere"])
            if op.get("intermediate_batch_id"):
                conditions.append("Intermediate batch: " + op["intermediate_batch_id"])
            lines.append(f"| {cell(op['name'])} | {cell('; '.join(conditions) or 'Not quantified')} | {cell(op.get('notes', ''))} |")
        if p.get("intermediate_batches"):
            lines += ["", "Intermediate transfers (recovery is not inferred from precursor inputs):", "",
                      "| Intermediate / destination | Recovered kg | Used kg | Source details |", "|---|---|---|---|"]
            for batch in p["intermediate_batches"]:
                values = [batch.get(key) if batch.get(key) is not None else "Not verified / 확인 못 함" for key in ("produced_mass_kg", "used_mass_kg")]
                lines.append(f"| {cell(batch['name'])} / {cell(batch.get('destination_batch_id') or 'final batch')} | {values[0]} | {values[1]} | {cell(batch.get('notes', ''))} |")
        purchases = [(op, item) for op in p["operations"] for item in op.get("purchases", [])]
        if purchases:
            lines += ["", "Explicit purchases/inputs (unpriced; missing amounts remain unknown):", "",
                      "| Operation | Material | Amount | Note |", "|---|---|---|---|"]
            for op, item in purchases:
                quantity = item.get("quantity")
                amount = f"{quantity} {item['unit']}" if quantity is not None else "Not verified / 확인 못 함"
                lines.append(f"| {cell(op['name'])} | {cell(item['name'])} | {amount} | {cell(item.get('notes', ''))} |")
        lines += ["", " ".join(p["limitations"]), ""]
    lines += ["## Operating references", "",
              "These public references retain geography, period, quantity basis and source locator. "
              "Only electricity averages can be applied directly as explicit scenarios. Wage-only statistics and equipment connected loads remain reference information. "
              "No reference substitutes for measured batch electricity, actual gas conditions, staffing or a supplier quotation. "
              "The source texts and manuals are not redistributed.", "",
              "| Reference | Value | Scope | Source |", "|---|---|---|---|"]
    for reference in data.get("operating_references", []):
        evidence = reference["evidence"]
        lines.append(f"| {cell(reference['label'])} | {reference['value']} {cell(reference['unit'])} | "
                     f"{cell(reference['scope'])} | [{cell(evidence['citation'])}]({evidence['url']}); {cell(evidence['locator'])}; accessed {evidence['accessed_on']} |")
    lines += ["", "## Input provenance", "",
              "Explicit numeric preparation values carry per-field source snapshots in the JSON library. "
              "The stored value, DOI, locator and review date survive import, editing, saving and export. "
              "An edit preserves the source value and is flagged as modified; it does not become a published value. "
              "Publication metadata verification, source transcription and actual operating measurements are separate evidence levels. "
              "Library imports do not populate unknown prices or dry output mass.", ""]
    lines += ["## Generic templates", "", "All templates remain generic cost sequences, not source-verified experimental preparations.", ""]
    lines += [f"- `{t['id']}`: {t['name']}" for t in data["templates"]]
    lines += ["", "## Bibliographic and access inventory", "",
              "Access flags indicate a retrieved public full text or PDF supplement; they do not indicate that its Methods were curated. "
              "No source article, supporting PDF or private author attachment is redistributed. All source materials retain their own terms.", "",
              "| DOI and title | Public full text | Public supplement | Method record |", "|---|---|---|---|"]
    for s in data["sources"]:
        flags = ["Yes" if s[k] else "Not verified" for k in ("public_fulltext", "public_supplement", "methods_curated")]
        lines.append(f"| [{cell(s['title'])}]({s['url']}) — {s['doi']} | {' | '.join(flags)} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    data["operating_references"] = json.loads(OPERATING.read_text(encoding="utf-8"))["references"]
    summary = {"review_date": data["review_date"], "candidates": len(data["candidates"]),
               "families": len({c["family"] for c in data["candidates"]}),
               "profiles": len(data["profiles"]), "primary_sources": len({p["doi"] for p in data["profiles"]}),
               "candidates_with_profile": sum(bool(c["profile_ids"]) for c in data["candidates"]),
               "source_mismatches": sum(c["status"] == "source_mismatch" for c in data["candidates"]),
               "crossref_dois": len(data["sources"]), "source": SOURCE.relative_to(ROOT).as_posix(),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "operating_references": len(data["operating_references"]),
               "operating_source": OPERATING.relative_to(ROOT).as_posix(),
               "operating_source_sha256": hashlib.sha256(OPERATING.read_bytes()).hexdigest()}
    for path, content in ((OUTPUT, render(data)), (SUMMARY, json.dumps(summary, indent=2) + "\n")):
        if args.check:
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Preparation evidence output differs: {path.name}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
