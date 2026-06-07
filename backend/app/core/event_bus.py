"""
Redis Streams Event Bus — lightweight pub/sub for execution events.
Falls back to in-memory if Redis is unavailable.
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Awaitable

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


EventCallback = Callable[[str, dict], Awaitable[None]]


class EventBus:
    """Simple event bus: Redis Streams with in-memory fallback."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self._listeners: dict[str, list[EventCallback]] = {}
        self._ready = False

    async def connect(self):
        if not REDIS_AVAILABLE:
            logger.warning("[EventBus] Redis not installed, using in-memory fallback")
            self._ready = True
            return

        try:
            self.redis = redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            self._ready = True
            logger.info("[EventBus] Connected to Redis")
        except Exception as e:
            logger.warning(f"[EventBus] Redis unavailable ({e}), using in-memory fallback")
            self.redis = None
            self._ready = True

    async def publish(self, channel: str, event: dict):
        """Publish an event to a channel."""
        data = json.dumps(event, default=str)

        if self.redis:
            try:
                await self.redis.xadd(channel, {"data": data}, maxlen=10000)
                return
            except Exception:
                pass

        # In-memory fallback
        for listener in self._listeners.get(channel, []):
            try:
                await listener(channel, event)
            except Exception as e:
                logger.error(f"[EventBus] Listener error: {e}")

    def subscribe(self, channel: str, callback: EventCallback):
        """Subscribe to events on a channel."""
        if channel not in self._listeners:
            self._listeners[channel] = []
        self._listeners[channel].append(callback)
        logger.debug(f"[EventBus] Subscribed to '{channel}' ({len(self._listeners[channel])} listeners)")

    def unsubscribe(self, channel: str, callback: EventCallback):
        """Unsubscribe from a channel."""
        if channel in self._listeners:
            self._listeners[channel] = [l for l in self._listeners[channel] if l != callback]


# Singleton
event_bus = EventBus()
