# LOGOS Persona Diary Module

Persona diary system for storing activity summaries and sentiments in the HCG.

## Overview

The `logos_persona` module provides:
- **PersonaEntry nodes** in Neo4j for storing diary entries
- **Sentiment tracking** for emotional context
- **Process linking** to associate entries with HCG processes
- **FastAPI endpoints** for Apollo to query entries

## Usage

### Basic Usage

```python
from logos_persona import PersonaDiary
from neo4j import GraphDatabase

# Connect to Neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
diary = PersonaDiary(driver)

# Create a diary entry
entry = diary.create_entry(
    summary="Successfully completed pick-and-place task",
    sentiment="confident",
    related_process="process-uuid-123"
)

print(f"Created entry: {entry.uuid}")
```

### Querying Entries

```python
# Get recent entries
recent = diary.get_recent_entries(limit=10)
for entry in recent:
    print(f"[{entry.sentiment}] {entry.summary}")

# Filter by sentiment
confident_entries = diary.get_recent_entries(limit=10, sentiment="confident")

# Get entries for a specific process
process_entries = diary.get_entries_for_process("process-uuid-123")

# Get sentiment distribution
summary = diary.get_sentiment_summary()
print(summary)  # {"confident": 5, "cautious": 3, "curious": 2}
```

## Node Schema

PersonaEntry nodes have the following properties:

```cypher
(:PersonaEntry {
    uuid: String,           // Unique identifier (required)
    timestamp: String,      // ISO 8601 timestamp (required)
    summary: String,        // Text summary of activity (required)
    sentiment: String,      // Emotional tone (optional)
    related_process: String // UUID of related Process (optional)
})
```

Relationships:
- `(:PersonaEntry)-[:RELATES_TO]->(:Process)` - Links to related process

## FastAPI Integration

Create API endpoints for Apollo:

```python
from fastapi import FastAPI
from logos_persona import create_persona_api

app = FastAPI()

# Add persona routes
persona_router = create_persona_api(driver)
app.include_router(persona_router)
```

### API Endpoints

#### Create Entry
```bash
POST /persona/entries
{
    "summary": "Completed task",
    "sentiment": "confident",
    "related_process": "process-uuid"
}
```

#### Get Recent Entries
```bash
GET /persona/entries?limit=10&sentiment=confident
```

#### Get Entries for Process
```bash
GET /persona/entries/process/{process_uuid}
```

#### Get Sentiment Summary
```bash
GET /persona/sentiment/summary
```

## Sentiment Types

Common sentiment values used in LOGOS:
- `confident` - Successfully completed tasks, high certainty
- `cautious` - Uncertain conditions, potential obstacles
- `curious` - Exploring new strategies or situations
- `neutral` - Routine operations, no strong sentiment
- `concerned` - Detected issues, low success probability

## Integration with CWM-E

Persona entries are consumed by the CWM-E reflection job to generate emotion states:

```python
from logos_cwm_e import CWMEReflector

reflector = CWMEReflector(driver)

# Reflect on persona entries to generate emotions
emotions = reflector.reflect_on_persona_entries(limit=10)
```

## Integration with Apollo

Apollo can query persona entries to influence chat tone and behavior:

```typescript
// Get recent confident entries for positive tone
const response = await fetch('/persona/entries?sentiment=confident&limit=5');
const entries = await response.json();

// Use in chat context
const context = entries.map(e => e.summary).join('\n');
```

## Neo4j Queries

### View Recent Entries
```cypher
MATCH (pe:PersonaEntry)
RETURN pe
ORDER BY pe.timestamp DESC
LIMIT 10
```

### Entries by Sentiment
```cypher
MATCH (pe:PersonaEntry)
WHERE pe.sentiment = 'confident'
RETURN pe
ORDER BY pe.timestamp DESC
```

### Entries Linked to Process
```cypher
MATCH (pe:PersonaEntry)-[:RELATES_TO]->(p:Process {uuid: 'process-uuid'})
RETURN pe, p
```

## See Also

- `docs/phase2/VERIFY.md` - P2-M4 verification checklist
- `docs/phase2/PHASE2_SPEC.md` - Phase 2 specification (Persona section)
- `logos_cwm_e/` - CWM-E reflection module
- `examples/p2_m4_demo.py` - Example usage
