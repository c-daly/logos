#!/usr/bin/env bash
#
# Start LOGOS services (Sophia, Hermes, Apollo)
#
# Usage:
#   ./start_services.sh [start|stop|status]
#
# Services:
#   - Sophia (port 8001): Cognitive core
#   - Hermes (port 8002): Language/embedding service
#   - Apollo API (port 8003): UI/command layer
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGOS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_DIR="$SCRIPT_DIR/.pids"

# Allow port overrides from environment (default to standardized values)
SOPHIA_PORT="${SOPHIA_PORT:-8001}"
HERMES_PORT="${HERMES_PORT:-8002}"
APOLLO_PORT="${APOLLO_PORT:-8003}"

if [ -z "${HERMES_LLM_PROVIDER:-}" ]; then
    HERMES_LLM_PROVIDER="openai"
fi

if [ -z "${HERMES_LLM_API_KEY:-}" ] && [ -n "${OPENAI_API_KEY:-}" ]; then
    HERMES_LLM_API_KEY="${OPENAI_API_KEY}"
fi

export HERMES_LLM_PROVIDER
if [ -n "${HERMES_LLM_API_KEY:-}" ]; then
    export HERMES_LLM_API_KEY
fi

# Service configuration
declare -A SERVICES=(
    [sophia]="${SOPHIA_PORT}:sophia:$LOGOS_ROOT/../sophia"
    [hermes]="${HERMES_PORT}:hermes:$LOGOS_ROOT/../hermes"
    [apollo]="${APOLLO_PORT}:apollo:$LOGOS_ROOT/../apollo"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if a port is in use
check_port() {
    local port=$1
    if ss -tuln 2>/dev/null | grep -q ":$port "; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Get service details
get_service_details() {
    local service=$1
    local details="${SERVICES[$service]}"
    local port="${details%%:*}"
    local remaining="${details#*:}"
    local module="${remaining%%:*}"
    local repo_path="${remaining#*:}"
    
    echo "$port:$module:$repo_path"
}

# Start a service
start_service() {
    local service=$1
    local details
    details=$(get_service_details "$service")
    
    local port="${details%%:*}"
    local remaining="${details#*:}"
    local module="${remaining%%:*}"
    local repo_path="${remaining#*:}"
    
    local pid_file="$PID_DIR/$service.pid"
    
    # Check if already running
    if [ -f "$pid_file" ] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
        log_warn "$service already running (PID: $(cat "$pid_file"))"
        return 0
    fi
    
    # Check if port is in use
    if check_port "$port"; then
        log_error "Port $port already in use (needed for $service)"
        return 1
    fi
    
    # Check if repository exists
    if [ ! -d "$repo_path" ]; then
        log_error "Repository not found: $repo_path"
        return 1
    fi
    
    log_info "Starting $service on port $port..."
    
    local milvus_host_for_services="${MILVUS_PUBLIC_HOST:-${MILVUS_HOST:-localhost}}"
    local milvus_port_for_services="${MILVUS_PORT:-19530}"

    # Start service based on type
    case "$service" in
        sophia)
            (cd "$repo_path" && \
             NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}" \
             NEO4J_USER="${NEO4J_USER:-neo4j}" \
             NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4jtest}" \
             MILVUS_HOST="${milvus_host_for_services}" \
             MILVUS_PORT="${milvus_port_for_services}" \
             SOPHIA_API_TOKEN="${SOPHIA_API_KEY:-test-token-12345}" \
             poetry run uvicorn sophia.api.app:app --host 0.0.0.0 --port "$port" \
             > "$PID_DIR/$service.log" 2>&1 & \
             echo $! > "$pid_file")
            ;;
        hermes)
            (cd "$repo_path" && \
             MILVUS_HOST="${milvus_host_for_services}" \
             MILVUS_PORT="${milvus_port_for_services}" \
             HERMES_PORT="$port" poetry run hermes \
             > "$PID_DIR/$service.log" 2>&1 & \
             echo $! > "$pid_file")
            ;;
        apollo)
            (cd "$repo_path" && \
             NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}" \
             NEO4J_USER="${NEO4J_USER:-neo4j}" \
             NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4jtest}" \
             SOPHIA_URL="${SOPHIA_URL:-http://localhost:${SOPHIA_PORT}}" \
             HERMES_URL="${HERMES_URL:-http://localhost:${HERMES_PORT}}" \
             APOLLO_PORT="$port" poetry run apollo-api \
             > "$PID_DIR/$service.log" 2>&1 & \
             echo $! > "$pid_file")
            ;;
    esac
    
    # Wait for service to start
    local retries=${SERVICE_START_RETRIES:-30}
    local delay=${SERVICE_START_DELAY:-1}
    for i in $(seq 1 $retries); do
        sleep "$delay"
        if check_port "$port"; then
            log_success "$service started successfully (PID: $(cat "$pid_file"))"
            return 0
        fi
    done

    local waited=$((retries * delay))
    log_error "$service failed to start within ${waited}s. Check $PID_DIR/$service.log"
    return 1
}

# Stop a service
stop_service() {
    local service=$1
    local pid_file="$PID_DIR/$service.pid"
    
    if [ ! -f "$pid_file" ]; then
        log_warn "$service is not running (no PID file)"
        return 0
    fi
    
    local pid
    pid=$(cat "$pid_file")
    
    if ! kill -0 "$pid" 2>/dev/null; then
        log_warn "$service is not running (stale PID: $pid)"
        rm -f "$pid_file"
        return 0
    fi
    
    log_info "Stopping $service (PID: $pid)..."
    kill "$pid" 2>/dev/null || true
    
    # Wait for process to terminate
    local retries=10
    for i in $(seq 1 $retries); do
        if ! kill -0 "$pid" 2>/dev/null; then
            rm -f "$pid_file"
            log_success "$service stopped"
            return 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    log_warn "Force killing $service..."
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$pid_file"
    log_success "$service force stopped"
}

# Get service status
status_service() {
    local service=$1
    local details
    details=$(get_service_details "$service")
    
    local port="${details%%:*}"
    local pid_file="$PID_DIR/$service.pid"
    
    printf "%-10s " "$service:"
    
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            if check_port "$port"; then
                echo -e "${GREEN}running${NC} (PID: $pid, port: $port)"
            else
                echo -e "${YELLOW}running but not listening${NC} (PID: $pid, port: $port expected)"
            fi
        else
            echo -e "${RED}stopped${NC} (stale PID: $pid)"
        fi
    else
        if check_port "$port"; then
            echo -e "${YELLOW}unknown process on port${NC} (port: $port)"
        else
            echo -e "${RED}stopped${NC}"
        fi
    fi
}

# Main commands
cmd_start() {
    mkdir -p "$PID_DIR"
    
    # Start OTel observability stack
    local otel_compose="$LOGOS_ROOT/infra/docker-compose.otel.yml"
    if [ -f "$otel_compose" ]; then
        log_info "Starting OTel observability stack..."
        docker compose -f "$otel_compose" up -d 2>/dev/null &&             log_success "OTel stack started (Collector, Tempo, Grafana)" ||             log_warn "OTel stack failed to start (services will run without tracing)"
    fi
    
    log_info "Starting LOGOS services..."
    
    local failed=0
    for service in "${!SERVICES[@]}"; do
        start_service "$service" || ((failed++))
    done
    
    echo ""
    log_info "Service status:"
    for service in "${!SERVICES[@]}"; do
        status_service "$service"
    done
    
    if [ $failed -eq 0 ]; then
        echo ""
        log_success "All services started successfully"
        return 0
    else
        echo ""
        log_error "$failed service(s) failed to start"
        return 1
    fi
}

cmd_stop() {
    log_info "Stopping LOGOS services..."
    
    for service in "${!SERVICES[@]}"; do
        stop_service "$service"
    done
    
    # Stop OTel observability stack
    local otel_compose="$LOGOS_ROOT/infra/docker-compose.otel.yml"
    if [ -f "$otel_compose" ]; then
        log_info "Stopping OTel observability stack..."
        docker compose -f "$otel_compose" down 2>/dev/null &&             log_success "OTel stack stopped" ||             log_warn "OTel stack stop failed"
    fi
    
    log_success "All services stopped"
}

cmd_status() {
    log_info "LOGOS services status:"
    for service in "${!SERVICES[@]}"; do
        status_service "$service"
    done
}

# Usage
usage() {
    cat <<EOF
Usage: $0 [COMMAND]

Commands:
    start   - Start all services (Sophia, Hermes, Apollo)
    stop    - Stop all services
    status  - Show service status
    help    - Show this help message

Examples:
    $0 start
    $0 status
    $0 stop

Services:
    - Sophia (port 8001): Cognitive core
    - Hermes (port 8002): Language/embedding service
    - Apollo (port 8003): UI/command layer

Prerequisites:
        - Infrastructure must be running (Neo4j, Milvus)
            Run: cd ../infra && docker compose -f docker-compose.hcg.dev.yml up -d
            Or:  ../tests/e2e/run_e2e.sh up
        - OTel stack (Collector, Tempo, Grafana) is started automatically

    - Poetry environments must be set up in each repository
EOF
}

# Main
main() {
    local command="${1:-help}"
    
    case "$command" in
        start)
            cmd_start
            ;;
        stop)
            cmd_stop
            ;;
        status)
            cmd_status
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

main "$@"
