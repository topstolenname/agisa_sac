"""Configuration management for AGI-SAC GUI.

This module handles parameter validation, preset loading, and custom configuration
management for the GUI application.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..config import PRESETS, SimulationConfig, get_preset
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manages simulation configuration with validation and preset support."""

    # Parameter constraints
    CONSTRAINTS = {
        "num_agents": {"min": 1, "max": 1000, "type": int},
        "num_epochs": {"min": 1, "max": 1000, "type": int},
        "agent_capacity": {"min": 10, "max": 1000, "type": int},
        "random_seed": {"min": 0, "max": 2**31 - 1, "type": int, "nullable": True},
        "satori_threshold_analyzer": {"min": 0.0, "max": 1.0, "type": float},
        "tda_max_dimension": {"min": 0, "max": 3, "type": int},
        "community_check_frequency": {"min": 1, "max": 100, "type": int},
        "epoch_log_frequency": {"min": 1, "max": 100, "type": int},
        "use_semantic": {"type": bool},
        "use_gpu": {"type": bool},
    }

    def __init__(self):
        """Initialize ConfigManager with default configuration."""
        self.current_config: Optional[SimulationConfig] = None
        self._load_default_config()

    def _load_default_config(self) -> None:
        """Load the default configuration preset."""
        self.current_config = get_preset("default")
        logger.info("Loaded default configuration")

    def get_preset(self, preset_name: str) -> SimulationConfig:
        """Load a configuration preset by name.

        Args:
            preset_name: Name of the preset (quick_test, default, medium, large)

        Returns:
            SimulationConfig instance

        Raises:
            KeyError: If preset name not found
        """
        try:
            config = get_preset(preset_name)
            self.current_config = config
            logger.info(f"Loaded preset: {preset_name}")
            return config
        except KeyError as e:
            logger.error(f"Invalid preset name: {preset_name}")
            raise e

    def get_available_presets(self) -> List[str]:
        """Get list of available preset names.

        Returns:
            List of preset names
        """
        return list(PRESETS.keys())

    def validate_parameters(self, **kwargs) -> Tuple[bool, List[str]]:
        """Validate simulation parameters against constraints.

        Args:
            **kwargs: Parameter name-value pairs to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        for param_name, value in kwargs.items():
            if param_name not in self.CONSTRAINTS:
                # Unknown parameter, skip validation
                continue

            constraint = self.CONSTRAINTS[param_name]

            # Check if None is allowed
            if value is None:
                if constraint.get("nullable", False):
                    continue
                else:
                    errors.append(f"{param_name}: Cannot be None")
                    continue

            # Type check
            expected_type = constraint["type"]
            if not isinstance(value, expected_type):
                errors.append(
                    f"{param_name}: Expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
                continue

            # Range check for numeric types
            if expected_type in (int, float):
                if "min" in constraint and value < constraint["min"]:
                    errors.append(
                        f"{param_name}: Value {value} is below minimum "
                        f"{constraint['min']}"
                    )
                if "max" in constraint and value > constraint["max"]:
                    errors.append(
                        f"{param_name}: Value {value} exceeds maximum "
                        f"{constraint['max']}"
                    )

        is_valid = len(errors) == 0
        return is_valid, errors

    def update_config(self, **kwargs) -> Tuple[bool, List[str]]:
        """Update current configuration with new parameters.

        Validates parameters before updating. If validation fails, config remains
        unchanged.

        Args:
            **kwargs: Parameters to update

        Returns:
            Tuple of (success, list of error messages)
        """
        is_valid, errors = self.validate_parameters(**kwargs)

        if not is_valid:
            logger.warning(f"Config update validation failed: {errors}")
            return False, errors

        # Update the current config
        if self.current_config is None:
            self._load_default_config()

        # Create a dict from current config
        config_dict = self.current_config.to_dict()

        # Update with new values
        config_dict.update(kwargs)

        # Create new config from updated dict
        try:
            self.current_config = SimulationConfig.from_dict(config_dict)
            logger.info(f"Config updated with parameters: {list(kwargs.keys())}")
            return True, []
        except Exception as e:
            error_msg = f"Failed to update config: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, [error_msg]

    def load_from_file(self, filepath: str) -> Tuple[bool, List[str]]:
        """Load configuration from a JSON file.

        Args:
            filepath: Path to JSON configuration file

        Returns:
            Tuple of (success, list of error messages)
        """
        try:
            path = Path(filepath)
            if not path.exists():
                error_msg = f"Configuration file not found: {filepath}"
                logger.error(error_msg)
                return False, [error_msg]

            with open(path, "r") as f:
                config_dict = json.load(f)

            # Validate loaded config
            is_valid, errors = self.validate_parameters(**config_dict)
            if not is_valid:
                logger.error(f"Loaded config validation failed: {errors}")
                return False, errors

            # Create config from dict
            self.current_config = SimulationConfig.from_dict(config_dict)
            logger.info(f"Loaded configuration from: {filepath}")
            return True, []

        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in config file: {str(e)}"
            logger.error(error_msg)
            return False, [error_msg]
        except Exception as e:
            error_msg = f"Failed to load config file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, [error_msg]

    def save_to_file(self, filepath: str) -> Tuple[bool, List[str]]:
        """Save current configuration to a JSON file.

        Args:
            filepath: Path where to save the configuration

        Returns:
            Tuple of (success, list of error messages)
        """
        if self.current_config is None:
            error_msg = "No configuration to save"
            logger.error(error_msg)
            return False, [error_msg]

        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)

            config_dict = self.current_config.to_dict()

            with open(path, "w") as f:
                json.dump(config_dict, f, indent=2)

            logger.info(f"Saved configuration to: {filepath}")
            return True, []

        except Exception as e:
            error_msg = f"Failed to save config file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, [error_msg]

    def to_orchestrator_dict(self) -> Dict[str, Any]:
        """Convert current configuration to format expected by SimulationOrchestrator.

        Returns:
            Dictionary suitable for SimulationOrchestrator initialization
        """
        if self.current_config is None:
            self._load_default_config()

        return self.current_config.to_dict()

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a human-readable summary of current configuration.

        Returns:
            Dictionary with configuration summary
        """
        if self.current_config is None:
            return {"status": "No configuration loaded"}

        return {
            "num_agents": self.current_config.num_agents,
            "num_epochs": self.current_config.num_epochs,
            "agent_capacity": self.current_config.agent_capacity,
            "use_semantic": self.current_config.use_semantic,
            "use_gpu": self.current_config.use_gpu,
            "random_seed": self.current_config.random_seed,
        }
