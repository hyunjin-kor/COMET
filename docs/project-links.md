# Project Links

Last verified: 2026-05-06

This page tracks CatPrice's external connection points. Only verified links are listed as active.

## Active Links

| Area | Link | Status |
| --- | --- | --- |
| GitHub repository | https://github.com/hyunjin-kor/CatPrice | Active public repository |
| Issues | https://github.com/hyunjin-kor/CatPrice/issues | Active |
| Releases index | https://github.com/hyunjin-kor/CatPrice/releases | Active |
| Latest release (per package.json) | https://github.com/hyunjin-kor/CatPrice/releases/tag/v1.3.5 | Re-verify with `gh release list -L 1` before quoting |
| Source repository clone URL | https://github.com/hyunjin-kor/CatPrice.git | Active |

## Not Yet Connected

| Area | Current status | Required next step |
| --- | --- | --- |
| Blog | No verified blog URL is present in repository files or GitHub repository metadata. | Add the exact blog URL after publication. |
| Public website / homepage | GitHub repository `homepage` metadata is currently empty. | Set the homepage in GitHub and mirror it in `README.md`, `package.json`, and `pyproject.toml`. |
| Hosted documentation site | No `mkdocs.yml` or hosted docs URL is present. | Add `mkdocs.yml` and publish docs only after the target URL is known. |
| Zenodo DOI | Planned in project notes, but no verified DOI is present. | Add the DOI only after Zenodo registration. |

## Release Metadata

Single source of truth: `package.json`, `pyproject.toml`, `frontend/package.json` must agree.

- Current package version: `1.3.5`
- Python package version: `1.3.5`
- Frontend package version: `1.3.5`
- Latest verified GitHub release: `v1.3.5` (published 2026-05-08, verified via `gh release view v1.3.5` on 2026-05-08)
- Asset name pattern: `CatPrice.Setup.<version>.exe` (installer), `CatPrice-win-unpacked.zip` (portable)

The published GitHub release tag may lag behind the package version when a bump has not yet been tagged. To re-verify, run `gh release list -L 1` against the repo.

## Claude Handoff

Use `CLAUDE.md` at the repository root as the first file for Claude or Claude Code. It points to the project rules, verified links, commands, and migration notes needed to continue development without relying on chat history.
