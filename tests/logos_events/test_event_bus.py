"""Tests for logos_events.EventBus."""

from __future__ import annotations

import threading
import time

import pytest
import redis

from logos_config.settings import RedisConfig
from logos_events.event_bus import EventBus

REDIS_AVAILABLE = False
try:
    r = redis.from_url("redis://localhost:6379/0")
    r.ping()
    REDIS_AVAILABLE = True
    r.close()
except Exception:
    pass

pytestmark = pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available")


def _wait_for(condition, timeout=5.0, interval=0.05):
    """Poll until condition() is truthy or timeout expires."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(interval)
    return False


class TestEventBus:
    """Tests for EventBus."""

    def setup_method(self) -> None:
        self.config = RedisConfig()
        self.bus = EventBus(self.config)

    def teardown_method(self) -> None:
        self.bus.close()

    def test_publish_and_subscribe(self) -> None:
        """Published events are received by subscribers."""
        received: list[dict] = []

        def on_event(event: dict) -> None:
            received.append(event)

        self.bus.subscribe("logos:test:ping", on_event)

        # Start listener in background thread
        listener = threading.Thread(target=self.bus.listen, daemon=True)
        listener.start()

        # Wait for listener thread to be running
        _wait_for(lambda: listener.is_alive())

        # Publish from a separate connection
        pub_bus = EventBus(self.config)
        pub_bus.publish(
            "logos:test:ping",
            {
                "event_type": "ping",
                "source": "test",
                "payload": {"value": 42},
            },
        )
        pub_bus.close()

        # Poll for delivery instead of fixed sleep
        assert _wait_for(
            lambda: len(received) >= 1
        ), "Event not received within timeout"
        self.bus.stop()

        assert received[0]["event_type"] == "ping"
        assert received[0]["source"] == "test"
        assert received[0]["payload"] == {"value": 42}
        assert "timestamp" in received[0]

    def test_publish_envelope_format(self) -> None:
        """Published events include standard envelope fields."""
        received: list[dict] = []

        def on_event(event: dict) -> None:
            received.append(event)

        self.bus.subscribe("logos:test:envelope", on_event)
        listener = threading.Thread(target=self.bus.listen, daemon=True)
        listener.start()
        _wait_for(lambda: listener.is_alive())

        pub_bus = EventBus(self.config)
        pub_bus.publish(
            "logos:test:envelope",
            {
                "event_type": "test_event",
                "source": "sophia",
                "payload": {},
            },
        )
        pub_bus.close()

        assert _wait_for(
            lambda: len(received) >= 1
        ), "Event not received within timeout"
        self.bus.stop()

        event = received[0]
        assert "event_type" in event
        assert "source" in event
        assert "timestamp" in event
        assert "payload" in event

    def test_publish_non_serializable_raises(self) -> None:
        """Publishing a non-JSON-serializable payload raises ValueError."""
        with pytest.raises(ValueError, match="not JSON-serializable"):
            self.bus.publish(
                "logos:test:bad",
                {
                    "event_type": "bad",
                    "source": "test",
                    "payload": {"value": {1, 2, 3}},  # set is not serializable
                },
            )

    def test_close_is_idempotent(self) -> None:
        """Closing multiple times does not raise."""
        self.bus.close()
        self.bus.close()  # Should not raise

    def test_stop_before_listen_prevents_blocking(self) -> None:
        """If stop() is called before listen(), listen() returns immediately."""
        self.bus.stop()
        # listen() should return without blocking
        self.bus.listen()
