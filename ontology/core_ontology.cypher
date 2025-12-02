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

//// Phase 2: PersonaEntry and EmotionState node constraints
CREATE CONSTRAINT logos_persona_entry_uuid IF NOT EXISTS
FOR (pe:PersonaEntry)
REQUIRE pe.uuid IS UNIQUE;

CREATE CONSTRAINT logos_emotion_state_uuid IF NOT EXISTS
FOR (es:EmotionState)
REQUIRE es.uuid IS UNIQUE;

//// Phase 2: Capability catalog node constraints (logos#284)
CREATE CONSTRAINT logos_capability_uuid IF NOT EXISTS
FOR (cap:Capability)
REQUIRE cap.uuid IS UNIQUE;

CREATE CONSTRAINT logos_capability_name IF NOT EXISTS
FOR (cap:Capability)
REQUIRE cap.name IS UNIQUE;

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

//// Phase 2: Indexes for PersonaEntry and EmotionState
CREATE INDEX logos_persona_entry_timestamp IF NOT EXISTS
FOR (pe:PersonaEntry)
ON (pe.timestamp);

CREATE INDEX logos_emotion_state_timestamp IF NOT EXISTS
FOR (es:EmotionState)
ON (es.timestamp);

//// Phase 2: Indexes for Capability catalog (logos#284)
CREATE INDEX logos_capability_name IF NOT EXISTS
FOR (cap:Capability)
ON (cap.name);

CREATE INDEX logos_capability_executor_type IF NOT EXISTS
FOR (cap:Capability)
ON (cap.executor_type);

CREATE INDEX logos_capability_tags IF NOT EXISTS
FOR (cap:Capability)
ON (cap.capability_tags);

//// Phase 2 P2-M3: Perception and Imagination node constraints (CWM-G)
CREATE CONSTRAINT logos_perception_frame_uuid IF NOT EXISTS
FOR (pf:PerceptionFrame)
REQUIRE pf.uuid IS UNIQUE;

CREATE CONSTRAINT logos_imagined_process_uuid IF NOT EXISTS
FOR (ip:ImaginedProcess)
REQUIRE ip.uuid IS UNIQUE;

CREATE CONSTRAINT logos_imagined_state_uuid IF NOT EXISTS
FOR (is:ImaginedState)
REQUIRE is.uuid IS UNIQUE;

//// CWM-A: Abstract/Associative World Model node constraints
CREATE CONSTRAINT logos_fact_uuid IF NOT EXISTS
FOR (f:Fact)
REQUIRE f.uuid IS UNIQUE;

CREATE CONSTRAINT logos_association_uuid IF NOT EXISTS
FOR (a:Association)
REQUIRE a.uuid IS UNIQUE;

CREATE CONSTRAINT logos_abstraction_uuid IF NOT EXISTS
FOR (abs:Abstraction)
REQUIRE abs.uuid IS UNIQUE;

CREATE CONSTRAINT logos_rule_uuid IF NOT EXISTS
FOR (r:Rule)
REQUIRE r.uuid IS UNIQUE;

CREATE CONSTRAINT logos_abstraction_name IF NOT EXISTS
FOR (abs:Abstraction)
REQUIRE abs.name IS UNIQUE;

CREATE CONSTRAINT logos_rule_name_domain IF NOT EXISTS
FOR (r:Rule)
REQUIRE (r.name, r.domain) IS UNIQUE;

//// Phase 2 P2-M3: Indexes for perception and imagination (CWM-G)
CREATE INDEX logos_perception_frame_timestamp IF NOT EXISTS
FOR (pf:PerceptionFrame)
ON (pf.timestamp);

CREATE INDEX logos_imagined_process_timestamp IF NOT EXISTS
FOR (ip:ImaginedProcess)
ON (ip.timestamp);

CREATE INDEX logos_imagined_state_step IF NOT EXISTS
FOR (is:ImaginedState)
ON (is.step);

//// CWM-A: Indexes for facts, associations, rules
CREATE INDEX logos_fact_subject IF NOT EXISTS
FOR (f:Fact)
ON (f.subject);

CREATE INDEX logos_fact_predicate IF NOT EXISTS
FOR (f:Fact)
ON (f.predicate);

CREATE INDEX logos_fact_status IF NOT EXISTS
FOR (f:Fact)
ON (f.status);

CREATE INDEX logos_fact_confidence IF NOT EXISTS
FOR (f:Fact)
ON (f.confidence);

CREATE INDEX logos_association_source IF NOT EXISTS
FOR (a:Association)
ON (a.source_concept);

CREATE INDEX logos_association_target IF NOT EXISTS
FOR (a:Association)
ON (a.target_concept);

CREATE INDEX logos_association_strength IF NOT EXISTS
FOR (a:Association)
ON (a.strength);

CREATE INDEX logos_rule_type IF NOT EXISTS
FOR (r:Rule)
ON (r.rule_type);

CREATE INDEX logos_rule_domain IF NOT EXISTS
FOR (r:Rule)
ON (r.domain);

CREATE INDEX logos_abstraction_domain IF NOT EXISTS
FOR (abs:Abstraction)
ON (abs.domain);

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

//// Phase 2: Extended relationship types for persona and emotions
//// - (:PersonaEntry)-[:RELATES_TO]->(:Process) — Diary entry linked to process
//// - (:EmotionState)-[:TAGGED_ON]->(:Process) — Emotion tag on process
//// - (:EmotionState)-[:TAGGED_ON]->(:Entity) — Emotion tag on entity
//// - (:EmotionState)-[:GENERATED_BY]->(:PersonaEntry) — Emotion derived from reflection

//// Phase 2 P2-M3: Extended relationship types for perception and imagination (CWM-G)
//// - (:PerceptionFrame)-[:TRIGGERED_SIMULATION]->(:ImaginedProcess) — Frame that initiated simulation
//// - (:ImaginedProcess)-[:PREDICTS]->(:ImaginedState) — Process predicting future state
//// - (:ImaginedState)-[:PRECEDES]->(:ImaginedState) — Temporal ordering of imagined states

//// CWM-A: Relationship types for abstract/associative world model
//// - (:Fact)-[:ABOUT]->(:Concept|:Entity) — Fact concerns this node
//// - (:Fact)-[:SUPPORTS]->(:Process) — Fact supports plan step
//// - (:Fact)-[:CONTRADICTS]->(:Fact) — Facts in conflict
//// - (:Fact)-[:SUPERSEDES]->(:Fact) — Newer fact replaces older
//// - (:Fact)-[:DERIVED_FROM]->(:Fact|:PerceptionFrame) — Provenance
//// - (:Fact)-[:INFERRED_FROM]->(:Fact) — Derived via inference
//// - (:Association)-[:CONNECTS]->(:Concept) — Association links concepts
//// - (:Association)-[:LEARNED_FROM]->(:Process) — How association was learned
//// - (:Abstraction)-[:GENERALIZES]->(:Concept) — Lower-level concepts
//// - (:Abstraction)-[:PART_OF]->(:Abstraction) — Abstraction hierarchy
//// - (:Rule)-[:APPLIES_TO]->(:Concept|:Entity) — Rule scope
//// - (:Rule)-[:TRIGGERS]->(:Rule) — Chained rules
//// - (:Rule)-[:CONFLICTS_WITH]->(:Rule) — Mutually exclusive rules
//// - (:Rule)-[:PART_OF]->(:Abstraction) — Rule grouped under abstraction

//// Phase 2: Extended relationship types for capability catalog (logos#284)
//// - (:Capability)-[:IMPLEMENTS]->(:Concept) — Capability implements action concept (e.g., GraspAction)
//// - (:Capability)-[:REQUIRES_INPUT]->(:Concept) — Input type required by capability
//// - (:Capability)-[:PRODUCES_OUTPUT]->(:Concept) — Output type produced by capability
//// - (:Capability)-[:EXECUTED_BY]->(:Entity) — Entity that can execute this capability
//// - (:Process)-[:USES_CAPABILITY]->(:Capability) — Plan step uses specific capability

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
//// Phase 2: PersonaEntry Properties (Section 3.4 - Diagnostics & Persona):
////   Required: uuid, timestamp
////   Optional: summary (text summary of activity), 
////            sentiment (e.g., "confident", "cautious", "neutral"),
////            related_process (UUID of linked Process)
////
//// Phase 2: EmotionState Properties (CWM-E reflection tags):
////   Required: uuid, timestamp
////   Optional: emotion_type (e.g., "confident", "cautious", "curious"),
////            intensity (0.0-1.0 confidence/strength),
////            context (brief description),
////            source (what triggered this emotion tag)
////
//// CWM-A: Fact Properties (declarative statements):
////   Required: uuid, subject, predicate, object, confidence, status
////   Optional: source (where fact came from),
////            source_type (knowledge_base|observation|inference|human),
////            valid_from (temporal validity start),
////            valid_until (temporal validity end),
////            domain (knowledge domain),
////            created_at, updated_at (timestamps)
////
//// CWM-A: Association Properties (weighted links between concepts):
////   Required: uuid, source_concept, target_concept, strength
////   Optional: relationship_type (type of association),
////            bidirectional (is relationship symmetric),
////            context (where valid),
////            source (how learned),
////            decay_rate (strength decay per day),
////            created_at (timestamp)
////
//// CWM-A: Abstraction Properties (higher-order concepts):
////   Required: uuid, name
////   Optional: description (human description),
////            level (hierarchy level, 0=concrete),
////            domain (knowledge domain),
////            created_at (timestamp)
////
//// CWM-A: Rule Properties (conditional inference rules):
////   Required: uuid, name, condition, consequent, rule_type
////   Optional: priority (higher = more important),
////            confidence (rule reliability),
////            domain (applicable domain),
////            created_at (timestamp)
////
//// Phase 2: Capability Properties (logos#284 - Capability Catalog):
////   Required: uuid, name, executor_type
////   Core: executor_type (enum: human|talos|service|llm),
////         description (what the capability does),
////         capability_tags (list of string tags for discovery)
////   Performance: estimated_duration_ms, estimated_cost,
////                success_rate (0.0-1.0), invocation_count
////   Versioning: version, created_at, updated_at, deprecated (boolean)
////   Integration: service_endpoint (for service type),
////                action_name (for talos type),
////                instruction_template (for human type)
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

//// Phase 2: Capability Catalog - Executor Type Concepts (logos#284)
//// These define the abstract executor categories for capabilities

MERGE (executor_type:Concept {uuid: 'concept-executor-type', name: 'ExecutorType'})
ON CREATE SET executor_type.description = 'Abstract category for capability executors';

MERGE (human_executor:Concept {uuid: 'concept-executor-human', name: 'HumanExecutor'})
ON CREATE SET human_executor.description = 'Capabilities executed by human operators with instructions';

MERGE (talos_executor:Concept {uuid: 'concept-executor-talos', name: 'TalosExecutor'})
ON CREATE SET talos_executor.description = 'Capabilities executed by Talos robotic system';

MERGE (service_executor:Concept {uuid: 'concept-executor-service', name: 'ServiceExecutor'})
ON CREATE SET service_executor.description = 'Capabilities executed via external service/API calls';

MERGE (llm_executor:Concept {uuid: 'concept-executor-llm', name: 'LLMExecutor'})
ON CREATE SET llm_executor.description = 'Capabilities executed by language model reasoning';

// Establish executor type hierarchy
MERGE (human_executor)-[:IS_A]->(executor_type);
MERGE (talos_executor)-[:IS_A]->(executor_type);
MERGE (service_executor)-[:IS_A]->(executor_type);
MERGE (llm_executor)-[:IS_A]->(executor_type);

//// Phase 2: Input/Output Type Concepts for Capability Catalog
MERGE (input_type:Concept {uuid: 'concept-input-type', name: 'InputType'})
ON CREATE SET input_type.description = 'Abstract category for capability input types';

MERGE (output_type:Concept {uuid: 'concept-output-type', name: 'OutputType'})
ON CREATE SET output_type.description = 'Abstract category for capability output types';

// Common input/output types
MERGE (text_input:Concept {uuid: 'concept-input-text', name: 'TextInput'})
ON CREATE SET text_input.description = 'Text string input';
MERGE (text_input)-[:IS_A]->(input_type);

MERGE (entity_ref_input:Concept {uuid: 'concept-input-entity-ref', name: 'EntityRefInput'})
ON CREATE SET entity_ref_input.description = 'Reference to an entity in HCG';
MERGE (entity_ref_input)-[:IS_A]->(input_type);

MERGE (location_input:Concept {uuid: 'concept-input-location', name: 'LocationInput'})
ON CREATE SET location_input.description = 'Spatial location coordinates';
MERGE (location_input)-[:IS_A]->(input_type);

MERGE (state_output:Concept {uuid: 'concept-output-state', name: 'StateOutput'})
ON CREATE SET state_output.description = 'New state produced by capability';
MERGE (state_output)-[:IS_A]->(output_type);

MERGE (text_output:Concept {uuid: 'concept-output-text', name: 'TextOutput'})
ON CREATE SET text_output.description = 'Text string output';
MERGE (text_output)-[:IS_A]->(output_type);

MERGE (boolean_output:Concept {uuid: 'concept-output-boolean', name: 'BooleanOutput'})
ON CREATE SET boolean_output.description = 'Success/failure boolean output';
MERGE (boolean_output)-[:IS_A]->(output_type);

RETURN "core ontology extended with pick-and-place domain and capability catalog (no-op if already present)";
