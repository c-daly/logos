"""
Planner API Client

Client utility for calling the planner stub API from tests and other services.
"""

import os

import httpx

from .models import PlanRequest, PlanResponse, StateDescription


class PlannerClient:
    """Client for the planner stub API."""

    def __init__(self, base_url: str | None = None):
        """
        Initialize the planner client.

        Args:
            base_url: Base URL for the planner service.
                     Defaults to http://localhost:8001 or PLANNER_URL env var.
        """
        self.base_url = base_url or os.getenv("PLANNER_URL", "http://localhost:8001")

    def health_check(self, timeout: float = 5.0) -> dict:
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
            return response.json()

    def is_available(self, timeout: float = 2.0) -> bool:
        """
        Check if the planner service is available.

        Args:
            timeout: Request timeout in seconds

        Returns:
            True if service is available, False otherwise
        """
        try:
            self.health_check(timeout=timeout)
            return True
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

        with httpx.Client(timeout=timeout) as client:
            response = client.post(f"{self.base_url}/plan", json=request.model_dump())
            response.raise_for_status()
            return PlanResponse(**response.json())

    def generate_plan_for_scenario(
        self, scenario_name: str, timeout: float = 10.0
    ) -> PlanResponse:
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
        return self.generate_plan(
            initial_state={},
            goal_state={},
            scenario_name=scenario_name,
            timeout=timeout,
        )


def get_client(base_url: str | None = None) -> PlannerClient:
    """
    Get a planner client instance.

    Args:
        base_url: Base URL for the planner service

    Returns:
        PlannerClient instance
    """
    return PlannerClient(base_url=base_url)
