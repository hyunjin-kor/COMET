# Project Links

Repository/release metadata checked: 2026-09-07. Other checks retain their stated evidence dates.

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
| Zenodo DOI (all versions) | https://doi.org/10.5281/zenodo.21451931 | Existing concept DOI, resolver/DataCite checked on 2026-09-06 as recorded below. No new deposit or future archive success is asserted. |

## Not Yet Connected

| Area | Current status | Required next step |
| --- | --- | --- |
| Blog | No verified blog URL is present in repository files or GitHub repository metadata. | Add the exact blog URL after publication. |
| Public product website | No standalone website exists; the repository `homepage` currently points at the latest release. | Publish the site, then set it as the GitHub homepage and mirror it in `README.md`, `package.json`, and `pyproject.toml`. |
| Hosted documentation site | No `mkdocs.yml` or hosted docs URL is present. | Add `mkdocs.yml` and publish docs only after the target URL is known. |

## Release Metadata

Version declarations in `package.json`, `pyproject.toml`, `frontend/package.json` and `backend/main.py` must agree; `test_version_sync.py` checks them.

- Current prepared package version: `1.4.0`
- Python package version: `1.4.0`
- Frontend and backend APP_VERSION: `1.4.0`
- Latest verified GitHub release: `v1.3.24` (published 2026-08-31T18:24:09Z; verified with `gh release list -L 1` on 2026-09-07). Version 1.4.0 has no release or tag from this run.
- Concept DOI `10.5281/zenodo.21451931`: DOI resolver, Zenodo and DataCite verified on 2026-09-06; resolves to the existing v1.3.24 record. Crossref 404 reflects DataCite registration, not a broken identifier. [Evidence](sources/t06-external-checks-2026-09-06.json).
- Citation metadata: root `CITATION.cff` and `codemeta.json` describe prepared source version 1.4.0; no release date is asserted.
- Asset name pattern: `COMET.Setup.<version>.exe` (installer), `COMET-win-unpacked.zip` (portable), plus `latest.yml` and `COMET.Setup.<version>.exe.blockmap` (auto-update metadata, from v1.3.13 on)

The published GitHub release tag may lag behind the package version when a bump has not yet been tagged. To re-verify, run `gh release list -L 1` against the repo.

## Claude Handoff

Use `CLAUDE.md` at the repository root as the first file for Claude or Claude Code. It points to the project rules, verified links, commands, and migration notes needed to continue development without relying on chat history.

## Submission evidence

The current [manuscript](paper/manuscript_2026-09-07.md), [SI](paper/si_2026-09-07.md), and [results](paper/submission-2026-09-07/results_2026-09-07.md) share the frozen May 2026 reference basis, with a separate [controlled experiment](paper/controlled-2026-09-07/README.md). [Source and format checks](paper/submission-format-2026-09-07.md) record the retrieved ACS guidance and existing DOI evidence; they do not establish Q1 eligibility, acceptance or the planned v1.4.0 release.

## Project and company preparation

- [Project portfolio and contribution evidence](project-portfolio.ko.md)
- [Current three-objective audit](audit/commercialization-run-2026-09-07.md)
- [Company licensing and subscription plan](commercial/strategy.ko.md)
- [Data rights register and distribution hold](commercial/rights-register-2026-09-07.md)
- [Hosted operation, account management and recovery](commercial/hosted-operations.ko.md)

No verified public subscription endpoint or executed company contract exists in these records. GitHub repository metadata remains the existing local-desktop description and release homepage; it was read, not remotely changed in this preparation.
