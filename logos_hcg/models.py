"""
Type-safe data models for HCG nodes.

These models represent the four primary node types in the HCG:
- Entity: Concrete instances in the world
- Concept: Abstract categories/types
- State: Temporal snapshots of entity properties
- Process: Actions that cause state changes

Each node type includes embedding metadata for vector integration (Section 4.2):
- embedding_id: Reference to vector in Milvus
- embedding_model: Model used for embedding generation
- last_sync: Timestamp of last vector sync

See Project LOGOS spec: Section 4.1 for ontology structure.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EmbeddingMetadata(BaseModel):
    """
    Embedding metadata for vector integration (Section 4.2).

    Properties:
    - embedding_id: Reference to vector in Milvus (matches node UUID)
    - embedding_model: Model used to generate the embedding
    - last_sync: Timestamp of last synchronization with Milvus
    """

    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        }
    )


class Entity(BaseModel):
    """
    Represents a concrete instance in the HCG.

    Properties:
    - uuid: Unique identifier (required, RFC 4122 UUID)
    - name: Human-readable name
    - description: Optional description
    - created_at: Timestamp of creation
    - Additional properties for spatial/physical entities (width, height, depth, etc.)
    - Embedding metadata (Section 4.2): embedding_id, embedding_model, last_sync
    """

    uuid: UUID
    name: str | None = None
    description: str | None = None
    created_at: datetime | None = None

    # Spatial properties (optional)
    width: float | None = Field(None, ge=0)
    height: float | None = Field(None, ge=0)
    depth: float | None = Field(None, ge=0)
    radius: float | None = Field(None, ge=0)
    mass: float | None = Field(None, ge=0)

    # Gripper properties (optional)
    max_grasp_width: float | None = Field(None, ge=0)
    max_force: float | None = Field(None, ge=0)

    # Joint properties (optional)
    joint_type: str | None = None  # enum: revolute|prismatic|fixed|continuous
    min_angle: float | None = None
    max_angle: float | None = None

    # Vector embedding metadata (Section 4.2)
    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    # Store any additional properties from Neo4j
    extra_properties: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_neo4j_datetime(cls, v):
        """Convert Neo4j DateTime to Python datetime."""
        if v is None:
            return None
        # Neo4j DateTime objects can be converted to Python datetime
        if hasattr(v, "to_native"):
            return v.to_native()
        return v


class Concept(BaseModel):
    """
    Represents an abstract category/type in the HCG.

    Properties:
    - uuid: Unique identifier (required, RFC 4122 UUID)
    - name: Concept name (required, unique)
    - description: Optional description
    - Embedding metadata (Section 4.2): embedding_id, embedding_model, last_sync
    """

    uuid: UUID
    name: str
    description: str | None = None

    # Vector embedding metadata (Section 4.2)
    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    # Store any additional properties from Neo4j
    extra_properties: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )


class State(BaseModel):
    """
    Represents a temporal snapshot of entity properties.

    Properties:
    - uuid: Unique identifier (required, RFC 4122 UUID)
    - timestamp: Time of state snapshot (optional, for instantiated states)
    - name: Optional state name
    - Position: position_x, position_y, position_z
    - Orientation: orientation_roll, orientation_pitch, orientation_yaw
    - Boolean flags: is_grasped, is_closed, is_empty
    - Physical: grasp_width, applied_force
    - Embedding metadata (Section 4.2): embedding_id, embedding_model, last_sync
    
    Note: timestamp is optional to support abstract/template states
    that define what CAN be true, vs instantiated states that ARE true.
    """

    uuid: UUID
    timestamp: datetime | None = None
    name: str | None = None

    # Position properties
    position_x: float | None = None
    position_y: float | None = None
    position_z: float | None = None

    # Orientation properties
    orientation_roll: float | None = None
    orientation_pitch: float | None = None
    orientation_yaw: float | None = None

    # Boolean state flags
    is_grasped: bool | None = None
    is_closed: bool | None = None
    is_empty: bool | None = None

    # Physical properties
    grasp_width: float | None = Field(None, ge=0)
    applied_force: float | None = Field(None, ge=0)

    # Vector embedding metadata (Section 4.2)
    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    # Store any additional properties from Neo4j
    extra_properties: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_neo4j_datetime(cls, v):
        """Convert Neo4j DateTime to Python datetime."""
        if v is None:
            return None
        # Neo4j DateTime objects can be converted to Python datetime
        if hasattr(v, "to_native"):
            return v.to_native()
        return v


class Process(BaseModel):
    """
    Represents an action that causes state changes.

    Properties:
    - uuid: Unique identifier (required, RFC 4122 UUID)
    - start_time: Process start timestamp (optional, for instantiated processes)
    - name: Optional process name
    - description: Optional description
    - duration_ms: Duration in milliseconds
    - Embedding metadata (Section 4.2): embedding_id, embedding_model, last_sync
    
    Note: start_time is optional to support abstract/template processes
    that define what CAN happen, vs instantiated processes that DID happen.
    """

    uuid: UUID
    start_time: datetime | None = None
    name: str | None = None
    description: str | None = None
    duration_ms: int | None = Field(None, ge=0)

    # Vector embedding metadata (Section 4.2)
    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    # Store any additional properties from Neo4j
    extra_properties: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    @field_validator("start_time", mode="before")
    @classmethod
    def parse_neo4j_datetime(cls, v):
        """Convert Neo4j DateTime to Python datetime."""
        if v is None:
            return None
        # Neo4j DateTime objects can be converted to Python datetime
        if hasattr(v, "to_native"):
            return v.to_native()
        return v


class ExecutorType:
    """Executor type constants for capabilities."""

    HUMAN = "human"
    TALOS = "talos"
    SERVICE = "service"
    LLM = "llm"

    ALL = [HUMAN, TALOS, SERVICE, LLM]


class Capability(BaseModel):
    """
    Represents a tool/process in the HCG capability catalog (logos#284).

    Capabilities are registered tools that Sophia can use during planning.
    Each capability defines what it does, how it's executed, and its
    performance characteristics.

    Properties:
    - uuid: Unique identifier (required, string with 'capability-' prefix)
    - name: Capability name (required, unique)
    - executor_type: How the capability is executed (required)
      - 'human': Instructions for human operators
      - 'talos': Robotic actions via Talos
      - 'service': External API/service calls
      - 'llm': Language model reasoning
    - description: What the capability does
    - capability_tags: Tags for discovery (e.g., ['manipulation', 'pick'])

    Performance:
    - estimated_duration_ms: Typical execution time
    - estimated_cost: Relative cost for planning optimization
    - success_rate: Historical success rate (0.0-1.0)
    - invocation_count: Usage statistics

    Integration (executor-specific):
    - service_endpoint: URL for service-type
    - action_name: ROS action for talos-type
    - instruction_template: Template for human-type
    - prompt_template: Template for llm-type

    Versioning:
    - version: Semantic version
    - deprecated: Whether capability is deprecated
    - created_at, updated_at: Timestamps
    """

    uuid: UUID
    name: str
    executor_type: str
    description: str | None = None
    capability_tags: list[str] = Field(default_factory=list)

    # Performance metrics
    estimated_duration_ms: int | None = Field(None, ge=0)
    estimated_cost: float | None = Field(None, ge=0)
    success_rate: float | None = Field(None, ge=0, le=1)
    invocation_count: int | None = Field(None, ge=0)

    # Integration properties (executor-specific)
    service_endpoint: str | None = None
    action_name: str | None = None
    instruction_template: str | None = None
    prompt_template: str | None = None

    # Versioning
    version: str | None = None
    deprecated: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Vector embedding metadata (Section 4.2)
    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    # Store any additional properties from Neo4j
    extra_properties: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    @field_validator("executor_type")
    @classmethod
    def validate_executor_type(cls, v: str) -> str:
        """Validate executor_type is one of the allowed values."""
        if v not in ExecutorType.ALL:
            raise ValueError(f"executor_type must be one of {ExecutorType.ALL}, got '{v}'")
        return v

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_neo4j_datetime(cls, v):
        """Convert Neo4j DateTime to Python datetime."""
        if v is None:
            return None
        if hasattr(v, "to_native"):
            return v.to_native()
        return v


# ============================================================================
# CWM-A: Abstract/Associative World Model Nodes (logos#288)
# ============================================================================


class FactStatus:
    """Fact lifecycle status constants."""

    HYPOTHESIS = "hypothesis"
    PROPOSED = "proposed"
    CANONICAL = "canonical"
    DEPRECATED = "deprecated"

    ALL = [HYPOTHESIS, PROPOSED, CANONICAL, DEPRECATED]


class SourceType:
    """Fact source type constants."""

    KNOWLEDGE_BASE = "knowledge_base"
    OBSERVATION = "observation"
    INFERENCE = "inference"
    HUMAN = "human"

    ALL = [KNOWLEDGE_BASE, OBSERVATION, INFERENCE, HUMAN]


class RuleType:
    """Rule type constants."""

    CONSTRAINT = "constraint"
    PREFERENCE = "preference"
    INFERENCE = "inference"
    DEFAULT = "default"

    ALL = [CONSTRAINT, PREFERENCE, INFERENCE, DEFAULT]


class Fact(BaseModel):
    """
    Represents a declarative statement in CWM-A.

    Facts are subject-predicate-object triples with confidence scores
    and lifecycle status. They represent symbolic knowledge for
    commonsense reasoning.

    Properties:
    - uuid: Unique identifier (required, string with 'fact-' prefix)
    - subject: Subject of the statement (required)
    - predicate: Relationship or property (required)
    - object: Object or value (required)
    - confidence: Confidence score 0.0-1.0 (required)
    - status: Lifecycle status (required)
      - 'hypothesis': Unverified, low confidence
      - 'proposed': Validated, pending integration
      - 'canonical': Stable, used in planning
      - 'deprecated': Superseded or invalidated

    Provenance:
    - source: Where the fact came from
    - source_type: Type of source (knowledge_base, observation, inference, human)

    Temporal:
    - valid_from: When the fact becomes valid
    - valid_until: When the fact expires

    Example:
        Fact(
            uuid="fact-mailbox-accepts-letters",
            subject="mailbox",
            predicate="accepts",
            object="stamped_letter",
            confidence=0.95,
            status="canonical"
        )
    """

    uuid: UUID
    subject: str
    predicate: str
    object: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    status: str

    # Provenance
    source: str | None = None
    source_type: str | None = None

    # Temporal validity
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    # Domain and timestamps
    domain: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Vector embedding metadata (Section 4.2)
    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    # Store any additional properties from Neo4j
    extra_properties: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of the allowed values."""
        if v not in FactStatus.ALL:
            raise ValueError(f"status must be one of {FactStatus.ALL}, got '{v}'")
        return v

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, v: str | None) -> str | None:
        """Validate source_type if provided."""
        if v is not None and v not in SourceType.ALL:
            raise ValueError(f"source_type must be one of {SourceType.ALL}, got '{v}'")
        return v

    @field_validator("created_at", "updated_at", "valid_from", "valid_until", mode="before")
    @classmethod
    def parse_neo4j_datetime(cls, v):
        """Convert Neo4j DateTime to Python datetime."""
        if v is None:
            return None
        if hasattr(v, "to_native"):
            return v.to_native()
        return v


class Association(BaseModel):
    """
    Represents a weighted link between concepts in CWM-A.

    Associations capture learned correlations and semantic relationships
    between concepts, with strength indicating how strongly the concepts
    are related.

    Properties:
    - uuid: Unique identifier (required, string with 'assoc-' prefix)
    - source_concept: Origin concept name/uuid (required)
    - target_concept: Target concept name/uuid (required)
    - strength: Association strength 0.0-1.0 (required)

    Metadata:
    - relationship_type: Type of association (e.g., 'temporal', 'causal')
    - bidirectional: Whether the relationship is symmetric
    - context: Context where association is valid
    - source: How the association was learned
    - decay_rate: Strength decay per day

    Example:
        Association(
            uuid="assoc-coffee-morning",
            source_concept="coffee",
            target_concept="morning",
            relationship_type="temporal",
            strength=0.85
        )
    """

    uuid: UUID
    source_concept: str
    target_concept: str
    strength: float = Field(..., ge=0.0, le=1.0)

    # Metadata
    relationship_type: str | None = None
    bidirectional: bool = False
    context: str | None = None
    source: str | None = None
    decay_rate: float | None = Field(None, ge=0.0)

    # Timestamps
    created_at: datetime | None = None

    # Vector embedding metadata (Section 4.2)
    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    # Store any additional properties from Neo4j
    extra_properties: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_neo4j_datetime(cls, v):
        """Convert Neo4j DateTime to Python datetime."""
        if v is None:
            return None
        if hasattr(v, "to_native"):
            return v.to_native()
        return v


class Abstraction(BaseModel):
    """
    Represents a higher-order concept in CWM-A.

    Abstractions group related concepts and rules, forming a hierarchy
    for organizing domain knowledge.

    Properties:
    - uuid: Unique identifier (required, string with 'abs-' prefix)
    - name: Unique name (required)

    Metadata:
    - description: Human-readable description
    - level: Hierarchy level (0=concrete, higher=more abstract)
    - domain: Knowledge domain

    Example:
        Abstraction(
            uuid="abs-grasp-preconditions",
            name="GraspPreconditions",
            description="Conditions required for successful grasping",
            level=1,
            domain="manipulation"
        )
    """

    uuid: UUID
    name: str

    # Metadata
    description: str | None = None
    level: int | None = Field(None, ge=0)
    domain: str | None = None

    # Timestamps
    created_at: datetime | None = None

    # Vector embedding metadata (Section 4.2)
    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    # Store any additional properties from Neo4j
    extra_properties: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_neo4j_datetime(cls, v):
        """Convert Neo4j DateTime to Python datetime."""
        if v is None:
            return None
        if hasattr(v, "to_native"):
            return v.to_native()
        return v


class Rule(BaseModel):
    """
    Represents a conditional inference rule in CWM-A.

    Rules encode domain knowledge as condition-consequent pairs,
    used for constraint checking, preference expression, and inference.

    Properties:
    - uuid: Unique identifier (required, string with 'rule-' prefix)
    - name: Rule name (required)
    - condition: When the rule applies (required)
    - consequent: What happens when the rule fires (required)
    - rule_type: Type of rule (required)
      - 'constraint': Must be satisfied
      - 'preference': Should be satisfied if possible
      - 'inference': Derives new facts
      - 'default': Applied unless overridden

    Metadata:
    - priority: For conflict resolution (higher = more important)
    - confidence: Rule reliability score
    - domain: Applicable knowledge domain

    Example:
        Rule(
            uuid="rule-fragile-handling",
            name="FragileObjectHandling",
            condition="object.fragile == true",
            consequent="action.force <= 2.0",
            rule_type="constraint",
            priority=10,
            domain="manipulation"
        )
    """

    uuid: UUID
    name: str
    condition: str
    consequent: str
    rule_type: str

    # Metadata
    priority: int | None = Field(None, ge=0)
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    domain: str | None = None

    # Timestamps
    created_at: datetime | None = None

    # Vector embedding metadata (Section 4.2)
    embedding_id: str | None = None
    embedding_model: str | None = None
    last_sync: datetime | None = None

    # Store any additional properties from Neo4j
    extra_properties: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    @field_validator("rule_type")
    @classmethod
    def validate_rule_type(cls, v: str) -> str:
        """Validate rule_type is one of the allowed values."""
        if v not in RuleType.ALL:
            raise ValueError(f"rule_type must be one of {RuleType.ALL}, got '{v}'")
        return v

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_neo4j_datetime(cls, v):
        """Convert Neo4j DateTime to Python datetime."""
        if v is None:
            return None
        if hasattr(v, "to_native"):
            return v.to_native()
        return v


# ============================================================================
# Planning Models (logos#157 + sophia#15)
# ============================================================================


class SourceService:
    """Source service constants for provenance tracking."""

    SOPHIA = "sophia"
    HERMES = "hermes"
    TALOS = "talos"
    APOLLO = "apollo"
    HUMAN = "human"

    ALL = [SOPHIA, HERMES, TALOS, APOLLO, HUMAN]


class GoalStatus:
    """Goal lifecycle status constants."""

    PENDING = "pending"
    ACTIVE = "active"
    ACHIEVED = "achieved"
    FAILED = "failed"
    CANCELLED = "cancelled"

    ALL = [PENDING, ACTIVE, ACHIEVED, FAILED, CANCELLED]


class PlanStatus:
    """Plan lifecycle status constants."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

    ALL = [PENDING, IN_PROGRESS, COMPLETED, FAILED]


class Provenance(BaseModel):
    """
    Audit trail for any authored artifact (sophia#15).

    Tracks who/what created an artifact and when, supporting
    governance and debugging across services.

    Properties:
    - source_service: Which service created this (sophia, hermes, talos, apollo, human)
    - author_id: UUID of the user or agent that authored this
    - created_at: When the artifact was created
    - trace_id: Distributed tracing ID for request correlation
    - tags: Arbitrary tags for filtering/categorization
    """


    source_service: str
    author_id: UUID | None = None
    created_at: datetime
    trace_id: UUID | None = None
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        }
    )

    @field_validator("source_service")
    @classmethod
    def validate_source_service(cls, v: str) -> str:
        """Validate source_service is one of the allowed values."""
        if v not in SourceService.ALL:
            raise ValueError(f"source_service must be one of {SourceService.ALL}, got '{v}'")
        return v


class GoalTarget(BaseModel):
    """
    Specifies what success looks like for a Goal.

    References HCG nodes to define the desired end state.
    The planner uses this to find processes that achieve
    matching states.

    Properties:
    - entity_uuid: Which entity should be in the target state
    - concept_uuid: Optional type/category of the desired state
    - state_properties: Optional property values to match (query criteria)
    """


    entity_uuid: UUID
    concept_uuid: UUID | None = None
    state_properties: dict[str, Any] | None = None


class Goal(BaseModel):
    """
    A planning goal - desired outcome to achieve.

    Goals are domain-agnostic; they specify what success looks like
    via GoalTarget, and the planner finds processes to achieve it.

    Properties:
    - uuid: Unique identifier for this goal
    - description: Human-readable description
    - target: What success looks like (entity + desired state)
    - status: Lifecycle status (pending, active, achieved, failed, cancelled)
    - priority: Relative priority for multi-goal planning (higher = more important)
    - provenance: Audit trail (who created, when, from where)
    """


    uuid: UUID
    description: str
    target: GoalTarget
    status: str = GoalStatus.PENDING
    priority: float = 1.0
    provenance: Provenance

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        }
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of the allowed values."""
        if v not in GoalStatus.ALL:
            raise ValueError(f"status must be one of {GoalStatus.ALL}, got '{v}'")
        return v


class PlanStep(BaseModel):
    """
    A single step in an execution plan.

    Each step references an HCG Process node and tracks its
    preconditions, effects, and execution binding.

    Properties:
    - uuid: Unique identifier for this step
    - name: Human-readable label (copied from Process.name)
    - index: Order in the plan (0-based)
    - process_uuid: HCG Process node this step executes
    - precondition_uuids: State UUIDs that must be true before execution
    - effect_uuids: State UUIDs caused by this step
    - capability_uuid: Which Capability executes this (executor binding)
    - estimated_duration_ms: Expected execution time
    - confidence: Confidence this step will succeed (0.0-1.0)
    - provenance: Audit trail
    """


    uuid: UUID
    name: str | None = None
    index: int = Field(..., ge=0)
    process_uuid: UUID
    precondition_uuids: list[UUID] = Field(default_factory=list)
    effect_uuids: list[UUID] = Field(default_factory=list)
    capability_uuid: UUID | None = None
    estimated_duration_ms: int | None = Field(None, ge=0)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    provenance: Provenance

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        }
    )


class Plan(BaseModel):
    """
    A complete execution plan to achieve a Goal.

    Plans are ordered sequences of PlanSteps produced by
    backward chaining over HCG REQUIRES/CAUSES edges.

    Properties:
    - uuid: Unique identifier for this plan
    - goal_uuid: The Goal this plan achieves
    - steps: Ordered list of PlanSteps
    - current_state_uuid: Starting state for plan execution
    - expected_final_state_uuid: Predicted state after successful execution
    - status: Lifecycle status (pending, in_progress, completed, failed)
    - confidence: Overall plan confidence (0.0-1.0)
    - provenance: Audit trail
    """


    uuid: UUID
    goal_uuid: UUID
    steps: list[PlanStep]
    current_state_uuid: UUID
    expected_final_state_uuid: UUID | None = None
    status: str = PlanStatus.PENDING
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    provenance: Provenance

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
        }
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status is one of the allowed values."""
        if v not in PlanStatus.ALL:
            raise ValueError(f"status must be one of {PlanStatus.ALL}, got '{v}'")
        return v

