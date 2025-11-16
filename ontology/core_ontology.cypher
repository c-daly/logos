// LOGOS HCG Core Ontology Scaffold
// See Project LOGOS spec: Section 4.1 (Core Ontology and Data Model).
// Minimal, syntactically valid scaffold to be extended per Appendix A.

//// Identity constraints
CREATE CONSTRAINT logos_entity_uuid IF NOT EXISTS
FOR (e:Entity)
REQUIRE e.uuid IS UNIQUE;

CREATE CONSTRAINT logos_concept_uuid IF NOT EXISTS
FOR (c:Concept)
REQUIRE c.uuid IS UNIQUE;

CREATE CONSTRAINT logos_state_uuid IF NOT EXISTS
FOR (s:State)
REQUIRE s.uuid IS UNIQUE;

CREATE CONSTRAINT logos_process_uuid IF NOT EXISTS
FOR (p:Process)
REQUIRE p.uuid IS UNIQUE;

//// Concept uniqueness
CREATE CONSTRAINT logos_concept_name IF NOT EXISTS
FOR (c:Concept)
REQUIRE c.name IS UNIQUE;

//// Example base relationships (scaffold)
//// - (:Entity)-[:IS_A]->(:Concept)
//// - (:Entity)-[:HAS_STATE]->(:State)
//// - (:Process)-[:CAUSES]->(:State)
//// - (:Entity)-[:PART_OF]->(:Entity)
//// Fill in the full ontology and relationship types according to Appendix A of the spec.

RETURN "core ontology scaffold created (no-op if constraints already present)";
