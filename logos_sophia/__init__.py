"""
LOGOS Sophia Service - Cognitive core API.

Provides REST API for:
- Planning (/plan)
- State queries (/state)
- Imagination simulation (/simulate)
"""

from .api import create_sophia_api
from .simulation import SimulationService

__all__ = [
    "create_sophia_api",
    "SimulationService",
]
