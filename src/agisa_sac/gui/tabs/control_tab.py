"""Control tab for AGI-SAC GUI.

Provides simulation lifecycle controls (start/pause/resume/stop) and status monitoring.
"""

import queue
from typing import Any

import gradio as gr

from ...gui.config_manager import ConfigManager
from ...gui.simulation_runner import SimulationRunner
from ...utils.logger import get_logger

logger = get_logger(__name__)


def create_control_tab(config_manager: ConfigManager) -> tuple[gr.Tab, dict[str, Any]]:
    """Create the control tab with simulation controls.

    Args:
        config_manager: ConfigManager instance

    Returns:
        Tuple of (Tab component, dict of component references)
    """
    components = {}

    with gr.Tab("Control") as tab:
        gr.Markdown("## Simulation Control")
        gr.Markdown("Start, pause, resume, or stop simulations.")

        # Simulation state (stored in Gradio state)
        runner_state = gr.State(None)
        components["runner_state"] = runner_state

        # Control buttons
        with gr.Row():
            start_btn = gr.Button("▶️ Start Simulation", variant="primary", size="lg")
            pause_btn = gr.Button("⏸️ Pause", variant="secondary", interactive=False)
            resume_btn = gr.Button("▶️ Resume", variant="secondary", interactive=False)
            stop_btn = gr.Button("⏹️ Stop", variant="stop", interactive=False)

        components["start_btn"] = start_btn
        components["pause_btn"] = pause_btn
        components["resume_btn"] = resume_btn
        components["stop_btn"] = stop_btn

        # Status display
        with gr.Group():
            gr.Markdown("### Status")

            status_text = gr.Markdown(
                value="**State:** IDLE\n\n" "Ready to start simulation."
            )

            _ = gr.Progress()  # Progress bar available to Gradio context

            with gr.Row():
                epoch_display = gr.Textbox(
                    label="Current Epoch", value="0 / 0", interactive=False
                )
                elapsed_time_display = gr.Textbox(
                    label="Elapsed Time (s)", value="0.0", interactive=False
                )

        components["status_text"] = status_text
        components["epoch_display"] = epoch_display
        components["elapsed_time_display"] = elapsed_time_display

        # Quick metrics
        with gr.Group():
            gr.Markdown("### Quick Metrics")

            with gr.Row():
                agent_count_display = gr.Number(
                    label="Agent Count", value=0, interactive=False
                )
                satori_ratio_display = gr.Number(
                    label="Satori Wave Ratio", value=0.0, interactive=False, precision=3
                )

        components["agent_count_display"] = agent_count_display
        components["satori_ratio_display"] = satori_ratio_display

        # Logs viewer
        with gr.Accordion("Logs", open=False):
            logs_display = gr.Textbox(
                label="Recent Logs", value="", lines=15, max_lines=20, interactive=False
            )

        components["logs_display"] = logs_display

    # Event handlers
    def start_simulation(runner, config_dict_placeholder):
        """Start a new simulation."""
        if runner is not None:
            return {
                status_text: gr.update(value="❌ Simulation already running!"),
            }

        try:
            # Get config from config_manager
            config_dict = config_manager.to_orchestrator_dict()

            # Create new runner
            metrics_queue = queue.Queue(maxsize=1000)
            new_runner = SimulationRunner(metrics_queue)

            # Start simulation
            success = new_runner.start(config_dict)

            if success:
                logger.info("Simulation started successfully")
                return {
                    runner_state: new_runner,
                    status_text: gr.update(
                        value="**State:** RUNNING\n\n" "Simulation is now running..."
                    ),
                    start_btn: gr.update(interactive=False),
                    pause_btn: gr.update(interactive=True),
                    stop_btn: gr.update(interactive=True),
                }
            else:
                logger.error("Failed to start simulation")
                return {
                    status_text: gr.update(value="❌ Failed to start simulation"),
                }

        except Exception as e:
            logger.error(f"Error starting simulation: {e}", exc_info=True)
            return {
                status_text: gr.update(value=f"❌ Error: {str(e)}"),
            }

    def pause_simulation(runner):
        """Pause the running simulation."""
        if runner is None:
            return {status_text: gr.update(value="❌ No simulation running")}

        try:
            success = runner.pause()
            if success:
                return {
                    status_text: gr.update(
                        value="**State:** PAUSED\n\n" "Simulation paused."
                    ),
                    pause_btn: gr.update(interactive=False),
                    resume_btn: gr.update(interactive=True),
                }
            else:
                return {status_text: gr.update(value="❌ Failed to pause")}
        except Exception as e:
            logger.error(f"Error pausing: {e}")
            return {status_text: gr.update(value=f"❌ Error: {str(e)}")}

    def resume_simulation(runner):
        """Resume a paused simulation."""
        if runner is None:
            return {status_text: gr.update(value="❌ No simulation to resume")}

        try:
            success = runner.resume()
            if success:
                return {
                    status_text: gr.update(
                        value="**State:** RUNNING\n\n" "Simulation resumed."
                    ),
                    pause_btn: gr.update(interactive=True),
                    resume_btn: gr.update(interactive=False),
                }
            else:
                return {status_text: gr.update(value="❌ Failed to resume")}
        except Exception as e:
            logger.error(f"Error resuming: {e}")
            return {status_text: gr.update(value=f"❌ Error: {str(e)}")}

    def stop_simulation(runner):
        """Stop the simulation."""
        if runner is None:
            return {status_text: gr.update(value="❌ No simulation running")}

        try:
            success = runner.stop()
            if success:
                return {
                    runner_state: None,
                    status_text: gr.update(
                        value="**State:** STOPPED\n\n" "Simulation stopped."
                    ),
                    start_btn: gr.update(interactive=True),
                    pause_btn: gr.update(interactive=False),
                    resume_btn: gr.update(interactive=False),
                    stop_btn: gr.update(interactive=False),
                }
            else:
                return {status_text: gr.update(value="❌ Failed to stop")}
        except Exception as e:
            logger.error(f"Error stopping: {e}")
            return {status_text: gr.update(value=f"❌ Error: {str(e)}")}

    # Wire up buttons
    start_btn.click(
        fn=start_simulation,
        inputs=[runner_state, gr.State(None)],
        outputs=[runner_state, status_text, start_btn, pause_btn, stop_btn],
    )

    pause_btn.click(
        fn=pause_simulation,
        inputs=[runner_state],
        outputs=[status_text, pause_btn, resume_btn],
    )

    resume_btn.click(
        fn=resume_simulation,
        inputs=[runner_state],
        outputs=[status_text, pause_btn, resume_btn],
    )

    stop_btn.click(
        fn=stop_simulation,
        inputs=[runner_state],
        outputs=[runner_state, status_text, start_btn, pause_btn, resume_btn, stop_btn],
    )

    return tab, components
