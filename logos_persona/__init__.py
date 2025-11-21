"""
LOGOS Persona Diary Module

Provides persona diary entries stored in the HCG for client surfaces (Apollo or others)
to query and use when shaping interaction tone/behavior.

See docs/architecture/PHASE2_SPEC.md for persona requirements.
"""

from .api import create_persona_api
from .diary import PersonaDiary, PersonaEntry

__all__ = [
    "PersonaDiary",
    "PersonaEntry",
    "create_persona_api",
]
