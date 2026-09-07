# COMET research, public portfolio and subscription preparation

Started 2026-09-07 on `autonomous/2026-09-06`, baseline `c513e1ccaf37b7a61f6d3d31a0491627e654bc5c`, existing [PR112](https://github.com/hyunjin-kor/COMET/pull/112). This is an ongoing preparation log, not a claim of journal acceptance, legal authorization, production readiness or sales.

Closing verification continued into2026-09-08 KST. Artifact names retain the run's start date; command records contain their actual UTC timestamps.

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
| C04 | Evidence review complete; target eligibility pending | 248c45e | Official indexed JIF displays and HTTP200 Engineering Au Article guidance; metric year/JCR category/Q1 unverified, no acceptance claim |
| C05 | Complete | 26a283e | 30 crossed price/evidence families,21 manufacturing scenarios,9 electrode scenarios; byte-identical replay;802 full tests passed |
| C06 | Evidence extension complete; real observations unresolved | f95ac74 | 2 additional Crossref-verified papers, actual HTTP/PDF checks and private collection worksheet; matched observations remain0 |
| C07 | Protocol complete; participants unresolved | b84e343 | 6 defined tasks, recording/analysis criteria, empty CSV, actual participants0 |
| C08 | Foundation complete | de54164 | 27 account/auth/storage tests;829 full tests460.46s; frontend lint/build/i18n and Table6.2 passed; startup remains rights-gated |
| C09 | Complete | d92c681 | Subscription periods/seats/audit/operator commands;843 full tests475.34s; no actual billing or accounts |
| C10 | Complete | 2c08f1f | Actual browser thermal/electrode/account/expiry QA;853 full tests511.11s; frontend lint/build/i18n, storage test, limits and new-directory recovery |
| C11 | Preparation complete | 9a566d6 | Controlled scientific claims,94 manuscript/1217 SI JSON-key references,13 focused tests;856 full tests504.21s |
| C12 | Complete | d972f18 | Concise public entry points, evidence-linked portfolio, accurate prepared/released and commercial status;54 local links checked |
| C13 | Local validation complete; final-head CI recorded in PR | final audit commit | 856 full tests/511.02s after portable path fix; Windows build172.791s/smoke17.651s; final replay26.009s |
| C14 | External facts required | — | Rights/company/author approvals, independent observations/participants, JCR category, billing/hosting/launch choices |

## Boundaries

No existing LICENSE change, paid source, new framework/ORM/build tool, destructive DB change, generated credentials, live billing, third-party message, contract execution, tag, merge, release, external hosting, deposit or journal submission is authorized by this preparation. New legal documents will be drafts with unresolved fields, not representations that the user or company has already acquired rights. Existing noncommercial desktop use remains available. A subscription entitlement is an access-control mechanism, not proof of copyright ownership or data reuse permission.

## Next action

Local preparation is verified. Final documentation-head CI is checked after push and recorded in PR112; C14 external facts remain open. No release is commercially cleared by these tests.

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

Follow-up: [CI34124287686](https://github.com/hyunjin-kor/COMET/actions/runs/34124287686) at248c45e completed success, including the Windows, frontend and backend jobs.

## C05 controlled scientific scenarios

Added [the deterministic analysis](../../scripts/run_controlled_cases.py) and [results, figure and interpretation](../paper/controlled-2026-09-07/README.md). An in-memory library reads the existing frozen reference/live bases; no network, price-library change or application DB is used. Provenance records input/code hashes and actual Python/package versions. Overrides to an unrecorded data directory are rejected. The seed is recorded, but conditions are enumerated without random sampling.

All30 reaction families cross numeric price state and source-confidence annotations independently. Reference-price/live-evidence winners differ in4 families; live-price/reference-evidence differs in1; both change5. Thus the combined count cannot all be attributed to market movement. The score decomposition reproduces endpoint changes; source evidence and route/performance remain author-assigned rubrics. Same-basis corners reproduce native rankings, retaining the production tie rule.

Three manufacturing routes are swept over7 quantities including the5/70 short-ton scale boundaries (21 cases), with fixed finished composition/material cost. The 4.99→5 short-ton incipient-wetness selling-price change13.0874→7.2813 USD/lb is a discrete model-class effect, not an observed factory discount. Nine electrode scenarios vary loading and a hypothetical powder-price multiplier. Catalog material-stack prices are area normalized; no industrial procurement, equal lifetime/activity or complete assembly claim is made.

The two final executions took2.208/2.357s and produced identical JSON/PNG/SVG/provenance bytes: [comparison](commercial-c05-replay-comparison-2026-09-07.json). Numerical SHA-256:`495b0fe9c5a60476bb29143082d745575976339aab5db4a3aca9c4c9fbd902ee`. Thirteen README numeric references resolve to actual JSON keys. The figure was rendered and visually inspected. Earlier analysis logs retain superseded hashes from incremental development; the `analysis-verified`/`replay-verified` logs and current comparison are final evidence.

Ten focused tests pass, including counterfactual attribution, incompatible candidates/compositions/units/routes, native electrode consistency, fixed-material scale sweep and rejected data override. Ruff passes. The first full run collected9 of those tests and passed801 in401.99s; a final full run was started after adding the provenance guard/test. Frontend/package behavior is unchanged from the passing CI above. Table6.2 was executed again and remains Pt27.3695, Ni19.2206(−6.65%), FCC footnote-b2.4380(+1.16%) USD/lb: [output](commercial-c05-table62-2026-09-07.log).

Critic: controlled scenarios are not new empirical validation. Input states have different observation dates and support-price bases. Material LCA coverage is not a complete process inventory; price scaling of catalog electrode materials does not establish an optimal design. Rights approvals and matched independent observations remain unresolved.

Final verification: **802 passed in397.81s**, wrapper401.044s: [output](commercial-c05-pytest-final-2026-09-07.log). No analysis or backend code changed during this final run. An initial shell attempt used a nonexistent worktree `.venv` path and did not start tests; the corrected run used the existing `python` runtime, also recorded in provenance. This shell invocation error was not an engine/test failure.

C05 whitespace review reported Matplotlib-generated SVG path-line trailing spaces and raw command-output blank lines at EOF. These generated artifacts were retained byte-for-byte to preserve replay hashes; this is not a clean whitespace-check claim. Source lint and802 tests passed before the commit; no hook or verification was bypassed.

## C06 free independent evidence extension

Screened two additional primary papers and verified both DOIs/titles against actual Crossref HTTP200 responses. [The extension](../sources/independent-evidence-extension-2026-09-07.md) distinguishes an independent laboratory ABC/TCO cost model from a separate CatCost-based TEA. A DOE author copy was retrieved HTTP200 and read. Both direct publisher pages returned403; the RSC SI URL redirected to an HTML challenge despite200. No successful SI retrieval is claimed.

Crossref's article license metadata and third-party input rights are separated. Full articles remain local; no new model price/data or commercial permissions were added. The bounded inventory now screens12 cases across the prior ten and these two, while matched independent full-cost observations remain0 and empirical MAPE remains unestimated. Prepared a blank private record collection worksheet matching the application's existing observation schema. No records, contacts, purchases or participant data were invented.

Validation: inspected the actual Crossref metadata, PDF text, URL final destinations/content types and file hashes in the access JSON. These documentation-only changes reuse26a283e's802 passing tests and unchanged frontend/package CI. Critic: laboratory economic modeling and published-method repetition are valuable context but insufficient evidence of industrial predictive accuracy. Acquiring a voluntarily shared, condition-matched production/procurement record remains C14.

## C07 actual researcher evaluation protocol

Added a Korean protocol with six application tasks, proposed recruitment mix, controlled version/price inputs, task ordering, assistance/time/error/comprehension recording and prespecified reporting distinctions. The initial target6 researchers is a proposed qualitative round, not a power calculation or completed sample. Consent, voluntary participation, institutional procedures and private storage must be established by the actual study team. No recruitment or message was sent.

The GOV.UK moderated-usability guide was read and its direct URL returnedHTTP200/text/html on2026-09-07. COMET task definitions and release criteria are our proposed rubric, not a certified psychometric instrument. The CSV parses and contains0 observation rows. Automatic browser QA and developer rehearsal are explicitly excluded from participant results.

Validation: inspected the protocol against current thermal/electrode/save/compare/evidence flows; preserved blank observations and reused26a283e's802 tests for unchanged software. Critic: real researcher usability evidence remains absent. The protocol prepares a study; it does not satisfy the empirical user-evaluation claim or establish customer demand. Actual participants and permissions remain C14.

Follow-up: [CI34127421166](https://github.com/hyunjin-kor/COMET/actions/runs/34127421166) atb84e343 completed success for backend, frontend and fresh Windows package/smoke.

## C08 hosted identity and private data foundation

Added opt-in hosted authentication and a [documented account boundary](../commercial/hosted-architecture.ko.md). The conservative assumption is stricter than company-wide sharing: each account gets its own SQLite data file, even inside one company. Company membership is retained for the upcoming subscription entitlement. Public code/desktop behavior remains login-free by default; existing desktop tables receive no owner columns or automatic data transfer. Hosted control tables are excluded from desktop schema creation.

An application-wide API dependency authenticates requests, and the existing session dependency selects storage using only the server-resolved account UUID. A missing private DB returns503 without creating it or falling back to desktop storage. Saved estimates, bulk comparison, observations, exports and custom material/equipment paths use that same private session. Auth responses expose only the account's own public fields.

Passwords use stdlib scrypt N=2^17/r8/p1 with random salt; sessions use random256-bit identifiers with hashed server storage and a12-hour absolute lifetime. HTTPS cookies use __Host/Secure/HttpOnly/SameSite=Strict. Login rotates the existing browser session; logout and disabled accounts invalidate access. Origin plus a custom AJAX header protects mutations and login, backed by the inspected OWASP API pattern. Database login counters enforce account/client/global limits, with two password verifications per process at once. Request bodies are capped at2MiB before parsing, including chunked requests. Authentication validation errors do not echo invalid password inputs.

Commercial hosted startup checks the existing data-rights manifest and deliberately fails on the current unapproved data. Network feed startup/refresh is disabled in hosted mode. Tests use disposable storage and explicit test-only review injection; no real reviewer entry, customer account, password or external credential was created. The configuration allows HTTP only through an explicit loopback-test option and restricts matching clients; production requires a configured HTTPS origin and host, debug off.

Related finding fixed within the hosted-read boundary: calculator/material template IDs previously reached filesystem paths without a character/path-boundary check, including Windows backslash forms. Both entry points now reject them and resolved files must stay inside the template directory. Valid catalog IDs and numerical formulas are unchanged.

Verification:27 targeted tests pass, including same-company material isolation, different-company estimate/equipment/list/detail/update/delete/export/observations/bulk comparison rejection, expiration/disable/logout/rotation, missing DB, desktop schema preservation, password hashes, CSRF, login throttling, chunked body size and template traversal. The first expected collection failure preceded the new module; the focused logs retain the runner's earlier `commercial-c05-hosted-*` prefix. Full suite is running on the final code. Ruff passes. Fresh frontend lint3.425s/build3.522s/i18n0.812s passed with0 missing keys/untranslated labels. [Table6.2](commercial-c08-table62-2026-09-07.log) retains Pt27.3695, Ni19.2206(−6.65%), FCC footnote-b2.4380(+1.16%) USD/lb.

Critic: two aggregate frontend harness attempts failed from nested PowerShell quoting and local script execution policy. Their logs are retained and are not pass evidence; direct `npm.cmd` calls then executed each check successfully without changing policy. UI is unchanged in this foundation commit; actual hosted account screens and browser validation follow in C10. Subscription status/seat controls, operating limits, backups and operator commands remain C09/C10. This is not an internet deployment or a production security certification; host ACL/TLS/proxy configuration and real rights remain external requirements.

Final C08 verification: **829 passed in460.46s**, wrapper463.727s: [full output](commercial-c08-pytest-2026-09-07.log). Code was held unchanged during the full run. Source/document whitespace checks pass; raw focused logs preserve their command-output trailing blank lines. This increase in total test runtime includes the added password-hashing/isolation tests and is not a measured application latency regression or improvement.

Follow-up: [CI34129271727](https://github.com/hyunjin-kor/COMET/actions/runs/34129271727) at de54164 completed success for all three jobs.

## C09 subscription periods, seats and operator actions

Added company pending/active/revoked records with explicit periods and derived expiry. New organizations and legacy C08 organizations default to pending; additive columns preserve existing records without inventing contracts. Active access begins at the stated start and ends before the stated end. Ordinary expiry/revocation permits saved reads and exports, while new computations and data changes require active access. Security account disable remains a separate action that revokes all sessions.

Seat availability is enforced with an immediate SQLite transaction on creation and reactivation. Decreasing seats below enabled accounts is rejected; no arbitrary user is disabled. Renewal takes effect for existing authenticated sessions. Browser-provided contract/company fields are rejected. No billing event is inferred and no real contract, customer identity or password was provisioned.

The [operator CLI](../../scripts/manage_hosted.py) requires a named actor for management actions and hidden, confirmed interactive input for account passwords/resets. No password command-line option or unattended echo fallback exists. Users can change their password after ordinary expiry by providing the current one; change/reset invalidates all existing sessions. Audit records contain identifiers, actions and contract before/after fields without password/token/research payloads. [Operations](../commercial/hosted-operations.ko.md) documents these exact boundaries.

Verification: the expanded focused suite passed40 tests in51.39s (wrapper54.766s), including a concurrent last-seat race, inactive saved access, renewal, actor/date/seat validation, legacy schema preservation and password session invalidation. One further client-self-grant rejection test was added before the full suite. Ruff and operator `--help` pass. Initial collection failed before the new model existed; an intermediate Ruff fixture-import warning was corrected, not suppressed. Focused command logs preserve these stages. Frontend and calculation code remain unchanged from C08; its passing lint/build/i18n and Table6.2 evidence is reused.

Critic: manual entitlement records are neither executed contracts nor verified payment receipts. The audit DB is not an externally immutable ledger, and password provisioning still needs an actual approved private delivery/identity procedure. UI, compute quotas and tested recovery remain C10. Real data rights still block hosted startup. No rights approval or commercial launch is claimed.

Final C09 verification: **843 passed in475.34s**, wrapper478.892s: [output](commercial-c09-pytest-2026-09-07.log). Code and tests were held unchanged during the full run. Ruff passed on all changed Python files. Source/document whitespace is checked separately from retained raw earlier log formatting.

Follow-up: [CI34131166529](https://github.com/hyunjin-kor/COMET/actions/runs/34131166529) at d92c681 completed success for all three jobs.

## C10 account screens, operating limits and recovery

The browser now bootstraps the server mode before mounting research pages. Default desktop remains login-free. Hosted mode adds English/Korean sign-in and a compact account page with subscription/expiry, historical saved-result viewing, JSON download, logout and current-password change. Ordinary inactive subscriptions route new-work pages to an explanation with a saved-work link. Saved calculations use their recorded values without a new computation. The account list displays the latest200 items, while backend search/read and recovery cover all records.

Account changes clear private drafts/results and unmount research state, retaining language/unit/basis preferences. Hosted reload deliberately starts with no unsaved draft. Cross-tab sign-in/logout clears other tabs; returning tabs check session state. The API requires a displayed-account confirmation header matching the server cookie, so an old tab cannot submit its prior user's inputs into the new user's storage. The header never chooses the owner. In-flight responses from an old browser generation are discarded. The two previous direct-fetch consumers for observations/comparison now share the same protected request path. Hosted price refresh reads stored prices and no longer attempts disabled scraper calls.

Work-request budgets use atomic persistent SQLite counters: account60/company240 per minute and uncertainty10/account/minute, with the existing maximum10,000 simulations per request. Fixed-window limitations are documented. Two process-local work slots release on failures and leave saved reads available;429 responses include Retry-After. These are initial single-worker bounds, not measured hosting capacity or billable entitlements.

The [backup tool](../../scripts/backup_hosted.py) copies control and all account databases, verifies hashes/quick_check and requires a stopped-service acknowledgment for backup/recovery. It restores only to a new private directory, rejects malformed/incomplete/changed archives, and revokes recovered login sessions. Active data are not overwritten. [Operations](../commercial/hosted-operations.ko.md) explicitly requires quiescing all writers for cross-DB consistency and reconciling subsequent contract/security changes before manual cutover. OS ACL/encryption, offsite retention and actual disaster-recovery objectives are not claimed.

Verification:46 auth/subscription/operating tests passed59.47s and5 backup tests passed6.76s. They cover stale-account rejection, per-account/company/uncertainty budgets, concurrency cleanup, unchanged source DB hashes, complete restoration, retained private records, revoked historic sessions and corrupt/missing/path-invalid archive rejection. A Node storage-state test passed and is added to CI/release checks. Ruff passes. Final frontend lint has no warnings, build passes and i18n has0 missing/untranslated static labels. The initial account effect warning and a ScientificText prop-name type error were corrected; earlier logs remain failed/intermediate evidence, not final passes.

[Actual browser evidence](commercial-c10-browser-2026-09-07.json) records a disposable loopback service and two synthetic accounts, each with one saved case. Ni/alumina thermal costing and an area-based fuel-cell electrode run completed. The second account's list excluded the first result. Logout in one tab closed the other research view. The expired first account displayed its historical10.41USD/kg result, downloaded an identical saved payload, and could not open new calculation controls. Two downloaded files were compared to the private SQLite result JSON; six screenshots are hashed in the evidence file. Both tabs reported no captured browser errors in the inspected final logs and were closed; the owned QA process was stopped. No real customer or installed-desktop DB was used.

Critic: the browser download-event waiter timed out at3s, but actual files were present and independently matched the saved payloads; the waiter failure was not hidden. Password mutation has backend tests and an inspected browser form, without claiming a browser-submitted credential change. Synthetic far-future contract dates are test fixtures, not real contracts. No external participant, live billing, paid data, internet deployment, OS-access certification or full penetration test occurred. Data rights continue to block actual hosted startup.

Final C10 verification: **853 passed in511.11s**, wrapper514.697s: [output](commercial-c10-pytest-2026-09-07.log). Backend code/tests stayed unchanged during the full run; independent UI/docs were finalized and checked separately. Calculator/range/notation Node rules and Table6.2 were rerun. The cost equations/data remain unchanged: Pt27.3695, Ni19.2206(−6.65%), FCC footnote-b2.4380(+1.16%) USD/lb.

## C11 publication package alignment

C10 follow-up: [CI34133310090](https://github.com/hyunjin-kor/COMET/actions/runs/34133310090) at2c08f1f completed success for backend, frontend and fresh Windows package/smoke.

Updated the generator and regenerated the current manuscript/SI from the preserved primary run and C05 controlled output. The abstract now leads with the controlled balanced-profile result:4 evidence-only,1 numeric-price-only and5 combined winner changes. The text explicitly separates this experiment from historical monthly replay and notes that a performance-weight-removed composite still includes evidence/route rubrics. No numerical result, price input or calculation formula changed.

The route/scale section adds21 fixed-composition cases and the5-short-ton class discontinuity;9 electrode cases preserve area units and mixed catalog boundaries. SI now has one additional controlled figure and seven tables. Added the C06 primary references from the already verified Crossref responses; laboratory ABC/TCO and a CatCost-based TEA remain contextual models, not matched actual manufacturing observations. The bounded screening inventory is12, with eligible industrial full-cost observations still0 and no empirical MAPE.

Data/code availability now discloses existing declared workbook origins and the unresolved distribution review instead of treating original-workbook exclusion as clearance of derived records. AI assistance and the proposed company-interest disclosure remain distinct from actual authorship, executed licenses or revenue. The prepared1.4.0 tag remains unpublished; a fresh release query still returnedv1.3.24, published2026-08-31. Added an author-readiness checklist, unsent cover letter and ten anticipated reviewer questions without fictitious approvals or participant findings.

The provisional format follows the actually retrieved Engineering Au Article guidance. Removed the old SC&E7000-word-equivalent rule from the new journal's checks; Article text/figure cap is null where not verified, and the2200-word Letters rule is not used. Current abstract182 lexical words/body2565, six main figures/two main tables, one SI figure/seven SI tables. Actual JIF year/category/Q1/indexing and publication-cost coverage remain external verification.

Validation: generator `--check` passes94 manuscript and1217 SI JSON-key references and verifies27 unchanged primary outputs. Controlled numerical bytes, seed and both selected price snapshots are checked before document generation.13 focused tests passed (three new provenance/claims guards plus ten controlled-study tests); Ruff passes. Cross-platform byte preservation was added for the controlled JSON/SVG and additional DOI access record. An exploratory read used the Windows default codec and failed; corrected UTF-8 reads supplied the metadata. No unknown bibliographic value was filled from that failed read.

Critic: the controlled figure strengthens interpretation within the model but does not create empirical industrial validation. Independent matched observations, actual researcher participation, rights, authors and journal eligibility remain C14. The new preparation documents are unsubmitted drafts, not accepted or company-approved representations. No source articles, paid data or new price values were added.

Final C11 verification: **856 passed in504.21s**, wrapper507.762s: [output](commercial-c11-pytest-2026-09-07.log). Python code and tests were held unchanged during this full run. Frontend code is unchanged from the passing C10 checks and CI above. The manuscript generator check resolves every recorded numerical key; it does not establish independent experimental accuracy or author approval.

## C12 public project and contribution evidence

README now distinguishes the login-free local desktop from prepared hosted mode, places prepared1.4.0 versus publishedv1.3.24 beside downloads, and links the detailed research/service records. The [portfolio](../project-portfolio.ko.md) connects user problems to implementation, commits, analysis and test evidence. It retains prior-art credit and AI assistance without inventing sole ownership, author approval, adoption, sales or publication. Existing CITATION/codemeta names and prepared-version status were inspected and preserved.

Updated project links and prepared release notes with current hosted, recovery, rights-review and controlled-study behavior. A fresh `gh repo view` confirms the existing public repository and release homepage; `gh release list -L 1` returnsv1.3.24, published2026-08-31T18:24:09Z, not draft/prerelease. No remote repository metadata changed. Historical Zenodo details were reduced to the verified concept DOI record with its actual evidence date, without assuming future archival success.

Validation reuses unchanged C11 code's856 tests and C10 frontend/Windows CI. Relative documentation links and whitespace are checked before commit. Critic: a portfolio is an evidence index, not an independent determination of individual contribution or ownership. The user's stated project direction is recorded; formal authorship, institutional/company rights and actual outcomes remain C14.

## C13 final integrated verification

The offline primary pipeline ran to a new `_local/commercial-final-paper-replay` directory, preserving the original frozen input/output files. Initial execution completed30.004s. Seven scientific JSON files and all12 main PNG/SVG files are byte-identical to the frozen run. Three further analysis files have equal numerical content after excluding only named run-time metadata: generated_at, history_file, price_source and price_basis_source as applicable. Paths were inspected and input history bytes match. All27 output hashes, current code/data hashes and unchanged frozen outputs verify. The [comparison](commercial-c13-replay-verified-2026-09-07.json) records actual differences; no blanket byte-identity claim is made for manifests.

Controlled replay completed2.677s with identical numerical JSON and PNG/SVG. Its provenance reflects added service/rights modules since C05; the frozen scientific hash remains495b0fe9c5a60476bb29143082d745575976339aab5db4a3aca9c4c9fbd902ee. The manuscript check again verifies94 main/1217 SI references. Fresh Ruff, frontend lint, i18n and all30 Node rules pass; static missing/untranslated label counts are0. Table6.2 remains unchanged. Current public/commercial rights checks returnexit1 as expected for unapproved records, not as a passed publication gate.

Two verification-harness issues are preserved. First, packaging was explicitly pointed at the general Python3.14 test runtime instead of the existing Python3.11 packaging runtime. The existing build script automatically installed PyInstaller6.22.2/hooks2026.7/altgraph0.17.5 into the user Python3.14 environment, then failed on its pre-existing obsolete pathlib backport. No package was removed and no application source/dependency declaration changed. The corrected package run uses the previously successful Python3.11.9/PyInstaller6.19.0 environment. The build forwards `--publish never` to electron-builder; no release or signing configuration is bypassed. Second, an initial comparison excluded only generated_at and correctly rejected relocated absolute input paths. The corrected comparison verifies the named path metadata and numerical payload separately; the failed log is retained.

The first replay overlapped that packager installation, so its environment capture is not claimed to represent an unchanged installed-package set throughout execution. A final replay after the environment stabilized is required for the closing manifest. Calculation inputs/code stayed unchanged. Actual account UI evidence remains C10's six screenshots and saved JSON comparisons, with no frontend source changes since that successful browser run.

That final replay subsequently passed30.522s: [stable comparison](commercial-c13-replay-stable-2026-09-07.json) and [actual environment/commands/input hashes](commercial-c13-reproduction-manifest-2026-09-07.json). The corrected unpublished package passed172.791s; isolated smoke passed17.651s, version1.4.0/one main window/prices and calculateHTTP200. User DB, launcher log and installed executable are byte-unchanged. Test and package jobs ran concurrently, so their timings are not controlled performance comparisons.

[Bounded source review](commercial-c13-source-review-2026-09-07.json) found no LICENSE, existing data, dependency declaration/lock, or file-deletion changes since this goal's baseline. Root package.json changes only the development frontend command. No private-key/GitHub/OpenAI credential-pattern matches occurred in added tracked text; this is not a comprehensive secret/security audit. Private `_local`/`.autonomy` directories remain untracked. Installer/packaged component hashes are recorded. The first build's automatic local tooling installation is the environment change described above, not a repository dependency change.

Closing journal recheck again returned403 for four direct publisher metrics pages. Indexed Engineering Au text displays9.0, while a different Elsevier endpoint displays9.2 versus the earlier issue-page9.6. [The record](commercial-c13-journal-recheck-2026-09-07.json) preserves this discrepancy without certifying a JCR year/category/Q1. The journal review now states both dated observations. No manuscript result or provisional format was altered by this unresolved bibliometric difference.

Linux CI atd972f18 subsequently completed853passed/3failed in766.97s; Windows/frontend jobs passed. The three new manuscript tests exposed a pre-existing Windows separator in frozen manifest figure paths. The manuscript reader now converts that separator before joining the relative path, without changing the manifest or a numerical value. The three focused tests and manuscript check pass locally. The authorized unattended CI-fix scope was followed; no check was disabled or approval/hook bypassed.

A direct Git-blob audit then detected that C11's `-text` attributes had not re-added four previously normalized files: controlled JSON/provenance/SVG and the extra literature access JSON. Their local original bytes still matched the recorded frozen hashes, while stored LF blobs differed. Re-added those exact existing bytes under the existing attributes. JSON content and SVG after line-ending normalization are unchanged; no number, source response or figure was recreated. [34 staged snapshot checks](commercial-c13-snapshot-index-2026-09-07.json) now match. Both the Linux failure and first blob-check failure remain in the logs. This fixes transport of the preserved snapshots instead of weakening their hash guards. A fresh full suite and26.009s paper replay follow this one-line reader correction; final-head CI remains required after push.

## C14 external facts and launch sequence

| Required fact | Current evidence | Responsible next step |
|---|---|---|
| Actual code rights and institutional obligations | Existing author metadata and user project direction; no reviewed employment/research/IP contracts | Developer, relevant institution and actual rights holders establish authority before a company grant |
| Company commercial permission and customer contract | Unexecuted nonexclusive company-license and B2B subscription drafts | Company/rights holders confirm parties, scope, improvement ownership, support and agreed economics; no blanket copyright assignment assumed |
| Bundled/static and dynamic data reuse |81 pending exact-file records,20 declared workbook-origin files; no commercial/public approval | Review permission evidence or independently replace with freely obtainable, commercially reusable sources; free viewing is insufficient |
| Journal objective | Official candidate displays and Engineering Au Article guidance; metric year/JCR category/Q1 not established | Actual authors verify target eligibility and publication-cost coverage, then approve submission |
| Industrial predictive accuracy |12 screened contextual sources; matched full manufacturing observations0; MAPE null | Obtain voluntarily supplied, condition-matched records with separate private/public/commercial consent |
| Researcher usability | Protocol/blank worksheet; actual participants0 | Recruit real consenting researchers and report observed outcomes separately from automated QA |
| Paid service operations | Tested synthetic sessions, entitlements, budgets and recovery; no production endpoint/payment | Company decides host/jurisdiction/TLS/OS access, retention/support, billing/privacy/tax obligations and performs a deployment review |
| Release/deposit | Prepared1.4.0; actual publicv1.3.24 | Resolve distribution hold, review PR, then human tagging/release/updater/Zenodo checks; no automatic launch from this log |

These are external prerequisites, not questions awaiting an unattended response. They remain unresolved without fabricating customers, data rights, contracts, author consent or publication. Acquisition remains free; no additional prices or generic LCA coefficients were invented. The original LICENSE is unchanged. No actual company billing, credentials, deployment, journal submission, release, tag, merge or third-party message occurred.

Final local C13 verification: **856 passed in578.14s**, wrapper582.502s. Corrected build172.791s and isolated smoke17.651s passed; user DB/log/installed-executable hashes are unchanged. The final stable-environment paper run completed30.522s and its numerical/figure comparison passed. No application code changed after the tested source head.


Final post-correction local verification: **856 passed in511.02s**, wrapper515.073s. This supersedes the earlier578.14s full run for the one-line manuscript portability fix. Source and working frozen bytes were held unchanged during this run; only Git staging restored previously normalized snapshot bytes. Final replay26.009s/27hashes and all figure/numerical comparisons passed. Desktop/UI code was unchanged from verified package and browser runs. Closing CI must pass on the pushed correction; no failed job is labelled successful.

## 최종 보고 — 논문·포트폴리오·회사 구독 준비

**준비 작업13개를 완료하고 외부 사실·실행1개(C14)를 보류했다.** 최종 문서 커밋의 CI 확인 결과는 PR112 본문에 기록한다. 이는 Q1 논문 게재나 판매 개시의 완료를 뜻하지 않는다. 기존 D03·V01의 자료/독립 실측 부분 완료 상태도 유지한다.

| ID | 상태 | 커밋 | 근거 명령 출력 요약 |
|---|---|---|---|
| C01 | 준비 완료 | c7f51f1 | 목표·작업표·기준선 |
| C02 | 준비 완료; 승인 미해결 | c2a17d1 | 81파일 권리 목록·12검사·792전체; 공개/상업 이용 검사는 현재 차단 |
| C03 | 완료 | a5279bd | Windows CI·개발 실행 수정·별도 프로필; build227.964s/smoke17.604s |
| C04 | 검토 완료; 자격 미확인 | 248c45e | 공식 저널 안내 확인; JIF연도/JCR분야/Q1 미확인 |
| C05 | 완료 | 26a283e | 30반응군 통제 분석·21제조·9전극; 고정 결과 재현 |
| C06 | 자료 조사 완료; 실측 없음 | f95ac74 | 추가2편 Crossref·무료원문 조사; 조건 일치 실측0 |
| C07 | 계획 완료; 참여 미실시 | b84e343 | 6과제 연구자 평가 계획·빈 관측표; 실제 참여자0 |
| C08 | 완료 | de54164 | 계정별 DB·인증·세션·경계 시험;829전체 |
| C09 | 완료 | d92c681 | 기간·좌석·만료·감사·관리 명령;843전체 |
| C10 | 완료 | 2c08f1f | 실제 브라우저6화면·계정 전환·만료 조회/다운로드·복구;853전체 |
| C11 | 준비 완료 | 9a566d6 | 원고94/SI1217 수치키·27고정산출물·856전체 |
| C12 | 완료 | d972f18 | 공개 설명·기여 근거·릴리스 상태;54상대링크 검사 |
| C13 | 로컬 검증 완료; 최종 CI는 PR에 기록 | 최종 감사 커밋 | 856전체/511.02s; lint/build/Node30/Table6.2/설치스모크/재현 통과 |
| C14 | 보류 — 외부 사실·실행 필요 | 해당 없음 | 실제 권리·회사·저자·저널 자격·실측·참여자·결제/배포 |

원고·SI·커버레터·예상 질문·저자 확인표, 근거 중심 포트폴리오, 회사 이용허락/구독 조건 초안과 실제 계정·권한·복구 구현을 준비했다. 공개 코드는 PolyForm Noncommercial1.0.0을 유지한다. 회사는 실제 권리자의 별도 상업 이용 허락을 확보하는 구조이며, 비독점 제안을 기본으로 하고 저작권 전부 양도를 가정하지 않는다. 코드·데이터·회사의 고객 계약을 각각 검토해야 한다.

### 계산 영향과 재현

이번 C01–C13에서는 기존 원가 계산식·가격 데이터·LCA 계수·미산정 공정 단가를 바꾸지 않았다. 통제 분석은 기존 모델에 새로운 조건 조합을 적용한 것이며 관측 데이터를 추가한 것이 아니다. Table6.2는 **Pt/C27.3695, Ni/Al₂O₃19.2206(−6.65%), FCC각주 b2.4380(+1.16%) USD/lb**로 유지됐다. Pt/C는 센트 단위 일치, Ni와 FCC는 합격 범위다. Ni 판매 마진 규칙과 FCC의 실효 생산 속도 차이를 공개하며 명목 FCC값1.6090을 각주 b 검증값으로 바꾸어 쓰지 않는다.

May2026/seed20260906 재현은27산출물 해시를 확인했다. 주요JSON7개와6그림의PNG/SVG가 기존 고정 결과와 동일하며,3분석 파일은 기록된 시각·절대경로만 다르다. 통제 분석의 수치 SHA-256은 `495b0fe9c5a60476bb29143082d745575976339aab5db4a3aca9c4c9fbd902ee`다. 가격 수치만 바꾸면1반응군, 출처 신뢰 점수만 바꾸면4반응군, 함께 바꾸면5반응군의 최상위 후보가 달라졌다. 전체 변화를 순수 가격 효과로 해석하지 않는다.

[최종 명령·환경·검사](commercial-c13-checks-2026-09-07.json), [현재 재현 매니페스트](commercial-c13-portable-manifest-2026-09-07.json), [수치·그림 비교](commercial-c13-replay-portable-2026-09-07.json), [브라우저 증거](commercial-c10-browser-2026-09-07.json)에 근거가 있다. 브라우저는 합성 계정으로 열촉매·전극 계산, 자료 분리, 다른 탭 로그아웃, 만료 후 저장 결과 조회·다운로드와 새 계산 차단을 확인했다. 실제 고객·독립 참가자 시험은 아니다.

### 성능 전후와 실행 시간

아래 API 수치는 기존 T11의 동일 입력 비교를 재인용한 것으로, 이번 구독 기능의 속도 개선 측정이 아니다. 로컬 TestClient·임시 SQLite, 네트워크 제외 조건이며 논문 기준월과도 다르다.

| 항목 | T11 개선 전 | T11 개선 후 | 근거/해석 |
|---|---:|---:|---|
| calculate20회 중앙값 |3.823ms|3.078ms|t11-performance-before.json / t11-performance-final.json |
| MC1000회 |0.2584s|0.06275s|동일seed 결과 일치 |
| MC10000회 |2.4119s|0.4188s|동일seed 결과 일치; 약5.76배 |
| all families |1.3965s|1.1722s|당시 고정 입력30반응군 |

| 이번 실행 | C03 | C13 | 해석 |
|---|---:|---:|---|
| Windows 패키지 빌드 |227.964s|172.791s|환경·부하/캐시 통제 비교가 아니므로 성능 개선 주장 없음 |
| 별도 프로필 스모크 |17.604s|17.651s|1.4.0·주 창1개·prices/calculate200 |
| 논문 전체 재현 |해당 없음|26.009s|경로 보완 후 최종 오프라인 재현; 가족 분석reference1.656s/live1.376s |

사용자의 DB·실행 로그·설치 실행 파일 해시는 전후 동일하다. 기존 설치본은 교체하지 않았고 검증용 프로세스는 종료했다. 이번 빌드의 설치 파일은 로컬 준비물이며 공개 릴리스가 아니다. 기존 Tailwind sourcemap와 PyInstaller 선택 모듈 경고는 로그에 남겼다.

Linux CI의 원고 검사3건 실패는 Windows 경로 구분자를 읽는 한 줄을 보완해 처리했다. 고정 JSON·SVG4파일은 이전 Git 줄바꿈 변환을 바로잡아 원래 해시 그대로 저장했다. 수치·그림 내용은 동일하며34스냅샷과5원고 메타데이터의 저장될 바이트를 확인했다. 기존 실패 로그도 보존한다.

### 사람이 해야 할 일과 확인 못 한 사항

- **판매 전 최우선:** 실제 코드 권리자·대학/연구비 계약·공동 기여자 권한과 회사 정보를 확인하고 별도 상업 이용허락을 체결한다. 기존81파일 중20파일이 워크북 유래를 명시한다. 무료 열람과 상업 재사용을 구분해 출처별 허락 또는 독립 대체 근거를 확보한다. 현재 공개·상업 이용 검사 모두exit1이며, 승인 없이 태그·출시하지 않는다.
- 회사가 구독 가격·기간·지원·개선분 권리·자료 보존·개인정보·세금·결제·호스팅 조건을 정한다. 실제TLS/OS접근/운영 용량·장애 복구 목표·결제 연동은 확인하지 않았다. 구현된 접근 권한은 실제 계약이나 결제 증명이 아니다.
- 논문 저자가 실제 저자·소속·연구비·이해상충·원고 책임을 확정한다. Engineering Au는 잠정 후보다. JIF의 정확한 연도·JCR분야/Q1과 출판비 조건을 확인하고 최종 저널을 정한다. 요청한 Q1/JIF목표를 달성했다고 쓰지 않는다.
- 조건이 맞는 독립 제조 원가 실적과 동의한 실제 연구자 평가를 확보한다. 현재 실측0·참여자0·MAPE미산정이다. 추가2편은 Crossref를 확인했지만 출판사403과 SI의HTML차단은 남았다. 문헌 기반 모델을 산업 실적으로 바꾸어 부르지 않는다.
- 배포 권리 문제가 해결되면 PR검토·머지 여부를 결정하고 사람이 태그v1.4.0을 푸시한다. 실제 설치/업데이트·릴리스 자산과 Zenodo버전 DOI/concept DOI10.5281/zenodo.21451931 연결을 확인한다. 이번 실행에서는 머지·태그·릴리스·배포·투고·외부 메시지·실결제를 하지 않았다.

### 보수적으로 정한 가정

- 초기 상품은 수동 계약 기록을 쓰는 조직 단위 B2B구독이며 가격·결제사를 만들어 내지 않는다. 계정별 자료를 같은 회사 안에서도 자동 공유하지 않는다.
- 기본 데스크톱은 로그인 없이 사용한다. 서비스 모드에서만 인증·기간·좌석을 강제하며 만료 후 기존 자료의 조회·내보내기를 허용한다. 보안 계정 정지는 별도다.
- 백업/복구는 서비스 중단을 운영자가 확인하고 새 폴더에 수행한다. 자동 무중단 일관성·불변 감사 원장·실제SLA·보안 인증을 주장하지 않는다.
- 실제 권리 승인이 없는 데이터는 승인 처리하지 않는다. 라이선스 파일·원자료·누락 단가를 임의로 바꾸거나 지우지 않는다. 유료 자료 구매·과금 API·키 발급/저장은 하지 않는다.
- 관측이 없는 정확도·참가자·저널 자격은 공백으로 남긴다. AI 지원을 숨기거나 단독 저자·소유권을 커밋 기록만으로 확정하지 않는다.

### 이전 실행 기록

아래 표는 당시 T01–T19 완료 기록이다. 현재 소스의 테스트 수·논문 기준월·데이터 권리 상태는 위 C01–C14와 현재 감사가 우선한다. 이전 실행에서의 공개 링크 응답이나 자료 상태를 이번에 재검증했다고 주장하지 않는다.

<details>
<summary>기존 T01–T19 작업 표 — 당시 결과 보존</summary>

| ID | 상태 | 커밋 | 근거 명령 출력 요약 | 메모 |
|---|---|---|---|---|
| T01 | 완료 | 06b33e3, 84d416f | All four baseline signals passed; outputs above | 필수; Draft PR #112 |
| T02 | 완료 | 87a4791 | Browser thermal/electrode HTTP 200; calculate median 4.15 ms, MC10000 2.812 s; 104 raw JSX/2 missing keys; 1,520 structural objects without direct source | 필수; 2026-09-06-baseline.md |
| T03 | 완료 | 9d08443 | 23 targeted passed; full 605 passed; frontend lint/build passed; browser reference review 18 to 0 | Publication month and fixed anchors; live review age 7 days |
| T04 | 완료 | a8e4597 | 7 focused passed; same seed both request shapes equal; two full family JSON outputs byte-identical; full605 passed | Default seed None replaces implicit42; deterministic score/cost/slug order |
| T05 | 완료 | f8ab863 | 17 focused passed; full pipeline completed; fresh14-series input; hashes/environment captured; full605 passed | Final data regenerated under T16; README and methodology command documented |
| T06 | 완료 | ccfedb6 | 80JSON,3046objects;317/317Crossref;467URLs:287ok,179unverified,1notfound; ruff passed | No source price corrected; Mo23.13 retained; exhaustive status evidence |
| T07 | 완료 | 3001c1b | 28 thermal methods x3 scales API parity; native Node9 passed; full605 and frontendlintbuild pass | Explicit card ID; repeated operations retained; catalog 28+custom+5electrode documented |
| T08 | 완료 | f0ed93e | Node defaults and poisoned-thermal ledger assertions pass; real PEM browser HTTP200 and area ledger verified | Application/template default table; area ledger matches headline; thermal campaign/margin hidden |
| T09 | 완료 | afc1615 | 27 focused tests pass; actual public feeds retrieved; Pt/Pd JM and Cu/Al Westmetall verified; Yahoo300s | Source deltas and full selected snapshot recorded; optional paid feeds not invoked |
| T10 | 완료 | 88bab31 | 38/83 support entries linked;20 focused pass;synthetic90 profile cases; frozen paper has noHS observations so values unchanged | 45 ambiguous entries explicitly unlinked; immutable fixed-price fallbacks |
| T11 | 완료 | 74175cb | 18 focused tests; exact seeded MC JSON equality; final MC10k 0.4188 s vs paired 2.4119 s (5.76x); Table 6.2 unchanged | mtime/size cache and row-major batched RNG; final performance evidence supersedes intermediate run |
| T12 | 완료 | 60c0588 | Methodology error-budget table cites exact price bounds, index inputs, 1/10/150 vs 67 t/day, recovery defaults, LCA gaps and uncosted routes | Prose landed with T05 (f8ab863); validated against regenerated summary and SI; no invented aggregate error bar |
| T13 | 완료 | b93c62d | Clean coverage run 625 passed in 347.52 s; backend/core 94%, every module at least89%; 20 provider HTTP contract tests added | pytest-cov temporary environment only; check:i18n and CI wiring land with T14 translations to keep intermediate CI green |
| T14 | 완료 | e209ff1 | check:i18n 781 calls/822 keys,0 missing/0 untranslated; frontend lint/build and Node9 pass; 3 real browser flows200; 11 README screenshots regenerated | Data text unchanged; Korean guide added; reference review0; capture failures and initial422 recorded honestly |
| T15 | 완료 | 300fbf7 | All4 versions1.4.0; final desktop build156.36s and smoke200/one window; total172.41s; latest public release remains1.3.24 | Prepared metadata, notes and checklist only; isolated junction packaging issue recovered with unchanged-lockfile npm ci |
| T16 | 완료 | ea787f0 | Full pipeline2026-07/seed20260906;14series91months; six PNG/SVGfigures; 26outputs+80data+34code hash checks pass; staged raw SHA preserved | Fresh history fetched; actual live12quote snapshot; latest-common July; live-classification edge tests11 included in final636 |
| T17 | 완료 | e7effeb | Manuscript69+SI980 keys resolve;466 numeric checks;4Crossref citations;165-word abstract; estimated6624 word equivalents; six figures inspected | New3.4/3.5/3.6 and4SI tables; ACS guidelines verified; no invented authorship or version DOI |
| T18 | 완료 | 5365889 | Reviewer checklist plus10 evidence-linked questions/answers; no fabricated performance/coverage/reuse claims | Expected objections cover method reproduction, proxies, sources, LCA, licensing and price reproducibility |
| T19 | 완료 | 0844666 | Final636 passed; ruff, frontend/i18n/Node9, desktop1.4.0, Table6.2 and paper hashes pass; final report prepared | Single PR #112; no merge/tag/release/deployment |

</details>
