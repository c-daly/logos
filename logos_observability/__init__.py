"""
LOGOS Observability Module

Provides OpenTelemetry instrumentation, structured logging, and telemetry export
for Sophia, Hermes, Apollo, and other LOGOS components.

See docs/phase2/PHASE2_SPEC.md for Phase 2 observability requirements.
"""

from .exporter import TelemetryExporter
from .telemetry import get_logger, get_tracer, setup_telemetry

__all__ = [
    "setup_telemetry",
    "get_tracer",
    "get_logger",
    "TelemetryExporter",
]
