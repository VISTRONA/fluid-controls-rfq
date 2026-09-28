#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "       Fluid Controls RFQ"
echo "=========================================="
echo

if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker is not running."
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "Creating .env..."
    cp .env.example .env
fi

echo "Starting application..."
docker compose up -d --build

echo
docker compose ps

echo
echo "=========================================="
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "Swagger:  http://localhost:8000/docs"
echo "=========================================="
