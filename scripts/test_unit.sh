#!/usr/bin/env bash
#
# Run unit tests (no external services required)
#
# Usage:
#   ./scripts/test_unit.sh [pytest-args...]
#
# Examples:
#   ./scripts/test_unit.sh                    # Run all unit tests
#   ./scripts/test_unit.sh -v                 # Verbose output
#   ./scripts/test_unit.sh -k "test_foo"      # Run specific tests
#   ./scripts/test_unit.sh --cov              # With coverage
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "=== LOGOS Unit Tests ==="
echo "Running unit tests (no external services required)..."
echo ""

# Default pytest args if none provided
if [ $# -eq 0 ]; then
    PYTEST_ARGS="-v"
else
    PYTEST_ARGS="$*"
fi

# Run unit tests only
poetry run pytest tests/unit/ $PYTEST_ARGS

echo ""
echo "=== Unit Tests Complete ==="
