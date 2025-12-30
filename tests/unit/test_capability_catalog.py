"""
Unit tests for HCG Capability model and queries.

Tests the capability catalog schema and query patterns for logos#284.
"""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from logos_hcg import Capability, ExecutorType
from logos_hcg.queries import HCGQueries

# Skip all tests - capability catalog not yet implemented
pytestmark = pytest.mark.skip(
    reason="Capability catalog not yet implemented. "
    "These tests define the expected API for future development."
)


class TestExecutorType:
    """Tests for ExecutorType constants."""

    def test_executor_types_defined(self):
        """All executor types should be defined."""
        assert ExecutorType.HUMAN == "human"
        assert ExecutorType.TALOS == "talos"
        assert ExecutorType.SERVICE == "service"
        assert ExecutorType.LLM == "llm"

    def test_all_contains_all_types(self):
        """ALL should contain all executor types."""
        assert len(ExecutorType.ALL) == 4
        assert ExecutorType.HUMAN in ExecutorType.ALL
        assert ExecutorType.TALOS in ExecutorType.ALL
        assert ExecutorType.SERVICE in ExecutorType.ALL
        assert ExecutorType.LLM in ExecutorType.ALL


class TestCapabilityModel:
    """Tests for Capability Pydantic model."""

    def test_minimal_capability(self):
        """Create capability with only required fields."""
        test_uuid = uuid4()
        cap = Capability(
            uuid=test_uuid,
            name="TestCapability",
            executor_type="human",
        )
        assert cap.uuid == test_uuid
        assert cap.name == "TestCapability"
        assert cap.executor_type == "human"
        assert cap.deprecated is False
        assert cap.capability_tags == []

    def test_full_capability(self):
        """Create capability with all fields."""
        now = datetime.now()
        cap = Capability(
            uuid=uuid4(),
            name="FullCapability",
            executor_type="talos",
            description="A complete capability",
            capability_tags=["manipulation", "pick"],
            estimated_duration_ms=5000,
            estimated_cost=1.5,
            success_rate=0.95,
            invocation_count=100,
            service_endpoint=None,
            action_name="/talos/pick",
            instruction_template=None,
            prompt_template=None,
            version="1.0.0",
            deprecated=False,
            created_at=now,
            updated_at=now,
        )
        assert cap.description == "A complete capability"
        assert cap.capability_tags == ["manipulation", "pick"]
        assert cap.estimated_duration_ms == 5000
        assert cap.estimated_cost == 1.5
        assert cap.success_rate == 0.95
        assert cap.invocation_count == 100
        assert cap.action_name == "/talos/pick"
        assert cap.version == "1.0.0"

    def test_invalid_executor_type(self):
        """Invalid executor type should raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Capability(
                uuid=uuid4(),
                name="BadCapability",
                executor_type="invalid",
            )
        assert "executor_type must be one of" in str(exc_info.value)

    def test_success_rate_bounds(self):
        """Success rate must be between 0 and 1."""
        # Valid success rates
        cap = Capability(
            uuid=uuid4(),
            name="RateCapability",
            executor_type="service",
            success_rate=0.5,
        )
        assert cap.success_rate == 0.5

        # At boundaries
        cap_low = Capability(
            uuid=uuid4(),
            name="LowRate",
            executor_type="service",
            success_rate=0.0,
        )
        assert cap_low.success_rate == 0.0

        cap_high = Capability(
            uuid=uuid4(),
            name="HighRate",
            executor_type="service",
            success_rate=1.0,
        )
        assert cap_high.success_rate == 1.0

        # Out of bounds
        with pytest.raises(ValidationError):
            Capability(
                uuid=uuid4(),
                name="OOBRate",
                executor_type="service",
                success_rate=1.5,
            )

        with pytest.raises(ValidationError):
            Capability(
                uuid=uuid4(),
                name="NegRate",
                executor_type="service",
                success_rate=-0.1,
            )

    def test_non_negative_constraints(self):
        """Duration, cost, and invocation count must be non-negative."""
        # Valid values
        cap = Capability(
            uuid=uuid4(),
            name="ValidCapability",
            executor_type="llm",
            estimated_duration_ms=0,
            estimated_cost=0.0,
            invocation_count=0,
        )
        assert cap.estimated_duration_ms == 0

        # Negative values should fail
        with pytest.raises(ValidationError):
            Capability(
                uuid=uuid4(),
                name="NegDuration",
                executor_type="llm",
                estimated_duration_ms=-1,
            )

        with pytest.raises(ValidationError):
            Capability(
                uuid=uuid4(),
                name="NegCost",
                executor_type="llm",
                estimated_cost=-0.1,
            )

    def test_human_executor_properties(self):
        """Human executor should have instruction template."""
        cap = Capability(
            uuid=uuid4(),
            name="HumanTask",
            executor_type="human",
            instruction_template="Please {{action}} the {{object}}.",
        )
        assert cap.instruction_template == "Please {{action}} the {{object}}."
        assert cap.action_name is None
        assert cap.service_endpoint is None

    def test_talos_executor_properties(self):
        """Talos executor should have action name."""
        cap = Capability(
            uuid=uuid4(),
            name="TalosAction",
            executor_type="talos",
            action_name="/talos/grasp",
        )
        assert cap.action_name == "/talos/grasp"
        assert cap.instruction_template is None

    def test_service_executor_properties(self):
        """Service executor should have endpoint."""
        cap = Capability(
            uuid=uuid4(),
            name="ServiceCall",
            executor_type="service",
            service_endpoint="https://api.example.com/action",
        )
        assert cap.service_endpoint == "https://api.example.com/action"

    def test_llm_executor_properties(self):
        """LLM executor should have prompt template."""
        cap = Capability(
            uuid=uuid4(),
            name="LLMTask",
            executor_type="llm",
            prompt_template="Analyze the following: {{input}}",
        )
        assert cap.prompt_template == "Analyze the following: {{input}}"


class TestCapabilityQueries:
    """Tests for capability-related Cypher queries."""

    def test_find_capability_by_uuid_returns_string(self):
        """Query should return a valid Cypher string."""
        query = HCGQueries.find_capability_by_uuid()
        assert isinstance(query, str)
        assert "MATCH" in query
        assert "$uuid" in query
        assert "Capability" in query

    def test_find_capability_by_name_returns_string(self):
        """Query should return a valid Cypher string."""
        query = HCGQueries.find_capability_by_name()
        assert isinstance(query, str)
        assert "$name" in query

    def test_find_capabilities_by_executor_type(self):
        """Query should filter by executor type and exclude deprecated."""
        query = HCGQueries.find_capabilities_by_executor_type()
        assert "$executor_type" in query
        assert "deprecated" in query.lower()

    def test_find_capabilities_by_tag(self):
        """Query should search by tag."""
        query = HCGQueries.find_capabilities_by_tag()
        assert "$tag" in query
        assert "capability_tags" in query

    def test_find_capabilities_by_tags_all(self):
        """Query should require all tags to match."""
        query = HCGQueries.find_capabilities_by_tags()
        assert "$tags" in query
        assert "all(" in query.lower()

    def test_find_capabilities_by_any_tag(self):
        """Query should match any tag."""
        query = HCGQueries.find_capabilities_by_any_tag()
        assert "$tags" in query
        assert "any(" in query.lower()

    def test_find_capabilities_implementing_concept(self):
        """Query should traverse IMPLEMENTS relationship."""
        query = HCGQueries.find_capabilities_implementing_concept()
        assert "IMPLEMENTS" in query
        assert "Concept" in query
        assert "$concept_uuid" in query

    def test_find_capabilities_for_entity(self):
        """Query should traverse EXECUTED_BY relationship."""
        query = HCGQueries.find_capabilities_for_entity()
        assert "EXECUTED_BY" in query
        assert "Entity" in query
        assert "$entity_uuid" in query

    def test_find_capabilities_with_inputs(self):
        """Query should return capability with input concepts."""
        query = HCGQueries.find_capabilities_with_inputs()
        assert "REQUIRES_INPUT" in query
        assert "required_inputs" in query

    def test_find_capabilities_with_outputs(self):
        """Query should return capability with output concepts."""
        query = HCGQueries.find_capabilities_with_outputs()
        assert "PRODUCES_OUTPUT" in query
        assert "produced_outputs" in query

    def test_find_all_capabilities_pagination(self):
        """Query should support pagination."""
        query = HCGQueries.find_all_capabilities()
        assert "$skip" in query
        assert "$limit" in query
        assert "$include_deprecated" in query

    def test_search_capabilities(self):
        """Query should search name and description."""
        query = HCGQueries.search_capabilities()
        assert "$query" in query
        assert "toLower" in query
        assert "name" in query
        assert "description" in query

    def test_get_capability_with_full_context(self):
        """Query should return all relationships."""
        query = HCGQueries.get_capability_with_full_context()
        assert "IMPLEMENTS" in query
        assert "REQUIRES_INPUT" in query
        assert "PRODUCES_OUTPUT" in query
        assert "EXECUTED_BY" in query
        assert "implements" in query
        assert "required_inputs" in query
        assert "produced_outputs" in query
        assert "executors" in query

    def test_create_capability(self):
        """Create query should set all properties."""
        query = HCGQueries.create_capability()
        assert "CREATE" in query
        assert "Capability" in query
        assert "uuid" in query
        assert "name" in query
        assert "executor_type" in query
        assert "created_at" in query
        assert "datetime()" in query

    def test_update_capability(self):
        """Update query should use COALESCE for optional updates."""
        query = HCGQueries.update_capability()
        assert "MATCH" in query
        assert "SET" in query
        assert "COALESCE" in query
        assert "updated_at" in query

    def test_deprecate_capability(self):
        """Deprecate query should set deprecated flag."""
        query = HCGQueries.deprecate_capability()
        assert "deprecated = true" in query

    def test_record_capability_invocation(self):
        """Invocation recording should update statistics."""
        query = HCGQueries.record_capability_invocation()
        assert "invocation_count" in query
        assert "success_rate" in query
        assert "$success" in query

    def test_link_capability_to_concept(self):
        """Link query should create IMPLEMENTS relationship."""
        query = HCGQueries.link_capability_to_concept()
        assert "MERGE" in query
        assert "IMPLEMENTS" in query
        assert "$capability_uuid" in query
        assert "$concept_uuid" in query

    def test_link_capability_input(self):
        """Link query should create REQUIRES_INPUT relationship."""
        query = HCGQueries.link_capability_input()
        assert "REQUIRES_INPUT" in query

    def test_link_capability_output(self):
        """Link query should create PRODUCES_OUTPUT relationship."""
        query = HCGQueries.link_capability_output()
        assert "PRODUCES_OUTPUT" in query

    def test_link_capability_executor(self):
        """Link query should create EXECUTED_BY relationship."""
        query = HCGQueries.link_capability_executor()
        assert "EXECUTED_BY" in query
        assert "$entity_uuid" in query

    def test_link_process_to_capability(self):
        """Link query should create USES_CAPABILITY relationship."""
        query = HCGQueries.link_process_to_capability()
        assert "USES_CAPABILITY" in query
        assert "Process" in query
        assert "$process_uuid" in query
        assert "$capability_uuid" in query

    def test_count_nodes_includes_capabilities(self):
        """Count query should include capabilities."""
        query = HCGQueries.count_nodes_by_type()
        assert "Capability" in query
        assert "capability_count" in query
