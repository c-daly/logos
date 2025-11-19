"""
Planner API Models

Data models for the planner stub API request/response schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class StateDescription(BaseModel):
    """Represents a state description with key-value properties."""
    
    properties: Dict[str, bool | str] = Field(
        ...,
        description="State properties as key-value pairs",
        examples=[{"gripper": "open", "arm_position": "home", "object_grasped": False}]
    )


class ProcessStep(BaseModel):
    """Represents a single step in an action plan."""
    
    process: str = Field(..., description="Name of the process/action")
    preconditions: List[str] = Field(
        default_factory=list,
        description="List of precondition state properties"
    )
    effects: List[str] = Field(
        default_factory=list,
        description="List of state changes caused by this process"
    )
    uuid: Optional[str] = Field(None, description="UUID for the process node in HCG")


class PlanRequest(BaseModel):
    """Request to generate a plan."""
    
    initial_state: StateDescription = Field(..., description="Current/initial state")
    goal_state: StateDescription = Field(..., description="Desired goal state")
    scenario_name: Optional[str] = Field(
        None,
        description="Optional scenario name for lookup in fixtures"
    )


class PlanResponse(BaseModel):
    """Response containing the generated plan."""
    
    plan: List[ProcessStep] = Field(..., description="Ordered sequence of process steps")
    success: bool = Field(..., description="Whether plan generation succeeded")
    message: Optional[str] = Field(None, description="Status or error message")
    scenario_name: Optional[str] = Field(None, description="Scenario name if applicable")


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
