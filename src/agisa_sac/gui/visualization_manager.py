"""Visualization management for GUI display.

This module provides matplotlib figure generation for Gradio components.
All functions return figures without calling plt.show() to avoid blocking.
"""

from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from agisa_sac.analysis import visualization
from agisa_sac.utils.logger import get_logger

logger = get_logger(__name__)

# Use non-interactive backend for GUI
matplotlib.use("Agg")


class VisualizationManager:
    """Generates matplotlib figures for GUI display.

    This class wraps existing visualization functions and adds GUI-specific
    plotting capabilities. All methods return matplotlib Figure objects
    without calling plt.show().
    """

    def __init__(self, figsize: tuple = (12, 6)):
        """Initialize the visualization manager.

        Args:
            figsize: Default figure size (width, height) in inches
        """
        self.default_figsize = figsize

    def plot_metrics_timeseries(
        self,
        metrics_history: list[dict[str, Any]],
        metrics_to_plot: list[str] | None = None,
        agent_id: str | None = None,
        title: str | None = None,
    ) -> plt.Figure:
        """Plot time series of metrics over epochs.

        Args:
            metrics_history: List of metric snapshots from MetricsCollector
            metrics_to_plot: List of metric keys to plot. If None, plots all.
            agent_id: If specified, plot per-agent metrics. Otherwise, system metrics.
            title: Plot title. If None, auto-generates based on content.

        Returns:
            matplotlib Figure object
        """
        if not metrics_history:
            return self._create_empty_plot("No metrics data available")

        try:
            # Extract epochs and values
            epochs = [snap["epoch"] for snap in metrics_history]

            # Determine which metrics to plot
            if metrics_to_plot is None:
                # Auto-detect available metrics
                first_snap = metrics_history[0]
                if agent_id and "agent_metrics" in first_snap:
                    agent_data = first_snap["agent_metrics"].get(agent_id, {})
                    metrics_to_plot = list(agent_data.keys())
                elif "system_metrics" in first_snap:
                    metrics_to_plot = list(first_snap["system_metrics"].keys())
                else:
                    metrics_to_plot = []

            if not metrics_to_plot:
                return self._create_empty_plot("No metrics to plot")

            # Create subplots
            num_metrics = len(metrics_to_plot)
            fig, axes = plt.subplots(
                num_metrics,
                1,
                figsize=(self.default_figsize[0], 3 * num_metrics),
                squeeze=False,
            )

            for idx, metric_key in enumerate(metrics_to_plot):
                ax = axes[idx, 0]
                values = []

                # Extract values for this metric
                for snap in metrics_history:
                    if agent_id and "agent_metrics" in snap:
                        agent_data = snap["agent_metrics"].get(agent_id, {})
                        value = agent_data.get(metric_key)
                    elif "system_metrics" in snap:
                        value = snap["system_metrics"].get(metric_key)
                    else:
                        value = None

                    # Handle dict values (like archetype_distribution)
                    if isinstance(value, dict):
                        value = len(value)  # Count keys for dicts

                    values.append(value if value is not None else np.nan)

                # Plot
                ax.plot(epochs, values, marker="o", markersize=3, linewidth=1.5)
                ax.set_xlabel("Epoch")
                ax.set_ylabel(metric_key.replace("_", " ").title())
                ax.set_title(f"{metric_key.upper()}")
                ax.grid(True, linestyle=":", alpha=0.6)

            # Overall title
            if title is None:
                if agent_id:
                    title = f"Metrics for Agent {agent_id}"
                else:
                    title = "System-Wide Metrics Over Time"
            fig.suptitle(title, fontsize=14, fontweight="bold")

            plt.tight_layout()
            return fig

        except Exception as e:
            logger.error(f"Error plotting metrics timeseries: {e}", exc_info=True)
            return self._create_empty_plot(f"Error: {str(e)}")

    def plot_persistence_diagram(
        self, diagram: np.ndarray | None, epoch: int, dimension: int = 1
    ) -> plt.Figure:
        """Plot TDA persistence diagram for a specific epoch.

        Args:
            diagram: Persistence diagram (Nx2 array of [birth, death])
            epoch: Epoch number for title
            dimension: Homology dimension

        Returns:
            matplotlib Figure object
        """
        if diagram is None or len(diagram) == 0:
            return self._create_empty_plot(
                f"No TDA data for epoch {epoch}, dimension H{dimension}"
            )

        try:
            fig, ax = plt.subplots(figsize=(6, 6))
            visualization.plot_persistence_diagram(
                diagram,
                title=f"Persistence Diagram (Epoch {epoch}, H{dimension})",
                ax=ax,
                show_plot=False,
                alpha=0.6,
                s=50,
            )
            plt.tight_layout()
            return fig

        except Exception as e:
            logger.error(f"Error plotting persistence diagram: {e}", exc_info=True)
            return self._create_empty_plot(f"Error: {str(e)}")

    def plot_persistence_barcode(
        self, diagram: np.ndarray | None, epoch: int, dimension: int = 1
    ) -> plt.Figure:
        """Plot TDA persistence barcode for a specific epoch.

        Args:
            diagram: Persistence diagram (Nx2 array of [birth, death])
            epoch: Epoch number for title
            dimension: Homology dimension

        Returns:
            matplotlib Figure object
        """
        if diagram is None or len(diagram) == 0:
            return self._create_empty_plot(
                f"No TDA data for epoch {epoch}, dimension H{dimension}"
            )

        try:
            fig, ax = plt.subplots(figsize=(8, 4))
            visualization.plot_persistence_barcode(
                diagram,
                title=f"Persistence Barcode (Epoch {epoch}, H{dimension})",
                ax=ax,
                show_plot=False,
                color="steelblue",
            )
            plt.tight_layout()
            return fig

        except Exception as e:
            logger.error(f"Error plotting persistence barcode: {e}", exc_info=True)
            return self._create_empty_plot(f"Error: {str(e)}")

    def plot_agent_metrics_comparison(
        self,
        metrics_history: list[dict[str, Any]],
        metric_key: str,
        agent_ids: list[str] | None = None,
        max_agents: int = 10,
    ) -> plt.Figure:
        """Plot a single metric across multiple agents.

        Args:
            metrics_history: List of metric snapshots
            metric_key: Metric to plot (e.g., 'sri', 'nds')
            agent_ids: List of agent IDs to plot. If None, plots up to max_agents.
            max_agents: Maximum number of agents to plot (to avoid crowding)

        Returns:
            matplotlib Figure object
        """
        if not metrics_history:
            return self._create_empty_plot("No metrics data available")

        try:
            # Get agent IDs
            if agent_ids is None:
                first_snap = metrics_history[0]
                if "agent_metrics" in first_snap:
                    all_agent_ids = list(first_snap["agent_metrics"].keys())
                    agent_ids = all_agent_ids[:max_agents]
                else:
                    return self._create_empty_plot("No agent metrics available")

            fig, ax = plt.subplots(figsize=self.default_figsize)

            epochs = [snap["epoch"] for snap in metrics_history]

            # Plot each agent
            for agent_id in agent_ids:
                values = []
                for snap in metrics_history:
                    agent_data = snap.get("agent_metrics", {}).get(agent_id, {})
                    value = agent_data.get(metric_key)
                    values.append(value if value is not None else np.nan)

                ax.plot(
                    epochs,
                    values,
                    marker="o",
                    markersize=2,
                    linewidth=1,
                    label=agent_id,
                    alpha=0.7,
                )

            ax.set_xlabel("Epoch")
            ax.set_ylabel(metric_key.upper())
            ax.set_title(f"{metric_key.upper()} Across Agents")
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

            plt.tight_layout()
            return fig

        except Exception as e:
            logger.error(f"Error plotting agent comparison: {e}", exc_info=True)
            return self._create_empty_plot(f"Error: {str(e)}")

    def plot_social_graph(
        self, graph_data: dict[str, Any] | None, epoch: int
    ) -> plt.Figure:
        """Plot social graph structure.

        Args:
            graph_data: Social graph data (adjacency matrix, communities, etc.)
            epoch: Current epoch number

        Returns:
            matplotlib Figure object
        """
        if graph_data is None:
            return self._create_empty_plot(f"No social graph data for epoch {epoch}")

        try:
            import networkx as nx

            fig, ax = plt.subplots(figsize=self.default_figsize)

            # Build NetworkX graph from adjacency matrix
            if "influence_matrix" in graph_data:
                matrix = np.array(graph_data["influence_matrix"])
                G = nx.from_numpy_array(matrix)

                # Layout
                pos = nx.spring_layout(G, seed=42)

                # Communities (if available)
                if "communities" in graph_data:
                    communities = graph_data["communities"]
                    # Color nodes by community
                    node_colors = [communities.get(i, 0) for i in range(len(G.nodes()))]
                    nx.draw_networkx_nodes(
                        G,
                        pos,
                        node_color=node_colors,
                        cmap="tab10",
                        node_size=300,
                        ax=ax,
                    )
                else:
                    nx.draw_networkx_nodes(G, pos, node_size=300, ax=ax)

                # Draw edges
                nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)

                ax.set_title(f"Social Graph (Epoch {epoch})")
                ax.axis("off")
            else:
                return self._create_empty_plot("Invalid graph data format")

            plt.tight_layout()
            return fig

        except Exception as e:
            logger.error(f"Error plotting social graph: {e}", exc_info=True)
            return self._create_empty_plot(f"Error: {str(e)}")

    def _create_empty_plot(self, message: str) -> plt.Figure:
        """Create a placeholder figure with a message.

        Args:
            message: Message to display

        Returns:
            matplotlib Figure with text message
        """
        fig, ax = plt.subplots(figsize=self.default_figsize)
        ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            fontsize=14,
            color="gray",
            transform=ax.transAxes,
        )
        ax.axis("off")
        return fig

    def close_figure(self, fig: plt.Figure) -> None:
        """Close a matplotlib figure to free memory.

        Args:
            fig: Figure to close
        """
        try:
            plt.close(fig)
        except Exception as e:
            logger.warning(f"Error closing figure: {e}")
