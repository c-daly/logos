"""
Sophia - Non-linguistic Cognitive Core

This package contains the skeleton modules for the Sophia cognitive architecture,
implementing non-linguistic reasoning using the Hybrid Causal Graph (HCG).

Components:
- Orchestrator: Manages overall control flow and subsystem coordination
- CWM-A: Continuous World Model - Abstract state representation
- CWM-G: Continuous World Model - Grounded physical/sensor state
- Planner: Generates action plans using causal reasoning over the HCG
- Executor: Executes plans and monitors outcomes

Reference: Section 3.3 of the LOGOS specification
"""

__version__ = "0.1.0"

from sophia.cwm_a import CWMAbstract
from sophia.cwm_g import CWMGrounded
from sophia.executor import Executor
from sophia.orchestrator import Orchestrator
from sophia.planner import Planner

__all__ = [
    "Orchestrator",
    "CWMAbstract",
    "CWMGrounded",
    "Planner",
    "Executor",
]
