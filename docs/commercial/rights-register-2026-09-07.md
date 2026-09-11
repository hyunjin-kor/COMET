# Code, data and service rights register

Reviewed as a preparation task on2026-09-07. This register records evidence and unresolved permissions; it is not a legal clearance. Existing LICENSE and input files remain unchanged. No permission requests, purchases, subscriptions, keys or third-party messages were sent.

## Code and ownership

| Asset/right | Evidence | Decision |
|---|---|---|
| COMET code | Root LICENSE; repository contribution history | Keep PolyForm Noncommercial1.0.0. A separate company license requires the actual rights holder; no automatic assignment or commercial grant |
| University/employment/funding rights | Actual contracts and institutional rules not supplied | Unconfirmed. Review before the company signs customer contracts |
| Outside contributions | CONTRIBUTING currently grants incorporation under the noncommercial license | Obtain any additional commercial permission actually required; do not presume retroactive agreement |
| Names, research contribution and authorship | Git records are evidence of commits, not all human intellectual contribution | Preserve verified attribution; authors and company conflicts must be confirmed separately |
| Dependency code, fonts and notices | [Metadata inventory](dependency-license-inventory-2026-09-07.json):49 installed runtime Python packages under the packaging interpreter3.11.9,580 npm lockfile entries including optional/dev entries; no missing Python runtime requirements | The COMET license cannot replace third-party licenses; metadata is not a complete binary SBOM or a notice/compatibility certification |

## Bundled data inventory

[The machine-readable inventory](data-rights-2026-09-07.json) covers **81 files**, including nested process templates. It records the exact SHA-256 of each file. **20 files** declare both CatCost and a workbook sheet in their source metadata. This is an origin finding, not a claim that every value in each file is protected or that a public methodology cannot be independently implemented.

| Group | Local evidence | Current action |
|---|---|---|
| Historical materials | `materials_library.json` declares the CatCost Materials Library sheet;606 records | Block new distribution pending independent source replacement or rights evidence |
| Equipment library | `equipment_library.json` declares the Equip. Library sheet;241 records | Same; a workbook exclusion alone does not clear extracted JSON |
| CEPCI, earlier ChemPPI, CapEx/OpEx and spent catalyst | Source fields identify corresponding workbook sheets | Review per original source. A generic government-data claim cannot clear a mixed or privately compiled series |
| Step library and12 process templates | Default or template source metadata identifies workbook sheets; some per-entry sources have been updated | Retain Table6.2 method validation; distinguish publicly published guide values from workbook extraction before clearance |
| Other61 files | Literature, independently authored definitions, supplier quotations, public reports and support history have mixed evidence | Pending use-specific review; no invented commercial permission |

The previous README sentence claiming that COMET did not redistribute CatCost source data was unsupported by these local files and has been corrected. The source workbook itself is ignored by git, but derived files are present. No original dataset was copied into this report; no data/history was deleted or rewritten. Local verification is not a new public release.

## Price and literature reuse

| Source | Verified evidence and access | Subscription decision |
|---|---|---|
| IMF PCPS | [Official terms](https://www.imf.org/en/about/copyright-and-terms) have special statistical-data conditions, attribution/transformation requirements, third-party caveats, and direct potential commercial reuse to permission requests. Readable through web retrieval; direct HTTP403 | Do not assume the reference basis can be sold or redistributed. No permission has been obtained |
| UN Comtrade | [Current policy](https://uncomtrade.org/docs/policy-on-use-and-re-dissemination/) HTTP200 distinguishes internal/free analytical use and small/publication exceptions from for-profit applications and redistribution fees; it also discusses substantially transformed data and case-specific decisions. [Agreement](https://comtrade.un.org/licenseagreement.html) HTTP200 | Existing small research evidence is distinct from a paid SaaS feed. No paid license is permitted by project policy; leave hosted redistribution disabled unless a no-fee permission/exemption for the exact service is confirmed |
| Yahoo/yfinance | [Maintainer documentation](https://github.com/ranaroussi/yfinance) HTTP200 distinguishes its Apache code license from Yahoo data rights and identifies the API as intended for personal use | Disable this feed for commercial service pending actual rights; a free library is not a commercial data license |
| Johnson Matthey, Kitco, Markets Insider, Westmetall, supplier offers | Retrieval and citation records exist; use-specific commercial redistribution permission was not established here | Pending; do not resell or expose quotations as a cleared commercial feed |
| BLS | [Copyright statement](https://www.bls.gov/opub/copyright-information.htm) identifies BLS publications as public domain except pre-existing copyrighted images. Web text readable; direct HTTP403 | Candidate for independent, attributed recollection of relevant original index values; does not retrospectively clear mixed workbook files |
| USGS/DOE reports and article aggregates | Review the particular publication, credited third-party material, license and extracted fact | Government hosting or a DOI alone is insufficient. Prefer free, expressly reusable original facts with source locators |
| Open-access articles | Existing literature audits retain specific article licenses where verified | Respect the exact article license, figure/table rights and cited external datasets. No bulk full-text/figure redistribution is authorized by this register |

Exact request times/status codes and response hashes are in [source access evidence](source-access-2026-09-07.json). Full fetched pages remain local. HTTP success establishes reachability, not permission. The IMF and BLS direct403 results are not represented as HTTP200. Previous research-only Comtrade findings remain valid within their stated small-evidence scope; they do not license a future for-profit offering.

## Enforced release review

```bash
python scripts/check_data_rights.py --purpose public_distribution
python scripts/check_data_rights.py --purpose commercial_use
```

Both currently return a nonzero exit because this is an **unapproved** inventory. This is the expected safety result, not a passed commercial-readiness check. The tag release workflow now checks public redistribution before packaging/publication. Local tests and unpublished PR packaging remain available. No release has been triggered.

For each file an authorized reviewer must record the evidence reference, review date, reviewer, exact content hash and separate public-distribution/commercial-use decision. New files, changed bytes, missing entries, malformed manifests and missing review details fail. An approval string is an accountable record, not proof that a legal right exists. The checker does not evaluate contracts, dependencies, source code ownership, customer data or dynamically collected feeds; these require their own approval. A cleared public manifest is not a commercial manifest.

Do not change `pending` to `approved` merely to make release CI green. Replace questionable data only with verified free originals or obtain no-cost permission covering the intended use. Preserve historical research snapshots, explain numerical changes and rerun Table6.2 and the affected analyses. No paid data fallback is allowed.
