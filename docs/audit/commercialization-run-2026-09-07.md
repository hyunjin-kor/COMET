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
| C04 | Evidence review complete; target eligibility pending | 248c45e | Official indexed JIF displays and HTTP200 Engineering Au Article guidance; metric year/JCR category/Q1 unverified, no acceptance claim |
| C05 | Complete | 26a283e | 30 crossed price/evidence families,21 manufacturing scenarios,9 electrode scenarios; byte-identical replay;802 full tests passed |
| C06 | Evidence extension complete; real observations unresolved | f95ac74 | 2 additional Crossref-verified papers, actual HTTP/PDF checks and private collection worksheet; matched observations remain0 |
| C07 | Protocol complete; participants unresolved | b84e343 | 6 defined tasks, recording/analysis criteria, empty CSV, actual participants0 |
| C08 | Foundation complete | de54164 | 27 account/auth/storage tests;829 full tests460.46s; frontend lint/build/i18n and Table6.2 passed; startup remains rights-gated |
| C09 | Complete | d92c681 | Subscription periods/seats/audit/operator commands;843 full tests475.34s; no actual billing or accounts |
| C10 | Complete | 2c08f1f | Actual browser thermal/electrode/account/expiry QA;853 full tests511.11s; frontend lint/build/i18n, storage test, limits and new-directory recovery |
| C11 | Preparation complete | 9a566d6 | Controlled scientific claims,94 manuscript/1217 SI JSON-key references,13 focused tests;856 full tests504.21s |
| C12 | Complete | this commit | Concise public entry points, evidence-linked portfolio, accurate prepared/released and commercial status; local links checked |
| C13 | Pending | — | Integrated truth signals, real UI, package and final CI |
| C14 | External facts required | — | Rights/company/author approvals, independent observations/participants, JCR category, billing/hosting/launch choices |

## Boundaries

No existing LICENSE change, paid source, new framework/ORM/build tool, destructive DB change, generated credentials, live billing, third-party message, contract execution, tag, merge, release, external hosting, deposit or journal submission is authorized by this preparation. New legal documents will be drafts with unresolved fields, not representations that the user or company has already acquired rights. Existing noncommercial desktop use remains available. A subscription entitlement is an access-control mechanism, not proof of copyright ownership or data reuse permission.

## Next action

Finish C12 public portfolio documentation, then C13 final package, replay and CI verification. No release can be described as commercially cleared before the actual data-origin permissions are resolved.

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
