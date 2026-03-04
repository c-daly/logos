"""Redis pub/sub event bus for LOGOS services.

Provides a thin wrapper over redis-py pub/sub for inter-service
event communication. Events use a standard envelope format with
event_type, source, timestamp, and payload.

Channel naming convention: logos:<service>:<event_type>
"""

from __future__ import annotations

import json
import logging
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import redis

from logos_config.settings import RedisConfig

logger = logging.getLogger(__name__)


class EventBus:
    """Redis pub/sub event bus for LOGOS services."""

    def __init__(self, redis_config: RedisConfig) -> None:
        self._redis = redis.from_url(redis_config.url)
        self._pubsub = self._redis.pubsub()
        self._stop_event = threading.Event()

    def publish(self, channel: str, event: dict) -> None:
        """Publish an event to a channel.

        The event dict should contain event_type, source, and payload.
        A timestamp is added automatically.

        Raises ValueError if the event payload is not JSON-serializable.
        """
        envelope = {
            "event_type": event.get("event_type", "unknown"),
            "source": event.get("source", "unknown"),
            "timestamp": datetime.now(UTC).isoformat(),
            "payload": event.get("payload", {}),
        }
        try:
            self._redis.publish(channel, json.dumps(envelope))
        except TypeError as e:
            logger.warning("Failed to serialize event on %s: %s", channel, e)
            raise ValueError(f"Event payload is not JSON-serializable: {e}") from e

    def subscribe(self, channel: str, callback: Callable[[dict], None]) -> None:
        """Subscribe to a channel with a callback.

        The callback receives the parsed event dict (envelope).
        """

        def _handler(message: dict[str, Any]) -> None:
            try:
                data = json.loads(message["data"])
                callback(data)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Failed to parse event on %s: %s", channel, e)

        self._pubsub.subscribe(**{channel: _handler})

    def listen(self) -> None:
        """Blocking listen loop. Run in a background thread.

        Call stop() from another thread to terminate.
        """
        if self._stop_event.is_set():
            return
        while not self._stop_event.is_set():
            try:
                self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            except redis.ConnectionError:
                logger.warning("Redis connection lost during listen, stopping")
                break

    def stop(self) -> None:
        """Signal the listen loop to stop."""
        self._stop_event.set()
        self._pubsub.unsubscribe()

    def close(self) -> None:
        """Close connections. Idempotent."""
        self._stop_event.set()
        try:
            self._pubsub.unsubscribe()
        except Exception:
            pass
        try:
            self._pubsub.close()
        except Exception:
            pass
        try:
            self._redis.close()
        except Exception:
            pass
