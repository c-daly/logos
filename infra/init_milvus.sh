#!/usr/bin/env bash
# LOGOS Milvus Collection Initialization Wrapper
# Initializes Milvus collections for HCG embeddings
# See Section 4.2 (Vector Integration) and Section 5.2 (HCG Development Cluster)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
MILVUS_HOST="${MILVUS_HOST:-localhost}"
MILVUS_PORT="${MILVUS_PORT:-19530}"
EMBEDDING_DIM="${EMBEDDING_DIM:-384}"

echo "=== LOGOS Milvus Collection Initialization ==="
echo ""

# Check if Milvus is running
echo "Checking if Milvus is accessible at ${MILVUS_HOST}:${MILVUS_PORT}..."
if ! timeout 5 bash -c "echo > /dev/tcp/${MILVUS_HOST}/${MILVUS_PORT}" 2>/dev/null; then
    echo "✗ Error: Cannot connect to Milvus at ${MILVUS_HOST}:${MILVUS_PORT}"
    echo ""
    echo "Please ensure Milvus is running:"
    echo "  docker compose -f infra/docker-compose.hcg.dev.yml up -d"
    exit 1
fi
echo "✓ Milvus is accessible"
echo ""

# Run Python script
python3 "${SCRIPT_DIR}/init_milvus_collections.py" \
    --host "${MILVUS_HOST}" \
    --port "${MILVUS_PORT}" \
    --embedding-dim "${EMBEDDING_DIM}" \
    "$@"
