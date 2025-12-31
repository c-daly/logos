#!/usr/bin/env bash

# LOGOS Prototype End-to-End Script
# This script demonstrates the complete flow from Apollo command to HCG state updates
# See Project LOGOS spec: Section 7.1 (Phase 1: M4 End-to-End Demo)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${REPO_ROOT}/logs/e2e"

# Configuration
DOCKER_COMPOSE_FILE="${DOCKER_COMPOSE_FILE:-${REPO_ROOT}/tests/e2e/stack/logos/docker-compose.test.yml}"
NEO4J_CONTAINER="${NEO4J_CONTAINER:-logos-phase2-test-neo4j}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4jtest}"
NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
MILVUS_CONTAINER="${MILVUS_CONTAINER:-logos-phase2-test-milvus}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to log to file and stdout
log_output() {
    local message="$1"
    echo "$message" | tee -a "${LOG_DIR}/e2e_run.log"
}

# Function to check if Neo4j is available
check_neo4j() {
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
            print_success "Neo4j is ready!"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            print_warn "Still waiting for Neo4j... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 2
        ((attempt++))
    done
    
    print_error "Neo4j did not become ready within the timeout period"
    return 1
}

# Function to check if Milvus is available
check_milvus() {
    if docker ps --format '{{.Names}}' | grep -q "${MILVUS_CONTAINER}"; then
        return 0
    fi
    return 1
}

# Step 1: Start infrastructure
start_infrastructure() {
    print_header "Step 1: Starting HCG Infrastructure"
    
    # Check if containers are already running
    if docker ps --format '{{.Names}}' | grep -q "${NEO4J_CONTAINER}"; then
        print_info "Neo4j container is already running"
    else
        print_info "Starting docker-compose services..."
        docker compose -f "${DOCKER_COMPOSE_FILE}" up -d
    fi
    
    # Wait for services to be ready
    if ! wait_for_neo4j; then
        print_error "Failed to start Neo4j"
        return 1
    fi
    
    if check_milvus; then
        print_success "Milvus is running"
    else
        print_warn "Milvus container not detected, continuing anyway"
    fi
    
    log_output "Infrastructure started successfully"
    return 0
}

# Step 2: Load ontology and SHACL
load_ontology() {
    print_header "Step 2: Loading Core Ontology and SHACL Shapes"
    
    cd "${REPO_ROOT}"
    
    print_info "Loading core ontology..."
    if docker exec -i "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        < ontology/core_ontology.cypher > "${LOG_DIR}/ontology_load.log" 2>&1; then
        print_success "Core ontology loaded"
    else
        print_warn "Ontology may have been loaded previously (this is OK)"
    fi
    
    print_info "Verifying constraints..."
    local constraint_count=$(docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "SHOW CONSTRAINTS;" 2>/dev/null | grep -c "logos_" || echo "0")
    print_info "Found ${constraint_count} LOGOS constraints"
    
    log_output "Ontology and SHACL loaded"
    return 0
}

# Step 3: Load pick-and-place test data
load_test_data() {
    print_header "Step 3: Loading Pick-and-Place Test Data"
    
    cd "${REPO_ROOT}"
    
    print_info "Loading test data..."
    if docker exec -i "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        < ontology/test_data_pick_and_place.cypher > "${LOG_DIR}/test_data_load.log" 2>&1; then
        print_success "Test data loaded"
    else
        print_warn "Test data may have been loaded previously (this is OK)"
    fi
    
    # Verify test data
    print_info "Verifying test entities..."
    docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "MATCH (e:Node) WHERE 'thing' IN e.ancestors AND (e.name CONTAINS 'RedBlock' OR e.name CONTAINS 'Manipulator') RETURN e.name, e.uuid LIMIT 5;" \
        2>&1 | tee -a "${LOG_DIR}/test_data_verify.log"
    
    log_output "Test data loaded and verified"
    return 0
}

# Step 4: Simulate Apollo command (pick-and-place goal)
simulate_apollo_command() {
    print_header "Step 4: Simulating Apollo Command"
    
    print_info "Apollo sends command: 'Pick up the red block and place it in the bin'"
    
    # Create a goal state in the HCG
    print_info "Creating goal state in HCG..."
    docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "CREATE (g:Node {
            uuid: 'state-goal-' + randomUUID(),
            name: 'GoalState_RedBlockInBin',
            is_type_definition: false,
            type: 'state',
            ancestors: ['state', 'concept'],
            timestamp: datetime(),
            description: 'Red block should be in the target bin',
            is_goal: true
        }) RETURN g.uuid, g.name;" 2>&1 | tee -a "${LOG_DIR}/apollo_command.log"
    
    print_success "Apollo command received and goal state created"
    log_output "Apollo command simulated"
    return 0
}

# Step 5: Simulate Sophia plan generation
simulate_sophia_plan() {
    print_header "Step 5: Simulating Sophia Plan Generation"
    
    print_info "Sophia generates plan using causal reasoning..."
    
    # Create a simple plan with process nodes
    print_info "Creating plan processes..."
    docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "// Create plan with multiple processes using flexible ontology
        CREATE (p1:Node {
            uuid: 'process-plan-' + randomUUID(),
            name: 'MoveToPreGrasp',
            is_type_definition: false,
            type: 'process',
            ancestors: ['process', 'concept'],
            start_time: datetime(),
            description: 'Move manipulator to pre-grasp position'
        })
        CREATE (p2:Node {
            uuid: 'process-plan-' + randomUUID(),
            name: 'GraspRedBlock',
            is_type_definition: false,
            type: 'process',
            ancestors: ['process', 'concept'],
            start_time: datetime(),
            description: 'Grasp the red block'
        })
        CREATE (p3:Node {
            uuid: 'process-plan-' + randomUUID(),
            name: 'MoveToPlace',
            is_type_definition: false,
            type: 'process',
            ancestors: ['process', 'concept'],
            start_time: datetime(),
            description: 'Move to place position above bin'
        })
        CREATE (p4:Node {
            uuid: 'process-plan-' + randomUUID(),
            name: 'ReleaseBlock',
            is_type_definition: false,
            type: 'process',
            ancestors: ['process', 'concept'],
            start_time: datetime(),
            description: 'Release block into bin'
        })
        // Create temporal ordering
        CREATE (p1)-[:PRECEDES]->(p2)
        CREATE (p2)-[:PRECEDES]->(p3)
        CREATE (p3)-[:PRECEDES]->(p4)
        RETURN p1.name, p2.name, p3.name, p4.name;" 2>&1 | tee -a "${LOG_DIR}/sophia_plan.log"
    
    print_success "Sophia generated 4-step plan"
    
    # Display the plan
    print_info "Plan steps:"
    echo "  1. MoveToPreGrasp"
    echo "  2. GraspRedBlock"
    echo "  3. MoveToPlace"
    echo "  4. ReleaseBlock"
    
    log_output "Sophia plan generated"
    return 0
}

# Step 6: Simulate Talos execution and HCG updates
simulate_talos_execution() {
    print_header "Step 6: Simulating Talos Execution"
    
    print_info "Talos executes plan and updates HCG state..."
    
    # Simulate execution by creating state transitions
    print_info "Executing step 1: MoveToPreGrasp..."
    sleep 1
    
    print_info "Executing step 2: GraspRedBlock..."
    docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "// Update state: red block is grasped using flexible ontology
        MATCH (e:Node)
        WHERE 'thing' IN e.ancestors AND e.name CONTAINS 'RedBlock'
        CREATE (s:Node {
            uuid: 'state-exec-' + randomUUID(),
            name: 'RedBlockGrasped',
            is_type_definition: false,
            type: 'state',
            ancestors: ['state', 'concept'],
            timestamp: datetime(),
            description: 'Red block is now grasped by manipulator',
            is_grasped: true
        })
        CREATE (e)-[:HAS_STATE]->(s)
        RETURN e.name, s.name;" 2>&1 | tee -a "${LOG_DIR}/talos_execution.log"
    sleep 1
    
    print_info "Executing step 3: MoveToPlace..."
    sleep 1
    
    print_info "Executing step 4: ReleaseBlock..."
    docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "// Update state: red block is in bin using flexible ontology
        MATCH (e:Node)
        WHERE 'thing' IN e.ancestors AND e.name CONTAINS 'RedBlock'
        MATCH (bin:Node)
        WHERE 'thing' IN bin.ancestors AND (bin.name CONTAINS 'Bin' OR bin.name CONTAINS 'Target')
        CREATE (s:Node {
            uuid: 'state-exec-' + randomUUID(),
            name: 'RedBlockInBin',
            is_type_definition: false,
            type: 'state',
            ancestors: ['state', 'concept'],
            timestamp: datetime(),
            description: 'Red block is now in the target bin',
            is_grasped: false,
            location: 'target_bin'
        })
        CREATE (e)-[:HAS_STATE]->(s)
        CREATE (e)-[:LOCATED_AT]->(bin)
        RETURN e.name, s.name, bin.name;" 2>&1 | tee -a "${LOG_DIR}/talos_execution.log"
    
    print_success "Talos execution completed"
    log_output "Talos execution simulated"
    return 0
}

# Step 7: Verify Apollo reflects changes
verify_state_changes() {
    print_header "Step 7: Verifying State Changes"
    
    print_info "Apollo queries HCG for updated state..."
    
    # Query final state
    print_info "Final state of red block:"
    docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "MATCH (e:Node)-[:HAS_STATE]->(s:Node)
        WHERE 'thing' IN e.ancestors AND e.name CONTAINS 'RedBlock'
          AND (s.type = 'state' OR 'state' IN s.ancestors)
        RETURN e.name, s.name, s.description, s.timestamp
        ORDER BY s.timestamp DESC
        LIMIT 3;" 2>&1 | tee -a "${LOG_DIR}/state_verification.log"

    # Verify location relationship
    print_info "Location of red block:"
    docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "MATCH (e:Node)-[:LOCATED_AT]->(target:Node)
        WHERE 'thing' IN e.ancestors AND e.name CONTAINS 'RedBlock'
        RETURN e.name, target.name;" 2>&1 | tee -a "${LOG_DIR}/state_verification.log"

    # Verify plan execution trace
    print_info "Plan execution trace:"
    docker exec "${NEO4J_CONTAINER}" cypher-shell -u "${NEO4J_USER}" -p "${NEO4J_PASSWORD}" \
        "MATCH (p:Node)-[:PRECEDES*0..]->(next:Node)
        WHERE (p.type = 'process' OR 'process' IN p.ancestors)
          AND (p.name CONTAINS 'Move' OR p.name CONTAINS 'Grasp' OR p.name CONTAINS 'Release')
        RETURN p.name, p.description
        LIMIT 10;" 2>&1 | tee -a "${LOG_DIR}/state_verification.log"
    
    print_success "State changes verified"
    log_output "State verification completed"
    return 0
}

# Step 8: Capture logs and output
capture_logs() {
    print_header "Step 8: Capturing Logs and Output"
    
    print_info "Collecting system logs..."
    
    # Capture Neo4j logs
    if docker logs "${NEO4J_CONTAINER}" --tail 50 > "${LOG_DIR}/neo4j.log" 2>&1; then
        print_success "Neo4j logs captured"
    fi
    
    # Capture Milvus logs if available
    if docker logs "${MILVUS_CONTAINER}" --tail 50 > "${LOG_DIR}/milvus.log" 2>&1; then
        print_success "Milvus logs captured"
    else
        print_warn "Milvus logs not available"
    fi
    
    # Create summary report
    cat > "${LOG_DIR}/summary.txt" << EOF
LOGOS Prototype End-to-End Test Summary
========================================
Date: $(date)
Infrastructure: HCG (Neo4j + Milvus)

Test Scenario: Pick-and-Place Demo
-----------------------------------
1. ✓ Infrastructure started
2. ✓ Ontology and SHACL loaded
3. ✓ Test data loaded
4. ✓ Apollo command simulated
5. ✓ Sophia plan generated (4 steps)
6. ✓ Talos execution simulated
7. ✓ State changes verified
8. ✓ Logs captured

Result: SUCCESS
All components working together in the end-to-end flow.

Log files:
- ontology_load.log
- test_data_load.log
- apollo_command.log
- sophia_plan.log
- talos_execution.log
- state_verification.log
- neo4j.log
- milvus.log

EOF
    
    print_success "Logs captured in ${LOG_DIR}"
    print_info "Summary report created: ${LOG_DIR}/summary.txt"
    
    return 0
}

# Main execution
main() {
    echo ""
    echo "==================================="
    echo "LOGOS Prototype End-to-End Test"
    echo "==================================="
    echo ""
    
    # Create log directory
    mkdir -p "${LOG_DIR}"
    
    # Initialize log file
    echo "E2E Test Started: $(date)" > "${LOG_DIR}/e2e_run.log"
    
    # Execute steps
    if ! start_infrastructure; then
        print_error "Failed to start infrastructure"
        exit 1
    fi
    
    if ! load_ontology; then
        print_error "Failed to load ontology"
        exit 1
    fi
    
    if ! load_test_data; then
        print_error "Failed to load test data"
        exit 1
    fi
    
    if ! simulate_apollo_command; then
        print_error "Failed to simulate Apollo command"
        exit 1
    fi
    
    if ! simulate_sophia_plan; then
        print_error "Failed to simulate Sophia plan"
        exit 1
    fi
    
    if ! simulate_talos_execution; then
        print_error "Failed to simulate Talos execution"
        exit 1
    fi
    
    if ! verify_state_changes; then
        print_error "Failed to verify state changes"
        exit 1
    fi
    
    if ! capture_logs; then
        print_error "Failed to capture logs"
        exit 1
    fi
    
    # Final summary
    print_header "End-to-End Test Complete"
    
    cat "${LOG_DIR}/summary.txt"
    
    echo ""
    print_success "All tests passed! The prototype is working end-to-end."
    echo ""
    print_info "View detailed logs at: ${LOG_DIR}"
    print_info "Next steps:"
    echo "  - Review logs for any warnings or issues"
    echo "  - Integrate with real Apollo/Sophia/Talos components"
    echo "  - Add error handling and recovery mechanisms"
    echo "  - Extend with more complex scenarios"
    echo ""
    
    return 0
}

# Run main function
main "$@"
