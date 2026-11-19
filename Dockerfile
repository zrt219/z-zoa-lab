# Stage 1: Build Frontend Assets
FROM node:22-slim AS frontend-builder
WORKDIR /app/frontend

RUN npm install -g pnpm
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

# Stage 2: Build Python Virtual Environment
FROM python:3.12-slim AS python-builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir --upgrade pip
COPY pyproject.toml ./
RUN /app/.venv/bin/pip install --no-cache-dir .

# Stage 3: Production Runtime
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

COPY --from=python-builder /app/.venv /app/.venv
COPY . /app
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

EXPOSE 8080

CMD ["/app/.venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
