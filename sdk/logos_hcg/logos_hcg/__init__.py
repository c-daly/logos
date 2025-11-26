"""logos-hcg: Shared HCG client for the LOGOS ecosystem."""

from logos_hcg.client import HCGClient
from logos_hcg.config import HCGConfig
from logos_hcg.exceptions import (
    HCGConnectionError,
    HCGError,
    HCGNotFoundError,
    HCGQueryError,
    HCGValidationError,
)
from logos_hcg.models import (
    CausalEdge,
    Entity,
    GraphSnapshot,
    PersonaEntry,
    PlanHistory,
    Process,
    State,
    StateHistory,
)

__version__ = "0.1.0"

__all__ = [
    # Client
    "HCGClient",
    "HCGConfig",
    # Models
    "Entity",
    "State",
    "Process",
    "CausalEdge",
    "PlanHistory",
    "StateHistory",
    "GraphSnapshot",
    "PersonaEntry",
    # Exceptions
    "HCGError",
    "HCGConnectionError",
    "HCGValidationError",
    "HCGQueryError",
    "HCGNotFoundError",
]
