#!/bin/bash
set -euo pipefail
echo "=== Logos Tests ==="
poetry run pytest -ra -q "$@"
