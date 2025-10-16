# ==============================================================================
# STRANGLER FIG PATTERN: Compatibility Shim
# ==============================================================================
# This file is a compatibility shim for the Strangler Fig refactoring pattern.
# 
# The canonical source for this class has been migrated to:
#   AGI-SAC_Clean/src/agisa_sac/analysis/exporter.py
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

# Calculate the path to the clean repository's exporter.py
_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
_clean_path = os.path.join(_base_path, 'AGI-SAC_Clean/src/agisa_sac/analysis/exporter.py')

# Load the module directly from the clean repository using importlib
_spec = importlib.util.spec_from_file_location("_clean_exporter", _clean_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load exporter module from clean repository: {_clean_path}")

_clean_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_clean_module)

# Re-export the class from the clean repository
ChronicleExporter = _clean_module.ChronicleExporter

__all__ = ["ChronicleExporter"]

# ==============================================================================
# Original implementation has been moved to:
#   AGI-SAC_Clean/src/agisa_sac/analysis/exporter.py
# ==============================================================================
