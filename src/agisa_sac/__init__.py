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

__version__ = "1.0.0-alpha"
FRAMEWORK_VERSION = f"AGI-SAC v{__version__}"

# Expose key classes for easier import from the top-level package
try:
    from .agents.agent import EnhancedAgent
    from .analysis.analyzer import AgentStateAnalyzer
    from .analysis.clustering import cluster_archetypes
    from .analysis.exporter import ChronicleExporter
    from .analysis.tda import PersistentHomologyTracker
    from .analysis.visualization import (
        plot_metric_comparison,
        plot_persistence_barcode,
        plot_persistence_diagram,
    )
    from .core.components.cognitive import CognitiveDiversityEngine
    from .core.components.crdt_memory import CRDTMemoryLayer
    from .core.components.enhanced_cbp import EnhancedContinuityBridgeProtocol
    from .core.components.memory import (
        MemoryContinuumLayer,
        MemoryEncapsulation,
    )
    from .core.components.reflexivity import ReflexivityLayer
    from .core.components.resonance import (
        ResonanceLiturgy,
        TemporalResonanceTracker,
    )
    from .core.components.semantic_analyzer import (
        EnhancedSemanticAnalyzer,
        SemanticProfile,
    )
    from .core.components.social import DynamicSocialGraph
    from .core.components.voice import VoiceEngine
    from .core.multi_agent_system import MultiAgentSystem
    from .core.orchestrator import SimulationOrchestrator
    from .gcp import VertexAgent
    from .metrics.monitoring import (
        compute_mce,
        compute_nds,
        compute_sri,
        compute_vsd,
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

