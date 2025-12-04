#!/bin/bash
# Collect test metrics across all LOGOS repos
# Usage: ./scripts/collect-test-metrics.sh [command] [output-dir]
#
# Commands:
#   collect    Run tests and collect metrics (default)
#   up         Start required services only
#   down       Stop services
#   status     Check service status
#   help       Show this help
#
# Outputs JSON with pass/fail/skip/coverage for each repo
# Designed to be run periodically to track Phase 2.5 progress

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGOS_ROOT="$(dirname "$SCRIPT_DIR")"
INFRA_DIR="$LOGOS_ROOT/infra"
COMPOSE_FILE="$INFRA_DIR/docker-compose.hcg.dev.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service configuration
NEO4J_PORT="${NEO4J_PORT:-7687}"
NEO4J_HTTP_PORT="${NEO4J_HTTP_PORT:-7474}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4jtest}"
MILVUS_PORT="${MILVUS_PORT:-19530}"

# Container names from docker-compose.hcg.dev.yml
NEO4J_CONTAINER="${NEO4J_CONTAINER:-logos-hcg-neo4j}"
MILVUS_CONTAINER="${MILVUS_CONTAINER:-logos-hcg-milvus}"

# Track if we started services
SERVICES_STARTED=0

#=============================================================================
# Service Management
#=============================================================================

compose() {
    docker compose -f "$COMPOSE_FILE" "$@"
}

check_neo4j() {
    docker exec "$NEO4J_CONTAINER" cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "RETURN 1" > /dev/null 2>&1
}

check_milvus() {
    curl -s -f "http://localhost:9091/healthz" > /dev/null 2>&1
}

wait_for_services() {
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        local neo4j_ok=0
        local milvus_ok=0
        
        check_neo4j && neo4j_ok=1
        check_milvus && milvus_ok=1
        
        if [ $neo4j_ok -eq 1 ] && [ $milvus_ok -eq 1 ]; then
            echo -e "${GREEN}All services ready${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    echo ""
    echo -e "${RED}Services failed to become healthy${NC}"
    return 1
}

start_services() {
    echo -e "${BLUE}Starting test infrastructure...${NC}"
    
    # Check if already running
    if check_neo4j && check_milvus; then
        echo -e "${GREEN}Services already running${NC}"
        return 0
    fi
    
    # Start services (only neo4j and milvus-standalone exist in this compose file)
    compose up -d neo4j milvus-standalone
    SERVICES_STARTED=1
    
    wait_for_services
}

stop_services() {
    if [ "$SERVICES_STARTED" -eq 1 ]; then
        echo -e "${BLUE}Stopping services started by this script...${NC}"
        compose down
        SERVICES_STARTED=0
    fi
}

show_status() {
    echo -e "${BLUE}Service Status:${NC}"
    echo -n "  Neo4j:  "
    if check_neo4j; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Not running${NC}"
    fi
    
    echo -n "  Milvus: "
    if check_milvus; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Not running${NC}"
    fi
}

# Cleanup on exit
cleanup() {
    stop_services
}
trap cleanup EXIT

print_usage() {
    echo "Usage: $0 [command] [output-dir]"
    echo ""
    echo "Commands:"
    echo "  collect    Run tests and collect metrics (default)"
    echo "  up         Start required services only"
    echo "  down       Stop services"
    echo "  status     Check service status"
    echo "  help       Show this help"
    echo ""
    echo "Examples:"
    echo "  $0                           # Collect metrics (auto-starts services)"
    echo "  $0 up                        # Start services for manual testing"
    echo "  $0 collect /tmp/metrics      # Collect to custom directory"
    echo "  $0 down                      # Stop services"
}

#=============================================================================
# Metrics Collection
#=============================================================================

run_collection() {
    local OUTPUT_DIR="${1:-$LOGOS_ROOT/docs/evidence/testing}"
    local DATE=$(date +%Y-%m-%d)
    local TIME=$(date +%H%M%S)
    local TIMESTAMP=$(date -Iseconds)

    echo "=========================================="
    echo "LOGOS Test Metrics Collection"
    echo "Date: $DATE"
    echo "=========================================="

    # Start services if needed
    start_services

    mkdir -p "$OUTPUT_DIR"

    # Find next sequence number for today
    local SEQ=1
    while [[ -f "$OUTPUT_DIR/metrics-${DATE}-${SEQ}.json" ]]; do
        ((SEQ++))
    done

    # Initialize JSON
    local OUTPUT_FILE="$OUTPUT_DIR/metrics-${DATE}-${SEQ}.json"
    local TMP_FILE=$(mktemp)

    cat > "$TMP_FILE" << EOF
{
  "date": "$DATE",
  "timestamp": "$TIMESTAMP",
  "phase": "2.5",
  "repos": {
EOF

    # Collect metrics for each repo
    {
        collect_repo_metrics "sophia" "$LOGOS_ROOT/../sophia" \
            "RUN_SOPHIA_INTEGRATION=1 RUN_NEO4J_SHACL=1 RUN_MEDIA_INTEGRATION=1 NEO4J_URI=bolt://localhost:$NEO4J_PORT NEO4J_USER=$NEO4J_USER NEO4J_PASSWORD=$NEO4J_PASSWORD"
        
        collect_repo_metrics "hermes" "$LOGOS_ROOT/../hermes" \
            "MILVUS_HOST=localhost MILVUS_PORT=$MILVUS_PORT ML_AVAILABLE=1 NLP_AVAILABLE=1"
        
        collect_repo_metrics "apollo" "$LOGOS_ROOT/../apollo" \
            "RUN_INTEGRATION_TESTS=1 NEO4J_URI=bolt://localhost:$NEO4J_PORT NEO4J_USER=$NEO4J_USER NEO4J_PASSWORD=$NEO4J_PASSWORD"
        
        collect_repo_metrics "talos" "$LOGOS_ROOT/../talos" \
            ""
        
        collect_repo_metrics "logos" "$LOGOS_ROOT" \
            "NEO4J_URI=bolt://localhost:$NEO4J_PORT NEO4J_USER=$NEO4J_USER NEO4J_PASSWORD=$NEO4J_PASSWORD RUN_NEO4J_SHACL=1"
    } >> "$TMP_FILE"

    # Remove trailing comma and close JSON
    sed -i '$ s/,$//' "$TMP_FILE"

    cat >> "$TMP_FILE" << EOF
  }
}
EOF

    # Pretty print and save
    python3 -m json.tool "$TMP_FILE" > "$OUTPUT_FILE" 2>/dev/null || mv "$TMP_FILE" "$OUTPUT_FILE"
    rm -f "$TMP_FILE"

    echo ""
    echo "=========================================="
    echo -e "${GREEN}Metrics saved to: $OUTPUT_FILE${NC}"
    echo "=========================================="

    # Show summary
    echo ""
    echo "Summary:"
    python3 << PYTHON
import json
with open("$OUTPUT_FILE") as f:
    data = json.load(f)

total_passed = sum(r.get("passed", 0) for r in data["repos"].values() if isinstance(r, dict))
total_failed = sum(r.get("failed", 0) for r in data["repos"].values() if isinstance(r, dict))
total_skipped = sum(r.get("skipped", 0) for r in data["repos"].values() if isinstance(r, dict))
total = total_passed + total_failed + total_skipped

if total > 0:
    print(f"  Total tests: {total}")
    print(f"  Passed: {total_passed} ({100*total_passed/total:.1f}%)")
    print(f"  Failed: {total_failed} ({100*total_failed/total:.1f}%)")
    print(f"  Skipped: {total_skipped} ({100*total_skipped/total:.1f}%)")
else:
    print("  No test results collected")
PYTHON
}

collect_repo_metrics() {
    local repo_name=$1
    local repo_path=$2
    local env_vars=$3
    
    # Progress output goes to stderr so it's visible
    echo "" >&2
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
    echo -e "${YELLOW}Collecting metrics for $repo_name...${NC}" >&2
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
    
    if [[ ! -d "$repo_path" ]]; then
        echo -e "${RED}  Repo not found: $repo_path${NC}" >&2
        echo "    \"$repo_name\": {\"error\": \"repo not found\"},"
        return
    fi
    
    cd "$repo_path"
    echo -e "  ${BLUE}Directory:${NC} $repo_path" >&2
    echo -e "  ${BLUE}Env vars:${NC} $env_vars" >&2
    echo -e "  ${YELLOW}Running pytest (this may take a minute)...${NC}" >&2
    
    # Run pytest and capture output, showing progress
    local pytest_output
    local start_time=$(date +%s)
    
    # Run pytest (no -q flag, it suppresses summary on failures)
    pytest_output=$(eval "$env_vars PYTHONPATH=src poetry run pytest tests/ --tb=no 2>&1" || true)
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    echo -e "  ${GREEN}Completed in ${duration}s${NC}" >&2
    
    # Debug: show last few lines of pytest output
    echo -e "  ${BLUE}Pytest summary:${NC}" >&2
    echo "$pytest_output" | tail -5 | sed 's/^/    /' >&2
    
    # Parse the summary line - pytest formats vary:
    # "235 passed, 19 skipped, 1 warning in 8.50s"
    # "===== 240 passed, 13 failed in 5.23s ====="
    # "1 failed, 191 passed, 102 skipped in 32.70s"  (failed first when there are failures)
    local summary_line
    summary_line=$(echo "$pytest_output" | grep -E "[0-9]+ passed" | tail -1 || echo "")
    
    # Extract numbers using grep -o and sed (more portable than -P)
    local passed=$(echo "$summary_line" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' || echo "0")
    local failed=$(echo "$summary_line" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' || echo "0")
    local skipped=$(echo "$summary_line" | grep -oE '[0-9]+ skipped' | grep -oE '[0-9]+' || echo "0")
    
    # Handle empty values
    passed=${passed:-0}
    failed=${failed:-0}
    skipped=${skipped:-0}
    
    local total=$((passed + failed + skipped))
    local skip_pct=0
    if [[ $total -gt 0 ]]; then
        # Use awk instead of bc for floating point
        skip_pct=$(awk "BEGIN {printf \"%.1f\", $skipped * 100 / $total}")
    fi
    
    # Get coverage from output if available
    local coverage=$(echo "$pytest_output" | grep -oP 'TOTAL\s+\d+\s+\d+\s+\K\d+(?=%)' | tail -1 || echo "0")
    coverage=${coverage:-0}
    
    # Count mock usage
    local mock_lines=0
    local mock_tests=0
    if [[ -d "tests" ]]; then
        mock_lines=$(grep -r "mock\|Mock\|patch\|MagicMock" tests/ 2>/dev/null | wc -l || echo "0")
        # Count test functions that use mocks (functions containing mock patterns)
        mock_tests=$(grep -rl "mock\|Mock\|patch\|MagicMock" tests/ 2>/dev/null | xargs grep -l "def test_" 2>/dev/null | xargs grep -c "def test_" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}' || echo "0")
    fi
    
    echo -e "  ${GREEN}Passed:${NC} $passed  ${RED}Failed:${NC} $failed  ${YELLOW}Skipped:${NC} $skipped  Coverage: $coverage%" >&2
    
    # Output JSON fragment
    cat << REPO_EOF
    "$repo_name": {
      "passed": $passed,
      "failed": $failed,
      "skipped": $skipped,
      "total": $total,
      "skip_pct": $skip_pct,
      "coverage": $coverage,
      "mock_lines": $mock_lines,
      "mock_tests": $mock_tests
    },
REPO_EOF
}

#=============================================================================
# Main Command Dispatcher
#=============================================================================

COMMAND="${1:-collect}"
shift || true

case "$COMMAND" in
    collect)
        run_collection "$@"
        ;;
    up|start)
        start_services
        echo -e "${GREEN}Services started. Run '$0 down' to stop.${NC}"
        # Don't stop on exit when just starting
        trap - EXIT
        ;;
    down|stop)
        SERVICES_STARTED=1  # Force stop
        stop_services
        trap - EXIT
        ;;
    status)
        show_status
        trap - EXIT
        ;;
    help|--help|-h)
        print_usage
        trap - EXIT
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        print_usage
        exit 1
        ;;
esac
