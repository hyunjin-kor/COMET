# CatPrice Documentation

CatPrice is a desktop catalyst cost application. The Electron shell, local FastAPI backend, calculation engine, and bundled datasets are all maintained in this repository.

## Project Links

- GitHub repository: [hyunjin-kor/CatPrice](https://github.com/hyunjin-kor/CatPrice)
- Latest release: [v1.3.4](https://github.com/hyunjin-kor/CatPrice/releases/tag/v1.3.4)
- Link map and Claude handoff notes: [`project-links.md`](project-links.md)

## Focus

- desktop packaging and installation
- catalyst composition costing
- thermocatalyst versus electrocatalyst workflow separation
- local-only calculation workflow
- live and indexed metal pricing
- source-linked evidence review
- optional spent catalyst recovery screening
- uncertainty and comparison analysis
- test and smoke-harness validation

## Local Development

```bash
npm install
npm run dev
```

This starts the Electron shell, the local FastAPI sidecar, and the Vite renderer used during desktop development.
