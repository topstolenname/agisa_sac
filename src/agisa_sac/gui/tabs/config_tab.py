"""Configuration tab for AGI-SAC GUI.

Provides preset selection, parameter controls, and configuration validation.
"""

from typing import Any

import gradio as gr

from ...gui.config_manager import ConfigManager
from ...utils.logger import get_logger

logger = get_logger(__name__)


def create_config_tab(config_manager: ConfigManager) -> tuple[gr.Tab, dict[str, Any]]:
    """Create the configuration tab with all controls.

    Args:
        config_manager: ConfigManager instance

    Returns:
        Tuple of (Tab component, dict of component references)
    """
    components = {}

    with gr.Tab("Configuration") as tab:
        gr.Markdown("## Simulation Configuration")
        gr.Markdown("Configure simulation parameters or load a preset.")

        # Preset selection
        with gr.Row():
            preset_dropdown = gr.Dropdown(
                choices=config_manager.get_available_presets(),
                value="default",
                label="Preset",
                info="Select a pre-configured simulation preset",
            )
            load_preset_btn = gr.Button("Load Preset", variant="primary")

        components["preset_dropdown"] = preset_dropdown
        components["load_preset_btn"] = load_preset_btn

        # Main parameters
        with gr.Group():
            gr.Markdown("### Main Parameters")

            num_agents = gr.Slider(
                minimum=1,
                maximum=1000,
                value=5,
                step=1,
                label="Number of Agents",
                info="Total agents in the simulation",
            )

            num_epochs = gr.Slider(
                minimum=1,
                maximum=1000,
                value=10,
                step=1,
                label="Number of Epochs",
                info="Simulation duration in epochs",
            )

            agent_capacity = gr.Slider(
                minimum=10,
                maximum=1000,
                value=100,
                step=10,
                label="Agent Memory Capacity",
                info="Maximum memories per agent",
            )

            random_seed = gr.Number(
                value=42,
                label="Random Seed",
                info="For reproducible results (leave empty for random)",
            )

        components["num_agents"] = num_agents
        components["num_epochs"] = num_epochs
        components["agent_capacity"] = agent_capacity
        components["random_seed"] = random_seed

        # Feature flags
        with gr.Group():
            gr.Markdown("### Feature Flags")

            use_semantic = gr.Checkbox(
                value=True,
                label="Use Semantic Memory",
                info="Enable semantic embeddings for memory retrieval",
            )

            use_gpu = gr.Checkbox(
                value=False,
                label="Use GPU Acceleration",
                info="Use GPU for computations (requires CUDA)",
            )

        components["use_semantic"] = use_semantic
        components["use_gpu"] = use_gpu

        # Advanced settings
        with gr.Accordion("Advanced Settings", open=False):
            satori_threshold = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.88,
                step=0.01,
                label="Satori Threshold",
                info="Threshold for satori wave detection",
            )

            tda_max_dimension = gr.Slider(
                minimum=0,
                maximum=3,
                value=1,
                step=1,
                label="TDA Max Dimension",
                info="Maximum homology dimension for TDA",
            )

            community_check_freq = gr.Slider(
                minimum=1,
                maximum=100,
                value=5,
                step=1,
                label="Community Check Frequency",
                info="Epochs between community detection runs",
            )

            epoch_log_freq = gr.Slider(
                minimum=1,
                maximum=100,
                value=2,
                step=1,
                label="Epoch Log Frequency",
                info="Epochs between log messages",
            )

        components["satori_threshold"] = satori_threshold
        components["tda_max_dimension"] = tda_max_dimension
        components["community_check_freq"] = community_check_freq
        components["epoch_log_freq"] = epoch_log_freq

        # Validation feedback
        validation_output = gr.Markdown(
            value="", visible=False, elem_classes=["validation-error"]
        )
        components["validation_output"] = validation_output

        # File operations
        with gr.Row():
            config_file_upload = gr.File(
                label="Load Config from File", file_types=[".json"]
            )
            save_config_btn = gr.Button("Save Config to File")
            config_file_download = gr.File(label="Download Config", visible=False)

        components["config_file_upload"] = config_file_upload
        components["save_config_btn"] = save_config_btn
        components["config_file_download"] = config_file_download

    # Event handlers
    def load_preset(preset_name):
        """Load a preset and update all controls."""
        try:
            config = config_manager.get_preset(preset_name)
            return {
                num_agents: config.num_agents,
                num_epochs: config.num_epochs,
                agent_capacity: config.agent_capacity,
                random_seed: config.random_seed,
                use_semantic: config.use_semantic,
                use_gpu: config.use_gpu,
                satori_threshold: config.satori_threshold_analyzer,
                tda_max_dimension: config.tda_max_dimension,
                community_check_freq: config.community_check_frequency,
                epoch_log_freq: config.epoch_log_frequency,
                validation_output: gr.update(value="", visible=False),
            }
        except Exception as e:
            logger.error(f"Error loading preset: {e}")
            return {
                validation_output: gr.update(
                    value=f"❌ Error loading preset: {str(e)}", visible=True
                )
            }

    load_preset_btn.click(
        fn=load_preset,
        inputs=[preset_dropdown],
        outputs=[
            num_agents,
            num_epochs,
            agent_capacity,
            random_seed,
            use_semantic,
            use_gpu,
            satori_threshold,
            tda_max_dimension,
            community_check_freq,
            epoch_log_freq,
            validation_output,
        ],
    )

    return tab, components
