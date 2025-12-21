"""Tests for logos_test_utils logging helpers."""

from __future__ import annotations

import json

from logos_test_utils.logging import setup_logging


def test_structured_logging_output(capsys) -> None:
    logger = setup_logging("test-service", level="INFO", structured=True)
    logger.info("hello")
    for handler in logger.handlers:
        handler.flush()
    captured = capsys.readouterr()
    payload = json.loads(captured.err.strip())
    assert payload["message"] == "hello"
    assert payload["logger"] == "test-service"
    assert payload["level"] == "INFO"


def test_human_logging_output(capsys) -> None:
    logger = setup_logging("test-service-human", level="WARNING", structured=False)
    logger.warning("hi")
    for handler in logger.handlers:
        handler.flush()
    captured = capsys.readouterr()
    output = captured.err
    assert "WARNING" in output
    assert "test-service-human" in output
    assert "hi" in output
