# AGI-SAC Refactoring Strategy

## Overview

This document describes the **Strangler Fig Pattern** refactoring strategy being used to gradually migrate the AGI-SAC codebase from its original monolithic structure to a clean, modular architecture.

## Migration Date

Started: **October 16, 2025**

## The Strangler Fig Pattern

The [Strangler Fig Pattern](https://martinfowler.com/bliki/StranglerFigApplication.html) is a refactoring approach where:

1. New functionality is built in a new system alongside the old
2. The old system is gradually strangled (replaced) by the new one
3. Once all functionality has migrated, the old system can be safely removed

## Our Implementation: The importlib Shim

### The Challenge

Python's module system doesn't natively support having the same package in two locations simultaneously. We need a way to:

- Keep the original import paths working
- Source code from a new, clean repository
- Avoid breaking existing code during the transition

### The Solution

We use **compatibility shims** - small Python files that dynamically load modules from the clean repository using `importlib.util`.

### Shim Template

```python
# ==============================================================================
# STRANGLER FIG PATTERN: Compatibility Shim
# Migration date: October 16, 2025
# ==============================================================================
import importlib.util
import os

# Calculate the path to the clean repository's module
_base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../'))
_clean_module_path = os.path.join(_base_path, 'AGI-SAC_Clean/src/agisa_sac/core/components/MODULE_NAME.py')

# Load the module directly from the clean repository
_spec = importlib.util.spec_from_file_location("_clean_MODULE_NAME", _clean_module_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load MODULE_NAME from clean repository: {_clean_module_path}")

_clean_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_clean_module)

# Re-export the classes from the clean repository
ClassName = _clean_module.ClassName

__all__ = ["ClassName"]
# ==============================================================================
```

### Why importlib?

Using `importlib.util.spec_from_file_location()` allows us to:

1. **Load a module from an absolute file path** without modifying `sys.path`
2. **Avoid circular imports** by giving the loaded module a different internal name
3. **Re-export classes** so existing imports continue to work unchanged
4. **Maintain compatibility** during the entire migration process

## Migration Process

### Step 1: Copy (Don't Move)

Copy the component to the clean repository, keeping the original in place:

```bash
cp agisa_sac/src/agisa_sac/core/components/MODULE.py AGI-SAC_Clean/src/agisa_sac/core/components/MODULE.py
```

### Step 2: Create the Shim

Replace the original file's contents with an importlib shim that redirects to the clean version.

### Step 3: Test

Run the golden master test to verify behavioral consistency:

```bash
pytest tests/test_simulation_fidelity.py -v
```

### Step 4: Refactor (Optional)

Now you can safely refactor the clean version. The shim ensures backward compatibility.

### Step 5: Clean Up (Future)

Once the migration is complete and stable, shims can be removed and imports updated.

## Migrated Components

### ✅ Completed

| Component | Original Location | Clean Location | Migration Date |
|-----------|------------------|----------------|----------------|
| `memory.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |
| `cognitive.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |
| `resonance.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |
| `semantic_analyzer.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |
| `reflexivity.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |
| `social.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |
| `voice.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |
| `crdt_memory.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |
| `enhanced_cbp.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |
| `continuity_bridge.py` | `agisa_sac/src/agisa_sac/core/components/` | `AGI-SAC_Clean/src/agisa_sac/core/components/` | Oct 16, 2025 |

### 🎊 MILESTONE: Core Components Migration Complete!

**All 10 core cognitive components successfully migrated with 100% test pass rate!**

### 🔄 In Progress

| Component | Status | Notes |
|-----------|--------|-------|
| TBD | Next target | To be determined |

### 📋 Planned

Components to migrate (priority order):

1. `cognitive.py` - Cognitive diversity engine
2. `semantic_analyzer.py` - Semantic analysis components
3. `resonance.py` - Resonance tracking
4. `reflexivity.py` - Reflexivity layer
5. `social.py` - Social graph dynamics
6. Additional components as identified

## Testing Strategy

### Golden Master Testing

We use **characterization testing** (golden master testing) to ensure that refactoring doesn't change behavior:

- `tests/test_simulation_fidelity.py` captures simulation output
- Compares against a known "golden" reference
- Any behavioral change is immediately detected

### Test-Driven Migration

Before each migration:
1. ✅ Ensure golden master test passes
2. 🔄 Perform migration (copy + shim)
3. ✅ Verify test still passes
4. 🎉 Migration successful

## Benefits of This Approach

1. **Zero Downtime** - System continues working throughout migration
2. **Incremental Progress** - Migrate one component at a time
3. **Safety Net** - Golden master tests catch any breaking changes
4. **Rollback Capable** - Easy to revert if issues arise
5. **Clear Documentation** - Shim files self-document the migration state

## Directory Structure

```
C:\New folder\
├── agisa_sac/                    # Original repository
│   └── src/agisa_sac/
│       └── core/components/
│           ├── memory.py         # ← SHIM: Redirects to clean repo
│           ├── cognitive.py      # ← SHIM: Redirects to clean repo
│           └── ...               # Other components (not yet migrated)
│
└── AGI-SAC_Clean/                # Clean refactored repository
    └── src/agisa_sac/
        └── core/components/
            ├── memory.py         # ← CANONICAL: Clean implementation
            ├── cognitive.py      # ← CANONICAL: Clean implementation
            └── ...               # Future clean implementations
```

## Notes

- Shim files are temporary and will be removed once migration is complete
- Each shim is approximately 30-40 lines vs 500+ lines of original code
- The clean repository becomes the source of truth for migrated components
- Original files can be backed up with `.backup` extension if needed

## References

- [Martin Fowler - Strangler Fig Application](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Working Effectively with Legacy Code](https://www.amazon.com/Working-Effectively-Legacy-Michael-Feathers/dp/0131177052) by Michael Feathers
- Golden Master Testing: Characterization tests for refactoring safety
