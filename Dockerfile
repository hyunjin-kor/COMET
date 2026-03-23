# --- Backend ---
FROM python:3.11-slim AS backend

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY backend/ backend/

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


# --- Frontend build ---
FROM node:20-alpine AS frontend-build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build


# --- Production ---
FROM python:3.11-slim AS production

WORKDIR /app

# Install Python deps
COPY pyproject.toml ./
RUN pip install --no-cache-dir . && pip install --no-cache-dir uvicorn[standard]

COPY backend/ backend/

# Copy built frontend
COPY --from=frontend-build /app/dist /app/static

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
