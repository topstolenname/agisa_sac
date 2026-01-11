"""Metrics collection system for GUI real-time updates.

This module provides a thread-safe metrics collector that subscribes to
orchestrator hooks and aggregates metrics for GUI display.
"""

import queue
import threading
import time
from collections import deque
from typing import Any

from agisa_sac.metrics import monitoring
from agisa_sac.utils.logger import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Aggregates metrics from orchestrator hooks for GUI display.

    This class subscribes to orchestrator hooks and maintains a rolling history
    of per-epoch metrics. It uses a thread-safe queue to push updates to the GUI
    without blocking the simulation.

    Attributes:
        metrics_queue: Thread-safe queue for passing metrics to GUI
        history: Rolling deque of epoch snapshots (max 1000)
        latest_snapshot: Most recent metrics snapshot
        _lock: Threading lock for thread-safe access
    """

    def __init__(
        self, metrics_queue: queue.Queue | None = None, max_history: int = 1000
    ):
        """Initialize the metrics collector.

        Args:
            metrics_queue: Optional queue for pushing metrics updates.
                          If None, creates a new queue.
            max_history: Maximum number of epochs to keep in history
        """
        self.metrics_queue = metrics_queue or queue.Queue(maxsize=1000)
        self.history = deque(maxlen=max_history)
        self.latest_snapshot: dict[str, Any] | None = None
        self._lock = threading.Lock()

        # Statistics
        self.total_epochs_processed = 0
        self.phase_transitions_detected = 0

    def on_epoch_end(self, orchestrator, epoch: int, **kwargs) -> None:
        """Hook callback triggered after each epoch completes.

        This method is registered as a hook with the orchestrator's
        'post_epoch' event. It collects metrics and pushes them to the queue.

        Args:
            orchestrator: SimulationOrchestrator instance
            epoch: Current epoch number
            **kwargs: Additional hook arguments
        """
        try:
            # Collect per-agent metrics
            agent_metrics = {}
            for agent_id, agent in orchestrator.agents.items():
                try:
                    agent_metrics[agent_id] = monitoring.generate_monitoring_metrics(
                        agent
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to collect metrics for agent {agent_id}: {e}"
                    )
                    agent_metrics[agent_id] = {
                        "sri": 0.0,
                        "nds": 0.0,
                        "vsd": 0.0,
                        "mce": 0.0,
                    }

            # Collect system-wide metrics
            try:
                system_metrics = orchestrator.analyzer.summarize()
            except Exception as e:
                logger.warning(f"Failed to collect system metrics: {e}")
                system_metrics = {}

            # Collect TDA metrics if available
            tda_metrics = {}
            if (
                orchestrator.tda_tracker
                and orchestrator.tda_tracker.persistence_diagrams_history
            ):
                try:
                    tda_metrics = orchestrator.tda_tracker.get_diagram_summary(-1)
                except Exception as e:
                    logger.warning(f"Failed to collect TDA metrics: {e}")

            # Create snapshot
            snapshot = {
                "epoch": epoch,
                "timestamp": time.time(),
                "agent_metrics": agent_metrics,
                "system_metrics": system_metrics,
                "tda_metrics": tda_metrics,
                "agent_count": len(orchestrator.agents),
            }

            # Update state (thread-safe)
            with self._lock:
                self.latest_snapshot = snapshot
                self.history.append(snapshot)
                self.total_epochs_processed += 1

            # Push to queue (non-blocking)
            try:
                self.metrics_queue.put_nowait(snapshot)
            except queue.Full:
                # Queue full - drop oldest and retry
                try:
                    self.metrics_queue.get_nowait()
                    self.metrics_queue.put_nowait(snapshot)
                except queue.Empty:
                    pass  # Race condition, ignore

        except Exception as e:
            logger.error(f"Error in on_epoch_end hook: {e}", exc_info=True)

    def on_tda_phase_transition(
        self,
        orchestrator,
        epoch: int,
        transition_detected: bool = False,
        distance: float = 0.0,
        **kwargs,
    ) -> None:
        """Hook callback triggered when TDA detects a phase transition.

        Args:
            orchestrator: SimulationOrchestrator instance
            epoch: Current epoch number
            transition_detected: Whether transition was detected
            distance: Distance metric value
            **kwargs: Additional hook arguments
        """
        if transition_detected:
            with self._lock:
                self.phase_transitions_detected += 1

            logger.info(
                f"Phase transition detected at epoch {epoch}, "
                f"distance={distance:.4f}"
            )

            # Push transition event to queue
            event = {
                "type": "tda_phase_transition",
                "epoch": epoch,
                "timestamp": time.time(),
                "distance": distance,
            }

            try:
                self.metrics_queue.put_nowait(event)
            except queue.Full:
                pass  # Non-critical, skip if queue full

    def get_latest_snapshot(self) -> dict[str, Any] | None:
        """Get the most recent metrics snapshot (thread-safe).

        Returns:
            Dictionary containing latest metrics, or None if no data yet
        """
        with self._lock:
            return self.latest_snapshot.copy() if self.latest_snapshot else None

    def get_timeseries(
        self, metric_key: str, agent_id: str | None = None, window: int | None = None
    ) -> list[dict[str, Any]]:
        """Extract time series data for a specific metric.

        Args:
            metric_key: Metric to extract (e.g., 'sri', 'satori_wave_ratio')
            agent_id: If specified, extract per-agent metric.
                     If None, extract system-wide metric.
            window: Optional number of most recent epochs to return

        Returns:
            List of dicts with 'epoch' and 'value' keys
        """
        with self._lock:
            history_list = list(self.history)

        if window:
            history_list = history_list[-window:]

        timeseries = []
        for snapshot in history_list:
            epoch = snapshot["epoch"]
            value = None

            if agent_id:
                # Per-agent metric
                agent_metrics = snapshot.get("agent_metrics", {})
                if agent_id in agent_metrics:
                    value = agent_metrics[agent_id].get(metric_key)
            else:
                # System-wide metric
                system_metrics = snapshot.get("system_metrics", {})
                value = system_metrics.get(metric_key)

                # Try TDA metrics if not in system metrics
                if value is None:
                    tda_metrics = snapshot.get("tda_metrics", {})
                    value = tda_metrics.get(metric_key)

            if value is not None:
                timeseries.append({"epoch": epoch, "value": value})

        return timeseries

    def get_agent_ids(self) -> list[str]:
        """Get list of all agent IDs from latest snapshot.

        Returns:
            List of agent ID strings
        """
        snapshot = self.get_latest_snapshot()
        if snapshot and "agent_metrics" in snapshot:
            return list(snapshot["agent_metrics"].keys())
        return []

    def get_statistics(self) -> dict[str, Any]:
        """Get collector statistics.

        Returns:
            Dictionary with statistics about collector state
        """
        with self._lock:
            return {
                "total_epochs_processed": self.total_epochs_processed,
                "history_length": len(self.history),
                "phase_transitions_detected": self.phase_transitions_detected,
                "queue_size": self.metrics_queue.qsize(),
                "has_latest_snapshot": self.latest_snapshot is not None,
            }

    def clear(self) -> None:
        """Clear all collected metrics and history (thread-safe)."""
        with self._lock:
            self.history.clear()
            self.latest_snapshot = None
            self.total_epochs_processed = 0
            self.phase_transitions_detected = 0

        # Drain queue
        while not self.metrics_queue.empty():
            try:
                self.metrics_queue.get_nowait()
            except queue.Empty:
                break
