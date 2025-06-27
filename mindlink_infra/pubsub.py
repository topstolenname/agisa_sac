import json
from typing import Callable

try:
    import redis
except ImportError:  # pragma: no cover - environment without redis
    redis = None


class RedisPubSub:
    """Minimal Redis-based pub/sub wrapper."""
    def __init__(self, url: str = "redis://localhost:6379/0"):
        if redis is None:
            raise RuntimeError("redis package not available")
        self.redis = redis.Redis.from_url(url)
        self.pubsub = self.redis.pubsub()

    def publish(self, channel: str, message: dict) -> None:
        self.redis.publish(channel, json.dumps(message))

    def subscribe(self, channel: str, callback: Callable[[dict], None]) -> None:
        def _handler(msg):
            if msg['type'] == 'message':
                callback(json.loads(msg['data']))
        self.pubsub.subscribe(**{channel: _handler})
        self.pubsub.run_in_thread(sleep_time=0.001)
