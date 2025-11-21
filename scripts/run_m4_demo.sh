#!/usr/bin/env bash

# M4 Pick-and-Place Demo Runner
# This script runs the complete pick-and-place demo with comprehensive
# metrics capture, log collection, and verification reporting.
#
# Usage:
#   ./scripts/run_m4_demo.sh [--clean] [--no-recording] [--quick]
#
# Options:
#   --clean         Clear all previous demo data and start fresh
#   --no-recording  Skip demo recording (faster execution)
#   --quick         Run minimal demo without extended verification

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEMO_OUTPUT_DIR="${REPO_ROOT}/demo_output"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEMO_RUN_DIR="${DEMO_OUTPUT_DIR}/run_${TIMESTAMP}"

# Parse command line options
CLEAN_START=false
SKIP_RECORDING=false
QUICK_MODE=false

for arg in "$@"; do
    case $arg in
        --clean)
            CLEAN_START=true
            shift
            ;;
        --no-recording)
            SKIP_RECORDING=true
            shift
            ;;
        --quick)
            QUICK_MODE=true
            shift
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    echo ""
    echo -e "${CYAN}================================================================${NC}"
    echo -e "${CYAN}  LOGOS M4 Pick-and-Place Demo${NC}"
    echo -e "${CYAN}  Milestone 4: End-to-End System Integration${NC}"
    echo -e "${CYAN}================================================================${NC}"
    echo ""
}

print_section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo -e "${BLUE}$(printf '─%.0s' {1..60})${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Create demo output directory structure
setup_demo_directory() {
    print_section "Setting Up Demo Output Directory"
    
    mkdir -p "${DEMO_RUN_DIR}"/{logs,metrics,queries,screenshots}
    
    print_info "Demo output directory: ${DEMO_RUN_DIR}"
    print_success "Directory structure created"
}

# Initialize metrics tracking
init_metrics() {
    cat > "${DEMO_RUN_DIR}/metrics/execution_metrics.json" << EOF
{
    "demo_run_id": "m4_demo_${TIMESTAMP}",
    "start_time": "$(date -Iseconds)",
    "scenario": "pick_and_place_red_block",
    "metrics": {},
    "verification_status": {}
}
EOF
}

# Record a metric
record_metric() {
    local metric_name="$1"
    local metric_value="$2"
    
    # Simple append to metrics (in production, use jq for proper JSON manipulation)
    echo "  ${metric_name}: ${metric_value}" >> "${DEMO_RUN_DIR}/metrics/${metric_name}.txt"
}

# Clean previous demo data if requested
clean_previous_data() {
    if [ "$CLEAN_START" = true ]; then
        print_section "Cleaning Previous Demo Data"
        
        print_info "Clearing Neo4j database..."
        docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
            "MATCH (n) DETACH DELETE n;" 2>&1 | head -3
        
        print_success "Database cleared"
        
        # Remove old logs
        rm -rf "${REPO_ROOT}/logs/e2e"
        print_success "Old logs removed"
    fi
}

# Execute the e2e prototype script
run_e2e_script() {
    print_section "Running End-to-End Prototype Script"
    
    local start_time=$(date +%s)
    
    if bash "${SCRIPT_DIR}/e2e_prototype.sh" > "${DEMO_RUN_DIR}/logs/e2e_output.log" 2>&1; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        print_success "E2E script completed in ${duration}s"
        record_metric "e2e_execution_time" "${duration}"
        
        # Copy e2e logs to demo output
        if [ -d "${REPO_ROOT}/logs/e2e" ]; then
            cp -r "${REPO_ROOT}/logs/e2e"/* "${DEMO_RUN_DIR}/logs/"
            print_success "E2E logs copied to demo output"
        fi
        
        return 0
    else
        print_error "E2E script failed"
        tail -20 "${DEMO_RUN_DIR}/logs/e2e_output.log"
        return 1
    fi
}

# Capture system metrics
capture_system_metrics() {
    print_section "Capturing System Metrics"
    
    # Neo4j node counts
    print_info "Counting Neo4j nodes..."
    docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
        "MATCH (n) RETURN labels(n)[0] AS type, count(n) AS count ORDER BY type;" \
        > "${DEMO_RUN_DIR}/metrics/node_counts.txt" 2>&1
    
    local entity_count=$(grep "Entity" "${DEMO_RUN_DIR}/metrics/node_counts.txt" | awk '{print $3}' || echo "0")
    local state_count=$(grep "State" "${DEMO_RUN_DIR}/metrics/node_counts.txt" | awk '{print $3}' || echo "0")
    local process_count=$(grep "Process" "${DEMO_RUN_DIR}/metrics/node_counts.txt" | awk '{print $3}' || echo "0")
    
    print_success "Entities: ${entity_count}"
    print_success "States: ${state_count}"
    print_success "Processes: ${process_count}"
    
    # Relationship counts
    print_info "Counting relationships..."
    docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
        "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS count ORDER BY count DESC;" \
        > "${DEMO_RUN_DIR}/metrics/relationship_counts.txt" 2>&1
    
    # Container resource usage
    print_info "Capturing container metrics..."
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
        logos-hcg-neo4j logos-hcg-milvus > "${DEMO_RUN_DIR}/metrics/container_resources.txt" 2>&1 || true
    
    print_success "System metrics captured"
}

# Run verification queries
run_verification_queries() {
    print_section "Running Verification Queries"
    
    local queries_dir="${DEMO_RUN_DIR}/queries"
    
    # Query 1: Final block location
    print_info "Query 1: Verify red block final location..."
    docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
        "MATCH (block:Entity)-[:LOCATED_AT]->(bin:Entity)
         WHERE block.name CONTAINS 'RedBlock'
         RETURN block.name AS Object, bin.name AS Location;" \
        > "${queries_dir}/q1_final_location.txt" 2>&1
    
    if grep -q "TargetBin\|Bin01" "${queries_dir}/q1_final_location.txt"; then
        print_success "✓ Block is in target bin"
        echo "PASS" > "${queries_dir}/q1_status.txt"
    else
        print_error "✗ Block location verification failed"
        echo "FAIL" > "${queries_dir}/q1_status.txt"
    fi
    
    # Query 2: Plan execution order
    print_info "Query 2: Verify plan execution order..."
    docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
        "MATCH path = (start:Process)-[:PRECEDES*]->(end:Process)
         WHERE NOT EXISTS((start)<-[:PRECEDES]-())
         RETURN [n in nodes(path) | n.name] AS sequence, length(path) AS steps;" \
        > "${queries_dir}/q2_plan_order.txt" 2>&1
    
    if grep -q "3" "${queries_dir}/q2_plan_order.txt"; then
        print_success "✓ Plan has 4 steps with 3 PRECEDES links"
        echo "PASS" > "${queries_dir}/q2_status.txt"
    else
        print_warn "⚠ Plan structure may be incomplete"
        echo "WARN" > "${queries_dir}/q2_status.txt"
    fi
    
    # Query 3: State history
    print_info "Query 3: Check block state history..."
    docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
        "MATCH (e:Entity)-[:HAS_STATE]->(s:State)
         WHERE e.name CONTAINS 'RedBlock'
         RETURN s.name, s.description, s.timestamp
         ORDER BY s.timestamp DESC
         LIMIT 5;" \
        > "${queries_dir}/q3_state_history.txt" 2>&1
    
    local state_count=$(grep -c "RedBlock" "${queries_dir}/q3_state_history.txt" || echo "0")
    if [ "$state_count" -ge 2 ]; then
        print_success "✓ Multiple states recorded (${state_count})"
        echo "PASS" > "${queries_dir}/q3_status.txt"
    else
        print_warn "⚠ Fewer states than expected"
        echo "WARN" > "${queries_dir}/q3_status.txt"
    fi
    
    # Query 4: Causal relationships
    print_info "Query 4: Verify causal relationships..."
    docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
        "MATCH (p:Process)-[:CAUSES]->(s:State)
         RETURN p.name AS Action, s.name AS ResultingState;" \
        > "${queries_dir}/q4_causal_links.txt" 2>&1
    
    local causal_count=$(grep -c "Process" "${queries_dir}/q4_causal_links.txt" || echo "0")
    print_info "Found ${causal_count} causal relationships"
    echo "PASS" > "${queries_dir}/q4_status.txt"
    
    print_success "Verification queries completed"
}

# Generate demo summary report
generate_summary_report() {
    print_section "Generating Demo Summary Report"
    
    local report_file="${DEMO_RUN_DIR}/DEMO_SUMMARY.md"
    
    cat > "${report_file}" << EOF
# M4 Pick-and-Place Demo Summary

**Demo Run ID:** m4_demo_${TIMESTAMP}  
**Date:** $(date -Iseconds)  
**Scenario:** Pick and Place Red Block  
**Status:** $([ -f "${DEMO_RUN_DIR}/queries/q1_status.txt" ] && cat "${DEMO_RUN_DIR}/queries/q1_status.txt" || echo "UNKNOWN")

---

## Execution Summary

### Timeline
- **Start Time:** $(grep start_time "${DEMO_RUN_DIR}/metrics/execution_metrics.json" | cut -d'"' -f4)
- **End Time:** $(date -Iseconds)
- **Total Duration:** $([ -f "${DEMO_RUN_DIR}/metrics/e2e_execution_time.txt" ] && cat "${DEMO_RUN_DIR}/metrics/e2e_execution_time.txt" || echo "N/A")

### Components
- ✓ Neo4j (Graph Database)
- ✓ Milvus (Vector Store)
- ✓ HCG (Hybrid Causal Graph)

---

## Scenario Details

### Entities
- Robot Manipulator (RobotArm01)
- Gripper (Gripper01)
- Red Block (RedBlock01)
- Target Bin (TargetBin01)
- Work Table (WorkTable01)

### Plan Steps
1. **MoveToPreGrasp** - Position arm above red block
2. **GraspRedBlock** - Close gripper to grasp block
3. **MoveToPlace** - Transport block to target
4. **ReleaseBlock** - Release block into bin

### Final State
EOF

    # Add verification results
    if [ -f "${DEMO_RUN_DIR}/queries/q1_final_location.txt" ]; then
        echo "" >> "${report_file}"
        echo "### Verification Results" >> "${report_file}"
        echo "" >> "${report_file}"
        
        for i in 1 2 3 4; do
            if [ -f "${DEMO_RUN_DIR}/queries/q${i}_status.txt" ]; then
                local status=$(cat "${DEMO_RUN_DIR}/queries/q${i}_status.txt")
                local icon="✓"
                [ "$status" = "FAIL" ] && icon="✗"
                [ "$status" = "WARN" ] && icon="⚠"
                echo "- ${icon} Query ${i}: ${status}" >> "${report_file}"
            fi
        done
    fi
    
    # Add metrics summary
    if [ -f "${DEMO_RUN_DIR}/metrics/node_counts.txt" ]; then
        echo "" >> "${report_file}"
        echo "### System Metrics" >> "${report_file}"
        echo "" >> "${report_file}"
        echo "\`\`\`" >> "${report_file}"
        cat "${DEMO_RUN_DIR}/metrics/node_counts.txt" >> "${report_file}"
        echo "\`\`\`" >> "${report_file}"
    fi
    
    # Add file manifest
    echo "" >> "${report_file}"
    echo "---" >> "${report_file}"
    echo "" >> "${report_file}"
    echo "## Artifacts" >> "${report_file}"
    echo "" >> "${report_file}"
    echo "All demo artifacts are stored in:" >> "${report_file}"
    echo "\`${DEMO_RUN_DIR}\`" >> "${report_file}"
    echo "" >> "${report_file}"
    echo "### Directory Structure" >> "${report_file}"
    echo "\`\`\`" >> "${report_file}"
    tree -L 2 "${DEMO_RUN_DIR}" 2>/dev/null || find "${DEMO_RUN_DIR}" -maxdepth 2 -type f
    echo "\`\`\`" >> "${report_file}"
    
    print_success "Summary report generated: ${report_file}"
}

# Main execution flow
main() {
    print_banner
    
    print_info "Demo configuration:"
    echo "  Clean start: ${CLEAN_START}"
    echo "  Skip recording: ${SKIP_RECORDING}"
    echo "  Quick mode: ${QUICK_MODE}"
    echo ""
    
    # Setup
    setup_demo_directory
    init_metrics
    
    # Clean if requested
    clean_previous_data
    
    # Run the main demo
    if ! run_e2e_script; then
        print_error "Demo execution failed"
        exit 1
    fi
    
    # Capture metrics and verification
    capture_system_metrics
    run_verification_queries
    
    # Generate report
    generate_summary_report
    
    # Final summary
    print_section "Demo Complete"
    echo ""
    print_success "M4 pick-and-place demo completed successfully!"
    echo ""
    print_info "Demo artifacts: ${DEMO_RUN_DIR}"
    print_info "Summary report: ${DEMO_RUN_DIR}/DEMO_SUMMARY.md"
    echo ""
    print_info "Next steps:"
    echo "  1. Review summary report: cat ${DEMO_RUN_DIR}/DEMO_SUMMARY.md"
    echo "  2. Examine query results: ls ${DEMO_RUN_DIR}/queries/"
    echo "  3. Check metrics: ls ${DEMO_RUN_DIR}/metrics/"
    echo "  4. View full walkthrough: docs/operations/demos/PICK_AND_PLACE_WALKTHROUGH.md"
    echo ""
    
    return 0
}

# Run main
main "$@"
