#!/bin/bash
set -euo pipefail
echo "=== Logos Lint ==="
poetry run ruff check .
poetry run black --check .
