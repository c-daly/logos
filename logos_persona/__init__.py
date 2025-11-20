"""
LOGOS Persona Diary Module

Provides persona diary entries stored in the HCG for Apollo to query
and influence chat tone/behavior.

See docs/phase2/PHASE2_SPEC.md for Phase 2 persona requirements.
"""

from .api import create_persona_api
from .diary import PersonaDiary, PersonaEntry

__all__ = [
    "PersonaDiary",
    "PersonaEntry",
    "create_persona_api",
]
