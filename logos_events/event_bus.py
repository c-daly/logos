"""Redis pub/sub event bus for LOGOS services.

Provides a thin wrapper over redis-py pub/sub for inter-service
event communication. Events use a standard envelope format with
event_type, source, timestamp, and payload.

Channel naming convention: logos:<service>:<event_type>
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Callable

import redis

from logos_config.settings import RedisConfig

logger = logging.getLogger(__name__)


class EventBus:
    """Redis pub/sub event bus for LOGOS services."""

    def __init__(self, redis_config: RedisConfig) -> None:
        self._redis = redis.from_url(redis_config.url)
        self._pubsub = self._redis.pubsub()
        self._callbacks: dict[str, Callable[[dict], None]] = {}
        self._running = False

    def publish(self, channel: str, event: dict) -> None:
        """Publish an event to a channel.

        The event dict should contain event_type, source, and payload.
        A timestamp is added automatically.
        """
        envelope = {
            "event_type": event.get("event_type", "unknown"),
            "source": event.get("source", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": event.get("payload", {}),
        }
        self._redis.publish(channel, json.dumps(envelope))

    def subscribe(self, channel: str, callback: Callable[[dict], None]) -> None:
        """Subscribe to a channel with a callback.

        The callback receives the parsed event dict (envelope).
        """
        self._callbacks[channel] = callback

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
        self._running = True
        for message in self._pubsub.listen():
            if not self._running:
                break

    def stop(self) -> None:
        """Signal the listen loop to stop."""
        self._running = False
        self._pubsub.unsubscribe()

    def close(self) -> None:
        """Close connections. Idempotent."""
        self.stop()
        try:
            self._pubsub.close()
        except Exception:
            pass
        try:
            self._redis.close()
        except Exception:
            pass
