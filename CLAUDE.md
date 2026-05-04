# CatPrice Claude Handoff

This file is the entry point for working on CatPrice in Claude or Claude Code.

## Read First

1. `AGENTS.md` is the master development guide and contains the project rules, architecture, phases, and methodology notes.
2. `README.md` is the public-facing product and release overview.
3. `docs/project-links.md` tracks verified external links and current handoff status.

## Current Verified Project Facts

- Project: CatPrice
- Repository: https://github.com/hyunjin-kor/CatPrice
- Default branch: `master`
- Latest verified GitHub release: `v1.1.13`
- Latest verified installer asset: `CatPrice.Setup.1.1.13.exe`
- Latest verified portable asset: `CatPrice-win-unpacked.zip`
- Public blog / homepage URL: not configured in GitHub repository metadata as of 2026-04-26
- License: source-available, all rights reserved; see `LICENSE`

## Working Rules

- Do not invent source links, blog URLs, benchmark values, prices, or external status.
- Do not commit secrets or API keys. Use `.env.example` only for key names.
- Keep new files purposeful and structured.
- Treat `CatCost_v1-1-1/` as proprietary source material; do not redistribute its raw data.
- Preserve CatPrice as an independent implementation that cites published methodology without claiming CatCost ownership.

## Local Commands

```bash
npm install
npm run dev
npm run build
npm run smoke:desktop
python -m pytest backend/tests -q
cd frontend && npm run build
```

## Important Paths

- `backend/` - FastAPI app, calculation engine, API routes, data libraries, tests
- `frontend/` - React/Vite renderer for the desktop UI
- `electron/` - Electron desktop shell and backend sidecar launcher
- `docs/` - project documentation
- `.github/workflows/` - CI and desktop release workflows
- `scripts/` - build, smoke, capture, and validation helpers

## Migration Notes

- Use this file plus `AGENTS.md` as the Claude context seed.
- If a public blog, website, DOI, or documentation site is later created, update `docs/project-links.md`, `README.md`, `package.json`, and `pyproject.toml` together.
- If a new release is published, update every versioned release reference together and verify the asset names from the GitHub Releases API.
