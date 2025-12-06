"""Unit tests for planning models (logos#157 + sophia#15)."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from logos_hcg import (
    Goal,
    GoalStatus,
    GoalTarget,
    Plan,
    PlanStatus,
    PlanStep,
    Provenance,
    SourceService,
)


class TestProvenance:
    """Tests for Provenance model."""

    def test_valid_provenance(self):
        """Test creating a valid Provenance."""
        prov = Provenance(
            source_service=SourceService.SOPHIA,
            author_id=uuid4(),
            created_at=datetime.now(UTC),
            trace_id=uuid4(),
            tags=["test", "unit"],
        )
        assert prov.source_service == "sophia"
        assert len(prov.tags) == 2

    def test_provenance_minimal(self):
        """Test Provenance with only required fields."""
        prov = Provenance(
            source_service=SourceService.HUMAN,
            created_at=datetime.now(UTC),
        )
        assert prov.author_id is None
        assert prov.trace_id is None
        assert prov.tags == []

    def test_provenance_invalid_source(self):
        """Test that invalid source_service raises error."""
        with pytest.raises(ValueError, match="source_service must be one of"):
            Provenance(
                source_service="invalid_service",
                created_at=datetime.now(UTC),
            )


class TestGoalTarget:
    """Tests for GoalTarget model."""

    def test_valid_goal_target(self):
        """Test creating a valid GoalTarget."""
        entity_id = uuid4()
        concept_id = uuid4()
        target = GoalTarget(
            entity_uuid=entity_id,
            concept_uuid=concept_id,
            state_properties={"is_grasped": True},
        )
        assert target.entity_uuid == entity_id
        assert target.concept_uuid == concept_id
        assert target.state_properties == {"is_grasped": True}

    def test_goal_target_minimal(self):
        """Test GoalTarget with only required fields."""
        entity_id = uuid4()
        target = GoalTarget(entity_uuid=entity_id)
        assert target.entity_uuid == entity_id
        assert target.concept_uuid is None
        assert target.state_properties is None


class TestGoal:
    """Tests for Goal model."""

    @pytest.fixture
    def sample_provenance(self):
        """Create a sample provenance for tests."""
        return Provenance(
            source_service=SourceService.SOPHIA,
            created_at=datetime.now(UTC),
        )

    @pytest.fixture
    def sample_target(self):
        """Create a sample goal target for tests."""
        return GoalTarget(entity_uuid=uuid4())

    def test_valid_goal(self, sample_provenance, sample_target):
        """Test creating a valid Goal."""
        goal = Goal(
            uuid=uuid4(),
            description="Move red block to bin",
            target=sample_target,
            provenance=sample_provenance,
        )
        assert goal.status == GoalStatus.PENDING
        assert goal.priority == 1.0

    def test_goal_with_status(self, sample_provenance, sample_target):
        """Test Goal with explicit status."""
        goal = Goal(
            uuid=uuid4(),
            description="Test goal",
            target=sample_target,
            status=GoalStatus.ACTIVE,
            priority=2.0,
            provenance=sample_provenance,
        )
        assert goal.status == "active"
        assert goal.priority == 2.0

    def test_goal_invalid_status(self, sample_provenance, sample_target):
        """Test that invalid status raises error."""
        with pytest.raises(ValueError, match="status must be one of"):
            Goal(
                uuid=uuid4(),
                description="Test goal",
                target=sample_target,
                status="invalid_status",
                provenance=sample_provenance,
            )


class TestPlanStep:
    """Tests for PlanStep model."""

    @pytest.fixture
    def sample_provenance(self):
        """Create a sample provenance for tests."""
        return Provenance(
            source_service=SourceService.SOPHIA,
            created_at=datetime.now(UTC),
        )

    def test_valid_plan_step(self, sample_provenance):
        """Test creating a valid PlanStep."""
        step = PlanStep(
            uuid=uuid4(),
            index=0,
            process_uuid=uuid4(),
            precondition_uuids=[uuid4(), uuid4()],
            effect_uuids=[uuid4()],
            capability_uuid=uuid4(),
            estimated_duration_ms=5000,
            confidence=0.95,
            provenance=sample_provenance,
        )
        assert step.index == 0
        assert len(step.precondition_uuids) == 2
        assert step.confidence == 0.95

    def test_plan_step_minimal(self, sample_provenance):
        """Test PlanStep with only required fields."""
        step = PlanStep(
            uuid=uuid4(),
            index=0,
            process_uuid=uuid4(),
            provenance=sample_provenance,
        )
        assert step.precondition_uuids == []
        assert step.effect_uuids == []
        assert step.capability_uuid is None
        assert step.confidence == 1.0

    def test_plan_step_invalid_index(self, sample_provenance):
        """Test that negative index raises error."""
        with pytest.raises(ValueError):
            PlanStep(
                uuid=uuid4(),
                index=-1,
                process_uuid=uuid4(),
                provenance=sample_provenance,
            )

    def test_plan_step_invalid_confidence(self, sample_provenance):
        """Test that confidence out of range raises error."""
        with pytest.raises(ValueError):
            PlanStep(
                uuid=uuid4(),
                index=0,
                process_uuid=uuid4(),
                confidence=1.5,
                provenance=sample_provenance,
            )


class TestPlan:
    """Tests for Plan model."""

    @pytest.fixture
    def sample_provenance(self):
        """Create a sample provenance for tests."""
        return Provenance(
            source_service=SourceService.SOPHIA,
            created_at=datetime.now(UTC),
        )

    @pytest.fixture
    def sample_steps(self, sample_provenance):
        """Create sample plan steps for tests."""
        return [
            PlanStep(
                uuid=uuid4(),
                index=0,
                process_uuid=uuid4(),
                provenance=sample_provenance,
            ),
            PlanStep(
                uuid=uuid4(),
                index=1,
                process_uuid=uuid4(),
                provenance=sample_provenance,
            ),
        ]

    def test_valid_plan(self, sample_provenance, sample_steps):
        """Test creating a valid Plan."""
        plan = Plan(
            uuid=uuid4(),
            goal_uuid=uuid4(),
            steps=sample_steps,
            current_state_uuid=uuid4(),
            expected_final_state_uuid=uuid4(),
            provenance=sample_provenance,
        )
        assert plan.status == PlanStatus.PENDING
        assert len(plan.steps) == 2

    def test_plan_invalid_status(self, sample_provenance, sample_steps):
        """Test that invalid status raises error."""
        with pytest.raises(ValueError, match="status must be one of"):
            Plan(
                uuid=uuid4(),
                goal_uuid=uuid4(),
                steps=sample_steps,
                current_state_uuid=uuid4(),
                status="invalid",
                provenance=sample_provenance,
            )

    def test_plan_empty_steps(self, sample_provenance):
        """Test Plan with empty steps list."""
        plan = Plan(
            uuid=uuid4(),
            goal_uuid=uuid4(),
            steps=[],
            current_state_uuid=uuid4(),
            provenance=sample_provenance,
        )
        assert plan.steps == []
