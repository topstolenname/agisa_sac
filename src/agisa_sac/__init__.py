"""
AGI-SAC Simulation Framework
----------------------------

A multi-agent simulation framework for exploring emergent cognition,
distributed identity, and Stand Alone Complex phenomena.
"""

__version__ = "1.0.0-alpha"
FRAMEWORK_VERSION = f"AGI-SAC v{__version__}"

# Expose only lightweight metadata at import time to keep package imports fast.
# Components such as the orchestrator or agent classes should be imported
# directly from their respective modules when needed.

# Define __all__ for explicit public API if desired
__all__ = ["FRAMEWORK_VERSION"]

# Optional: Basic logging setup for the library
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

print(f"AGI-SAC Framework ({FRAMEWORK_VERSION}) initialized.")


























