# ==============================================================================
# STRANGLER FIG PATTERN: Compatibility Shim
# ==============================================================================
# This file is a compatibility shim for the Strangler Fig refactoring pattern.
# 
# The canonical source for this class has been migrated to:
#   AGI-SAC_Clean/src/agisa_sac/core/components/cognitive.py
#
# This shim ensures that existing import paths continue to work during the
# transition period. Once all code has been updated to import from the new
# location, this file can be safely deleted.
#
# Migration date: October 16, 2025
# ==============================================================================

import sys
import os
import importlib.util

# Calculate the path to the clean repository's cognitive.py
_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
_clean_cognitive_path = os.path.join(_base_path, 'AGI-SAC_Clean/src/agisa_sac/core/components/cognitive.py')

# Load the module directly from the clean repository using importlib
_spec = importlib.util.spec_from_file_location("_clean_cognitive", _clean_cognitive_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load cognitive module from clean repository: {_clean_cognitive_path}")

_clean_cognitive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_clean_cognitive)

# Re-export the class from the clean repository
CognitiveDiversityEngine = _clean_cognitive.CognitiveDiversityEngine

__all__ = ["CognitiveDiversityEngine"]

# ==============================================================================
# Original implementation has been moved to:
#   AGI-SAC_Clean/src/agisa_sac/core/components/cognitive.py
# ==============================================================================
