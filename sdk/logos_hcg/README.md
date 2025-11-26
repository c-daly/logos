# logos-hcg

Shared HCG (Hybrid Causal Graph) client for the LOGOS ecosystem.

## Overview

This package provides a unified Neo4j client for interacting with the Hybrid Causal Graph (HCG). It consolidates functionality from both Apollo and Sophia repositories into a single, well-tested SDK.

## Features

- **Read Operations**: Query entities, states, processes, causal edges, and history
- **Write Operations**: Create, update, and delete nodes and edges with SHACL validation
- **Retry Logic**: Automatic retries with exponential backoff for transient failures
- **Connection Pooling**: Efficient connection management for high-throughput scenarios
- **Type Safety**: Full Pydantic models with validation
- **SHACL Validation**: Optional schema validation before graph mutations

## Installation

```bash
# From the logos repository root
pip install -e sdk/logos_hcg

# Or with poetry
poetry add ../sdk/logos_hcg
```

## Quick Start

```python
from logos_hcg import HCGClient
from logos_hcg.config import HCGConfig

# Configuration from environment variables
config = HCGConfig()

# Or explicit configuration
config = HCGConfig(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
)

# Use as context manager
with HCGClient(config) as client:
    # Read operations
    entities = client.get_entities(entity_type="manipulator", limit=10)
    entity = client.get_entity_by_id("entity_abc123")
    states = client.get_states(limit=50)
    processes = client.get_processes(status="running")
    
    # Write operations (with SHACL validation)
    entity_id = client.create_entity(
        entity_type="manipulator",
        properties={"name": "gripper", "status": "ready"}
    )
    
    client.add_relationship(
        source_id=entity_id,
        target_id="state_xyz789",
        relation_type="HAS_STATE",
    )
    
    # Graph snapshot for visualization
    snapshot = client.get_graph_snapshot(entity_types=["manipulator", "object"])
    
    # Health check
    if client.health_check():
        print("Neo4j is healthy")
```

## Configuration

The client can be configured via environment variables or directly:

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j Bolt URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password` | Neo4j password |
| `NEO4J_DATABASE` | `neo4j` | Database name |
| `HCG_MAX_POOL_SIZE` | `50` | Maximum connection pool size |
| `HCG_RETRY_ATTEMPTS` | `3` | Number of retry attempts |
| `HCG_SHACL_ENABLED` | `true` | Enable SHACL validation |

## Models

The package provides Pydantic models for all HCG entities:

```python
from logos_hcg.models import (
    Entity,
    State,
    Process,
    CausalEdge,
    PlanHistory,
    StateHistory,
    GraphSnapshot,
    PersonaEntry,
)
```

## SHACL Validation

SHACL validation is enabled by default for write operations. You can customize shapes:

```python
from logos_hcg import HCGClient
from logos_hcg.validation import SHACLValidator

# Custom SHACL shapes
custom_shapes = '''
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/hcg/> .

ex:CustomNodeShape a sh:NodeShape ;
    sh:targetClass ex:CustomNode ;
    sh:property [
        sh:path ex:requiredField ;
        sh:minCount 1 ;
    ] .
'''

validator = SHACLValidator(shapes_graph=custom_shapes)
client = HCGClient(config, validator=validator)
```

To disable validation:

```python
config = HCGConfig(shacl_enabled=False)
```

## Error Handling

The client raises specific exceptions:

```python
from logos_hcg.exceptions import (
    HCGConnectionError,
    HCGValidationError,
    HCGQueryError,
    HCGNotFoundError,
)

try:
    entity = client.get_entity_by_id("nonexistent")
except HCGNotFoundError:
    print("Entity not found")
except HCGConnectionError:
    print("Failed to connect to Neo4j")
```

## Migration from Apollo/Sophia

### From Apollo

```python
# Before
from apollo.data.hcg_client import HCGClient
from apollo.config.settings import Neo4jConfig

# After
from logos_hcg import HCGClient
from logos_hcg.config import HCGConfig
```

### From Sophia

```python
# Before
from sophia.hcg_client.neo4j_adapter import Neo4jAdapter

# After
from logos_hcg import HCGClient
```

## Development

```bash
cd sdk/logos_hcg

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=logos_hcg --cov-report=term-missing

# Lint
poetry run ruff check .
poetry run ruff format .
```

## License

MIT License - see LICENSE file.
