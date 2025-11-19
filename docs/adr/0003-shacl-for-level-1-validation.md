# ADR-0003: SHACL for Level 1 Validation

**Status:** Accepted

**Date:** 2024-01 (Phase 1 Foundation)

**Decision Makers:** Project LOGOS Core Team

**Related Issues:** Phase 1 HCG Validation, M2 Milestone

## Context and Problem Statement

The Hybrid Causal Graph (HCG) requires validation to ensure data quality and causal coherence. The specification defines a three-level validation strategy:
- **Level 1 (Deterministic)**: Schema validation, type checking, constraint enforcement
- **Level 2 (Probabilistic)**: Causal plausibility, temporal ordering consistency
- **Level 3 (Learned)**: Neural validators trained on domain examples

For Phase 1, we need to implement Level 1 validation that can:
- Validate HCG node types (Entity, Concept, State, Process)
- Enforce cardinality constraints (min/max counts)
- Check datatype correctness for node properties
- Validate UUID patterns and uniqueness
- Integrate with the Neo4j graph database
- Run in CI/CD pipelines without requiring full database infrastructure

Which validation framework and approach should we use for Level 1 deterministic validation?

## Decision Drivers

* **Graph-native validation**: Must understand graph structures, not just flat data
* **RDF/Semantic web standards**: Leverage established ontology validation patterns
* **CI/CD compatibility**: Fast, connectionless validation for automated testing
* **Neo4j integration**: Ability to validate data within the database for production checks
* **Expressiveness**: Rich constraint language for complex validation rules
* **Tooling maturity**: Stable libraries and good documentation
* **Python integration**: Align with project's primary language

## Considered Options

* **Option 1**: SHACL (Shapes Constraint Language) with dual validation strategy (pyshacl + Neo4j n10s)
* **Option 2**: JSON Schema validation with custom graph-aware rules
* **Option 3**: Cypher queries for constraint checking
* **Option 4**: OWL (Web Ontology Language) with reasoner

## Decision Outcome

Chosen option: "SHACL with dual validation strategy", because it provides standardized graph validation with excellent tooling support. The dual strategy enables:
- **Fast CI gates**: pyshacl validates RDF fixtures without database connection
- **Production integration**: Neo4j n10s plugin validates live graph data

This approach satisfies both development velocity (fast CI) and production requirements (in-database validation).

### Positive Consequences

* SHACL is a W3C standard with broad tool support and community
* Declarative constraint definitions are readable and maintainable
* pyshacl provides fast, connectionless validation for CI/CD pipelines
* Neo4j n10s plugin enables validation of live graph data in production
* RDF/Turtle syntax aligns with semantic web best practices
* SHACL shapes serve as living documentation of HCG schema
* Can validate both structure (cardinality, types) and semantics (patterns, value ranges)
* Test fixtures can be validated without spinning up full infrastructure

### Negative Consequences

* Requires learning SHACL/RDF syntax and concepts
* Dual validation approach adds some complexity (two validation paths)
* RDF/Turtle representation differs from Neo4j's property graph model (requires conceptual mapping)
* Neo4j n10s integration requires plugin installation (optional, not in default CI)
* SHACL violations produce technical error messages that may need translation for end users

## Pros and Cons of the Options

### SHACL (Shapes Constraint Language)

* Good, because W3C standard with mature specification and tooling
* Good, because declarative constraints are easier to maintain than procedural code
* Good, because pyshacl enables fast CI validation without database
* Good, because Neo4j n10s provides production validation path
* Good, because shapes double as schema documentation
* Good, because supports complex constraints (patterns, value ranges, logical combinations)
* Good, because active development and community support
* Bad, because requires understanding RDF/semantic web concepts
* Bad, because dual strategy (pyshacl + n10s) adds complexity
* Bad, because RDF ↔ property graph mapping requires care

### JSON Schema validation

* Good, because JSON Schema is widely understood format
* Good, because many validation libraries available
* Good, because easy to integrate with Python tooling
* Bad, because not graph-native (validates individual nodes, not relationships)
* Bad, because no standard integration with Neo4j
* Bad, because would require custom graph-aware validation layer
* Bad, because less expressive for complex graph constraints

### Cypher queries for validation

* Good, because directly queries Neo4j graph structure
* Good, because no additional frameworks or formats
* Good, because can validate arbitrary graph patterns
* Bad, because requires database connection (cannot validate in CI without infrastructure)
* Bad, because validation logic is procedural, not declarative
* Bad, because Cypher queries don't serve as schema documentation
* Bad, because no standard format for sharing constraints
* Bad, because testing requires full Neo4j instance

### OWL (Web Ontology Language)

* Good, because rich semantic expressiveness
* Good, because automatic inference capabilities
* Good, because established semantic web standard
* Bad, because OWL reasoners are computationally expensive
* Bad, because closed-world assumption conflicts with HCG's open-world model
* Bad, because steeper learning curve than SHACL
* Bad, because less tooling support for Python ecosystem
* Bad, because inference may produce unexpected results

## Implementation Details

### pyshacl Validation (CI/CD)
```python
# tests/phase1/test_shacl_pyshacl.py
from pyshacl import validate

shapes_graph = rdflib.Graph().parse("ontology/shacl_shapes.ttl")
data_graph = rdflib.Graph().parse("tests/fixtures/valid_entity.ttl")

conforms, results_graph, results_text = validate(
    data_graph,
    shacl_graph=shapes_graph,
    inference='rdfs',
    abort_on_first=False
)
```

### Neo4j n10s Validation (Optional Integration Tests)
```cypher
// Validate node against SHACL shapes in Neo4j
CALL n10s.validation.shacl.validate()
YIELD focusNode, propertyShape, value, severity
RETURN focusNode, propertyShape, value, severity
```

### Validation Strategy

| Phase | Validator | Trigger | Purpose |
|-------|-----------|---------|---------|
| **CI/CD** | pyshacl | Every push/PR | Fast schema validation without infrastructure |
| **Integration** | Neo4j n10s | Weekly or on-demand | Comprehensive validation of live graph |
| **Production** | Neo4j n10s | Pre-deployment | Data quality gate before release |

## Links

* Related to [ADR-0001](0001-use-neo4j-for-graph-database.md) - Neo4j integration via n10s
* Implemented in `ontology/shacl_shapes.ttl`
* Test suite in `tests/phase1/test_shacl_pyshacl.py`
* Integration tests in `tests/phase1/test_shacl_neo4j_validation.py`
* CI workflow: `.github/workflows/validate-artifacts.yml`
* Weekly validation: `.github/workflows/shacl-neo4j-validation.yml`

## References

* [SHACL W3C Recommendation](https://www.w3.org/TR/shacl/)
* [pyshacl Documentation](https://github.com/RDFLib/pySHACL)
* [Neo4j neosemantics (n10s)](https://neo4j.com/labs/neosemantics/)
* [SHACL Playground](https://shacl.org/playground/) - Test SHACL shapes online
* Project LOGOS Specification: Section 4.3.1 (SHACL shapes for validation)
* Project LOGOS Specification: Section 6.2 (Validation strategies)
