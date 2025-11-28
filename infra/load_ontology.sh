#!/usr/bin/env bash

# LOGOS HCG Ontology Loader
# Loads core ontology constraints, indexes, and concepts into Neo4j
# See Project LOGOS spec: Section 4.1 (Core Ontology and Data Model)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ONTOLOGY_FILE="${REPO_ROOT}/ontology/core_ontology.cypher"

# Configuration
NEO4J_CONTAINER="${NEO4J_CONTAINER:-logos-hcg-neo4j}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4jtest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Neo4j is available
check_neo4j() {
    print_info "Checking Neo4j connectivity..."
    if ! docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" "RETURN 1 AS test;" > /dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Function to wait for Neo4j to be ready
wait_for_neo4j() {
    print_info "Waiting for Neo4j to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if check_neo4j; then
            print_info "Neo4j is ready!"
            return 0
        fi
        
        if [ $attempt -eq 1 ]; then
            print_warn "Neo4j not ready yet, waiting... (attempt $attempt/$max_attempts)"
        elif [ $((attempt % 5)) -eq 0 ]; then
            print_warn "Still waiting for Neo4j... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 2
        ((attempt++))
    done
    
    print_error "Neo4j did not become ready within the timeout period"
    return 1
}

# Function to load ontology
load_ontology() {
    print_info "Loading core ontology from ${ONTOLOGY_FILE}..."
    
    if [ ! -f "${ONTOLOGY_FILE}" ]; then
        print_error "Ontology file not found: ${ONTOLOGY_FILE}"
        return 1
    fi
    
    if docker exec -i "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" < "${ONTOLOGY_FILE}" > /tmp/load_output.txt 2>&1; then
        print_info "Ontology loaded successfully!"
        
        # Show summary of what was created
        if grep -q "Added" /tmp/load_output.txt || grep -q "Created" /tmp/load_output.txt; then
            print_info "Summary:"
            grep -E "Added|Created|Set" /tmp/load_output.txt | head -10
        fi
        
        return 0
    else
        print_error "Failed to load ontology"
        cat /tmp/load_output.txt
        return 1
    fi
}

# Function to verify constraints
verify_constraints() {
    print_info "Verifying constraints..."
    
    local constraint_count=$(docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "SHOW CONSTRAINTS;" 2>/dev/null | grep -c "logos_" || echo "0")
    
    if [ "$constraint_count" -ge 5 ]; then
        print_info "✓ Found ${constraint_count} LOGOS constraints"
        return 0
    else
        print_warn "Expected at least 5 constraints, found ${constraint_count}"
        return 1
    fi
}

# Function to verify indexes
verify_indexes() {
    print_info "Verifying indexes..."
    
    local index_count=$(docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "SHOW INDEXES;" 2>/dev/null | grep -c "logos_" || echo "0")
    
    if [ "$index_count" -ge 3 ]; then
        print_info "✓ Found ${index_count} LOGOS indexes"
        return 0
    else
        print_warn "Expected at least 3 indexes, found ${index_count}"
        return 1
    fi
}

# Function to verify concepts
verify_concepts() {
    print_info "Verifying concepts..."
    
    local concept_count=$(docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "MATCH (c:Concept) RETURN count(c) AS count;" 2>/dev/null | tail -1 | tr -d '"')
    
    if [ "$concept_count" -ge 14 ]; then
        print_info "✓ Found ${concept_count} concepts loaded"
        return 0
    else
        print_warn "Expected at least 14 concepts, found ${concept_count}"
        return 1
    fi
}

# Main execution
main() {
    echo ""
    echo "==================================="
    echo "LOGOS Core Ontology Loader"
    echo "==================================="
    echo ""
    
    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^${NEO4J_CONTAINER}$"; then
        print_error "Neo4j container '${NEO4J_CONTAINER}' not found"
        print_info "Start the HCG cluster first:"
        print_info "  docker compose -f infra/docker-compose.hcg.dev.yml up -d"
        exit 1
    fi
    
    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${NEO4J_CONTAINER}$"; then
        print_error "Neo4j container '${NEO4J_CONTAINER}' is not running"
        print_info "Start the container first:"
        print_info "  docker compose -f infra/docker-compose.hcg.dev.yml up -d"
        exit 1
    fi
    
    # Wait for Neo4j to be ready
    if ! wait_for_neo4j; then
        print_error "Failed to connect to Neo4j"
        print_info "Check the container logs:"
        print_info "  docker logs ${NEO4J_CONTAINER}"
        exit 1
    fi
    
    # Load the ontology
    if ! load_ontology; then
        print_error "Ontology loading failed"
        exit 1
    fi
    
    echo ""
    print_info "Verifying ontology..."
    echo ""
    
    # Verify what was loaded
    local verification_failed=0
    
    if ! verify_constraints; then
        verification_failed=1
    fi
    
    if ! verify_indexes; then
        verification_failed=1
    fi
    
    if ! verify_concepts; then
        verification_failed=1
    fi
    
    echo ""
    
    if [ $verification_failed -eq 0 ]; then
        echo "==================================="
        print_info "✓ Ontology loaded and verified successfully!"
        echo "==================================="
        echo ""
        print_info "Access Neo4j Browser at: http://localhost:7474"
        print_info "  Username: ${NEO4J_USER}"
        print_info "  Password: ${NEO4J_PASSWORD}"
        echo ""
        print_info "Try running queries like:"
        print_info '  MATCH (c:Concept) RETURN c.name ORDER BY c.name;'
        print_info '  SHOW CONSTRAINTS;'
        print_info '  SHOW INDEXES;'
        echo ""
    else
        echo "==================================="
        print_warn "Ontology loaded but verification had warnings"
        echo "==================================="
        echo ""
        print_info "The ontology may have been loaded previously"
        print_info "Check the Neo4j Browser for details: http://localhost:7474"
        echo ""
    fi
    
    # Cleanup
    rm -f /tmp/load_output.txt
}

# Run main function
main "$@"
