#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if ! docker info >/dev/null 2>&1; then
  echo "Start Docker before launching Fluid Controls RFQ."
  exit 1
fi
if [ ! -f .env ]; then cp .env.example .env; fi
docker compose up -d --build --wait
echo "Fluid Controls RFQ: http://localhost:5000"
