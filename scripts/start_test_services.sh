#!/usr/bin/env bash
#
# Start/stop test infrastructure (Neo4j, Milvus)
#
# Usage:
#   ./scripts/start_test_services.sh [start|stop|status|restart]
#
# This manages the docker-compose.test.yml stack for integration testing.
# Unlike start_services.sh (which manages app services), this only handles
# the database/vector store infrastructure.
#
# Examples:
#   ./scripts/start_test_services.sh           # Start services
#   ./scripts/start_test_services.sh start     # Start services  
#   ./scripts/start_test_services.sh stop      # Stop and remove containers
#   ./scripts/start_test_services.sh status    # Check service health
#   ./scripts/start_test_services.sh restart   # Stop then start
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker-compose.test.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default ports (can be overridden via environment)
NEO4J_BOLT_PORT="${NEO4J_BOLT_PORT:-7687}"
MILVUS_PORT="${MILVUS_PORT:-19530}"

check_docker() {
    if ! command -v docker &>/dev/null; then
        echo -e "${RED}Error: docker is not installed${NC}"
        exit 1
    fi
    if ! docker info &>/dev/null; then
        echo -e "${RED}Error: docker daemon is not running${NC}"
        exit 1
    fi
}

wait_for_neo4j() {
    local max_attempts=30
    local attempt=1
    
    echo -n "Waiting for Neo4j..."
    while [ $attempt -le $max_attempts ]; do
        if docker exec logos-phase2-test-neo4j cypher-shell -u neo4j -p testpassword "RETURN 1" &>/dev/null; then
            echo -e " ${GREEN}ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo -e " ${RED}timeout${NC}"
    return 1
}

wait_for_milvus() {
    local max_attempts=30
    local attempt=1
    
    echo -n "Waiting for Milvus..."
    while [ $attempt -le $max_attempts ]; do
        if curl -sf "http://localhost:${MILVUS_PORT}/healthz" &>/dev/null; then
            echo -e " ${GREEN}ready${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo -e " ${RED}timeout${NC}"
    return 1
}

start_services() {
    echo -e "${GREEN}Starting test infrastructure...${NC}"
    
    cd "$REPO_ROOT"
    docker compose -f "$COMPOSE_FILE" up -d
    
    echo ""
    wait_for_neo4j
    wait_for_milvus
    
    echo ""
    echo -e "${GREEN}Test infrastructure is ready${NC}"
    echo "  Neo4j:  bolt://localhost:${NEO4J_BOLT_PORT}"
    echo "  Milvus: localhost:${MILVUS_PORT}"
}

stop_services() {
    echo -e "${YELLOW}Stopping test infrastructure...${NC}"
    
    cd "$REPO_ROOT"
    docker compose -f "$COMPOSE_FILE" down -v
    
    echo -e "${GREEN}Test infrastructure stopped${NC}"
}

show_status() {
    echo "Test Infrastructure Status:"
    echo "============================"
    
    cd "$REPO_ROOT"
    
    # Check Neo4j - use docker health status
    local neo4j_status
    neo4j_status=$(docker inspect --format='{{.State.Health.Status}}' logos-phase2-test-neo4j 2>/dev/null || echo "stopped")
    case "$neo4j_status" in
        healthy)
            echo -e "  Neo4j:  ${GREEN}healthy${NC} (bolt://localhost:${NEO4J_BOLT_PORT})"
            ;;
        starting)
            echo -e "  Neo4j:  ${YELLOW}starting${NC}"
            ;;
        *)
            echo -e "  Neo4j:  ${RED}${neo4j_status}${NC}"
            ;;
    esac
    
    # Check Milvus - use docker health status
    local milvus_status
    milvus_status=$(docker inspect --format='{{.State.Health.Status}}' logos-phase2-test-milvus 2>/dev/null || echo "stopped")
    case "$milvus_status" in
        healthy)
            echo -e "  Milvus: ${GREEN}healthy${NC} (localhost:${MILVUS_PORT})"
            ;;
        starting)
            echo -e "  Milvus: ${YELLOW}starting${NC}"
            ;;
        *)
            echo -e "  Milvus: ${RED}${milvus_status}${NC}"
            ;;
    esac
    
    echo ""
    docker compose -f "$COMPOSE_FILE" ps 2>/dev/null || true
}

# Main
check_docker

case "${1:-start}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    status)
        show_status
        ;;
    restart)
        stop_services
        echo ""
        start_services
        ;;
    *)
        echo "Usage: $0 [start|stop|status|restart]"
        exit 1
        ;;
esac
