"""
CWM-E reflection job for generating emotional/affective state tags.

Analyzes persona entries, process outcomes, and HCG context to infer
emotional states like "confident", "cautious", "curious" and tag them
onto processes and entities.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from neo4j import Driver


@dataclass
class EmotionState:
    """
    Represents an emotional/affective state tag.

    Attributes:
        uuid: Unique identifier for the emotion state
        timestamp: When this state was generated
        emotion_type: Type of emotion (e.g., "confident", "cautious", "curious")
        intensity: Confidence/strength of this emotion (0.0-1.0)
        context: Brief description of what triggered this emotion
        source: What generated this tag (e.g., "cwm-e-reflection")
    """

    uuid: str
    timestamp: str
    emotion_type: str
    intensity: float
    context: str | None = None
    source: str = "cwm-e-reflection"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "uuid": self.uuid,
            "timestamp": self.timestamp,
            "emotion_type": self.emotion_type,
            "intensity": self.intensity,
            "context": self.context,
            "source": self.source,
        }


class CWMEReflector:
    """
    CWM-E reflection engine that generates EmotionState tags.

    Analyzes persona entries and HCG context to infer emotional states
    and tag them onto processes and entities for consumption by planners,
    executors, and Apollo.
    """

    def __init__(self, driver: Driver):
        """
        Initialize the CWM-E reflector with a Neo4j driver.

        Args:
            driver: Neo4j driver instance
        """
        self.driver = driver

    def create_emotion_state(
        self,
        emotion_type: str,
        intensity: float,
        context: str | None = None,
    ) -> EmotionState:
        """
        Create a new emotion state node.

        Args:
            emotion_type: Type of emotion
            intensity: Intensity value (0.0-1.0)
            context: Context description

        Returns:
            Created EmotionState
        """
        emotion_uuid = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        with self.driver.session() as session:
            query = """
            CREATE (es:EmotionState {
                uuid: $uuid,
                timestamp: $timestamp,
                emotion_type: $emotion_type,
                intensity: $intensity,
                context: $context,
                source: $source
            })
            RETURN es
            """

            result = session.run(
                query,
                uuid=emotion_uuid,
                timestamp=timestamp,
                emotion_type=emotion_type,
                intensity=intensity,
                context=context,
                source="cwm-e-reflection",
            )
            result.consume()

        return EmotionState(
            uuid=emotion_uuid,
            timestamp=timestamp,
            emotion_type=emotion_type,
            intensity=intensity,
            context=context,
        )

    def tag_process(self, emotion_uuid: str, process_uuid: str):
        """
        Tag a process with an emotion state.

        Args:
            emotion_uuid: UUID of the EmotionState node
            process_uuid: UUID of the Process node
        """
        with self.driver.session() as session:
            query = """
            MATCH (es:EmotionState {uuid: $emotion_uuid})
            MATCH (p:Process {uuid: $process_uuid})
            MERGE (es)-[:TAGGED_ON]->(p)
            """
            session.run(query, emotion_uuid=emotion_uuid, process_uuid=process_uuid)

    def tag_entity(self, emotion_uuid: str, entity_uuid: str):
        """
        Tag an entity with an emotion state.

        Args:
            emotion_uuid: UUID of the EmotionState node
            entity_uuid: UUID of the Entity node
        """
        with self.driver.session() as session:
            query = """
            MATCH (es:EmotionState {uuid: $emotion_uuid})
            MATCH (e:Entity {uuid: $entity_uuid})
            MERGE (es)-[:TAGGED_ON]->(e)
            """
            session.run(query, emotion_uuid=emotion_uuid, entity_uuid=entity_uuid)

    def reflect_on_persona_entries(self, limit: int = 10) -> list[EmotionState]:
        """
        Analyze recent persona entries and generate emotion states.

        This is a simplified Phase 2 implementation. In production, this would
        use ML models or rule-based inference to analyze sentiment patterns
        and generate appropriate emotional tags.

        Args:
            limit: Number of recent entries to analyze

        Returns:
            List of generated EmotionState objects
        """
        with self.driver.session() as session:
            # Get recent persona entries
            query = """
            MATCH (pe:PersonaEntry)
            RETURN pe
            ORDER BY pe.timestamp DESC
            LIMIT $limit
            """
            result = session.run(query, limit=limit)

            emotion_states = []

            for record in result:
                entry = record["pe"]
                sentiment = entry.get("sentiment")

                if not sentiment:
                    continue

                # Simple rule-based emotion inference
                emotion_type, intensity = self._infer_emotion(sentiment)

                # Create emotion state
                emotion_state = self.create_emotion_state(
                    emotion_type=emotion_type,
                    intensity=intensity,
                    context=f"Inferred from persona entry: {entry.get('summary', '')[:50]}",
                )

                # Link back to the persona entry
                self._link_to_persona_entry(emotion_state.uuid, entry["uuid"])

                # If entry has a related process, tag it
                related_process = entry.get("related_process")
                if related_process:
                    self.tag_process(emotion_state.uuid, related_process)

                emotion_states.append(emotion_state)

            return emotion_states

    def _infer_emotion(self, sentiment: str) -> tuple[str, float]:
        """
        Infer emotion type and intensity from sentiment.

        Simple rule-based implementation for Phase 2.

        Args:
            sentiment: Sentiment string from persona entry

        Returns:
            Tuple of (emotion_type, intensity)
        """
        sentiment_lower = sentiment.lower()

        # Map sentiments to emotions
        if "confident" in sentiment_lower:
            return ("confident", 0.8)
        elif "cautious" in sentiment_lower or "careful" in sentiment_lower:
            return ("cautious", 0.7)
        elif "curious" in sentiment_lower or "interested" in sentiment_lower:
            return ("curious", 0.6)
        elif "neutral" in sentiment_lower:
            return ("neutral", 0.5)
        elif "concerned" in sentiment_lower or "worried" in sentiment_lower:
            return ("concerned", 0.7)
        else:
            # Default to neutral
            return ("neutral", 0.5)

    def _link_to_persona_entry(self, emotion_uuid: str, entry_uuid: str):
        """Create relationship between EmotionState and PersonaEntry."""
        with self.driver.session() as session:
            query = """
            MATCH (es:EmotionState {uuid: $emotion_uuid})
            MATCH (pe:PersonaEntry {uuid: $entry_uuid})
            MERGE (es)-[:GENERATED_BY]->(pe)
            """
            session.run(query, emotion_uuid=emotion_uuid, entry_uuid=entry_uuid)

    def get_emotions_for_process(self, process_uuid: str) -> list[EmotionState]:
        """
        Get all emotion states tagged on a process.

        Args:
            process_uuid: UUID of the Process node

        Returns:
            List of EmotionState objects
        """
        with self.driver.session() as session:
            query = """
            MATCH (es:EmotionState)-[:TAGGED_ON]->(p:Process {uuid: $process_uuid})
            RETURN es
            ORDER BY es.timestamp DESC
            """
            result = session.run(query, process_uuid=process_uuid)

            emotions = []
            for record in result:
                node = record["es"]
                emotions.append(
                    EmotionState(
                        uuid=node["uuid"],
                        timestamp=node["timestamp"],
                        emotion_type=node["emotion_type"],
                        intensity=node["intensity"],
                        context=node.get("context"),
                        source=node.get("source", "cwm-e-reflection"),
                    )
                )

            return emotions

    def get_emotions_for_entity(self, entity_uuid: str) -> list[EmotionState]:
        """
        Get all emotion states tagged on an entity.

        Args:
            entity_uuid: UUID of the Entity node

        Returns:
            List of EmotionState objects
        """
        with self.driver.session() as session:
            query = """
            MATCH (es:EmotionState)-[:TAGGED_ON]->(e:Entity {uuid: $entity_uuid})
            RETURN es
            ORDER BY es.timestamp DESC
            """
            result = session.run(query, entity_uuid=entity_uuid)

            emotions = []
            for record in result:
                node = record["es"]
                emotions.append(
                    EmotionState(
                        uuid=node["uuid"],
                        timestamp=node["timestamp"],
                        emotion_type=node["emotion_type"],
                        intensity=node["intensity"],
                        context=node.get("context"),
                        source=node.get("source", "cwm-e-reflection"),
                    )
                )

            return emotions
