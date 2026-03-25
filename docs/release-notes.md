# Release Notes

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
