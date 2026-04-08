# Release Notes

## v1.1.10 Benchmark Detail Fit and Desktop Refresh

Date: April 9, 2026

This release fixes benchmark-detail overflow in the desktop app and republishes the packaged Windows build so the desktop artifact matches the latest repository state.

### Included In This Update

- Replaced raw benchmark `screening_basis` keys with reader-facing labels in the benchmark detail surface.
- Added safe wrapping for long benchmark metric values so they stay inside the detail cards.
- Rebuilt the packaged desktop app and installer so the benchmark-detail fix is present in the Windows build.
- Updated versioned download references in the repository docs to the `1.1.10` package line.

### Validation Status

The following checks passed on April 9, 2026:

```bash
npm run build
npm run smoke:desktop
```

## v1.1.8 Desktop Sync for Matrix Harness

Date: April 8, 2026

This release updates the packaged desktop app to include the latest calculation-matrix harness and backend runtime fixes already merged on `master`.

### Included In This Update

- Added a calculation harness that exercises frontend thermal composition choices across active-metal, promoter, support, and bimetallic matrices.
- Added route coverage for every valid saved process template and every valid single-step / two-step preparation combination.
- Updated UTC timestamp handling in the backend scheduler and health-report flow to remove deprecated naive UTC calls.
- Rebuilt the Windows desktop package so the GitHub release matches the latest verified repository state.

### Validation Status

The following checks passed on April 8, 2026:

```bash
python -m pytest backend/tests/test_calculation_harness.py -q
python -m pytest backend/tests -q
npm run build
npm run smoke:desktop
```

## v1.1.7 Dataset and Release Sync

Date: April 8, 2026

This release aligns the packaged desktop app and GitHub release state with the latest repository changes.

### Included In This Update

- Expanded energy-transition benchmark families with additional thermal and electrocatalyst datasets.
- Added new benchmark coverage for `CO2 methanation`, `formic acid dehydrogenation`, and `AEM electrolyzer OER`.
- Extended benchmark and library harness tests so route templates, citation links, and candidate references are checked together.
- Tightened GitHub-facing README and documentation copy to keep the repository description factual and project-specific.

### Validation Status

The following checks passed on April 8, 2026:

```bash
python -m pytest backend/tests -q
cd frontend && npm run build
npm run build
npm run smoke:desktop
```

## v1.0.1 Desktop Hardening

Date: March 26, 2026

This patch release focuses on desktop startup reliability, packaging repeatability, and release verification.

### Included In This Update

- Added a packaged backend sidecar build flow for the Electron desktop app.
- Fixed splash-screen hang cases where the backend was ready but the splash window remained visible.
- Improved second-instance handling so relaunch brings the running app forward instead of starting a broken duplicate path.
- Added launcher logging at `AppData\Roaming\CatPrice\catprice-launcher.log`.
- Added `desktop:stop`, `smoke:desktop`, and `pack:smoke` scripts for repeatable desktop validation.
- Added desktop troubleshooting documentation and updated getting-started instructions.

### Validation Status

The following checks passed on March 26, 2026:

```bash
python -m pytest backend/tests -q
cd frontend && npm run lint
cd frontend && npm run build
npm run pack:smoke
```

## Release Prep Snapshot

Date: March 25, 2026

This snapshot prepares CatPrice for public GitHub use by aligning the checked-in project state with the CatCost workbook and by restoring a clean validation path across backend and frontend.

## Included In This Update

- Synced workbook-derived data assets from `CatCost_v1-1-1.xlsx`.
- Added repeatable sync and validation scripts for CatCost-derived JSON files.
- Restored backend compatibility for both legacy flat calculator inputs and the newer component-based payloads.
- Fixed CEPCI/ChemPPI loading and UTF-8 file handling issues that broke tests on Windows.
- Added missing process template and factor data files required by the workbook-backed workflow.
- Fixed frontend lint/build issues and separated unit context utilities for cleaner React refresh behavior.
- Updated documentation to reflect the actual Electron-based desktop packaging flow.

## Validation Status

The following checks passed on March 25, 2026:

```bash
python scripts/validate_catcost_data.py
python -m pytest backend/tests -q
cd frontend && npm run lint
cd frontend && npm run build
```

## Notes

- The GitHub default branch remains `master`.
- Local helper files for Codex launcher workflows were intentionally kept out of the Git commit history.
- Frontend production build still reports a large bundle-size warning, but the build completes successfully.
