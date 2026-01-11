"""Unit tests for VisualizationManager.

Tests the visualization system that generates matplotlib figures for GUI display.
"""

from unittest.mock import Mock, patch

import matplotlib.pyplot as plt
import numpy as np
import pytest

from agisa_sac.gui.visualization_manager import VisualizationManager


class TestVisualizationManagerInitialization:
    """Test VisualizationManager initialization."""

    def test_initialization_with_defaults(self):
        """Test manager initializes with default figsize."""
        manager = VisualizationManager()

        assert manager.default_figsize == (12, 6)

    def test_initialization_with_custom_figsize(self):
        """Test manager accepts custom figsize."""
        manager = VisualizationManager(figsize=(10, 8))

        assert manager.default_figsize == (10, 8)


class TestMetricsTimeseriesPlot:
    """Test plot_metrics_timeseries method."""

    def test_plot_with_system_metrics(self):
        """Test plotting system-wide metrics."""
        manager = VisualizationManager()

        metrics_history = [
            {
                "epoch": 0,
                "system_metrics": {"satori_wave_ratio": 0.3, "archetype_entropy": 0.8},
            },
            {
                "epoch": 1,
                "system_metrics": {"satori_wave_ratio": 0.5, "archetype_entropy": 0.9},
            },
            {
                "epoch": 2,
                "system_metrics": {"satori_wave_ratio": 0.7, "archetype_entropy": 0.95},
            },
        ]

        fig = manager.plot_metrics_timeseries(
            metrics_history, metrics_to_plot=["satori_wave_ratio"]
        )

        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0

        # Clean up
        plt.close(fig)

    def test_plot_with_agent_metrics(self):
        """Test plotting per-agent metrics."""
        manager = VisualizationManager()

        metrics_history = [
            {
                "epoch": 0,
                "agent_metrics": {"agent_0": {"sri": 0.1, "nds": 3.0}},
            },
            {
                "epoch": 1,
                "agent_metrics": {"agent_0": {"sri": 0.2, "nds": 5.0}},
            },
        ]

        fig = manager.plot_metrics_timeseries(
            metrics_history, metrics_to_plot=["sri", "nds"], agent_id="agent_0"
        )

        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 2  # One subplot per metric

        plt.close(fig)

    def test_plot_with_empty_history(self):
        """Test handles empty metrics history."""
        manager = VisualizationManager()

        fig = manager.plot_metrics_timeseries([])

        assert isinstance(fig, plt.Figure)
        # Should return empty plot with message
        ax = fig.axes[0]
        assert ax.get_xlim() == (0, 1)  # Default empty axis

        plt.close(fig)

    def test_plot_with_auto_detected_metrics(self):
        """Test auto-detects available metrics when none specified."""
        manager = VisualizationManager()

        metrics_history = [
            {
                "epoch": 0,
                "system_metrics": {
                    "satori_wave_ratio": 0.5,
                    "archetype_entropy": 0.8,
                    "mean_resonance_strength": 0.6,
                },
            }
        ]

        fig = manager.plot_metrics_timeseries(metrics_history)

        assert isinstance(fig, plt.Figure)
        # Should plot all available metrics
        assert len(fig.axes) == 3

        plt.close(fig)

    def test_plot_with_dict_values(self):
        """Test handles dict values by counting keys."""
        manager = VisualizationManager()

        metrics_history = [
            {
                "epoch": 0,
                "system_metrics": {
                    "archetype_distribution": {"creative": 2, "systematic": 3}
                },
            },
            {
                "epoch": 1,
                "system_metrics": {
                    "archetype_distribution": {
                        "creative": 2,
                        "systematic": 3,
                        "analytical": 1,
                    }
                },
            },
        ]

        fig = manager.plot_metrics_timeseries(
            metrics_history, metrics_to_plot=["archetype_distribution"]
        )

        assert isinstance(fig, plt.Figure)

        plt.close(fig)

    def test_plot_with_custom_title(self):
        """Test accepts custom title."""
        manager = VisualizationManager()

        metrics_history = [
            {"epoch": 0, "system_metrics": {"satori_wave_ratio": 0.5}}
        ]

        fig = manager.plot_metrics_timeseries(
            metrics_history, title="Custom Title Test"
        )

        assert isinstance(fig, plt.Figure)
        assert "Custom Title Test" in fig._suptitle.get_text()

        plt.close(fig)


class TestPersistenceDiagramPlot:
    """Test plot_persistence_diagram method."""

    def test_plot_valid_diagram(self):
        """Test plotting valid persistence diagram."""
        manager = VisualizationManager()

        # Create sample persistence diagram
        diagram = np.array([[0.0, 1.0], [0.5, 2.0], [1.0, 3.0]])

        fig = manager.plot_persistence_diagram(diagram, epoch=10, dimension=1)

        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0

        plt.close(fig)

    def test_plot_empty_diagram(self):
        """Test handles empty diagram."""
        manager = VisualizationManager()

        fig = manager.plot_persistence_diagram(None, epoch=5, dimension=1)

        assert isinstance(fig, plt.Figure)
        # Should show empty plot message

        plt.close(fig)

    def test_plot_diagram_with_infinite_death(self):
        """Test handles diagrams with infinite death values."""
        manager = VisualizationManager()

        # Diagram with infinite death
        diagram = np.array([[0.0, 1.0], [0.5, np.inf], [1.0, 2.5]])

        fig = manager.plot_persistence_diagram(diagram, epoch=10, dimension=0)

        assert isinstance(fig, plt.Figure)

        plt.close(fig)


class TestPersistenceBarcödePlot:
    """Test plot_persistence_barcode method."""

    def test_plot_valid_barcode(self):
        """Test plotting valid persistence barcode."""
        manager = VisualizationManager()

        diagram = np.array([[0.0, 1.0], [0.5, 2.0], [1.0, 3.0]])

        fig = manager.plot_persistence_barcode(diagram, epoch=10, dimension=1)

        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0

        plt.close(fig)

    def test_plot_empty_barcode(self):
        """Test handles empty barcode."""
        manager = VisualizationManager()

        fig = manager.plot_persistence_barcode(None, epoch=5, dimension=1)

        assert isinstance(fig, plt.Figure)

        plt.close(fig)


class TestAgentMetricsComparison:
    """Test plot_agent_metrics_comparison method."""

    def test_plot_multiple_agents(self):
        """Test plotting metric across multiple agents."""
        manager = VisualizationManager()

        metrics_history = [
            {
                "epoch": 0,
                "agent_metrics": {
                    "agent_0": {"sri": 0.1},
                    "agent_1": {"sri": 0.2},
                    "agent_2": {"sri": 0.15},
                },
            },
            {
                "epoch": 1,
                "agent_metrics": {
                    "agent_0": {"sri": 0.3},
                    "agent_1": {"sri": 0.4},
                    "agent_2": {"sri": 0.35},
                },
            },
        ]

        fig = manager.plot_agent_metrics_comparison(
            metrics_history, metric_key="sri", agent_ids=["agent_0", "agent_1"]
        )

        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0

        plt.close(fig)

    def test_plot_auto_select_agents(self):
        """Test auto-selects agents when none specified."""
        manager = VisualizationManager()

        metrics_history = [
            {
                "epoch": 0,
                "agent_metrics": {
                    f"agent_{i}": {"sri": 0.1 * i} for i in range(15)
                },
            }
        ]

        fig = manager.plot_agent_metrics_comparison(
            metrics_history, metric_key="sri", max_agents=5
        )

        assert isinstance(fig, plt.Figure)
        # Should only plot first 5 agents

        plt.close(fig)

    def test_plot_with_empty_history(self):
        """Test handles empty history."""
        manager = VisualizationManager()

        fig = manager.plot_agent_metrics_comparison([], metric_key="sri")

        assert isinstance(fig, plt.Figure)

        plt.close(fig)


class TestSocialGraphPlot:
    """Test plot_social_graph method."""

    def test_plot_valid_graph(self):
        """Test plotting valid social graph."""
        manager = VisualizationManager()

        # Simple 3-node graph
        graph_data = {
            "influence_matrix": [[0.0, 0.5, 0.3], [0.5, 0.0, 0.4], [0.3, 0.4, 0.0]],
            "communities": {0: 0, 1: 0, 2: 1},
        }

        fig = manager.plot_social_graph(graph_data, epoch=10)

        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) > 0

        plt.close(fig)

    def test_plot_graph_without_communities(self):
        """Test plotting graph without community data."""
        manager = VisualizationManager()

        graph_data = {
            "influence_matrix": [[0.0, 0.5], [0.5, 0.0]],
        }

        fig = manager.plot_social_graph(graph_data, epoch=5)

        assert isinstance(fig, plt.Figure)

        plt.close(fig)

    def test_plot_empty_graph(self):
        """Test handles None graph data."""
        manager = VisualizationManager()

        fig = manager.plot_social_graph(None, epoch=10)

        assert isinstance(fig, plt.Figure)
        # Should show empty plot message

        plt.close(fig)

    def test_plot_invalid_graph_format(self):
        """Test handles invalid graph format."""
        manager = VisualizationManager()

        # Missing influence_matrix
        graph_data = {"communities": {0: 0}}

        fig = manager.plot_social_graph(graph_data, epoch=10)

        assert isinstance(fig, plt.Figure)

        plt.close(fig)


class TestUtilityMethods:
    """Test utility methods."""

    def test_create_empty_plot(self):
        """Test _create_empty_plot creates placeholder figure."""
        manager = VisualizationManager()

        fig = manager._create_empty_plot("Test message")

        assert isinstance(fig, plt.Figure)
        assert len(fig.axes) == 1
        ax = fig.axes[0]
        # Axis should be turned off
        assert not ax.axison

        plt.close(fig)

    def test_close_figure(self):
        """Test close_figure properly closes matplotlib figure."""
        manager = VisualizationManager()

        fig = plt.figure()
        fig_num = fig.number

        manager.close_figure(fig)

        # Figure should be closed
        assert fig_num not in plt.get_fignums()

    def test_close_figure_handles_exception(self):
        """Test close_figure handles exceptions gracefully."""
        manager = VisualizationManager()

        # Should not raise exception
        manager.close_figure(None)


class TestErrorHandling:
    """Test error handling in visualization methods."""

    @patch("agisa_sac.gui.visualization_manager.visualization.plot_persistence_diagram")
    def test_handles_plotting_exception(self, mock_plot):
        """Test handles exceptions during plotting."""
        mock_plot.side_effect = Exception("Plot error")

        manager = VisualizationManager()
        diagram = np.array([[0.0, 1.0]])

        # Should not raise, returns error plot
        fig = manager.plot_persistence_diagram(diagram, epoch=5, dimension=1)

        assert isinstance(fig, plt.Figure)

        plt.close(fig)

    def test_handles_missing_data_gracefully(self):
        """Test all methods handle missing data without crashing."""
        manager = VisualizationManager()

        # Should all return valid figures (with error messages)
        fig1 = manager.plot_metrics_timeseries([])
        fig2 = manager.plot_persistence_diagram(None, epoch=0, dimension=1)
        fig3 = manager.plot_persistence_barcode(None, epoch=0, dimension=1)
        fig4 = manager.plot_agent_metrics_comparison([], metric_key="sri")
        fig5 = manager.plot_social_graph(None, epoch=0)

        assert all(isinstance(f, plt.Figure) for f in [fig1, fig2, fig3, fig4, fig5])

        for fig in [fig1, fig2, fig3, fig4, fig5]:
            plt.close(fig)


class TestMemoryManagement:
    """Test memory management and figure cleanup."""

    def test_figures_can_be_closed(self):
        """Test generated figures can be closed to free memory."""
        manager = VisualizationManager()

        metrics_history = [
            {"epoch": 0, "system_metrics": {"satori_wave_ratio": 0.5}}
        ]

        # Create multiple figures
        figures = []
        for _ in range(5):
            fig = manager.plot_metrics_timeseries(metrics_history)
            figures.append(fig)

        initial_count = len(plt.get_fignums())

        # Close all figures
        for fig in figures:
            manager.close_figure(fig)

        final_count = len(plt.get_fignums())

        # All figures should be closed
        assert final_count < initial_count

    def test_no_show_called(self):
        """Test plt.show() is never called (non-blocking requirement)."""
        manager = VisualizationManager()

        metrics_history = [
            {"epoch": 0, "system_metrics": {"satori_wave_ratio": 0.5}}
        ]

        with patch("matplotlib.pyplot.show") as mock_show:
            fig = manager.plot_metrics_timeseries(metrics_history)

            # plt.show() should NOT be called
            mock_show.assert_not_called()

        plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
