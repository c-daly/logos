"""Tests for the logos_observability module."""

import json
from datetime import datetime
from pathlib import Path
from logos_observability import setup_telemetry, get_logger, TelemetryExporter


def test_setup_telemetry():
    """Test telemetry setup."""
    provider = setup_telemetry(service_name="test-service", export_to_console=False)
    assert provider is not None


def test_structured_logger():
    """Test structured logger functionality."""
    logger = get_logger("test-logger")
    
    # Test logging methods don't raise exceptions
    logger.log_plan_update(
        plan_uuid="test-plan-123",
        action="created",
        details={"test": "data"}
    )
    
    logger.log_state_change(
        entity_uuid="test-entity-123",
        state_uuid="test-state-456",
        old_state="idle",
        new_state="active"
    )
    
    logger.log_process_execution(
        process_uuid="test-process-789",
        status="completed",
        duration_ms=100.5
    )
    
    logger.log_persona_entry(
        entry_uuid="test-entry-111",
        summary="Test entry",
        sentiment="neutral"
    )
    
    logger.log_emotion_state(
        emotion_uuid="test-emotion-222",
        emotion_type="confident",
        intensity=0.8
    )


def test_telemetry_exporter(tmp_path):
    """Test telemetry exporter."""
    exporter = TelemetryExporter(output_dir=str(tmp_path), enable_file_export=True)
    
    # Export a test event
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "test_event",
        "data": "test"
    }
    exporter.export_event(event)
    
    # Verify file was created
    files = list(tmp_path.glob("*.jsonl"))
    assert len(files) > 0
    
    # Retrieve events
    events = exporter.get_events(event_type="test_event")
    assert len(events) > 0
    assert events[0]["event_type"] == "test_event"
    
    # Get summary
    summary = exporter.get_summary()
    assert "test_event" in summary["event_types"]
    assert summary["event_types"]["test_event"] == 1


def test_telemetry_exporter_batch(tmp_path):
    """Test batch export."""
    exporter = TelemetryExporter(output_dir=str(tmp_path), enable_file_export=True)
    
    events = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "batch_event",
            "index": i
        }
        for i in range(5)
    ]
    
    exporter.export_batch(events)
    
    # Verify all events were exported
    retrieved = exporter.get_events(event_type="batch_event")
    assert len(retrieved) == 5


def test_telemetry_exporter_disabled():
    """Test that exporter can be disabled."""
    exporter = TelemetryExporter(enable_file_export=False)
    
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "disabled_event",
    }
    
    # Should not raise exception
    exporter.export_event(event)
    
    # Should return empty
    events = exporter.get_events()
    assert len(events) == 0
