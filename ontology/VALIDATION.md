# LOGOS SHACL Validation Guide

This document describes the SHACL validation infrastructure for the LOGOS HCG ontology, including integration with Neo4j and validation workflows.

## Overview

The LOGOS ontology uses SHACL (Shapes Constraint Language) for Level 1 deterministic validation of the Hybrid Causal Graph (HCG). SHACL shapes enforce:

- **Type constraints**: Data type validation (string, decimal, integer, datetime)
- **Cardinality constraints**: Required fields and uniqueness constraints
- **Value constraints**: Pattern matching, enumerated values, numeric ranges
- **Relationship constraints**: Valid relationship types between node classes

Reference: Project LOGOS Specification, Section 4.3.1

## SHACL Shapes Coverage

The `ontology/shacl_shapes.ttl` file defines shapes for:

### Node Type Shapes

1. **EntityShape** - Validates Entity nodes
   - Required: `uuid` (pattern: `^entity-.*`)
   - Optional: `name`, `description`, `created_at`

2. **ConceptShape** - Validates Concept nodes
   - Required: `uuid` (pattern: `^concept-.*`), `name`
   - Optional: `description`

3. **StateShape** - Validates State nodes
   - Required: `uuid` (pattern: `^state-.*`), `timestamp`
   - Optional: `name`, spatial properties (`position_x`, `position_y`, `position_z`, etc.)

4. **ProcessShape** - Validates Process nodes
   - Required: `uuid` (pattern: `^process-.*`), `start_time`
   - Optional: `name`, `description`, `duration_ms`

### Property Constraint Shapes

5. **SpatialPropertiesShape** - Validates spatial properties on Entities
   - Properties: `width`, `height`, `depth`, `radius`, `mass`
   - Constraint: All values must be ≥ 0.0

6. **GripperPropertiesShape** - Validates gripper-specific properties
   - Properties: `max_grasp_width`, `max_force`
   - Constraint: All values must be ≥ 0.0

7. **JointPropertiesShape** - Validates joint-specific properties
   - Property: `joint_type` (enumeration: "revolute", "prismatic", "fixed", "continuous")
   - Properties: `min_angle`, `max_angle`

### Relationship Shapes

8. **IsARelationshipShape** - Validates `(:Entity)-[:IS_A]->(:Concept)`
9. **HasStateRelationshipShape** - Validates `(:Entity)-[:HAS_STATE]->(:State)`
10. **CausesRelationshipShape** - Validates `(:Process)-[:CAUSES]->(:State)`
11. **PartOfRelationshipShape** - Validates `(:Entity)-[:PART_OF]->(:Entity)`
12. **LocatedAtRelationshipShape** - Validates `(:Entity)-[:LOCATED_AT]->(:Entity)`
13. **AttachedToRelationshipShape** - Validates `(:Entity)-[:ATTACHED_TO]->(:Entity)`
14. **PrecedesRelationshipShape** - Validates `(:State)-[:PRECEDES]->(:State)`
15. **RequiresRelationshipShape** - Validates `(:Process)-[:REQUIRES]->(:State)`
16. **CanPerformRelationshipShape** - Validates `(:Entity)-[:CAN_PERFORM]->(:Concept)`

## Neo4j Integration with Neosemantics (n10s)

### Prerequisites

Neo4j must be configured with the neosemantics (n10s) plugin to enable SHACL validation.

### Installation

1. **Install n10s plugin** in Neo4j:
   ```
   # For Neo4j Desktop: Install from Graph Apps
   # For Docker: Use official Neo4j image with n10s
   ```

2. **Initialize neosemantics** in your Neo4j database:
   ```cypher
   CREATE CONSTRAINT n10s_unique_uri 
   FOR (r:Resource) 
   REQUIRE r.uri IS UNIQUE;
   
   CALL n10s.graphconfig.init({
     handleVocabUris: "MAP",
     handleMultival: "ARRAY",
     keepLangTag: true
   });
   ```

### Loading SHACL Shapes into Neo4j

Load the SHACL shapes into Neo4j using n10s:

```cypher
// Load SHACL shapes from file
CALL n10s.validation.shacl.import.fetch(
  "file:///path/to/logos/ontology/shacl_shapes.ttl",
  "Turtle"
);
```

Or load from a string:

```cypher
// Load SHACL shapes from inline RDF
CALL n10s.validation.shacl.import.inline('
  @prefix sh: <http://www.w3.org/ns/shacl#> .
  @prefix logos: <http://logos.ontology/> .
  // ... shape definitions ...
', "Turtle");
```

### Validating Data in Neo4j

#### Validate the entire graph:

```cypher
CALL n10s.validation.shacl.validate();
```

This returns a validation report with:
- `focusNode`: The node that failed validation
- `resultPath`: The property that failed
- `resultMessage`: Description of the violation
- `resultSeverity`: Severity level (Violation, Warning, Info)

#### Validate specific nodes:

```cypher
// Validate all Entity nodes
MATCH (e:Entity)
CALL n10s.validation.shacl.validateNode(e)
YIELD focusNode, propertyShape, offendingValue, resultMessage
RETURN focusNode, propertyShape, offendingValue, resultMessage;
```

#### Validate before committing changes:

```cypher
// Example: Validate a new entity before creation
CREATE (e:Entity {
  uuid: "entity-test-001",
  name: "TestEntity"
})
WITH e
CALL n10s.validation.shacl.validateNode(e)
YIELD focusNode, resultMessage
RETURN focusNode, resultMessage;
```

## Python Validation Workflow

### Standalone Validation with pyshacl

For validation outside Neo4j (e.g., in CI/CD pipelines):

```python
from pyshacl import validate
from rdflib import Graph

# Load SHACL shapes
shapes_graph = Graph()
shapes_graph.parse("ontology/shacl_shapes.ttl", format="turtle")

# Load data to validate
data_graph = Graph()
data_graph.parse("path/to/data.ttl", format="turtle")

# Validate
conforms, results_graph, results_text = validate(
    data_graph,
    shacl_graph=shapes_graph,
    inference='rdfs',
    abort_on_first=False
)

if conforms:
    print("✓ Data validates successfully")
else:
    print("✗ Validation failed:")
    print(results_text)
```

### Basic Ontology Validation Script

A basic validation script is provided at `ontology/validate_ontology.py`:

```bash
cd /path/to/logos
python ontology/validate_ontology.py
```

This performs syntax checking on Cypher and TTL files without requiring a running Neo4j instance.

## Test Fixtures

Test fixtures are located in `tests/integration/ontology/fixtures/`:

### valid_entities.ttl

Contains valid test data organized by category:
- Basic node types (Entity, Concept, State, Process)
- Entities with spatial properties
- Entities with gripper/joint properties
- Valid relationships of all types

### invalid_entities.ttl

Contains invalid test data that should fail validation:
- Missing required fields
- Wrong UUID formats
- Invalid property values (negative numbers, wrong types)
- Invalid relationship targets (wrong node classes)

## Running Validation Tests

### Run all validation tests:

```bash
pytest tests/integration/ontology/test_shacl_validation.py -v
```

### Run specific test:

```bash
pytest tests/integration/ontology/test_shacl_validation.py::test_valid_entities_pass_validation -v
```

### Run with coverage:

```bash
pytest tests/integration/ontology/test_shacl_validation.py --cov=ontology --cov-report=html
```

## CI/CD Integration

SHACL validation is integrated into GitHub Actions via `.github/workflows/m2-shacl-validation.yml`.

The workflow:
1. Checks out the repository
2. Sets up Python environment
3. Installs dependencies (pytest, rdflib, pyshacl)
4. Runs validation test suite
5. Reports results to GitHub Actions summary

Validation runs on:
- All pull requests to `main` and `develop`
- Direct pushes to `main` and `develop`
- Weekly schedule (Mondays at 9:00 AM UTC)
- Manual workflow dispatch

### Viewing CI Results

1. Navigate to the "Actions" tab in GitHub
2. Select "M2 - SHACL Validation" workflow
3. View test results and validation reports

## Validation Workflow Best Practices

### Development Workflow

1. **Before committing changes** to ontology files:
   ```bash
   python ontology/validate_ontology.py
   pytest tests/integration/ontology/test_shacl_validation.py -v
   ```

2. **When adding new node types or properties**:
   - Add SHACL shape constraints to `ontology/shacl_shapes.ttl`
   - Add valid test case to `tests/integration/ontology/fixtures/valid_entities.ttl`
   - Add invalid test case to `tests/integration/ontology/fixtures/invalid_entities.ttl`
   - Add test function to `tests/integration/ontology/test_shacl_validation.py`

3. **When modifying relationships**:
   - Update corresponding relationship shape in `shacl_shapes.ttl`
   - Add test cases for valid and invalid relationship targets
   - Verify tests pass before committing

### Production Workflow

1. **Load core ontology** into Neo4j:
   ```cypher
   :source ontology/core_ontology.cypher
   ```

2. **Load SHACL shapes**:
   ```cypher
   CALL n10s.validation.shacl.import.fetch(
     "file:///path/to/shacl_shapes.ttl",
     "Turtle"
   );
   ```

3. **Validate before major operations**:
   ```cypher
   // Before bulk import
   CALL n10s.validation.shacl.validate()
   YIELD focusNode, resultMessage
   WHERE resultMessage IS NOT NULL
   RETURN focusNode, resultMessage;
   ```

4. **Monitor validation in application code**:
   ```python
   # Example with neo4j driver
   def validate_graph(session):
       result = session.run("""
           CALL n10s.validation.shacl.validate()
           YIELD focusNode, resultMessage
           WHERE resultMessage IS NOT NULL
           RETURN count(*) as violations
       """)
       violations = result.single()["violations"]
       if violations > 0:
           raise ValueError(f"Graph validation failed with {violations} violations")
   ```

## Troubleshooting

### Common Issues

1. **n10s plugin not found**
   - Ensure n10s is installed in Neo4j plugins directory
   - Restart Neo4j after installing plugin
   - Check Neo4j logs for plugin initialization errors

2. **Validation shapes not loading**
   - Verify TTL syntax: `rapper -i turtle shacl_shapes.ttl`
   - Check Neo4j logs for RDF parsing errors
   - Ensure file path is accessible to Neo4j

3. **False positives in validation**
   - Review shape constraints for overly restrictive rules
   - Check data type conversions (e.g., string vs decimal)
   - Verify namespace prefixes match between shapes and data

4. **Performance issues with large graphs**
   - Validate incrementally rather than entire graph
   - Use `validateNode()` for specific nodes
   - Consider batching validation operations

### Debug Mode

Enable verbose validation output in pyshacl:

```python
conforms, results_graph, results_text = validate(
    data_graph,
    shacl_graph=shapes_graph,
    inference='rdfs',
    debug=True,
    abort_on_first=False
)

# Print detailed results
for s, p, o in results_graph:
    print(f"{s} {p} {o}")
```

## References

- **SHACL Specification**: https://www.w3.org/TR/shacl/
- **Neosemantics (n10s)**: https://neo4j.com/labs/neosemantics/
- **pyshacl**: https://github.com/RDFLib/pySHACL
- **Project LOGOS Specification**: `docs/spec/project_logos_full.md`, Section 4.3.1

## Extending SHACL Shapes

To add new validation rules:

1. **Define the shape** in `shacl_shapes.ttl`:
   ```turtle
   logos:MyCustomShape
       a sh:NodeShape ;
       sh:targetClass logos:MyClass ;
       rdfs:label "My Custom Shape" ;
       rdfs:comment "Validates my custom constraints" ;
       sh:property [
           sh:path logos:myProperty ;
           sh:minCount 1 ;
           sh:datatype xsd:string ;
       ] .
   ```

2. **Add test fixtures**:
   - Valid case in `valid_entities.ttl`
   - Invalid case in `invalid_entities.ttl`

3. **Add test function** in `tests/integration/ontology/test_shacl_validation.py`:
   ```python
   def test_my_custom_validation(shacl_shapes):
       """Test that my custom constraint is enforced."""
       # Test implementation
   ```

4. **Verify tests pass**:
   ```bash
   pytest tests/integration/ontology/test_shacl_validation.py::test_my_custom_validation -v
   ```

5. **Update this documentation** with new shape details.

---

**Last Updated**: 2025-11-17  
**Maintainer**: LOGOS Development Team  
**Status**: Phase 1 Complete
