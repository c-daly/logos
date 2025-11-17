# Pick-and-Place Ontology Extension

This document describes the ontology extension for the pick-and-place robotic manipulation scenario.

## Overview

The extended ontology defines entities, concepts, states, processes, and relationships for a simple pick-and-place scenario where a robotic manipulator picks objects from a table and places them in a target location.

## Entity Types

### Robot Components
- **Manipulator** (`Entity:RobotArm`) - The robotic arm capable of movement
- **Gripper** (`Entity:Gripper`) - End-effector for grasping objects
- **Joint** (`Entity:Joint`) - Articulated joints of the manipulator

### Workspace Components
- **Surface** (`Entity:Table`, `Entity:Bin`) - Planar surfaces for object placement
- **Workspace** - Physical region accessible to the manipulator

### Graspable Objects
- **GraspableObject** (`Entity:Block`, `Entity:Cylinder`) - Objects that can be picked up
- **Container** (`Entity:Bin`) - Objects that can hold other objects

## Concept Hierarchy

```
Concept
├── Manipulator
│   └── Gripper
├── RigidBody
│   └── GraspableObject
│       └── Container
├── Surface
├── Workspace
├── Location
├── GraspAction (Process category)
├── ReleaseAction (Process category)
├── MoveAction (Process category)
├── PlaceAction (Process category)
├── GraspedState (State category)
├── FreeState (State category)
└── PositionedState (State category)
```

## Relationship Types

### Core Relationships (Section 4.1)
- **IS_A**: `(:Entity)-[:IS_A]->(:Concept)` - Type membership
- **HAS_STATE**: `(:Entity)-[:HAS_STATE]->(:State)` - Current state
- **CAUSES**: `(:Process)-[:CAUSES]->(:State)` - Causal relationship
- **PART_OF**: `(:Entity)-[:PART_OF]->(:Entity)` - Compositional hierarchy

### Extended Relationships
- **LOCATED_AT**: `(:Entity)-[:LOCATED_AT]->(:Entity)` - Spatial relationship
- **ATTACHED_TO**: `(:Entity)-[:ATTACHED_TO]->(:Entity)` - Physical attachment
- **PRECEDES**: `(:State)-[:PRECEDES]->(:State)` - Temporal ordering
- **REQUIRES**: `(:Process)-[:REQUIRES]->(:State)` - Precondition
- **CAN_PERFORM**: `(:Entity)-[:CAN_PERFORM]->(:Concept)` - Capability

## Property Schemas

### Entity Properties
Common properties for all entities:
- `uuid` (string, required) - Unique identifier (format: `entity-*`)
- `name` (string) - Human-readable name
- `description` (string) - Detailed description
- `created_at` (datetime) - Creation timestamp

### Spatial Properties
For physical objects:
- `width` (decimal) - Width in meters
- `height` (decimal) - Height in meters
- `depth` (decimal) - Depth in meters
- `radius` (decimal) - Radius in meters (for cylindrical objects)
- `mass` (decimal) - Mass in kilograms

### Gripper Properties
- `max_grasp_width` (decimal) - Maximum opening width in meters
- `max_force` (decimal) - Maximum grasping force in Newtons

### Joint Properties
- `joint_type` (string) - Type: "revolute", "prismatic", "fixed", or "continuous"
- `min_angle` (decimal) - Minimum angle in radians
- `max_angle` (decimal) - Maximum angle in radians

### State Properties
Common properties for all states:
- `uuid` (string, required) - Unique identifier (format: `state-*`)
- `name` (string) - Human-readable name
- `timestamp` (datetime, required) - When the state occurred

Spatial state properties:
- `position_x`, `position_y`, `position_z` (decimal) - Position in workspace
- `orientation_roll`, `orientation_pitch`, `orientation_yaw` (decimal) - Orientation angles

Object state properties:
- `is_grasped` (boolean) - Whether object is being held
- `is_empty` (boolean) - Whether container is empty

Gripper state properties:
- `is_closed` (boolean) - Whether gripper is closed
- `grasp_width` (decimal) - Current opening width
- `applied_force` (decimal) - Current force being applied

### Process Properties
- `uuid` (string, required) - Unique identifier (format: `process-*`)
- `name` (string) - Human-readable name
- `description` (string) - Detailed description
- `start_time` (datetime, required) - When process started
- `duration_ms` (integer) - Duration in milliseconds

## Test Data

The `test_data_pick_and_place.cypher` script creates a complete pick-and-place scenario:

### Entities Created
- Robot arm with gripper and 3 joints
- Work table with target bin
- Three graspable objects (red block, blue block, green cylinder)

### Example Process Flow
1. **Initial State**: Objects on table, gripper open, arm at home position
2. **Move to Pre-grasp**: Arm moves above red block
3. **Grasp**: Gripper closes around red block
4. **Move to Place**: Arm carries block to bin location
5. **Release**: Gripper opens, releasing block into bin

### Causal Chain
The test data demonstrates:
- Temporal ordering via `PRECEDES` relationships
- Causal relationships via `CAUSES` relationships
- Preconditions via `REQUIRES` relationships
- State transitions through the complete pick-and-place sequence

## Usage

### Load Core Ontology
```cypher
// Load constraints and concepts
:source ontology/core_ontology.cypher
```

### Load Test Data
```cypher
// Populate test scenario
:source ontology/test_data_pick_and_place.cypher
```

### Query Examples

#### Find all graspable objects
```cypher
MATCH (e:Entity)-[:IS_A]->(c:Concept {name: 'GraspableObject'})
RETURN e.name, e.uuid
```

#### Get current state of an entity
```cypher
MATCH (e:Entity {name: 'RedBlock01'})-[:HAS_STATE]->(s:State)
RETURN s
ORDER BY s.timestamp DESC
LIMIT 1
```

#### Trace causal chain of a process
```cypher
MATCH path = (p:Process {name: 'GraspRedBlock'})-[:CAUSES*1..3]->(s:State)
RETURN path
```

#### Find all processes that require a specific state
```cypher
MATCH (p:Process)-[:REQUIRES]->(s:State {name: 'ArmPreGraspState'})
RETURN p.name, p.description
```

## Validation

The SHACL shapes in `shacl_shapes.ttl` enforce:
- UUID format constraints (e.g., entity UUIDs must start with "entity-")
- Required fields (uuid, timestamps)
- Data type constraints
- Value range constraints (e.g., mass >= 0)
- Enumerated values (e.g., joint_type must be one of defined types)
- Relationship constraints

## Future Extensions

This ontology can be extended with:
- Additional object types (deformable objects, articulated objects)
- Force and torque sensing
- Collision detection and avoidance
- Multi-arm coordination
- Vision-based object recognition
- Trajectory planning and optimization
