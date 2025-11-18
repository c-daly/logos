# LOGOS Scripts

This directory contains utility scripts for the LOGOS project.

## End-to-End Prototype Script

### `e2e_prototype.sh`

A comprehensive end-to-end test script that demonstrates the complete LOGOS prototype workflow.

**Purpose**: Validate the integration of Apollo → Sophia → Talos → HCG components through a simulated pick-and-place task.

**What it does**:
1. Starts HCG infrastructure (Neo4j + Milvus)
2. Loads core ontology and SHACL shapes
3. Loads pick-and-place test data
4. Simulates Apollo command (creates goal state)
5. Simulates Sophia plan generation (4-step process plan)
6. Simulates Talos execution (updates HCG state)
7. Verifies state changes in HCG
8. Captures logs and generates summary report

**Usage**:
```bash
# Basic usage
./scripts/e2e_prototype.sh

# Prerequisites: HCG infrastructure must be running
cd infra
docker compose -f docker-compose.hcg.dev.yml up -d
```

**Output**:
- Colored terminal output showing progress through each step
- Log files in `logs/e2e/`:
  - `e2e_run.log` - Main execution log
  - `ontology_load.log` - Ontology loading output
  - `test_data_load.log` - Test data loading output
  - `apollo_command.log` - Apollo command simulation
  - `sophia_plan.log` - Sophia plan generation
  - `talos_execution.log` - Talos execution simulation
  - `state_verification.log` - State verification queries
  - `neo4j.log` - Neo4j container logs
  - `milvus.log` - Milvus container logs (if available)
  - `summary.txt` - Summary report

**Exit codes**:
- `0` - Success (all tests passed)
- `1` - Failure (one or more tests failed)

**Environment variables**:
- `NEO4J_CONTAINER` - Neo4j container name (default: `logos-hcg-neo4j`)
- `NEO4J_USER` - Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD` - Neo4j password (default: `logosdev`)
- `NEO4J_URI` - Neo4j connection URI (default: `bolt://localhost:7687`)

**Example**:
```bash
# Run with custom container name
NEO4J_CONTAINER=my-neo4j ./scripts/e2e_prototype.sh

# View logs after run
cat logs/e2e/summary.txt
ls -la logs/e2e/
```

**CI Integration**:
The script is automatically run in CI via `.github/workflows/m4-end-to-end.yml`. It can be skipped in CI by setting the `skip_e2e` input to `true`.

**Related Documentation**:
- Phase 1 Verification: `docs/PHASE1_VERIFY.md` (M4 section)
- Prototype Capabilities: `docs/PROTOTYPE_CAPABILITIES.md`
- Test Suite: `tests/phase1/test_m4_end_to_end.py`

## Troubleshooting

**Script fails with "Neo4j not found"**:
- Ensure docker-compose is running: `docker ps | grep logos-hcg-neo4j`
- Start infrastructure: `cd infra && docker compose -f docker-compose.hcg.dev.yml up -d`

**Script fails with "Permission denied"**:
- Make script executable: `chmod +x scripts/e2e_prototype.sh`

**Script reports "Ontology already loaded"**:
- This is expected if you've run the script before
- The script handles this gracefully and continues

**Want to reset and start fresh**:
```bash
# Stop and remove all containers and volumes
cd infra
docker compose -f docker-compose.hcg.dev.yml down -v

# Start fresh
docker compose -f docker-compose.hcg.dev.yml up -d
```
