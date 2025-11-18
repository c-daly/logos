# Phase 1 Tests

This directory contains functional tests for Phase 1 milestones of Project LOGOS.

## Test Files

### M1: Neo4j CRUD and Relationship Traversal
- **File:** `test_m1_neo4j_crud.py`
- **Requirements:** Running Neo4j instance (docker-compose.hcg.dev.yml)
- **Purpose:** Tests basic CRUD operations, UUID constraints, and relationship traversal

### M2: SHACL Validation

#### Standalone RDF Validation (pyshacl)
- **File:** `test_m2_shacl_validation.py`
- **Requirements:** None (uses pyshacl library standalone)
- **Purpose:** Tests SHACL shapes validate correctly using pyshacl library
- **Usage:**
  ```bash
  pytest tests/phase1/test_m2_shacl_validation.py -v
  ```

#### Neo4j-based Validation (n10s)
- **File:** `test_m2_neo4j_shacl_validation.py`
- **Requirements:** Running Neo4j instance with n10s plugin installed
- **Purpose:** Tests SHACL validation through Neo4j neosemantics (n10s) plugin
- **Tests:**
  1. Loading SHACL shapes into Neo4j via n10s
  2. Validation of valid test data (should pass)
  3. Validation of invalid test data (should fail with violations)
  4. Rejection of bad writes through Neo4j:
     - Wrong UUID prefix
     - Missing required fields
     - Negative spatial values
     - Invalid joint types
- **Usage:**
  ```bash
  # Start Neo4j with n10s plugin
  cd infra
  docker-compose -f docker-compose.hcg.dev.yml up -d neo4j
  
  # Install n10s plugin (see .github/workflows/shacl-neo4j-validation.yml for details)
  # or use the GitHub Actions workflow which handles this automatically
  
  # Run tests
  pytest tests/phase1/test_m2_neo4j_shacl_validation.py -v
  ```

### M3: Planning
- **File:** `test_m3_planning.py`
- **Requirements:** Running Neo4j instance
- **Purpose:** Tests planning and goal decomposition functionality

## Test Fixtures

The `fixtures/` directory contains test data files:
- `valid_entities.ttl` - Valid RDF data that should pass SHACL validation
- `invalid_entities.ttl` - Invalid RDF data that should fail SHACL validation

## Running All Phase 1 Tests

```bash
# Install dependencies
pip install -e .
pip install pytest pytest-cov neo4j rdflib pyshacl

# Run all phase 1 tests
pytest tests/phase1/ -v

# Run with coverage
pytest tests/phase1/ -v --cov=logos_hcg --cov=logos_tools
```

## CI/CD Integration

Phase 1 tests are integrated into GitHub Actions workflows:
- `.github/workflows/m1-neo4j-crud.yml` - M1 tests
- `.github/workflows/m2-shacl-validation.yml` - M2 pyshacl tests
- `.github/workflows/shacl-neo4j-validation.yml` - M2 Neo4j n10s tests (comprehensive)
- `.github/workflows/m3-planning.yml` - M3 tests
- `.github/workflows/phase1-gate.yml` - Combined gate check

## Acceptance Criteria

These tests implement the acceptance criteria for:
- **Issue #163**: Phase 1 Gate - M2 SHACL Validation
- **Issue #167**: CI Integration

See `docs/PHASE1_VERIFY.md` for complete verification checklist.
