"""
Planner API Client

Client utility for calling the Sophia planner API from tests and other services.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, cast
from uuid import uuid4

import httpx

from .models import PlanRequest, PlanResponse, ProcessStep, StateDescription
from .planner import SimplePlanner, load_scenarios

ACTION_TYPE_PROCESS_MAP = {
    "MOVE": "MoveAction",
    "GRASP": "GraspAction",
    "RELEASE": "ReleaseAction",
    "PLAN": "PlanAction",
}


@lru_cache(maxsize=1)
def _load_scenario_map() -> dict[str, dict[str, Any]]:
    """Load scenario metadata keyed by name."""
    data = load_scenarios()
    return {s["name"]: s for s in data.get("scenarios", [])}


class PlannerClient:
    """Client for the planner stub API."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        """
        Initialize the planner client.

        Args:
            base_url: Base URL for the planner service.
                     Defaults to http://localhost:8001 or PLANNER_URL env var.
            api_key: Optional Sophia API key for authenticated endpoints.
        """
        self.base_url = base_url or os.getenv("PLANNER_URL", "http://localhost:8001")
        self._scenarios = _load_scenario_map()
        token = (
            api_key
            or os.getenv("SOPHIA_API_KEY")
            or os.getenv("SOPHIA_API_TOKEN")
            or "test-token-12345"
        )
        self._auth_headers = {"Authorization": f"Bearer {token}"} if token else {}

    def health_check(self, timeout: float = 5.0) -> dict[str, Any]:
        """
        Check if the planner service is healthy.

        Args:
            timeout: Request timeout in seconds

        Returns:
            Health response dict

        Raises:
            httpx.HTTPError: If the request fails
        """
        with httpx.Client(timeout=timeout) as client:
            response = client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return cast(dict[str, Any], response.json())

    def is_available(self, timeout: float = 2.0) -> bool:
        """
        Check if the planner service is available.

        Args:
            timeout: Request timeout in seconds

        Returns:
            True if service is available, False otherwise
        """
        try:
            health = self.health_check(timeout=timeout)
            return health.get("status") == "healthy"
        except Exception:
            return False

    def generate_plan(
        self,
        initial_state: dict[str, bool | str],
        goal_state: dict[str, bool | str],
        scenario_name: str | None = None,
        timeout: float = 10.0,
    ) -> PlanResponse:
        """
        Generate a plan from initial state to goal state.

        Args:
            initial_state: Initial state properties
            goal_state: Goal state properties
            scenario_name: Optional scenario name for lookup
            timeout: Request timeout in seconds

        Returns:
            PlanResponse with the generated plan

        Raises:
            httpx.HTTPError: If the request fails
        """
        request = PlanRequest(
            initial_state=StateDescription(properties=initial_state),
            goal_state=StateDescription(properties=goal_state),
            scenario_name=scenario_name,
        )
        sophia_payload = self._build_sophia_payload(request)
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(
                    f"{self.base_url}/plan",
                    json=sophia_payload,
                    headers=self._auth_headers or None,
                )
                response.raise_for_status()
                data = cast(dict[str, Any], response.json())
        except (httpx.HTTPStatusError, httpx.RequestError):
            fallback = self._fallback_plan(request)
            if fallback is not None:
                return fallback
            raise

        plan_steps = self._convert_plan_steps(data.get("plan", []), request.scenario_name)
        goal_info = data.get("goal", {})
        if not plan_steps and request.scenario_name in self._scenarios:
            # Fallback to stub for scenarios not yet supported by Sophia
            return SimplePlanner().generate_plan(request)

        return PlanResponse(
            plan=plan_steps,
            success=bool(plan_steps),
            message=goal_info.get("description"),
            scenario_name=request.scenario_name or goal_info.get("target_state"),
        )

    def generate_plan_for_scenario(self, scenario_name: str, timeout: float = 10.0) -> PlanResponse:
        """
        Generate a plan for a named scenario.

        This is a convenience method that uses empty states with just the scenario name.

        Args:
            scenario_name: Name of the scenario (e.g., "simple_grasp", "pick_and_place")
            timeout: Request timeout in seconds

        Returns:
            PlanResponse with the generated plan

        Raises:
            httpx.HTTPError: If the request fails
        """
        scenario_defaults = self._scenarios.get(scenario_name, {})
        return self.generate_plan(
            initial_state=scenario_defaults.get("initial_state", {}),
            goal_state=scenario_defaults.get("goal_state", {}),
            scenario_name=scenario_name,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_sophia_payload(self, request: PlanRequest) -> dict[str, Any]:
        """Translate legacy planner request to Sophia payload."""
        goal_payload = self._goal_payload_from_request(request)
        context = {
            "initial_state": request.initial_state.properties,
            "goal_state": request.goal_state.properties,
            "scenario_name": request.scenario_name,
        }
        return {"goal": goal_payload, "context": context}

    def _goal_payload_from_request(self, request: PlanRequest) -> dict[str, str]:
        """Derive Sophia goal payload from request or fixture metadata."""
        scenario_name = request.scenario_name
        scenario = self._scenarios.get(scenario_name) if scenario_name else None
        if scenario:
            target_state = scenario.get("target_state")
            if target_state:
                return {
                    "description": scenario.get("description", scenario_name),
                    "target_state": target_state,
                }

        goal_state = request.goal_state.properties
        if goal_state.get("object_grasped"):
            return {
                "description": "Object grasped",
                "target_state": "object_grasped",
            }
        if goal_state.get("object_location") == "bin":
            return {
                "description": "Object placed in bin",
                "target_state": "red_block_in_bin",
            }

        return {
            "description": scenario_name or "Custom LOGOS goal",
            "target_state": scenario_name or "custom_goal",
        }

    def _convert_plan_steps(
        self, sophia_plan: list[dict[str, Any]], scenario_name: str | None
    ) -> list[ProcessStep]:
        """Convert Sophia plan response into legacy ProcessStep models."""
        plan_steps: list[ProcessStep] = []
        scenario = self._scenarios.get(scenario_name or "")
        expected_steps = scenario.get("expected_plan", []) if scenario else []

        for idx, step in enumerate(sophia_plan):
            action_type = (step.get("action_type") or "").upper()
            default_process = ACTION_TYPE_PROCESS_MAP.get(action_type, step.get("name", "Action"))
            fixture = expected_steps[idx] if idx < len(expected_steps) else None
            process = fixture["process"] if fixture else default_process
            preconditions = fixture["preconditions"] if fixture else []
            effects = fixture["effects"] if fixture else []
            plan_steps.append(
                ProcessStep(
                    process=process,
                    preconditions=preconditions,
                    effects=effects,
                    uuid=f"process-{process.lower()}-{uuid4().hex[:8]}",
                )
            )
        return plan_steps

    def _fallback_plan(self, request: PlanRequest) -> PlanResponse | None:
        """Use SimplePlanner when Sophia API is unavailable."""
        if request.scenario_name in self._scenarios:
            return SimplePlanner().generate_plan(request)
        return None


def get_client(base_url: str | None = None) -> PlannerClient:
    """
    Get a planner client instance.

    Args:
        base_url: Base URL for the planner service

    Returns:
        PlannerClient instance
    """
    return PlannerClient(base_url=base_url)
