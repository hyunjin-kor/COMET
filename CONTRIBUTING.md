# Contributing to CatPrice

Thanks for taking an interest. CatPrice is an independently developed
desktop tool with a locked stack and a small surface area, so the
contribution path is intentionally tight.

## Before you open a PR

1. Read [`AGENTS.md`](./AGENTS.md). It is the master development guide
   (architecture, locked stack, validation cases, coding conventions).
2. Read [`CLAUDE.md`](./CLAUDE.md). It captures the four operating
   principles applied to every change: think before coding, simplicity
   first, surgical changes, goal-driven execution.
3. Check that the change clears the local validation gates:

   ```bash
   # backend
   ruff check .
   python -m pytest backend/tests -q

   # frontend
   cd frontend && npm run build

   # full desktop smoke (only when Electron paths or sidecar change)
   npm run build
   npm run smoke:desktop
   ```

## What we will accept

- Bug fixes that come with a pytest case (or a frontend reproduction
  step) showing the bug.
- Small surface improvements that fit the locked stack in `AGENTS.md`
  §2 — please don't introduce a new framework, ORM, build tool, or
  charting library without filing an issue first.
- Methodology contributions inside `backend/core/` only when the
  three CatCost validation cases (2 wt% Pt/C, 21 wt% Ni/Al₂O₃, USY-FCC)
  still land within the tolerances declared in `AGENTS.md` §7.
- Documentation fixes (typos, broken links, stale screenshots).

## What we will not accept

- "While I was here" reformat / restyle commits unrelated to the
  feature.
- Drive-by dependency bumps that don't fix a security advisory or
  unblock a feature.
- Replacements for Electron, FastAPI, SQLModel, React 19, Vite, or
  Tailwind 4 without prior agreement on an issue.

## Reporting a security issue

Please follow [`SECURITY.md`](./SECURITY.md) — do not open a public
issue for vulnerabilities.

## License

CatPrice is source-available, all rights reserved (`LICENSE`). By
opening a PR you confirm that you authored the change and grant the
maintainer permission to incorporate it under that license.
