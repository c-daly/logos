"""Reified edge model for the Hybrid Cognitive Graph.

Edges are nodes in Neo4j connected to source and target via :FROM/:TO
structural relationships. This is the ONLY edge representation in the graph.
"""

from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class Edge(BaseModel):
    """Reified edge in the HCG.

    Stored as a node in Neo4j:
        (source)<-[:FROM]-(edge_node)-[:TO]->(target)
    """

    model_config = ConfigDict(frozen=False)

    id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    target: str
    relation: str
    bidirectional: bool = False
    properties: dict[str, Any] = Field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return False
        return self.id == other.id
