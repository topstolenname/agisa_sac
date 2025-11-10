"""Unit tests for metrics module."""

import pytest
from unittest.mock import Mock, patch
from agisa_sac.utils.metrics import PrometheusMetrics, get_metrics, reset_metrics


class TestPrometheusMetrics:
    """Test PrometheusMetrics class."""

    def test_metrics_disabled_when_prometheus_not_installed(self):
        """Test that metrics are disabled when prometheus-client is not installed."""
        with patch('agisa_sac.utils.metrics.HAS_PROMETHEUS', False):
            # Reset to ensure we get a new instance
            reset_metrics()
            metrics = get_metrics()
            assert metrics.enabled is False

    def test_metrics_enabled_when_prometheus_installed(self):
        """Test that metrics are enabled when prometheus-client is installed."""
        with patch('agisa_sac.utils.metrics.HAS_PROMETHEUS', True):
            with patch('agisa_sac.utils.metrics.HAS_PSUTIL', True):
                metrics = PrometheusMetrics()
                assert metrics.enabled is True

    def test_system_resources_skipped_when_disabled(self):
        """Test that update_system_resources does nothing when disabled."""
        with patch('agisa_sac.utils.metrics.HAS_PROMETHEUS', False):
            metrics = PrometheusMetrics()
            # Should not raise an error
            metrics.update_system_resources()

    def test_system_resources_skipped_when_psutil_missing(self):
        """Test that update_system_resources handles missing psutil gracefully."""
        with patch('agisa_sac.utils.metrics.HAS_PROMETHEUS', True):
            with patch('agisa_sac.utils.metrics.HAS_PSUTIL', False):
                metrics = PrometheusMetrics()
                # Should not raise an error even though psutil is missing
                metrics.update_system_resources()

    def test_record_epoch_when_disabled(self):
        """Test that record_epoch does nothing when disabled."""
        with patch('agisa_sac.utils.metrics.HAS_PROMETHEUS', False):
            metrics = PrometheusMetrics()
            # Should not raise an error
            metrics.record_epoch(1.5)

    def test_update_agent_count_when_disabled(self):
        """Test that update_agent_count does nothing when disabled."""
        with patch('agisa_sac.utils.metrics.HAS_PROMETHEUS', False):
            metrics = PrometheusMetrics()
            # Should not raise an error
            metrics.update_agent_count(100)

    def test_record_memory_operation_when_disabled(self):
        """Test that record_memory_operation does nothing when disabled."""
        with patch('agisa_sac.utils.metrics.HAS_PROMETHEUS', False):
            metrics = PrometheusMetrics()
            # Should not raise an error
            metrics.record_memory_operation("read")

    def test_get_metrics_singleton(self):
        """Test that get_metrics returns the same instance."""
        reset_metrics()
        metrics1 = get_metrics()
        metrics2 = get_metrics()
        assert metrics1 is metrics2

    def test_reset_metrics(self):
        """Test that reset_metrics creates a new instance."""
        reset_metrics()
        metrics1 = get_metrics()
        reset_metrics()
        metrics2 = get_metrics()
        assert metrics1 is not metrics2

    def test_get_metrics_returns_empty_when_disabled(self):
        """Test that get_metrics returns empty bytes when disabled."""
        with patch('agisa_sac.utils.metrics.HAS_PROMETHEUS', False):
            reset_metrics()
            metrics = get_metrics()
            assert metrics.get_metrics() == b""

    def test_content_type_when_disabled(self):
        """Test that get_content_type returns text/plain when disabled."""
        with patch('agisa_sac.utils.metrics.HAS_PROMETHEUS', False):
            reset_metrics()
            metrics = get_metrics()
            assert metrics.get_content_type() == "text/plain"
