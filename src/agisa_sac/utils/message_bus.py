import asyncio
import time
import warnings
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional


class MessageBus:
    """Simple asynchronous message passing system using a pub/sub pattern."""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[Dict[str, Any]] = []
        self._loop = None  # Store loop for task creation if needed

    def _get_loop(self):
        """Get the current asyncio event loop."""
        if self._loop is None:
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                # If no loop is running, create/get one (use case might be outside async context)
                # This might have implications depending on how it's used.
                # Consider warning or requiring explicit loop management.
                warnings.warn(
                    "No running asyncio loop found. Getting/creating one.",
                    RuntimeWarning,
                )
                self._loop = asyncio.get_event_loop_policy().get_event_loop()
        return self._loop

    def subscribe(self, topic: str, callback: Callable):
        """Register a callback function for a specific topic."""
        if not callable(callback):
            raise TypeError("Callback must be a callable function.")
        self.subscribers[topic].append(callback)
        # print(f"Subscribed {callback.__name__} to topic '{topic}'") # Debug

    def publish(self, topic: str, message: Dict):
        """Publish a message to all subscribers registered for the topic."""
        if not isinstance(message, dict):
            warnings.warn(
                f"Publishing non-dict message to '{topic}'. Converting to dict.",
                RuntimeWarning,
            )
            message = {"data": message}

        message["timestamp"] = time.time()
        message["topic"] = topic
        # Limit history size?
        self.message_history.append(message)
        if len(self.message_history) > 10000:  # Example limit
            self.message_history.pop(0)

        # print(f"Publishing to topic '{topic}': {message}") # Debug
        loop = self._get_loop()
        for callback in self.subscribers[topic]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    # Create task to run async callback
                    if loop.is_running():
                        loop.create_task(
                            self._execute_callback(callback, message.copy())
                        )
                    else:
                        # If loop isn't running, might need different handling or warning
                        warnings.warn(
                            f"Cannot schedule async callback {callback.__name__} for '{topic}' - loop not running.",
                            RuntimeWarning,
                        )
                else:
                    # Execute synchronous callback directly
                    # Consider asyncio.to_thread if callback might block
                    callback(message.copy())
            except Exception as e:
                warnings.warn(
                    f"Error executing callback {callback.__name__} for topic '{topic}': {e}",
                    RuntimeWarning,
                )

    async def _execute_callback(self, callback: Callable, message: Dict):
        """Safely execute an asynchronous callback."""
        try:
            await callback(message)
        except Exception as e:
            warnings.warn(
                f"Exception in async callback {callback.__name__}: {e}",
                RuntimeWarning,
            )

    def get_recent_messages(
        self, topic: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """Retrieve recent messages, optionally filtered by topic."""
        if topic:
            # Iterate backwards for efficiency if history is large
            filtered_messages = [
                m
                for m in reversed(self.message_history)
                if m["topic"] == topic
            ]
            return filtered_messages[:limit][
                ::-1
            ]  # Get limit and reverse back
        else:
            return self.message_history[-limit:]

    def clear_history(self):
        """Clears the message history."""
        self.message_history = []

    def clear_subscribers(self, topic: Optional[str] = None):
        """Clears subscribers, optionally for a specific topic."""
        if topic:
            if topic in self.subscribers:
                del self.subscribers[topic]
        else:
            self.subscribers.clear()
