"""AGI-SAC Simulation Framework
----------------------------
A multi-agent simulation framework for exploring emergent cognition,
distributed identity, and Stand Alone Complex phenomena.
"""

__version__ = "1.0.0-alpha"
FRAMEWORK_VERSION = f"AGI-SAC v{__version__}"

# Expose key classes for easier import from the top-level package
try:
    from .core.orchestrator import SimulationOrchestrator
    from .agents.agent import EnhancedAgent
    from .core.components.memory import MemoryContinuumLayer, MemoryEncapsulation
    from .core.components.cognitive import CognitiveDiversityEngine
    from .core.components.social import DynamicSocialGraph
    from .core.components.resonance import TemporalResonanceTracker, ResonanceLiturgy
    from .core.components.voice import VoiceEngine
    from .core.components.reflexivity import ReflexivityLayer
    from .core.components.semantic_analyzer import (
        EnhancedSemanticAnalyzer,
        SemanticProfile,
    )
    from .core.components.crdt_memory import CRDTMemoryLayer
    from .core.components.enhanced_cbp import EnhancedContinuityBridgeProtocol
    from .analysis.analyzer import AgentStateAnalyzer
    from .analysis.exporter import ChronicleExporter
    from .analysis.tda import PersistentHomologyTracker
    from .analysis.visualization import (
        plot_persistence_diagram,
        plot_persistence_barcode,
        plot_metric_comparison,
    )
    from .core.multi_agent_system import MultiAgentSystem
    from .gcp import VertexAgent
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
    warnings.warn(
        f"Could not import all AGI-SAC components during package initialization: {e}",
        ImportWarning,
    )

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
    "EnhancedSemanticAnalyzer",
    "SemanticProfile",
    "CRDTMemoryLayer",
    "EnhancedContinuityBridgeProtocol",
    "AgentStateAnalyzer",
    "ChronicleExporter",
    "PersistentHomologyTracker",
    "MessageBus",
    "plot_persistence_diagram",
    "plot_persistence_barcode",
    "plot_metric_comparison",
    "cluster_archetypes",
    "MultiAgentSystem",
    "compute_sri",
    "compute_nds",
    "compute_vsd",
    "compute_mce",
    "generate_monitoring_metrics",
    "VertexAgent",
]

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
