#!/usr/bin/env bash
set -euo pipefail

# One-command Docker demo using simulated data.
# Requires: docker compose, .env copied from example.env

echo "=== RuView Docker Demo ==="
echo "Starting simulated data source..."
echo "Open http://localhost:4000/ui/index.html when ready"
echo ""

docker compose -f docker/docker-compose.yml up --build
