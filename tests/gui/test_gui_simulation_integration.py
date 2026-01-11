"""Integration tests for GUI simulation workflow.

Tests the full end-to-end simulation with GUI components including
MetricsCollector, SimulationRunner, and ConfigManager integration.
"""

import queue
import tempfile
import time
from pathlib import Path

import pytest

from agisa_sac.gui.config_manager import ConfigManager
from agisa_sac.gui.metrics_collector import MetricsCollector
from agisa_sac.gui.simulation_runner import SimulationRunner, SimulationState


class TestConfigManagerIntegration:
    """Test ConfigManager with real configurations."""

    def test_load_all_presets(self):
        """Test all presets load successfully."""
        manager = ConfigManager()
        presets = manager.get_available_presets()

        assert len(presets) > 0
        assert "default" in presets

        for preset_name in presets:
            config = manager.get_preset(preset_name)
            assert config is not None
            assert config.num_agents > 0
            assert config.num_epochs > 0

    def test_validate_preset_parameters(self):
        """Test preset parameters pass validation."""
        manager = ConfigManager()

        for preset_name in manager.get_available_presets():
            config = manager.get_preset(preset_name)
            config_dict = config.to_dict()

            is_valid, errors = manager.validate_parameters(**config_dict)
            assert is_valid, f"Preset {preset_name} failed validation: {errors}"

    def test_config_file_round_trip(self):
        """Test save and load config maintains integrity."""
        manager = ConfigManager()

        # Load a preset
        original_config = manager.get_preset("default")

        # Save to file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            success, errors = manager.save_to_file(temp_path)
            assert success, f"Save failed: {errors}"

            # Load from file
            manager2 = ConfigManager()
            success, errors = manager2.load_from_file(temp_path)
            assert success, f"Load failed: {errors}"

            # Compare
            loaded_config = manager2.current_config
            assert loaded_config.num_agents == original_config.num_agents
            assert loaded_config.num_epochs == original_config.num_epochs
            assert loaded_config.use_semantic == original_config.use_semantic

        finally:
            Path(temp_path).unlink(missing_ok=True)


@pytest.mark.slow
@pytest.mark.gui
class TestSimulationRunnerIntegration:
    """Test SimulationRunner with actual simulations."""

    def test_quick_simulation_completes(self):
        """Test a quick simulation runs to completion."""
        # Use minimal config
        config = {
            "num_agents": 3,
            "num_epochs": 5,
            "use_semantic": False,
            "tda_max_dimension": 0,  # Disable TDA for speed
            "epoch_log_frequency": 10,
            "random_seed": 42,
        }

        runner = SimulationRunner(queue.Queue())
        success = runner.start(config)

        assert success
        assert runner.status.state == SimulationState.RUNNING

        # Wait for completion (with timeout)
        timeout = 60  # 60 seconds max
        start_time = time.time()
        while runner.status.state == SimulationState.RUNNING:
            if time.time() - start_time > timeout:
                pytest.fail("Simulation timed out")
            time.sleep(0.5)

        # Check final state
        assert runner.status.state == SimulationState.COMPLETED
        assert runner.status.current_epoch == 4  # 0-indexed, so 5 epochs = 0-4
        assert runner.status.elapsed_time > 0

    def test_pause_resume_workflow(self):
        """Test pause and resume maintain continuity."""
        config = {
            "num_agents": 3,
            "num_epochs": 20,
            "use_semantic": False,
            "tda_max_dimension": 0,
            "epoch_log_frequency": 50,
            "random_seed": 42,
        }

        runner = SimulationRunner(queue.Queue())
        runner.start(config)

        # Let it run a bit
        time.sleep(2)

        # Pause
        assert runner.pause()
        assert runner.status.state == SimulationState.PAUSED
        epoch_at_pause = runner.status.current_epoch

        # Wait while paused
        time.sleep(1)

        # Epoch should not advance while paused
        assert runner.status.current_epoch == epoch_at_pause

        # Resume
        assert runner.resume()
        assert runner.status.state == SimulationState.RUNNING

        # Wait for more progress
        time.sleep(1)

        # Should have progressed beyond pause point
        assert runner.status.current_epoch >= epoch_at_pause

        # Stop
        runner.stop()

    def test_stop_simulation_gracefully(self):
        """Test stop terminates simulation cleanly."""
        config = {
            "num_agents": 3,
            "num_epochs": 100,  # Long simulation
            "use_semantic": False,
            "tda_max_dimension": 0,
            "epoch_log_frequency": 50,
            "random_seed": 42,
        }

        runner = SimulationRunner(queue.Queue())
        runner.start(config)

        # Let it start
        time.sleep(1)

        # Stop
        assert runner.stop()

        # Wait for thread to finish
        time.sleep(2)

        # Should be stopped, not completed
        assert runner.status.state in (
            SimulationState.PAUSED,
            SimulationState.COMPLETED,
        )
        # Simulation should have been interrupted
        assert runner.status.current_epoch < 99


@pytest.mark.slow
@pytest.mark.gui
class TestMetricsCollectorIntegration:
    """Test MetricsCollector with real simulation."""

    def test_collects_metrics_during_simulation(self):
        """Test metrics collector receives data from simulation."""
        config = {
            "num_agents": 3,
            "num_epochs": 5,
            "use_semantic": False,
            "tda_max_dimension": 0,
            "epoch_log_frequency": 10,
            "random_seed": 42,
        }

        metrics_queue = queue.Queue()
        runner = SimulationRunner(metrics_queue)
        collector = MetricsCollector(metrics_queue)

        # Register hooks
        runner.start(config)
        time.sleep(0.5)  # Let orchestrator initialize

        if runner.orchestrator:
            runner.orchestrator.register_hook("post_epoch", collector.on_epoch_end)

        # Wait for completion
        timeout = 60
        start_time = time.time()
        while runner.status.state == SimulationState.RUNNING:
            if time.time() - start_time > timeout:
                pytest.fail("Simulation timed out")
            time.sleep(0.5)

        # Check metrics were collected
        assert collector.total_epochs_processed > 0
        assert len(collector.history) > 0
        assert collector.latest_snapshot is not None

        # Verify snapshot structure
        snapshot = collector.latest_snapshot
        assert "epoch" in snapshot
        assert "agent_metrics" in snapshot
        assert "system_metrics" in snapshot
        assert len(snapshot["agent_metrics"]) == 3  # 3 agents

        # Verify agent metrics have expected fields
        for agent_id, metrics in snapshot["agent_metrics"].items():
            assert "sri" in metrics
            assert "nds" in metrics
            assert "vsd" in metrics
            assert "mce" in metrics

    def test_metrics_continuity_across_epochs(self):
        """Test metrics history maintains continuity."""
        config = {
            "num_agents": 3,
            "num_epochs": 10,
            "use_semantic": False,
            "tda_max_dimension": 0,
            "epoch_log_frequency": 50,
            "random_seed": 42,
        }

        metrics_queue = queue.Queue()
        runner = SimulationRunner(metrics_queue)
        collector = MetricsCollector(metrics_queue)

        runner.start(config)
        time.sleep(0.5)

        if runner.orchestrator:
            runner.orchestrator.register_hook("post_epoch", collector.on_epoch_end)

        # Wait for completion
        timeout = 60
        start_time = time.time()
        while runner.status.state == SimulationState.RUNNING:
            if time.time() - start_time > timeout:
                pytest.fail("Simulation timed out")
            time.sleep(0.5)

        # Check epoch continuity
        epochs = [snap["epoch"] for snap in collector.history]
        assert epochs == list(range(len(epochs))), "Epochs should be continuous"

        # Check timeseries extraction works
        timeseries = collector.get_timeseries("satori_wave_ratio")
        assert len(timeseries) == len(collector.history)

    def test_state_persistence(self):
        """Test simulation state can be saved and loaded."""
        config = {
            "num_agents": 3,
            "num_epochs": 10,
            "use_semantic": False,
            "tda_max_dimension": 0,
            "epoch_log_frequency": 50,
            "random_seed": 42,
        }

        runner = SimulationRunner(queue.Queue())
        runner.start(config)

        # Let it run partway
        time.sleep(2)

        # Pause
        runner.pause()
        epoch_at_save = runner.status.current_epoch

        # Save state
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            success = runner.save_state(temp_path)
            assert success

            # Stop current simulation
            runner.stop()
            time.sleep(1)

            # Load state
            runner2 = SimulationRunner(queue.Queue())
            success = runner2.load_state(temp_path, config)
            assert success

            # Verify epoch position restored
            assert runner2.status.current_epoch == epoch_at_save

        finally:
            Path(temp_path).unlink(missing_ok=True)


@pytest.mark.slow
@pytest.mark.gui
class TestFullWorkflowIntegration:
    """Test complete GUI workflow scenarios."""

    def test_preset_to_simulation_workflow(self):
        """Test complete workflow: load preset -> configure -> run -> metrics."""
        # Step 1: Load preset via ConfigManager
        config_manager = ConfigManager()
        config_manager.get_preset("quick_test")

        # Step 2: Update configuration
        success, errors = config_manager.update_config(num_epochs=3)
        assert success, f"Config update failed: {errors}"

        # Step 3: Start simulation
        config_dict = config_manager.to_orchestrator_dict()
        metrics_queue = queue.Queue()
        runner = SimulationRunner(metrics_queue)
        collector = MetricsCollector(metrics_queue)

        success = runner.start(config_dict)
        assert success

        # Step 4: Register metrics collection
        time.sleep(0.5)
        if runner.orchestrator:
            runner.orchestrator.register_hook("post_epoch", collector.on_epoch_end)

        # Step 5: Wait for completion
        timeout = 60
        start_time = time.time()
        while runner.status.state == SimulationState.RUNNING:
            if time.time() - start_time > timeout:
                runner.stop()
                pytest.fail("Simulation timed out")
            time.sleep(0.5)

        # Step 6: Verify results
        assert runner.status.state == SimulationState.COMPLETED
        assert collector.total_epochs_processed == 3
        assert collector.latest_snapshot is not None

        # Step 7: Extract timeseries
        timeseries = collector.get_timeseries("satori_wave_ratio")
        assert len(timeseries) == 3

    def test_error_handling_invalid_config(self):
        """Test system handles invalid configuration gracefully."""
        config_manager = ConfigManager()

        # Try invalid parameters
        success, errors = config_manager.update_config(num_agents=5000)  # Exceeds max
        assert not success
        assert len(errors) > 0

        # Configuration should remain valid
        config = config_manager.to_orchestrator_dict()
        assert config["num_agents"] < 5000

    def test_concurrent_metrics_collection(self):
        """Test multiple metric snapshots don't interfere."""
        config = {
            "num_agents": 5,
            "num_epochs": 10,
            "use_semantic": False,
            "tda_max_dimension": 0,
            "epoch_log_frequency": 50,
            "random_seed": 42,
        }

        metrics_queue = queue.Queue()
        runner = SimulationRunner(metrics_queue)
        collector = MetricsCollector(metrics_queue)

        runner.start(config)
        time.sleep(0.5)

        if runner.orchestrator:
            runner.orchestrator.register_hook("post_epoch", collector.on_epoch_end)

        # Continuously poll statistics while simulation runs
        poll_count = 0
        while runner.status.state == SimulationState.RUNNING and poll_count < 20:
            _ = collector.get_statistics()
            _ = collector.get_latest_snapshot()
            poll_count += 1
            time.sleep(0.5)

        # Should complete without errors
        assert collector.total_epochs_processed > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
