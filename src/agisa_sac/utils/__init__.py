"""Utility classes and functions for the AGI-SAC framework."""

from .message_bus import MessageBus

# Lazy import for optional metrics module
_metrics_module = None


def get_metrics():
    """Get or import the metrics module lazily.

    Returns:
        The get_metrics function from the metrics module, or a no-op version
        if metrics dependencies are not available.
    """
    global _metrics_module
    if _metrics_module is None:
        try:
            from . import metrics as _metrics_module
        except ImportError:
            # Create a no-op module if prometheus-client/psutil not available
            class NoOpMetrics:
                enabled = False
                def get_metrics(self):
                    return lambda: type('obj', (object,), {'enabled': False})()
            _metrics_module = NoOpMetrics()

    if hasattr(_metrics_module, 'get_metrics'):
        return _metrics_module.get_metrics()
    return _metrics_module.get_metrics


def reset_metrics():
    """Reset the metrics module (if available)."""
    global _metrics_module
    if _metrics_module is not None and hasattr(_metrics_module, 'reset_metrics'):
        _metrics_module.reset_metrics()


# Only expose core utilities that are always available
__all__ = ["MessageBus", "get_metrics", "reset_metrics"]
