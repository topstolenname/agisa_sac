# Golden Master Testing for AGI-SAC

This directory contains the golden master test outputs that serve as a "fingerprint" of correct simulation behavior.

## What is Golden Master Testing?

Golden master testing (also called characterization testing or snapshot testing) is a technique where you capture the output of a working system and use it as a reference for future tests. This ensures that refactoring or changes don't inadvertently alter the system's behavior.

## Files in This Directory

- **`quick_test_output_golden.txt`**: The reference output from a known-good simulation run using `config_quick_test.json`. This file should only be updated when you intentionally change the simulation behavior.

- **`quick_test_output_new.txt`**: Temporary file created during test runs to compare against the golden reference.

## Running the Golden Master Test

From the root of the `agisa_sac` directory:

```bash
# Run the test
pytest tests/test_simulation_fidelity.py -v

# Run with output visible
pytest tests/test_simulation_fidelity.py -v -s
```

## What the Test Does

1. Runs the simulation with `config_quick_test.json`
2. Captures the output summary (satori wave ratio, archetypes, etc.)
3. Compares it to the golden reference
4. Fails if the output has changed unexpectedly

## When the Test Fails

If the test fails, it means one of two things:

1. **Unintended change**: You've accidentally changed the simulation behavior. Review your changes and fix the bug.

2. **Intended change**: You've intentionally modified the simulation. In this case:
   - Review the differences shown in the test output
   - If the new behavior is correct, update the golden file:
     ```bash
     # Delete the old golden file
     rm tests/outputs/quick_test_output_golden.txt
     
     # Run the test to create a new golden file
     pytest tests/test_simulation_fidelity.py
     ```

## Why This Matters

This test protects against regression bugs. As you refactor code (e.g., moving from Phase 3.5 to a modular structure), this test ensures that the simulation still produces the same results, giving you confidence that your refactoring is correct.

## Configuration

The test uses `config_quick_test.json` which runs a minimal simulation:
- 3 agents
- 5 epochs
- Fixed random seed for reproducibility

This keeps the test fast while still exercising all the core simulation components.
