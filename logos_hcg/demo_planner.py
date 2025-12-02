#!/usr/bin/env python3
"""
Demo: HCGPlanner executing a pick-and-place plan.

Seeds Neo4j with pick-and-place scenario data, then uses the
HCGPlanner to generate a plan to move a block from table to bin.

Run with: python -m logos_hcg.demo_planner
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from logos_hcg import (
    Goal,
    GoalStatus,
    GoalTarget,
    HCGClient,
    HCGPlanner,
    Provenance,
    SourceService,
)
from logos_test_utils.neo4j import get_neo4j_config


def seed_pick_and_place_data(client: HCGClient) -> dict:
    """
    Seed Neo4j with pick-and-place scenario.

    Creates:
    - Entities: robot arm, gripper, red block, table, bin
    - States: block on table, block grasped, block in bin
    - Processes: move_to_block, grasp, move_to_bin, release
    - Relationships: REQUIRES, CAUSES, HAS_STATE, IS_A

    Returns dict with UUIDs for use in planning.
    """
    print("Seeding pick-and-place data...")

    # Clear existing data (for demo purposes)
    client._execute_query("MATCH (n) DETACH DELETE n")

    # Generate UUIDs
    uuids = {
        # Entities
        "robot_arm": str(uuid4()),
        "gripper": str(uuid4()),
        "red_block": str(uuid4()),
        "table": str(uuid4()),
        "bin": str(uuid4()),
        # Concepts
        "graspable": str(uuid4()),
        "container": str(uuid4()),
        "surface": str(uuid4()),
        # States
        "block_on_table": str(uuid4()),
        "gripper_at_block": str(uuid4()),
        "block_grasped": str(uuid4()),
        "gripper_at_bin": str(uuid4()),
        "block_in_bin": str(uuid4()),
        # Processes
        "move_to_block": str(uuid4()),
        "grasp_block": str(uuid4()),
        "move_to_bin": str(uuid4()),
        "release_block": str(uuid4()),
    }

    # Create entities
    entities = [
        ("robot_arm", "Robot Arm", "Panda robot arm"),
        ("gripper", "Gripper", "Parallel gripper"),
        ("red_block", "Red Block", "Red wooden block"),
        ("table", "Table", "Work surface"),
        ("bin", "Bin", "Target container"),
    ]
    for key, name, desc in entities:
        client._execute_query(
            """
            CREATE (e:Entity {
                uuid: $uuid,
                name: $name,
                description: $desc,
                created_at: datetime()
            })
            """,
            {"uuid": uuids[key], "name": name, "desc": desc},
        )

    # Create concepts
    concepts = [
        ("graspable", "Graspable", "Objects that can be grasped"),
        ("container", "Container", "Objects that can contain others"),
        ("surface", "Surface", "Flat surfaces for placing objects"),
    ]
    for key, name, desc in concepts:
        client._execute_query(
            """
            CREATE (c:Concept {
                uuid: $uuid,
                name: $name,
                description: $desc
            })
            """,
            {"uuid": uuids[key], "name": name, "desc": desc},
        )

    # Link entities to concepts
    client._execute_query(
        "MATCH (e:Entity {uuid: $e}), (c:Concept {uuid: $c}) CREATE (e)-[:IS_A]->(c)",
        {"e": uuids["red_block"], "c": uuids["graspable"]},
    )
    client._execute_query(
        "MATCH (e:Entity {uuid: $e}), (c:Concept {uuid: $c}) CREATE (e)-[:IS_A]->(c)",
        {"e": uuids["bin"], "c": uuids["container"]},
    )
    client._execute_query(
        "MATCH (e:Entity {uuid: $e}), (c:Concept {uuid: $c}) CREATE (e)-[:IS_A]->(c)",
        {"e": uuids["table"], "c": uuids["surface"]},
    )

    # Create states
    states = [
        ("block_on_table", "Block on table", {"location": "table", "grasped": False}),
        ("gripper_at_block", "Gripper at block", {"position": "block"}),
        ("block_grasped", "Block grasped", {"grasped": True}),
        ("gripper_at_bin", "Gripper at bin", {"position": "bin"}),
        ("block_in_bin", "Block in bin", {"location": "bin", "grasped": False}),
    ]
    for key, name, props in states:
        client._execute_query(
            """
            CREATE (s:State {
                uuid: $uuid,
                name: $name,
                timestamp: datetime(),
                location: $location,
                grasped: $grasped,
                position: $position
            })
            """,
            {
                "uuid": uuids[key],
                "name": name,
                "location": props.get("location", ""),
                "grasped": props.get("grasped", False),
                "position": props.get("position", ""),
            },
        )

    # Link block to its states
    client._execute_query(
        "MATCH (e:Entity {uuid: $e}), (s:State {uuid: $s}) CREATE (e)-[:HAS_STATE]->(s)",
        {"e": uuids["red_block"], "s": uuids["block_on_table"]},
    )

    # Create processes
    processes = [
        ("move_to_block", "Move to Block", "Move gripper to block position", 2000),
        ("grasp_block", "Grasp Block", "Close gripper on block", 1500),
        ("move_to_bin", "Move to Bin", "Move gripper to bin position", 2000),
        ("release_block", "Release Block", "Open gripper to release block", 1000),
    ]
    for key, name, desc, duration in processes:
        client._execute_query(
            """
            CREATE (p:Process {
                uuid: $uuid,
                name: $name,
                description: $desc,
                start_time: datetime(),
                duration_ms: $duration
            })
            """,
            {"uuid": uuids[key], "name": name, "desc": desc, "duration": duration},
        )

    # Create REQUIRES relationships (preconditions)
    requires = [
        # move_to_block requires block_on_table (block must be there to move to it)
        ("move_to_block", "block_on_table"),
        # grasp requires gripper_at_block
        ("grasp_block", "gripper_at_block"),
        # move_to_bin requires block_grasped
        ("move_to_bin", "block_grasped"),
        # release requires gripper_at_bin
        ("release_block", "gripper_at_bin"),
    ]
    for proc_key, state_key in requires:
        client._execute_query(
            """
            MATCH (p:Process {uuid: $p}), (s:State {uuid: $s})
            CREATE (p)-[:REQUIRES]->(s)
            """,
            {"p": uuids[proc_key], "s": uuids[state_key]},
        )

    # Create CAUSES relationships (effects)
    causes = [
        # move_to_block causes gripper_at_block
        ("move_to_block", "gripper_at_block"),
        # grasp causes block_grasped
        ("grasp_block", "block_grasped"),
        # move_to_bin causes gripper_at_bin
        ("move_to_bin", "gripper_at_bin"),
        # release causes block_in_bin
        ("release_block", "block_in_bin"),
    ]
    for proc_key, state_key in causes:
        client._execute_query(
            """
            MATCH (p:Process {uuid: $p}), (s:State {uuid: $s})
            CREATE (p)-[:CAUSES]->(s)
            """,
            {"p": uuids[proc_key], "s": uuids[state_key]},
        )

    print(f"  Created {len(entities)} entities")
    print(f"  Created {len(concepts)} concepts")
    print(f"  Created {len(states)} states")
    print(f"  Created {len(processes)} processes")
    print(f"  Created {len(requires)} REQUIRES relationships")
    print(f"  Created {len(causes)} CAUSES relationships")

    return uuids


def run_demo():
    """Run the planner demo."""
    # Connect to Neo4j using shared config
    config = get_neo4j_config()

    print(f"Connecting to Neo4j at {config.uri}...")
    client = HCGClient(uri=config.uri, user=config.user, password=config.password)

    if not client.verify_connection():
        print("ERROR: Could not connect to Neo4j")
        return

    print("Connected!\n")

    # Seed data
    uuids = seed_pick_and_place_data(client)
    print()

    # Create planner
    planner = HCGPlanner(client, max_depth=10)

    # Create goal: block in bin
    goal = Goal(
        uuid=uuid4(),
        description="Move red block from table to bin",
        target=GoalTarget(
            entity_uuid=UUID(uuids["red_block"]),
            state_properties={"location": "bin"},
        ),
        status=GoalStatus.PENDING,
        priority=1.0,
        provenance=Provenance(
            source_service=SourceService.HUMAN,
            created_at=datetime.now(timezone.utc),
            tags=["demo", "pick-and-place"],
        ),
    )

    print("=" * 60)
    print("GOAL")
    print("=" * 60)
    print(f"Description: {goal.description}")
    print(f"Target entity: {uuids['red_block'][:8]}... (Red Block)")
    print("Target state: location=bin")
    print()

    # Current state: block on table (this state is satisfied/true)
    current_state_uuid = UUID(uuids["block_on_table"])
    satisfied_states = {current_state_uuid}
    print(f"Current state: {str(current_state_uuid)[:8]}... (Block on Table)")
    print()

    # Generate plan
    print("=" * 60)
    print("PLANNING...")
    print("=" * 60)

    try:
        plan = planner.plan(
            goal=goal,
            satisfied_states=satisfied_states,
        )

        print("\nPlan generated successfully!")
        print(f"Plan UUID: {plan.uuid}")
        print(f"Confidence: {plan.confidence:.2%}")
        print(f"Total steps: {len(plan.steps)}")
        print()

        print("=" * 60)
        print("PLAN STEPS")
        print("=" * 60)

        for step in plan.steps:
            # Look up process details
            process = client.find_process_by_uuid(step.process_uuid)
            process_name = process.name if process else "Unknown"

            print(f"\nStep {step.index + 1}: {process_name}")
            print(f"  Process UUID: {str(step.process_uuid)[:8]}...")
            print(f"  Preconditions: {len(step.precondition_uuids)} states")
            print(f"  Effects: {len(step.effect_uuids)} states")
            if step.estimated_duration_ms:
                print(f"  Duration: {step.estimated_duration_ms}ms")

        print()
        print("=" * 60)
        print("EXECUTION ORDER")
        print("=" * 60)

        for step in plan.steps:
            process = client.find_process_by_uuid(step.process_uuid)
            process_name = process.name if process else "Unknown"
            print(f"  {step.index + 1}. {process_name}")

        print()
        print("Plan ready for execution!")

    except Exception as e:
        print(f"ERROR: Planning failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        client.close()


if __name__ == "__main__":
    run_demo()
