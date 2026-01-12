"""
Prometheus metrics for AGI-SAC simulation monitoring.

This module provides comprehensive metrics collection for production monitoring
of multi-agent simulations, including performance, resource usage, and system health.
"""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        generate_latest,
    )

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

    # Provide no-op placeholders
    class Counter:
        def __init__(self, *args, **kwargs):
            pass

        def inc(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Gauge:
        def __init__(self, *args, **kwargs):
            pass

        def set(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):
            return self

    class Histogram:
        def __init__(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

    CollectorRegistry = None
    CONTENT_TYPE_LATEST = "text/plain"

    def generate_latest(registry):
        return b""


try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    psutil = None  # type: ignore

logger = logging.getLogger(__name__)


def _require_enabled(func: Callable) -> Callable:
    """Decorator to skip method execution when metrics are disabled.

    Args:
        func: The method to wrap

    Returns:
        Wrapped method that checks self.enabled before executing
    """

    @wraps(func)
    def wrapper(self: "PrometheusMetrics", *args: Any, **kwargs: Any) -> Any:
        if not self.enabled:
            return None
        return func(self, *args, **kwargs)

    return wrapper


class PrometheusMetrics:
    """Prometheus metrics collector for AGI-SAC simulations."""

    def __init__(self, registry: Optional["CollectorRegistry"] = None):
        """Initialize Prometheus metrics.

        Args:
            registry: Optional custom CollectorRegistry. If None, uses default.
        """
        if not HAS_PROMETHEUS:
            logger.warning(
                "prometheus-client not installed. Metrics collection disabled. "
                "Install with: pip install prometheus-client"
            )
            self.enabled = False
            return

        if not HAS_PSUTIL:
            logger.warning(
                "psutil not installed. System resource metrics will be unavailable. "
                "Install with: pip install psutil"
            )

        self.enabled = True
        self.registry = registry
        self._process = psutil.Process() if HAS_PSUTIL and psutil else None

        # Simulation metrics
        self.simulation_duration = Histogram(
            "agisa_simulation_duration_seconds",
            "Time spent in simulation epoch",
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0],
            registry=self.registry,
        )

        self.simulation_epochs_total = Counter(
            "agisa_simulation_epochs_total",
            "Total number of simulation epochs completed",
            registry=self.registry,
        )

        self.simulation_errors_total = Counter(
            "agisa_simulation_errors_total",
            "Total number of simulation errors",
            ["error_type"],
            registry=self.registry,
        )

        # Agent metrics
        self.agent_count = Gauge(
            "agisa_agent_count",
            "Current number of active agents",
            registry=self.registry,
        )

        self.agent_interactions_total = Counter(
            "agisa_agent_interactions_total",
            "Total number of agent interactions",
            registry=self.registry,
        )

        self.agent_state_changes_total = Counter(
            "agisa_agent_state_changes_total",
            "Total number of agent state changes",
            ["state_type"],
            registry=self.registry,
        )

        # Memory metrics
        self.memory_operations_total = Counter(
            "agisa_memory_operations_total",
            "Total number of memory operations",
            ["operation"],
            registry=self.registry,
        )

        self.memory_size_bytes = Gauge(
            "agisa_memory_size_bytes",
            "Current memory usage in bytes",
            ["memory_type"],
            registry=self.registry,
        )

        self.memory_items_count = Gauge(
            "agisa_memory_items_count",
            "Number of items in memory stores",
            ["memory_type"],
            registry=self.registry,
        )

        # TDA (Topological Data Analysis) metrics
        self.tda_persistence_features = Gauge(
            "agisa_tda_persistence_features",
            "Number of persistent topological features",
            ["dimension"],
            registry=self.registry,
        )

        self.tda_computation_duration = Histogram(
            "agisa_tda_computation_duration_seconds",
            "Time spent computing topological features",
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0],
            registry=self.registry,
        )

        # Social graph metrics
        self.social_graph_edges = Gauge(
            "agisa_social_graph_edges",
            "Number of edges in social graph",
            registry=self.registry,
        )

        self.social_graph_density = Gauge(
            "agisa_social_graph_density",
            "Density of the social graph (0-1)",
            registry=self.registry,
        )

        self.social_clustering_coefficient = Gauge(
            "agisa_social_clustering_coefficient",
            "Average clustering coefficient of social graph",
            registry=self.registry,
        )

        # System resource metrics
        self.system_cpu_percent = Gauge(
            "agisa_system_cpu_percent", "CPU usage percentage", registry=self.registry
        )

        self.system_memory_bytes = Gauge(
            "agisa_system_memory_bytes",
            "Memory usage in bytes",
            ["type"],
            registry=self.registry,
        )

        self.system_memory_percent = Gauge(
            "agisa_system_memory_percent",
            "Memory usage percentage",
            registry=self.registry,
        )

        # Federation metrics
        self.federation_nodes_count = Gauge(
            "agisa_federation_nodes_count",
            "Number of federation nodes",
            registry=self.registry,
        )

        self.federation_messages_total = Counter(
            "agisa_federation_messages_total",
            "Total federation messages sent",
            ["message_type"],
            registry=self.registry,
        )

        self.federation_sync_duration = Histogram(
            "agisa_federation_sync_duration_seconds",
            "Time spent synchronizing with federation",
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
            registry=self.registry,
        )

        # Integration metrics (IIT-inspired)
        # Note: Metric names retained for monitoring API compatibility
        self.consciousness_phi = Gauge(
            "agisa_consciousness_phi",
            "IIT-inspired integration (Φ-like) metric",
            registry=self.registry,
        )

        self.consciousness_recursive_depth = Gauge(
            "agisa_consciousness_recursive_depth",
            "Meta-cognitive monitoring depth level",
            registry=self.registry,
        )

        # Ethical metrics
        self.ethics_coexistence_score = Gauge(
            "agisa_ethics_coexistence_score",
            "Harmony/coexistence score (0-1)",
            registry=self.registry,
        )

        self.ethics_violations_total = Counter(
            "agisa_ethics_violations_total",
            "Total number of ethical violations detected",
            ["violation_type"],
            registry=self.registry,
        )

    @_require_enabled
    def record_epoch(self, duration: float) -> None:
        """Record completion of a simulation epoch.

        Args:
            duration: Time taken for the epoch in seconds
        """
        self.simulation_duration.observe(duration)
        self.simulation_epochs_total.inc()

    @_require_enabled
    def record_error(self, error_type: str) -> None:
        """Record a simulation error.

        Args:
            error_type: Type/category of the error
        """
        self.simulation_errors_total.labels(error_type=error_type).inc()

    @_require_enabled
    def update_agent_count(self, count: int) -> None:
        """Update the current agent count.

        Args:
            count: Number of active agents
        """
        self.agent_count.set(count)

    @_require_enabled
    def record_agent_interaction(self) -> None:
        """Record a single agent interaction."""
        self.agent_interactions_total.inc()

    @_require_enabled
    def record_memory_operation(self, operation: str) -> None:
        """Record a memory operation.

        Args:
            operation: Type of operation (read, write, delete, etc.)
        """
        self.memory_operations_total.labels(operation=operation).inc()

    @_require_enabled
    def update_memory_stats(
        self, memory_type: str, size_bytes: int, item_count: int
    ) -> None:
        """Update memory statistics.

        Args:
            memory_type: Type of memory (episodic, semantic, etc.)
            size_bytes: Size in bytes
            item_count: Number of items
        """
        self.memory_size_bytes.labels(memory_type=memory_type).set(size_bytes)
        self.memory_items_count.labels(memory_type=memory_type).set(item_count)

    @_require_enabled
    def update_tda_features(self, dimension: int, count: int) -> None:
        """Update TDA feature count.

        Args:
            dimension: Homology dimension (0, 1, 2)
            count: Number of features in this dimension
        """
        self.tda_persistence_features.labels(dimension=str(dimension)).set(count)

    @_require_enabled
    def record_tda_computation(self, duration: float) -> None:
        """Record TDA computation time.

        Args:
            duration: Computation time in seconds
        """
        self.tda_computation_duration.observe(duration)

    @_require_enabled
    def update_social_graph_stats(
        self, edge_count: int, density: float, clustering: float
    ) -> None:
        """Update social graph statistics.

        Args:
            edge_count: Number of edges
            density: Graph density (0-1)
            clustering: Average clustering coefficient
        """
        self.social_graph_edges.set(edge_count)
        self.social_graph_density.set(density)
        self.social_clustering_coefficient.set(clustering)

    def update_system_resources(self) -> None:
        """Update system resource metrics from psutil."""
        if not self.enabled or not self._process:
            return

        try:
            # CPU usage
            cpu_percent = self._process.cpu_percent(interval=0.1)
            self.system_cpu_percent.set(cpu_percent)

            # Memory usage
            mem_info = self._process.memory_info()
            self.system_memory_bytes.labels(type="rss").set(mem_info.rss)
            self.system_memory_bytes.labels(type="vms").set(mem_info.vms)

            mem_percent = self._process.memory_percent()
            self.system_memory_percent.set(mem_percent)
        except Exception as e:
            # Handle all exceptions gracefully (psutil may not be available)
            logger.warning(f"Failed to update system resource metrics: {e}")

    @_require_enabled
    def update_consciousness_metrics(self, phi: float, recursive_depth: int) -> None:
        """Update integration-related metrics (IIT-inspired Φ and meta-cognitive depth).

        Note: Function name retained for monitoring API compatibility.

        Args:
            phi: IIT-inspired integration metric (Φ-like)
            recursive_depth: Meta-cognitive monitoring depth
        """
        self.consciousness_phi.set(phi)
        self.consciousness_recursive_depth.set(recursive_depth)

    @_require_enabled
    def update_ethics_score(self, score: float) -> None:
        """Update ethical coexistence score.

        Args:
            score: Harmony/coexistence score (0-1)
        """
        self.ethics_coexistence_score.set(score)

    @_require_enabled
    def record_ethics_violation(self, violation_type: str) -> None:
        """Record an ethical violation.

        Args:
            violation_type: Type of violation
        """
        self.ethics_violations_total.labels(violation_type=violation_type).inc()

    def get_metrics(self) -> bytes:
        """Get current metrics in Prometheus exposition format.

        Returns:
            Metrics in Prometheus text format
        """
        if not self.enabled:
            return b""

        return generate_latest(self.registry)

    def get_content_type(self) -> str:
        """Get the content type for metrics endpoint.

        Returns:
            Prometheus content type string
        """
        if not self.enabled:
            return "text/plain"

        return CONTENT_TYPE_LATEST


# Global metrics instance
_global_metrics: PrometheusMetrics | None = None


def get_metrics() -> PrometheusMetrics:
    """Get or create the global metrics instance.

    Returns:
        Global PrometheusMetrics instance
    """
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = PrometheusMetrics()
    return _global_metrics


def reset_metrics() -> None:
    """Reset the global metrics instance (useful for testing)."""
    global _global_metrics
    _global_metrics = None
