"""
Unit tests for Planner module

Tests cover:
- Plan generation (stub)
- Plan validation
- Backward chaining infrastructure
"""

from sophia.planner import Action, Plan, Planner, PlanStatus


class TestPlanner:
    """Test suite for Planner class"""

    def test_initialization(self):
        """Test Planner initializes with no active plan"""
        planner = Planner()
        assert planner.current_plan is None
        assert len(planner.plan_history) == 0
        assert planner.validation_enabled is True

    def test_generate_plan_creates_plan(self):
        """Test that generate_plan creates a Plan object"""
        planner = Planner()

        goal = {"cup": {"location": "on_table"}}
        current_state = {"cup": {"location": "in_hand"}}

        plan = planner.generate_plan(goal, current_state)

        assert isinstance(plan, Plan)
        assert plan.goal == goal
        assert plan.status == PlanStatus.DRAFT
        assert planner.current_plan is plan

    def test_validate_plan_with_validation_enabled(self):
        """Test plan validation when enabled"""
        planner = Planner()

        goal = {"test": "goal"}
        current_state = {"test": "state"}
        plan = planner.generate_plan(goal, current_state)

        result = planner.validate_plan(plan)

        assert isinstance(result, bool)
        assert plan.status == PlanStatus.VALIDATED

    def test_validate_plan_with_validation_disabled(self):
        """Test plan validation when disabled"""
        planner = Planner()
        planner.validation_enabled = False

        goal = {"test": "goal"}
        current_state = {"test": "state"}
        plan = planner.generate_plan(goal, current_state)

        result = planner.validate_plan(plan)

        assert result is True
        assert plan.status == PlanStatus.VALIDATED

    def test_estimate_plan_cost(self):
        """Test plan cost estimation"""
        planner = Planner()

        plan = Plan(
            goal={},
            actions=[
                Action("action1", {}, [], []),
                Action("action2", {}, [], []),
                Action("action3", {}, [], [])
            ],
            status=PlanStatus.DRAFT,
            validation_errors=[]
        )

        cost = planner.estimate_plan_cost(plan)

        assert cost == 3.0

    def test_execute_backward_chaining_returns_list(self):
        """Test that backward chaining returns a list"""
        planner = Planner()

        result = planner.execute_backward_chaining("goal_id", "current_id")

        assert isinstance(result, list)

    def test_replan_returns_none_for_stub(self):
        """Test that replan returns None in stub implementation"""
        planner = Planner()

        result = planner.replan(0)

        assert result is None

    def test_get_current_plan(self):
        """Test getting current plan"""
        planner = Planner()

        assert planner.get_current_plan() is None

        goal = {"test": "goal"}
        current_state = {"test": "state"}
        plan = planner.generate_plan(goal, current_state)

        assert planner.get_current_plan() is plan
