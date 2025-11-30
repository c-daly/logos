#!/bin/bash
set -e

echo "Starting LOGOS OpenTelemetry stack..."

# Start OTel collector and Jaeger
docker compose -f docker-compose.otel.yml up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 5

# Check service status
docker compose -f docker-compose.otel.yml ps

echo ""
echo "✓ OTel stack is ready!"
echo "  Jaeger UI:    http://localhost:16686"
echo "  Prometheus:   http://localhost:9090"
echo "  OTLP gRPC:    localhost:4319"
echo "  OTLP HTTP:    localhost:4320"
echo ""
echo "Note: Services may take 10-15 seconds to become fully healthy."
echo "Check status with: docker compose -f docker-compose.otel.yml ps"
