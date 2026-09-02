# Project Links

Last verified: 2026-09-02

This page tracks COMET's external connection points. Only verified links are listed as active.

## Active Links

| Area | Link | Status |
| --- | --- | --- |
| GitHub repository | https://github.com/hyunjin-kor/COMET | Active public repository |
| Issues | https://github.com/hyunjin-kor/COMET/issues | Active |
| Releases index | https://github.com/hyunjin-kor/COMET/releases | Active |
| Latest release | https://github.com/hyunjin-kor/COMET/releases/latest | Redirects to the newest tag; re-verify with `gh release list -L 1` before quoting a specific version |
| Source repository clone URL | https://github.com/hyunjin-kor/COMET.git | Active |
| Repository `homepage` metadata | https://github.com/hyunjin-kor/COMET/releases/latest | Active; corrected on 2026-09-02 from a stale `hyunjin-kor/CatPrice` URL left over from the rename |
| Zenodo DOI (all versions) | https://doi.org/10.5281/zenodo.21451931 | Active; auto-archives each new GitHub release. v1.3.19 (`10.5281/zenodo.22110422`) is the first record archived from a fully renamed tree, so its title, links and `COMET-v1.3.19.zip` archive all read COMET. The nine earlier records for v1.3.10-v1.3.18 predate the rename: their metadata was corrected in place on 2026-08-26 with DOIs unchanged, but each still holds a `CatPrice-<version>.zip` because published files are immutable |

## Not Yet Connected

| Area | Current status | Required next step |
| --- | --- | --- |
| Blog | No verified blog URL is present in repository files or GitHub repository metadata. | Add the exact blog URL after publication. |
| Public product website | No standalone website exists; the repository `homepage` currently points at the latest release. | Publish the site, then set it as the GitHub homepage and mirror it in `README.md`, `package.json`, and `pyproject.toml`. |
| Hosted documentation site | No `mkdocs.yml` or hosted docs URL is present. | Add `mkdocs.yml` and publish docs only after the target URL is known. |

## Release Metadata

Single source of truth: `package.json`, `pyproject.toml`, `frontend/package.json` must agree.

- Current package version: `1.3.24`
- Python package version: `1.3.24`
- Frontend package version: `1.3.24`
- Latest verified GitHub release: `v1.3.24` (published 2026-08-31, verified via `gh release view v1.3.24` on 2026-09-01; every release is archived on Zenodo under concept DOI `10.5281/zenodo.21451931`)
- Asset name pattern: `COMET.Setup.<version>.exe` (installer), `COMET-win-unpacked.zip` (portable), plus `latest.yml` and `COMET.Setup.<version>.exe.blockmap` (auto-update metadata, from v1.3.13 on)

The published GitHub release tag may lag behind the package version when a bump has not yet been tagged. To re-verify, run `gh release list -L 1` against the repo.

## Claude Handoff

Use `CLAUDE.md` at the repository root as the first file for Claude or Claude Code. It points to the project rules, verified links, commands, and migration notes needed to continue development without relying on chat history.
