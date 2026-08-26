# Project Links

Last verified: 2026-08-26

This page tracks COMET's external connection points. Only verified links are listed as active.

## Active Links

| Area | Link | Status |
| --- | --- | --- |
| GitHub repository | https://github.com/hyunjin-kor/COMET | Active public repository |
| Issues | https://github.com/hyunjin-kor/COMET/issues | Active |
| Releases index | https://github.com/hyunjin-kor/COMET/releases | Active |
| Latest release | https://github.com/hyunjin-kor/COMET/releases/latest | Redirects to the newest tag; re-verify with `gh release list -L 1` before quoting a specific version |
| Source repository clone URL | https://github.com/hyunjin-kor/COMET.git | Active |
| Zenodo DOI (all versions) | https://doi.org/10.5281/zenodo.21451931 | Active; auto-archives each new GitHub release. The nine records for v1.3.10-v1.3.18 predate the COMET rename and were retitled on Zenodo on 2026-08-26 with their DOIs unchanged; the archived zip inside each one is still named `CatPrice-<version>.zip` because published files are immutable |

## Not Yet Connected

| Area | Current status | Required next step |
| --- | --- | --- |
| Blog | No verified blog URL is present in repository files or GitHub repository metadata. | Add the exact blog URL after publication. |
| Public website / homepage | GitHub repository `homepage` metadata is currently empty. | Set the homepage in GitHub and mirror it in `README.md`, `package.json`, and `pyproject.toml`. |
| Hosted documentation site | No `mkdocs.yml` or hosted docs URL is present. | Add `mkdocs.yml` and publish docs only after the target URL is known. |

## Release Metadata

Single source of truth: `package.json`, `pyproject.toml`, `frontend/package.json` must agree.

- Current package version: `1.3.18`
- Python package version: `1.3.18`
- Frontend package version: `1.3.18`
- Latest verified GitHub release: `v1.3.18` (published 2026-07-21, verified via `gh release list -L 1` on 2026-08-26; every release is archived on Zenodo under concept DOI `10.5281/zenodo.21451931`)
- Asset name pattern: `COMET.Setup.<version>.exe` (installer), `COMET-win-unpacked.zip` (portable), plus `latest.yml` and `COMET.Setup.<version>.exe.blockmap` (auto-update metadata, from v1.3.13 on)

The published GitHub release tag may lag behind the package version when a bump has not yet been tagged. To re-verify, run `gh release list -L 1` against the repo.

## Claude Handoff

Use `CLAUDE.md` at the repository root as the first file for Claude or Claude Code. It points to the project rules, verified links, commands, and migration notes needed to continue development without relying on chat history.
