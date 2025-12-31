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
