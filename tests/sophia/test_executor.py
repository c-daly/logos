"""
Unit tests for Executor module

Tests cover:
- Plan execution
- Status management
- Callback mechanisms
"""

from sophia.executor import ExecutionResult, ExecutionStatus, Executor
from sophia.planner import Action, Plan, PlanStatus


class TestExecutor:
    """Test suite for Executor class"""

    def test_initialization(self):
        """Test Executor initializes with correct default state"""
        executor = Executor()
        assert executor.current_plan is None
        assert executor.execution_status == ExecutionStatus.NOT_STARTED
        assert executor.current_action_index == 0
        assert len(executor.execution_results) == 0

    def test_execute_plan_with_empty_plan(self):
        """Test executing a plan with no actions"""
        executor = Executor()

        plan = Plan(
            goal={},
            actions=[],
            status=PlanStatus.VALIDATED,
            validation_errors=[]
        )

        result = executor.execute_plan(plan)

        assert result is True
        assert executor.execution_status == ExecutionStatus.COMPLETED

    def test_execute_plan_with_actions(self):
        """Test executing a plan with actions"""
        executor = Executor()

        plan = Plan(
            goal={"test": "goal"},
            actions=[
                Action("action1", {}, [], []),
                Action("action2", {}, [], [])
            ],
            status=PlanStatus.VALIDATED,
            validation_errors=[]
        )

        result = executor.execute_plan(plan)

        assert result is True
        assert executor.execution_status == ExecutionStatus.COMPLETED
        assert len(executor.execution_results) == 2

    def test_success_callback_invoked(self):
        """Test that success callbacks are invoked"""
        executor = Executor()
        callback_invoked = []

        def success_callback():
            callback_invoked.append(True)

        executor.register_success_callback(success_callback)

        plan = Plan(goal={}, actions=[], status=PlanStatus.VALIDATED, validation_errors=[])
        executor.execute_plan(plan)

        assert len(callback_invoked) == 1

    def test_pause_and_resume_execution(self):
        """Test pausing and resuming execution"""
        executor = Executor()
        executor.execution_status = ExecutionStatus.RUNNING

        executor.pause_execution()
        assert executor.execution_status == ExecutionStatus.PAUSED

        result = executor.resume_execution()
        assert result is True
        assert executor.execution_status == ExecutionStatus.RUNNING

    def test_abort_execution(self):
        """Test aborting execution"""
        executor = Executor()
        callback_invoked = []

        def failure_callback(result):
            callback_invoked.append(result)

        executor.register_failure_callback(failure_callback)
        executor.execution_status = ExecutionStatus.RUNNING

        executor.abort_execution()

        assert executor.execution_status == ExecutionStatus.FAILED
        assert len(callback_invoked) == 1
        assert isinstance(callback_invoked[0], ExecutionResult)

    def test_get_execution_status(self):
        """Test getting execution status"""
        executor = Executor()

        status = executor.get_execution_status()
        assert status == ExecutionStatus.NOT_STARTED

    def test_get_execution_results(self):
        """Test getting execution results"""
        executor = Executor()

        results = executor.get_execution_results()
        assert isinstance(results, list)
        assert len(results) == 0

    def test_register_failure_callback(self):
        """Test registering failure callback"""
        executor = Executor()

        def failure_callback(result):
            pass

        executor.register_failure_callback(failure_callback)

        assert failure_callback in executor.failure_callbacks
