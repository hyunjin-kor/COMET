# Release preparation — v1.4.0

Prepared on 2026-09-06; evidence updated on 2026-09-07. This checklist does not publish a release. Current command outputs and CI status are in [the commercialization audit](audit/commercialization-run-2026-09-07.md); [the original run](audit/autonomous-run-2026-09-06.md) retains earlier evidence.

**Distribution hold, 2026-09-07:** the [rights register](commercial/rights-register-2026-09-07.md) identifies legacy workbook-origin data. Do not tag/publish the prepared version until exact-file public-distribution approval is recorded. Passing calculation or installer tests does not clear data rights. Commercial service also needs separate commercial-use, code-ownership and dynamic-feed review.

- [x] Set package.json, frontend/package.json, pyproject.toml and backend/main.py APP_VERSION to 1.4.0; synchronise lockfile package headers.
- [x] Update release notes, CITATION.cff, codemeta.json and project links; retain PolyForm Noncommercial 1.0.0.
- [x] Verify final C13 full pytest (856 passed in511.02s), frontend lint/build/i18n, Node30, CatCost reproduction and frozen replay. Local Windows build172.791s/smoke17.651s preserve the user's DB and installed executable; current audit records outputs and PR112 records final-head CI.
- [ ] Human: review and merge the single run PR after CI passes; this execution does not merge it.
- [ ] Human: resolve each bundled data permission/source replacement and pass `python scripts/check_data_rights.py --purpose public_distribution`; review dependency notices and code ownership separately.
- [ ] Human: create and push tag v1.4.0 from the approved release commit.
- [ ] Human: confirm GitHub release assets and updater metadata (installer, portable archive, latest.yml, blockmap); test an upgrade from the prior public release.
- [ ] Human: verify the new Zenodo version archive, license and relationship to concept DOI 10.5281/zenodo.21451931.
- [x] Regenerate the May 2026 manuscript/SI and controlled-study supplement; verify94 main/1217 SI numerical references, six main figures and the retrieved Article guidance. Engineering Au is provisional; no Q1/JIF eligibility claim.
- [ ] Human: confirm authorship, affiliations, funding, final typeset length, cover letter and journal submission requirements.
- [ ] Human: decide deferred data/coverage questions and source URLs that could not be verified.
- [ ] Company: establish code/data commercial rights, approve actual company/customer contracts and operating/privacy/billing terms before hosted activation. Synthetic tests do not establish an SLA or production security clearance.

Never copy the proprietary CatCost workbook into release assets. Version 1.4.0 remains prepared source until the tag and release actually exist.
