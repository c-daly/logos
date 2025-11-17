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

//// Entity property indexes for efficient querying
CREATE INDEX logos_entity_name IF NOT EXISTS
FOR (e:Entity)
ON (e.name);

CREATE INDEX logos_state_timestamp IF NOT EXISTS
FOR (s:State)
ON (s.timestamp);

CREATE INDEX logos_process_timestamp IF NOT EXISTS
FOR (p:Process)
ON (p.start_time);

//// Base relationship types (Section 4.1)
//// - (:Entity)-[:IS_A]->(:Concept) — Type membership
//// - (:Entity)-[:HAS_STATE]->(:State) — Current state
//// - (:Process)-[:CAUSES]->(:State) — Causal relationship
//// - (:Entity)-[:PART_OF]->(:Entity) — Compositional hierarchy

//// Extended relationship types for pick-and-place domain
//// - (:Entity)-[:LOCATED_AT]->(:Entity) — Spatial relationship
//// - (:Entity)-[:ATTACHED_TO]->(:Entity) — Physical attachment
//// - (:State)-[:PRECEDES]->(:State) — Temporal ordering
//// - (:Process)-[:REQUIRES]->(:State) — Precondition
//// - (:Entity)-[:CAN_PERFORM]->(:Concept) — Capability

//// Property Schemas by Node Type (see ontology/README_PICK_AND_PLACE.md for details)
////
//// Entity Properties:
////   Common: uuid (required), name, description, created_at
////   Spatial: width, height, depth, radius, mass (all decimal, >= 0)
////   Gripper: max_grasp_width, max_force (decimal, >= 0)
////   Joint: joint_type (enum: revolute|prismatic|fixed|continuous), min_angle, max_angle (decimal)
////
//// Concept Properties:
////   Required: uuid, name
////   Optional: description
////
//// State Properties:
////   Required: uuid, timestamp
////   Optional: name, position_x/y/z, orientation_roll/pitch/yaw,
////            is_grasped, is_closed, is_empty, grasp_width, applied_force
////
//// Process Properties:
////   Required: uuid, start_time
////   Optional: name, description, duration_ms
////
//// See shacl_shapes.ttl for validation constraints

//// Pick-and-Place Domain Concepts
//// These define the abstract categories for the pick-and-place scenario

// Core Manipulator Concepts
MERGE (manipulator:Concept {uuid: 'concept-manipulator', name: 'Manipulator'})
ON CREATE SET manipulator.description = 'Abstract concept of robotic manipulator';

MERGE (gripper:Concept {uuid: 'concept-gripper', name: 'Gripper'})
ON CREATE SET gripper.description = 'Abstract concept of end-effector for grasping';

MERGE (joint:Concept {uuid: 'concept-joint', name: 'Joint'})
ON CREATE SET joint.description = 'Abstract concept of articulated joint';

// Object Concepts
MERGE (graspable:Concept {uuid: 'concept-graspable', name: 'GraspableObject'})
ON CREATE SET graspable.description = 'Object that can be grasped by manipulator';

MERGE (container:Concept {uuid: 'concept-container', name: 'Container'})
ON CREATE SET container.description = 'Object that can hold other objects';

MERGE (rigid_body:Concept {uuid: 'concept-rigid-body', name: 'RigidBody'})
ON CREATE SET rigid_body.description = 'Physical object with fixed shape';

// Workspace Concepts
MERGE (surface:Concept {uuid: 'concept-surface', name: 'Surface'})
ON CREATE SET surface.description = 'Planar surface for object placement';

MERGE (workspace:Concept {uuid: 'concept-workspace', name: 'Workspace'})
ON CREATE SET workspace.description = 'Physical region accessible to manipulator';

MERGE (location:Concept {uuid: 'concept-location', name: 'Location'})
ON CREATE SET location.description = 'Spatial position in workspace';

// Action Concepts (Process categories)
MERGE (grasp_action:Concept {uuid: 'concept-grasp', name: 'GraspAction'})
ON CREATE SET grasp_action.description = 'Action of grasping an object';

MERGE (release_action:Concept {uuid: 'concept-release', name: 'ReleaseAction'})
ON CREATE SET release_action.description = 'Action of releasing a grasped object';

MERGE (move_action:Concept {uuid: 'concept-move', name: 'MoveAction'})
ON CREATE SET move_action.description = 'Action of moving manipulator or object';

MERGE (place_action:Concept {uuid: 'concept-place', name: 'PlaceAction'})
ON CREATE SET place_action.description = 'Action of placing object at location';

// State Concepts
MERGE (grasped_state:Concept {uuid: 'concept-grasped', name: 'GraspedState'})
ON CREATE SET grasped_state.description = 'State where object is held by gripper';

MERGE (free_state:Concept {uuid: 'concept-free', name: 'FreeState'})
ON CREATE SET free_state.description = 'State where object is not grasped';

MERGE (positioned_state:Concept {uuid: 'concept-positioned', name: 'PositionedState'})
ON CREATE SET positioned_state.description = 'State with specific spatial position';

// Establish concept hierarchy
MERGE (gripper)-[:IS_A]->(manipulator);
MERGE (container)-[:IS_A]->(graspable);
MERGE (graspable)-[:IS_A]->(rigid_body);

//// Vector Embedding Integration (Section 4.2)
//// Each graph node that requires semantic search maintains:
//// - embedding_id: Reference to vector in Milvus
//// - embedding_model: Model used for embedding generation
//// - last_sync: Timestamp of last vector sync
////
//// Example usage (to be integrated in Phase 1):
//// MERGE (c:Concept {uuid: 'concept-manipulator'})
//// SET c.embedding_id = 'milvus-vector-id-manipulator',
////     c.embedding_model = 'sentence-transformers/all-MiniLM-L6-v2',
////     c.last_sync = datetime();

RETURN "core ontology extended with pick-and-place domain (no-op if already present)";
