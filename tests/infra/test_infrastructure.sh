#!/usr/bin/env bash

# Test script for LOGOS infrastructure
# Validates that the HCG development cluster is working correctly

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "=== LOGOS Infrastructure Test ==="
echo ""

# Test 1: Check if docker-compose config is valid
echo "Test 1: Validating docker-compose configuration..."
docker compose -f "${REPO_ROOT}/infra/docker-compose.hcg.dev.yml" config > /dev/null 2>&1
echo "✓ Docker-compose configuration is valid"
echo ""

# Test 2: Start services
echo "Test 2: Starting services..."
docker compose -f "${REPO_ROOT}/infra/docker-compose.hcg.dev.yml" up -d
echo "✓ Services started"
echo ""

# Test 3: Wait for Neo4j to be ready
echo "Test 3: Waiting for Neo4j to be ready..."
timeout 60 bash -c 'until docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "RETURN 1 AS test;" 2>/dev/null; do sleep 2; done' > /dev/null
echo "✓ Neo4j is ready"
echo ""

# Test 4: Load ontology
echo "Test 4: Loading core ontology..."
docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev < "${REPO_ROOT}/ontology/core_ontology.cypher" > /dev/null 2>&1
echo "✓ Ontology loaded"
echo ""

# Test 5: Verify constraints
echo "Test 5: Verifying Neo4j constraints..."
CONSTRAINT_COUNT=$(docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "SHOW CONSTRAINTS;" 2>/dev/null | grep -c "logos_")
if [ "$CONSTRAINT_COUNT" -ge 5 ]; then
  echo "✓ Found $CONSTRAINT_COUNT LOGOS constraints"
else
  echo "✗ Expected at least 5 constraints, found $CONSTRAINT_COUNT"
  exit 1
fi
echo ""

# Test 6: Verify indexes
echo "Test 6: Verifying Neo4j indexes..."
INDEX_COUNT=$(docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev "SHOW INDEXES;" 2>/dev/null | grep -c "logos_")
if [ "$INDEX_COUNT" -ge 7 ]; then
  echo "✓ Found $INDEX_COUNT LOGOS indexes"
else
  echo "✗ Expected at least 7 indexes, found $INDEX_COUNT"
  exit 1
fi
echo ""

# Test 7: Verify APOC is loaded
echo "Test 7: Verifying APOC plugin..."
APOC_COUNT=$(docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'apoc' RETURN count(name) AS count;" 2>/dev/null | tail -1)
if [ "$APOC_COUNT" -gt 0 ]; then
  echo "✓ APOC loaded with $APOC_COUNT procedures"
else
  echo "✗ APOC not loaded"
  exit 1
fi
echo ""

# Test 8: Check Milvus is running
echo "Test 8: Checking Milvus status..."
docker exec logos-hcg-milvus ps aux | grep milvus > /dev/null
echo "✓ Milvus is running"
echo ""

# Test 9: Initialize and verify Milvus collections
echo "Test 9: Initializing Milvus collections..."
python3 "${REPO_ROOT}/infra/init_milvus_collections.py" --host localhost --port 19530 > /dev/null 2>&1
echo "✓ Milvus collections initialized"
echo ""

# Test 10: Verify Milvus collections exist
echo "Test 10: Verifying Milvus collections..."
COLLECTION_COUNT=$(python3 -c "
from pymilvus import connections, utility
connections.connect(alias='default', host='localhost', port='19530')
collections = ['hcg_entity_embeddings', 'hcg_concept_embeddings', 'hcg_state_embeddings', 'hcg_process_embeddings']
count = sum(1 for c in collections if utility.has_collection(c))
connections.disconnect('default')
print(count)
" 2>/dev/null)
if [ "$COLLECTION_COUNT" -eq 4 ]; then
  echo "✓ Found all 4 Milvus collections"
else
  echo "✗ Expected 4 collections, found $COLLECTION_COUNT"
  exit 1
fi
echo ""

# Test 11: Verify volumes exist
echo "Test 11: Verifying data volumes..."
VOLUMES=$(docker volume ls | grep -c "infra_")
if [ "$VOLUMES" -ge 4 ]; then
  echo "✓ Found $VOLUMES data volumes"
else
  echo "✗ Expected at least 4 volumes, found $VOLUMES"
  exit 1
fi
echo ""

# Test 12: Verify network exists
echo "Test 12: Verifying network..."
docker network inspect infra_logos-hcg-dev-net > /dev/null 2>&1
echo "✓ Network infra_logos-hcg-dev-net exists"
echo ""

echo "=== All Tests Passed ==="
echo ""
echo "Infrastructure is ready for development!"
echo "- Neo4j Browser: http://localhost:7474 (neo4j/logosdev)"
echo "- Neo4j Bolt: bolt://localhost:7687"
echo "- Milvus gRPC: localhost:19530"
echo "- Milvus Collections: 4 initialized (Entity, Concept, State, Process)"
echo ""
echo "To stop the cluster:"
echo "  docker compose -f infra/docker-compose.hcg.dev.yml down"
echo ""
echo "To remove all data:"
echo "  docker compose -f infra/docker-compose.hcg.dev.yml down -v"
