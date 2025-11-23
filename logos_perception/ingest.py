"""
Media ingest service for handling uploaded/streamed frames.

Wires frames to the JEPA runner and stores them in Neo4j/Milvus.
"""

import logging
from typing import Any

from neo4j import Driver
from pymilvus import Collection, connections

from .models import MediaFrame

logger = logging.getLogger(__name__)


class MediaIngestService:
    """
    Service for ingesting media frames (video/images/audio).

    Handles:
    - Frame uploads and streaming
    - Storage in Neo4j (metadata) and Milvus (embeddings)
    - Wiring frames to JEPA runner for processing
    """

    def __init__(
        self,
        neo4j_driver: Driver,
        milvus_collection_name: str = "perception_frames",
        milvus_alias: str = "default",
    ):
        """
        Initialize media ingest service.

        Args:
            neo4j_driver: Neo4j driver for metadata storage
            milvus_collection_name: Name of Milvus collection for embeddings
            milvus_alias: Milvus connection alias
        """
        self.neo4j_driver = neo4j_driver
        self.milvus_collection_name = milvus_collection_name
        self.milvus_alias = milvus_alias
        logger.info(
            f"Initialized MediaIngestService with collection {milvus_collection_name}"
        )

    def ingest_frame(
        self,
        data: bytes,
        format: str = "image/jpeg",
        metadata: dict[str, Any] | None = None,
    ) -> MediaFrame:
        """
        Ingest a single media frame.

        Args:
            data: Frame data bytes
            format: Media format (e.g., "image/jpeg", "video/mp4")
            metadata: Optional metadata dictionary

        Returns:
            MediaFrame object with assigned frame_id
        """
        frame = MediaFrame(
            data=data,
            format=format,
            metadata=metadata or {},
        )

        logger.info(f"Ingesting frame {frame.frame_id} with format {format}")

        # Store metadata in Neo4j
        self._store_frame_metadata(frame)

        return frame

    def _store_frame_metadata(self, frame: MediaFrame) -> None:
        """
        Store frame metadata in Neo4j.

        Args:
            frame: MediaFrame to store
        """
        query = """
        CREATE (f:PerceptionFrame {
            uuid: $frame_id,
            timestamp: datetime($timestamp),
            format: $format,
            metadata: $metadata
        })
        RETURN f.uuid as frame_id
        """

        with self.neo4j_driver.session() as session:
            result = session.run(
                query,
                frame_id=frame.frame_id,
                timestamp=frame.timestamp.isoformat(),
                format=frame.format,
                metadata=frame.metadata,
            )
            result.single()
            logger.info(f"Stored frame metadata in Neo4j: {frame.frame_id}")

    def store_frame_embedding(self, frame_id: str, embedding: list[float]) -> str:
        """
        Store frame embedding in Milvus.

        Args:
            frame_id: Frame ID
            embedding: Embedding vector

        Returns:
            Embedding ID in Milvus
        """
        try:
            # Check if connected to Milvus
            if not connections.has_connection(self.milvus_alias):
                logger.warning(
                    f"Not connected to Milvus alias {self.milvus_alias}, skipping embedding storage"
                )
                return frame_id

            collection = Collection(
                name=self.milvus_collection_name, using=self.milvus_alias
            )

            # Insert embedding
            data = [[frame_id], [embedding]]
            collection.insert(data)

            logger.info(
                f"Stored embedding for frame {frame_id} in Milvus collection {self.milvus_collection_name}"
            )

            return frame_id

        except Exception as e:
            logger.error(f"Failed to store embedding in Milvus: {e}")
            # In Talos-free scenarios, this is non-critical
            return frame_id

    def link_frame_to_simulation(
        self, frame_id: str, simulation_process_uuid: str
    ) -> None:
        """
        Link a frame to an imagination simulation process.

        Args:
            frame_id: Frame ID
            simulation_process_uuid: UUID of ImaginedProcess
        """
        query = """
        MATCH (f:PerceptionFrame {uuid: $frame_id})
        MATCH (p:ImaginedProcess {uuid: $process_uuid})
        CREATE (f)-[:TRIGGERED_SIMULATION]->(p)
        """

        with self.neo4j_driver.session() as session:
            session.run(
                query,
                frame_id=frame_id,
                process_uuid=simulation_process_uuid,
            )
            logger.info(
                f"Linked frame {frame_id} to simulation {simulation_process_uuid}"
            )

    def get_frame_metadata(self, frame_id: str) -> dict[str, Any] | None:
        """
        Retrieve frame metadata from Neo4j.

        Args:
            frame_id: Frame ID

        Returns:
            Frame metadata dictionary or None if not found
        """
        query = """
        MATCH (f:PerceptionFrame {uuid: $frame_id})
        RETURN f
        """

        with self.neo4j_driver.session() as session:
            result = session.run(query, frame_id=frame_id)
            record = result.single()

            if record:
                return dict(record["f"])
            return None
