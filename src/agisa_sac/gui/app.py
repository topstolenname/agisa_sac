"""Main Gradio application for AGI-SAC simulation control.

This module provides a web-based GUI for configuring, running, and monitoring
AGI-SAC multi-agent simulations.
"""

import gradio as gr

from ..gui.config_manager import ConfigManager
from ..gui.tabs import (
    create_config_tab,
    create_control_tab,
    create_export_tab,
    create_visualization_tab,
)
from ..gui.visualization_manager import VisualizationManager
from ..utils.logger import get_logger

logger = get_logger(__name__)


def create_gui(
    share: bool = False, server_name: str = "0.0.0.0", server_port: int = 7860
) -> gr.Blocks:
    """Create the main Gradio application.

    Args:
        share: If True, create a public shareable link
        server_name: Server hostname (default: 0.0.0.0 for all interfaces)
        server_port: Server port (default: 7860)

    Returns:
        Gradio Blocks application
    """
    # Initialize managers
    config_manager = ConfigManager()
    _ = VisualizationManager()  # Initialized for side effects

    # Create the Gradio interface
    with gr.Blocks(title="AGI-SAC Simulation Control") as app:
        gr.Markdown(
            """
            # AGI-SAC Simulation Control

            **A Model Organism for System-Level Alignment in Stateful Multi-Agent Systems**

            Configure and monitor agent simulations with real-time visualization and analysis.
            """
        )

        # Create tabs
        with gr.Tabs():
            config_tab, config_components = create_config_tab(config_manager)
            control_tab, control_components = create_control_tab(config_manager)
            _, viz_components = create_visualization_tab()
            export_tab, export_components = create_export_tab()

        # Footer
        gr.Markdown(
            """
            ---

            **AGI-SAC** | [GitHub](https://github.com/topstolenname/agisa_sac) |
            [Documentation](docs/) | Research Infrastructure for Alignment Studies
            """
        )

    logger.info(
        f"Gradio app created. Launch with share={share}, "
        f"server={server_name}:{server_port}"
    )

    return app


def main(
    share: bool = False,
    server_name: str = "0.0.0.0",
    server_port: int = 7860,
    debug: bool = False,
):
    """Launch the AGI-SAC GUI application.

    Args:
        share: If True, create a public shareable link
        server_name: Server hostname
        server_port: Server port
        debug: Enable debug mode
    """
    logger.info("Launching AGI-SAC GUI application...")

    try:
        app = create_gui(share=share, server_name=server_name, server_port=server_port)

        app.launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
            debug=debug,
            show_error=True,
            quiet=False,
            theme=gr.themes.Soft(),
            css="""
            .validation-error {
                color: #d32f2f;
                background-color: #ffebee;
                padding: 10px;
                border-radius: 4px;
                border-left: 4px solid #d32f2f;
            }
            """,
        )

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Error launching GUI: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="AGI-SAC GUI - Web interface for simulation control"
    )
    parser.add_argument(
        "--share", action="store_true", help="Create a public shareable link"
    )
    parser.add_argument(
        "--server-name", default="0.0.0.0", help="Server hostname (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--server-port", type=int, default=7860, help="Server port (default: 7860)"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    main(
        share=args.share,
        server_name=args.server_name,
        server_port=args.server_port,
        debug=args.debug,
    )
