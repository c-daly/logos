# LOGOS Ontology and SHACL Validation

This directory contains the LOGOS ontology definition, SHACL validation shapes, and validation scripts.

## Files

### Ontology Definition
- **`core_ontology.cypher`** - Neo4j Cypher script defining HCG ontology structure, constraints, and base concepts
- **`test_data_pick_and_place.cypher`** - Sample test data for pick-and-place scenario

### SHACL Validation
- **`shacl_shapes.ttl`** - SHACL shapes for Level 1 deterministic validation (RDF/Turtle format)
- **`load_and_validate_shacl.py`** - Script to load shapes into Neo4j via n10s and run validation
- **`validate_ontology.py`** - Basic syntax validation for Cypher and TTL files (no Neo4j required)

### Documentation
- **`README_PICK_AND_PLACE.md`** - Documentation for pick-and-place ontology extension

## Quick Start

### 1. Start Neo4j with APOC plugin

```bash
cd ../infra
docker compose -f docker-compose.hcg.dev.yml up -d
```

Wait for Neo4j to be ready at http://localhost:7474 (login: neo4j/logosdev)

### 2. Install n10s Plugin (Manual)

The n10s plugin needs to be installed manually as it's not available via NEO4JLABS_PLUGINS:

```bash
# Download n10s plugin for Neo4j 5.13.0
wget https://github.com/neo4j-labs/neosemantics/releases/download/5.13.0/neosemantics-5.13.0.jar

# Copy into Neo4j container
docker cp neosemantics-5.13.0.jar logos-hcg-neo4j:/var/lib/neo4j/plugins/

# Restart Neo4j to load the plugin
docker restart logos-hcg-neo4j

# Wait for Neo4j to be ready again
sleep 15
```

Verify the plugin is loaded:
```bash
docker exec logos-hcg-neo4j cypher-shell -u neo4j -p logosdev \
  "SHOW PROCEDURES YIELD name WHERE name STARTS WITH 'n10s' RETURN count(name) AS count"
```

### 3. Load Core Ontology

```bash
cat core_ontology.cypher | \
  docker exec -i logos-hcg-neo4j cypher-shell -u neo4j -p logosdev
```

### 4. Load SHACL Shapes and Run Validation

```bash
# Install Python dependencies
pip install neo4j rdflib pyshacl

# Load shapes into Neo4j via n10s
python load_and_validate_shacl.py \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password logosdev \
  --shapes shacl_shapes.ttl \
  --skip-validation
```

### 5. Validate Test Data

#### Valid Data (should pass)
```bash
python load_and_validate_shacl.py \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password logosdev \
  --shapes shacl_shapes.ttl \
  --test-data ../tests/phase1/fixtures/valid_entities.ttl \
  --clear
```

#### Invalid Data (should fail)
```bash
python load_and_validate_shacl.py \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password logosdev \
  --shapes shacl_shapes.ttl \
  --test-data ../tests/phase1/fixtures/invalid_entities.ttl \
  --clear
```

## Script Usage

### load_and_validate_shacl.py

**Purpose**: Load SHACL shapes into Neo4j via neosemantics (n10s) and run validation against test data.

**Arguments**:
- `--uri` - Neo4j connection URI (default: bolt://localhost:7687)
- `--user` - Neo4j username (default: neo4j)
- `--password` - Neo4j password (default: logosdev)
- `--shapes` - Path to SHACL shapes TTL file (default: shacl_shapes.ttl)
- `--test-data` - Path to test data TTL file to validate (optional)
- `--clear` - Clear graph before loading data
- `--skip-validation` - Load shapes but skip validation (useful for setup)

**Exit Codes**:
- `0` - Validation passed (or skipped)
- `1` - Validation failed or error occurred
- `130` - Interrupted by user (Ctrl+C)

**Examples**:

```bash
# Just load shapes without validation
python load_and_validate_shacl.py --skip-validation

# Load and validate in one step
python load_and_validate_shacl.py --test-data valid_entities.ttl

# Clear graph first, then load and validate
python load_and_validate_shacl.py --test-data invalid_entities.ttl --clear

# Use custom Neo4j connection
python load_and_validate_shacl.py \
  --uri bolt://remote-neo4j:7687 \
  --user myuser \
  --password mypass \
  --shapes shacl_shapes.ttl
```

### validate_ontology.py

**Purpose**: Basic syntax validation for Cypher and TTL files (no Neo4j required).

**Usage**:
```bash
python validate_ontology.py
```

This script validates:
- Balanced braces, parentheses, and brackets
- Required Cypher statements (CREATE, MERGE, CONSTRAINT)
- UUID format patterns
- Required prefixes in TTL files
- SHACL shape definitions

## CI Integration

The GitHub Actions workflow `.github/workflows/shacl-neo4j-validation.yml` runs SHACL validation on every push/PR:

1. Starts Neo4j with n10s plugin in a service container
2. Loads core ontology
3. Loads SHACL shapes via n10s
4. Tests validation with valid data (should pass)
5. Tests validation with invalid data (should fail)
6. Reports results in GitHub Actions summary

See `docs/PHASE1_VERIFY.md` for complete M2 verification checklist.

## SHACL Shapes Overview

The SHACL shapes in `shacl_shapes.ttl` enforce:

### EntityShape
- UUID format: `entity-*`
- UUID uniqueness and required
- Optional name, description, created_at

### ConceptShape
- UUID format: `concept-*`
- UUID uniqueness and required
- Name required and unique
- Optional description

### StateShape
- UUID format: `state-*`
- UUID uniqueness and required
- Timestamp required
- Optional spatial properties (position_x, position_y, position_z, orientation_*)

### ProcessShape
- UUID format: `process-*`
- UUID uniqueness and required
- start_time required
- Optional duration_ms

### Domain-Specific Shapes
- SpatialPropertiesShape - Validates spatial dimensions (width, height, depth, radius, mass)
- GripperPropertiesShape - Validates gripper properties (max_grasp_width, max_force)
- JointPropertiesShape - Validates joint properties (joint_type, min_angle, max_angle)
- Relationship shapes - Validates IS_A, HAS_STATE, CAUSES relationships

## Troubleshooting

### n10s plugin not available

If you see "n10s plugin not available", ensure:
1. Neo4j is running with n10s plugin enabled
2. Check `infra/docker-compose.hcg.dev.yml` has `NEO4J_PLUGINS=["apoc", "n10s"]`
3. Restart Neo4j container

### Validation fails unexpectedly

1. Check that shapes are loaded: `MATCH (n) WHERE n.uri CONTAINS 'shacl' RETURN n;`
2. Verify n10s config: `CALL n10s.graphconfig.show();`
3. Check Neo4j logs: `docker logs logos-hcg-neo4j`

### Connection refused

1. Ensure Neo4j is running: `docker ps | grep neo4j`
2. Check port 7687 is exposed: `docker port logos-hcg-neo4j`
3. Verify credentials (default: neo4j/logosdev)

## References

- **Specification**: `docs/spec/project_logos_full.md`, Section 4.3.1 (SHACL validation)
- **Verification**: `docs/PHASE1_VERIFY.md`, M2 section
- **Infrastructure**: `infra/docker-compose.hcg.dev.yml`
- **Test Fixtures**: `tests/phase1/fixtures/`
