#!/bin/bash
# LOGOS E2E test runner script with convenience commands

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
STACK_DIR="${SCRIPT_DIR}/stack/logos"
COMPOSE_FILE="${STACK_DIR}/docker-compose.test.yml"
COMPOSE_ENV_FILE="${STACK_DIR}/.env.test"

# Export container names for tests that use docker exec
export NEO4J_CONTAINER="logos-phase2-test-neo4j"

START_SERVICES_SCRIPT="${REPO_ROOT}/scripts/start_services.sh"
SHOULD_START_APP_SERVICES=0
if [[ "${RUN_M4_E2E:-0}" == "1" || "${RUN_P2_E2E:-0}" == "1" ]]; then
    SHOULD_START_APP_SERVICES=1
fi
APP_SERVICES_STARTED=0
APP_SERVICE_TRAP_SET=0

compose() {
    docker compose \
        --env-file "${COMPOSE_ENV_FILE}" \
        -f "${COMPOSE_FILE}" \
        "$@"
}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

start_application_services() {
    if [ "$SHOULD_START_APP_SERVICES" -eq 0 ]; then
        return 0
    fi

    if [ ! -x "$START_SERVICES_SCRIPT" ]; then
        echo -e "${RED}Application service script missing: ${START_SERVICES_SCRIPT}${NC}"
        exit 1
    fi

    echo -e "${BLUE}Starting Sophia/Hermes/Apollo for E2E coverage...${NC}"
    "$START_SERVICES_SCRIPT" start
    APP_SERVICES_STARTED=1

    if [ "$APP_SERVICE_TRAP_SET" -eq 0 ]; then
        trap stop_application_services EXIT
        APP_SERVICE_TRAP_SET=1
    fi
}

stop_application_services() {
    if [ "$APP_SERVICES_STARTED" -eq 0 ]; then
        return 0
    fi

    echo -e "${BLUE}Stopping Sophia/Hermes/Apollo started by this run...${NC}"
    if [ -x "$START_SERVICES_SCRIPT" ]; then
        "$START_SERVICES_SCRIPT" stop || true
    fi
    APP_SERVICES_STARTED=0
}

function print_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  test       Run the full test suite (default)"
    echo "  up         Start services only"
    echo "  down       Stop and remove services"
    echo "  logs       Show service logs"
    echo "  seed       Seed test data (load ontology)"
    echo "  status     Check service status"
    echo "  clean      Clean up everything including volumes"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Run full test"
    echo "  $0 up              # Start services for manual testing"
    echo "  $0 logs            # View logs"
    echo "  $0 down            # Stop services"
}

function stop_host_processes_on_ports() {
    local ports=("8001" "8002" "8003")
    for port in "${ports[@]}"; do
        local pids=""
        if command -v lsof >/dev/null 2>&1; then
            pids=$(lsof -ti tcp:"${port}" 2>/dev/null || true)
        elif command -v fuser >/dev/null 2>&1; then
            pids=$(fuser "${port}"/tcp 2>/dev/null || true)
        fi
        if [ -n "$pids" ]; then
            echo -e "${YELLOW}Killing processes using port ${port}...${NC}"
            xargs kill -9 <<<"$pids" 2>/dev/null || true
        fi
    done
}

function stop_containers_on_ports() {
    local ports=("7474" "7687" "19530" "9091" "9000" "9001" "2379")
    for port in "${ports[@]}"; do
        local container=$(docker ps --format '{{.ID}}' --filter "publish=${port}" 2>/dev/null)
        if [ -n "$container" ]; then
            echo -e "${YELLOW}Stopping container using port ${port}...${NC}"
            docker stop "$container" 2>/dev/null || true
        fi
    done
}

function start_services() {
    echo -e "${BLUE}Stopping any containers using test ports...${NC}"
    stop_host_processes_on_ports
    stop_containers_on_ports
    compose down 2>/dev/null || true
    
    echo -e "${BLUE}Starting E2E test services...${NC}"
    compose up -d
    
    echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
    sleep 5
    
    # Check Neo4j
    echo -n "Neo4j: "
    if compose exec -T neo4j cypher-shell -u neo4j -p neo4jtest "RETURN 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ready${NC}"
    else
        echo -e "${RED}✗ Not ready${NC}"
    fi
    
    # Check Milvus
    echo -n "Milvus: "
    if curl -s -f http://localhost:9091/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Ready${NC}"
    else
        echo -e "${RED}✗ Not ready${NC}"
    fi
}

function stop_services() {
    echo -e "${BLUE}Stopping E2E test services...${NC}"
    compose down
    echo -e "${GREEN}Services stopped${NC}"
}

function show_logs() {
    compose logs "$@"
}

function seed_data() {
    echo -e "${BLUE}Seeding test data...${NC}"
    
    # Load ontology using the infra script
    echo -e "${YELLOW}Loading ontology...${NC}"
    NEO4J_CONTAINER="${NEO4J_CONTAINER}" \
    NEO4J_USER=neo4j \
    NEO4J_PASSWORD=neo4jtest \
    "${REPO_ROOT}/infra/load_ontology.sh"
    
    # Initialize Milvus collections
    echo -e "${YELLOW}Initializing Milvus collections...${NC}"
    MILVUS_HOST=localhost \
    MILVUS_PORT=19530 \
    "${REPO_ROOT}/infra/init_milvus.sh"
    
    echo -e "${GREEN}✓ Test data seeded${NC}"
}

function check_status() {
    echo -e "${BLUE}Service Status:${NC}"
    compose ps
    
    echo ""
    echo -e "${BLUE}Health Checks:${NC}"
    
    echo -n "Neo4j (bolt://localhost:7687): "
    if compose exec -T neo4j cypher-shell -u neo4j -p neo4jtest "RETURN 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
    
    echo -n "Milvus (localhost:19530): "
    if curl -s -f http://localhost:9091/healthz > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
}

function run_test() {
    echo -e "${BLUE}Running test suite...${NC}"
    cd "${REPO_ROOT}"
    start_application_services

    set +e
    NEO4J_CONTAINER="${NEO4J_CONTAINER}" poetry run pytest -v tests/
    local test_status=$?
    set -e

    stop_application_services
    return $test_status
}

function clean_all() {
    echo -e "${YELLOW}Cleaning up all E2E test resources...${NC}"
    compose down -v
    echo -e "${GREEN}Cleanup complete${NC}"
}

# Main command handling
COMMAND="${1:-test}"

case "$COMMAND" in
    test)
        start_services
        seed_data
        run_test
        ;;
    up)
        start_services
        ;;
    down)
        stop_services
        ;;
    logs)
        shift
        show_logs "$@"
        ;;
    seed)
        seed_data
        ;;
    status)
        check_status
        ;;
    clean)
        clean_all
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
