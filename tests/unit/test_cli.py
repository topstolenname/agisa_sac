"""Tests for the CLI module (agisa_sac.cli)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock, patch

import pytest

from agisa_sac.cli import list_presets, main, run_simulation

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture


class TestListPresets:
    """Tests for list_presets() function."""

    def test_list_presets_output(self, capsys: CaptureFixture) -> None:
        """Test that list_presets displays all available presets."""
        list_presets()

        captured = capsys.readouterr()
        output = captured.out

        # Check header
        assert "Available configuration presets:" in output

        # Check that known presets appear
        assert "default" in output
        assert "quick_test" in output
        assert "medium" in output

        # Check usage hint
        assert "Usage: agisa-sac run --preset <name>" in output

    def test_list_presets_format(self, capsys: CaptureFixture) -> None:
        """Test that preset output includes agent and epoch counts."""
        list_presets()

        captured = capsys.readouterr()
        output = captured.out

        # Should show "N agents, M epochs" for each preset
        assert "agents" in output
        assert "epochs" in output


class TestRunSimulation:
    """Tests for run_simulation() function."""

    def test_config_file_not_found(self, capsys: CaptureFixture, tmp_path: Path) -> None:
        """Test error handling when config file doesn't exist."""
        args = argparse.Namespace(
            config=str(tmp_path / "nonexistent.json"),
            preset=None,
            gpu=False,
            agents=None,
            epochs=None,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Config file not found" in captured.err

    def test_config_file_invalid_json(
        self, capsys: CaptureFixture, tmp_path: Path
    ) -> None:
        """Test error handling when config file contains invalid JSON."""
        config_path = tmp_path / "bad_config.json"
        config_path.write_text("not valid json {{{")

        args = argparse.Namespace(
            config=str(config_path),
            preset=None,
            gpu=False,
            agents=None,
            epochs=None,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error loading config" in captured.err

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_config_file_success(
        self,
        mock_orchestrator_class: Mock,
        capsys: CaptureFixture,
        tmp_path: Path,
    ) -> None:
        """Test successful config file loading and simulation run."""
        # Create valid config file
        config_path = tmp_path / "config.json"
        config_data = {
            "version": "1.0.0",
            "num_agents": 5,
            "num_epochs": 3,
            "use_gpu": False,
            "random_seed": 42,
        }
        config_path.write_text(json.dumps(config_data))

        # Mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.analyzer.summarize.return_value = "Test summary"
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=str(config_path),
            preset=None,
            gpu=False,
            agents=None,
            epochs=None,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 0
        mock_orchestrator.run_simulation.assert_called_once()
        captured = capsys.readouterr()
        assert "Loaded configuration from:" in captured.out
        assert "SIMULATION COMPLETE" in captured.out

    def test_preset_invalid(self, capsys: CaptureFixture) -> None:
        """Test error handling for invalid preset name."""
        args = argparse.Namespace(
            config=None,
            preset="nonexistent_preset",
            gpu=False,
            agents=None,
            epochs=None,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error:" in captured.err

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_preset_success(
        self, mock_orchestrator_class: Mock, capsys: CaptureFixture
    ) -> None:
        """Test successful preset loading and simulation run."""
        # Mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.analyzer.summarize.return_value = "Test summary"
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=None,
            preset="quick_test",
            gpu=False,
            agents=None,
            epochs=None,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 0
        mock_orchestrator.run_simulation.assert_called_once()
        captured = capsys.readouterr()
        assert "Using preset: quick_test" in captured.out

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_default_preset(
        self, mock_orchestrator_class: Mock, capsys: CaptureFixture
    ) -> None:
        """Test using default preset when no config or preset specified."""
        # Mock orchestrator
        mock_orchestrator = MagicMock()
        mock_orchestrator.analyzer.summarize.return_value = "Test summary"
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=None,
            preset=None,
            gpu=False,
            agents=None,
            epochs=None,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Using default configuration" in captured.out

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_gpu_override(
        self, mock_orchestrator_class: Mock, capsys: CaptureFixture
    ) -> None:
        """Test GPU flag overrides config."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.analyzer.summarize.return_value = "Test summary"
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=None,
            preset="quick_test",
            gpu=True,
            agents=None,
            epochs=None,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "GPU acceleration enabled" in captured.out

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_agents_override(
        self, mock_orchestrator_class: Mock, capsys: CaptureFixture
    ) -> None:
        """Test agents override."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.analyzer.summarize.return_value = "Test summary"
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=None,
            preset="quick_test",
            gpu=False,
            agents=10,
            epochs=None,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Overriding num_agents: 10" in captured.out

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_epochs_override(
        self, mock_orchestrator_class: Mock, capsys: CaptureFixture
    ) -> None:
        """Test epochs override."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.analyzer.summarize.return_value = "Test summary"
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=None,
            preset="quick_test",
            gpu=False,
            agents=None,
            epochs=5,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Overriding num_epochs: 5" in captured.out

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_seed_override(
        self, mock_orchestrator_class: Mock, capsys: CaptureFixture
    ) -> None:
        """Test random seed override."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.analyzer.summarize.return_value = "Test summary"
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=None,
            preset="quick_test",
            gpu=False,
            agents=None,
            epochs=None,
            seed=12345,
            verbose=False,
        )

        exit_code = run_simulation(args)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "Using random seed: 12345" in captured.out

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_simulation_exception_verbose(
        self, mock_orchestrator_class: Mock, capsys: CaptureFixture
    ) -> None:
        """Test error handling during simulation with verbose mode."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.run_simulation.side_effect = Exception("Test error")
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=None,
            preset="quick_test",
            gpu=False,
            agents=None,
            epochs=None,
            seed=None,
            verbose=True,
        )

        exit_code = run_simulation(args)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error during simulation: Test error" in captured.err

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_lazy_import(self, mock_orchestrator_class: Mock) -> None:
        """Test that SimulationOrchestrator is lazily imported."""
        # The import happens inside run_simulation, not at module level
        # This test verifies we can call run_simulation without import errors
        mock_orchestrator = MagicMock()
        mock_orchestrator.analyzer.summarize.return_value = "Test summary"
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=None,
            preset="quick_test",
            gpu=False,
            agents=None,
            epochs=None,
            seed=None,
            verbose=False,
        )

        exit_code = run_simulation(args)

        # Should complete successfully
        assert exit_code == 0

    @patch("agisa_sac.core.orchestrator.SimulationOrchestrator")
    def test_log_file_attribute(
        self, mock_orchestrator_class: Mock, capsys: CaptureFixture
    ) -> None:
        """Test log_file attribute handling."""
        mock_orchestrator = MagicMock()
        mock_orchestrator.analyzer.summarize.return_value = "Test summary"
        mock_orchestrator_class.return_value = mock_orchestrator

        args = argparse.Namespace(
            config=None,
            preset="quick_test",
            gpu=False,
            agents=None,
            epochs=None,
            seed=None,
            verbose=False,
            log_file="/tmp/test.log",
        )

        exit_code = run_simulation(args)

        assert exit_code == 0


class TestMain:
    """Tests for main() CLI entry point."""

    def test_version_argument(self, capsys: CaptureFixture) -> None:
        """Test --version argument."""
        with pytest.raises(SystemExit) as exc_info:
            with patch.object(sys, "argv", ["agisa-sac", "--version"]):
                main()

        # argparse exits with 0 for --version
        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        # Should print version string
        assert "agisa-sac" in captured.out

    def test_no_command_shows_help(self, capsys: CaptureFixture) -> None:
        """Test that no command shows help and returns 1."""
        with patch.object(sys, "argv", ["agisa-sac"]):
            exit_code = main()

        assert exit_code == 1
        captured = capsys.readouterr()
        # Should show help
        assert "usage:" in captured.out or "Usage:" in captured.out

    @patch("agisa_sac.cli.list_presets")
    def test_list_presets_command(self, mock_list_presets: Mock) -> None:
        """Test list-presets command routes correctly."""
        with patch.object(sys, "argv", ["agisa-sac", "list-presets"]):
            exit_code = main()

        assert exit_code == 0
        mock_list_presets.assert_called_once()

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_preset(self, mock_run_simulation: Mock) -> None:
        """Test run command with preset."""
        mock_run_simulation.return_value = 0

        with patch.object(sys, "argv", ["agisa-sac", "run", "--preset", "quick_test"]):
            exit_code = main()

        assert exit_code == 0
        mock_run_simulation.assert_called_once()
        args = mock_run_simulation.call_args[0][0]
        assert args.preset == "quick_test"

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_config(self, mock_run_simulation: Mock) -> None:
        """Test run command with config file."""
        mock_run_simulation.return_value = 0

        with patch.object(
            sys, "argv", ["agisa-sac", "run", "--config", "/path/to/config.json"]
        ):
            exit_code = main()

        assert exit_code == 0
        mock_run_simulation.assert_called_once()
        args = mock_run_simulation.call_args[0][0]
        assert args.config == "/path/to/config.json"

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_gpu_flag(self, mock_run_simulation: Mock) -> None:
        """Test run command with GPU flag."""
        mock_run_simulation.return_value = 0

        with patch.object(
            sys, "argv", ["agisa-sac", "run", "--preset", "quick_test", "--gpu"]
        ):
            exit_code = main()

        assert exit_code == 0
        args = mock_run_simulation.call_args[0][0]
        assert args.gpu is True

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_agents_override(
        self, mock_run_simulation: Mock
    ) -> None:
        """Test run command with agents override."""
        mock_run_simulation.return_value = 0

        with patch.object(
            sys, "argv", ["agisa-sac", "run", "--preset", "quick_test", "--agents", "10"]
        ):
            exit_code = main()

        assert exit_code == 0
        args = mock_run_simulation.call_args[0][0]
        assert args.agents == 10

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_epochs_override(
        self, mock_run_simulation: Mock
    ) -> None:
        """Test run command with epochs override."""
        mock_run_simulation.return_value = 0

        with patch.object(
            sys, "argv", ["agisa-sac", "run", "--preset", "quick_test", "--epochs", "5"]
        ):
            exit_code = main()

        assert exit_code == 0
        args = mock_run_simulation.call_args[0][0]
        assert args.epochs == 5

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_seed(self, mock_run_simulation: Mock) -> None:
        """Test run command with random seed."""
        mock_run_simulation.return_value = 0

        with patch.object(
            sys, "argv", ["agisa-sac", "run", "--preset", "quick_test", "--seed", "42"]
        ):
            exit_code = main()

        assert exit_code == 0
        args = mock_run_simulation.call_args[0][0]
        assert args.seed == 42

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_verbose(self, mock_run_simulation: Mock) -> None:
        """Test run command with verbose flag."""
        mock_run_simulation.return_value = 0

        with patch.object(
            sys, "argv", ["agisa-sac", "run", "--preset", "quick_test", "--verbose"]
        ):
            exit_code = main()

        assert exit_code == 0
        args = mock_run_simulation.call_args[0][0]
        assert args.verbose is True

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_log_level(self, mock_run_simulation: Mock) -> None:
        """Test run command with log level."""
        mock_run_simulation.return_value = 0

        with patch.object(
            sys,
            "argv",
            ["agisa-sac", "run", "--preset", "quick_test", "--log-level", "DEBUG"],
        ):
            exit_code = main()

        assert exit_code == 0
        args = mock_run_simulation.call_args[0][0]
        assert args.log_level == "DEBUG"

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_log_file(self, mock_run_simulation: Mock) -> None:
        """Test run command with log file."""
        mock_run_simulation.return_value = 0

        with patch.object(
            sys,
            "argv",
            [
                "agisa-sac",
                "run",
                "--preset",
                "quick_test",
                "--log-file",
                "/tmp/test.log",
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        args = mock_run_simulation.call_args[0][0]
        assert args.log_file == "/tmp/test.log"

    @patch("agisa_sac.cli.run_simulation")
    def test_run_command_with_json_logs(self, mock_run_simulation: Mock) -> None:
        """Test run command with JSON logs flag."""
        mock_run_simulation.return_value = 0

        with patch.object(
            sys,
            "argv",
            ["agisa-sac", "run", "--preset", "quick_test", "--json-logs"],
        ):
            exit_code = main()

        assert exit_code == 0
        args = mock_run_simulation.call_args[0][0]
        assert args.json_logs is True

    @patch("agisa_sac.cli.convert_transcript")
    def test_convert_transcript_command(self, mock_convert: Mock) -> None:
        """Test convert-transcript command routes correctly."""
        mock_convert.return_value = 0

        with patch.object(
            sys,
            "argv",
            [
                "agisa-sac",
                "convert-transcript",
                "--input",
                "input.json",
                "--output",
                "output.json",
            ],
        ):
            exit_code = main()

        assert exit_code == 0
        mock_convert.assert_called_once()
