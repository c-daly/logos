#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/infra/docker-compose.hcg.dev.yml"
SERVICES=(milvus minio etcd)
stack_started=0

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[error] Required command '$1' not found in PATH" >&2
    exit 1
  fi
}

start_stack() {
  echo "[logos:test] Starting ${SERVICES[*]} via docker compose..."
  docker compose -f "$COMPOSE_FILE" up -d "${SERVICES[@]}" >/dev/null
  stack_started=1
  echo "[logos:test] Waiting for Milvus health endpoint..."
  timeout 180 bash -c 'until curl -sSf http://localhost:9091/healthz >/dev/null; do sleep 3; done'
}

cleanup() {
  if [[ $stack_started -eq 1 && -z "${KEEP_LOGOS_INFRA:-}" ]]; then
    echo "[logos:test] Stopping docker compose services..."
    docker compose -f "$COMPOSE_FILE" stop "${SERVICES[@]}" >/dev/null || true
    docker compose -f "$COMPOSE_FILE" rm -f "${SERVICES[@]}" >/dev/null || true
  fi
}

trap cleanup EXIT

require_command docker
require_command curl
require_command poetry

pushd "$REPO_ROOT" >/dev/null

start_stack
./infra/init_milvus.sh

echo "[logos:test] Installing dependencies (poetry install --with dev)..."
poetry install --with dev >/dev/null

echo "[logos:test] Running pytest $*"
poetry run pytest "$@"

popd >/dev/null
