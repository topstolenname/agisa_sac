import warnings
from typing import TYPE_CHECKING

# Use TYPE_CHECKING for chronicler hint
if TYPE_CHECKING:
    from ..chronicler import (
        ResonanceChronicler,
    )  # Adjust if chronicler is moved

# Dependency check
try:

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    warnings.warn(
        "`scikit-learn` not found. Archetype clustering disabled.",
        ImportWarning,
    )


def cluster_archetypes(
    chronicler: "ResonanceChronicler",
    n_clusters: int = 5,
    min_samples: int = 10,
) -> dict[int, list[str]] | None:
    """
    Clusters agent style vectors recorded by the chronicler using KMeans
    to identify emergent archetypes based on linguistic style.

    Args:
        chronicler: The ResonanceChronicler instance containing simulation history.
        n_clusters: The target number of clusters (archetypes) to find.
        min_samples: Minimum number of style vectors required to attempt clustering.

    Returns:
        A dictionary mapping cluster label (int) to a list of agent IDs belonging
        predominantly to that cluster, or None if clustering fails or insufficient data.
    """
    if not HAS_SKLEARN:
        warnings.warn(
            "Cannot cluster archetypes: scikit-learn not installed.",
            RuntimeWarning,
        )
