"""
Data models for perception pipeline and imagination subsystem.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MediaFrame(BaseModel):
    """Represents a single frame from media input."""

    frame_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: bytes
    format: str = "image/jpeg"
    metadata: dict[str, Any] = Field(default_factory=dict)


class SimulationRequest(BaseModel):
    """Request for running k-step imagination simulation."""

    capability_id: str
    context: dict[str, Any]
    k_steps: int = Field(default=5, ge=1, le=50)
    frame_id: str | None = None


class ImaginedState(BaseModel):
    """Represents a predicted future state from JEPA rollout."""

    uuid: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    step: int
    embedding: list[float] | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ImaginedProcess(BaseModel):
    """Represents a simulated process leading to imagined states."""

    uuid: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    capability_id: str
    imagined: bool = True
    horizon: int
    assumptions: dict[str, Any] = Field(default_factory=dict)
    model_version: str = "jepa-v0.1"


class SimulationResult(BaseModel):
    """Result of a simulation run."""

    process: ImaginedProcess
    states: list[ImaginedState]
    metadata: dict[str, Any] = Field(default_factory=dict)
