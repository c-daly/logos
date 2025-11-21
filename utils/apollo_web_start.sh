#!/usr/bin/env bash

# Bootstrap the LOGOS Phase 2 demo stack (Sophia + Hermes + Apollo web)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/logs/apollo_web_start"
INFRA_COMPOSE="${ROOT_DIR}/infra/docker-compose.hcg.dev.yml"
SOPHIA_DIR="${ROOT_DIR}/logos_sophia"
HERMES_DIR="${ROOT_DIR}/../hermes"
APOLLO_WEB_DIR="${ROOT_DIR}/../apollo/webapp"

mkdir -p "${LOG_DIR}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "❌ Missing required command: $1" >&2
    exit 1
  fi
}

require_cmd docker
require_cmd poetry
require_cmd npm

echo "🚀 Starting Apollo web stack (working directory: ${ROOT_DIR})"
echo ""

echo "▶️  Bringing up shared Neo4j/Milvus infrastructure..."
docker compose -f "${INFRA_COMPOSE}" up -d

echo "ℹ️  Skipping Sophia API (no standalone server defined yet in logos_sophia)."

echo "▶️  Preparing Hermes API..."
(
  cd "${HERMES_DIR}"
  poetry install -E ml -E dev --sync >/dev/null
)
HERMES_LOG="${LOG_DIR}/hermes.log"
pkill -f "hermes.main:app" >/dev/null 2>&1 || true
(
  cd "${HERMES_DIR}"
  hermes_env=()
  for var in HERMES_LLM_PROVIDER HERMES_LLM_API_KEY HERMES_LLM_MODEL HERMES_LLM_BASE_URL; do
    if [[ -n "${!var:-}" ]]; then
      hermes_env+=("${var}=${!var}")
    fi
  done

  if ((${#hermes_env[@]} > 0)); then
    env "${hermes_env[@]}" nohup poetry run uvicorn hermes.main:app --host 0.0.0.0 --port 8080 \
      >"${HERMES_LOG}" 2>&1 &
  else
    nohup poetry run uvicorn hermes.main:app --host 0.0.0.0 --port 8080 \
      >"${HERMES_LOG}" 2>&1 &
  fi
)
echo "    Hermes running (logs: ${HERMES_LOG})"

echo "▶️  Preparing Apollo webapp..."
(
  cd "${APOLLO_WEB_DIR}"
  npm install >/dev/null
)
APOLLO_LOG="${LOG_DIR}/apollo-web.log"
pkill -f "vite" >/dev/null 2>&1 || true
(
  cd "${APOLLO_WEB_DIR}"
  nohup npm run dev -- --host 0.0.0.0 \
    >"${APOLLO_LOG}" 2>&1 &
)
echo "    Apollo web running (logs: ${APOLLO_LOG})"

echo ""
echo "✅ Stack ready! Quick reference:"
echo "   • Sophia API : (skipped)"
echo "   • Hermes API : http://localhost:8080"
echo "   • Apollo UI  : http://localhost:5173"
echo ""
echo "Logs stored in ${LOG_DIR}"
echo ""
echo "To stop everything manually:"
echo "   pkill -f 'logos_sophia.api:app'"
echo "   pkill -f 'hermes.main:app'"
echo "   pkill -f 'vite'"
echo "   docker compose -f ${INFRA_COMPOSE} down"
