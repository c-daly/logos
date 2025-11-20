"""
FastAPI endpoints for persona diary queries accessible to any client surface.
"""


from fastapi import APIRouter
from neo4j import Driver
from pydantic import BaseModel

from .diary import PersonaDiary


class PersonaEntryResponse(BaseModel):
    """Response model for persona entries."""
    uuid: str
    timestamp: str
    summary: str
    sentiment: str | None = None
    related_process: str | None = None


class CreatePersonaEntryRequest(BaseModel):
    """Request model for creating persona entries."""
    summary: str
    sentiment: str | None = None
    related_process: str | None = None


class SentimentSummaryResponse(BaseModel):
    """Response model for sentiment summary."""
    sentiments: dict


def create_persona_api(driver: Driver) -> APIRouter:
    """
    Create FastAPI router for persona diary endpoints.

    Args:
        driver: Neo4j driver instance

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/persona", tags=["persona"])
    diary = PersonaDiary(driver)

    @router.post("/entries", response_model=PersonaEntryResponse)
    def create_entry(request: CreatePersonaEntryRequest):
        """
        Create a new persona diary entry.

        Args:
            request: Entry creation request

        Returns:
            Created entry
        """
        entry = diary.create_entry(
            summary=request.summary,
            sentiment=request.sentiment,
            related_process=request.related_process,
        )
        return PersonaEntryResponse(**entry.to_dict())

    @router.get("/entries", response_model=list[PersonaEntryResponse])
    def get_entries(
        limit: int = 10,
        sentiment: str | None = None,
    ):
        """
        Get recent persona entries.

        Args:
            limit: Maximum number of entries to return
            sentiment: Filter by sentiment (optional)

        Returns:
            List of persona entries
        """
        entries = diary.get_recent_entries(limit=limit, sentiment=sentiment)
        return [PersonaEntryResponse(**entry.to_dict()) for entry in entries]

    @router.get("/entries/process/{process_uuid}", response_model=list[PersonaEntryResponse])
    def get_entries_for_process(process_uuid: str):
        """
        Get all persona entries related to a specific process.

        Args:
            process_uuid: UUID of the Process node

        Returns:
            List of persona entries
        """
        entries = diary.get_entries_for_process(process_uuid)
        return [PersonaEntryResponse(**entry.to_dict()) for entry in entries]

    @router.get("/sentiment/summary", response_model=SentimentSummaryResponse)
    def get_sentiment_summary():
        """
        Get sentiment distribution summary.

        Returns:
            Sentiment summary statistics
        """
        summary = diary.get_sentiment_summary()
        return SentimentSummaryResponse(sentiments=summary)

    return router
