#!/usr/bin/env bash
#
# Run E2E tests (requires full test stack)
#
# Usage:
#   ./scripts/test_e2e.sh [pytest-args...]
#
# Examples:
#   ./scripts/test_e2e.sh                    # Run all E2E tests
#   ./scripts/test_e2e.sh -v                 # Verbose output
#   ./scripts/test_e2e.sh -k "test_phase1"   # Run specific tests
#   ./scripts/test_e2e.sh --run-slow         # Include slow tests
#
# This script:
#   1. Starts test infrastructure (Neo4j, Milvus)
#   2. Seeds test data (ontology, collections)
#   3. Runs the full test suite
#   4. Leaves services running for inspection
#
# To stop services after:
#   ./scripts/start_test_services.sh stop
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

# Delegate to the existing run_e2e.sh which handles everything
exec "$REPO_ROOT/tests/e2e/run_e2e.sh" "$@"
