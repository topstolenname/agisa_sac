"""Tests for ConfigManager component."""

import json
import tempfile
from pathlib import Path

import pytest

from agisa_sac.gui.config_manager import ConfigManager


class TestConfigManager:
    """Test suite for ConfigManager class."""

    def test_initialization(self):
        """Test ConfigManager initializes with default config."""
        manager = ConfigManager()
        assert manager.current_config is not None
        assert manager.current_config.num_agents == 5  # default preset
        assert manager.current_config.num_epochs == 10

    def test_get_available_presets(self):
        """Test retrieval of available preset names."""
        manager = ConfigManager()
        presets = manager.get_available_presets()
        assert isinstance(presets, list)
        assert "quick_test" in presets
        assert "default" in presets
        assert "medium" in presets
        assert "large" in presets

    def test_get_preset_valid(self):
        """Test loading a valid preset."""
        manager = ConfigManager()
        config = manager.get_preset("quick_test")
        assert config.num_agents == 3
        assert config.num_epochs == 5
        assert manager.current_config == config

    def test_get_preset_invalid(self):
        """Test loading an invalid preset raises KeyError."""
        manager = ConfigManager()
        with pytest.raises(KeyError):
            manager.get_preset("nonexistent_preset")

    def test_validate_parameters_valid(self):
        """Test validation passes for valid parameters."""
        manager = ConfigManager()
        is_valid, errors = manager.validate_parameters(
            num_agents=100, num_epochs=50, agent_capacity=150
        )
        assert is_valid
        assert len(errors) == 0

    def test_validate_parameters_invalid_type(self):
        """Test validation fails for wrong type."""
        manager = ConfigManager()
        is_valid, errors = manager.validate_parameters(num_agents="not_an_int")
        assert not is_valid
        assert len(errors) > 0
        assert "Expected int" in errors[0]

    def test_validate_parameters_below_min(self):
        """Test validation fails for value below minimum."""
        manager = ConfigManager()
        is_valid, errors = manager.validate_parameters(num_agents=0)
        assert not is_valid
        assert len(errors) > 0
        assert "below minimum" in errors[0]

    def test_validate_parameters_above_max(self):
        """Test validation fails for value above maximum."""
        manager = ConfigManager()
        is_valid, errors = manager.validate_parameters(num_agents=2000)
        assert not is_valid
        assert len(errors) > 0
        assert "exceeds maximum" in errors[0]

    def test_validate_parameters_nullable(self):
        """Test validation allows None for nullable parameters."""
        manager = ConfigManager()
        is_valid, errors = manager.validate_parameters(random_seed=None)
        assert is_valid
        assert len(errors) == 0

    def test_validate_parameters_multiple_errors(self):
        """Test validation reports multiple errors."""
        manager = ConfigManager()
        is_valid, errors = manager.validate_parameters(num_agents=-5, num_epochs=2000)
        assert not is_valid
        assert len(errors) == 2  # Both parameters invalid

    def test_update_config_valid(self):
        """Test config update with valid parameters."""
        manager = ConfigManager()
        success, errors = manager.update_config(num_agents=50, num_epochs=100)
        assert success
        assert len(errors) == 0
        assert manager.current_config.num_agents == 50
        assert manager.current_config.num_epochs == 100

    def test_update_config_invalid(self):
        """Test config update fails with invalid parameters."""
        manager = ConfigManager()
        original_agents = manager.current_config.num_agents
        success, errors = manager.update_config(num_agents=-10)
        assert not success
        assert len(errors) > 0
        # Config should remain unchanged
        assert manager.current_config.num_agents == original_agents

    def test_update_config_partial(self):
        """Test partial config update only changes specified parameters."""
        manager = ConfigManager()
        manager.get_preset("default")
        original_epochs = manager.current_config.num_epochs

        success, errors = manager.update_config(num_agents=25)
        assert success
        assert manager.current_config.num_agents == 25
        # Other parameters unchanged
        assert manager.current_config.num_epochs == original_epochs

    def test_save_and_load_config(self):
        """Test saving config to file and loading it back."""
        manager = ConfigManager()
        manager.update_config(num_agents=42, num_epochs=99)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test_config.json"

            # Save
            success, errors = manager.save_to_file(str(filepath))
            assert success
            assert len(errors) == 0
            assert filepath.exists()

            # Load into new manager
            manager2 = ConfigManager()
            success, errors = manager2.load_from_file(str(filepath))
            assert success
            assert len(errors) == 0
            assert manager2.current_config.num_agents == 42
            assert manager2.current_config.num_epochs == 99

    def test_load_from_nonexistent_file(self):
        """Test loading from nonexistent file returns error."""
        manager = ConfigManager()
        success, errors = manager.load_from_file("/nonexistent/path/config.json")
        assert not success
        assert len(errors) > 0
        assert "not found" in errors[0]

    def test_load_from_invalid_json(self):
        """Test loading from invalid JSON returns error."""
        manager = ConfigManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ invalid json }")
            filepath = f.name

        try:
            success, errors = manager.load_from_file(filepath)
            assert not success
            assert len(errors) > 0
            assert "Invalid JSON" in errors[0]
        finally:
            Path(filepath).unlink()

    def test_load_config_with_invalid_values(self):
        """Test loading config with invalid values fails validation."""
        manager = ConfigManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"num_agents": -5, "num_epochs": 10}, f)
            filepath = f.name

        try:
            success, errors = manager.load_from_file(filepath)
            assert not success
            assert len(errors) > 0
        finally:
            Path(filepath).unlink()

    def test_to_orchestrator_dict(self):
        """Test conversion to orchestrator format."""
        manager = ConfigManager()
        manager.update_config(num_agents=30, num_epochs=40)

        orch_dict = manager.to_orchestrator_dict()

        assert isinstance(orch_dict, dict)
        assert orch_dict["num_agents"] == 30
        assert orch_dict["num_epochs"] == 40
        assert "random_seed" in orch_dict
        assert "use_semantic" in orch_dict

    def test_get_config_summary(self):
        """Test getting human-readable config summary."""
        manager = ConfigManager()
        manager.update_config(num_agents=100)

        summary = manager.get_config_summary()

        assert isinstance(summary, dict)
        assert summary["num_agents"] == 100
        assert "num_epochs" in summary
        assert "use_gpu" in summary

    def test_float_parameter_validation(self):
        """Test validation of float parameters."""
        manager = ConfigManager()

        # Valid float
        is_valid, errors = manager.validate_parameters(satori_threshold_analyzer=0.85)
        assert is_valid
        assert len(errors) == 0

        # Invalid float (out of range)
        is_valid, errors = manager.validate_parameters(satori_threshold_analyzer=1.5)
        assert not is_valid
        assert "exceeds maximum" in errors[0]

    def test_boolean_parameter_validation(self):
        """Test validation of boolean parameters."""
        manager = ConfigManager()

        # Valid booleans
        is_valid, errors = manager.validate_parameters(use_gpu=True, use_semantic=False)
        assert is_valid
        assert len(errors) == 0

        # Invalid type for boolean
        is_valid, errors = manager.validate_parameters(use_gpu="yes")
        assert not is_valid
        assert "Expected bool" in errors[0]

    def test_unknown_parameters_ignored(self):
        """Test that unknown parameters are ignored during validation."""
        manager = ConfigManager()

        # Unknown parameter should not cause validation failure
        is_valid, errors = manager.validate_parameters(
            num_agents=10, unknown_param="value"
        )
        assert is_valid
        assert len(errors) == 0
