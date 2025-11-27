"""Data models for HCG entities."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """Base entity in HCG ontology.

    Represents any node in the Hybrid Causal Graph.
    """

    id: str = Field(..., description="Unique identifier for the entity")
    type: str = Field(..., description="Entity type (e.g., 'goal', 'state', 'action')")
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Entity properties"
    )
    labels: list[str] = Field(
        default_factory=list, description="Neo4j labels for the entity"
    )
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class State(BaseModel):
    """State entity representing agent or world state in HCG.

    States are snapshots of the world or agent at a point in time.
    """

    id: str = Field(..., description="Unique state identifier")
    type: str = Field(default="state", description="Entity type")
    description: str = Field(default="", description="State description")
    variables: dict[str, Any] = Field(
        default_factory=dict, description="State variables"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="State timestamp"
    )
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Additional properties"
    )


class Process(BaseModel):
    """Process entity representing actions or transformations in HCG.

    Processes transform states and create causal relationships.
    """

    id: str = Field(..., description="Unique process identifier")
    type: str = Field(default="process", description="Entity type")
    name: str = Field(..., description="Process name")
    description: str | None = Field(None, description="Process description")
    status: str = Field(
        default="pending", description="Process status (pending, running, completed)"
    )
    inputs: list[str] = Field(default_factory=list, description="Input state IDs")
    outputs: list[str] = Field(default_factory=list, description="Output state IDs")
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Additional properties"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )
    completed_at: datetime | None = Field(None, description="Completion timestamp")


class CausalEdge(BaseModel):
    """Causal edge representing relationships between entities in HCG.

    Edges define causal relationships, dependencies, and transformations.
    """

    id: str = Field(..., description="Unique edge identifier")
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    edge_type: str = Field(
        ..., description="Edge type (e.g., 'causes', 'requires', 'produces')"
    )
    properties: dict[str, Any] = Field(
        default_factory=dict, description="Edge properties"
    )
    weight: float = Field(default=1.0, description="Edge weight or strength")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Creation timestamp"
    )


class PlanHistory(BaseModel):
    """Historical record of a plan in HCG.

    Tracks plan generation, execution, and outcomes.
    """

    id: str = Field(..., description="Unique plan identifier")
    goal_id: str = Field(..., description="Associated goal ID")
    status: str = Field(
        ..., description="Plan status (pending, executing, completed, failed)"
    )
    steps: list[dict[str, Any]] = Field(default_factory=list, description="Plan steps")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Plan creation time"
    )
    started_at: datetime | None = Field(None, description="Execution start time")
    completed_at: datetime | None = Field(None, description="Completion time")
    result: dict[str, Any] | None = Field(None, description="Execution result")


class StateHistory(BaseModel):
    """Historical record of state changes in HCG.

    Tracks state transitions over time for visualization and analysis.
    """

    id: str = Field(..., description="Unique history entry identifier")
    state_id: str = Field(..., description="State identifier")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Change timestamp"
    )
    changes: dict[str, Any] = Field(default_factory=dict, description="State changes")
    previous_values: dict[str, Any] | None = Field(
        None, description="Previous state values"
    )
    trigger: str | None = Field(None, description="What triggered the state change")


class GraphSnapshot(BaseModel):
    """Complete snapshot of HCG graph state.

    Used for visualization and analysis of the entire graph.
    """

    entities: list[Entity] = Field(
        default_factory=list, description="All entities in the graph"
    )
    edges: list[CausalEdge] = Field(
        default_factory=list, description="All causal edges"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Snapshot timestamp"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Snapshot metadata"
    )


class PersonaEntry(BaseModel):
    """Persona diary entry capturing agent's internal reasoning and experiences.

    Used for building a narrative of the agent's decision-making process
    and providing context to LLM-based chat interfaces.
    """

    id: str = Field(..., description="Unique entry identifier")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Entry creation timestamp"
    )
    entry_type: str = Field(
        ...,
        description="Entry type: 'belief', 'decision', 'observation', or 'reflection'",
    )
    content: str = Field(..., description="The main content/narrative of the entry")
    summary: str | None = Field(
        None, description="Brief summary for quick reference"
    )
    sentiment: str | None = Field(
        None, description="Sentiment: 'positive', 'negative', 'neutral', or 'mixed'"
    )
    confidence: float | None = Field(
        None, ge=0.0, le=1.0, description="Confidence level (0.0-1.0)"
    )
    related_process_ids: list[str] = Field(
        default_factory=list, description="IDs of related processes/actions"
    )
    related_goal_ids: list[str] = Field(
        default_factory=list, description="IDs of related goals"
    )
    emotion_tags: list[str] = Field(
        default_factory=list, description="Emotion tags associated with this entry"
    )
    trigger: str | None = Field(
        None, description="What triggered this entry (error, user_request, etc.)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
