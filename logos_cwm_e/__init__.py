"""
LOGOS CWM-E (Causal World Model - Emotional/Social)

Reflection job that analyzes persona entries and generates EmotionState tags
for processes and entities. Used by planners, executors, and Apollo to adjust
behavior and tone.

See docs/phase2/PHASE2_SPEC.md and docs/spec/LOGOS_SPEC_FLEXIBLE.md for CWM-E design.
"""

from .api import create_cwm_e_api
from .reflection import CWMEReflector, EmotionState

__all__ = [
    "EmotionState",
    "CWMEReflector",
    "create_cwm_e_api",
]
