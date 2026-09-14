"""Render the preparation evidence supplement from the curated factual catalog."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "backend/data/manufacturing_literature.json"
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
            lines.append(f"| {cell(op['name'])} | {cell('; '.join(conditions) or 'Not quantified')} | {cell(op.get('notes', ''))} |")
        lines += ["", " ".join(p["limitations"]), ""]
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
    summary = {"review_date": data["review_date"], "candidates": len(data["candidates"]),
               "families": len({c["family"] for c in data["candidates"]}),
               "profiles": len(data["profiles"]), "primary_sources": len({p["doi"] for p in data["profiles"]}),
               "candidates_with_profile": sum(bool(c["profile_ids"]) for c in data["candidates"]),
               "source_mismatches": sum(c["status"] == "source_mismatch" for c in data["candidates"]),
               "crossref_dois": len(data["sources"]), "source": SOURCE.relative_to(ROOT).as_posix(),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
    for path, content in ((OUTPUT, render(data)), (SUMMARY, json.dumps(summary, indent=2) + "\n")):
        if args.check:
            if path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Preparation evidence output differs: {path.name}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
