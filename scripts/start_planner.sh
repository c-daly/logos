#!/usr/bin/env bash

# Start Planner Stub Service
# This script starts the planner stub service for local development and testing.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Configuration
PLANNER_PORT="${PLANNER_PORT:-8001}"
PLANNER_HOST="${PLANNER_HOST:-0.0.0.0}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}LOGOS Planner Stub Service${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if port is already in use
if lsof -Pi :${PLANNER_PORT} -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}Planner service is already running on port ${PLANNER_PORT}${NC}"
    echo ""
    echo "Health check:"
    curl -s http://localhost:${PLANNER_PORT}/health | python -m json.tool
    echo ""
    echo "API documentation: http://localhost:${PLANNER_PORT}/docs"
    exit 0
fi

echo "Starting planner stub service..."
echo "  Host: ${PLANNER_HOST}"
echo "  Port: ${PLANNER_PORT}"
echo ""

cd "${REPO_ROOT}"

# Start the service
python -m uvicorn planner_stub.app:app \
    --host "${PLANNER_HOST}" \
    --port "${PLANNER_PORT}" \
    --log-level info \
    --reload

echo ""
echo -e "${GREEN}Planner service stopped${NC}"
