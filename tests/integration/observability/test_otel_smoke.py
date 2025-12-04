"""
Smoke test for OpenTelemetry instrumentation.

Verifies that OTel exporters don't break service functionality.
Does NOT require collector/Tempo running - uses in-memory spans.
"""

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from logos_observability import get_logger, get_tracer, setup_telemetry


class InMemorySpanExporter:
    """In-memory span exporter for testing."""

    def __init__(self):
        self.spans = []

    def export(self, spans):
        """Collect spans for verification."""
        self.spans.extend(spans)
        return trace.SpanExportResult.SUCCESS

    def shutdown(self):
        """Cleanup."""
        pass


def test_telemetry_setup_with_console():
    """Test basic telemetry setup with console export."""
    provider = setup_telemetry(service_name="test-service", export_to_console=True)
    assert provider is not None
    assert isinstance(provider, TracerProvider)


def test_telemetry_setup_with_otlp_endpoint():
    """Test telemetry setup with OTLP endpoint (won't actually connect)."""
    # This should not fail even if endpoint is unreachable
    provider = setup_telemetry(
        service_name="test-service",
        export_to_console=False,
        otlp_endpoint="http://nonexistent:4317",
    )
    assert provider is not None


def test_tracer_creates_spans():
    """Test that tracer can create spans."""
    setup_telemetry(service_name="test-trace", export_to_console=False)
    tracer = get_tracer("test-module")

    # Create an in-memory exporter to capture spans
    exporter = InMemorySpanExporter()
    provider = trace.get_tracer_provider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    # Create a span
    with tracer.start_as_current_span("test-operation") as span:
        span.set_attribute("test_attr", "test_value")
        span.set_attribute("plan_id", "plan-123")

    # Force flush
    provider.force_flush()

    # Verify span was created
    assert len(exporter.spans) > 0
    span_data = exporter.spans[0]
    assert span_data.name == "test-operation"
    assert span_data.attributes["test_attr"] == "test_value"
    assert span_data.attributes["plan_id"] == "plan-123"


def test_structured_logger_with_otel():
    """Test structured logger works with OTel enabled."""
    setup_telemetry(service_name="test-logger", export_to_console=False)
    logger = get_logger("test-logger")

    # These should not raise exceptions
    logger.log_plan_update(plan_uuid="test-plan-456", action="created", details={"test": "data"})

    logger.log_state_change(
        entity_uuid="test-entity-789",
        state_uuid="test-state-101",
        old_state="idle",
        new_state="active",
    )


def test_nested_spans():
    """Test nested span creation."""
    setup_telemetry(service_name="test-nested", export_to_console=False)
    tracer = get_tracer("test-nested")

    exporter = InMemorySpanExporter()
    provider = trace.get_tracer_provider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    # Create nested spans
    with tracer.start_as_current_span("parent-operation") as parent:
        parent.set_attribute("level", "parent")

        with tracer.start_as_current_span("child-operation") as child:
            child.set_attribute("level", "child")
            child.set_attribute("plan_id", "plan-nested")

    provider.force_flush()

    # Verify we have multiple spans
    assert len(exporter.spans) >= 2

    # Find parent and child
    parent_span = next(s for s in exporter.spans if s.name == "parent-operation")
    child_span = next(s for s in exporter.spans if s.name == "child-operation")

    assert parent_span.attributes["level"] == "parent"
    assert child_span.attributes["level"] == "child"
    assert child_span.attributes["plan_id"] == "plan-nested"


def test_span_error_handling():
    """Test span status on exceptions."""
    setup_telemetry(service_name="test-errors", export_to_console=False)
    tracer = get_tracer("test-errors")

    exporter = InMemorySpanExporter()
    provider = trace.get_tracer_provider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    # Create a span that encounters an error
    with pytest.raises(ValueError):
        with tracer.start_as_current_span("error-operation") as span:
            span.set_attribute("will_fail", True)
            raise ValueError("Test error")

    provider.force_flush()

    # Verify span was created and marked as error
    assert len(exporter.spans) > 0
    error_span = exporter.spans[0]
    assert error_span.name == "error-operation"
    assert error_span.status.status_code == trace.StatusCode.ERROR


def test_multiple_services():
    """Test multiple service instances with different names."""
    services = ["sophia", "hermes", "apollo"]

    for service in services:
        provider = setup_telemetry(service_name=service, export_to_console=False)
        assert provider is not None

        tracer = get_tracer(service)
        with tracer.start_as_current_span(f"{service}-operation") as span:
            span.set_attribute("service", service)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
