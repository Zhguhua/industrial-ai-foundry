#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "Starting Industrial AI Foundry..."
docker compose up --build -d

echo "Waiting for API..."
for _ in $(seq 1 60); do
  if python - <<'PY'
import urllib.request
try:
    urllib.request.urlopen("http://localhost:8000/health", timeout=2).read()
except Exception:
    raise SystemExit(1)
PY
  then
    break
  fi
  sleep 2
done

docker compose wait demo-seed || true

echo
echo "Industrial AI Foundry is ready."
echo "UI:       http://localhost:5173"
echo "API:      http://localhost:8000/docs"
echo "Neo4j:    http://localhost:7474"
echo "MinIO:    http://localhost:9001"
echo
echo "Run smoke test: python scripts/smoke-test.py"
