#!/bin/bash
set -e
echo "=== Logos Dev Services ==="

# Logos is a library — start test infrastructure services
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$SCRIPT_DIR/start_test_services.sh" ]; then
    exec "$SCRIPT_DIR/start_test_services.sh"
else
    echo "No test services script found. Running tests instead."
    exec "$SCRIPT_DIR/test.sh"
fi
