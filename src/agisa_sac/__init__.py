"""
AGI-SAC Simulation Framework
----------------------------

A multi-agent simulation framework for exploring emergent cognition,
distributed identity, and Stand Alone Complex phenomena.
"""

__version__ = "1.0.0-alpha"
FRAMEWORK_VERSION = f"AGI-SAC v{__version__}"

# Expose key classes for easier import from the top-level package
try:
    from .orchestrator import SimulationOrchestrator
    from .agent import EnhancedAgent
    from .components.memory import MemoryContinuumLayer, MemoryEncapsulation
    from .components.cognitive import CognitiveDiversityEngine
    from .components.social import DynamicSocialGraph
    from .components.resonance import TemporalResonanceTracker, ResonanceLiturgy
    from .components.voice import VoiceEngine
    from .components.reflexivity import ReflexivityLayer
    from .analysis.analyzer import AgentStateAnalyzer
    from .analysis.exporter import ChronicleExporter
    from .analysis.tda import PersistentHomologyTracker
    from .analysis.visualization import plot_persistence_diagram, plot_persistence_barcode, plot_metric_comparison
    from .analysis.clustering import cluster_archetypes
    from .metrics.monitoring import (
        compute_sri,
        compute_nds,
        compute_vsd,
        compute_mce,
        generate_monitoring_metrics,
    )
    from .utils.message_bus import MessageBus
except ImportError as e:
    import warnings
    warnings.warn(f"Could not import all AGI-SAC components during package initialization: {e}", ImportWarning)

# Define __all__ for explicit public API if desired
__all__ = [
    "FRAMEWORK_VERSION",
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
    "AgentStateAnalyzer",
    "ChronicleExporter",
    "PersistentHomologyTracker",
    "MessageBus",
    "plot_persistence_diagram",
    "plot_persistence_barcode",
    "plot_metric_comparison",
    "cluster_archetypes",
    "compute_sri",
    "compute_nds",
    "compute_vsd",
    "compute_mce",
    "generate_monitoring_metrics",
]

# Optional: Basic logging setup for the library
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

print(f"AGI-SAC Framework ({FRAMEWORK_VERSION}) initialized.")


























