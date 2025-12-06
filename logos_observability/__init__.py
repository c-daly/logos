"""
LOGOS Observability Module

Provides OpenTelemetry instrumentation, structured logging, metrics, and telemetry export
for Sophia, Hermes, Apollo, and other LOGOS components.

See docs/architecture/PHASE2_SPEC.md for Phase 2 observability requirements.
"""

from .exporter import TelemetryExporter
from .telemetry import (
    get_logger,
    get_meter,
    get_tracer,
    setup_metrics,
    setup_telemetry,
)

__all__ = [
    "setup_telemetry",
    "setup_metrics",
    "get_tracer",
    "get_meter",
    "get_logger",
    "TelemetryExporter",
]
