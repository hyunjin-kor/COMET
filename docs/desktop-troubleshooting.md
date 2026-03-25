# Desktop Troubleshooting

## Launch Flow

CatPrice desktop startup follows this order:

1. launch `CatPrice.exe`
2. start or reuse the packaged FastAPI sidecar
3. wait for `http://127.0.0.1:8765/api/health`
4. open the packaged frontend
5. close the splash window and show the main app window

If startup stalls, the launcher log is the first place to check.

## Launcher Log

The Electron launcher writes a startup log here:

```text
C:\Users\<your-user>\AppData\Roaming\CatPrice\catprice-launcher.log
```

Typical entries include:

- backend reuse
- sidecar startup path
- backend timeout
- packaged frontend load path
- second-instance recovery

## Common Fixes

### Splash screen stays visible

The backend may already be running, or the frontend window may have failed to load.

Check:

- `catprice-launcher.log`
- `http://127.0.0.1:8765/api/health`

### Packaging fails with `Access is denied`

This usually means `CatPrice.exe` is still running while `electron-builder` tries to overwrite the old build.

Use:

```bash
npm run desktop:stop
npm run pack
```

### Quick smoke test

After packaging, run:

```bash
npm run smoke:desktop
```

This verifies:

- desktop app launch
- backend health endpoint
- prices endpoint
- sample calculate request
- second-instance recovery

## Manual Recovery

If you want to reset the desktop app state before a new test run:

```bash
npm run desktop:stop
```
