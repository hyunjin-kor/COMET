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
| C02 | Pending | — | Copyright/company/third-party/data rights matrix and unexecuted commercial terms |
| C03 | Complete locally; fresh CI pending | This task commit | 780 tests; frontend/Ruff/i18n/29 Node cases; Windows build227.964s, isolated smoke17.604s; user DB/log hashes unchanged |
| C04 | Pending | — | Official journal metrics/scope and dated quartile verification or explicit unknown |
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
