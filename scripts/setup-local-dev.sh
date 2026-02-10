#!/bin/bash
set -e
echo "=== Logos Local Development Setup ==="

# Check for Poetry
if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Install it from https://python-poetry.org/"
    exit 1
fi

poetry install --with dev,test

if [ ! -f .env ] && [ -f .env.example ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
fi

echo "Local dev setup complete. Run 'poetry run pytest' to verify."
