"""
FastAPI endpoints for CWM-E reflection and emotion queries.

Provides REST API for triggering reflection jobs and querying emotion states.
"""


from fastapi import APIRouter
from neo4j import Driver
from pydantic import BaseModel

from .reflection import CWMEReflector


class EmotionStateResponse(BaseModel):
    """Response model for emotion states."""
    uuid: str
    timestamp: str
    emotion_type: str
    intensity: float
    context: str | None = None
    source: str


class CreateEmotionStateRequest(BaseModel):
    """Request model for creating emotion states."""
    emotion_type: str
    intensity: float
    context: str | None = None


class TagProcessRequest(BaseModel):
    """Request model for tagging a process."""
    emotion_uuid: str
    process_uuid: str


class TagEntityRequest(BaseModel):
    """Request model for tagging an entity."""
    emotion_uuid: str
    entity_uuid: str


class ReflectionResponse(BaseModel):
    """Response model for reflection job."""
    emotions_generated: int
    emotions: list[EmotionStateResponse]


def create_cwm_e_api(driver: Driver) -> APIRouter:
    """
    Create FastAPI router for CWM-E endpoints.

    Args:
        driver: Neo4j driver instance

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/cwm-e", tags=["cwm-e"])
    reflector = CWMEReflector(driver)

    @router.post("/emotions", response_model=EmotionStateResponse)
    def create_emotion_state(request: CreateEmotionStateRequest):
        """
        Create a new emotion state node.

        Args:
            request: Emotion state creation request

        Returns:
            Created emotion state
        """
        emotion = reflector.create_emotion_state(
            emotion_type=request.emotion_type,
            intensity=request.intensity,
            context=request.context,
        )
        return EmotionStateResponse(**emotion.to_dict())

    @router.post("/emotions/tag-process")
    def tag_process(request: TagProcessRequest):
        """
        Tag a process with an emotion state.

        Args:
            request: Tag process request

        Returns:
            Success message
        """
        reflector.tag_process(request.emotion_uuid, request.process_uuid)
        return {"status": "success", "message": "Process tagged with emotion state"}

    @router.post("/emotions/tag-entity")
    def tag_entity(request: TagEntityRequest):
        """
        Tag an entity with an emotion state.

        Args:
            request: Tag entity request

        Returns:
            Success message
        """
        reflector.tag_entity(request.emotion_uuid, request.entity_uuid)
        return {"status": "success", "message": "Entity tagged with emotion state"}

    @router.post("/reflect", response_model=ReflectionResponse)
    def run_reflection(limit: int = 10):
        """
        Run CWM-E reflection job to analyze persona entries and generate emotions.

        Args:
            limit: Number of recent persona entries to analyze

        Returns:
            Reflection job results
        """
        emotions = reflector.reflect_on_persona_entries(limit=limit)
        return ReflectionResponse(
            emotions_generated=len(emotions),
            emotions=[EmotionStateResponse(**e.to_dict()) for e in emotions],
        )

    @router.get("/emotions/process/{process_uuid}", response_model=list[EmotionStateResponse])
    def get_emotions_for_process(process_uuid: str):
        """
        Get all emotion states tagged on a process.

        Args:
            process_uuid: UUID of the Process node

        Returns:
            List of emotion states
        """
        emotions = reflector.get_emotions_for_process(process_uuid)
        return [EmotionStateResponse(**e.to_dict()) for e in emotions]

    @router.get("/emotions/entity/{entity_uuid}", response_model=list[EmotionStateResponse])
    def get_emotions_for_entity(entity_uuid: str):
        """
        Get all emotion states tagged on an entity.

        Args:
            entity_uuid: UUID of the Entity node

        Returns:
            List of emotion states
        """
        emotions = reflector.get_emotions_for_entity(entity_uuid)
        return [EmotionStateResponse(**e.to_dict()) for e in emotions]

    return router
