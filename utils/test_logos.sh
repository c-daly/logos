#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/infra/docker-compose.hcg.dev.yml"
SERVICES=(milvus-standalone neo4j shacl-validation)
stack_started=0

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[error] Required command '$1' not found in PATH" >&2
    exit 1
  fi
}

start_stack() {
echo "[logos:test] Ensuring ${SERVICES[*]} are running via docker compose..."
services_to_start=()
for svc in "${SERVICES[@]}"; do
  case "$svc" in
    milvus-standalone)
      port=9091
      container_name="logos-hcg-milvus"
      ;;
    neo4j)
      port=7687
      container_name="logos-hcg-neo4j"
      ;;
    shacl-validation)
      port=8081
      container_name="logos-shacl-validation"
      ;;
    *)
      port=""
      container_name=""
      ;;
  esac

  if [[ -n "$port" ]]; then
    if lsof -iTCP:$port -sTCP:LISTEN >/dev/null 2>&1; then
      echo "[logos:test] Port $port already in use; assuming $svc is running."
      continue
    fi
  fi

  state=$(docker compose -f "$COMPOSE_FILE" ps -q "$svc" | xargs -r docker inspect -f '{{ .State.Running }}' 2>/dev/null || true)
  if [[ "$state" != "true" ]]; then
    services_to_start+=("$svc")
  fi
done

if [[ ${#services_to_start[@]} -gt 0 ]]; then
  docker compose -f "$COMPOSE_FILE" up -d "${services_to_start[@]}" >/dev/null
  stack_started=1
else
  echo "[logos:test] All services already running; skipping compose up."
fi

  echo "[logos:test] Waiting for Milvus health endpoint..."
  timeout 180 bash -c 'until curl -sSf http://localhost:9091/healthz >/dev/null; do sleep 3; done'
  echo "[logos:test] Waiting for Neo4j Bolt port..."
  timeout 120 bash -c 'until nc -z localhost 7687 >/dev/null 2>&1; do sleep 3; done'
  echo "[logos:test] Waiting for SHACL validation service..."
  timeout 120 bash -c 'until curl -sSf http://localhost:8081/health >/dev/null; do sleep 3; done'
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
require_command lsof
require_command nc
require_command poetry

pushd "$REPO_ROOT" >/dev/null

start_stack
./infra/init_milvus.sh

echo "[logos:test] Installing dependencies (poetry install --with dev)..."
poetry install --with dev >/dev/null

echo "[logos:test] Running pytest $*"
poetry run pytest "$@"

popd >/dev/null
