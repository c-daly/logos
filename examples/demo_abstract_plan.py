#!/usr/bin/env python3
"""
Demo: Abstract Planning - Write a Research Paper

Uses the HCG planner to generate a plan for an abstract cognitive task:
writing a research paper. Shows the planner is domain-agnostic.

Run: poetry run python examples/demo_abstract_plan.py
"""

from datetime import UTC, datetime
from uuid import UUID

from logos_hcg.client import HCGClient
from logos_hcg.models import Goal, GoalStatus, GoalTarget, Provenance, SourceService
from logos_hcg.planner import GoalUnachievableError, HCGPlanner

# UUIDs from test_data_research_paper.cypher
PAPER_UUID = UUID("b0000001-0000-0000-0000-000000000001")
TOPIC_SELECTED_STATE = UUID("c0000001-0000-0000-0000-000000000000")
PAPER_FINALIZED_STATE = UUID("c0000001-0000-0000-0000-000000000006")


def main():
    print("=" * 60)
    print("Abstract Planning Demo: Write a Research Paper")
    print("=" * 60)

    # Connect to HCG
    client = HCGClient(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="neo4jtest",
    )

    planner = HCGPlanner(hcg_client=client, max_depth=10)

    # Define the goal: Paper is finalized
    goal = Goal(
        uuid=UUID("eeee0001-0000-0000-0000-000000000001"),
        description="Finalize the research paper",
        target=GoalTarget(
            entity_uuid=PAPER_UUID,
            state_properties={"name": "PaperFinalized"},
        ),
        priority=1,
        status=GoalStatus.PENDING,
        provenance=Provenance(
            source_service=SourceService.HUMAN,
            created_at=datetime.now(UTC),
        ),
    )

    # Current state: Topic has been selected
    satisfied_states = {TOPIC_SELECTED_STATE}

    print(f"\nGoal: {goal.description}")
    print("Starting state: TopicSelected")
    print("Target state: PaperFinalized")
    print("\nPlanning...\n")

    try:
        plan = planner.plan(goal=goal, satisfied_states=satisfied_states)

        print(f"✓ Plan created with {len(plan.steps)} steps:\n")

        # Capability name lookup
        cap_names = {
            UUID("e0000001-0000-0000-0000-000000000001"): "WebSearch",
            UUID("e0000001-0000-0000-0000-000000000002"): "LLM",
            UUID("e0000001-0000-0000-0000-000000000003"): "Human",
        }

        total_ms = 0
        for step in plan.steps:
            duration_ms = step.estimated_duration_ms or 0
            total_ms += duration_ms
            cap_name = (
                cap_names.get(step.capability_uuid, "?")
                if step.capability_uuid
                else "?"
            )

            # Format duration nicely
            if duration_ms >= 3600000:
                duration_str = f"{duration_ms / 3600000:.1f}h"
            elif duration_ms >= 60000:
                duration_str = f"{duration_ms / 60000:.0f}m"
            else:
                duration_str = f"{duration_ms / 1000:.0f}s"

            print(f"  {step.index + 1}. {step.name} [{cap_name}] ({duration_str})")

        print()
        total_min = total_ms / 60000
        print(f"Total estimated time: {total_min:.0f} minutes")
        print(f"Plan confidence: {plan.confidence:.1%}")

    except GoalUnachievableError as e:
        print(f"✗ Planning failed: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
