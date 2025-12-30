// LOGOS HCG Test Data - Pick and Place Scenario
// See Project LOGOS spec: Section 4.1 (Core Ontology and Data Model).
// This script populates test data for a simple pick-and-place scenario.
// All UUIDs are RFC 4122 compliant for type safety.
//
// FLEXIBLE ONTOLOGY:
// All nodes use the :Node label with:
// - uuid: unique identifier
// - name: human-readable name
// - is_type_definition: boolean (true for types, false for instances)
// - type: immediate type name
// - ancestors: list of ancestor types

//// UUID Reference Table (for human readability):
// Entities:
//   RobotArm01:       c551e7ad-c12a-40bc-8c29-3a721fa311cb
//   Gripper01:        47a157d3-1092-4069-9e39-4e80e6735342
//   Joint01-Base:     43117773-50b8-43fd-9d79-d10017674116
//   Joint02-Shoulder: 6a813f24-eca4-4df3-bc85-228c1d001ee8
//   Joint03-Elbow:    543ccec9-4e43-4ad6-8b47-a5c1766c274f
//   WorkTable01:      f4d97052-466f-4466-bfa7-8df1623969f9
//   TargetBin01:      563e215e-3192-497c-8997-57fb9bba3922
//   RedBlock01:       4338a6cc-c125-4531-ac3b-69eca0751aa0
//   BlueBlock01:      ad892f3e-dd35-48fa-b3c8-4e8316e5fe7a
//   GreenCylinder01:  6f69f9f9-50a7-40e3-b915-b95f31d9a00a
//
// States:
//   ArmHomeState:           1957c02d-a22a-483c-8ccb-cd04e7f03817
//   GripperOpenState:       a906bb2e-4609-449d-9c2b-503976ec48c5
//   RedBlockOnTableState:   0c6bf539-0214-4b9e-a212-3cc8c03de716
//   BlueBlockOnTableState:  7487dec5-6aed-4988-abce-ccd7daa9bc0d
//   GreenCylinderOnTable:   7a12cfd9-d533-46cd-8ecb-f2f1a84cdf69
//   BinEmptyState:          09c15995-3bdb-48c8-af88-056e50285ea6
//   ArmPreGraspState:       4e4faa83-9e53-40c3-8ca5-7799e706afe3
//   RedBlockGraspedState:   f25e11ff-f33f-43a7-a4d8-a2839ec39976
//   ArmPlacePositionState:  7daabd8b-6c39-435f-98cf-d4629cd86e36
//   RedBlockInBinState:     9a329df2-e778-40f9-8b37-f23314f33366
//
// Processes:
//   MoveToPreGraspPosition: 5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd
//   GraspRedBlock:          350e8968-647d-47b3-b2a5-54a6c828256c
//   MoveToPlacePosition:    492d0005-972b-4b3c-9db4-a6e4cdd4b824
//   ReleaseRedBlock:        a843ccc0-c597-424a-a8e9-c5227f1af717
//
// Capabilities:
//   MoveCapability:         6e618722-6812-4c04-a828-add791c83a9b
//   GraspCapability:        96d8b91c-6fab-44ac-867f-81e397368b56
//   ReleaseCapability:      ebee7aab-9cb8-4fa9-8491-ffb9f8490819

//// Type Definitions (these extend the bootstrap types)
// These are type definitions that instances will inherit from

// Entity type (subtype of thing)
MERGE (entity_type:Node {uuid: 'e003e45c-50bd-5e4b-85db-883756ecfcf7'})
ON CREATE SET
    entity_type.name = 'entity',
    entity_type.is_type_definition = true,
    entity_type.type = 'entity',
    entity_type.ancestors = ['thing'];

// Manipulator type (subtype of entity)
MERGE (manip:Node {uuid: '3bed753e-51ad-5f8f-bb3a-1f7dc39ae01c'})
ON CREATE SET
    manip.name = 'Manipulator',
    manip.is_type_definition = true,
    manip.type = 'Manipulator',
    manip.ancestors = ['entity', 'thing'];

// Gripper type (subtype of entity)
MERGE (grip_type:Node {uuid: '4f753e84-47ef-5f42-a490-bc4dc4910dfb'})
ON CREATE SET
    grip_type.name = 'Gripper',
    grip_type.is_type_definition = true,
    grip_type.type = 'Gripper',
    grip_type.ancestors = ['entity', 'thing'];

// Joint type (subtype of entity)
MERGE (joint_type:Node {uuid: '91f9e1a4-4b26-55f4-a174-a68afef6b1bd'})
ON CREATE SET
    joint_type.name = 'Joint',
    joint_type.is_type_definition = true,
    joint_type.type = 'Joint',
    joint_type.ancestors = ['entity', 'thing'];

// GraspableObject type (subtype of entity)
MERGE (grasp_type:Node {uuid: 'e970660c-a39d-5934-8e69-82b60b525faf'})
ON CREATE SET
    grasp_type.name = 'GraspableObject',
    grasp_type.is_type_definition = true,
    grasp_type.type = 'GraspableObject',
    grasp_type.ancestors = ['entity', 'thing'];

// Container type (subtype of entity)
MERGE (cont_type:Node {uuid: '88398524-e7e4-5341-8eac-38234e032f2c'})
ON CREATE SET
    cont_type.name = 'Container',
    cont_type.is_type_definition = true,
    cont_type.type = 'Container',
    cont_type.ancestors = ['entity', 'thing'];

// Surface type (subtype of entity)
MERGE (surf_type:Node {uuid: 'c6873cd9-2281-57ae-8e42-b352959526dc'})
ON CREATE SET
    surf_type.name = 'Surface',
    surf_type.is_type_definition = true,
    surf_type.type = 'Surface',
    surf_type.ancestors = ['entity', 'thing'];

// State type (subtype of concept) - if not already in bootstrap
MERGE (state_type:Node {uuid: '2dd3d0d8-569f-5132-b4a1-7ec30dc2d92b'})
ON CREATE SET
    state_type.name = 'state',
    state_type.is_type_definition = true,
    state_type.type = 'state',
    state_type.ancestors = ['concept'];

// Process type (subtype of concept) - if not already in bootstrap
MERGE (process_type:Node {uuid: 'a62326cc-bd8b-5378-a428-9600eb3bafe8'})
ON CREATE SET
    process_type.name = 'process',
    process_type.is_type_definition = true,
    process_type.type = 'process',
    process_type.ancestors = ['concept'];

// Capability type (subtype of concept)
MERGE (cap_type:Node {uuid: 'cb264b3b-bc01-511f-8326-596f88f20102'})
ON CREATE SET
    cap_type.name = 'capability',
    cap_type.is_type_definition = true,
    cap_type.type = 'capability',
    cap_type.ancestors = ['concept'];

// State subtypes
MERGE (positioned_type:Node {uuid: '9fa024a3-2119-5e92-b809-2c175d807d49'})
ON CREATE SET
    positioned_type.name = 'PositionedState',
    positioned_type.is_type_definition = true,
    positioned_type.type = 'PositionedState',
    positioned_type.ancestors = ['state', 'concept'];

MERGE (free_type:Node {uuid: '49aa09f5-7261-5d32-936e-3a03a1305199'})
ON CREATE SET
    free_type.name = 'FreeState',
    free_type.is_type_definition = true,
    free_type.type = 'FreeState',
    free_type.ancestors = ['state', 'concept'];

MERGE (grasped_type:Node {uuid: '21f381d0-efc5-51e1-b2ca-3f66fb184785'})
ON CREATE SET
    grasped_type.name = 'GraspedState',
    grasped_type.is_type_definition = true,
    grasped_type.type = 'GraspedState',
    grasped_type.ancestors = ['state', 'concept'];

// Process subtypes (actions)
MERGE (move_type:Node {uuid: '3cc680d2-4b5f-574f-9e03-4843487d1a7a'})
ON CREATE SET
    move_type.name = 'MoveAction',
    move_type.is_type_definition = true,
    move_type.type = 'MoveAction',
    move_type.ancestors = ['process', 'concept'];

MERGE (grasp_action_type:Node {uuid: 'b238755d-e2a6-58f6-ae96-8f8dedacc493'})
ON CREATE SET
    grasp_action_type.name = 'GraspAction',
    grasp_action_type.is_type_definition = true,
    grasp_action_type.type = 'GraspAction',
    grasp_action_type.ancestors = ['process', 'concept'];

MERGE (release_type:Node {uuid: 'efdec656-6ba2-598b-8121-4a6c6462fc2c'})
ON CREATE SET
    release_type.name = 'ReleaseAction',
    release_type.is_type_definition = true,
    release_type.type = 'ReleaseAction',
    release_type.ancestors = ['process', 'concept'];

MERGE (place_type:Node {uuid: '3b48d857-90a4-5ac8-9f35-3c232b763931'})
ON CREATE SET
    place_type.name = 'PlaceAction',
    place_type.is_type_definition = true,
    place_type.type = 'PlaceAction',
    place_type.ancestors = ['process', 'concept'];

//// Sample Robot Manipulator Entities (Instances)

// Robot arm entity
MERGE (robot_arm:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
ON CREATE SET
    robot_arm.name = 'RobotArm01',
    robot_arm.is_type_definition = false,
    robot_arm.type = 'Manipulator',
    robot_arm.ancestors = ['Manipulator', 'entity', 'thing'],
    robot_arm.description = 'Six-axis robotic manipulator',
    robot_arm.created_at = datetime();

// Robot gripper entity
MERGE (robot_gripper:Node {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
ON CREATE SET
    robot_gripper.name = 'Gripper01',
    robot_gripper.is_type_definition = false,
    robot_gripper.type = 'Gripper',
    robot_gripper.ancestors = ['Gripper', 'entity', 'thing'],
    robot_gripper.description = 'Two-finger parallel gripper',
    robot_gripper.max_grasp_width = 0.08,
    robot_gripper.max_force = 50.0,
    robot_gripper.created_at = datetime();

// Joint entities (simplified - 3 joints for arm)
MERGE (joint1:Node {uuid: '43117773-50b8-43fd-9d79-d10017674116'})
ON CREATE SET
    joint1.name = 'Joint01-Base',
    joint1.is_type_definition = false,
    joint1.type = 'Joint',
    joint1.ancestors = ['Joint', 'entity', 'thing'],
    joint1.joint_type = 'revolute',
    joint1.min_angle = -3.14159,
    joint1.max_angle = 3.14159,
    joint1.created_at = datetime();

MERGE (joint2:Node {uuid: '6a813f24-eca4-4df3-bc85-228c1d001ee8'})
ON CREATE SET
    joint2.name = 'Joint02-Shoulder',
    joint2.is_type_definition = false,
    joint2.type = 'Joint',
    joint2.ancestors = ['Joint', 'entity', 'thing'],
    joint2.joint_type = 'revolute',
    joint2.min_angle = -1.5708,
    joint2.max_angle = 1.5708,
    joint2.created_at = datetime();

MERGE (joint3:Node {uuid: '543ccec9-4e43-4ad6-8b47-a5c1766c274f'})
ON CREATE SET
    joint3.name = 'Joint03-Elbow',
    joint3.is_type_definition = false,
    joint3.type = 'Joint',
    joint3.ancestors = ['Joint', 'entity', 'thing'],
    joint3.joint_type = 'revolute',
    joint3.min_angle = -1.5708,
    joint3.max_angle = 1.5708,
    joint3.created_at = datetime();

//// Workspace Entities

// Table surface
MERGE (table:Node {uuid: 'f4d97052-466f-4466-bfa7-8df1623969f9'})
ON CREATE SET
    table.name = 'WorkTable01',
    table.is_type_definition = false,
    table.type = 'Surface',
    table.ancestors = ['Surface', 'entity', 'thing'],
    table.description = 'Main work surface',
    table.width = 1.0,
    table.depth = 0.8,
    table.height = 0.75,
    table.created_at = datetime();

// Target container
MERGE (bin:Node {uuid: '563e215e-3192-497c-8997-57fb9bba3922'})
ON CREATE SET
    bin.name = 'TargetBin01',
    bin.is_type_definition = false,
    bin.type = 'Container',
    bin.ancestors = ['Container', 'entity', 'thing'],
    bin.description = 'Target container for placement',
    bin.width = 0.3,
    bin.depth = 0.3,
    bin.height = 0.15,
    bin.created_at = datetime();

//// Graspable Object Entities

// Block to be manipulated
MERGE (block_red:Node {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
ON CREATE SET
    block_red.name = 'RedBlock01',
    block_red.is_type_definition = false,
    block_red.type = 'GraspableObject',
    block_red.ancestors = ['GraspableObject', 'entity', 'thing'],
    block_red.description = 'Red cubic block',
    block_red.width = 0.05,
    block_red.height = 0.05,
    block_red.depth = 0.05,
    block_red.mass = 0.1,
    block_red.color = 'red',
    block_red.graspable = true,
    block_red.created_at = datetime();

MERGE (block_blue:Node {uuid: 'ad892f3e-dd35-48fa-b3c8-4e8316e5fe7a'})
ON CREATE SET
    block_blue.name = 'BlueBlock01',
    block_blue.is_type_definition = false,
    block_blue.type = 'GraspableObject',
    block_blue.ancestors = ['GraspableObject', 'entity', 'thing'],
    block_blue.description = 'Blue cubic block',
    block_blue.width = 0.05,
    block_blue.height = 0.05,
    block_blue.depth = 0.05,
    block_blue.mass = 0.15,
    block_blue.color = 'blue',
    block_blue.graspable = true,
    block_blue.created_at = datetime();

MERGE (cylinder_green:Node {uuid: '6f69f9f9-50a7-40e3-b915-b95f31d9a00a'})
ON CREATE SET
    cylinder_green.name = 'GreenCylinder01',
    cylinder_green.is_type_definition = false,
    cylinder_green.type = 'GraspableObject',
    cylinder_green.ancestors = ['GraspableObject', 'entity', 'thing'],
    cylinder_green.description = 'Green cylindrical object',
    cylinder_green.radius = 0.03,
    cylinder_green.height = 0.08,
    cylinder_green.mass = 0.12,
    cylinder_green.color = 'green',
    cylinder_green.graspable = true,
    cylinder_green.created_at = datetime();

//// Entity Type Relationships (IS_A)

// Robot components to their types
MATCH (robot_arm:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MATCH (manip:Node {uuid: '3bed753e-51ad-5f8f-bb3a-1f7dc39ae01c'})
MERGE (robot_arm)-[:IS_A]->(manip);

MATCH (robot_gripper:Node {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MATCH (grip_concept:Node {uuid: '4f753e84-47ef-5f42-a490-bc4dc4910dfb'})
MERGE (robot_gripper)-[:IS_A]->(grip_concept);

MATCH (joint1:Node {uuid: '43117773-50b8-43fd-9d79-d10017674116'})
MATCH (joint2:Node {uuid: '6a813f24-eca4-4df3-bc85-228c1d001ee8'})
MATCH (joint3:Node {uuid: '543ccec9-4e43-4ad6-8b47-a5c1766c274f'})
MATCH (joint_concept:Node {uuid: '91f9e1a4-4b26-55f4-a174-a68afef6b1bd'})
MERGE (joint1)-[:IS_A]->(joint_concept)
MERGE (joint2)-[:IS_A]->(joint_concept)
MERGE (joint3)-[:IS_A]->(joint_concept);

// Workspace components
MATCH (table:Node {uuid: 'f4d97052-466f-4466-bfa7-8df1623969f9'})
MATCH (surf:Node {uuid: 'c6873cd9-2281-57ae-8e42-b352959526dc'})
MERGE (table)-[:IS_A]->(surf);

MATCH (bin:Node {uuid: '563e215e-3192-497c-8997-57fb9bba3922'})
MATCH (cont:Node {uuid: '88398524-e7e4-5341-8eac-38234e032f2c'})
MERGE (bin)-[:IS_A]->(cont);

// Graspable objects
MATCH (block_red:Node {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
MATCH (block_blue:Node {uuid: 'ad892f3e-dd35-48fa-b3c8-4e8316e5fe7a'})
MATCH (cylinder_green:Node {uuid: '6f69f9f9-50a7-40e3-b915-b95f31d9a00a'})
MATCH (grasp:Node {uuid: 'e970660c-a39d-5934-8e69-82b60b525faf'})
MERGE (block_red)-[:IS_A]->(grasp)
MERGE (block_blue)-[:IS_A]->(grasp)
MERGE (cylinder_green)-[:IS_A]->(grasp);

//// Compositional Relationships (PART_OF)

MATCH (robot_gripper:Node {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MATCH (robot_arm:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (robot_gripper)-[:PART_OF]->(robot_arm);

MATCH (joint1:Node {uuid: '43117773-50b8-43fd-9d79-d10017674116'})
MATCH (robot_arm2:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (joint1)-[:PART_OF]->(robot_arm2);

MATCH (joint2:Node {uuid: '6a813f24-eca4-4df3-bc85-228c1d001ee8'})
MATCH (robot_arm3:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (joint2)-[:PART_OF]->(robot_arm3);

MATCH (joint3:Node {uuid: '543ccec9-4e43-4ad6-8b47-a5c1766c274f'})
MATCH (robot_arm4:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (joint3)-[:PART_OF]->(robot_arm4);

MATCH (bin:Node {uuid: '563e215e-3192-497c-8997-57fb9bba3922'})
MATCH (table:Node {uuid: 'f4d97052-466f-4466-bfa7-8df1623969f9'})
MERGE (bin)-[:LOCATED_AT]->(table);

//// Initial States

// Robot arm state - home position
MERGE (arm_state_home:Node {uuid: '1957c02d-a22a-483c-8ccb-cd04e7f03817'})
ON CREATE SET
    arm_state_home.name = 'ArmHomeState',
    arm_state_home.is_type_definition = false,
    arm_state_home.type = 'state',
    arm_state_home.ancestors = ['state', 'concept'],
    arm_state_home.timestamp = datetime(),
    arm_state_home.position_x = 0.0,
    arm_state_home.position_y = 0.5,
    arm_state_home.position_z = 0.3,
    arm_state_home.orientation_roll = 0.0,
    arm_state_home.orientation_pitch = 0.0,
    arm_state_home.orientation_yaw = 0.0;

MATCH (robot_arm:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MATCH (arm_state_home:Node {uuid: '1957c02d-a22a-483c-8ccb-cd04e7f03817'})
MERGE (robot_arm)-[:HAS_STATE]->(arm_state_home);

// Gripper state - open
MERGE (gripper_state_open:Node {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
ON CREATE SET
    gripper_state_open.name = 'GripperOpenState',
    gripper_state_open.is_type_definition = false,
    gripper_state_open.type = 'FreeState',
    gripper_state_open.ancestors = ['FreeState', 'state', 'concept'],
    gripper_state_open.timestamp = datetime(),
    gripper_state_open.is_closed = false,
    gripper_state_open.grasp_width = 0.08,
    gripper_state_open.applied_force = 0.0;

MATCH (robot_gripper:Node {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MATCH (gripper_state_open:Node {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
MERGE (robot_gripper)-[:HAS_STATE]->(gripper_state_open);

MATCH (gripper_state_open2:Node {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
MATCH (free:Node {uuid: '49aa09f5-7261-5d32-936e-3a03a1305199'})
MERGE (gripper_state_open2)-[:IS_A]->(free);

// Red block state - on table (INITIAL/CURRENT state)
MERGE (block_red_state_01:Node {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
ON CREATE SET
    block_red_state_01.name = 'RedBlockOnTableState',
    block_red_state_01.is_type_definition = false,
    block_red_state_01.type = 'PositionedState',
    block_red_state_01.ancestors = ['PositionedState', 'state', 'concept'],
    block_red_state_01.timestamp = datetime(),
    block_red_state_01.position_x = 0.2,
    block_red_state_01.position_y = 0.3,
    block_red_state_01.position_z = 0.775,
    block_red_state_01.is_grasped = false,
    block_red_state_01.location = 'table';

MATCH (block_red:Node {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
MATCH (block_red_state_01:Node {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
MERGE (block_red)-[:HAS_STATE]->(block_red_state_01);

MATCH (block_red_state_01_2:Node {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
MATCH (positioned:Node {uuid: '9fa024a3-2119-5e92-b809-2c175d807d49'})
MERGE (block_red_state_01_2)-[:IS_A]->(positioned);

// Blue block state - on table
MERGE (block_blue_state_01:Node {uuid: '7487dec5-6aed-4988-abce-ccd7daa9bc0d'})
ON CREATE SET
    block_blue_state_01.name = 'BlueBlockOnTableState',
    block_blue_state_01.is_type_definition = false,
    block_blue_state_01.type = 'PositionedState',
    block_blue_state_01.ancestors = ['PositionedState', 'state', 'concept'],
    block_blue_state_01.timestamp = datetime(),
    block_blue_state_01.position_x = 0.3,
    block_blue_state_01.position_y = 0.4,
    block_blue_state_01.position_z = 0.775,
    block_blue_state_01.is_grasped = false,
    block_blue_state_01.location = 'table';

MATCH (block_blue:Node {uuid: 'ad892f3e-dd35-48fa-b3c8-4e8316e5fe7a'})
MATCH (block_blue_state_01:Node {uuid: '7487dec5-6aed-4988-abce-ccd7daa9bc0d'})
MERGE (block_blue)-[:HAS_STATE]->(block_blue_state_01);

// Green cylinder state - on table
MERGE (cylinder_green_state_01:Node {uuid: '7a12cfd9-d533-46cd-8ecb-f2f1a84cdf69'})
ON CREATE SET
    cylinder_green_state_01.name = 'GreenCylinderOnTableState',
    cylinder_green_state_01.is_type_definition = false,
    cylinder_green_state_01.type = 'PositionedState',
    cylinder_green_state_01.ancestors = ['PositionedState', 'state', 'concept'],
    cylinder_green_state_01.timestamp = datetime(),
    cylinder_green_state_01.position_x = 0.25,
    cylinder_green_state_01.position_y = 0.5,
    cylinder_green_state_01.position_z = 0.775,
    cylinder_green_state_01.is_grasped = false,
    cylinder_green_state_01.location = 'table';

MATCH (cylinder_green:Node {uuid: '6f69f9f9-50a7-40e3-b915-b95f31d9a00a'})
MATCH (cylinder_green_state_01:Node {uuid: '7a12cfd9-d533-46cd-8ecb-f2f1a84cdf69'})
MERGE (cylinder_green)-[:HAS_STATE]->(cylinder_green_state_01);

// Bin state - empty on table
MERGE (bin_state_01:Node {uuid: '09c15995-3bdb-48c8-af88-056e50285ea6'})
ON CREATE SET
    bin_state_01.name = 'BinEmptyState',
    bin_state_01.is_type_definition = false,
    bin_state_01.type = 'state',
    bin_state_01.ancestors = ['state', 'concept'],
    bin_state_01.timestamp = datetime(),
    bin_state_01.position_x = 0.5,
    bin_state_01.position_y = 0.3,
    bin_state_01.position_z = 0.75,
    bin_state_01.is_empty = true;

MATCH (bin:Node {uuid: '563e215e-3192-497c-8997-57fb9bba3922'})
MATCH (bin_state_01:Node {uuid: '09c15995-3bdb-48c8-af88-056e50285ea6'})
MERGE (bin)-[:HAS_STATE]->(bin_state_01);

//// Intermediate and Goal States

// Arm pre-grasp position state (intermediate)
MERGE (arm_state_pregrasp:Node {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
ON CREATE SET
    arm_state_pregrasp.name = 'ArmPreGraspState',
    arm_state_pregrasp.is_type_definition = false,
    arm_state_pregrasp.type = 'PositionedState',
    arm_state_pregrasp.ancestors = ['PositionedState', 'state', 'concept'],
    arm_state_pregrasp.timestamp = datetime(),
    arm_state_pregrasp.position_x = 0.2,
    arm_state_pregrasp.position_y = 0.3,
    arm_state_pregrasp.position_z = 0.85,
    arm_state_pregrasp.orientation_roll = 0.0,
    arm_state_pregrasp.orientation_pitch = 1.5708,
    arm_state_pregrasp.orientation_yaw = 0.0;

// Red block grasped state (intermediate)
MERGE (block_red_grasped:Node {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
ON CREATE SET
    block_red_grasped.name = 'RedBlockGraspedState',
    block_red_grasped.is_type_definition = false,
    block_red_grasped.type = 'GraspedState',
    block_red_grasped.ancestors = ['GraspedState', 'state', 'concept'],
    block_red_grasped.timestamp = datetime(),
    block_red_grasped.is_grasped = true,
    block_red_grasped.location = 'gripper';

MATCH (block_red:Node {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
MATCH (block_red_grasped:Node {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (block_red)-[:HAS_STATE]->(block_red_grasped);

// Arm at place position state (intermediate)
MERGE (arm_state_place:Node {uuid: '7daabd8b-6c39-435f-98cf-d4629cd86e36'})
ON CREATE SET
    arm_state_place.name = 'ArmPlacePositionState',
    arm_state_place.is_type_definition = false,
    arm_state_place.type = 'PositionedState',
    arm_state_place.ancestors = ['PositionedState', 'state', 'concept'],
    arm_state_place.timestamp = datetime(),
    arm_state_place.position_x = 0.5,
    arm_state_place.position_y = 0.3,
    arm_state_place.position_z = 0.85,
    arm_state_place.orientation_roll = 0.0,
    arm_state_place.orientation_pitch = 1.5708,
    arm_state_place.orientation_yaw = 0.0;

// Red block in bin state (GOAL state)
MERGE (block_red_in_bin:Node {uuid: '9a329df2-e778-40f9-8b37-f23314f33366'})
ON CREATE SET
    block_red_in_bin.name = 'RedBlockInBinState',
    block_red_in_bin.is_type_definition = false,
    block_red_in_bin.type = 'PositionedState',
    block_red_in_bin.ancestors = ['PositionedState', 'state', 'concept'],
    block_red_in_bin.timestamp = datetime(),
    block_red_in_bin.position_x = 0.5,
    block_red_in_bin.position_y = 0.3,
    block_red_in_bin.position_z = 0.775,
    block_red_in_bin.is_grasped = false,
    block_red_in_bin.location = 'bin';

MATCH (block_red:Node {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
MATCH (block_red_in_bin:Node {uuid: '9a329df2-e778-40f9-8b37-f23314f33366'})
MERGE (block_red)-[:HAS_STATE]->(block_red_in_bin);

//// Processes - The Causal Chain

// Process 1: Move to pre-grasp position
// REQUIRES: arm at home, gripper open
// CAUSES: arm at pre-grasp position
MERGE (process_move_pre:Node {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
ON CREATE SET
    process_move_pre.name = 'MoveToPreGraspPosition',
    process_move_pre.is_type_definition = false,
    process_move_pre.type = 'MoveAction',
    process_move_pre.ancestors = ['MoveAction', 'process', 'concept'],
    process_move_pre.description = 'Move arm above red block for grasping',
    process_move_pre.start_time = datetime(),
    process_move_pre.duration_ms = 2000;

MATCH (process_move_pre:Node {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (move_concept:Node {uuid: '3cc680d2-4b5f-574f-9e03-4843487d1a7a'})
MERGE (process_move_pre)-[:IS_A]->(move_concept);

// Requirements for move-to-pregrasp
MATCH (process_move_pre:Node {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (arm_state_home:Node {uuid: '1957c02d-a22a-483c-8ccb-cd04e7f03817'})
MERGE (process_move_pre)-[:REQUIRES]->(arm_state_home);

MATCH (process_move_pre:Node {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (gripper_state_open:Node {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
MERGE (process_move_pre)-[:REQUIRES]->(gripper_state_open);

// Effects of move-to-pregrasp
MATCH (process_move_pre:Node {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (arm_state_pregrasp:Node {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
MERGE (process_move_pre)-[:CAUSES]->(arm_state_pregrasp);

// Process 2: Grasp red block
// REQUIRES: arm at pre-grasp, block on table, gripper open
// CAUSES: block grasped
MERGE (process_grasp:Node {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
ON CREATE SET
    process_grasp.name = 'GraspRedBlock',
    process_grasp.is_type_definition = false,
    process_grasp.type = 'GraspAction',
    process_grasp.ancestors = ['GraspAction', 'process', 'concept'],
    process_grasp.description = 'Close gripper on red block',
    process_grasp.start_time = datetime(),
    process_grasp.duration_ms = 1500;

MATCH (process_grasp:Node {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (grasp_concept:Node {uuid: 'b238755d-e2a6-58f6-ae96-8f8dedacc493'})
MERGE (process_grasp)-[:IS_A]->(grasp_concept);

// Requirements for grasp
MATCH (process_grasp:Node {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (arm_state_pregrasp:Node {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
MERGE (process_grasp)-[:REQUIRES]->(arm_state_pregrasp);

MATCH (process_grasp:Node {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (block_red_on_table:Node {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
MERGE (process_grasp)-[:REQUIRES]->(block_red_on_table);

MATCH (process_grasp:Node {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (gripper_open:Node {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
MERGE (process_grasp)-[:REQUIRES]->(gripper_open);

// Effects of grasp
MATCH (process_grasp:Node {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (block_red_grasped:Node {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (process_grasp)-[:CAUSES]->(block_red_grasped);

// Process 3: Move to place position
// REQUIRES: block grasped
// CAUSES: arm at place position
MERGE (process_move_place:Node {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
ON CREATE SET
    process_move_place.name = 'MoveToPlacePosition',
    process_move_place.is_type_definition = false,
    process_move_place.type = 'MoveAction',
    process_move_place.ancestors = ['MoveAction', 'process', 'concept'],
    process_move_place.description = 'Move arm with grasped block to bin',
    process_move_place.start_time = datetime(),
    process_move_place.duration_ms = 2500;

MATCH (process_move_place:Node {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MATCH (move_concept:Node {uuid: '3cc680d2-4b5f-574f-9e03-4843487d1a7a'})
MERGE (process_move_place)-[:IS_A]->(move_concept);

// Requirements for move-to-place
MATCH (process_move_place:Node {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MATCH (block_red_grasped:Node {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (process_move_place)-[:REQUIRES]->(block_red_grasped);

// Effects of move-to-place
MATCH (process_move_place:Node {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MATCH (arm_state_place:Node {uuid: '7daabd8b-6c39-435f-98cf-d4629cd86e36'})
MERGE (process_move_place)-[:CAUSES]->(arm_state_place);

// Process 4: Release red block
// REQUIRES: arm at place position, block grasped
// CAUSES: block in bin (GOAL!)
MERGE (process_release:Node {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
ON CREATE SET
    process_release.name = 'ReleaseRedBlock',
    process_release.is_type_definition = false,
    process_release.type = 'ReleaseAction',
    process_release.ancestors = ['ReleaseAction', 'process', 'concept'],
    process_release.description = 'Open gripper to release block into bin',
    process_release.start_time = datetime(),
    process_release.duration_ms = 1000;

MATCH (process_release:Node {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (release_concept:Node {uuid: 'efdec656-6ba2-598b-8121-4a6c6462fc2c'})
MERGE (process_release)-[:IS_A]->(release_concept);

// Requirements for release
MATCH (process_release:Node {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (arm_state_place:Node {uuid: '7daabd8b-6c39-435f-98cf-d4629cd86e36'})
MERGE (process_release)-[:REQUIRES]->(arm_state_place);

MATCH (process_release:Node {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (block_red_grasped:Node {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (process_release)-[:REQUIRES]->(block_red_grasped);

// Effects of release - THE GOAL STATE
MATCH (process_release:Node {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (block_red_in_bin:Node {uuid: '9a329df2-e778-40f9-8b37-f23314f33366'})
MERGE (process_release)-[:CAUSES]->(block_red_in_bin);

//// State Temporal Ordering (PRECEDES)

MATCH (arm_home:Node {uuid: '1957c02d-a22a-483c-8ccb-cd04e7f03817'})
MATCH (arm_pregrasp:Node {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
MERGE (arm_home)-[:PRECEDES]->(arm_pregrasp);

MATCH (block_on_table:Node {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
MATCH (block_grasped:Node {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (block_on_table)-[:PRECEDES]->(block_grasped);

MATCH (arm_pregrasp:Node {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
MATCH (arm_place:Node {uuid: '7daabd8b-6c39-435f-98cf-d4629cd86e36'})
MERGE (arm_pregrasp)-[:PRECEDES]->(arm_place);

MATCH (block_grasped:Node {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MATCH (block_in_bin:Node {uuid: '9a329df2-e778-40f9-8b37-f23314f33366'})
MERGE (block_grasped)-[:PRECEDES]->(block_in_bin);

//// Capabilities

// Move capability
MERGE (cap_move:Node {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
ON CREATE SET
    cap_move.name = 'MoveCapability',
    cap_move.is_type_definition = false,
    cap_move.type = 'capability',
    cap_move.ancestors = ['capability', 'concept'],
    cap_move.description = 'Ability to move arm to target position',
    cap_move.created_at = datetime();

MATCH (cap_move:Node {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MATCH (robot_arm:Node {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (robot_arm)-[:HAS_CAPABILITY]->(cap_move);

// Link move capability to move processes
MATCH (cap_move:Node {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MATCH (process_move_pre:Node {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MERGE (cap_move)-[:ENABLES]->(process_move_pre);

MATCH (cap_move:Node {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MATCH (process_move_place:Node {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MERGE (cap_move)-[:ENABLES]->(process_move_place);

// Grasp capability
MERGE (cap_grasp:Node {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
ON CREATE SET
    cap_grasp.name = 'GraspCapability',
    cap_grasp.is_type_definition = false,
    cap_grasp.type = 'capability',
    cap_grasp.ancestors = ['capability', 'concept'],
    cap_grasp.description = 'Ability to close gripper and grasp objects',
    cap_grasp.created_at = datetime();

MATCH (cap_grasp:Node {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
MATCH (robot_gripper:Node {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MERGE (robot_gripper)-[:HAS_CAPABILITY]->(cap_grasp);

MATCH (cap_grasp:Node {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
MATCH (process_grasp:Node {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MERGE (cap_grasp)-[:ENABLES]->(process_grasp);

// Release capability
MERGE (cap_release:Node {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
ON CREATE SET
    cap_release.name = 'ReleaseCapability',
    cap_release.is_type_definition = false,
    cap_release.type = 'capability',
    cap_release.ancestors = ['capability', 'concept'],
    cap_release.description = 'Ability to open gripper and release objects',
    cap_release.created_at = datetime();

MATCH (cap_release:Node {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
MATCH (robot_gripper:Node {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MERGE (robot_gripper)-[:HAS_CAPABILITY]->(cap_release);

MATCH (cap_release:Node {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
MATCH (process_release:Node {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MERGE (cap_release)-[:ENABLES]->(process_release);

//// USES_CAPABILITY relationships (Process -> Capability)
// These are used by the planner to find which capability executes a process

MATCH (process_move_pre:Node {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (cap_move:Node {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MERGE (process_move_pre)-[:USES_CAPABILITY]->(cap_move);

MATCH (process_grasp:Node {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (cap_grasp:Node {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
MERGE (process_grasp)-[:USES_CAPABILITY]->(cap_grasp);

MATCH (process_move_place:Node {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MATCH (cap_move:Node {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MERGE (process_move_place)-[:USES_CAPABILITY]->(cap_move);

MATCH (process_release:Node {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (cap_release:Node {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
MERGE (process_release)-[:USES_CAPABILITY]->(cap_release);

//// IMPLEMENTS relationships (Capability -> Type)
// These allow capability lookup via process type (Process -[:IS_A]-> Type <-[:IMPLEMENTS]- Capability)

MATCH (cap_move:Node {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MATCH (move_concept:Node {uuid: '3cc680d2-4b5f-574f-9e03-4843487d1a7a'})
MERGE (cap_move)-[:IMPLEMENTS]->(move_concept);

MATCH (cap_grasp:Node {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
MATCH (grasp_concept:Node {uuid: 'b238755d-e2a6-58f6-ae96-8f8dedacc493'})
MERGE (cap_grasp)-[:IMPLEMENTS]->(grasp_concept);

MATCH (cap_release:Node {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
MATCH (release_concept:Node {uuid: 'efdec656-6ba2-598b-8121-4a6c6462fc2c'})
MERGE (cap_release)-[:IMPLEMENTS]->(release_concept);

//// Summary: The Causal Chain for Pick-and-Place
//
// GOAL: RedBlock in Bin (state: 9a329df2-e778-40f9-8b37-f23314f33366)
//
// Backward chaining from goal:
//   ReleaseRedBlock (a843ccc0-c597-424a-a8e9-c5227f1af717) CAUSES RedBlockInBin
//     REQUIRES: ArmPlacePositionState, RedBlockGraspedState
//
//   MoveToPlacePosition (492d0005-972b-4b3c-9db4-a6e4cdd4b824) CAUSES ArmPlacePositionState
//     REQUIRES: RedBlockGraspedState
//
//   GraspRedBlock (350e8968-647d-47b3-b2a5-54a6c828256c) CAUSES RedBlockGraspedState
//     REQUIRES: ArmPreGraspState, RedBlockOnTableState, GripperOpenState
//
//   MoveToPreGraspPosition (5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd) CAUSES ArmPreGraspState
//     REQUIRES: ArmHomeState, GripperOpenState
//
// Initial satisfied states (no process needed):
//   - ArmHomeState (1957c02d-a22a-483c-8ccb-cd04e7f03817)
//   - GripperOpenState (a906bb2e-4609-449d-9c2b-503976ec48c5)
//   - RedBlockOnTableState (0c6bf539-0214-4b9e-a212-3cc8c03de716)
//
// Expected plan order:
//   1. MoveToPreGraspPosition
//   2. GraspRedBlock
//   3. MoveToPlacePosition
//   4. ReleaseRedBlock
