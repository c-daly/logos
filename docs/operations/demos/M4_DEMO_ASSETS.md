# M4 Pick-and-Place Demo Assets

This directory contains all assets for running and demonstrating the M4 milestone: end-to-end pick-and-place scenario.

## Quick Links

- **📖 [Complete Walkthrough](../docs/PICK_AND_PLACE_WALKTHROUGH.md)** - Step-by-step guide for running the demo
- **🚀 [Quick Start](#quick-start)** - Get running in 2 minutes
- **📊 [Verification Report](../logs/m4-verification/M4_VERIFICATION_REPORT.md)** - Complete verification documentation
- **🎯 [Success Criteria](#success-criteria)** - M4 milestone requirements

## Quick Start

### Option 1: Automated Demo (Recommended)

Run the complete demo with metrics and log capture:

```bash
# Run with all features
./scripts/run_m4_demo.sh

# Or with clean database start
./scripts/run_m4_demo.sh --clean

# Quick mode (faster, minimal verification)
./scripts/run_m4_demo.sh --quick
```

**Output:** Creates `demo_output/run_<timestamp>/` with complete metrics, logs, and summary report.

### Option 2: Basic E2E Script

Run the basic end-to-end prototype:

```bash
./scripts/e2e_prototype.sh
```

**Output:** Creates `logs/e2e/` with execution logs and summary.

### Option 3: Manual Walkthrough

Follow the complete step-by-step guide:

```bash
# Open the walkthrough
cat docs/PICK_AND_PLACE_WALKTHROUGH.md

# Or view in browser
open docs/PICK_AND_PLACE_WALKTHROUGH.md  # macOS
xdg-open docs/PICK_AND_PLACE_WALKTHROUGH.md  # Linux
```

## What Gets Demonstrated

### Scenario

A robotic manipulator picks up a red block from a table and places it in a target bin.

**Visual Flow:**
```
Initial State          Goal Created         Plan Generated       Executed
┌─────────────┐       ┌─────────────┐      ┌─────────────┐     ┌─────────────┐
│   [Block]   │       │   [Block]   │      │ 1. Move     │     │             │
│    Table    │  →    │    ↓ Goal   │  →   │ 2. Grasp    │  →  │   [Block]   │
│             │       │   [Bin]     │      │ 3. Move     │     │    in Bin   │
└─────────────┘       └─────────────┘      │ 4. Release  │     └─────────────┘
                                            └─────────────┘
```

### System Components Integration

**Apollo** (User Interface) → Creates goal state in HCG  
**Sophia** (Cognitive Core) → Generates 4-step plan using causal reasoning  
**Talos** (Execution) → Simulates physical execution of plan  
**HCG** (Knowledge Store) → Maintains state, causality, and temporal ordering

### Observable Outcomes

✅ **Entities Created:**
- Robot manipulator with gripper
- Red block and target bin
- Work surface

✅ **Plan Steps Generated:**
1. MoveToPreGrasp
2. GraspRedBlock
3. MoveToPlace
4. ReleaseBlock

✅ **State Transitions Tracked:**
- Initial: Block on table, gripper open
- Grasped: Block held by gripper
- Released: Block in bin

✅ **Relationships Established:**
- `PRECEDES` - Temporal ordering of plan steps
- `CAUSES` - Causal links from actions to states
- `LOCATED_AT` - Final spatial relationship

## Demo Assets Overview

### Scripts

| Script | Purpose | Duration | Output |
|--------|---------|----------|--------|
| `run_m4_demo.sh` | Full demo with metrics capture | ~30s | `demo_output/run_*/` |
| `e2e_prototype.sh` | Basic end-to-end execution | ~20s | `logs/e2e/` |
| `demo_capture/capture_demo.py` | Record demo sessions | Variable | `demo_output/` |

### Documentation

| Document | Description |
|----------|-------------|
| `docs/PICK_AND_PLACE_WALKTHROUGH.md` | Complete step-by-step guide |
| `logs/m4-verification/M4_VERIFICATION_REPORT.md` | Official verification report |
| `logs/m4-verification/COMPLETION_CHECKLIST.md` | Acceptance criteria checklist |
| `ontology/README_PICK_AND_PLACE.md` | Ontology structure details |
| `README.md` (this file) | Demo assets overview |

### Test Data

| File | Description |
|------|-------------|
| `ontology/core_ontology.cypher` | Core HCG ontology constraints |
| `ontology/test_data_pick_and_place.cypher` | Demo scenario entities |
| `tests/e2e/test_phase1_end_to_end.py` | Automated integration tests |

## Demo Workflow Details

### 1. Infrastructure Setup (10-15s)

```bash
docker compose -f infra/docker-compose.hcg.dev.yml up -d
```

Starts:
- Neo4j (Graph database) on ports 7474, 7687
- Milvus (Vector store) on ports 19530, 9091

### 2. Ontology Loading (2-3s)

```bash
docker exec -i logos-hcg-neo4j cypher-shell < ontology/core_ontology.cypher
```

Creates:
- UUID constraints for Entity, Concept, State, Process
- Core concept hierarchy
- Validation indexes

### 3. Test Data Loading (1-2s)

```bash
docker exec -i logos-hcg-neo4j cypher-shell < ontology/test_data_pick_and_place.cypher
```

Creates:
- 5 entities (robot, gripper, block, bin, table)
- Initial states
- Capability relationships

### 4. Apollo Command Simulation (<1s)

Creates goal state:
- Goal: Red block should be in target bin
- Links goal to block entity
- References target location

### 5. Sophia Plan Generation (<1s)

Generates 4-step plan:
- Creates Process nodes for each action
- Establishes PRECEDES relationships
- Validates preconditions

### 6. Talos Execution Simulation (2-3s)

Executes each step:
- Updates entity states
- Creates state transitions
- Establishes LOCATED_AT relationship

### 7. Verification (<1s)

Queries HCG to verify:
- Block is in target bin
- Plan executed in order
- State history is complete
- Causal relationships exist

## Success Criteria

Per Section 7.1 of the LOGOS specification, M4 validates:

### ✅ Agent Maintains Abstract State in HCG

**Verification:**
```cypher
MATCH (n) RETURN labels(n), count(n)
```

**Expected:** Entity, State, Process, Concept nodes present

### ✅ Agent Generates Simple Plans Using Causal Reasoning

**Verification:**
```cypher
MATCH (p:Process)-[:PRECEDES]->(next)
RETURN p.name, next.name
```

**Expected:** 4-step plan with temporal ordering

### ✅ All Components Communicate Via Defined Contracts

**Verification:** All updates go through HCG (Neo4j Cypher API)

**Components:**
- Apollo → HCG (goal creation)
- Sophia → HCG (plan generation)
- Talos → HCG (execution updates)

### ✅ SHACL Validation Catches Malformed Graph Updates

**Verification:**
```cypher
SHOW CONSTRAINTS
```

**Expected:** UUID constraints enforce `entity-*`, `state-*`, `process-*` format

## Metrics Captured

The `run_m4_demo.sh` script captures:

### Execution Metrics
- Total execution time
- Time per major step
- Infrastructure startup time

### System Metrics
- Node counts by type (Entity, State, Process, Concept)
- Relationship counts by type
- Container resource usage (CPU, memory)

### Verification Metrics
- Query execution status (PASS/FAIL/WARN)
- State transition count
- Causal relationship count
- Plan completeness

### Output Files

```
demo_output/run_<timestamp>/
├── DEMO_SUMMARY.md           # Executive summary
├── logs/
│   ├── e2e_output.log        # Full execution log
│   ├── ontology_load.log     # Ontology loading
│   ├── apollo_command.log    # Goal creation
│   ├── sophia_plan.log       # Plan generation
│   └── talos_execution.log   # Execution updates
├── metrics/
│   ├── execution_metrics.json
│   ├── node_counts.txt
│   ├── relationship_counts.txt
│   └── container_resources.txt
└── queries/
    ├── q1_final_location.txt
    ├── q2_plan_order.txt
    ├── q3_state_history.txt
    └── q4_causal_links.txt
```

## Recording Demo Sessions

Use the capture script to record demonstrations:

### CLI Session Recording

```bash
python scripts/demo_capture/capture_demo.py --mode cli --duration 300
```

Records terminal session with all commands and output.

### Log Aggregation

```bash
python scripts/demo_capture/capture_demo.py --mode logs \
    --log-dirs logs/e2e demo_output/run_*/logs
```

Aggregates all logs into structured format with manifest.

## Automated Testing

Run the complete M4 test suite:

```bash
pytest tests/e2e/test_phase1_end_to_end.py -v
```

**Coverage:**
- Infrastructure startup verification
- Ontology loading validation
- Test data integrity checks
- Simulated workflow execution
- State verification queries
- End-to-end script execution
- Complete workflow integration

**Expected Result:** 22 passed, 1 skipped (optional planner service)

## GitHub Actions Integration

The M4 workflow runs automatically:

**Triggers:**
- Push to main/develop
- Pull requests to main/develop
- Weekly schedule (Mondays 10:00 AM UTC)
- Manual dispatch

**Workflow:** `.github/workflows/m4-end-to-end.yml`

**Badge:** [![M4 Gate](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml/badge.svg)](https://github.com/c-daly/logos/actions/workflows/m4-end-to-end.yml)

## Troubleshooting

### Demo Script Fails

```bash
# Check container status
docker ps | grep logos

# Restart infrastructure
docker compose -f infra/docker-compose.hcg.dev.yml restart

# Clear and retry with clean start
./scripts/run_m4_demo.sh --clean
```

### Neo4j Connection Issues

```bash
# Check Neo4j logs
docker logs logos-hcg-neo4j --tail 50

# Verify Neo4j is ready
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p neo4jtest "RETURN 1;"
```

### No Verification Results

Ensure the e2e script completed successfully:

```bash
cat demo_output/run_*/logs/e2e_output.log | grep -i error
```

### Permission Denied

```bash
chmod +x scripts/*.sh
```

## Advanced Usage

### Custom Scenarios

Modify `ontology/test_data_pick_and_place.cypher` to create custom demos:
- Add more objects (different colors/shapes)
- Add multiple bins (sorting scenarios)
- Add obstacles (path planning)
- Modify gripper capabilities

### Interactive Exploration

Use Neo4j browser to explore the graph:

1. Open http://localhost:7474
2. Login: neo4j / neo4jtest
3. Run exploratory queries:

```cypher
// Visualize complete scenario
MATCH (n)
RETURN n
LIMIT 100

// Trace plan execution
MATCH path = (p:Process)-[:PRECEDES*]->(end)
WHERE NOT EXISTS((p)<-[:PRECEDES]-())
RETURN path

// Entity relationships
MATCH path = (e:Entity)-[r]-(related)
WHERE e.name CONTAINS 'RedBlock'
RETURN path
```

## Performance Benchmarks

Typical execution times on development hardware:

| Operation | Duration | Notes |
|-----------|----------|-------|
| Infrastructure startup | 10-15s | First time only |
| Ontology loading | 2-3s | Constraint creation |
| Test data loading | 1-2s | ~10 entities |
| Goal creation | <1s | Single query |
| Plan generation | <1s | 4 process nodes |
| Execution simulation | 2-3s | Multiple updates |
| Verification | <1s | 4 queries |
| **Full Demo** | **~20-30s** | Complete run |

## Next Steps

After running the demo:

1. **Review Results:**
   - Summary report: `demo_output/run_*/DEMO_SUMMARY.md`
   - Verification queries: `demo_output/run_*/queries/`
   - Metrics: `demo_output/run_*/metrics/`

2. **Explore Documentation:**
   - [Complete Walkthrough](../docs/PICK_AND_PLACE_WALKTHROUGH.md)
   - [Verification Report](../logs/m4-verification/M4_VERIFICATION_REPORT.md)
   - [Ontology Details](../ontology/README_PICK_AND_PLACE.md)

3. **Phase 2 Preparation:**
   - Implement real Apollo UI
   - Build Sophia cognitive services
   - Integrate Hermes language services
   - Add Talos hardware abstraction

## Support

For issues or questions:
- Review troubleshooting section above
- Check GitHub Actions logs
- See [M4 Verification Report](../logs/m4-verification/M4_VERIFICATION_REPORT.md)

## References

- **Specification:** `docs/old/spec/project_logos_full.md` Section 7.1
- **Milestone Definition:** `milestones/M4_End_to_End_Pick_and_Place.json`
- **Phase 1 Spec:** `docs/phase1/PHASE1_SPEC.md`
- **Ontology:** `ontology/README_PICK_AND_PLACE.md`

---

**Version:** 1.0  
**Last Updated:** 2025-11-20  
**Milestone:** M4 - End-to-End Pick-and-Place Demo
