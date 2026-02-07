"""AGI-SAC Simulation Framework
----------------------------
A multi-agent simulation framework for exploring emergent cognition,
distributed identity, and Stand Alone Complex phenomena.
"""

import logging

# Import configuration module
from .config import (
    DEFAULT,
    LARGE,
    MEDIUM,
    QUICK_TEST,
    SimulationConfig,
    get_preset,
)
from .utils.logger import get_logger, setup_logging

__version__ = "1.0.0"
FRAMEWORK_VERSION = f"AGI-SAC v{__version__}"

# Lazy import mappings - components are loaded on first access
# This keeps CLI startup fast while maintaining backward compatibility
_LAZY_IMPORTS = {
    # Core components
    "SimulationOrchestrator": ".core.orchestrator",
    "EnhancedAgent": ".agents.agent",
    "MemoryContinuumLayer": ".core.components.memory",
    "MemoryEncapsulation": ".core.components.memory",
    "CognitiveDiversityEngine": ".core.components.cognitive",
    "DynamicSocialGraph": ".core.components.social",
    "TemporalResonanceTracker": ".core.components.resonance",
    "ResonanceLiturgy": ".core.components.resonance",
    "VoiceEngine": ".core.components.voice",
    "ReflexivityLayer": ".core.components.reflexivity",
    "EnhancedSemanticAnalyzer": ".core.components.semantic_analyzer",
    "SemanticProfile": ".core.components.semantic_analyzer",
    "CRDTMemoryLayer": ".core.components.crdt_memory",
    "EnhancedContinuityBridgeProtocol": ".core.components.enhanced_cbp",
    # Analysis
    "AgentStateAnalyzer": ".analysis.analyzer",
    "ChronicleExporter": ".analysis.exporter",
    "PersistentHomologyTracker": ".analysis.tda",
    "plot_persistence_diagram": ".analysis.visualization",
    "plot_persistence_barcode": ".analysis.visualization",
    "plot_metric_comparison": ".analysis.visualization",
    "cluster_archetypes": ".analysis.clustering",
    # Systems
    "MultiAgentSystem": ".core.multi_agent_system",
    "MessageBus": ".utils.message_bus",
    # Metrics
    "compute_sri": ".metrics.monitoring",
    "compute_nds": ".metrics.monitoring",
    "compute_vsd": ".metrics.monitoring",
    "compute_mce": ".metrics.monitoring",
    "generate_monitoring_metrics": ".metrics.monitoring",
    # Cloud
    "VertexAgent": ".gcp",
}


def __getattr__(name: str):
    """Lazy-load heavy components only when accessed.

    This dramatically improves CLI startup time by deferring imports
    of ML dependencies (torch, sentence-transformers) until actually needed.
    """
    if name in _LAZY_IMPORTS:
        module_path = _LAZY_IMPORTS[name]
        try:
            from importlib import import_module

            module = import_module(module_path, package=__package__)
            attr = getattr(module, name)
            # Cache the imported attribute to avoid repeated imports
            globals()[name] = attr
            return attr
        except ImportError as e:
            import warnings

            warnings.warn(
                f"Could not import {name} from {module_path}: {e}",
                ImportWarning,
            )
            raise AttributeError(
                f"Module {__name__} has no attribute {name} "
                f"(failed to lazy-load from {module_path})"
            ) from e

    raise AttributeError(f"Module {__name__} has no attribute {name}")


__all__ = [
    "FRAMEWORK_VERSION",
    # Configuration
    "SimulationConfig",
    "get_preset",
    "QUICK_TEST",
    "DEFAULT",
    "MEDIUM",
    "LARGE",
    # Core components
    "SimulationOrchestrator",
    "EnhancedAgent",
    "MemoryContinuumLayer",
    "MemoryEncapsulation",
    "CognitiveDiversityEngine",
    "DynamicSocialGraph",
    "TemporalResonanceTracker",
    "ResonanceLiturgy",
    "VoiceEngine",
    "ReflexivityLayer",
    "EnhancedSemanticAnalyzer",
    "SemanticProfile",
    "CRDTMemoryLayer",
    "EnhancedContinuityBridgeProtocol",
    # Analysis
    "AgentStateAnalyzer",
    "ChronicleExporter",
    "PersistentHomologyTracker",
    "plot_persistence_diagram",
    "plot_persistence_barcode",
    "plot_metric_comparison",
    "cluster_archetypes",
    # Systems
    "MultiAgentSystem",
    "MessageBus",
    # Metrics
    "compute_sri",
    "compute_nds",
    "compute_vsd",
    "compute_mce",
    "generate_monitoring_metrics",
    # Cloud
    "VertexAgent",
    # Logging
    "get_logger",
    "setup_logging",
]

# Configure logging
# Set up default logging configuration (can be overridden by applications)
logging.getLogger(__name__).addHandler(logging.NullHandler())
