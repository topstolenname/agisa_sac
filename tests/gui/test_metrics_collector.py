"""Unit tests for MetricsCollector.

Tests the metrics collection system that aggregates data from orchestrator hooks.
"""

import queue
import threading
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from agisa_sac.gui.metrics_collector import MetricsCollector


class TestMetricsCollectorInitialization:
    """Test MetricsCollector initialization and basic properties."""

    def test_initialization_with_default_queue(self):
        """Test collector initializes with default queue."""
        collector = MetricsCollector()

        assert collector.metrics_queue is not None
        assert isinstance(collector.metrics_queue, queue.Queue)
        assert collector.metrics_queue.maxsize == 1000
        assert len(collector.history) == 0
        assert collector.latest_snapshot is None
        assert collector.total_epochs_processed == 0
        assert collector.phase_transitions_detected == 0

    def test_initialization_with_custom_queue(self):
        """Test collector accepts custom queue."""
        custom_queue = queue.Queue(maxsize=100)
        collector = MetricsCollector(metrics_queue=custom_queue)

        assert collector.metrics_queue is custom_queue
        assert collector.metrics_queue.maxsize == 100

    def test_initialization_with_custom_max_history(self):
        """Test collector respects max_history parameter."""
        collector = MetricsCollector(max_history=500)

        assert collector.history.maxlen == 500


class TestMetricsCollectorEpochHook:
    """Test on_epoch_end hook callback."""

    def create_mock_orchestrator(self, num_agents=3):
        """Create a mock orchestrator with agents."""
        orchestrator = Mock()

        # Mock agents
        agents = {}
        for i in range(num_agents):
            agent = Mock()
            agent.memory.memories = {
                f"mem_{j}": Mock(theme="test", is_corrupted=Mock(return_value=False))
                for j in range(5)
            }
            agent.temporal_resonance.history = {
                time.time(): {"vector": [1, 2, 3], "theme": "test"}
            }
            agents[f"agent_{i}"] = agent

        orchestrator.agents = agents

        # Mock analyzer
        orchestrator.analyzer.summarize.return_value = {
            "satori_wave_ratio": 0.5,
            "archetype_distribution": {"creative": 2, "systematic": 1},
            "archetype_entropy": 0.918,
            "mean_resonance_strength": 0.75,
            "agent_count": num_agents,
        }

        # Mock TDA tracker
        orchestrator.tda_tracker = Mock()
        orchestrator.tda_tracker.persistence_diagrams_history = [[1, 2, 3]]
        orchestrator.tda_tracker.get_diagram_summary.return_value = {
            "H0_features": 5,
            "H1_features": 2,
        }

        return orchestrator

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_on_epoch_end_collects_metrics(self, mock_monitoring):
        """Test on_epoch_end collects and queues metrics."""
        mock_monitoring.return_value = {
            "sri": 0.3,
            "nds": 5.0,
            "vsd": 0.1,
            "mce": 0.0,
        }

        collector = MetricsCollector()
        orchestrator = self.create_mock_orchestrator(num_agents=3)

        collector.on_epoch_end(orchestrator, epoch=10)

        # Check snapshot was created
        assert collector.latest_snapshot is not None
        assert collector.latest_snapshot["epoch"] == 10
        assert "timestamp" in collector.latest_snapshot
        assert "agent_metrics" in collector.latest_snapshot
        assert "system_metrics" in collector.latest_snapshot
        assert "tda_metrics" in collector.latest_snapshot
        assert collector.latest_snapshot["agent_count"] == 3

        # Check history updated
        assert len(collector.history) == 1
        assert collector.total_epochs_processed == 1

        # Check queue has data
        assert not collector.metrics_queue.empty()
        queued_data = collector.metrics_queue.get_nowait()
        assert queued_data["epoch"] == 10

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_on_epoch_end_handles_missing_tda(self, mock_monitoring):
        """Test hook handles missing TDA tracker gracefully."""
        mock_monitoring.return_value = {"sri": 0.3, "nds": 5.0, "vsd": 0.1, "mce": 0.0}

        collector = MetricsCollector()
        orchestrator = self.create_mock_orchestrator()
        orchestrator.tda_tracker = None

        collector.on_epoch_end(orchestrator, epoch=5)

        # Should still collect metrics
        assert collector.latest_snapshot is not None
        assert collector.latest_snapshot["tda_metrics"] == {}

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_on_epoch_end_handles_queue_overflow(self, mock_monitoring):
        """Test hook handles full queue by dropping oldest."""
        mock_monitoring.return_value = {"sri": 0.3, "nds": 5.0, "vsd": 0.1, "mce": 0.0}

        small_queue = queue.Queue(maxsize=2)
        collector = MetricsCollector(metrics_queue=small_queue)
        orchestrator = self.create_mock_orchestrator()

        # Fill queue beyond capacity
        for epoch in range(5):
            collector.on_epoch_end(orchestrator, epoch=epoch)

        # Queue should not exceed maxsize
        assert collector.metrics_queue.qsize() <= 2

        # All epochs should be in history
        assert len(collector.history) == 5

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_on_epoch_end_thread_safety(self, mock_monitoring):
        """Test concurrent calls to on_epoch_end are thread-safe."""
        mock_monitoring.return_value = {"sri": 0.3, "nds": 5.0, "vsd": 0.1, "mce": 0.0}

        collector = MetricsCollector()
        orchestrator = self.create_mock_orchestrator()

        # Call from multiple threads
        threads = []
        for epoch in range(10):
            thread = threading.Thread(
                target=collector.on_epoch_end, args=(orchestrator, epoch)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # All epochs should be recorded
        assert collector.total_epochs_processed == 10
        assert len(collector.history) == 10


class TestMetricsCollectorTDAHook:
    """Test on_tda_phase_transition hook callback."""

    def test_on_tda_phase_transition_detected(self):
        """Test phase transition detection is tracked."""
        collector = MetricsCollector()
        orchestrator = Mock()

        collector.on_tda_phase_transition(
            orchestrator, epoch=15, transition_detected=True, distance=0.5
        )

        assert collector.phase_transitions_detected == 1

        # Check event was queued
        assert not collector.metrics_queue.empty()
        event = collector.metrics_queue.get_nowait()
        assert event["type"] == "tda_phase_transition"
        assert event["epoch"] == 15
        assert event["distance"] == 0.5

    def test_on_tda_phase_transition_not_detected(self):
        """Test no tracking when transition not detected."""
        collector = MetricsCollector()
        orchestrator = Mock()

        collector.on_tda_phase_transition(
            orchestrator, epoch=15, transition_detected=False, distance=0.1
        )

        assert collector.phase_transitions_detected == 0
        assert collector.metrics_queue.empty()

    def test_on_tda_phase_transition_queue_full(self):
        """Test handles full queue gracefully."""
        small_queue = queue.Queue(maxsize=0)  # No capacity
        collector = MetricsCollector(metrics_queue=small_queue)
        orchestrator = Mock()

        # Should not raise exception
        collector.on_tda_phase_transition(
            orchestrator, epoch=15, transition_detected=True, distance=0.5
        )

        # Transition should still be counted
        assert collector.phase_transitions_detected == 1


class TestMetricsCollectorDataRetrieval:
    """Test data retrieval methods."""

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_get_latest_snapshot(self, mock_monitoring):
        """Test get_latest_snapshot returns most recent data."""
        mock_monitoring.return_value = {"sri": 0.3, "nds": 5.0, "vsd": 0.1, "mce": 0.0}

        collector = MetricsCollector()
        orchestrator = Mock()
        orchestrator.agents = {"agent_0": Mock()}
        orchestrator.analyzer.summarize.return_value = {"satori_wave_ratio": 0.5}
        orchestrator.tda_tracker = None

        # Initially None
        assert collector.get_latest_snapshot() is None

        # Add data
        collector.on_epoch_end(orchestrator, epoch=5)

        snapshot = collector.get_latest_snapshot()
        assert snapshot is not None
        assert snapshot["epoch"] == 5

        # Returns a copy (not the original)
        snapshot["epoch"] = 999
        assert collector.latest_snapshot["epoch"] == 5

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_get_timeseries_agent_metric(self, mock_monitoring):
        """Test get_timeseries extracts per-agent metric."""
        mock_monitoring.side_effect = lambda agent: {
            "sri": 0.1 * (len(agent.memory.memories) % 10),
            "nds": 5.0,
            "vsd": 0.1,
            "mce": 0.0,
        }

        collector = MetricsCollector()
        orchestrator = Mock()
        orchestrator.agents = {"agent_0": Mock()}
        orchestrator.agents["agent_0"].memory.memories = {f"m{i}": Mock() for i in range(5)}
        orchestrator.analyzer.summarize.return_value = {}
        orchestrator.tda_tracker = None

        # Add multiple epochs
        for epoch in range(5):
            collector.on_epoch_end(orchestrator, epoch=epoch)

        timeseries = collector.get_timeseries("sri", agent_id="agent_0")

        assert len(timeseries) == 5
        assert all("epoch" in entry and "value" in entry for entry in timeseries)
        assert timeseries[0]["epoch"] == 0

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_get_timeseries_system_metric(self, mock_monitoring):
        """Test get_timeseries extracts system-wide metric."""
        mock_monitoring.return_value = {"sri": 0.3, "nds": 5.0, "vsd": 0.1, "mce": 0.0}

        collector = MetricsCollector()
        orchestrator = Mock()
        orchestrator.agents = {"agent_0": Mock()}
        orchestrator.analyzer.summarize.return_value = {
            "satori_wave_ratio": 0.5,
            "archetype_entropy": 0.9,
        }
        orchestrator.tda_tracker = None

        # Add multiple epochs
        for epoch in range(3):
            collector.on_epoch_end(orchestrator, epoch=epoch)

        timeseries = collector.get_timeseries("satori_wave_ratio")

        assert len(timeseries) == 3
        assert all(entry["value"] == 0.5 for entry in timeseries)

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_get_timeseries_with_window(self, mock_monitoring):
        """Test get_timeseries respects window parameter."""
        mock_monitoring.return_value = {"sri": 0.3, "nds": 5.0, "vsd": 0.1, "mce": 0.0}

        collector = MetricsCollector()
        orchestrator = Mock()
        orchestrator.agents = {"agent_0": Mock()}
        orchestrator.analyzer.summarize.return_value = {"satori_wave_ratio": 0.5}
        orchestrator.tda_tracker = None

        # Add 10 epochs
        for epoch in range(10):
            collector.on_epoch_end(orchestrator, epoch=epoch)

        # Get last 3 epochs only
        timeseries = collector.get_timeseries("satori_wave_ratio", window=3)

        assert len(timeseries) == 3
        assert timeseries[0]["epoch"] == 7
        assert timeseries[2]["epoch"] == 9

    def test_get_agent_ids(self):
        """Test get_agent_ids returns list of agent IDs."""
        collector = MetricsCollector()

        # Empty initially
        assert collector.get_agent_ids() == []

        # Add snapshot with agents
        collector.latest_snapshot = {
            "agent_metrics": {
                "agent_0": {"sri": 0.1},
                "agent_1": {"sri": 0.2},
                "agent_2": {"sri": 0.3},
            }
        }

        agent_ids = collector.get_agent_ids()
        assert len(agent_ids) == 3
        assert "agent_0" in agent_ids
        assert "agent_1" in agent_ids
        assert "agent_2" in agent_ids


class TestMetricsCollectorStatistics:
    """Test statistics and utility methods."""

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_get_statistics(self, mock_monitoring):
        """Test get_statistics returns correct stats."""
        mock_monitoring.return_value = {"sri": 0.3, "nds": 5.0, "vsd": 0.1, "mce": 0.0}

        collector = MetricsCollector(max_history=500)
        orchestrator = Mock()
        orchestrator.agents = {"agent_0": Mock()}
        orchestrator.analyzer.summarize.return_value = {}
        orchestrator.tda_tracker = None

        # Initial stats
        stats = collector.get_statistics()
        assert stats["total_epochs_processed"] == 0
        assert stats["history_length"] == 0
        assert stats["phase_transitions_detected"] == 0
        assert stats["has_latest_snapshot"] is False

        # Add some data
        for epoch in range(5):
            collector.on_epoch_end(orchestrator, epoch=epoch)

        collector.on_tda_phase_transition(
            orchestrator, epoch=3, transition_detected=True, distance=0.5
        )

        stats = collector.get_statistics()
        assert stats["total_epochs_processed"] == 5
        assert stats["history_length"] == 5
        assert stats["phase_transitions_detected"] == 1
        assert stats["has_latest_snapshot"] is True
        assert stats["queue_size"] >= 5  # At least 5 epoch events

    def test_clear(self):
        """Test clear resets all state."""
        collector = MetricsCollector()

        # Add some data
        collector.history.append({"epoch": 0})
        collector.history.append({"epoch": 1})
        collector.latest_snapshot = {"epoch": 1}
        collector.total_epochs_processed = 2
        collector.phase_transitions_detected = 1
        collector.metrics_queue.put({"test": "data"})

        # Clear
        collector.clear()

        # Verify reset
        assert len(collector.history) == 0
        assert collector.latest_snapshot is None
        assert collector.total_epochs_processed == 0
        assert collector.phase_transitions_detected == 0
        assert collector.metrics_queue.empty()


class TestMetricsCollectorEdgeCases:
    """Test edge cases and error handling."""

    @patch("agisa_sac.gui.metrics_collector.monitoring.generate_monitoring_metrics")
    def test_handles_missing_agent_attributes(self, mock_monitoring):
        """Test gracefully handles agents missing attributes."""
        mock_monitoring.side_effect = AttributeError("No memory attribute")

        collector = MetricsCollector()
        orchestrator = Mock()
        orchestrator.agents = {"agent_0": Mock()}
        orchestrator.analyzer.summarize.return_value = {}
        orchestrator.tda_tracker = None

        # Should not raise exception
        collector.on_epoch_end(orchestrator, epoch=0)

        # Should still create snapshot with fallback values
        assert collector.latest_snapshot is not None
        assert "agent_0" in collector.latest_snapshot["agent_metrics"]

    def test_handles_analyzer_exception(self):
        """Test handles analyzer.summarize() exceptions."""
        collector = MetricsCollector()
        orchestrator = Mock()
        orchestrator.agents = {}
        orchestrator.analyzer.summarize.side_effect = Exception("Analyzer error")
        orchestrator.tda_tracker = None

        # Should not raise exception
        collector.on_epoch_end(orchestrator, epoch=0)

        # Should create snapshot with empty system metrics
        assert collector.latest_snapshot is not None
        assert collector.latest_snapshot["system_metrics"] == {}

    def test_max_history_limit(self):
        """Test history respects maxlen limit."""
        collector = MetricsCollector(max_history=5)
        orchestrator = Mock()
        orchestrator.agents = {}
        orchestrator.analyzer.summarize.return_value = {}
        orchestrator.tda_tracker = None

        # Add 10 epochs
        for epoch in range(10):
            collector.on_epoch_end(orchestrator, epoch=epoch)

        # History should only keep last 5
        assert len(collector.history) == 5
        assert collector.history[0]["epoch"] == 5
        assert collector.history[-1]["epoch"] == 9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
