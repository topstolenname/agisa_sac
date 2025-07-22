import numpy as np
import warnings
from typing import Dict, List, Optional, Any, Tuple

# Import framework version
try:
    from .. import FRAMEWORK_VERSION
except ImportError:
    FRAMEWORK_VERSION = "unknown"

# TDA Dependency Handling
try:
    import ripser

    HAS_RIPSER = True
except ImportError:
    HAS_RIPSER = False
    warnings.warn("`ripser` N/A. TDA compute disabled.", ImportWarning)
try:
    import persim

    HAS_PERSIM = True
except ImportError:
    HAS_PERSIM = False
    warnings.warn("`persim` N/A. TDA distance disabled.", ImportWarning)


class PersistentHomologyTracker:
    """Performs TDA using persistent homology. Includes serialization."""

    def __init__(self, max_dimension: int = 1):
        self.max_dimension = max_dimension
        self.persistence_diagrams_history: List[Optional[List[np.ndarray]]] = []
        self.has_tda_lib = HAS_RIPSER  # Store availability

    def compute_persistence(
        self, point_cloud: np.ndarray, max_radius: Optional[float] = None, **ripser_kwargs
    ) -> Optional[List[np.ndarray]]:
        """Computes persistence diagram using ripser."""
        if (
            not self.has_tda_lib
            or point_cloud is None
            or point_cloud.ndim != 2
            or point_cloud.shape[0] < 2
        ):
            self.persistence_diagrams_history.append(None)
            return None
        try:
            default_kwargs = {
                "maxdim": self.max_dimension,
                "thresh": max_radius if max_radius is not None else np.inf,
            }
            default_kwargs.update(ripser_kwargs)
            result = ripser.ripser(point_cloud, **default_kwargs)
            diagrams = result["dgms"]
            cleaned_diagrams = []
            for dim, diag in enumerate(diagrams):
                if diag.shape[0] > 0:
                    if dim == 0:
                        finite_bars = diag[diag[:, 1] != np.inf]
                        inf_bars = diag[diag[:, 1] == np.inf]
                        if inf_bars.shape[0] > 0:
                            inf_bars = inf_bars[np.argsort(inf_bars[:, 0])[:1]]
                            cleaned_diag = (
                                np.vstack((finite_bars, inf_bars))
                                if finite_bars.shape[0] > 0
                                else inf_bars
                            )
                        else:
                            cleaned_diag = finite_bars
                    else:
                        cleaned_diag = diag[diag[:, 1] != np.inf]
                    cleaned_diagrams.append(cleaned_diag)
                else:
                    cleaned_diagrams.append(np.empty((0, 2)))
            self.persistence_diagrams_history.append(cleaned_diagrams)
            return cleaned_diagrams
        except Exception as e:
            warnings.warn(f"Persistence computation failed: {e}", RuntimeWarning)
            self.persistence_diagrams_history.append(None)
            return None

    def detect_phase_transition(
        self,
        comparison_dimension: int = 1,
        distance_metric: str = "bottleneck",
        threshold: float = 0.2,
    ) -> Tuple[bool, float]:
        """Detects phase transitions by comparing diagrams using persim. Returns (detected, distance)."""
        if not HAS_PERSIM or len(self.persistence_diagrams_history) < 2:
            return False, 0.0
        current_diagram_list = self.persistence_diagrams_history[-1]
        previous_diagram_list = self.persistence_diagrams_history[-2]
        if (
            current_diagram_list is None
            or previous_diagram_list is None
            or len(current_diagram_list) <= comparison_dimension
            or len(previous_diagram_list) <= comparison_dimension
        ):
            return False, 0.0
        current_diagram = np.array(current_diagram_list[comparison_dimension])
        previous_diagram = np.array(previous_diagram_list[comparison_dimension])
        distance = 0.0
        if current_diagram.shape[0] == 0 and previous_diagram.shape[0] == 0:
            distance = 0.0
        elif current_diagram.shape[0] == 0 or previous_diagram.shape[0] == 0:
            distance = threshold + 0.1  # Assume change if features appear/vanish
        else:
            try:
                if distance_metric == "bottleneck":
                    distance, _ = persim.bottleneck(
                        current_diagram, previous_diagram, matching=False
                    )
                elif distance_metric == "wasserstein":
                    distance, _ = persim.wasserstein(
                        current_diagram, previous_diagram, matching=False, p=2
                    )
                else:
                    warnings.warn(
                        f"Unsupported TDA metric: {distance_metric}. Using Bottleneck.",
                        RuntimeWarning,
                    )
                    distance, _ = persim.bottleneck(
                        current_diagram, previous_diagram, matching=False
                    )
            except Exception as e:
                warnings.warn(
                    f"TDA distance failed ({distance_metric}, dim={comparison_dimension}): {e}",
                    RuntimeWarning,
                )
                return False, 0.0
        transition_detected = distance > threshold
        return transition_detected, float(distance)  # Return distance as well

    def get_diagram_summary(self, diagram_index: int = -1) -> Dict:
        """Returns summary stats for a specific diagram in history."""
        if (
            not self.persistence_diagrams_history
            or diagram_index >= len(self.persistence_diagrams_history)
            or self.persistence_diagrams_history[diagram_index] is None
        ):
            return {"error": "Diagram not available"}
        summary = {}
        diagram_list = self.persistence_diagrams_history[diagram_index]
        for dim, diag in enumerate(diagram_list):
            persistence = diag[:, 1] - diag[:, 0]
            finite_persistence = persistence[np.isfinite(persistence)]
            summary[f"H{dim}_features"] = diag.shape[0]
            summary[f"H{dim}_total_persistence"] = (
                float(np.sum(finite_persistence)) if finite_persistence.size > 0 else 0.0
            )
            summary[f"H{dim}_mean_persistence"] = (
                float(np.mean(finite_persistence)) if finite_persistence.size > 0 else 0.0
            )
        return summary

    def to_dict(self) -> Dict:
        serializable_history = [
            [d.tolist() for d in diag_list] if diag_list is not None else None
            for diag_list in self.persistence_diagrams_history
        ]
        return {
            "version": FRAMEWORK_VERSION,
            "max_dimension": self.max_dimension,
            "persistence_diagrams_history": serializable_history,
        }

    def load_state(self, state: Dict):
        loaded_version = state.get("version")
        if loaded_version != FRAMEWORK_VERSION:
            warnings.warn(
                f"Loading TDA v '{loaded_version}' into v '{FRAMEWORK_VERSION}'.", UserWarning
            )
        self.max_dimension = state.get("max_dimension", self.max_dimension)
        loaded_history = state.get("persistence_diagrams_history", [])
        self.persistence_diagrams_history = [
            [np.array(d) for d in diag_list_data] if diag_list_data is not None else None
            for diag_list_data in loaded_history
        ]
        self.has_tda_lib = HAS_RIPSER  # Re-check on load
