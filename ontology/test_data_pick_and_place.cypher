// LOGOS HCG Test Data - Pick and Place Scenario
// See Project LOGOS spec: Section 4.1 (Core Ontology and Data Model).
// This script populates test data for a simple pick-and-place scenario.
// All UUIDs are RFC 4122 compliant for type safety.

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

//// Sample Robot Manipulator Entities

// Robot arm entity
MERGE (robot_arm:Entity {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
ON CREATE SET 
    robot_arm.name = 'RobotArm01',
    robot_arm.description = 'Six-axis robotic manipulator',
    robot_arm.created_at = datetime();

// Robot gripper entity
MERGE (robot_gripper:Entity {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
ON CREATE SET 
    robot_gripper.name = 'Gripper01',
    robot_gripper.description = 'Two-finger parallel gripper',
    robot_gripper.max_grasp_width = 0.08,
    robot_gripper.max_force = 50.0,
    robot_gripper.created_at = datetime();

// Joint entities (simplified - 3 joints for arm)
MERGE (joint1:Entity {uuid: '43117773-50b8-43fd-9d79-d10017674116'})
ON CREATE SET 
    joint1.name = 'Joint01-Base',
    joint1.joint_type = 'revolute',
    joint1.min_angle = -3.14159,
    joint1.max_angle = 3.14159,
    joint1.created_at = datetime();

MERGE (joint2:Entity {uuid: '6a813f24-eca4-4df3-bc85-228c1d001ee8'})
ON CREATE SET 
    joint2.name = 'Joint02-Shoulder',
    joint2.joint_type = 'revolute',
    joint2.min_angle = -1.5708,
    joint2.max_angle = 1.5708,
    joint2.created_at = datetime();

MERGE (joint3:Entity {uuid: '543ccec9-4e43-4ad6-8b47-a5c1766c274f'})
ON CREATE SET 
    joint3.name = 'Joint03-Elbow',
    joint3.joint_type = 'revolute',
    joint3.min_angle = -1.5708,
    joint3.max_angle = 1.5708,
    joint3.created_at = datetime();

//// Workspace Entities

// Table surface
MERGE (table:Entity {uuid: 'f4d97052-466f-4466-bfa7-8df1623969f9'})
ON CREATE SET 
    table.name = 'WorkTable01',
    table.description = 'Main work surface',
    table.width = 1.0,
    table.depth = 0.8,
    table.height = 0.75,
    table.created_at = datetime();

// Target container
MERGE (bin:Entity {uuid: '563e215e-3192-497c-8997-57fb9bba3922'})
ON CREATE SET 
    bin.name = 'TargetBin01',
    bin.description = 'Target container for placement',
    bin.width = 0.3,
    bin.depth = 0.3,
    bin.height = 0.15,
    bin.created_at = datetime();

//// Graspable Object Entities

// Block to be manipulated
MERGE (block_red:Entity {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
ON CREATE SET 
    block_red.name = 'RedBlock01',
    block_red.description = 'Red cubic block',
    block_red.width = 0.05,
    block_red.height = 0.05,
    block_red.depth = 0.05,
    block_red.mass = 0.1,
    block_red.color = 'red',
    block_red.graspable = true,
    block_red.created_at = datetime();

MERGE (block_blue:Entity {uuid: 'ad892f3e-dd35-48fa-b3c8-4e8316e5fe7a'})
ON CREATE SET 
    block_blue.name = 'BlueBlock01',
    block_blue.description = 'Blue cubic block',
    block_blue.width = 0.05,
    block_blue.height = 0.05,
    block_blue.depth = 0.05,
    block_blue.mass = 0.15,
    block_blue.color = 'blue',
    block_blue.graspable = true,
    block_blue.created_at = datetime();

MERGE (cylinder_green:Entity {uuid: '6f69f9f9-50a7-40e3-b915-b95f31d9a00a'})
ON CREATE SET 
    cylinder_green.name = 'GreenCylinder01',
    cylinder_green.description = 'Green cylindrical object',
    cylinder_green.radius = 0.03,
    cylinder_green.height = 0.08,
    cylinder_green.mass = 0.12,
    cylinder_green.color = 'green',
    cylinder_green.graspable = true,
    cylinder_green.created_at = datetime();

//// Entity Type Relationships (IS_A)

// Robot components
MATCH (robot_arm:Entity {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MATCH (manip:Concept {uuid: 'concept-manipulator'})
MERGE (robot_arm)-[:IS_A]->(manip);

MATCH (robot_gripper:Entity {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MATCH (grip_concept:Concept {uuid: 'concept-gripper'})
MERGE (robot_gripper)-[:IS_A]->(grip_concept);

MATCH (joint1:Entity {uuid: '43117773-50b8-43fd-9d79-d10017674116'})
MATCH (joint2:Entity {uuid: '6a813f24-eca4-4df3-bc85-228c1d001ee8'})
MATCH (joint3:Entity {uuid: '543ccec9-4e43-4ad6-8b47-a5c1766c274f'})
MATCH (joint_concept:Concept {uuid: 'concept-joint'})
MERGE (joint1)-[:IS_A]->(joint_concept)
MERGE (joint2)-[:IS_A]->(joint_concept)
MERGE (joint3)-[:IS_A]->(joint_concept);

// Workspace components
MATCH (table:Entity {uuid: 'f4d97052-466f-4466-bfa7-8df1623969f9'})
MATCH (surf:Concept {uuid: 'concept-surface'})
MERGE (table)-[:IS_A]->(surf);

MATCH (bin:Entity {uuid: '563e215e-3192-497c-8997-57fb9bba3922'})
MATCH (cont:Concept {uuid: 'concept-container'})
MERGE (bin)-[:IS_A]->(cont);

// Graspable objects
MATCH (block_red:Entity {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
MATCH (block_blue:Entity {uuid: 'ad892f3e-dd35-48fa-b3c8-4e8316e5fe7a'})
MATCH (cylinder_green:Entity {uuid: '6f69f9f9-50a7-40e3-b915-b95f31d9a00a'})
MATCH (grasp:Concept {uuid: 'concept-graspable'})
MERGE (block_red)-[:IS_A]->(grasp)
MERGE (block_blue)-[:IS_A]->(grasp)
MERGE (cylinder_green)-[:IS_A]->(grasp);

//// Compositional Relationships (PART_OF)

MATCH (robot_gripper:Entity {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MATCH (robot_arm:Entity {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (robot_gripper)-[:PART_OF]->(robot_arm);

MATCH (joint1:Entity {uuid: '43117773-50b8-43fd-9d79-d10017674116'})
MATCH (robot_arm2:Entity {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (joint1)-[:PART_OF]->(robot_arm2);

MATCH (joint2:Entity {uuid: '6a813f24-eca4-4df3-bc85-228c1d001ee8'})
MATCH (robot_arm3:Entity {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (joint2)-[:PART_OF]->(robot_arm3);

MATCH (joint3:Entity {uuid: '543ccec9-4e43-4ad6-8b47-a5c1766c274f'})
MATCH (robot_arm4:Entity {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (joint3)-[:PART_OF]->(robot_arm4);

MATCH (bin:Entity {uuid: '563e215e-3192-497c-8997-57fb9bba3922'})
MATCH (table:Entity {uuid: 'f4d97052-466f-4466-bfa7-8df1623969f9'})
MERGE (bin)-[:LOCATED_AT]->(table);

//// Initial States

// Robot arm state - home position
MERGE (arm_state_home:State {uuid: '1957c02d-a22a-483c-8ccb-cd04e7f03817'})
ON CREATE SET 
    arm_state_home.name = 'ArmHomeState',
    arm_state_home.timestamp = datetime(),
    arm_state_home.position_x = 0.0,
    arm_state_home.position_y = 0.5,
    arm_state_home.position_z = 0.3,
    arm_state_home.orientation_roll = 0.0,
    arm_state_home.orientation_pitch = 0.0,
    arm_state_home.orientation_yaw = 0.0;

MATCH (robot_arm:Entity {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MATCH (arm_state_home:State {uuid: '1957c02d-a22a-483c-8ccb-cd04e7f03817'})
MERGE (robot_arm)-[:HAS_STATE]->(arm_state_home);

// Gripper state - open
MERGE (gripper_state_open:State {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
ON CREATE SET 
    gripper_state_open.name = 'GripperOpenState',
    gripper_state_open.timestamp = datetime(),
    gripper_state_open.is_closed = false,
    gripper_state_open.grasp_width = 0.08,
    gripper_state_open.applied_force = 0.0;

MATCH (robot_gripper:Entity {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MATCH (gripper_state_open:State {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
MERGE (robot_gripper)-[:HAS_STATE]->(gripper_state_open);

MATCH (gripper_state_open2:State {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
MATCH (free:Concept {uuid: 'concept-free'})
MERGE (gripper_state_open2)-[:IS_A]->(free);

// Red block state - on table (INITIAL/CURRENT state)
MERGE (block_red_state_01:State {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
ON CREATE SET 
    block_red_state_01.name = 'RedBlockOnTableState',
    block_red_state_01.timestamp = datetime(),
    block_red_state_01.position_x = 0.2,
    block_red_state_01.position_y = 0.3,
    block_red_state_01.position_z = 0.775,
    block_red_state_01.is_grasped = false,
    block_red_state_01.location = 'table';

MATCH (block_red:Entity {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
MATCH (block_red_state_01:State {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
MERGE (block_red)-[:HAS_STATE]->(block_red_state_01);

MATCH (block_red_state_01_2:State {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
MATCH (positioned:Concept {uuid: 'concept-positioned'})
MERGE (block_red_state_01_2)-[:IS_A]->(positioned);

// Blue block state - on table
MERGE (block_blue_state_01:State {uuid: '7487dec5-6aed-4988-abce-ccd7daa9bc0d'})
ON CREATE SET 
    block_blue_state_01.name = 'BlueBlockOnTableState',
    block_blue_state_01.timestamp = datetime(),
    block_blue_state_01.position_x = 0.3,
    block_blue_state_01.position_y = 0.4,
    block_blue_state_01.position_z = 0.775,
    block_blue_state_01.is_grasped = false,
    block_blue_state_01.location = 'table';

MATCH (block_blue:Entity {uuid: 'ad892f3e-dd35-48fa-b3c8-4e8316e5fe7a'})
MATCH (block_blue_state_01:State {uuid: '7487dec5-6aed-4988-abce-ccd7daa9bc0d'})
MERGE (block_blue)-[:HAS_STATE]->(block_blue_state_01);

// Green cylinder state - on table
MERGE (cylinder_green_state_01:State {uuid: '7a12cfd9-d533-46cd-8ecb-f2f1a84cdf69'})
ON CREATE SET 
    cylinder_green_state_01.name = 'GreenCylinderOnTableState',
    cylinder_green_state_01.timestamp = datetime(),
    cylinder_green_state_01.position_x = 0.25,
    cylinder_green_state_01.position_y = 0.5,
    cylinder_green_state_01.position_z = 0.775,
    cylinder_green_state_01.is_grasped = false,
    cylinder_green_state_01.location = 'table';

MATCH (cylinder_green:Entity {uuid: '6f69f9f9-50a7-40e3-b915-b95f31d9a00a'})
MATCH (cylinder_green_state_01:State {uuid: '7a12cfd9-d533-46cd-8ecb-f2f1a84cdf69'})
MERGE (cylinder_green)-[:HAS_STATE]->(cylinder_green_state_01);

// Bin state - empty on table
MERGE (bin_state_01:State {uuid: '09c15995-3bdb-48c8-af88-056e50285ea6'})
ON CREATE SET 
    bin_state_01.name = 'BinEmptyState',
    bin_state_01.timestamp = datetime(),
    bin_state_01.position_x = 0.5,
    bin_state_01.position_y = 0.3,
    bin_state_01.position_z = 0.75,
    bin_state_01.is_empty = true;

MATCH (bin:Entity {uuid: '563e215e-3192-497c-8997-57fb9bba3922'})
MATCH (bin_state_01:State {uuid: '09c15995-3bdb-48c8-af88-056e50285ea6'})
MERGE (bin)-[:HAS_STATE]->(bin_state_01);

//// Intermediate and Goal States

// Arm pre-grasp position state (intermediate)
MERGE (arm_state_pregrasp:State {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
ON CREATE SET 
    arm_state_pregrasp.name = 'ArmPreGraspState',
    arm_state_pregrasp.timestamp = datetime(),
    arm_state_pregrasp.position_x = 0.2,
    arm_state_pregrasp.position_y = 0.3,
    arm_state_pregrasp.position_z = 0.85,
    arm_state_pregrasp.orientation_roll = 0.0,
    arm_state_pregrasp.orientation_pitch = 1.5708,
    arm_state_pregrasp.orientation_yaw = 0.0;

// Red block grasped state (intermediate)
MERGE (block_red_grasped:State {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
ON CREATE SET 
    block_red_grasped.name = 'RedBlockGraspedState',
    block_red_grasped.timestamp = datetime(),
    block_red_grasped.is_grasped = true,
    block_red_grasped.location = 'gripper';

MATCH (block_red:Entity {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
MATCH (block_red_grasped:State {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (block_red)-[:HAS_STATE]->(block_red_grasped);

// Arm at place position state (intermediate)
MERGE (arm_state_place:State {uuid: '7daabd8b-6c39-435f-98cf-d4629cd86e36'})
ON CREATE SET 
    arm_state_place.name = 'ArmPlacePositionState',
    arm_state_place.timestamp = datetime(),
    arm_state_place.position_x = 0.5,
    arm_state_place.position_y = 0.3,
    arm_state_place.position_z = 0.85,
    arm_state_place.orientation_roll = 0.0,
    arm_state_place.orientation_pitch = 1.5708,
    arm_state_place.orientation_yaw = 0.0;

// Red block in bin state (GOAL state)
MERGE (block_red_in_bin:State {uuid: '9a329df2-e778-40f9-8b37-f23314f33366'})
ON CREATE SET 
    block_red_in_bin.name = 'RedBlockInBinState',
    block_red_in_bin.timestamp = datetime(),
    block_red_in_bin.position_x = 0.5,
    block_red_in_bin.position_y = 0.3,
    block_red_in_bin.position_z = 0.775,
    block_red_in_bin.is_grasped = false,
    block_red_in_bin.location = 'bin';

MATCH (block_red:Entity {uuid: '4338a6cc-c125-4531-ac3b-69eca0751aa0'})
MATCH (block_red_in_bin:State {uuid: '9a329df2-e778-40f9-8b37-f23314f33366'})
MERGE (block_red)-[:HAS_STATE]->(block_red_in_bin);

//// Processes - The Causal Chain

// Process 1: Move to pre-grasp position
// REQUIRES: arm at home, gripper open
// CAUSES: arm at pre-grasp position
MERGE (process_move_pre:Process {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
ON CREATE SET 
    process_move_pre.name = 'MoveToPreGraspPosition',
    process_move_pre.description = 'Move arm above red block for grasping',
    process_move_pre.start_time = datetime(),
    process_move_pre.duration_ms = 2000;

MATCH (process_move_pre:Process {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (move_concept:Concept {uuid: 'concept-move'})
MERGE (process_move_pre)-[:IS_A]->(move_concept);

// Requirements for move-to-pregrasp
MATCH (process_move_pre:Process {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (arm_state_home:State {uuid: '1957c02d-a22a-483c-8ccb-cd04e7f03817'})
MERGE (process_move_pre)-[:REQUIRES]->(arm_state_home);

MATCH (process_move_pre:Process {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (gripper_state_open:State {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
MERGE (process_move_pre)-[:REQUIRES]->(gripper_state_open);

// Effects of move-to-pregrasp
MATCH (process_move_pre:Process {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (arm_state_pregrasp:State {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
MERGE (process_move_pre)-[:CAUSES]->(arm_state_pregrasp);

// Process 2: Grasp red block
// REQUIRES: arm at pre-grasp, block on table, gripper open
// CAUSES: block grasped
MERGE (process_grasp:Process {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
ON CREATE SET 
    process_grasp.name = 'GraspRedBlock',
    process_grasp.description = 'Close gripper on red block',
    process_grasp.start_time = datetime(),
    process_grasp.duration_ms = 1500;

MATCH (process_grasp:Process {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (grasp_concept:Concept {uuid: 'concept-grasp'})
MERGE (process_grasp)-[:IS_A]->(grasp_concept);

// Requirements for grasp
MATCH (process_grasp:Process {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (arm_state_pregrasp:State {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
MERGE (process_grasp)-[:REQUIRES]->(arm_state_pregrasp);

MATCH (process_grasp:Process {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (block_red_on_table:State {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
MERGE (process_grasp)-[:REQUIRES]->(block_red_on_table);

MATCH (process_grasp:Process {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (gripper_open:State {uuid: 'a906bb2e-4609-449d-9c2b-503976ec48c5'})
MERGE (process_grasp)-[:REQUIRES]->(gripper_open);

// Effects of grasp
MATCH (process_grasp:Process {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (block_red_grasped:State {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (process_grasp)-[:CAUSES]->(block_red_grasped);

// Process 3: Move to place position
// REQUIRES: block grasped
// CAUSES: arm at place position
MERGE (process_move_place:Process {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
ON CREATE SET 
    process_move_place.name = 'MoveToPlacePosition',
    process_move_place.description = 'Move arm with grasped block to bin',
    process_move_place.start_time = datetime(),
    process_move_place.duration_ms = 2500;

MATCH (process_move_place:Process {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MATCH (move_concept:Concept {uuid: 'concept-move'})
MERGE (process_move_place)-[:IS_A]->(move_concept);

// Requirements for move-to-place
MATCH (process_move_place:Process {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MATCH (block_red_grasped:State {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (process_move_place)-[:REQUIRES]->(block_red_grasped);

// Effects of move-to-place
MATCH (process_move_place:Process {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MATCH (arm_state_place:State {uuid: '7daabd8b-6c39-435f-98cf-d4629cd86e36'})
MERGE (process_move_place)-[:CAUSES]->(arm_state_place);

// Process 4: Release red block
// REQUIRES: arm at place position, block grasped
// CAUSES: block in bin (GOAL!)
MERGE (process_release:Process {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
ON CREATE SET 
    process_release.name = 'ReleaseRedBlock',
    process_release.description = 'Open gripper to release block into bin',
    process_release.start_time = datetime(),
    process_release.duration_ms = 1000;

MATCH (process_release:Process {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (release_concept:Concept {uuid: 'concept-release'})
MERGE (process_release)-[:IS_A]->(release_concept);

// Requirements for release
MATCH (process_release:Process {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (arm_state_place:State {uuid: '7daabd8b-6c39-435f-98cf-d4629cd86e36'})
MERGE (process_release)-[:REQUIRES]->(arm_state_place);

MATCH (process_release:Process {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (block_red_grasped:State {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (process_release)-[:REQUIRES]->(block_red_grasped);

// Effects of release - THE GOAL STATE
MATCH (process_release:Process {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (block_red_in_bin:State {uuid: '9a329df2-e778-40f9-8b37-f23314f33366'})
MERGE (process_release)-[:CAUSES]->(block_red_in_bin);

//// State Temporal Ordering (PRECEDES)

MATCH (arm_home:State {uuid: '1957c02d-a22a-483c-8ccb-cd04e7f03817'})
MATCH (arm_pregrasp:State {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
MERGE (arm_home)-[:PRECEDES]->(arm_pregrasp);

MATCH (block_on_table:State {uuid: '0c6bf539-0214-4b9e-a212-3cc8c03de716'})
MATCH (block_grasped:State {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MERGE (block_on_table)-[:PRECEDES]->(block_grasped);

MATCH (arm_pregrasp:State {uuid: '4e4faa83-9e53-40c3-8ca5-7799e706afe3'})
MATCH (arm_place:State {uuid: '7daabd8b-6c39-435f-98cf-d4629cd86e36'})
MERGE (arm_pregrasp)-[:PRECEDES]->(arm_place);

MATCH (block_grasped:State {uuid: 'f25e11ff-f33f-43a7-a4d8-a2839ec39976'})
MATCH (block_in_bin:State {uuid: '9a329df2-e778-40f9-8b37-f23314f33366'})
MERGE (block_grasped)-[:PRECEDES]->(block_in_bin);

//// Capabilities

// Move capability
MERGE (cap_move:Capability {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
ON CREATE SET 
    cap_move.name = 'MoveCapability',
    cap_move.description = 'Ability to move arm to target position',
    cap_move.created_at = datetime();

MATCH (cap_move:Capability {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MATCH (robot_arm:Entity {uuid: 'c551e7ad-c12a-40bc-8c29-3a721fa311cb'})
MERGE (robot_arm)-[:HAS_CAPABILITY]->(cap_move);

// Link move capability to move processes
MATCH (cap_move:Capability {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MATCH (process_move_pre:Process {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MERGE (cap_move)-[:ENABLES]->(process_move_pre);

MATCH (cap_move:Capability {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MATCH (process_move_place:Process {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MERGE (cap_move)-[:ENABLES]->(process_move_place);

// Grasp capability
MERGE (cap_grasp:Capability {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
ON CREATE SET 
    cap_grasp.name = 'GraspCapability',
    cap_grasp.description = 'Ability to close gripper and grasp objects',
    cap_grasp.created_at = datetime();

MATCH (cap_grasp:Capability {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
MATCH (robot_gripper:Entity {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MERGE (robot_gripper)-[:HAS_CAPABILITY]->(cap_grasp);

MATCH (cap_grasp:Capability {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
MATCH (process_grasp:Process {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MERGE (cap_grasp)-[:ENABLES]->(process_grasp);

// Release capability
MERGE (cap_release:Capability {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
ON CREATE SET 
    cap_release.name = 'ReleaseCapability',
    cap_release.description = 'Ability to open gripper and release objects',
    cap_release.created_at = datetime();

MATCH (cap_release:Capability {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
MATCH (robot_gripper:Entity {uuid: '47a157d3-1092-4069-9e39-4e80e6735342'})
MERGE (robot_gripper)-[:HAS_CAPABILITY]->(cap_release);

MATCH (cap_release:Capability {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
MATCH (process_release:Process {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MERGE (cap_release)-[:ENABLES]->(process_release);

//// USES_CAPABILITY relationships (Process -> Capability)
// These are used by the planner to find which capability executes a process

MATCH (process_move_pre:Process {uuid: '5bbb0f4b-a869-49dc-b61b-be2a1b6d8ebd'})
MATCH (cap_move:Capability {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MERGE (process_move_pre)-[:USES_CAPABILITY]->(cap_move);

MATCH (process_grasp:Process {uuid: '350e8968-647d-47b3-b2a5-54a6c828256c'})
MATCH (cap_grasp:Capability {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
MERGE (process_grasp)-[:USES_CAPABILITY]->(cap_grasp);

MATCH (process_move_place:Process {uuid: '492d0005-972b-4b3c-9db4-a6e4cdd4b824'})
MATCH (cap_move:Capability {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MERGE (process_move_place)-[:USES_CAPABILITY]->(cap_move);

MATCH (process_release:Process {uuid: 'a843ccc0-c597-424a-a8e9-c5227f1af717'})
MATCH (cap_release:Capability {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
MERGE (process_release)-[:USES_CAPABILITY]->(cap_release);

//// IMPLEMENTS relationships (Capability -> Concept)
// These allow capability lookup via process type (Process -[:IS_A]-> Concept <-[:IMPLEMENTS]- Capability)

MATCH (cap_move:Capability {uuid: '6e618722-6812-4c04-a828-add791c83a9b'})
MATCH (move_concept:Concept {uuid: 'concept-move'})
MERGE (cap_move)-[:IMPLEMENTS]->(move_concept);

MATCH (cap_grasp:Capability {uuid: '96d8b91c-6fab-44ac-867f-81e397368b56'})
MATCH (grasp_concept:Concept {uuid: 'concept-grasp'})
MERGE (cap_grasp)-[:IMPLEMENTS]->(grasp_concept);

MATCH (cap_release:Capability {uuid: 'ebee7aab-9cb8-4fa9-8491-ffb9f8490819'})
MATCH (release_concept:Concept {uuid: 'concept-release'})
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
