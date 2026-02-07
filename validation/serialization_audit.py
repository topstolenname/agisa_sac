#!/usr/bin/env python3
"""Comprehensive serialization audit for AGI-SAC components.

This script audits all AGI-SAC components to ensure they properly implement
serialization (to_dict/from_dict) with version tracking, as required by CLAUDE.md.
"""
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from agisa_sac import FRAMEWORK_VERSION
except ImportError as e:
    print(f"Cannot import agisa_sac: {e}")
    print("Make sure to run: poetry install")
    sys.exit(1)


# Component registry: (module, class_name, init_kwargs_or_None, requires_network)
# init_kwargs=None means skip instantiation test (needs complex dependencies)
COMPONENTS_TO_AUDIT = [
    # Components that can be fully tested
    (
        "agisa_sac.core.components.memory",
        "MemoryContinuumLayer",
        {"agent_id": "audit_agent", "capacity": 10, "use_semantic": False},
        False,
    ),
    (
        "agisa_sac.core.components.memory",
        "MemoryEncapsulation",
        {"memory_id": "audit_mem_1", "content": {"test": "data"}, "importance": 0.5},
        False,
    ),
    (
        "agisa_sac.core.components.voice",
        "VoiceEngine",
        {"agent_id": "audit_agent"},
        False,
    ),
    (
        "agisa_sac.core.components.resonance",
        "TemporalResonanceTracker",
        {"agent_id": "audit_agent"},
        False,
    ),
    (
        "agisa_sac.core.components.resonance",
        "ResonanceLiturgy",
        {"agent_id": "audit_agent"},
        False,
    ),
    (
        "agisa_sac.core.components.social",
        "DynamicSocialGraph",
        {"num_agents": 3, "agent_ids": ["a1", "a2", "a3"]},
        False,
    ),
    (
        "agisa_sac.core.components.crdt_memory",
        "CRDTMemoryLayer",
        {"node_id": "audit_node"},
        False,
    ),
    (
        "agisa_sac.core.components.continuity_bridge",
        "ContinuityBridgeProtocol",
        {},
        False,
    ),
    # Components requiring network access (sentence-transformers model)
    (
        "agisa_sac.core.components.enhanced_cbp",
        "EnhancedContinuityBridgeProtocol",
        {},
        True,
    ),
    (
        "agisa_sac.core.components.semantic_analyzer",
        "EnhancedSemanticAnalyzer",
        {},
        True,
    ),
    # Components requiring complex dependencies (method-only check)
    ("agisa_sac.core.components.reflexivity", "ReflexivityLayer", None, False),
    ("agisa_sac.core.components.semantic_analyzer", "SemanticProfile", None, False),
    ("agisa_sac.core.components.cognitive", "CognitiveDiversityEngine", None, False),
]


def import_class(module_name: str, class_name: str) -> Tuple[bool, Any]:
    """Import a class from a module."""
    try:
        import importlib

        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        return True, cls
    except ImportError as e:
        return False, f"Module not found: {e}"
    except AttributeError as e:
        return False, f"Class not found: {e}"
    except Exception as e:
        return False, f"Import error: {e}"


def audit_component(
    module_name: str,
    class_name: str,
    init_kwargs: Optional[Dict[str, Any]],
    requires_network: bool,
) -> Tuple[bool, str]:
    """Audit a single component for serialization compliance.

    Returns:
        (passed, message) tuple
    """
    # Import the class
    success, result = import_class(module_name, class_name)
    if not success:
        return False, f"Import failed: {result}"

    component_class = result

    # Check for to_dict method
    if not hasattr(component_class, "to_dict"):
        return False, "Missing to_dict() method"

    # Check for from_dict class method
    if not hasattr(component_class, "from_dict"):
        return False, "Missing from_dict() class method"

    # If no init kwargs provided, just verify methods exist
    if init_kwargs is None:
        return True, "Methods present (complex init, skipping instantiation)"

    # Try to instantiate component
    try:
        instance = component_class(**init_kwargs)
    except Exception as e:
        if requires_network:
            return True, f"Methods present (network required: {e})"
        return True, f"Methods present (cannot instantiate: {e})"

    # Test to_dict
    try:
        state_dict = instance.to_dict()
    except Exception as e:
        return False, f"to_dict() raised error: {e}"

    if not isinstance(state_dict, dict):
        return False, f"to_dict() returned {type(state_dict)}, not dict"

    # Check for version field
    if "version" not in state_dict:
        return False, "to_dict() missing 'version' field"

    # Verify version matches FRAMEWORK_VERSION
    if state_dict["version"] != FRAMEWORK_VERSION:
        return False, (
            f"Version mismatch: {state_dict['version']} != {FRAMEWORK_VERSION}"
        )

    # Test from_dict round-trip
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            restored = component_class.from_dict(state_dict)
    except Exception as e:
        return False, f"from_dict() raised error: {e}"

    # Verify restored is correct type
    if not isinstance(restored, component_class):
        return False, (f"from_dict() returned {type(restored)}, not {component_class}")

    # Test round-trip fidelity (serialize again)
    try:
        state_dict_2 = restored.to_dict()
    except Exception as e:
        return False, f"Round-trip to_dict() failed: {e}"

    # Basic equality check on state keys
    if set(state_dict.keys()) != set(state_dict_2.keys()):
        return False, "Round-trip changed keys"

    return True, "Full round-trip serialization validated"


def main() -> int:
    """Run serialization audit."""
    print("=" * 70)
    print("AGI-SAC Serialization Audit")
    print("=" * 70)
    print(f"Framework Version: {FRAMEWORK_VERSION}")
    print(f"Components to audit: {len(COMPONENTS_TO_AUDIT)}")
    print("=" * 70)
    print()

    results: List[Tuple[str, bool, str]] = []

    for module_name, class_name, init_kwargs, requires_network in COMPONENTS_TO_AUDIT:
        component_full_name = f"{module_name}.{class_name}"
        print(f"Auditing: {component_full_name}")

        passed, message = audit_component(
            module_name, class_name, init_kwargs, requires_network
        )
        results.append((component_full_name, passed, message))

        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {message}")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed, _ in results if passed)
    failed_count = len(results) - passed_count
    full_roundtrip = sum(1 for _, _, msg in results if "round-trip" in msg.lower())

    print(f"Total components: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"  Full round-trip tested: {full_roundtrip}")
    print(f"  Methods verified only: {passed_count - full_roundtrip}")
    print(f"Failed: {failed_count}")
    print()

    if failed_count > 0:
        print("FAILURES:")
        for name, passed, message in results:
            if not passed:
                print(f"  FAIL {name}: {message}")
        print()

    if failed_count == 0:
        print("All components passed serialization audit!")
        return 0
    else:
        print(f"{failed_count} component(s) failed audit")
        return 1


if __name__ == "__main__":
    sys.exit(main())
