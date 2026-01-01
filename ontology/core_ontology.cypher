// LOGOS Flexible Ontology - Core Bootstrap
// Single Node label with type, is_type_definition, ancestors properties.
// IS_A edges form type hierarchy.
// See docs/plans/2025-12-30-flexible-ontology-design.md for full specification.

// === Constraints ===
CREATE CONSTRAINT logos_node_uuid IF NOT EXISTS
FOR (n:Node) REQUIRE n.uuid IS UNIQUE;

// === Indexes ===
CREATE INDEX logos_node_type IF NOT EXISTS FOR (n:Node) ON (n.type);
CREATE INDEX logos_node_name IF NOT EXISTS FOR (n:Node) ON (n.name);
CREATE INDEX logos_node_is_type_def IF NOT EXISTS FOR (n:Node) ON (n.is_type_definition);
CREATE INDEX logos_node_type_name IF NOT EXISTS FOR (n:Node) ON (n.type, n.name);

// === Bootstrap: type_definition (self-referential) ===
// The meta-type that all type definitions inherit from
MERGE (td:Node {uuid: "c8d4bdc0-a619-5328-a410-a5fce1cec3c5"})
SET td.name = "type_definition",
    td.is_type_definition = true,
    td.type = "type_definition",
    td.ancestors = []
MERGE (td)-[:IS_A]->(td);

// === Bootstrap: edge_type ===
// Type definition for relationship/edge types
MERGE (et:Node {uuid: "99c56c6a-9666-566f-b12a-5e05c4b00dab"})
SET et.name = "edge_type",
    et.is_type_definition = true,
    et.type = "edge_type",
    et.ancestors = []
WITH et
MATCH (td:Node {uuid: "c8d4bdc0-a619-5328-a410-a5fce1cec3c5"})
MERGE (et)-[:IS_A]->(td);

// === Bootstrap: thing ===
// Root type for concrete/physical entities
MERGE (th:Node {uuid: "a1234567-89ab-5cde-f012-3456789abcde"})
SET th.name = "thing",
    th.is_type_definition = true,
    th.type = "thing",
    th.ancestors = []
WITH th
MATCH (td:Node {uuid: "c8d4bdc0-a619-5328-a410-a5fce1cec3c5"})
MERGE (th)-[:IS_A]->(td);

// === Bootstrap: concept ===
// Root type for abstract/mental entities (facts, rules, abstractions are concepts)
MERGE (co:Node {uuid: "f8b89a6c-9c3e-5e4d-b2f1-83a4d7e4c5f2"})
SET co.name = "concept",
    co.is_type_definition = true,
    co.type = "concept",
    co.ancestors = []
WITH co
MATCH (td:Node {uuid: "c8d4bdc0-a619-5328-a410-a5fce1cec3c5"})
MERGE (co)-[:IS_A]->(td);

// === Bootstrap: IS_A edge type ===
// The fundamental relationship for type hierarchy
MERGE (isa:Node {uuid: "edge-is_a"})
SET isa.name = "IS_A",
    isa.is_type_definition = true,
    isa.type = "IS_A",
    isa.ancestors = ["edge_type"]
WITH isa
MATCH (et:Node {uuid: "99c56c6a-9666-566f-b12a-5e05c4b00dab"})
MERGE (isa)-[:IS_A]->(et);

// === Bootstrap: COMPONENT_OF edge type ===
// Structural composition relationship
MERGE (cof:Node {uuid: "b3e7f2a1-8c4d-5e6f-9a0b-1c2d3e4f5a6b"})
SET cof.name = "COMPONENT_OF",
    cof.is_type_definition = true,
    cof.type = "COMPONENT_OF",
    cof.ancestors = ["edge_type"]
WITH cof
MATCH (et:Node {uuid: "99c56c6a-9666-566f-b12a-5e05c4b00dab"})
MERGE (cof)-[:IS_A]->(et);

// === Bootstrap: cognition ===
// Root type for internal cognitive structures (CWM, persona, etc.)
MERGE (cog:Node {uuid: "d4a5b6c7-8e9f-5a0b-1c2d-3e4f5a6b7c8d"})
SET cog.name = "cognition",
    cog.is_type_definition = true,
    cog.type = "cognition",
    cog.ancestors = []
WITH cog
MATCH (td:Node {uuid: "c8d4bdc0-a619-5328-a410-a5fce1cec3c5"})
MERGE (cog)-[:IS_A]->(td);

// === Bootstrap: cwm ===
// Causal World Model - grouping type for CWM-A/G/E
MERGE (cwm:Node {uuid: "e5b6c7d8-9f0a-5b1c-2d3e-4f5a6b7c8d9e"})
SET cwm.name = "cwm",
    cwm.is_type_definition = true,
    cwm.type = "cwm",
    cwm.ancestors = ["cognition"]
WITH cwm
MATCH (cog:Node {uuid: "d4a5b6c7-8e9f-5a0b-1c2d-3e4f5a6b7c8d"})
MERGE (cwm)-[:IS_A]->(cog)
MERGE (cwm)-[:COMPONENT_OF]->(cog);

// === Bootstrap: cwm_a ===
// CWM-A: Abstract reasoning - entities, relations, causal rules
MERGE (cwma:Node {uuid: "f6c7d8e9-0a1b-5c2d-3e4f-5a6b7c8d9e0f"})
SET cwma.name = "cwm_a",
    cwma.is_type_definition = true,
    cwma.type = "cwm_a",
    cwma.ancestors = ["cwm", "cognition"]
WITH cwma
MATCH (cwm:Node {uuid: "e5b6c7d8-9f0a-5b1c-2d3e-4f5a6b7c8d9e"})
MERGE (cwma)-[:IS_A]->(cwm);

// === Bootstrap: cwm_g ===
// CWM-G: Grounded - JEPA outputs, sensor predictions, physics
MERGE (cwmg:Node {uuid: "07d8e9f0-1a2b-5c3d-4e5f-6a7b8c9d0e1f"})
SET cwmg.name = "cwm_g",
    cwmg.is_type_definition = true,
    cwmg.type = "cwm_g",
    cwmg.ancestors = ["cwm", "cognition"]
WITH cwmg
MATCH (cwm:Node {uuid: "e5b6c7d8-9f0a-5b1c-2d3e-4f5a6b7c8d9e"})
MERGE (cwmg)-[:IS_A]->(cwm);

// === Bootstrap: cwm_e ===
// CWM-E: Emotional - persona state, sentiment, reflections
MERGE (cwme:Node {uuid: "18e9f0a1-2b3c-5d4e-5f6a-7b8c9d0e1f2a"})
SET cwme.name = "cwm_e",
    cwme.is_type_definition = true,
    cwme.type = "cwm_e",
    cwme.ancestors = ["cwm", "cognition"]
WITH cwme
MATCH (cwm:Node {uuid: "e5b6c7d8-9f0a-5b1c-2d3e-4f5a6b7c8d9e"})
MERGE (cwme)-[:IS_A]->(cwm);

// === Bootstrap: persona ===
// Persona type - identity/character configurations
MERGE (per:Node {uuid: "29f0a1b2-3c4d-5e5f-6a7b-8c9d0e1f2a3b"})
SET per.name = "persona",
    per.is_type_definition = true,
    per.type = "persona",
    per.ancestors = ["cognition"]
WITH per
MATCH (cog:Node {uuid: "d4a5b6c7-8e9f-5a0b-1c2d-3e4f5a6b7c8d"})
MERGE (per)-[:IS_A]->(cog)
MERGE (per)-[:COMPONENT_OF]->(cog);

// === Node Structure ===
// All nodes have:
//   uuid: str                - Required, unique identifier
//   name: str                - Required, human-readable name
//   is_type_definition: bool - Required, true for types, false for instances
//   type: str                - Required, immediate type name
//   ancestors: list[str]     - Required, inheritance chain to bootstrap root

// === Query Patterns ===
// All type definitions:
//   MATCH (n:Node {is_type_definition: true})
//
// All instances of a type:
//   MATCH (n:Node {type: "robot_state", is_type_definition: false})
//
// All states (including subtypes):
//   MATCH (n:Node) WHERE n.type = "state" OR "state" IN n.ancestors
//
// Is X a concept?
//   MATCH (n:Node {name: "X"}) RETURN "concept" IN n.ancestors

// === Type Creation Pattern ===
// New types are created by Sophia as data nodes:
//
// Create a new type under 'concept':
//   MATCH (parent:Node {name: "concept"})
//   CREATE (t:Node {
//     uuid: "type-my_new_type",
//     name: "my_new_type",
//     is_type_definition: true,
//     type: "my_new_type",
//     ancestors: ["concept"]
//   })-[:IS_A]->(parent)
//
// Create an instance:
//   MATCH (t:Node {name: "my_new_type"})
//   CREATE (n:Node {
//     uuid: "instance-123",
//     name: "specific_instance",
//     is_type_definition: false,
//     type: "my_new_type",
//     ancestors: ["my_new_type", "concept"]
//   })-[:IS_A]->(t)

RETURN "LOGOS flexible ontology bootstrap complete";
