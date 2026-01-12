"""Pytest configuration and fixtures for AGI-SAC tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add project src directory to sys.path for tests without requiring installation
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
for path in (str(SRC_DIR), str(ROOT_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture
def sample_config() -> dict:
    """Minimal simulation configuration for testing."""
    return {
        "num_agents": 3,
        "num_epochs": 2,
        "random_seed": 42,
        "agent_capacity": 50,
        "use_semantic": False,
        "use_gpu": False,
        "tda_max_dimension": 1,
        "community_check_frequency": 1,
        "epoch_log_frequency": 1,
        "satori_threshold_analyzer": 0.90,
    }


@pytest.fixture
def sample_personality() -> dict:
    """Sample agent personality traits."""
    return {
        "openness": 0.5,
        "consistency": 0.5,
        "conformity": 0.5,
        "curiosity": 0.6,
    }


@pytest.fixture
def test_config_path(tmp_path: Path) -> Path:
    """Create a temporary config file for testing."""
    import json

    config = {
        "num_agents": 2,
        "num_epochs": 1,
        "random_seed": 1,
        "agent_capacity": 10,
        "use_semantic": False,
        "use_gpu": False,
    }

    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f)

    return config_file
