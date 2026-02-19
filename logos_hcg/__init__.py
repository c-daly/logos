"""
LOGOS HCG Query Utilities

This package provides foundational infrastructure for accessing the Hybrid Causal Graph (HCG)
stored in Neo4j. It includes:
- Connection management with pooling
- Common Cypher queries for graph operations
- Type-safe result models
- Error handling and retry logic
- Milvus synchronization utilities (Section 4.2)

See Project LOGOS spec: Section 4.1 (Core Ontology and Data Model)
"""

from logos_hcg.client import HCGClient
from logos_hcg.edge import Edge
from logos_hcg.models import (
    Abstraction,
    Association,
    Capability,
    Concept,
    Entity,
    ExecutorType,
    Fact,
    FactStatus,
    Goal,
    GoalStatus,
    GoalTarget,
    Plan,
    PlanStatus,
    PlanStep,
    Process,
    Provenance,
    Rule,
    RuleType,
    SourceService,
    SourceType,
    State,
)
from logos_hcg.planner import GoalUnachievableError, HCGPlanner, PlanningError
from logos_hcg.queries import HCGQueries
from logos_hcg.seeder import TYPE_PARENTS, HCGSeeder
from logos_hcg.sync import HCGMilvusSync, MilvusSyncError

__all__ = [
    # Core client
    "HCGClient",
    "HCGQueries",
    "HCGMilvusSync",
    "MilvusSyncError",
    # Core node types
    "Entity",
    "Concept",
    "State",
    "Process",
    "Edge",
    # Capability catalog (logos#284)
    "Capability",
    "ExecutorType",
    # CWM-A nodes (logos#288)
    "Fact",
    "FactStatus",
    "SourceType",
    "Association",
    "Abstraction",
    "Rule",
    "RuleType",
    # Planning models (logos#157, sophia#15)
    "Goal",
    "GoalStatus",
    "GoalTarget",
    "Plan",
    "PlanStatus",
    "PlanStep",
    "Provenance",
    "SourceService",
    # Planner (logos#157)
    "HCGPlanner",
    "PlanningError",
    "GoalUnachievableError",
    # Seeder
    "HCGSeeder",
    "TYPE_PARENTS",
]

__version__ = "0.1.0"
