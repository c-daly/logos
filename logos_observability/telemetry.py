"""
OpenTelemetry setup and structured logging for LOGOS components.

Provides tracer and logger instances configured with OpenTelemetry SDK.
Captures plan/state updates, process execution, and diagnostic events.
"""

import json
import logging
from datetime import datetime
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    OTLP_AVAILABLE = True
except ImportError:
    OTLP_AVAILABLE = False

# Global tracer provider
_tracer_provider: TracerProvider | None = None


class StructuredLogger:
    """
    Structured logger that outputs JSON-formatted logs for easy parsing.
    Captures LOGOS-specific events like plan updates, state changes, and HCG operations.
    """

    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Configure JSON formatter if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JsonFormatter())
            self.logger.addHandler(handler)

    def log_plan_update(
        self,
        plan_uuid: str,
        action: str,
        details: dict[str, Any] | None = None,
    ):
        """Log a plan update event."""
        self._log_event(
            event_type="plan_update",
            plan_uuid=plan_uuid,
            action=action,
            details=details or {},
        )

    def log_state_change(
        self,
        entity_uuid: str,
        state_uuid: str,
        old_state: str | None = None,
        new_state: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Log a state change event."""
        self._log_event(
            event_type="state_change",
            entity_uuid=entity_uuid,
            state_uuid=state_uuid,
            old_state=old_state,
            new_state=new_state,
            details=details or {},
        )

    def log_process_execution(
        self,
        process_uuid: str,
        status: str,
        duration_ms: float | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Log a process execution event."""
        self._log_event(
            event_type="process_execution",
            process_uuid=process_uuid,
            status=status,
            duration_ms=duration_ms,
            details=details or {},
        )

    def log_persona_entry(
        self,
        entry_uuid: str,
        summary: str,
        sentiment: str | None = None,
        related_process: str | None = None,
    ):
        """Log a persona diary entry creation."""
        self._log_event(
            event_type="persona_entry",
            entry_uuid=entry_uuid,
            summary=summary,
            sentiment=sentiment,
            related_process=related_process,
        )

    def log_emotion_state(
        self,
        emotion_uuid: str,
        emotion_type: str,
        intensity: float,
        context: str | None = None,
    ):
        """Log an emotion state generation from CWM-E."""
        self._log_event(
            event_type="emotion_state",
            emotion_uuid=emotion_uuid,
            emotion_type=emotion_type,
            intensity=intensity,
            context=context,
        )

    def _log_event(self, event_type: str, **kwargs):
        """Internal method to log structured events."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            **kwargs,
        }
        self.logger.info(json.dumps(event))


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # If the message is already JSON, parse it and merge
        try:
            parsed_message = json.loads(record.getMessage())
            if isinstance(parsed_message, dict):
                log_data.update(parsed_message)
                log_data.pop("message", None)  # Remove redundant message field
        except (json.JSONDecodeError, ValueError):
            pass

        return json.dumps(log_data)


def setup_telemetry(
    service_name: str = "logos-service",
    export_to_console: bool = True,
    otlp_endpoint: str | None = None,
) -> TracerProvider:
    """
    Setup OpenTelemetry tracer provider for the service.

    Args:
        service_name: Name of the service for trace identification
        export_to_console: If True, export spans to console (dev mode)
        otlp_endpoint: Optional OTLP collector endpoint (e.g., "http://localhost:4317")

    Returns:
        Configured TracerProvider instance
    """
    global _tracer_provider

    # Create resource with service name
    resource = Resource.create({"service.name": service_name})

    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)

    # Add span processors
    if export_to_console:
        console_exporter = ConsoleSpanExporter()
        _tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))

    # Add OTLP exporter if endpoint provided and available
    if otlp_endpoint and OTLP_AVAILABLE:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        _tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set as global tracer provider
    trace.set_tracer_provider(_tracer_provider)

    return _tracer_provider


def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer instance for the given name.

    Args:
        name: Name/module for the tracer

    Returns:
        Tracer instance
    """
    return trace.get_tracer(name)


def get_logger(name: str, level: int = logging.INFO) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name
        level: Log level

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, level)
