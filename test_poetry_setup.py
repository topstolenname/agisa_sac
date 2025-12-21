#!/usr/bin/env python3
"""Test script to verify Poetry setup for AGI-SAC."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Test basic imports
    from agisa_sac.config import PRESETS, get_preset
    from agisa_sac.core.orchestrator import SimulationOrchestrator
    from agisa_sac.utils.logger import get_logger
    
    print("✅ All core imports successful!")
    
    # Test preset loading
    print("\nAvailable presets:")
    for name, config in PRESETS.items():
        print(f"  {name}: {config.num_agents} agents, {config.num_epochs} epochs")
    
    # Test getting a preset
    config = get_preset("quick_test")
    print(f"\n✅ Successfully loaded 'quick_test' preset:")
    print(f"  Agents: {config.num_agents}")
    print(f"  Epochs: {config.num_epochs}")
    print(f"  GPU: {config.use_gpu}")
    print(f"  Semantic: {config.use_semantic}")
    
    # Test logger
    logger = get_logger(__name__)
    logger.info("✅ Logger working correctly")
    
    print("\n🎉 Poetry setup test completed successfully!")
    print("\nYou can now run simulations using:")
    print("  poetry run python test_poetry_setup.py")
    print("\nOr install the full package with:")
    print("  poetry install --all-extras")
    
except Exception as e:
    print(f"❌ Error during setup test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)