import warnings
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

# TDA Dependency Handling
try:

    HAS_PERSIM = True
except ImportError:
    HAS_PERSIM = False


def plot_persistence_diagram(
    diagram: np.ndarray,
    title: str = "Persistence Diagram",
    ax: Optional[plt.Axes] = None,
    show_plot: bool = True,
    **kwargs,
):
    """Plots a persistence diagram using matplotlib."""
    if (
        diagram is None
        or diagram.ndim != 2
        or diagram.shape[1] != 2
        or diagram.shape[0] == 0
    ):
        warnings.warn(
            f"Invalid diagram for '{title}'. Skip plot.", RuntimeWarning
        )
        return
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    finite_vals = diagram[np.isfinite(diagram)]
    min_val = np.min(finite_vals) if finite_vals.size > 0 else 0
    max_val = np.max(finite_vals) if finite_vals.size > 0 else 1
    plot_diagram = diagram.copy()
    inf_death_val = max_val + 0.1 * (max_val - min_val + 1e-6)
    inf_indices = np.isinf(plot_diagram[:, 1])
    plot_diagram[inf_indices, 1] = inf_death_val
    ax.scatter(plot_diagram[:, 0], plot_diagram[:, 1], **kwargs)
    lim_min = min_val - 0.05 * (max_val - min_val + 1e-6)
    lim_max = inf_death_val + 0.05 * (max_val - min_val + 1e-6)
    ax.plot(
        [lim_min, lim_max], [lim_min, lim_max], "--", color="grey", label="y=x"
    )
    ax.set_xlabel("Birth")
    ax.set_ylabel("Death")
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend()
    if show_plot:
        plt.tight_layout()
        plt.show()


def plot_persistence_barcode(
    diagram: np.ndarray,
    title: str = "Persistence Barcode",
    ax: Optional[plt.Axes] = None,
    show_plot: bool = True,
    **kwargs,
):
    """Plots a persistence barcode using matplotlib."""
    if (
        diagram is None
        or diagram.ndim != 2
        or diagram.shape[1] != 2
        or diagram.shape[0] == 0
    ):
        warnings.warn(
            f"Invalid diagram for '{title}'. Skip plot.", RuntimeWarning
        )
        return
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))
    sorted_diagram = diagram[np.argsort(diagram[:, 0])]
    plot_diagram = sorted_diagram.copy()
    finite_deaths = plot_diagram[np.isfinite(plot_diagram[:, 1]), 1]
    max_finite_death = (
        np.max(finite_deaths)
        if finite_deaths.size > 0
        else np.max(plot_diagram[:, 0])
    )
    inf_death_val = max_finite_death + 0.1 * (
        max_finite_death - np.min(plot_diagram[:, 0]) + 1e-6
    )
    inf_indices = np.isinf(plot_diagram[:, 1])
    plot_diagram[inf_indices, 1] = inf_death_val
    for i, (birth, death) in enumerate(plot_diagram):
        ax.hlines(y=i, xmin=birth, xmax=death, linewidth=2, **kwargs)
    ax.set_xlabel("Time (Radius/Scale)")
    ax.set_ylabel("Feature Index")
    ax.set_title(title)
    ax.set_yticks([])
    if show_plot:
        plt.tight_layout()
        plt.show()


def plot_metric_comparison(
    epoch_history: Dict[int, Dict[str, Any]],
    metrics_to_plot: List[str],
    tda_metric_history: Optional[Dict[int, Dict[str, Any]]] = None,
    tda_metrics_to_plot: Optional[List[str]] = None,
    title: str = "Simulation Metrics Over Time",
    figsize: Tuple[int, int] = (12, 6),
):
    """Plots specified simulation metrics and optional TDA metrics over epochs."""
    if not epoch_history:
        warnings.warn("Empty epoch history. Cannot plot.", RuntimeWarning)
        return
    epochs = sorted(epoch_history.keys())
    num_metrics = len(metrics_to_plot)
    num_tda_metrics = len(tda_metrics_to_plot) if tda_metrics_to_plot else 0
    total_plots = num_metrics + num_tda_metrics
    if total_plots == 0:
        warnings.warn("No metrics specified for plotting.", RuntimeWarning)
        return
    fig, axes = plt.subplots(
        total_plots, 1, figsize=figsize, sharex=True, squeeze=False
    )
    fig.suptitle(title, fontsize=14)
    plot_idx = 0
    # Plot general metrics
    for metric_key in metrics_to_plot:
        ax = axes[plot_idx, 0]
        values = [epoch_history[e].get(metric_key) for e in epochs]
        valid_epochs = [
            e
            for i, e in enumerate(epochs)
            if values[i] is not None and np.isfinite(values[i])
        ]
        valid_values = [v for v in values if v is not None and np.isfinite(v)]
        if valid_values:
            ax.plot(
                valid_epochs,
                valid_values,
                marker=".",
                linestyle="-",
                label=metric_key,
            )
            ax.legend(loc="upper left")
        else:
            ax.text(
                0.5,
                0.5,
                f"No data for '{metric_key}'",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
        ax.set_ylabel(metric_key.replace("_", " ").title())
        ax.grid(True, linestyle=":", alpha=0.6)
        plot_idx += 1
    # Plot TDA metrics
    if tda_metric_history and tda_metrics_to_plot:
        tda_epochs = sorted(tda_metric_history.keys())
        for metric_key in tda_metrics_to_plot:
            ax = axes[plot_idx, 0]
            values = [
                tda_metric_history[e].get(metric_key)
                for e in tda_epochs
                if e in tda_metric_history
            ]
            valid_epochs = [
                e
                for e in tda_epochs
                if e in tda_metric_history
                and tda_metric_history[e].get(metric_key) is not None
                and np.isfinite(tda_metric_history[e].get(metric_key))
            ]
            valid_values = [
                tda_metric_history[e].get(metric_key) for e in valid_epochs
            ]
            if valid_values:
                ax.plot(
                    valid_epochs,
                    valid_values,
                    marker="x",
                    linestyle="--",
                    label=f"TDA: {metric_key}",
                    color="red",
                )
                ax.legend(loc="upper left")
            else:
                ax.text(
                    0.5,
                    0.5,
                    f"No data for TDA '{metric_key}'",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
            ax.set_ylabel(metric_key.replace("_", " ").title())
            ax.grid(True, linestyle=":", alpha=0.6)
            plot_idx += 1
    axes[-1, 0].set_xlabel("Simulation Epoch")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.show()
