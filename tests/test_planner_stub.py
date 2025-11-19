"""
Tests for the Planner Stub Service

Tests the planner stub API, models, and client functionality.
"""

import pytest
from planner_stub.client import PlannerClient
from planner_stub.models import PlanRequest, StateDescription
from planner_stub.planner import SimplePlanner


class TestPlannerModels:
    """Test planner data models."""
    
    def test_state_description_model(self):
        """Test StateDescription model."""
        state = StateDescription(properties={"gripper": "open", "object_grasped": False})
        assert "gripper" in state.properties
        assert state.properties["gripper"] == "open"
    
    def test_plan_request_model(self):
        """Test PlanRequest model."""
        request = PlanRequest(
            initial_state=StateDescription(properties={"gripper": "open"}),
            goal_state=StateDescription(properties={"object_grasped": True}),
            scenario_name="simple_grasp"
        )
        assert request.scenario_name == "simple_grasp"
        assert request.initial_state.properties["gripper"] == "open"


class TestSimplePlanner:
    """Test the SimplePlanner implementation."""
    
    def test_planner_initialization(self):
        """Test that planner initializes with scenarios."""
        planner = SimplePlanner()
        assert len(planner.scenarios) > 0
        assert "simple_grasp" in planner.scenarios
        assert "pick_and_place" in planner.scenarios
    
    def test_generate_plan_with_scenario_name(self):
        """Test plan generation with explicit scenario name."""
        planner = SimplePlanner()
        request = PlanRequest(
            initial_state=StateDescription(properties={}),
            goal_state=StateDescription(properties={}),
            scenario_name="simple_grasp"
        )
        
        response = planner.generate_plan(request)
        assert response.success is True
        assert response.scenario_name == "simple_grasp"
        assert len(response.plan) == 1
        assert response.plan[0].process == "GraspAction"
        assert response.plan[0].uuid is not None
    
    def test_generate_plan_pick_and_place(self):
        """Test pick and place plan generation."""
        planner = SimplePlanner()
        request = PlanRequest(
            initial_state=StateDescription(properties={"gripper": "open"}),
            goal_state=StateDescription(properties={"object_location": "bin"}),
            scenario_name="pick_and_place"
        )
        
        response = planner.generate_plan(request)
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
    
    def test_generate_plan_with_goal_matching(self):
        """Test plan generation with goal state matching."""
        planner = SimplePlanner()
        request = PlanRequest(
            initial_state=StateDescription(properties={"gripper": "open"}),
            goal_state=StateDescription(properties={"object_grasped": True}),
            scenario_name=None  # No explicit scenario
        )
        
        response = planner.generate_plan(request)
        assert response.success is True
        # Should match simple_grasp scenario
        assert len(response.plan) >= 1
    
    def test_generate_plan_fallback(self):
        """Test plan generation fallback for unmatched scenarios."""
        planner = SimplePlanner()
        request = PlanRequest(
            initial_state=StateDescription(properties={}),
            goal_state=StateDescription(properties={"unknown_goal": True}),
            scenario_name=None
        )
        
        response = planner.generate_plan(request)
        # Should fail gracefully or return minimal plan
        assert response.success is False or len(response.plan) == 0


@pytest.mark.skipif(
    not pytest.importorskip("httpx"),
    reason="httpx not installed - planner client tests require httpx"
)
class TestPlannerClient:
    """Test the PlannerClient (requires running planner service)."""
    
    @pytest.fixture
    def client(self):
        """Get a planner client instance."""
        return PlannerClient()
    
    def test_client_initialization(self, client):
        """Test client initializes with default URL."""
        assert client.base_url is not None
        assert "http" in client.base_url
    
    @pytest.mark.skipif(
        not PlannerClient().is_available(timeout=1.0),
        reason="Planner service not available"
    )
    def test_health_check(self, client):
        """Test health check endpoint."""
        health = client.health_check()
        assert "status" in health
        assert health["status"] == "healthy"
        assert "version" in health
    
    @pytest.mark.skipif(
        not PlannerClient().is_available(timeout=1.0),
        reason="Planner service not available"
    )
    def test_generate_plan_via_client(self, client):
        """Test plan generation via client."""
        response = client.generate_plan(
            initial_state={"gripper": "open"},
            goal_state={"object_grasped": True},
            scenario_name="simple_grasp"
        )
        
        assert response.success is True
        assert len(response.plan) > 0
        assert response.plan[0].process == "GraspAction"
    
    @pytest.mark.skipif(
        not PlannerClient().is_available(timeout=1.0),
        reason="Planner service not available"
    )
    def test_generate_plan_for_scenario(self, client):
        """Test convenience method for scenario-based planning."""
        response = client.generate_plan_for_scenario("pick_and_place")
        
        assert response.success is True
        assert response.scenario_name == "pick_and_place"
        assert len(response.plan) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
