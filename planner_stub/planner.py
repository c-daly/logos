"""
Simple Planner Stub Implementation

This stub planner uses pre-defined scenarios from the plan_scenarios.json fixture
to generate plans. It provides basic planning capabilities without requiring
full causal reasoning implementation.

For Phase 1, this demonstrates the planner API contract and integration points.
"""

import json
import uuid
from typing import Any, cast

from logos_test_utils.env import get_repo_root

from .models import PlanRequest, PlanResponse, ProcessStep, StateDescription

# Load plan scenarios from fixtures
REPO_ROOT = get_repo_root()
FIXTURES_DIR = REPO_ROOT / "tests" / "integration" / "planning" / "fixtures"
SCENARIOS_FILE = FIXTURES_DIR / "plan_scenarios.json"


def load_scenarios() -> dict[str, Any]:
    """Load planning scenarios from fixtures."""
    if not SCENARIOS_FILE.exists():
        return {"scenarios": [], "causal_relationships": []}

    with open(SCENARIOS_FILE) as f:
        return cast(dict[str, Any], json.load(f))


class SimplePlanner:
    """Simple stub planner that uses pre-defined scenarios."""

    def __init__(self):
        """Initialize the planner with scenario fixtures."""
        self.scenarios_data = load_scenarios()
        self.scenarios = {
            s["name"]: s for s in self.scenarios_data.get("scenarios", [])
        }

    def generate_plan(self, request: PlanRequest) -> PlanResponse:
        """
        Generate a plan from initial state to goal state.

        For Phase 1, this uses pre-defined scenarios. A full implementation
        would perform causal reasoning over the HCG.

        Args:
            request: PlanRequest with initial_state, goal_state, and optional scenario_name

        Returns:
            PlanResponse with the generated plan or error
        """
        # If scenario name is provided, use that scenario
        if request.scenario_name and request.scenario_name in self.scenarios:
            scenario = self.scenarios[request.scenario_name]
            return self._build_response_from_scenario(scenario)

        # Try to match based on goal state
        matched_scenario = self._match_scenario(
            request.initial_state, request.goal_state
        )
        if matched_scenario:
            return self._build_response_from_scenario(matched_scenario)

        # If no match, try to generate a simple plan
        return self._generate_simple_plan(request)

    def _match_scenario(
        self, initial_state: StateDescription, goal_state: StateDescription
    ) -> dict[str, Any] | None:
        """Match request to a known scenario based on goal state."""
        for scenario in self.scenarios.values():
            # Simple matching: if the goal has object_grasped=true, use simple_grasp
            if goal_state.properties.get("object_grasped") is True:
                if "object_location" not in goal_state.properties:
                    # Just grasping, not moving
                    if scenario["name"] == "simple_grasp":
                        return cast(dict[str, Any], scenario)
                else:
                    # Pick and place
                    if scenario["name"] == "pick_and_place":
                        return cast(dict[str, Any], scenario)
        return None

    def _build_response_from_scenario(self, scenario: dict[str, Any]) -> PlanResponse:
        """Build a PlanResponse from a scenario definition."""
        plan_steps = []
        for step in scenario["expected_plan"]:
            # Generate UUID for each process step
            process_uuid = f"process-{step['process'].lower()}-{uuid.uuid4().hex[:8]}"

            plan_steps.append(
                ProcessStep(
                    process=step["process"],
                    preconditions=step["preconditions"],
                    effects=step["effects"],
                    uuid=process_uuid,
                )
            )

        return PlanResponse(
            plan=plan_steps,
            success=True,
            message=f"Plan generated for scenario: {scenario['name']}",
            scenario_name=scenario["name"],
        )

    def _generate_simple_plan(self, request: PlanRequest) -> PlanResponse:
        """
        Generate a simple plan when no scenario matches.

        This is a fallback that creates a minimal valid plan.
        """
        # For now, return a simple grasp action if goal involves grasping
        if request.goal_state.properties.get("object_grasped"):
            process_uuid = f"process-graspaction-{uuid.uuid4().hex[:8]}"
            plan_steps = [
                ProcessStep(
                    process="GraspAction",
                    preconditions=["gripper_open", "arm_at_pre_grasp"],
                    effects=["object_grasped"],
                    uuid=process_uuid,
                )
            ]
            return PlanResponse(
                plan=plan_steps,
                success=True,
                message="Generated simple grasp plan",
                scenario_name=None,
            )

        # No plan could be generated
        return PlanResponse(
            plan=[],
            success=False,
            message="Could not generate plan for given initial and goal states",
            scenario_name=None,
        )


# Global planner instance
_planner_instance: SimplePlanner | None = None


def get_planner() -> SimplePlanner:
    """Get or create the global planner instance."""
    global _planner_instance
    if _planner_instance is None:
        _planner_instance = SimplePlanner()
    return _planner_instance
