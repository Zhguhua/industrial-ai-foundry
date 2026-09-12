#!/usr/bin/env bash
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

if [ ! -f .env ]; then
  cp .env.example .env
fi

docker compose up --build -d

echo
echo "Industrial AI Foundry is starting."
echo "Open the forwarded port 5173 from the Codespaces Ports panel."
echo "The port is configured as private."
