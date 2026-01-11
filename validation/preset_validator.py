#!/usr/bin/env python3
"""Validate all configuration presets are loadable and valid.

This script validates that all configuration presets defined in agisa_sac.config
can be loaded and create valid SimulationConfig objects.
"""
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from agisa_sac.config import PRESETS, SimulationConfig, get_preset
except ImportError as e:
    print(f"❌ Cannot import agisa_sac.config: {e}")
    print("Make sure to run: poetry install")
    sys.exit(1)


# Known preset names (from agisa_sac.__init__.py)
EXPECTED_PRESETS = ["quick_test", "default", "medium", "large"]


def validate_preset(name: str, config_dict: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a preset configuration.

    Returns:
        (passed, message) tuple
    """
    # Check if it's a dictionary
    if not isinstance(config_dict, dict):
        return False, f"Preset is {type(config_dict)}, not dict"

    # Try to create SimulationConfig from preset
    try:
        config = SimulationConfig.from_dict(config_dict)
    except Exception as e:
        return False, f"from_dict() failed: {type(e).__name__}: {e}"

    # Basic validation
    if config.num_agents <= 0:
        return False, "num_agents must be positive"

    if config.num_epochs <= 0:
        return False, "num_epochs must be positive"

    # Try to serialize it back
    try:
        serialized = config.to_dict()
    except Exception as e:
        return False, f"to_dict() failed: {type(e).__name__}: {e}"

    if not isinstance(serialized, dict):
        return False, f"to_dict() returned {type(serialized)}, not dict"

    # Return success with config summary
    return True, (
        f"✓ Valid ({config.num_agents} agents, {config.num_epochs} epochs, "
        f"seed={getattr(config, 'random_seed', 'N/A')})"
    )


def validate_get_preset(name: str) -> Tuple[bool, str]:
    """Validate that get_preset() works for a preset name."""
    try:
        config = get_preset(name)
    except Exception as e:
        return False, f"get_preset('{name}') failed: {type(e).__name__}: {e}"

    if not isinstance(config, SimulationConfig):
        return False, f"get_preset() returned {type(config)}, not SimulationConfig"

    return True, f"✓ get_preset('{name}') works"


def main() -> int:
    """Run preset validation."""
    print("=" * 70)
    print("AGI-SAC Configuration Preset Validation")
    print("=" * 70)
    print(f"Presets to validate: {len(PRESETS)}")
    print(f"Expected presets: {', '.join(EXPECTED_PRESETS)}")
    print("=" * 70)
    print()

    results = []

    # Validate each preset in PRESETS
    print("Validating preset dictionaries:")
    print("-" * 70)
    for preset_name in sorted(PRESETS.keys()):
        preset_config = PRESETS[preset_name]
        print(f"\nPreset: {preset_name}")

        passed, message = validate_preset(preset_name, preset_config)
        results.append((f"PRESETS[{preset_name}]", passed, message))

        print(f"  {message}")

    # Validate get_preset() function for expected presets
    print("\n" + "=" * 70)
    print("Validating get_preset() function:")
    print("-" * 70)
    for preset_name in EXPECTED_PRESETS:
        print(f"\nget_preset('{preset_name}')")

        passed, message = validate_get_preset(preset_name)
        results.append((f"get_preset('{preset_name}')", passed, message))

        print(f"  {message}")

    # Check for missing expected presets
    print("\n" + "=" * 70)
    print("Checking for missing presets:")
    print("-" * 70)
    missing_presets = set(EXPECTED_PRESETS) - set(PRESETS.keys())
    if missing_presets:
        print(f"⚠ Missing presets: {', '.join(missing_presets)}")
        for name in missing_presets:
            results.append((f"PRESETS[{name}]", False, "Preset not found"))
    else:
        print("✓ All expected presets are defined")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed, _ in results if passed)
    failed_count = len(results) - passed_count

    print(f"Total validations: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print()

    if failed_count > 0:
        print("FAILURES:")
        for name, passed, message in results:
            if not passed:
                print(f"  ✗ {name}: {message}")
        print()

    # Return exit code
    if failed_count == 0:
        print("✓ All presets validated successfully!")
        return 0
    else:
        print(f"✗ {failed_count} validation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
