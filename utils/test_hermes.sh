#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGOS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
HERMES_ROOT="${HERMES_REPO:-${LOGOS_ROOT}/../hermes}"
COMPOSE_FILE="${HERMES_ROOT}/docker-compose.test.yml"
SERVICES=(etcd minio milvus)
stack_started=0

if [[ ! -d "$HERMES_ROOT" ]]; then
  echo "[error] Hermes repository not found at '$HERMES_ROOT'. Set HERMES_REPO to override." >&2
  exit 1
fi

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[error] Required command '$1' not found in PATH" >&2
    exit 1
  fi
}

start_stack() {
  echo "[hermes:test] Starting ${SERVICES[*]} via docker compose..."
  docker compose -f "$COMPOSE_FILE" up -d "${SERVICES[@]}" >/dev/null
  stack_started=1
  echo "[hermes:test] Waiting for Milvus health endpoint..."
  timeout 180 bash -c 'until curl -sSf http://localhost:9091/healthz >/dev/null; do sleep 3; done'
}

cleanup() {
  if [[ $stack_started -eq 1 && -z "${KEEP_HERMES_INFRA:-}" ]]; then
    echo "[hermes:test] Stopping docker compose services..."
    docker compose -f "$COMPOSE_FILE" stop "${SERVICES[@]}" >/dev/null || true
    docker compose -f "$COMPOSE_FILE" rm -f "${SERVICES[@]}" >/dev/null || true
  fi
}

trap cleanup EXIT

require_command docker
require_command curl
require_command poetry

pushd "$HERMES_ROOT" >/dev/null

echo "[hermes:test] Installing poetry dependencies (dev extras)..."
poetry install --extras "dev" >/dev/null
echo "[hermes:test] Installing CPU torch wheels..."
poetry run pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu >/dev/null
echo "[hermes:test] Installing sentence-transformers..."
poetry run pip install sentence-transformers >/dev/null

start_stack

echo "[hermes:test] Running pytest $*"
poetry run pytest "$@"

popd >/dev/null
