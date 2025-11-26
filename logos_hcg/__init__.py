"""
LOGOS HCG Query Utilities

This package provides foundational infrastructure for accessing the Hybrid Causal Graph (HCG)
stored in Neo4j. It includes:
- Connection management with pooling
- Common Cypher queries for graph operations
- Type-safe result models
- Error handling and retry logic
- SHACL validation for graph mutations
- Milvus synchronization utilities (Section 4.2)

See Project LOGOS spec: Section 4.1 (Core Ontology and Data Model)
"""

from logos_hcg.client import HCGClient, HCGConnectionError, HCGQueryError
from logos_hcg.models import Concept, Entity, Process, State
from logos_hcg.queries import HCGQueries
from logos_hcg.shacl_validator import HCGValidationError, SHACLValidator
from logos_hcg.sync import HCGMilvusSync, MilvusSyncError

__all__ = [
    # Client
    "HCGClient",
    # Exceptions
    "HCGConnectionError",
    "HCGQueryError",
    "HCGValidationError",
    "MilvusSyncError",
    # Validation
    "SHACLValidator",
    # Queries
    "HCGQueries",
    # Sync
    "HCGMilvusSync",
    # Models
    "Entity",
    "Concept",
    "State",
    "Process",
]

__version__ = "0.1.0"
