#!/bin/bash
set -e
echo "=== Logos Lint ==="
ruff check .
black --check .
