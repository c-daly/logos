# Copilot Instructions for Project LOGOS

## Project Overview

Project LOGOS is a foundational research initiative building a non-linguistic cognitive architecture for autonomous agents. The system uses a Hybrid Causal Graph (HCG) for knowledge representation, combining symbolic reasoning with vector-based semantic search.

### Core Philosophy
- **Non-linguistic cognition first**: Internal reasoning occurs in abstract causal graph structures, not natural language
- **Language as interface**: Natural language is treated as an I/O modality, not the substrate of thought
- **Causal coherence**: All reasoning maintains explicit causal relationships and temporal ordering
- **Validation by constraint**: Multi-level validation ensures logical consistency

## Repository Structure

This is the LOGOS meta-repository serving as the canonical source of truth for:
- `/docs/spec/` - Formal specifications and design documents (see `project_logos_full.md`)
- `/ontology/` - HCG ontology definition (`core_ontology.cypher`) and validation constraints (`shacl_shapes.ttl`)
- `/contracts/` - API contracts in OpenAPI format (`hermes.openapi.yaml`)
- `/infra/` - Development infrastructure (docker-compose configurations)

## Ecosystem Components

The LOGOS ecosystem consists of five components (all in separate repositories):
1. **Sophia** (`c-daly/sophia`) - Non-linguistic cognitive core with Orchestrator, CWM-A, CWM-G, Planner, and Executor
2. **Hermes** (`c-daly/hermes`) - Stateless language & embedding utility (STT, TTS, NLP, text embeddings)
3. **Talos** (`c-daly/talos`) - Hardware abstraction layer for sensors/actuators
4. **Apollo** (`c-daly/apollo`) - Thin client UI and command layer
5. **LOGOS** (this repo) - Foundry and canonical source of truth

## General Guidelines

### Working with HCG Ontology
- The HCG ontology uses **Neo4j** (graph database) + **Milvus** (vector store)
- Four primary node types: `Entity`, `Concept`, `State`, `Process`
- All constraints and relationships must maintain causal coherence
- UUID constraints are enforced for all node types
- Follow the patterns defined in `ontology/core_ontology.cypher`

### Cypher Query Language
- Use parameterized queries to prevent injection attacks
- Always include UUID uniqueness constraints when creating new nodes
- Follow the relationship patterns: `[:IS_A]`, `[:HAS_STATE]`, `[:CAUSES]`, `[:PART_OF]`
- Include descriptive comments explaining the purpose of complex queries
- Reference Section 4.1 of the spec for ontology structure

### SHACL Shapes and Validation
- SHACL shapes in `ontology/shacl_shapes.ttl` serve as Level 1 deterministic validation guardrails
- All shape definitions must align with the ontology structure
- Use RDF/Turtle syntax consistently
- Include human-readable labels and descriptions for all shapes

### OpenAPI Contracts
- The Hermes API contract is the canonical reference in `contracts/hermes.openapi.yaml`
- Follow OpenAPI 3.1.0 specification
- All endpoints must be stateless (no HCG access)
- Include comprehensive descriptions for all endpoints, parameters, and responses
- Reference Table 2 in Section 3.4 of the spec for endpoint definitions

### Documentation
- All specification updates must reference section numbers from `docs/spec/project_logos_full.md`
- Use clear, concise language focusing on causal relationships
- Include examples where appropriate
- Maintain consistency with the non-linguistic cognitive architecture philosophy

### Docker Infrastructure
- Development environment uses `infra/docker-compose.hcg.dev.yml`
- Neo4j accessible on ports 7474 (HTTP) and 7687 (Bolt)
- Milvus accessible on ports 19530 and 9091
- Include neosemantics/SHACL support requirements for Neo4j

## File Naming and Organization

- Use snake_case for Cypher and SHACL files: `core_ontology.cypher`, `shacl_shapes.ttl`
- Use kebab-case for configuration files: `docker-compose.hcg.dev.yml`
- Use dot notation for OpenAPI files: `hermes.openapi.yaml`
- Prefix all LOGOS-specific constraints with `logos_`

## Code Style and Conventions

### Cypher Scripts
- Include file header comments with purpose and spec reference
- Use descriptive constraint and relationship names
- Group related constraints together with section comments
- End scripts with meaningful RETURN statements

### YAML Files (OpenAPI, Docker Compose)
- Use 2-space indentation
- Include inline comments for complex configurations
- Maintain alphabetical ordering of keys where logical
- Include version numbers and descriptions

### Markdown Documentation
- Use ATX-style headers (`#`, `##`, etc.)
- Include table of contents for documents over 100 lines
- Use code blocks with language identifiers
- Cross-reference specification sections explicitly

## Phase 1 Constraints

This repository is targeted at **Phase 1: Formalize HCG and Abstract Pipeline**
- Focus on ontology scaffolds, not full implementations
- Keep examples minimal but syntactically valid
- Include comments indicating where full implementations will be extended
- Ensure all artifacts are development-ready but intentionally incomplete

## Integration Points

- All components must reference this repository for authoritative definitions
- Changes to ontology or contracts require updates to dependent repositories
- The spec document (`project_logos_full.md`) is the source of truth for design decisions
- Infrastructure changes should maintain backward compatibility during Phase 1

## Quality Standards

- All Cypher scripts must be syntactically valid and executable against Neo4j
- SHACL shapes must validate successfully with RDF tools
- OpenAPI specifications must pass validation tools
- Docker configurations must successfully start the development environment
- Documentation must be clear enough for new team members to understand the architecture

## Common Patterns

### Creating New Ontology Nodes
```cypher
CREATE CONSTRAINT logos_<nodetype>_uuid IF NOT EXISTS
FOR (n:NodeType)
REQUIRE n.uuid IS UNIQUE;
```

### Defining SHACL Shapes
Include `sh:targetClass`, `sh:property`, `sh:minCount`, `sh:maxCount`, and descriptive labels.

### Adding OpenAPI Endpoints
Follow the stateless pattern with clear request/response schemas and operation IDs.
