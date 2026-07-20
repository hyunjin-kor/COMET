# Roadmap

Last updated: 2026-07-20 (v1.3.9)

CatPrice currently does one thing well: local catalyst cost screening on Windows, validated against the published CatCost reference cases. The next stage of the project is about three things — being citable, being easier to trust, and answering more of the questions a catalysis researcher actually has. The phases below are ordered by leverage, not by difficulty.

## Phase 1 — Credibility (make it citable)

The app is used in a research context, so the biggest near-term win is making it referenceable.

- **Zenodo DOI** — done (2026-07-20): every release from v1.3.10 on is archived automatically; concept DOI `10.5281/zenodo.21451931`.
- **`CITATION.cff`** — done: GitHub shows a "Cite this repository" button.
- **Hosted documentation**: publish `docs/` with MkDocs Material on GitHub Pages. The methodology page in particular deserves a readable home — it is the strongest argument for trusting the numbers.
- **Tighten the FCC validation band**: the USY-FCC case currently passes at ±25% because the large-scale slurry route needs a public USY precursor proxy. Sourcing one (USGS / vendor public pages) and bringing the band back to ±20% closes the last gap against the published reference cases.

## Phase 2 — Distribution (make it easy to keep)

- **Auto-update**: wire `electron-updater` to GitHub Releases so users stop downloading installers by hand. This matters more with every release shipped.
- **Windows SmartScreen**: document the unsigned-binary warning honestly in the README; evaluate code signing when the user base justifies the certificate cost.
- **Winget manifest**: `winget install CatPrice` is a cheap distribution channel once releases are stable.

## Phase 3 — Capability (answer more questions)

These were previously listed as "planned" in the README and are consolidated here.

- **Lifecycle economics**: deactivation kinetics and regeneration-cycle costing, so the estimate covers catalyst lifetime, not just first fill. This is the most requested class of question the current model cannot answer.
- **Synthesis complexity penalty**: an SCScore-style term that penalizes hard-to-make compositions, catching cases where cheap ingredients hide an expensive route.
- **Chemistry validation layer**: an RDKit/ChemPy check on composition inputs (stoichiometry sanity, precursor plausibility) before money math runs on them.
- **Structure-editor entry**: let users start from a drawn or imported structure instead of composition rows.
- **CatCost JSON import polish**: the import endpoint exists; the workflow around it (mapping report, partial-import handling) needs UX attention so CatCost users can migrate a workbook in one sitting.

## Phase 4 — Reach

- **2026 index data**: extend ChemPPI/CEPCI series when the annual values publish; the BLS updater already automates ChemPPI.
- **Korean documentation**: a Korean getting-started page, given where much of the current user base sits.
- **Community templates**: accept benchmark-family and process-template contributions with a documented review bar (source links required, no proprietary data).

## Standing rule

Every release bumps `package.json`, `frontend/package.json`, `pyproject.toml`, and `backend/main.py:APP_VERSION` together — `backend/tests/test_version_sync.py` fails the suite if they disagree. Docs quote `releases/latest` instead of hardcoded versions wherever possible.
