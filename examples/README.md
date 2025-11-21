# LOGOS Examples

This directory contains example scripts demonstrating LOGOS functionality.

## Phase 2 Examples

### p2_m4_demo.py

Demonstrates the P2-M4 observability, persona diary, and CWM-E integration:

- OpenTelemetry structured logging
- Creating and querying persona entries
- Running CWM-E reflection to generate emotion states
- Querying telemetry summaries

**Prerequisites:**
- Neo4j running on localhost:7687
- Python packages installed: `pip install -e .`

**Usage:**
```bash
# Start Neo4j
docker compose -f infra/docker-compose.hcg.dev.yml up -d

# Load the ontology (includes PersonaEntry and EmotionState constraints)
./infra/load_ontology.sh

# Run the demo
python examples/p2_m4_demo.py
```

**Expected Output:**
The script will:
1. Setup OpenTelemetry telemetry
2. Connect to Neo4j
3. Create 3 persona diary entries with different sentiments
4. Run CWM-E reflection to generate emotion states
5. Query and display recent entries
6. Show sentiment distribution
7. Display telemetry summary

**Verification:**
After running the demo, you can verify the data in Neo4j:
```cypher
// View persona entries
MATCH (pe:PersonaEntry)
RETURN pe
ORDER BY pe.timestamp DESC
LIMIT 10

// View emotion states
MATCH (es:EmotionState)
RETURN es
ORDER BY es.timestamp DESC
LIMIT 10

// View relationships
MATCH (es:EmotionState)-[:GENERATED_BY]->(pe:PersonaEntry)
RETURN es, pe
```

And check the telemetry files:
```bash
ls -la /tmp/logos_telemetry/
cat /tmp/logos_telemetry/persona_entry_*.jsonl | jq
cat /tmp/logos_telemetry/emotion_state_*.jsonl | jq
```

## See Also

- `docs/phase2/VERIFY.md` - Verification checklist for Phase 2
- `docs/phase2/PHASE2_SPEC.md` - Phase 2 specification
- `logos_observability/` - Observability module
- `logos_persona/` - Persona diary module
- `logos_cwm_e/` - CWM-E reflection module
