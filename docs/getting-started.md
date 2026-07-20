# Getting Started

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+
- Windows for desktop packaging

## Desktop Build

```bash
npm install
npm run build
```

The packaged app is generated locally under:

```text
dist-electron\
```

Primary local outputs:

- `dist-electron\CatPrice Setup <version>.exe`
- `dist-electron\win-unpacked\CatPrice.exe`

GitHub release assets follow the pattern `CatPrice.Setup.<version>.exe`, where `<version>` matches `package.json`.

For normal distribution, the installer is enough. The packaged app bundles the local backend and the seed data files, and CatPrice initializes or updates the local SQLite database at startup.

Before rebuilding, you can stop any running desktop instance with:

```bash
npm run desktop:stop
```

## Local Desktop Development

```bash
npm install
npm run dev
```

The Vite renderer appears at `http://localhost:5173`, but this is only a local development service for the Electron app on the same machine.

## Configuration

### API Keys (Optional)

CatPrice works without API keys using indexed or manual prices. For real-time prices:

| Key | Source | Free Tier |
|-----|--------|-----------|
| `METALS_DEV_API_KEY` | [metals.dev](https://metals.dev) | 50 req/month |
| `METALPRICE_API_KEY` | [metalpriceapi.com](https://metalpriceapi.com) | 50 req/month |
| `BLS_API_KEY` | [bls.gov](https://www.bls.gov/developers/) | Free (registration) |

## Running Tests

```bash
pytest backend/tests/ -v
cd frontend && npm run build
```

## Desktop Smoke Test

After packaging, run:

```bash
npm run smoke:desktop
```

This verifies:

- desktop launch
- backend health
- prices API
- sample calculation API
- second-instance recovery

The desktop launcher log is written to:

```text
C:\Users\<your-user>\AppData\Roaming\CatPrice\catprice-launcher.log
```
