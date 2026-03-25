# Release Notes

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
