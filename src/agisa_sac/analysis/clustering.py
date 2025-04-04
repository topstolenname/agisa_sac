import numpy as np
import warnings
from collections import defaultdict
from typing import Dict, List, Optional, TYPE_CHECKING

# Use TYPE_CHECKING for chronicler hint
if TYPE_CHECKING:
    from ..chronicler import ResonanceChronicler # Adjust if chronicler is moved

# Dependency check
try:
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    warnings.warn("`scikit-learn` not found. Archetype clustering disabled.", ImportWarning)

def cluster_archetypes(chronicler: 'ResonanceChronicler', n_clusters: int = 5, min_samples: int = 10) -> Optional[Dict[int, List[str]]]:
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
        warnings.warn("Cannot cluster archetypes: scikit-learn not installed.", RuntimeWarning)
        return None

    all_vectors = []; agent_epoch_ids = []
    # Extract valid style vectors (ensure they are lists/convert back to numpy)
    for agent_id, lineage in chronicler.lineages.items():
        for i, entry in enumerate(lineage):
            if entry.style_vector is not None:
                 try:
                     # Ensure vector is numpy array for clustering
                     vec = np.array(entry.style_vector)
                     if vec.ndim == 1: # Check if it's a 1D vector
                          all_vectors.append(vec)
                          agent_epoch_ids.append((agent_id, i))
                 except Exception as e:
                      warnings.warn(f"Skipping invalid style vector for {agent_id} epoch {i}: {e}", RuntimeWarning)

    if len(all_vectors) < max(n_clusters, min_samples):
        warnings.warn(f"Insufficient valid data ({len(all_vectors)}) for clustering into {n_clusters} clusters.", RuntimeWarning)
        return None

    print(f"Clustering {len(all_vectors)} style vectors into {n_clusters} archetypes using KMeans...")
    all_vectors_array = np.array(all_vectors)

    try:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto').fit(all_vectors_array) # Use 'auto' n_init
        labels = kmeans.labels_
        # Map agents to their most frequent cluster label
        agent_cluster_counts = defaultdict(lambda: defaultdict(int))
        for i, label in enumerate(labels):
            agent_id, _ = agent_epoch_ids[i]
            agent_cluster_counts[agent_id][label] += 1

        # Assign agent to the cluster they appeared in most often
        agent_dominant_cluster = {}
        for agent_id, counts in agent_cluster_counts.items():
            dominant_label = max(counts, key=counts.get)
            agent_dominant_cluster[agent_id] = dominant_label

        # Group agents by their dominant cluster
        clustered_agents = defaultdict(list)
        for agent_id, label in agent_dominant_cluster.items():
            clustered_agents[label].append(agent_id)

        print(f"Clustering successful. Found {len(clustered_agents)} clusters.")
        # Return dict mapping cluster label to list of agent IDs primarily in that cluster
        return dict(clustered_agents)

    except Exception as e:
        warnings.warn(f"KMeans clustering failed: {e}", RuntimeWarning)
        return None





















