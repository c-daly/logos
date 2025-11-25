#!/bin/bash
set -e

echo "Stopping LOGOS OpenTelemetry stack..."
docker compose -f docker-compose.otel.yml down

echo "✓ OTel stack stopped"
