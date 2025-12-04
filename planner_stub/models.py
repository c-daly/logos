"""
Planner API Models

Data models for the planner stub API request/response schemas.
"""

from pydantic import BaseModel, Field


class StateDescription(BaseModel):
    """Represents a state description with key-value properties."""

    properties: dict[str, bool | str] = Field(
        ...,
        description="State properties as key-value pairs",
        examples=[{"gripper": "open", "arm_position": "home", "object_grasped": False}],
    )


class ProcessStep(BaseModel):
    """Represents a single step in an action plan."""

    process: str = Field(..., description="Name of the process/action")
    preconditions: list[str] = Field(
        default_factory=list, description="List of precondition state properties"
    )
    effects: list[str] = Field(
        default_factory=list, description="List of state changes caused by this process"
    )
    uuid: str | None = Field(None, description="UUID for the process node in HCG")


class PlanRequest(BaseModel):
    """Request to generate a plan."""

    initial_state: StateDescription = Field(..., description="Current/initial state")
    goal_state: StateDescription = Field(..., description="Desired goal state")
    scenario_name: str | None = Field(
        None, description="Optional scenario name for lookup in fixtures"
    )


class PlanResponse(BaseModel):
    """Response containing the generated plan."""

    plan: list[ProcessStep] = Field(..., description="Ordered sequence of process steps")
    success: bool = Field(..., description="Whether plan generation succeeded")
    message: str | None = Field(None, description="Status or error message")
    scenario_name: str | None = Field(None, description="Scenario name if applicable")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
