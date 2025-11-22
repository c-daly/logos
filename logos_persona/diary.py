"""
Persona diary writer and query functionality.

Stores persona entries as HCG nodes (:PersonaEntry) that capture
summaries, sentiments, and related process information.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from neo4j import Driver


@dataclass
class PersonaEntry:
    """
    Represents a persona diary entry.

    Attributes:
        uuid: Unique identifier for the entry
        timestamp: When this entry was created
        summary: Text summary of the activity/interaction
        sentiment: Emotional tone (e.g., "confident", "cautious", "neutral")
        related_process: Optional UUID of related Process node
    """

    uuid: str
    timestamp: str
    summary: str
    sentiment: str | None = None
    related_process: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "summary": self.summary,
            "sentiment": self.sentiment,
            "related_process": self.related_process,
        }


class PersonaDiary:
    """
    Manages persona diary entries in the HCG.

    Writes entries to Neo4j as (:PersonaEntry) nodes and provides
    query methods for client surfaces (Apollo or others) to retrieve relevant context.
    """

    def __init__(self, driver: Driver):
        """
        Initialize the persona diary with a Neo4j driver.

        Args:
            driver: Neo4j driver instance
        """
        self.driver = driver

    def create_entry(
        self,
        summary: str,
        sentiment: str | None = None,
        related_process: str | None = None,
    ) -> PersonaEntry:
        """
        Create a new persona diary entry.

        Args:
            summary: Text summary of the activity
            sentiment: Emotional tone
            related_process: UUID of related Process node

        Returns:
            Created PersonaEntry
        """
        entry_uuid = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        with self.driver.session() as session:
            query = """
            CREATE (pe:PersonaEntry {
                uuid: $uuid,
                timestamp: $timestamp,
                summary: $summary,
                sentiment: $sentiment,
                related_process: $related_process
            })
            RETURN pe
            """

            result = session.run(
                query,
                uuid=entry_uuid,
                timestamp=timestamp,
                summary=summary,
                sentiment=sentiment,
                related_process=related_process,
            )
            result.consume()

        # Create relationship to Process if specified
        if related_process:
            self._link_to_process(entry_uuid, related_process)

        return PersonaEntry(
            uuid=entry_uuid,
            timestamp=timestamp,
            summary=summary,
            sentiment=sentiment,
            related_process=related_process,
        )

    def _link_to_process(self, entry_uuid: str, process_uuid: str):
        """Create relationship between PersonaEntry and Process."""
        with self.driver.session() as session:
            query = """
            MATCH (pe:PersonaEntry {uuid: $entry_uuid})
            MATCH (p:Process {uuid: $process_uuid})
            MERGE (pe)-[:RELATES_TO]->(p)
            """
            session.run(query, entry_uuid=entry_uuid, process_uuid=process_uuid)

    def get_recent_entries(
        self,
        limit: int = 10,
        sentiment: str | None = None,
    ) -> list[PersonaEntry]:
        """
        Get recent persona entries.

        Args:
            limit: Maximum number of entries to return
            sentiment: Filter by sentiment (optional)

        Returns:
            List of PersonaEntry objects
        """
        with self.driver.session() as session:
            if sentiment:
                query = """
                MATCH (pe:PersonaEntry)
                WHERE pe.sentiment = $sentiment
                RETURN pe
                ORDER BY pe.timestamp DESC
                LIMIT $limit
                """
                result = session.run(query, sentiment=sentiment, limit=limit)
            else:
                query = """
                MATCH (pe:PersonaEntry)
                RETURN pe
                ORDER BY pe.timestamp DESC
                LIMIT $limit
                """
                result = session.run(query, limit=limit)

            entries = []
            for record in result:
                node = record["pe"]
                entries.append(
                    PersonaEntry(
                        uuid=node["uuid"],
                        timestamp=node["timestamp"],
                        summary=node["summary"],
                        sentiment=node.get("sentiment"),
                        related_process=node.get("related_process"),
                    )
                )

            return entries

    def get_entries_for_process(self, process_uuid: str) -> list[PersonaEntry]:
        """
        Get all persona entries related to a specific process.

        Args:
            process_uuid: UUID of the Process node

        Returns:
            List of PersonaEntry objects
        """
        with self.driver.session() as session:
            query = """
            MATCH (pe:PersonaEntry)-[:RELATES_TO]->(p:Process {uuid: $process_uuid})
            RETURN pe
            ORDER BY pe.timestamp DESC
            """
            result = session.run(query, process_uuid=process_uuid)

            entries = []
            for record in result:
                node = record["pe"]
                entries.append(
                    PersonaEntry(
                        uuid=node["uuid"],
                        timestamp=node["timestamp"],
                        summary=node["summary"],
                        sentiment=node.get("sentiment"),
                        related_process=node.get("related_process"),
                    )
                )

            return entries

    def get_sentiment_summary(self) -> dict[str, int]:
        """
        Get a summary of sentiment distribution across entries.

        Returns:
            Dictionary mapping sentiment types to counts
        """
        with self.driver.session() as session:
            query = """
            MATCH (pe:PersonaEntry)
            WHERE pe.sentiment IS NOT NULL
            RETURN pe.sentiment AS sentiment, count(*) AS count
            """
            result = session.run(query)

            summary = {}
            for record in result:
                sentiment = record["sentiment"]
                count = record["count"]
                summary[sentiment] = count

            return summary
