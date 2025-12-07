# logos_config

Shared configuration utilities for the LOGOS ecosystem. This package provides centralized configuration helpers used across all LOGOS repositories (apollo, hermes, logos, sophia, talos).

## Installation

`logos_config` is included in the `logos-foundry` package. Add to your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
logos-foundry = {git = "https://github.com/c-daly/logos.git", branch = "main"}
```

Then import:

```python
from logos_config import get_env_value, get_repo_ports, Neo4jConfig
```

## Modules

### `env` - Environment Variable Resolution

```python
from logos_config import get_env_value, get_repo_root, load_env_file

# Get env var with fallback
db_host = get_env_value("DB_HOST", default="localhost")

# Load .env file (development only)
load_env_file()  # Loads from repo root
load_env_file("/path/to/.env")  # Explicit path

# Get repo root (development only - not for production/containers)
root = get_repo_root()
```

**⚠️ Production Note:** `get_repo_root()` and `load_env_file()` are development conveniences. In production (containers), config comes from environment variables directly.

### `ports` - Centralized Port Allocation

Each repo has a consistent port offset to avoid conflicts when running multiple services:

| Repo | Offset | Neo4j HTTP | Neo4j Bolt | Milvus | API |
|------|--------|------------|------------|--------|-----|
| hermes | +10000 | 17474 | 17687 | 29530 | 18000 |
| apollo | +20000 | 27474 | 27687 | 39530 | 28000 |
| logos | +30000 | 37474 | 37687 | 49530 | 38000 |
| sophia | +40000 | 47474 | 47687 | 59530 | 48000 |
| talos | +50000 | 57474 | 57687 | 69530 | 58000 |

```python
from logos_config import get_repo_ports, SOPHIA_PORTS

# Get ports for a specific repo
ports = get_repo_ports("sophia")
print(ports.neo4j_http)  # 47474
print(ports.neo4j_bolt)  # 47687
print(ports.milvus)      # 59530

# Or use pre-defined constants
print(SOPHIA_PORTS.neo4j_http)  # 47474
```

### `settings` - Pydantic Configuration Models

```python
from logos_config import Neo4jConfig, MilvusConfig, ServiceConfig

# Neo4j configuration with env var support
neo4j = Neo4jConfig()  # Reads from NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
neo4j = Neo4jConfig(uri="bolt://localhost:7687", user="neo4j", password="secret")

# Milvus configuration
milvus = MilvusConfig()  # Reads from MILVUS_HOST, MILVUS_PORT

# Generic service configuration
service = ServiceConfig(host="0.0.0.0", port=8000, debug=False)
```

### `health` - Unified Health Response Schema

```python
from logos_config.health import HealthResponse, HealthStatus, ComponentHealth

# Create a health response
health = HealthResponse(
    status=HealthStatus.HEALTHY,
    version="1.0.0",
    components={
        "database": ComponentHealth(status=HealthStatus.HEALTHY),
        "cache": ComponentHealth(status=HealthStatus.DEGRADED, message="High latency"),
    }
)
```

## Port Allocation Convention

The port scheme uses **base port + repo offset**:

- **Base ports**: Neo4j HTTP (7474), Neo4j Bolt (7687), Milvus (19530), API (8000)
- **Repo offset**: Each repo adds its offset to avoid collisions

This allows running the full stack locally without port conflicts, and makes it easy to identify which service owns a port (e.g., port 47474 = sophia's Neo4j).

## Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| `.env` files | ✅ Loaded via `load_env_file()` | ❌ Use K8s ConfigMaps/Secrets |
| `get_repo_root()` | ✅ Returns repo path | ❌ Not available in containers |
| Port offsets | ✅ For local multi-service | ⚠️ May use standard ports |
| Config source | Files + env vars | Env vars only |

## API Reference

See module docstrings for detailed API documentation:
- `logos_config.env`
- `logos_config.ports`
- `logos_config.settings`
- `logos_config.health`
