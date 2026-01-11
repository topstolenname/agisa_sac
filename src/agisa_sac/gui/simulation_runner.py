"""Simulation execution controller for AGI-SAC GUI.

This module manages background simulation execution with support for
start/pause/resume/stop operations.
"""

from __future__ import annotations

import queue
import threading
import time
from enum import Enum
from typing import Any, Dict, Optional

from ..core.orchestrator import SimulationOrchestrator
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SimulationState(str, Enum):
    """Enum representing simulation execution states."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class SimulationStatus:
    """Container for simulation status information."""

    def __init__(self):
        """Initialize status with idle state."""
        self.state: SimulationState = SimulationState.IDLE
        self.current_epoch: int = 0
        self.total_epochs: int = 0
        self.elapsed_time: float = 0.0
        self.error_message: Optional[str] = None
        self.run_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert status to dictionary format.

        Returns:
            Dictionary representation of status
        """
        return {
            "state": self.state.value,
            "current_epoch": self.current_epoch,
            "total_epochs": self.total_epochs,
            "elapsed_time": self.elapsed_time,
            "error_message": self.error_message,
            "run_id": self.run_id,
        }


class SimulationRunner:
    """Manages simulation execution in background thread with lifecycle control."""

    def __init__(self, metrics_queue: queue.Queue):
        """Initialize SimulationRunner.

        Args:
            metrics_queue: Thread-safe queue for pushing metrics updates
        """
        self.orchestrator: Optional[SimulationOrchestrator] = None
        self.thread: Optional[threading.Thread] = None
        self.status = SimulationStatus()
        self.metrics_queue = metrics_queue
        self._stop_event = threading.Event()
        self._start_time: float = 0.0
        self._lock = threading.Lock()

    def start(self, config: Dict[str, Any]) -> bool:
        """Start a new simulation in background thread.

        Args:
            config: Configuration dictionary for SimulationOrchestrator

        Returns:
            True if simulation started successfully, False otherwise
        """
        with self._lock:
            if self.status.state in (SimulationState.RUNNING, SimulationState.PAUSED):
                logger.warning("Cannot start simulation: already running or paused")
                return False

            try:
                # Reset state
                self._stop_event.clear()
                self.status = SimulationStatus()
                self.status.state = SimulationState.RUNNING
                self.status.total_epochs = config.get("num_epochs", 0)
                # Use high-precision timestamp for unique run_id
                self.status.run_id = f"run_{int(time.time() * 1000)}"

                # Create orchestrator
                logger.info(
                    f"Creating SimulationOrchestrator with "
                    f"{config.get('num_agents')} agents, "
                    f"{config.get('num_epochs')} epochs"
                )
                self.orchestrator = SimulationOrchestrator(config)

                # Start simulation thread
                self.thread = threading.Thread(
                    target=self._run_simulation, daemon=True, name="SimulationThread"
                )
                self._start_time = time.time()
                self.thread.start()

                logger.info(f"Simulation started: {self.status.run_id}")
                return True

            except Exception as e:
                error_msg = f"Failed to start simulation: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.status.state = SimulationState.ERROR
                self.status.error_message = error_msg
                return False

    def pause(self) -> bool:
        """Pause the running simulation.

        Returns:
            True if paused successfully, False otherwise
        """
        with self._lock:
            if self.status.state != SimulationState.RUNNING:
                logger.warning("Cannot pause: simulation not running")
                return False

            if self.orchestrator is None:
                logger.error("Cannot pause: orchestrator is None")
                return False

            try:
                self.orchestrator.is_running = False
                self.status.state = SimulationState.PAUSED
                logger.info("Simulation paused")
                return True
            except Exception as e:
                logger.error(f"Failed to pause simulation: {e}", exc_info=True)
                return False

    def resume(self) -> bool:
        """Resume a paused simulation.

        Returns:
            True if resumed successfully, False otherwise
        """
        with self._lock:
            if self.status.state != SimulationState.PAUSED:
                logger.warning("Cannot resume: simulation not paused")
                return False

            if self.orchestrator is None:
                logger.error("Cannot resume: orchestrator is None")
                return False

            try:
                self.orchestrator.is_running = True
                self.status.state = SimulationState.RUNNING
                logger.info("Simulation resumed")
                return True
            except Exception as e:
                logger.error(f"Failed to resume simulation: {e}", exc_info=True)
                return False

    def stop(self) -> bool:
        """Gracefully stop the simulation.

        Returns:
            True if stopped successfully, False otherwise
        """
        with self._lock:
            if self.status.state not in (
                SimulationState.RUNNING,
                SimulationState.PAUSED,
            ):
                logger.warning("Cannot stop: simulation not running or paused")
                return False

            try:
                self._stop_event.set()
                if self.orchestrator:
                    self.orchestrator.is_running = False
                logger.info("Stop signal sent to simulation")
                return True
            except Exception as e:
                logger.error(f"Failed to stop simulation: {e}", exc_info=True)
                return False

    def get_status(self) -> SimulationStatus:
        """Get current simulation status.

        Returns:
            Current SimulationStatus object
        """
        with self._lock:
            # Update elapsed time if running
            if self.status.state == SimulationState.RUNNING and self._start_time > 0:
                self.status.elapsed_time = time.time() - self._start_time

            # Update current epoch from orchestrator if available
            if self.orchestrator and self.status.state in (
                SimulationState.RUNNING,
                SimulationState.PAUSED,
            ):
                self.status.current_epoch = self.orchestrator.current_epoch

            return self.status

    def get_orchestrator(self) -> Optional[SimulationOrchestrator]:
        """Get the current orchestrator instance.

        Returns:
            SimulationOrchestrator if simulation is active, None otherwise
        """
        return self.orchestrator

    def save_state(self, filepath: str) -> bool:
        """Save current simulation state to file.

        Args:
            filepath: Path where to save the state

        Returns:
            True if saved successfully, False otherwise
        """
        if self.orchestrator is None:
            logger.error("Cannot save state: no active simulation")
            return False

        try:
            success = self.orchestrator.save_state(filepath)
            if success:
                logger.info(f"Simulation state saved to {filepath}")
            return success
        except Exception as e:
            logger.error(f"Failed to save state: {e}", exc_info=True)
            return False

    def load_state(self, filepath: str, config: Dict[str, Any]) -> bool:
        """Load simulation state from file.

        Args:
            filepath: Path to the state file
            config: Base configuration for orchestrator

        Returns:
            True if loaded successfully, False otherwise
        """
        with self._lock:
            if self.status.state in (SimulationState.RUNNING, SimulationState.PAUSED):
                logger.error("Cannot load state: simulation is running")
                return False

            try:
                # Create new orchestrator with config
                self.orchestrator = SimulationOrchestrator(config)

                # Load state
                success = self.orchestrator.load_state(filepath)
                if success:
                    self.status.state = SimulationState.PAUSED
                    self.status.current_epoch = self.orchestrator.current_epoch
                    self.status.total_epochs = self.orchestrator.num_epochs
                    self.status.run_id = f"loaded_{int(time.time())}"
                    logger.info(
                        f"Loaded simulation state from {filepath} "
                        f"at epoch {self.status.current_epoch}"
                    )
                return success
            except Exception as e:
                error_msg = f"Failed to load state: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.status.state = SimulationState.ERROR
                self.status.error_message = error_msg
                return False

    def _run_simulation(self) -> None:
        """Internal method to run simulation in background thread."""
        try:
            logger.info("Simulation thread started")

            if self.orchestrator is None:
                raise RuntimeError("Orchestrator not initialized")

            # Run simulation epoch by epoch with pause/stop support
            # The orchestrator's run_simulation() doesn't support pause,
            # so we need to manually iterate
            start_epoch = self.orchestrator.current_epoch

            for epoch in range(start_epoch, self.orchestrator.num_epochs):
                if self._stop_event.is_set():
                    break

                # Wait while paused
                while (
                    not self.orchestrator.is_running and not self._stop_event.is_set()
                ):
                    time.sleep(0.1)

                if self._stop_event.is_set():
                    break

                # Set current epoch and run it
                # This matches how orchestrator.run_simulation() works
                try:
                    self.orchestrator.current_epoch = epoch
                    self.orchestrator.run_epoch()
                except Exception as e:
                    logger.error(f"Error in epoch {epoch}: {e}")
                    raise

            # Check if completed normally or stopped
            # Update final status
            with self._lock:
                self.status.current_epoch = self.orchestrator.current_epoch
                self.status.elapsed_time = time.time() - self._start_time

                if self._stop_event.is_set():
                    self.status.state = SimulationState.PAUSED
                    logger.info(
                        f"Simulation stopped by user at epoch {self.status.current_epoch}"
                    )
                else:
                    self.status.state = SimulationState.COMPLETED
                    logger.info(
                        f"Simulation completed: {self.status.total_epochs} epochs "
                        f"in {self.status.elapsed_time:.2f}s"
                    )

        except Exception as e:
            error_msg = f"Simulation error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            with self._lock:
                self.status.state = SimulationState.ERROR
                self.status.error_message = error_msg
