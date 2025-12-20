"""Logging helpers for LOGOS services."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


class HumanFormatter(logging.Formatter):
    """Format logs for local development."""

    def __init__(self) -> None:
        super().__init__(fmt="[{asctime}] {levelname} {name}: {message}", style="{")


def setup_logging(
    service_name: str,
    level: str | None = None,
    structured: bool | None = None,
) -> logging.Logger:
    """Configure logging for a LOGOS service."""

    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    if structured is None:
        structured = os.getenv("LOG_FORMAT", "json").lower() == "json"

    logger = logging.getLogger(service_name)
    logger.setLevel(log_level)
    logger.propagate = False

    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter() if structured else HumanFormatter())

    logger.handlers.clear()
    logger.addHandler(handler)
    return logger
