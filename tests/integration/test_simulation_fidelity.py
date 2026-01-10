"""
Golden master test for simulation fidelity.

This test ensures that refactoring doesn't change the simulation's
core behavior by comparing output against a known 'golden' reference.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Get the absolute paths to our source directories
# This ensures the test can be run from anywhere
base_path = os.path.abspath("C:/New folder/")
clean_src_path = os.path.join(base_path, "AGI-SAC_Clean/src")
old_src_path = os.path.join(base_path, "agisa_sac/src")

# Add the new, clean source directory to the Python path FIRST
# This makes Python look here for modules before looking anywhere else.
if clean_src_path not in sys.path:
    sys.path.insert(0, clean_src_path)

# ALSO add the old source directory to the path for files we haven't moved
if old_src_path not in sys.path:
    sys.path.insert(1, old_src_path)


def test_simulation_produces_consistent_output():
    """
    Runs a quick simulation and compares its output to a known 'golden' version.
    This ensures that refactoring doesn't change the simulation's core behavior.
    """
    # Define the paths for the config, the new output, and the reference output
    root_dir = Path(__file__).parent.parent
    config_file = root_dir / "config_quick_test.json"
    output_dir = root_dir / "tests" / "outputs"
    new_output_file = output_dir / "quick_test_output_new.txt"
    golden_output_file = output_dir / "quick_test_output_golden.txt"

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run the simulation using the quick test configuration
    result = subprocess.run(
        ["python", str(root_dir / "sim_runner.py"), str(config_file)],
        capture_output=True,
        text=True,
        cwd=str(root_dir),
    )

    # First, check that the simulation command ran successfully
    assert result.returncode == 0, f"Simulation run failed: {result.stderr}"

    # Extract the final summary line (the dictionary output)
    # This is the deterministic part we want to compare
    stdout_lines = result.stdout.strip().split("\n")
    summary_line = stdout_lines[-1]  # Last line should be the summary dict

    try:
        # Parse and normalize the output to handle minor formatting differences
        summary_dict = eval(summary_line)
        normalized_output = json.dumps(summary_dict, sort_keys=True, indent=2)
    except Exception:
        # If parsing fails, just use the raw output
        normalized_output = summary_line

    # Write the new output
    new_output_file.write_text(normalized_output, encoding="utf-8")

    # --- This is a one-time setup step ---
    # If the 'golden' file doesn't exist yet, we create it from this first run.
    if not golden_output_file.exists():
        golden_output_file.write_text(normalized_output, encoding="utf-8")
        print(f"✓ Created golden reference file: {golden_output_file}")
        return  # First run always passes after creating golden file

    # Finally, compare the new output with the golden reference
    golden_content = golden_output_file.read_text(encoding="utf-8")
    new_content = new_output_file.read_text(encoding="utf-8")

    # For better error messages, parse both and compare
    try:
        golden_dict = json.loads(golden_content)
        new_dict = json.loads(new_content)

        # Check if they match
        if golden_dict != new_dict:
            print("\n❌ Simulation output has changed!")
            print(f"\nGolden output:\n{json.dumps(golden_dict, indent=2)}")
            print(f"\nNew output:\n{json.dumps(new_dict, indent=2)}")

            # Show differences
            all_keys = set(golden_dict.keys()) | set(new_dict.keys())
            for key in all_keys:
                if golden_dict.get(key) != new_dict.get(key):
                    print(f"\n  Difference in '{key}':")
                    print(f"    Golden: {golden_dict.get(key)}")
                    print(f"    New:    {new_dict.get(key)}")

            assert (
                False
            ), "The simulation output has changed. See above for differences."
    except json.JSONDecodeError:
        # Fallback to simple text comparison
        assert new_content == golden_content, (
            f"The simulation output has changed.\n"
            f"Golden: {golden_content}\nNew: {new_content}"
        )

    print("✓ Simulation output matches golden reference")
