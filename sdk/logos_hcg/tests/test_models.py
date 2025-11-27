"""Tests for HCG data models."""

from datetime import datetime

import pytest

from logos_hcg.models import (
    CausalEdge,
    Entity,
    GraphSnapshot,
    PersonaEntry,
    PlanHistory,
    Process,
    State,
    StateHistory,
)


class TestEntity:
    """Test Entity model."""

    def test_minimal_entity(self) -> None:
        """Test entity with required fields only."""
        entity = Entity(id="entity_123", type="manipulator")

        assert entity.id == "entity_123"
        assert entity.type == "manipulator"
        assert entity.properties == {}
        assert entity.labels == []
        assert entity.created_at is None

    def test_full_entity(self) -> None:
        """Test entity with all fields."""
        now = datetime.now()
        entity = Entity(
            id="entity_456",
            type="object",
            properties={"name": "cube", "color": "red"},
            labels=["Entity", "Object"],
            created_at=now,
            updated_at=now,
        )

        assert entity.id == "entity_456"
        assert entity.type == "object"
        assert entity.properties["name"] == "cube"
        assert "Entity" in entity.labels
        assert entity.created_at == now


class TestState:
    """Test State model."""

    def test_state_defaults(self) -> None:
        """Test state with defaults."""
        state = State(id="state_123")

        assert state.id == "state_123"
        assert state.type == "state"
        assert state.description == ""
        assert state.variables == {}
        assert state.timestamp is not None

    def test_state_with_variables(self) -> None:
        """Test state with variables."""
        state = State(
            id="state_456",
            description="Object at position A",
            variables={"x": 1.0, "y": 2.0, "z": 0.0},
        )

        assert state.description == "Object at position A"
        assert state.variables["x"] == 1.0


class TestProcess:
    """Test Process model."""

    def test_process_defaults(self) -> None:
        """Test process with defaults."""
        process = Process(id="proc_123", name="grasp")

        assert process.id == "proc_123"
        assert process.name == "grasp"
        assert process.status == "pending"
        assert process.inputs == []
        assert process.outputs == []

    def test_process_with_io(self) -> None:
        """Test process with inputs/outputs."""
        process = Process(
            id="proc_456",
            name="move",
            description="Move object from A to B",
            status="completed",
            inputs=["state_a"],
            outputs=["state_b"],
        )

        assert process.status == "completed"
        assert "state_a" in process.inputs


class TestCausalEdge:
    """Test CausalEdge model."""

    def test_causal_edge(self) -> None:
        """Test causal edge creation."""
        edge = CausalEdge(
            id="edge_123",
            source_id="proc_1",
            target_id="state_1",
            edge_type="CAUSES",
        )

        assert edge.id == "edge_123"
        assert edge.edge_type == "CAUSES"
        assert edge.weight == 1.0

    def test_edge_with_weight(self) -> None:
        """Test edge with custom weight."""
        edge = CausalEdge(
            id="edge_456",
            source_id="a",
            target_id="b",
            edge_type="INFLUENCES",
            weight=0.75,
        )

        assert edge.weight == 0.75


class TestPlanHistory:
    """Test PlanHistory model."""

    def test_plan_history(self) -> None:
        """Test plan history record."""
        plan = PlanHistory(
            id="plan_123",
            goal_id="goal_456",
            status="completed",
            steps=[{"action": "grasp"}, {"action": "move"}],
        )

        assert plan.id == "plan_123"
        assert plan.goal_id == "goal_456"
        assert len(plan.steps) == 2


class TestStateHistory:
    """Test StateHistory model."""

    def test_state_history(self) -> None:
        """Test state history record."""
        history = StateHistory(
            id="hist_123",
            state_id="state_456",
            changes={"x": 2.0},
            previous_values={"x": 1.0},
            trigger="process_execution",
        )

        assert history.state_id == "state_456"
        assert history.changes["x"] == 2.0
        assert history.trigger == "process_execution"


class TestGraphSnapshot:
    """Test GraphSnapshot model."""

    def test_empty_snapshot(self) -> None:
        """Test empty graph snapshot."""
        snapshot = GraphSnapshot()

        assert snapshot.entities == []
        assert snapshot.edges == []
        assert snapshot.metadata == {}

    def test_snapshot_with_data(self) -> None:
        """Test snapshot with entities and edges."""
        entity = Entity(id="e1", type="test")
        edge = CausalEdge(
            id="r1", source_id="e1", target_id="e2", edge_type="RELATES"
        )

        snapshot = GraphSnapshot(
            entities=[entity],
            edges=[edge],
            metadata={"entity_count": 1, "edge_count": 1},
        )

        assert len(snapshot.entities) == 1
        assert len(snapshot.edges) == 1
        assert snapshot.metadata["entity_count"] == 1


class TestPersonaEntry:
    """Test PersonaEntry model."""

    def test_minimal_persona_entry(self) -> None:
        """Test persona entry with required fields."""
        entry = PersonaEntry(
            id="entry_123",
            entry_type="observation",
            content="User requested help with task.",
        )

        assert entry.id == "entry_123"
        assert entry.entry_type == "observation"
        assert entry.sentiment is None
        assert entry.confidence is None

    def test_full_persona_entry(self) -> None:
        """Test persona entry with all fields."""
        entry = PersonaEntry(
            id="entry_456",
            entry_type="reflection",
            content="I noticed I made an error in the previous step.",
            summary="Error recognition",
            sentiment="negative",
            confidence=0.85,
            related_process_ids=["proc_1"],
            emotion_tags=["cautious", "learning"],
            trigger="error",
        )

        assert entry.sentiment == "negative"
        assert entry.confidence == 0.85
        assert entry.trigger == "error"
        assert "cautious" in entry.emotion_tags

    def test_confidence_bounds(self) -> None:
        """Test confidence value bounds."""
        # Valid bounds
        entry = PersonaEntry(
            id="e1", entry_type="belief", content="test", confidence=0.0
        )
        assert entry.confidence == 0.0

        entry = PersonaEntry(
            id="e2", entry_type="belief", content="test", confidence=1.0
        )
        assert entry.confidence == 1.0

        # Invalid bounds
        with pytest.raises(ValueError):
            PersonaEntry(
                id="e3", entry_type="belief", content="test", confidence=-0.1
            )

        with pytest.raises(ValueError):
            PersonaEntry(
                id="e4", entry_type="belief", content="test", confidence=1.1
            )
