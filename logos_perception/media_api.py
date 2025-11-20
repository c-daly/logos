"""
FastAPI endpoints for media ingestion service.

Provides REST API for uploading and streaming media frames with authentication.
"""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from neo4j import Driver
from pydantic import BaseModel

from .ingest import MediaIngestService

logger = logging.getLogger(__name__)

# Authentication
security = HTTPBearer()


class UploadResponse(BaseModel):
    """Response model for /upload endpoint."""

    media_id: str
    timestamp: str
    format: str
    size_bytes: int
    status: str = "uploaded"


class StreamStartRequest(BaseModel):
    """Request model for starting a media stream."""

    source: str
    fps: int = 10
    format: str = "image/jpeg"


class StreamStartResponse(BaseModel):
    """Response model for stream start."""

    stream_id: str
    source: str
    status: str = "active"


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    neo4j_connected: bool
    milvus_connected: bool


def verify_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    """
    Verify authentication token.

    Args:
        credentials: HTTP Authorization credentials

    Returns:
        Token string if valid

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    # In production, validate against a token store or JWT
    # For Phase 2, we accept any non-empty token
    if not token or len(token) < 8:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return token


def create_media_api(
    neo4j_driver: Driver,
    storage_path: Path | None = None,
) -> APIRouter:
    """
    Create FastAPI router for media ingestion endpoints.

    Args:
        neo4j_driver: Neo4j driver instance
        storage_path: Optional path for storing media files (defaults to /tmp/logos_media)

    Returns:
        Configured APIRouter
    """
    router = APIRouter(prefix="/media", tags=["media"])
    storage_path = storage_path or Path("/tmp/logos_media")
    storage_path.mkdir(parents=True, exist_ok=True)

    ingest_service = MediaIngestService(neo4j_driver)

    @router.get("/health", response_model=HealthResponse)
    def health_check():
        """
        Health check endpoint.

        Returns:
            Health status with connectivity information
        """
        neo4j_connected = False
        milvus_connected = False

        try:
            # Test Neo4j connection
            with neo4j_driver.session() as session:
                session.run("RETURN 1")
            neo4j_connected = True
        except Exception as e:
            logger.warning(f"Neo4j health check failed: {e}")

        # Milvus connection check
        try:
            from pymilvus import connections

            milvus_connected = connections.has_connection("default")
        except Exception as e:
            logger.warning(f"Milvus health check failed: {e}")

        status = "healthy" if neo4j_connected else "degraded"

        return HealthResponse(
            status=status,
            service="media-ingest",
            neo4j_connected=neo4j_connected,
            milvus_connected=milvus_connected,
        )

    @router.post("/upload", response_model=UploadResponse)
    async def upload_media(
        file: UploadFile = File(...),
        metadata: str = Form("{}"),
        token: str = Depends(verify_token),
    ):
        """
        Upload a media file (image, video frame, audio).

        Args:
            file: Uploaded file
            metadata: JSON string with additional metadata
            token: Authentication token

        Returns:
            Upload confirmation with media ID
        """
        try:
            # Read file data
            file_data = await file.read()
            file_size = len(file_data)

            logger.info(
                f"Receiving media upload: {file.filename}, "
                f"type={file.content_type}, size={file_size}"
            )

            # Parse metadata
            import json

            try:
                metadata_dict = json.loads(metadata) if metadata != "{}" else {}
            except json.JSONDecodeError as err:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON") from err

            # Determine format
            format_type = file.content_type or "application/octet-stream"

            # Ingest frame
            frame = ingest_service.ingest_frame(
                data=file_data,
                format=format_type,
                metadata=metadata_dict,
            )

            # Save to disk storage
            file_path = storage_path / f"{frame.frame_id}.bin"
            with open(file_path, "wb") as f:
                f.write(file_data)

            logger.info(f"Media uploaded successfully: {frame.frame_id}")

            return UploadResponse(
                media_id=frame.frame_id,
                timestamp=frame.timestamp.isoformat(),
                format=format_type,
                size_bytes=file_size,
                status="uploaded",
            )

        except Exception as e:
            logger.error(f"Upload failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Upload failed: {str(e)}"
            ) from e

    @router.post("/stream/start", response_model=StreamStartResponse)
    def start_stream(
        stream_request: StreamStartRequest,
        token: str = Depends(verify_token),
    ):
        """
        Start a media stream (WebRTC or file watcher).

        Args:
            stream_request: Stream configuration
            token: Authentication token

        Returns:
            Stream ID and status
        """
        try:
            # Generate stream ID
            from uuid import uuid4

            stream_id = str(uuid4())

            logger.info(
                f"Starting stream {stream_id}: source={stream_request.source}, fps={stream_request.fps}"
            )

            # In production, initialize WebRTC connection or file watcher here
            # For Phase 2, we just create a placeholder stream record

            # Store stream metadata in Neo4j
            query = """
            CREATE (s:MediaStream {
                uuid: $stream_id,
                source: $source,
                fps: $fps,
                format: $format,
                status: 'active',
                started_at: datetime()
            })
            RETURN s.uuid as stream_id
            """

            with neo4j_driver.session() as session:
                session.run(
                    query,
                    stream_id=stream_id,
                    source=stream_request.source,
                    fps=stream_request.fps,
                    format=stream_request.format,
                )

            return StreamStartResponse(
                stream_id=stream_id,
                source=stream_request.source,
                status="active",
            )

        except Exception as e:
            logger.error(f"Stream start failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Stream start failed: {str(e)}"
            ) from e

    @router.post("/stream/{stream_id}/stop")
    def stop_stream(
        stream_id: str,
        token: str = Depends(verify_token),
    ):
        """
        Stop an active media stream.

        Args:
            stream_id: Stream ID from /stream/start
            token: Authentication token

        Returns:
            Confirmation of stream stop
        """
        try:
            logger.info(f"Stopping stream {stream_id}")

            # Update stream status in Neo4j
            query = """
            MATCH (s:MediaStream {uuid: $stream_id})
            SET s.status = 'stopped', s.stopped_at = datetime()
            RETURN s.uuid as stream_id
            """

            with neo4j_driver.session() as session:
                result = session.run(query, stream_id=stream_id)
                record = result.single()

                if not record:
                    raise HTTPException(
                        status_code=404, detail=f"Stream {stream_id} not found"
                    )

            return {"stream_id": stream_id, "status": "stopped"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Stream stop failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Stream stop failed: {str(e)}"
            ) from e

    @router.get("/frames/{frame_id}")
    def get_frame_metadata(
        frame_id: str,
        token: str = Depends(verify_token),
    ):
        """
        Retrieve metadata for a specific frame.

        Args:
            frame_id: Frame ID
            token: Authentication token

        Returns:
            Frame metadata
        """
        metadata = ingest_service.get_frame_metadata(frame_id)

        if metadata is None:
            raise HTTPException(
                status_code=404, detail=f"Frame {frame_id} not found"
            )

        return metadata

    return router
