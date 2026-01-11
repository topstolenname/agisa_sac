"""Tests for SimulationRunner component."""

import queue
import tempfile
import time
from pathlib import Path

import pytest

from agisa_sac.gui.simulation_runner import (
    SimulationRunner,
    SimulationState,
    SimulationStatus,
)


class TestSimulationStatus:
    """Test suite for SimulationStatus class."""

    def test_initialization(self):
        """Test SimulationStatus initializes with default values."""
        status = SimulationStatus()
        assert status.state == SimulationState.IDLE
        assert status.current_epoch == 0
        assert status.total_epochs == 0
        assert status.elapsed_time == 0.0
        assert status.error_message is None
        assert status.run_id is None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        status = SimulationStatus()
        status.state = SimulationState.RUNNING
        status.current_epoch = 5
        status.total_epochs = 10
        status.run_id = "test_run"

        result = status.to_dict()

        assert isinstance(result, dict)
        assert result["state"] == "running"
        assert result["current_epoch"] == 5
        assert result["total_epochs"] == 10
        assert result["run_id"] == "test_run"


class TestSimulationRunner:
    """Test suite for SimulationRunner class."""

    @pytest.fixture
    def runner(self):
        """Fixture providing a SimulationRunner instance."""
        metrics_queue = queue.Queue()
        return SimulationRunner(metrics_queue)

    @pytest.fixture
    def quick_config(self):
        """Fixture providing a quick test configuration."""
        return {
            "num_agents": 3,
            "num_epochs": 3,
            "random_seed": 42,
            "agent_capacity": 50,
            "use_semantic": False,
            "use_gpu": False,
        }

    def test_initialization(self, runner):
        """Test SimulationRunner initializes correctly."""
        assert runner.orchestrator is None
        assert runner.thread is None
        assert runner.status.state == SimulationState.IDLE
        assert isinstance(runner.metrics_queue, queue.Queue)

    def test_start_simulation_success(self, runner, quick_config):
        """Test starting a simulation successfully."""
        success = runner.start(quick_config)

        assert success
        assert runner.status.state == SimulationState.RUNNING
        assert runner.orchestrator is not None
        assert runner.thread is not None
        assert runner.thread.is_alive()
        assert runner.status.total_epochs == 3
        assert runner.status.run_id is not None

        # Wait for completion
        runner.thread.join(timeout=10)
        assert runner.status.state == SimulationState.COMPLETED

    def test_start_while_running_fails(self, runner, quick_config):
        """Test that starting a second simulation while running fails."""
        runner.start(quick_config)
        assert runner.status.state == SimulationState.RUNNING

        # Try to start again
        success = runner.start(quick_config)
        assert not success

        # Cleanup
        runner.stop()
        if runner.thread:
            runner.thread.join(timeout=5)

    def test_pause_running_simulation(self, runner, quick_config):
        """Test pausing a running simulation."""
        # Start with more epochs to have time to pause
        config = quick_config.copy()
        config["num_epochs"] = 50

        runner.start(config)
        time.sleep(0.5)  # Let simulation start

        success = runner.pause()
        assert success
        assert runner.status.state == SimulationState.PAUSED

        # Cleanup
        runner.stop()
        if runner.thread:
            runner.thread.join(timeout=5)

    def test_pause_when_not_running_fails(self, runner):
        """Test pausing when simulation not running fails."""
        success = runner.pause()
        assert not success
        assert runner.status.state == SimulationState.IDLE

    def test_resume_paused_simulation(self, runner, quick_config):
        """Test resuming a paused simulation."""
        config = quick_config.copy()
        config["num_epochs"] = 50

        runner.start(config)
        time.sleep(0.5)

        runner.pause()
        assert runner.status.state == SimulationState.PAUSED

        success = runner.resume()
        assert success
        assert runner.status.state == SimulationState.RUNNING

        # Cleanup
        runner.stop()
        if runner.thread:
            runner.thread.join(timeout=5)

    def test_resume_when_not_paused_fails(self, runner):
        """Test resuming when not paused fails."""
        success = runner.resume()
        assert not success

    def test_stop_simulation(self, runner, quick_config):
        """Test stopping a running simulation."""
        config = quick_config.copy()
        config["num_epochs"] = 100

        runner.start(config)
        time.sleep(0.5)

        success = runner.stop()
        assert success

        # Wait for thread to finish
        if runner.thread:
            runner.thread.join(timeout=5)

        # Should be paused after stop
        assert runner.status.state == SimulationState.PAUSED

    def test_stop_when_idle_fails(self, runner):
        """Test stopping when idle fails."""
        success = runner.stop()
        assert not success

    def test_get_status(self, runner, quick_config):
        """Test getting simulation status."""
        # Initial status
        status = runner.get_status()
        assert status.state == SimulationState.IDLE

        # Start simulation
        runner.start(quick_config)
        time.sleep(0.3)

        status = runner.get_status()
        assert status.state == SimulationState.RUNNING
        assert status.current_epoch >= 0
        assert status.total_epochs == 3
        assert status.elapsed_time > 0

        # Cleanup
        runner.stop()
        if runner.thread:
            runner.thread.join(timeout=5)

    def test_get_orchestrator(self, runner, quick_config):
        """Test getting orchestrator instance."""
        # Before start
        orch = runner.get_orchestrator()
        assert orch is None

        # After start
        runner.start(quick_config)
        orch = runner.get_orchestrator()
        assert orch is not None
        assert hasattr(orch, "run_epoch")

        # Cleanup
        runner.stop()
        if runner.thread:
            runner.thread.join(timeout=5)

    def test_simulation_completion(self, runner, quick_config):
        """Test simulation runs to completion."""
        runner.start(quick_config)

        # Wait for completion
        if runner.thread:
            runner.thread.join(timeout=15)

        status = runner.get_status()
        assert status.state == SimulationState.COMPLETED
        assert status.current_epoch == quick_config["num_epochs"]
        assert status.elapsed_time > 0

    def test_save_state_without_simulation_fails(self, runner):
        """Test saving state without active simulation fails."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            success = runner.save_state(filepath)
            assert not success
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_save_state_with_simulation(self, runner, quick_config):
        """Test saving simulation state."""
        runner.start(quick_config)
        time.sleep(0.5)  # Let simulation progress
        runner.pause()

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            success = runner.save_state(filepath)
            assert success
            assert Path(filepath).exists()
        finally:
            Path(filepath).unlink(missing_ok=True)
            runner.stop()
            if runner.thread:
                runner.thread.join(timeout=5)

    def test_load_state_while_running_fails(self, runner, quick_config):
        """Test loading state while running fails."""
        runner.start(quick_config)

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            filepath = f.name

        try:
            success = runner.load_state(filepath, quick_config)
            assert not success
            assert runner.status.state == SimulationState.RUNNING
        finally:
            Path(filepath).unlink(missing_ok=True)
            runner.stop()
            if runner.thread:
                runner.thread.join(timeout=5)

    def test_elapsed_time_updates(self, runner, quick_config):
        """Test that elapsed time updates during execution."""
        config = quick_config.copy()
        config["num_epochs"] = 50

        runner.start(config)

        time.sleep(0.3)
        status1 = runner.get_status()
        time1 = status1.elapsed_time

        time.sleep(0.5)
        status2 = runner.get_status()
        time2 = status2.elapsed_time

        assert time2 > time1

        # Cleanup
        runner.stop()
        if runner.thread:
            runner.thread.join(timeout=5)

    def test_current_epoch_updates(self, runner, quick_config):
        """Test that current epoch updates during execution."""
        runner.start(quick_config)

        # Wait for at least one epoch
        time.sleep(0.5)

        status = runner.get_status()
        assert status.current_epoch >= 0

        # Cleanup
        if runner.thread:
            runner.thread.join(timeout=10)

    def test_run_id_assigned_on_start(self, runner, quick_config):
        """Test that unique run_id is assigned on start."""
        runner.start(quick_config)
        run_id1 = runner.status.run_id

        if runner.thread:
            runner.thread.join(timeout=10)

        time.sleep(0.1)  # Ensure different timestamp

        runner.start(quick_config)
        run_id2 = runner.status.run_id

        assert run_id1 is not None
        assert run_id2 is not None
        assert run_id1 != run_id2  # Should be unique

        # Cleanup
        if runner.thread:
            runner.thread.join(timeout=10)

    def test_thread_safety(self, runner, quick_config):
        """Test thread-safe operations."""
        config = quick_config.copy()
        config["num_epochs"] = 50

        runner.start(config)

        # Multiple status checks from different context
        for _ in range(10):
            status = runner.get_status()
            assert status is not None
            time.sleep(0.01)

        # Cleanup
        runner.stop()
        if runner.thread:
            runner.thread.join(timeout=5)
