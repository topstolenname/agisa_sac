#!/usr/bin/env python3
"""Validate all documented CLI commands work correctly.

This script tests that all CLI commands defined in pyproject.toml work as expected
and return proper exit codes and help text.
"""
import subprocess
import sys
from typing import List, Tuple


# CLI commands to validate: (command, args, expected_exit_code, description)
CLI_COMMANDS = [
    ("agisa-sac", ["--help"], 0, "Main CLI help"),
    ("agisa-sac", ["--version"], 0, "Version display"),
    ("agisa-sac", ["list-presets"], 0, "List configuration presets"),
    ("agisa-sac", ["run", "--help"], 0, "Run command help"),
    ("agisa-sac", ["convert-transcript", "--help"], 0, "Convert transcript help"),
    ("agisa-federation", ["--help"], 0, "Federation CLI help"),
    ("agisa-chaos", ["--help"], 0, "Chaos CLI help"),
]


def validate_command(
    cmd: str,
    args: List[str],
    expected_code: int,
    description: str
) -> Tuple[bool, str]:
    """Run a CLI command and validate exit code.

    Returns:
        (passed, message) tuple
    """
    full_cmd = ["poetry", "run", cmd] + args
    full_cmd_str = " ".join(full_cmd)

    try:
        result = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=None  # Use current directory
        )

        # Check exit code
        if result.returncode != expected_code:
            return False, (
                f"✗ Exit code {result.returncode} (expected {expected_code})\n"
                f"   stdout: {result.stdout[:200]}\n"
                f"   stderr: {result.stderr[:200]}"
            )

        # For help commands, verify we got some output
        if "--help" in args:
            if not result.stdout and not result.stderr:
                return False, "✗ No help output produced"

        # For version command, verify output contains version info
        if "--version" in args:
            output = result.stdout + result.stderr
            if not any(word in output.lower() for word in ["version", "v1.", "alpha"]):
                return False, f"✗ No version info in output: {output[:100]}"

        return True, f"✓ Exit code {result.returncode}"

    except subprocess.TimeoutExpired:
        return False, "✗ Command timed out after 10s"
    except FileNotFoundError:
        return False, f"✗ Command not found: {cmd}"
    except Exception as e:
        return False, f"✗ Error: {type(e).__name__}: {e}"


def main() -> int:
    """Run CLI validation."""
    print("=" * 70)
    print("AGI-SAC CLI Command Validation")
    print("=" * 70)
    print(f"Commands to validate: {len(CLI_COMMANDS)}")
    print("=" * 70)
    print()

    results: List[Tuple[str, bool, str]] = []

    for cmd, args, expected_code, description in CLI_COMMANDS:
        full_cmd_str = f"{cmd} {' '.join(args)}"
        print(f"Testing: {full_cmd_str}")
        print(f"  Description: {description}")

        passed, message = validate_command(cmd, args, expected_code, description)
        results.append((full_cmd_str, passed, message))

        print(f"  {message}")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed_count = sum(1 for _, passed, _ in results if passed)
    failed_count = len(results) - passed_count

    print(f"Total commands: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print()

    if failed_count > 0:
        print("FAILURES:")
        for cmd, passed, message in results:
            if not passed:
                print(f"  {cmd}")
                print(f"    {message}")
        print()

    # Return exit code
    if failed_count == 0:
        print("✓ All CLI commands validated successfully!")
        return 0
    else:
        print(f"✗ {failed_count} command(s) failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
