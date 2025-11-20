"""
Telemetry exporter for storing and forwarding observability data.

Supports local file storage and forwarding to external observability platforms.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any


class TelemetryExporter:
    """
    Exports telemetry data to local storage or external collectors.

    Phase 2 implementation focuses on local file storage.
    Can be extended for Grafana, Prometheus, or other backends.
    """

    def __init__(
        self,
        output_dir: str = "/tmp/logos_telemetry",
        enable_file_export: bool = True,
    ):
        """
        Initialize the telemetry exporter.

        Args:
            output_dir: Directory for storing telemetry files
            enable_file_export: Enable file-based export
        """
        self.output_dir = Path(output_dir)
        self.enable_file_export = enable_file_export
        self.logger = logging.getLogger(__name__)

        if self.enable_file_export:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Telemetry exporter initialized: {self.output_dir}")

    def export_event(self, event: dict[str, Any]):
        """
        Export a single telemetry event.

        Args:
            event: Event data to export
        """
        if not self.enable_file_export:
            return

        event_type = event.get("event_type", "generic")
        timestamp = event.get("timestamp", datetime.utcnow().isoformat())

        # Create dated file for this event type
        date_str = timestamp.split("T")[0]
        filename = f"{event_type}_{date_str}.jsonl"
        filepath = self.output_dir / filename

        try:
            with open(filepath, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to export event: {e}")

    def export_batch(self, events: list[dict[str, Any]]):
        """
        Export a batch of telemetry events.

        Args:
            events: List of events to export
        """
        for event in events:
            self.export_event(event)

    def get_events(
        self,
        event_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve stored telemetry events.

        Args:
            event_type: Filter by event type
            start_date: Filter events after this date (YYYY-MM-DD)
            end_date: Filter events before this date (YYYY-MM-DD)

        Returns:
            List of matching events
        """
        if not self.enable_file_export:
            return []

        events = []

        # Find matching files
        pattern = f"{event_type}_*.jsonl" if event_type else "*.jsonl"
        for filepath in self.output_dir.glob(pattern):
            try:
                with open(filepath) as f:
                    for line in f:
                        event = json.loads(line.strip())

                        # Apply date filters
                        event_date = event.get("timestamp", "").split("T")[0]
                        if start_date and event_date < start_date:
                            continue
                        if end_date and event_date > end_date:
                            continue

                        events.append(event)
            except Exception as e:
                self.logger.error(f"Failed to read events from {filepath}: {e}")

        return events

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of stored telemetry data.

        Returns:
            Summary statistics
        """
        if not self.enable_file_export:
            return {"status": "file export disabled"}

        summary = {
            "output_dir": str(self.output_dir),
            "event_types": {},
            "total_files": 0,
        }

        for filepath in self.output_dir.glob("*.jsonl"):
            summary["total_files"] += 1

            # Extract event type from filename
            event_type = filepath.stem.rsplit("_", 1)[0]

            # Count lines in file
            try:
                with open(filepath) as f:
                    count = sum(1 for _ in f)

                if event_type not in summary["event_types"]:
                    summary["event_types"][event_type] = 0
                summary["event_types"][event_type] += count
            except Exception as e:
                self.logger.error(f"Failed to count events in {filepath}: {e}")

        return summary
