# CatPrice Documentation

CatPrice is a desktop-only catalyst cost tool. The application is packaged and distributed through Electron, while the FastAPI backend runs as a local loopback sidecar inside the desktop workflow.

## Focus

- desktop packaging and installation
- catalyst composition costing
- local-only calculation workflow
- live and indexed metal pricing
- uncertainty and comparison analysis

## Local Development

```bash
npm install
npm run dev
```

This starts the Electron shell, the local FastAPI sidecar, and the Vite renderer used during desktop development.
