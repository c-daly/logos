// LOGOS HCG Test Data - Pick and Place Scenario
// See Project LOGOS spec: Section 4.1 (Core Ontology and Data Model).
// This script populates test data for a simple pick-and-place scenario.

//// Sample Robot Manipulator Entities

// Robot arm entity
MERGE (robot_arm:Entity {uuid: 'entity-robot-arm-01'})
ON CREATE SET 
    robot_arm.name = 'RobotArm01',
    robot_arm.description = 'Six-axis robotic manipulator',
    robot_arm.created_at = datetime();

// Robot gripper entity
MERGE (robot_gripper:Entity {uuid: 'entity-gripper-01'})
ON CREATE SET 
    robot_gripper.name = 'Gripper01',
    robot_gripper.description = 'Two-finger parallel gripper',
    robot_gripper.max_grasp_width = 0.08,
    robot_gripper.max_force = 50.0,
    robot_gripper.created_at = datetime();

// Joint entities (simplified - 6 joints for arm)
MERGE (joint1:Entity {uuid: 'entity-joint-01'})
ON CREATE SET 
    joint1.name = 'Joint01-Base',
    joint1.joint_type = 'revolute',
    joint1.min_angle = -3.14159,
    joint1.max_angle = 3.14159,
    joint1.created_at = datetime();

MERGE (joint2:Entity {uuid: 'entity-joint-02'})
ON CREATE SET 
    joint2.name = 'Joint02-Shoulder',
    joint2.joint_type = 'revolute',
    joint2.min_angle = -1.5708,
    joint2.max_angle = 1.5708,
    joint2.created_at = datetime();

MERGE (joint3:Entity {uuid: 'entity-joint-03'})
ON CREATE SET 
    joint3.name = 'Joint03-Elbow',
    joint3.joint_type = 'revolute',
    joint3.min_angle = -1.5708,
    joint3.max_angle = 1.5708,
    joint3.created_at = datetime();

//// Workspace Entities

// Table surface
MERGE (table:Entity {uuid: 'entity-table-01'})
ON CREATE SET 
    table.name = 'WorkTable01',
    table.description = 'Main work surface',
    table.width = 1.0,
    table.depth = 0.8,
    table.height = 0.75,
    table.created_at = datetime();

// Target container
MERGE (bin:Entity {uuid: 'entity-bin-01'})
ON CREATE SET 
    bin.name = 'TargetBin01',
    bin.description = 'Target container for placement',
    bin.width = 0.3,
    bin.depth = 0.3,
    bin.height = 0.15,
    bin.created_at = datetime();

//// Graspable Object Entities

// Block to be manipulated
MERGE (block_red:Entity {uuid: 'entity-block-red-01'})
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

MERGE (block_blue:Entity {uuid: 'entity-block-blue-01'})
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

MERGE (cylinder_green:Entity {uuid: 'entity-cylinder-green-01'})
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
MERGE (robot_arm)-[:IS_A]->(manip:Concept {uuid: 'concept-manipulator'});
MERGE (robot_gripper)-[:IS_A]->(grip_concept:Concept {uuid: 'concept-gripper'});
MERGE (joint1)-[:IS_A]->(joint_concept:Concept {uuid: 'concept-joint'});
MERGE (joint2)-[:IS_A]->(joint_concept);
MERGE (joint3)-[:IS_A]->(joint_concept);

// Workspace components
MERGE (table)-[:IS_A]->(surf:Concept {uuid: 'concept-surface'});
MERGE (bin)-[:IS_A]->(cont:Concept {uuid: 'concept-container'});

// Graspable objects
MERGE (block_red)-[:IS_A]->(grasp:Concept {uuid: 'concept-graspable'});
MERGE (block_blue)-[:IS_A]->(grasp);
MERGE (cylinder_green)-[:IS_A]->(grasp);

//// Compositional Relationships (PART_OF)

MERGE (robot_gripper)-[:PART_OF]->(robot_arm);
MERGE (joint1)-[:PART_OF]->(robot_arm);
MERGE (joint2)-[:PART_OF]->(robot_arm);
MERGE (joint3)-[:PART_OF]->(robot_arm);
MERGE (bin)-[:LOCATED_AT]->(table);

//// Initial States

// Robot arm state - home position
MERGE (arm_state_home:State {uuid: 'state-arm-home-01'})
ON CREATE SET 
    arm_state_home.name = 'ArmHomeState',
    arm_state_home.timestamp = datetime(),
    arm_state_home.position_x = 0.0,
    arm_state_home.position_y = 0.5,
    arm_state_home.position_z = 0.3,
    arm_state_home.orientation_roll = 0.0,
    arm_state_home.orientation_pitch = 0.0,
    arm_state_home.orientation_yaw = 0.0;

MERGE (robot_arm)-[:HAS_STATE]->(arm_state_home);

// Gripper state - open
MERGE (gripper_state_open:State {uuid: 'state-gripper-open-01'})
ON CREATE SET 
    gripper_state_open.name = 'GripperOpenState',
    gripper_state_open.timestamp = datetime(),
    gripper_state_open.is_closed = false,
    gripper_state_open.grasp_width = 0.08,
    gripper_state_open.applied_force = 0.0;

MERGE (robot_gripper)-[:HAS_STATE]->(gripper_state_open);
MERGE (gripper_state_open)-[:IS_A]->(free:Concept {uuid: 'concept-free'});

// Red block state - on table
MERGE (block_red_state_01:State {uuid: 'state-block-red-01'})
ON CREATE SET 
    block_red_state_01.name = 'RedBlockOnTableState',
    block_red_state_01.timestamp = datetime(),
    block_red_state_01.position_x = 0.2,
    block_red_state_01.position_y = 0.3,
    block_red_state_01.position_z = 0.775,
    block_red_state_01.is_grasped = false;

MERGE (block_red)-[:HAS_STATE]->(block_red_state_01);
MERGE (block_red_state_01)-[:IS_A]->(positioned:Concept {uuid: 'concept-positioned'});

// Blue block state - on table
MERGE (block_blue_state_01:State {uuid: 'state-block-blue-01'})
ON CREATE SET 
    block_blue_state_01.name = 'BlueBlockOnTableState',
    block_blue_state_01.timestamp = datetime(),
    block_blue_state_01.position_x = 0.3,
    block_blue_state_01.position_y = 0.4,
    block_blue_state_01.position_z = 0.775,
    block_blue_state_01.is_grasped = false;

MERGE (block_blue)-[:HAS_STATE]->(block_blue_state_01);

// Green cylinder state - on table
MERGE (cylinder_green_state_01:State {uuid: 'state-cylinder-green-01'})
ON CREATE SET 
    cylinder_green_state_01.name = 'GreenCylinderOnTableState',
    cylinder_green_state_01.timestamp = datetime(),
    cylinder_green_state_01.position_x = 0.25,
    cylinder_green_state_01.position_y = 0.5,
    cylinder_green_state_01.position_z = 0.775,
    cylinder_green_state_01.is_grasped = false;

MERGE (cylinder_green)-[:HAS_STATE]->(cylinder_green_state_01);

// Bin state - empty on table
MERGE (bin_state_01:State {uuid: 'state-bin-01'})
ON CREATE SET 
    bin_state_01.name = 'BinEmptyState',
    bin_state_01.timestamp = datetime(),
    bin_state_01.position_x = 0.5,
    bin_state_01.position_y = 0.3,
    bin_state_01.position_z = 0.75,
    bin_state_01.is_empty = true;

MERGE (bin)-[:HAS_STATE]->(bin_state_01);

//// Example Process - Grasping Red Block

// Process: Move to pre-grasp position
MERGE (process_move_pre:Process {uuid: 'process-move-pregrasp-01'})
ON CREATE SET 
    process_move_pre.name = 'MoveToPreGraspPosition',
    process_move_pre.description = 'Move arm above red block',
    process_move_pre.start_time = datetime(),
    process_move_pre.duration_ms = 2000;

MERGE (process_move_pre)-[:IS_A]->(move_concept:Concept {uuid: 'concept-move'});
MERGE (process_move_pre)-[:REQUIRES]->(arm_state_home);

// Resulting state: arm above block
MERGE (arm_state_pregrasp:State {uuid: 'state-arm-pregrasp-01'})
ON CREATE SET 
    arm_state_pregrasp.name = 'ArmPreGraspState',
    arm_state_pregrasp.timestamp = datetime(),
    arm_state_pregrasp.position_x = 0.2,
    arm_state_pregrasp.position_y = 0.3,
    arm_state_pregrasp.position_z = 0.85,
    arm_state_pregrasp.orientation_roll = 0.0,
    arm_state_pregrasp.orientation_pitch = 1.5708,
    arm_state_pregrasp.orientation_yaw = 0.0;

MERGE (process_move_pre)-[:CAUSES]->(arm_state_pregrasp);
MERGE (arm_state_home)-[:PRECEDES]->(arm_state_pregrasp);

// Process: Grasp red block
MERGE (process_grasp:Process {uuid: 'process-grasp-red-01'})
ON CREATE SET 
    process_grasp.name = 'GraspRedBlock',
    process_grasp.description = 'Close gripper around red block',
    process_grasp.start_time = datetime(),
    process_grasp.duration_ms = 500;

MERGE (process_grasp)-[:IS_A]->(grasp_concept:Concept {uuid: 'concept-grasp'});
MERGE (process_grasp)-[:REQUIRES]->(arm_state_pregrasp);
MERGE (process_grasp)-[:REQUIRES]->(gripper_state_open);

// Resulting states: gripper closed, block grasped
MERGE (gripper_state_closed:State {uuid: 'state-gripper-closed-01'})
ON CREATE SET 
    gripper_state_closed.name = 'GripperClosedState',
    gripper_state_closed.timestamp = datetime(),
    gripper_state_closed.is_closed = true,
    gripper_state_closed.grasp_width = 0.05,
    gripper_state_closed.applied_force = 20.0;

MERGE (block_red_state_grasped:State {uuid: 'state-block-red-grasped-01'})
ON CREATE SET 
    block_red_state_grasped.name = 'RedBlockGraspedState',
    block_red_state_grasped.timestamp = datetime(),
    block_red_state_grasped.position_x = 0.2,
    block_red_state_grasped.position_y = 0.3,
    block_red_state_grasped.position_z = 0.8,
    block_red_state_grasped.is_grasped = true;

MERGE (process_grasp)-[:CAUSES]->(gripper_state_closed);
MERGE (process_grasp)-[:CAUSES]->(block_red_state_grasped);
MERGE (gripper_state_open)-[:PRECEDES]->(gripper_state_closed);
MERGE (block_red_state_01)-[:PRECEDES]->(block_red_state_grasped);
MERGE (block_red_state_grasped)-[:IS_A]->(grasped_concept:Concept {uuid: 'concept-grasped'});

// Process: Move to placement position
MERGE (process_move_place:Process {uuid: 'process-move-place-01'})
ON CREATE SET 
    process_move_place.name = 'MoveToPlacePosition',
    process_move_place.description = 'Move arm with block to bin',
    process_move_place.start_time = datetime(),
    process_move_place.duration_ms = 2500;

MERGE (process_move_place)-[:IS_A]->(move_concept);
MERGE (process_move_place)-[:REQUIRES]->(block_red_state_grasped);

// Resulting state: arm above bin
MERGE (arm_state_place:State {uuid: 'state-arm-place-01'})
ON CREATE SET 
    arm_state_place.name = 'ArmPlaceState',
    arm_state_place.timestamp = datetime(),
    arm_state_place.position_x = 0.5,
    arm_state_place.position_y = 0.3,
    arm_state_place.position_z = 0.9,
    arm_state_place.orientation_roll = 0.0,
    arm_state_place.orientation_pitch = 1.5708,
    arm_state_place.orientation_yaw = 0.0;

MERGE (process_move_place)-[:CAUSES]->(arm_state_place);
MERGE (arm_state_pregrasp)-[:PRECEDES]->(arm_state_place);

// Process: Release block
MERGE (process_release:Process {uuid: 'process-release-red-01'})
ON CREATE SET 
    process_release.name = 'ReleaseRedBlock',
    process_release.description = 'Open gripper to release block into bin',
    process_release.start_time = datetime(),
    process_release.duration_ms = 500;

MERGE (process_release)-[:IS_A]->(release_concept:Concept {uuid: 'concept-release'});
MERGE (process_release)-[:REQUIRES]->(arm_state_place);
MERGE (process_release)-[:REQUIRES]->(gripper_state_closed);

// Resulting states: gripper open, block in bin
MERGE (gripper_state_open_final:State {uuid: 'state-gripper-open-final-01'})
ON CREATE SET 
    gripper_state_open_final.name = 'GripperOpenFinalState',
    gripper_state_open_final.timestamp = datetime(),
    gripper_state_open_final.is_closed = false,
    gripper_state_open_final.grasp_width = 0.08,
    gripper_state_open_final.applied_force = 0.0;

MERGE (block_red_state_in_bin:State {uuid: 'state-block-red-in-bin-01'})
ON CREATE SET 
    block_red_state_in_bin.name = 'RedBlockInBinState',
    block_red_state_in_bin.timestamp = datetime(),
    block_red_state_in_bin.position_x = 0.5,
    block_red_state_in_bin.position_y = 0.3,
    block_red_state_in_bin.position_z = 0.8,
    block_red_state_in_bin.is_grasped = false;

MERGE (process_release)-[:CAUSES]->(gripper_state_open_final);
MERGE (process_release)-[:CAUSES]->(block_red_state_in_bin);
MERGE (gripper_state_closed)-[:PRECEDES]->(gripper_state_open_final);
MERGE (block_red_state_grasped)-[:PRECEDES]->(block_red_state_in_bin);
MERGE (block_red_state_in_bin)-[:IS_A]->(positioned);

// Establish spatial relationship
MERGE (block_red)-[:LOCATED_AT {timestamp: datetime()}]->(bin);

RETURN "test data for pick-and-place scenario created";
