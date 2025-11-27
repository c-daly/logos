#!/usr/bin/env bash
# Mirror the Python portion of .github/workflows/ci.yml locally so contributors can
# run identical checks before opening a PR.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
POETRY_BIN="${POETRY_BIN:-poetry}"

if ! command -v "$POETRY_BIN" >/dev/null 2>&1; then
  echo "[run_ci] poetry not found (override via POETRY_BIN)." >&2
  exit 1
fi

cd "$REPO_ROOT"

run_step() {
  local description=$1
  shift
  echo "\n==> ${description}" >&2
  "$@"
}

run_step "Installing dependencies via Poetry" "$POETRY_BIN" install --with dev
run_step "Ruff lint" "$POETRY_BIN" run ruff check .
run_step "Black formatting check" "$POETRY_BIN" run black --check .
run_step "mypy type check" "$POETRY_BIN" run mypy .
run_step "pytest with coverage" "$POETRY_BIN" run pytest -v --cov --cov-report=term-missing --cov-report=xml

echo "\nCI parity run completed successfully." >&2
