// LOGOS Flexible Ontology - Core Bootstrap
// Flat vocabulary: all leaf types are direct children of root.
// Sophia discovers hierarchy through graph analysis (community detection,
// node similarity) and creates supertypes organically.
// See docs/plans/2025-12-30-flexible-ontology-design.md for full specification.

// === Constraints ===
CREATE CONSTRAINT logos_node_uuid IF NOT EXISTS
FOR (n:Node) REQUIRE n.uuid IS UNIQUE;

// === Indexes ===
CREATE INDEX logos_node_type IF NOT EXISTS FOR (n:Node) ON (n.type);
CREATE INDEX logos_node_name IF NOT EXISTS FOR (n:Node) ON (n.name);
CREATE INDEX logos_node_relation IF NOT EXISTS FOR (n:Node) ON (n.relation);
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

// === Bootstrap: IS_A edge type ===
// The fundamental relationship for type hierarchy
MERGE (isa:Node {uuid: "87e0d3c8-1f86-5f0c-b1b2-5bfe5cef3b73"})
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

// === Bootstrap: root ===
// Single root type — all leaf types are direct children.
// No intermediate groupings. Sophia discovers hierarchy organically.
MERGE (r:Node {uuid: "a1234567-89ab-5cde-f012-3456789abcde"})
SET r.name = "root",
    r.is_type_definition = true,
    r.type = "root",
    r.ancestors = []
WITH r
MATCH (td:Node {uuid: "c8d4bdc0-a619-5328-a410-a5fce1cec3c5"})
MERGE (r)-[:IS_A]->(td);

// === Node Structure ===
// All nodes have:
//   uuid: str                - Required, unique identifier
//   name: str                - Required, human-readable name
//   is_type_definition: bool - Required, true for types, false for instances
//   type: str                - Required, immediate type name
//   ancestors: list[str]     - Required, inheritance chain to root

// === Query Patterns ===
// All type definitions:
//   MATCH (n:Node {is_type_definition: true})
//
// All instances of a type:
//   MATCH (n:Node {type: "state", is_type_definition: false})
//
// All nodes of a type (flat — no subtypes to worry about):
//   MATCH (n:Node {type: "state"})
//
// Type creation (sophia discovers and adds supertypes):
//   MATCH (parent:Node {name: "root"})
//   CREATE (t:Node {
//     uuid: "type-my_new_type",
//     name: "my_new_type",
//     is_type_definition: true,
//     type: "my_new_type",
//     ancestors: ["root"]
//   })-[:IS_A]->(parent)

RETURN "LOGOS flexible ontology bootstrap complete";
