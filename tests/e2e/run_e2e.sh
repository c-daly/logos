#!/bin/bash
# LOGOS E2E test runner script with convenience commands

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
STACK_DIR="${SCRIPT_DIR}/stack/logos"
DEFAULT_COMPOSE_FILE="${STACK_DIR}/docker-compose.test.yml"
DEFAULT_COMPOSE_ENV_FILE="${STACK_DIR}/.env.test"

COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-${DEFAULT_COMPOSE_FILE}}"
COMPOSE_ENV_FILE="${DOCKER_COMPOSE_ENV_FILE:-${DEFAULT_COMPOSE_ENV_FILE}}"

# Load stack environment variables to allow port overrides
if [ -f "${COMPOSE_ENV_FILE}" ]; then
    set -a
    # shellcheck source=/dev/null
    source "${COMPOSE_ENV_FILE}"
    set +a
fi

SOPHIA_PORT="${SOPHIA_PORT:-$(python3 -c "from logos_config.ports import get_repo_ports; print(get_repo_ports('sophia').api)")}"
HERMES_PORT="${HERMES_PORT:-$(python3 -c "from logos_config.ports import get_repo_ports; print(get_repo_ports('hermes').api)")}"
APOLLO_PORT="${APOLLO_PORT:-$(python3 -c "from logos_config.ports import get_repo_ports; print(get_repo_ports('apollo').api)")}"

NEO4J_HTTP_PORT="${NEO4J_HTTP_PORT:-7474}"
NEO4J_BOLT_PORT="${NEO4J_BOLT_PORT:-7687}"
MILVUS_PORT="${MILVUS_PORT:-19530}"
MILVUS_METRICS_PORT="${MILVUS_METRICS_PORT:-9091}"
MINIO_API_PORT="${MINIO_API_PORT:-9000}"
MINIO_CONSOLE_PORT="${MINIO_CONSOLE_PORT:-9001}"
ETCD_PORT="${ETCD_PORT:-2379}"

MILVUS_PUBLIC_HOST="${MILVUS_PUBLIC_HOST:-localhost}"
SOPHIA_URL="${SOPHIA_URL:-http://localhost:${SOPHIA_PORT}}"
HERMES_URL="${HERMES_URL:-http://localhost:${HERMES_PORT}}"
APOLLO_URL="${APOLLO_URL:-http://localhost:${APOLLO_PORT}}"
MILVUS_METRICS_URL="${MILVUS_METRICS_URL:-http://${MILVUS_PUBLIC_HOST}:${MILVUS_METRICS_PORT}/healthz}"

export SOPHIA_PORT HERMES_PORT APOLLO_PORT
export NEO4J_HTTP_PORT NEO4J_BOLT_PORT MILVUS_PORT MILVUS_METRICS_PORT MINIO_API_PORT MINIO_CONSOLE_PORT ETCD_PORT
export SOPHIA_URL HERMES_URL APOLLO_URL MILVUS_PUBLIC_HOST MILVUS_METRICS_URL

NEO4J_PUBLIC_HOST="${NEO4J_PUBLIC_HOST:-localhost}"
STACK_NEO4J_HOST="${NEO4J_HOST:-neo4j}"
if [ "${STACK_NEO4J_HOST}" != "${NEO4J_PUBLIC_HOST}" ]; then
    export STACK_NEO4J_HOST
fi
export NEO4J_HOST="${NEO4J_PUBLIC_HOST}"
NEO4J_URI="${NEO4J_URI:-bolt://${NEO4J_PUBLIC_HOST}:${NEO4J_BOLT_PORT}}"
export NEO4J_PUBLIC_HOST NEO4J_URI

# Ensure host-side processes connect via the public Milvus interface
STACK_MILVUS_HOST="${MILVUS_HOST:-milvus}"
if [ "${STACK_MILVUS_HOST}" != "${MILVUS_PUBLIC_HOST}" ]; then
    export STACK_MILVUS_HOST
    export MILVUS_HOST="${MILVUS_PUBLIC_HOST}"
fi

# Export container names for tests that use docker exec
export NEO4J_CONTAINER="${NEO4J_CONTAINER:-logos-phase2-test-neo4j}"
export MILVUS_CONTAINER="${MILVUS_CONTAINER:-logos-phase2-test-milvus}"

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
    local ports=("${SOPHIA_PORT}" "${HERMES_PORT}" "${APOLLO_PORT}")
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
    local ports=(
        "${NEO4J_HTTP_PORT}"
        "${NEO4J_BOLT_PORT}"
        "${MILVUS_PORT}"
        "${MILVUS_METRICS_PORT}"
        "${MINIO_API_PORT}"
        "${MINIO_CONSOLE_PORT}"
        "${ETCD_PORT}"
    )
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
    if curl -s -f "${MILVUS_METRICS_URL}" > /dev/null 2>&1; then
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
    MILVUS_HOST="${MILVUS_PUBLIC_HOST}" \
    MILVUS_PORT="${MILVUS_PORT}" \
    "${REPO_ROOT}/infra/init_milvus.sh"
    
    echo -e "${GREEN}✓ Test data seeded${NC}"
}

function check_status() {
    echo -e "${BLUE}Service Status:${NC}"
    compose ps
    
    echo ""
    echo -e "${BLUE}Health Checks:${NC}"
    
    echo -n "Neo4j (bolt://localhost:${NEO4J_BOLT_PORT}): "
    if compose exec -T neo4j cypher-shell -u neo4j -p neo4jtest "RETURN 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
    
    echo -n "Milvus (${MILVUS_PUBLIC_HOST}:${MILVUS_PORT}): "
    if curl -s -f "${MILVUS_METRICS_URL}" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
    fi
}

function run_test() {
    echo -e "${BLUE}Running test suite...${NC}"
    cd "${REPO_ROOT}"
    export SOPHIA_URL HERMES_URL APOLLO_URL
    export SOPHIA_PORT HERMES_PORT APOLLO_PORT
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
