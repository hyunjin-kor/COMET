# Getting Started

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

## Installation

### Backend

```bash
# Clone the repository
git clone https://github.com/yourusername/catprice.git
cd catprice

# Install Python dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env
# Edit .env with your API keys (optional)

# Start the API server
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (one-command)

```bash
docker compose up --build
```

## Configuration

### API Keys (Optional)

CatPrice works without API keys using reference prices. For real-time prices:

| Key | Source | Free Tier |
|-----|--------|-----------|
| `METALS_DEV_API_KEY` | [metals.dev](https://metals.dev) | 50 req/month |
| `METALPRICE_API_KEY` | [metalpriceapi.com](https://metalpriceapi.com) | 50 req/month |
| `BLS_API_KEY` | [bls.gov](https://www.bls.gov/developers/) | Free (registration) |

## Running Tests

```bash
# Backend
pytest backend/tests/ -v

# Frontend type check
cd frontend && npx tsc --noEmit
```
