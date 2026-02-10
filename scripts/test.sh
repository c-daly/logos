#!/bin/bash
set -e
echo "=== Logos Tests ==="
poetry run pytest -ra -q "$@"
