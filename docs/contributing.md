# Contributing

## Development Setup

```bash
git clone https://github.com/hyunjin-kor/CatPrice.git
cd CatPrice
pip install -e ".[dev]"
cd frontend && npm install && cd ..
npm install
```

## Code Standards

- **Python**: ruff, type hints required, Google-style docstrings
- **TypeScript**: strict mode
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`)
- **PRs**: Include tests, one feature per PR

## Running Tests

```bash
pytest backend/tests/ -v
cd frontend && npm run build
```

## Desktop Packaging Check

```bash
npm run build
npm run smoke:desktop
```

## Adding a New Processing Step

1. Add the step to `backend/core/constants.py` in `STEP_COSTS`
2. Add metadata to `backend/data/step_library.json`
3. Add tests in `backend/tests/test_step_method.py`

## Adding a New Metal

1. Add to `backend/data/materials_library.json`
2. Update `backend/services/price_scheduler.py` name/unit maps
3. Add to `backend/core/constants.py` if it has spent catalyst recovery data

## License

All rights reserved. See `LICENSE`.
