#!/usr/bin/env bash
#
# Run integration tests (requires Neo4j and Milvus)
#
# Usage:
#   ./scripts/test_integration.sh [pytest-args...]
#
# Examples:
#   ./scripts/test_integration.sh                    # Run all integration tests
#   ./scripts/test_integration.sh -v                 # Verbose output
#   ./scripts/test_integration.sh -k "test_neo4j"    # Run specific tests
#   ./scripts/test_integration.sh --cov              # With coverage
#
# Prerequisites:
#   Start test infrastructure first:
#     ./scripts/start_test_services.sh
#
#   Or manually:
#     docker compose -f tests/e2e/stack/logos/docker-compose.test.yml up -d
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

# Source test environment
STACK_DIR="$REPO_ROOT/tests/e2e/stack/logos"
if [ -f "$STACK_DIR/.env.test" ]; then
    set -a
    source "$STACK_DIR/.env.test"
    set +a
fi

# Export standard test ports
export NEO4J_HTTP_PORT="${NEO4J_HTTP_PORT:-7474}"
export NEO4J_BOLT_PORT="${NEO4J_BOLT_PORT:-7687}"
export MILVUS_PORT="${MILVUS_PORT:-19530}"
export NEO4J_URI="${NEO4J_URI:-bolt://localhost:${NEO4J_BOLT_PORT}}"
export NEO4J_USER="${NEO4J_USER:-neo4j}"
export NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4jtest}"
export NEO4J_CONTAINER="${NEO4J_CONTAINER:-logos-phase2-test-neo4j}"
export MILVUS_CONTAINER="${MILVUS_CONTAINER:-logos-phase2-test-milvus}"

echo "=== LOGOS Integration Tests ==="
echo "Testing against:"
echo "  Neo4j:  bolt://localhost:${NEO4J_BOLT_PORT}"
echo "  Milvus: localhost:${MILVUS_PORT}"
echo ""

# Check if services are running
check_service() {
    local name=$1
    local container=$2
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        echo "✓ $name is running"
        return 0
    else
        echo "✗ $name is NOT running"
        return 1
    fi
}

SERVICES_OK=true
check_service "Neo4j" "$NEO4J_CONTAINER" || SERVICES_OK=false
check_service "Milvus" "$MILVUS_CONTAINER" || SERVICES_OK=false

if [ "$SERVICES_OK" = false ]; then
    echo ""
    echo "Some services are not running. Start them with:"
    echo "  ./scripts/start_test_services.sh"
    echo ""
    echo "Or run tests anyway (they will skip if services unavailable):"
    echo "  ./scripts/test_integration.sh --continue-on-collection-errors"
    echo ""
fi

echo ""

# Default pytest args if none provided
if [ $# -eq 0 ]; then
    PYTEST_ARGS="-v"
else
    PYTEST_ARGS="$*"
fi

# Run integration tests (includes tests/integration/ and tests/infra/)
poetry run pytest tests/integration/ tests/infra/ $PYTEST_ARGS

echo ""
echo "=== Integration Tests Complete ==="
