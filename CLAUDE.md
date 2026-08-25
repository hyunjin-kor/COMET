# CatTEA Claude Handoff

Entry point for Claude / Claude Code on CatTEA. Read this first, then `AGENTS.md`.

## Read first

1. `AGENTS.md` — master dev guide (rules, architecture, phases, methodology, validation cases).
2. `README.md` — public product / release overview.
3. `docs/project-links.md` — verified external links and current handoff status.

---

## Operating principles (apply to every change)

### 1. Think before coding

State assumptions before acting. If the request has multiple plausible readings, missing inputs, or conflicts with the verified facts below, ask one short question — don't guess. Pick a default only when the user has explicitly said "just decide".

For non-trivial work, write out the plan in 2–4 lines first: *what files, what behavior, how I'll know it works*. Then code.

### 2. Simplicity first

Build only what was asked.

- No speculative abstractions, no helpers for one-shot logic, no error handling for cases that can't happen.
- Don't add fallbacks, feature flags, or backwards-compat shims unless the task names them.
- If 200 lines could be 50, rewrite. Three similar lines beat a premature abstraction.
- Default to no comments. Only add one when the *why* is non-obvious (hidden constraint, workaround, surprising invariant).

### 3. Surgical changes

Every changed line must trace to the user's request.

- Don't refactor code you weren't asked to refactor.
- Don't reformat adjacent blocks, rename "while you're there", or rewrite imports/style on the side.
- If you spot something worth fixing out-of-scope, mention it at the end of your response — don't do it.
- Bug fixes don't need surrounding cleanup; one-shot scripts don't need helpers.

### 4. Goal-driven execution

Convert the task into a verifiable success criterion, then loop until it passes. State the criterion up front so the user can correct it.

Truth signals for this repo:

- Backend logic / engine: `python -m pytest backend/tests -q`
- Frontend type/build: `cd frontend && npm run build`
- Desktop packaging: `npm run build` then `npm run smoke:desktop`
- Methodology changes: the three CatCost validation cases (2 wt% Pt/C, 21 wt% Ni/Al₂O₃, USY-FCC) within ±20% — see `AGENTS.md` §7.

If a UI/desktop change can't be verified by a command, say so explicitly — don't claim success from a clean type-check alone.

### Scope of these principles

Bias toward caution on anything touching the calculation engine, price feeds, packaging, or release-versioned files. For trivial edits (typo, comment, single-line tweak in obvious context) you may skip the explicit plan step — but the other three principles still hold.

---

## Verified project facts

These are the *only* facts you may state without re-verification. Re-verify (`gh release list -L 1`, file read, etc.) before quoting in responses or commits.

- **Project**: CatTEA
- **Repository**: https://github.com/hyunjin-kor/CatTEA
- **Default branch**: `master`
- **Package version**: defined in `package.json`, `pyproject.toml`, `frontend/package.json` — read those files directly instead of quoting from this doc (snapshots go stale across releases)
  - Installer name pattern: `CatTEA.Setup.<version>.exe`
  - Portable archive: `CatTEA-win-unpacked.zip`
- **Public blog / homepage**: not configured in GitHub repo metadata
- **License**: source-available, all rights reserved (see `LICENSE`)

The package version is *not* automatically a published GitHub release. Before quoting "the latest release", run `gh release list -L 1` and compare. If `package.json` is ahead of the latest release tag, that's a prepared bump — say "package version vA.B.C, latest release vX.Y.Z" rather than conflating the two.

---

## Working rules

- **Don't invent.** No fabricated source links, blog URLs, benchmark values, prices, citations, or release status. If unknown, say so or check.
- **Don't commit secrets.** `.env.example` holds key names only; never real values.
- **Treat `CatCost_v1-1-1/` as proprietary.** Don't redistribute its raw data. Re-source materials from public references (ICIS public, Sigma-Aldrich, USGS).
- **CatTEA is independent.** Cite CatCost methodology academically; never claim CatCost ownership or NREL endorsement.
- **Co-update versioned references.** When a release ships, update `docs/project-links.md`, `README.md`, `package.json`, and `pyproject.toml` together — never one alone. Verify asset names from the GitHub Releases API.
- **Stay inside the locked stack** in `AGENTS.md` §2. Don't introduce a new framework, ORM, or build tool without asking.

---

## Local commands

```bash
npm install
npm run dev                       # frontend dev server
npm run build                     # full build (frontend + electron)
npm run smoke:desktop             # packaged-app smoke test
python -m pytest backend/tests -q # backend unit + validation tests
cd frontend && npm run build      # frontend-only build / type-check
```

---

## Important paths

- `backend/` — FastAPI app, calculation engine (`core/`), API routers, data libraries, tests
- `frontend/` — React 19 + TypeScript + Vite renderer
- `electron/` — desktop shell and FastAPI sidecar launcher
- `docs/` — project documentation (`project-links.md` is the source of truth for external URLs)
- `.github/workflows/` — CI and release pipelines
- `scripts/` — build, smoke, capture, validation helpers

---

## Migration notes

- This file plus `AGENTS.md` is the full Claude context seed. Don't rely on chat history.
- If a public blog, website, DOI, or hosted docs site is later created, update `docs/project-links.md`, `README.md`, `package.json`, and `pyproject.toml` in one change.
- If a new release is published, update every versioned reference together and confirm asset names against the GitHub Releases API before quoting them.
