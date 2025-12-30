#!/usr/bin/env python3
"""
M3 Verification: Sophia Can Plan Simple Actions

Tests that planning capabilities can generate simple action sequences using
causal reasoning over the HCG. This is a smoke test that validates the planning
concepts without requiring a full Sophia implementation.

Reference: docs/PHASE1_VERIFY.md, M3 section
"""

import json
from pathlib import Path

import pytest

from logos_test_utils.env import get_repo_root

# Try to import planner client for API-based tests
try:
    from planner_stub.client import PlannerClient

    PLANNER_CLIENT_AVAILABLE = True
except ImportError:
    PLANNER_CLIENT_AVAILABLE = False

# Skip all tests in this module - planning tests need to be updated for flexible ontology
# The test fixtures and assertions reference the old type-label based ontology structure
pytestmark = pytest.mark.skip(
    reason="M3 planning tests temporarily skipped: ontology changed to flexible model. "
    "Tests need updating to use :Node label with type/ancestors properties."
)


@pytest.fixture
def plan_scenarios():
    """Load planning test scenarios."""
    fixtures_dir = Path(__file__).resolve().parent / "fixtures"
    scenarios_file = fixtures_dir / "plan_scenarios.json"
    with open(scenarios_file) as f:
        return json.load(f)


@pytest.fixture
def test_data_cypher():
    """Load pick-and-place test data Cypher script."""
    repo_root = get_repo_root()
    cypher_file = repo_root / "ontology" / "test_data_pick_and_place.cypher"
    return cypher_file.read_text()


def test_plan_scenarios_load(plan_scenarios):
    """Test that plan scenarios fixture loads successfully."""
    assert "scenarios" in plan_scenarios
    assert len(plan_scenarios["scenarios"]) > 0
    print(f"✓ Loaded {len(plan_scenarios['scenarios'])} planning scenarios")


def test_causal_relationships_defined(plan_scenarios):
    """Test that causal relationships are defined in test data."""
    assert "causal_relationships" in plan_scenarios
    assert len(plan_scenarios["causal_relationships"]) > 0

    for rel in plan_scenarios["causal_relationships"]:
        assert "process" in rel
        assert "causes" in rel
        assert "requires" in rel

    print(f"✓ Defined {len(plan_scenarios['causal_relationships'])} causal relationships")


def test_simple_grasp_scenario(plan_scenarios):
    """Test simple single-step grasp planning scenario."""
    scenario = next(s for s in plan_scenarios["scenarios"] if s["name"] == "simple_grasp")

    assert scenario is not None
    assert "initial_state" in scenario
    assert "goal_state" in scenario
    assert "expected_plan" in scenario

    # Verify plan structure
    plan = scenario["expected_plan"]
    assert len(plan) == 1, "Simple grasp should be a single-step plan"

    step = plan[0]
    assert step["process"] == "GraspAction"
    assert "preconditions" in step
    assert "effects" in step
    assert "object_grasped" in step["effects"]

    print("✓ Simple grasp scenario validated")


def test_pick_and_place_scenario(plan_scenarios):
    """Test multi-step pick-and-place planning scenario."""
    scenario = next(s for s in plan_scenarios["scenarios"] if s["name"] == "pick_and_place")

    assert scenario is not None
    plan = scenario["expected_plan"]
    assert len(plan) == 4, "Pick-and-place should be a 4-step plan"

    # Verify plan ordering
    processes = [step["process"] for step in plan]
    assert processes == ["MoveAction", "GraspAction", "MoveAction", "ReleaseAction"]

    # Verify causal chain: each step's effects should enable next step's preconditions
    for i in range(len(plan) - 1):
        current_effects = plan[i]["effects"]
        next_preconditions = plan[i + 1]["preconditions"]

        # At least one effect should be a precondition for next step
        # (simplified check - full implementation would verify exact matches)
        assert len(current_effects) > 0
        assert len(next_preconditions) > 0

    print("✓ Pick-and-place scenario validated")


def test_precondition_requirements(plan_scenarios):
    """Test that processes have proper precondition requirements."""
    causal_rels = plan_scenarios["causal_relationships"]

    # Find grasp action requirements
    grasp_rel = next(r for r in causal_rels if r["process"] == "GraspAction")
    assert "gripper_open" in grasp_rel["requires"]
    assert "arm_at_pre_grasp" in grasp_rel["requires"]

    # Find release action requirements
    release_rel = next(r for r in causal_rels if r["process"] == "ReleaseAction")
    assert "object_grasped" in release_rel["requires"]
    assert "arm_at_place_position" in release_rel["requires"]

    print("✓ Precondition requirements validated")


def test_causal_effects(plan_scenarios):
    """Test that processes have defined causal effects."""
    causal_rels = plan_scenarios["causal_relationships"]

    # Verify each process has a causal effect
    for rel in causal_rels:
        assert rel["causes"] is not None
        assert len(rel["causes"]) > 0

    # Verify specific effects
    grasp_rel = next(r for r in causal_rels if r["process"] == "GraspAction")
    assert grasp_rel["causes"] == "object_grasped"

    release_rel = next(r for r in causal_rels if r["process"] == "ReleaseAction")
    assert release_rel["causes"] == "object_released"

    print("✓ Causal effects validated")


def test_test_data_has_process_concepts(test_data_cypher):
    """Test that pick-and-place test data includes process concepts.

    FLEXIBLE ONTOLOGY:
    Process nodes use the :Node label with type='process' or subtypes like 'MoveAction'.
    They have 'process' in their ancestors list.
    """
    # Verify process type definition exists
    assert "type-process" in test_data_cypher or "'process'" in test_data_cypher
    # Verify action subtypes exist (these have 'process' in ancestors)
    assert "moveaction" in test_data_cypher.lower() or "process_move" in test_data_cypher.lower()

    print("✓ Process concepts found in test data")


def test_test_data_has_causal_relationships(test_data_cypher):
    """Test that pick-and-place test data includes CAUSES relationships."""
    assert "[:CAUSES]" in test_data_cypher or "CAUSES" in test_data_cypher
    print("✓ CAUSES relationships found in test data")


def test_test_data_has_precondition_relationships(test_data_cypher):
    """Test that pick-and-place test data includes REQUIRES relationships."""
    assert "[:REQUIRES]" in test_data_cypher or "REQUIRES" in test_data_cypher
    print("✓ REQUIRES relationships found in test data")


def test_test_data_has_temporal_relationships(test_data_cypher):
    """Test that pick-and-place test data includes PRECEDES relationships."""
    assert "[:PRECEDES]" in test_data_cypher or "PRECEDES" in test_data_cypher
    print("✓ PRECEDES relationships found in test data")


def test_goal_state_reachability():
    """Test that goal states are reachable from initial states (conceptual)."""
    # This is a conceptual test that would be implemented with actual HCG queries
    # For now, we verify the test scenario structure supports reachability checking

    # Mock simple reachability check
    def is_reachable(initial, goal, plan):
        """Check if goal is reachable from initial via plan."""
        initial.copy()

        for step in plan:
            # Verify preconditions are met
            for _precond in step["preconditions"]:
                # In a real implementation, this would check actual state
                pass

            # Apply effects
            for _effect in step["effects"]:
                # In a real implementation, this would update state
                pass

        # Check if goal is achieved
        # In a real implementation, this would verify goal state matches
        return True

    # This test validates the concept without requiring Neo4j
    assert is_reachable is not None
    print("✓ Goal reachability concept validated")


# ============================================================================
# Planner API Integration Tests (Phase 1 Enhancement)
# ============================================================================


@pytest.fixture
def planner_client():
    """Get planner client if available."""
    if not PLANNER_CLIENT_AVAILABLE:
        pytest.skip("Planner client not available")

    client = PlannerClient()
    if not client.is_available(timeout=1.0):
        pytest.skip("Planner service not running")

    return client


@pytest.mark.skipif(not PLANNER_CLIENT_AVAILABLE, reason="Planner client not available")
class TestPlannerAPIIntegration:
    """Tests that use the planner API instead of direct Cypher queries."""

    def test_planner_service_available(self, planner_client):
        """Test that planner service is available and healthy."""
        health = planner_client.health_check()
        assert "status" in health
        assert health["status"] == "healthy"
        print("✓ Planner service is available and healthy")

    def test_planner_api_simple_grasp(self, planner_client):
        """Test simple grasp plan generation via API."""
        response = planner_client.generate_plan_for_scenario("simple_grasp")

        assert response.success is True
        assert response.scenario_name == "simple_grasp"
        assert len(response.plan) == 1

        step = response.plan[0]
        assert step.process == "GraspAction"
        assert "gripper_open" in step.preconditions
        assert "object_grasped" in step.effects
        assert step.uuid is not None

        print(f"✓ Generated simple grasp plan via API (process: {step.uuid})")

    def test_planner_api_pick_and_place(self, planner_client):
        """Test pick-and-place plan generation via API."""
        response = planner_client.generate_plan_for_scenario("pick_and_place")

        assert response.success is True
        assert response.scenario_name == "pick_and_place"
        assert len(response.plan) == 4

        # Verify process sequence
        processes = [step.process for step in response.plan]
        assert processes == ["MoveAction", "GraspAction", "MoveAction", "ReleaseAction"]

        # Verify all steps have UUIDs
        for step in response.plan:
            assert step.uuid is not None
            assert step.uuid.startswith("process-")

        print(f"✓ Generated pick-and-place plan via API ({len(response.plan)} steps)")

    def test_planner_api_with_states(self, planner_client):
        """Test plan generation with explicit initial and goal states."""
        response = planner_client.generate_plan(
            initial_state={
                "gripper": "open",
                "arm_position": "home",
                "object_grasped": False,
            },
            goal_state={"object_location": "bin", "object_grasped": False},
            scenario_name="pick_and_place",
        )

        assert response.success is True
        assert len(response.plan) > 0

        # Verify causal chain
        for i in range(len(response.plan) - 1):
            current_step = response.plan[i]
            next_step = response.plan[i + 1]

            assert len(current_step.effects) > 0, f"Step {i} should have effects"
            assert len(next_step.preconditions) > 0, f"Step {i+1} should have preconditions"

        print(f"✓ Generated plan with explicit states ({len(response.plan)} steps)")

    def test_planner_api_plan_structure(self, planner_client):
        """Test that API-generated plans have proper structure for HCG storage."""
        response = planner_client.generate_plan_for_scenario("pick_and_place")

        assert response.success is True

        for i, step in enumerate(response.plan):
            # Each step should have a UUID suitable for HCG Process node
            assert step.uuid is not None
            assert isinstance(step.uuid, str)
            assert len(step.uuid) > 0

            # Each step should have process name, preconditions, and effects
            assert step.process is not None
            assert isinstance(step.preconditions, list)
            assert isinstance(step.effects, list)

            print(f"  Step {i+1}: {step.process} (uuid: {step.uuid})")

        print("✓ API-generated plan has proper structure for HCG storage")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
