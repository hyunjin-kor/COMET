# COMET research, public portfolio and subscription preparation

Started 2026-09-07 on `autonomous/2026-09-06`, baseline `c513e1ccaf37b7a61f6d3d31a0491627e654bc5c`, existing [PR112](https://github.com/hyunjin-kor/COMET/pull/112). This is an ongoing preparation log, not a claim of journal acceptance, legal authorization, production readiness or sales.

## User objectives and decisions

1. One research paper targeting Q1 and a Journal Impact Factor from 8 to the mid-teens. Verify the metric year and JCR category; CiteScore/SJR quartiles are not substitutes. Prior ACS SC&E targeting may change under this newer instruction.
2. A usable public GitHub project that accurately records the user's research/software contribution. Do not invent sole authorship, institutional ownership or contributor consent.
3. Subscription commercialization through the professor's company. Keep the existing PolyForm Noncommercial license and prepare separate commercial rights and service terms. Copyright ownership, company identity, institutional technology-transfer rules and third-party data permissions remain unconfirmed.

The six improvements accepted from the preceding review are all tracked: independent cost validation, representative scientific analyses, hosted identity/private data/limits, reliable release/install, data reuse rights, and external researcher evaluation. Data acquisition stays free. Human participation and observations will never be simulated and reported as real.

## Baseline evidence

No source changed for this initial log. Reused evidence is explicitly distinguished from new executions: [scientific checks](scientific-checks-2026-09-07.json), [notation audit](scientific-notation-2026-09-07.md), and [CI34096387831](https://github.com/hyunjin-kor/COMET/actions/runs/34096387831) at the unchanged baseline. Local pytest: 780 passed/444.01s; CI: 780 passed/620.21s, two dependency deprecation warnings; frontend checks passed. Windows build198.068s, smoke17.604s; installed package hash matched. Table6.2: Pt/C27.37, Ni19.2206 (−6.65%), FCC footnote-b2.4380 (+1.16%) USD/lb. Matched independent full-cost observations remain0; empirical MAPE is unestimated.

## Work register

| ID | Status | Commit | Evidence / acceptance |
|---|---|---|---|
| C01 | Complete | c7f51f1 | Goal and persisted C01–C14 backlog; clean tested baseline |
| C02 | Preparation complete; rights approval unresolved | c2a17d1 | 81-file rights inventory,20 workbook-origin declarations,12 guard tests,792 full tests; actual public/commercial checks correctly reject unapproved data; contract drafts |
| C03 | Complete; all CI jobs passed | a5279bd | Local780 tests; CI780/498.13s plus Windows/frontend; build227.964s, isolated smoke17.604s; user DB/log hashes unchanged |
| C04 | Evidence review complete; target eligibility pending | This task commit | Official indexed JIF displays and HTTP200 Engineering Au Article guidance; metric year/JCR category/Q1 unverified, no acceptance claim |
| C05 | Pending | — | Controlled, reproducible scientific case studies |
| C06 | Pending | — | Free independent validation evidence; no inferred missing conditions |
| C07 | Pending | — | External researcher evaluation protocol; real participation remains distinct |
| C08 | Pending | — | Opt-in hosted identity and private resource isolation |
| C09 | Pending | — | Subscription active/expired/revoked lifecycle and access tests |
| C10 | Pending | — | Account UI, limits, backup/restore and operating procedures |
| C11 | Pending | — | Claims/results/version aligned in publication package |
| C12 | Pending | — | Public portfolio and evidence-based contribution documentation |
| C13 | Pending | — | Integrated truth signals, real UI, package and final CI |
| C14 | External facts required | — | Rights/company/author approvals, independent observations/participants, JCR category, billing/hosting/launch choices |

## Boundaries

No existing LICENSE change, paid source, new framework/ORM/build tool, destructive DB change, generated credentials, live billing, third-party message, contract execution, tag, merge, release, external hosting, deposit or journal submission is authorized by this preparation. New legal documents will be drafts with unresolved fields, not representations that the user or company has already acquired rights. Existing noncommercial desktop use remains available. A subscription entitlement is an access-control mechanism, not proof of copyright ownership or data reuse permission.

## Next action

Continue C02 rights review and C04 journal evidence, then the controlled scientific and hosted-service work. No release can be described as commercially cleared before C02 resolves the actual data-origin findings.

## C03 implementation and verification

The frontend development script now runs npm in the frontend directory through `--prefix`; its previous `cross-env ... cd frontend` command treated the shell builtin as an executable and risked the wrong working directory. The corrected command was actually started and returned HTTP200 with the Vite client on5173; its owned process tree was stopped. See [development output](commercial-c03-dev-2026-09-07.log).

README now installs both npm dependency sets and a Python virtual environment, uses an explicit Python for packaging, documents the actual installer name, and recommends Node24 LTS. Windows instructions use npm.cmd and an environment PATH without requiring activation-script policy changes. CI uses Node24 and adds an unpublished Windows package/smoke job. The tag-triggered release workflow adds full backend tests, Table6.2, i18n/Node rules and packaged smoke before release creation. No tag or release was triggered.

`COMET_PROFILE_DIR` is an optional absolute-path Electron profile override. Smoke uses a fresh random temporary directory, checks its DB creation, checks exactly one main window after relaunch, and restores the caller's environment. Both the original user DB and launcher log have identical SHA-256 before/after smoke: [isolation evidence](commercial-c03-profile-isolation-2026-09-07.json). The existing installed desktop was not replaced. A SQLite online backup passed quick_check before packaging. Recursive build cleanup now validates paths inside the build directory, rejects redirected roots/targets, and uses native PowerShell deletion only for build products.

| New execution | Result |
|---|---|
| Full pytest | 780 passed; wrapper544.959s (concurrent packaging); [output](commercial-c03-pytest-2026-09-07.log) |
| Ruff, frontend lint/build/i18n, Node rules and Table6.2 | All passed; aggregate14.794s; [output](commercial-c03-checks-corrected-2026-09-07.log) |
| npm run build | Passed227.964s; [output](commercial-c03-desktop-build-2026-09-07.log) |
| npm run smoke:desktop | Passed17.604s; prices/calculate HTTP200,1 main window, separate DB; [output](commercial-c03-desktop-smoke-2026-09-07.log) |
| PowerShell parser / git diff | Both changed scripts parsed; whitespace check required at commit |

No calculation formula or data changed. Table6.2 retains Pt/C27.3695, Ni19.2206(−6.65%), FCC at footnote-b rate2.4380(+1.16%) USD/lb. These timing measurements do not establish a performance improvement.

Critic: the first aggregate runner returned exit0 even though the child Windows PowerShell blocked npm.ps1. That run is **not frontend pass evidence**; its [failed harness output](commercial-c03-checks-2026-09-07.log) is retained. The corrected runner uses terminating errors and npm.cmd and actually executed all checks. Tailwind still emits the previously observed sourcemap warning; packaging has optional-hook warnings. Neither was suppressed. Fresh Windows GitHub CI remains to be verified after push.

Follow-up: [CI34122880587](https://github.com/hyunjin-kor/COMET/actions/runs/34122880587) at a5279bd passed the new fresh Windows build/smoke job and frontend job. The Windows job installed from scratch and completed in about4min; its smoke phase passed in16s. Backend was still running at that observation, so no whole-run success is asserted here.

Final C03 CI observation: the same run subsequently completed **success**, including780 backend tests in498.13s with two upstream dependency deprecation warnings. All three jobs passed.

## C02 rights and distribution control

The [rights register](../commercial/rights-register-2026-09-07.md) distinguishes the code license, actual copyright ownership, contributor permission, static data and dynamic feeds. Added a Korean commercialization strategy and unexecuted company-license/subscription drafts with unknown party, fee, SLA and ownership fields. No permissions or customer contracts have been created.

The exact-file inventory covers81 bundled files recursively,20 with declared CatCost/workbook-sheet origins. Material/equipment counts606/241 are metadata counts, not a new data import. The previous README denial of CatCost source-data redistribution was corrected. All current data remain preserved and unapproved for the newly proposed distribution review.49 installed Python runtime packages and580 npm lock entries were inventoried from local metadata; this is not a full binary license audit.

The new public-release gate rejects missing/modified/unreviewed data, absent review records and malformed manifests. Public distribution permission does not imply commercial permission. The gate is deliberately placed before tag release packaging/publication; it does not block local calculation/testing. Both checks on the real manifest returned exit1 as expected: [public](commercial-c02-public-gate-2026-09-07.log), [commercial](commercial-c02-commercial-gate-2026-09-07.log). They are **not** commercial-readiness passes. No tag-triggered workflow was executed.

Verification:12 focused tests passed, including separate-use permissions, file mutation/new nested files, review metadata and malformed/duplicate manifests. Initial test collection correctly failed because the protection module did not exist; [before](commercial-c03-rights-before-2026-09-07.log) and [after](commercial-c03-rights-after-2026-09-07.log) retain the runner's earlier C03 filename prefix. Full suite **792 passed in467.83s**, wrapper471.319s: [output](commercial-c02-pytest-2026-09-07.log). Ruff passed. Frontend and calculations were unchanged from a5279bd, so its passing frontend/Table6.2/desktop evidence is reused rather than described as newly executed.

Critic: a reachable DOI or permissively licensed downloader does not clear its data. IMF terms require attention to commercial permission; UN Comtrade's free research exceptions do not automatically apply to a for-profit analytics service; yfinance's Apache license does not license Yahoo data. Data acquisition remains free. Existing workbooks, source snapshots, schemas and LICENSE were not changed. The new checker only records and enforces explicit review decisions; it cannot establish legal rights itself. Company/college/contributor authority, dependency notices and data replacements/permissions remain C14 release blockers.

## C04 journal target evidence

[The target review](../paper/journal-targets-2026-09-07.md) supersedes unconditional ACS SC&E targeting under the user's newer JIF minimum8. Official indexed publisher text displays7.6 for ACS SC&E,9.0 for ACS Engineering Au and9.6 on a Sustainable Production and Consumption issue page. Exact metric year/JCR category quartile are not verified. Repeated direct publisher metrics/insights responses403 prevent treating these as fully confirmed current-year eligibility. No SJR, CiteScore or aggregator quartile was substituted.

Engineering Au Article guidance was retrieved HTTP200, updated2026-08-27. Its computational/process scope supports a provisional fit; the Article abstract is typically at most300 words, whereas2200 words is the Letter limit. No fixed Article text/figure cap was found in the inspected section. Existing six figures and frozen manuscript structure remain intact. APC coverage, indexing, authors and journal selection require actual confirmation. No paid access, author contact or submission took place.

Verification for this documentation-only task reuses c2a17d1's792 passing backend tests and a5279bd's unchanged frontend/package evidence. Critic: citing a publisher-displayed number without its year and category is insufficient to say the Q1/JIF objective is met. Eligibility is explicitly deferred to C14; preparation and independent research analysis can continue.
