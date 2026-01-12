"""Comprehensive tests for MessageBus."""
import asyncio
import pytest
import warnings
from unittest.mock import Mock, patch
import time

from agisa_sac.utils.message_bus import MessageBus


@pytest.fixture
def message_bus():
    """Create a fresh message bus instance."""
    return MessageBus()


class TestMessageBusInitialization:
    """Test message bus initialization."""

    def test_initialization(self, message_bus):
        """Test that message bus initializes correctly."""
        assert isinstance(message_bus.subscribers, dict)
        assert isinstance(message_bus.message_history, list)
        assert len(message_bus.subscribers) == 0
        assert len(message_bus.message_history) == 0
        assert message_bus._loop is None


class TestSubscription:
    """Test subscription functionality."""

    def test_subscribe_valid_callback(self, message_bus):
        """Test subscribing with a valid callback."""
        callback = Mock(__name__="test_callback")
        message_bus.subscribe("test_topic", callback)

        assert "test_topic" in message_bus.subscribers
        assert callback in message_bus.subscribers["test_topic"]
        assert len(message_bus.subscribers["test_topic"]) == 1

    def test_subscribe_multiple_callbacks(self, message_bus):
        """Test subscribing multiple callbacks to same topic."""
        callback1 = Mock(__name__="callback1")
        callback2 = Mock(__name__="callback2")

        message_bus.subscribe("topic", callback1)
        message_bus.subscribe("topic", callback2)

        assert len(message_bus.subscribers["topic"]) == 2
        assert callback1 in message_bus.subscribers["topic"]
        assert callback2 in message_bus.subscribers["topic"]

    def test_subscribe_different_topics(self, message_bus):
        """Test subscribing to different topics."""
        callback1 = Mock(__name__="callback1")
        callback2 = Mock(__name__="callback2")

        message_bus.subscribe("topic1", callback1)
        message_bus.subscribe("topic2", callback2)

        assert len(message_bus.subscribers) == 2
        assert "topic1" in message_bus.subscribers
        assert "topic2" in message_bus.subscribers

    def test_subscribe_non_callable_raises_error(self, message_bus):
        """Test that subscribing with non-callable raises TypeError."""
        with pytest.raises(TypeError, match="Callback must be a callable"):
            message_bus.subscribe("topic", "not_a_function")


class TestPublishSync:
    """Test synchronous publishing."""

    def test_publish_dict_message(self, message_bus):
        """Test publishing a dict message."""
        callback = Mock(__name__="callback")
        message_bus.subscribe("test_topic", callback)

        test_message = {"data": "test_data"}
        message_bus.publish("test_topic", test_message)

        # Verify callback was called
        assert callback.call_count == 1
        called_message = callback.call_args[0][0]

        # Verify message has timestamp and topic
        assert "timestamp" in called_message
        assert "topic" in called_message
        assert called_message["topic"] == "test_topic"
        assert called_message["data"] == "test_data"

    def test_publish_non_dict_converts_to_dict(self, message_bus):
        """Test that non-dict messages are converted."""
        callback = Mock(__name__="callback")
        message_bus.subscribe("topic", callback)

        with pytest.warns(RuntimeWarning, match="non-dict message"):
            message_bus.publish("topic", "string_data")

        called_message = callback.call_args[0][0]
        assert isinstance(called_message, dict)
        assert "data" in called_message
        assert called_message["data"] == "string_data"

    def test_publish_adds_to_history(self, message_bus):
        """Test that published messages are added to history."""
        message_bus.publish("topic", {"test": "data"})

        assert len(message_bus.message_history) == 1
        assert message_bus.message_history[0]["topic"] == "topic"
        assert message_bus.message_history[0]["test"] == "data"

    def test_publish_history_limit(self, message_bus):
        """Test that history is limited to 10000 messages."""
        # Publish 10001 messages
        for i in range(10001):
            message_bus.publish("topic", {"index": i})

        # History should be capped at 10000
        assert len(message_bus.message_history) == 10000
        # Oldest message (0) should be removed
        assert message_bus.message_history[0]["index"] == 1
        assert message_bus.message_history[-1]["index"] == 10000

    def test_publish_no_subscribers(self, message_bus):
        """Test publishing to topic with no subscribers."""
        # Should not raise error
        message_bus.publish("topic", {"data": "test"})
        assert len(message_bus.message_history) == 1

    def test_publish_callback_error_handling(self, message_bus):
        """Test that callback errors are caught and warned."""
        def failing_callback(message):
            raise ValueError("Callback error")

        failing_callback.__name__ = "failing_callback"
        message_bus.subscribe("topic", failing_callback)

        with pytest.warns(RuntimeWarning, match="Error executing callback"):
            message_bus.publish("topic", {"data": "test"})

        # Message should still be in history
        assert len(message_bus.message_history) == 1

    def test_publish_multiple_callbacks(self, message_bus):
        """Test publishing to multiple subscribers."""
        callback1 = Mock(__name__="callback1")
        callback2 = Mock(__name__="callback2")

        message_bus.subscribe("topic", callback1)
        message_bus.subscribe("topic", callback2)

        message_bus.publish("topic", {"data": "test"})

        # Both callbacks should be called
        assert callback1.call_count == 1
        assert callback2.call_count == 1

    def test_publish_message_copy(self, message_bus):
        """Test that callbacks receive a copy of the message."""
        received_messages = []

        def callback(message):
            received_messages.append(message)
            message["modified"] = True

        callback.__name__ = "callback"
        message_bus.subscribe("topic", callback)

        original_message = {"data": "test"}
        message_bus.publish("topic", original_message)

        # Original message should not be modified
        assert "modified" not in original_message


class TestPublishAsync:
    """Test asynchronous publishing."""

    @pytest.mark.asyncio
    async def test_publish_async_callback(self, message_bus):
        """Test publishing with async callback."""
        received_message = {}

        async def async_callback(message):
            received_message.update(message)

        async_callback.__name__ = "async_callback"
        message_bus.subscribe("topic", async_callback)

        message_bus.publish("topic", {"data": "async_test"})

        # Give async task time to complete
        await asyncio.sleep(0.1)

        assert received_message["data"] == "async_test"
        assert "timestamp" in received_message

    @pytest.mark.asyncio
    async def test_async_callback_error_handling(self, message_bus):
        """Test that async callback errors are caught."""
        async def failing_async_callback(message):
            raise ValueError("Async error")

        failing_async_callback.__name__ = "failing_async"
        message_bus.subscribe("topic", failing_async_callback)

        with pytest.warns(RuntimeWarning):
            message_bus.publish("topic", {"data": "test"})
            await asyncio.sleep(0.1)

    def test_publish_async_no_running_loop(self, message_bus):
        """Test async callback when loop is not running."""
        async def async_callback(message):
            pass

        async_callback.__name__ = "async_callback"
        message_bus.subscribe("topic", async_callback)

        # Get a loop but don't run it
        message_bus._loop = asyncio.new_event_loop()

        with pytest.warns(RuntimeWarning, match="loop not running"):
            message_bus.publish("topic", {"data": "test"})


class TestGetRecentMessages:
    """Test message retrieval."""

    def test_get_recent_messages_all(self, message_bus):
        """Test getting recent messages without filter."""
        for i in range(5):
            message_bus.publish("topic", {"index": i})

        recent = message_bus.get_recent_messages(limit=10)
        assert len(recent) == 5
        assert recent[0]["index"] == 0
        assert recent[-1]["index"] == 4

    def test_get_recent_messages_with_limit(self, message_bus):
        """Test getting recent messages with limit."""
        for i in range(10):
            message_bus.publish("topic", {"index": i})

        recent = message_bus.get_recent_messages(limit=3)
        assert len(recent) == 3
        # Should get last 3 messages
        assert recent[0]["index"] == 7
        assert recent[-1]["index"] == 9

    def test_get_recent_messages_filtered_by_topic(self, message_bus):
        """Test getting recent messages filtered by topic."""
        message_bus.publish("topic1", {"source": "topic1", "index": 0})
        message_bus.publish("topic2", {"source": "topic2", "index": 1})
        message_bus.publish("topic1", {"source": "topic1", "index": 2})
        message_bus.publish("topic2", {"source": "topic2", "index": 3})

        topic1_messages = message_bus.get_recent_messages(topic="topic1", limit=10)
        assert len(topic1_messages) == 2
        assert all(m["source"] == "topic1" for m in topic1_messages)
        # Should be in chronological order
        assert topic1_messages[0]["index"] == 0
        assert topic1_messages[1]["index"] == 2

    def test_get_recent_messages_topic_with_limit(self, message_bus):
        """Test getting recent messages by topic with limit."""
        for i in range(5):
            message_bus.publish("target_topic", {"index": i})
            message_bus.publish("other_topic", {"index": i + 100})

        recent = message_bus.get_recent_messages(topic="target_topic", limit=2)
        assert len(recent) == 2
        # Should get last 2 target_topic messages
        assert recent[0]["index"] == 3
        assert recent[1]["index"] == 4

    def test_get_recent_messages_empty_history(self, message_bus):
        """Test getting messages when history is empty."""
        recent = message_bus.get_recent_messages()
        assert recent == []

    def test_get_recent_messages_nonexistent_topic(self, message_bus):
        """Test getting messages for topic that doesn't exist."""
        message_bus.publish("topic1", {"data": "test"})
        recent = message_bus.get_recent_messages(topic="nonexistent")
        assert recent == []


class TestClearHistory:
    """Test history clearing."""

    def test_clear_history(self, message_bus):
        """Test clearing message history."""
        for i in range(5):
            message_bus.publish("topic", {"index": i})

        assert len(message_bus.message_history) > 0

        message_bus.clear_history()

        assert len(message_bus.message_history) == 0

    def test_clear_history_empty(self, message_bus):
        """Test clearing already empty history."""
        message_bus.clear_history()
        assert len(message_bus.message_history) == 0


class TestClearSubscribers:
    """Test subscriber clearing."""

    def test_clear_all_subscribers(self, message_bus):
        """Test clearing all subscribers."""
        callback1 = Mock(__name__="callback1")
        callback2 = Mock(__name__="callback2")

        message_bus.subscribe("topic1", callback1)
        message_bus.subscribe("topic2", callback2)

        assert len(message_bus.subscribers) == 2

        message_bus.clear_subscribers()

        assert len(message_bus.subscribers) == 0

    def test_clear_specific_topic_subscribers(self, message_bus):
        """Test clearing subscribers for specific topic."""
        callback1 = Mock(__name__="callback1")
        callback2 = Mock(__name__="callback2")

        message_bus.subscribe("topic1", callback1)
        message_bus.subscribe("topic2", callback2)

        message_bus.clear_subscribers(topic="topic1")

        assert "topic1" not in message_bus.subscribers
        assert "topic2" in message_bus.subscribers
        assert len(message_bus.subscribers["topic2"]) == 1

    def test_clear_nonexistent_topic(self, message_bus):
        """Test clearing subscribers for nonexistent topic."""
        callback = Mock(__name__="callback")
        message_bus.subscribe("topic1", callback)

        # Should not raise error
        message_bus.clear_subscribers(topic="nonexistent")

        # Existing topic should remain
        assert "topic1" in message_bus.subscribers


class TestEventLoop:
    """Test event loop management."""

    @pytest.mark.asyncio
    async def test_get_loop_running(self, message_bus):
        """Test getting loop when one is already running."""
        loop = message_bus._get_loop()
        assert isinstance(loop, asyncio.AbstractEventLoop)
        assert loop.is_running()

    def test_get_loop_no_running_loop(self, message_bus):
        """Test getting loop when none is running."""
        with pytest.warns(RuntimeWarning, match="No running asyncio loop"):
            loop = message_bus._get_loop()
            assert isinstance(loop, asyncio.AbstractEventLoop)

    def test_loop_cached(self, message_bus):
        """Test that loop is cached after first retrieval."""
        with pytest.warns(RuntimeWarning):
            loop1 = message_bus._get_loop()
            loop2 = message_bus._get_loop()
            assert loop1 is loop2
