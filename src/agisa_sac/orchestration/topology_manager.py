"""
Topology Orchestration Manager with TDA-based Coordination

This module implements topological data analysis (TDA) for agent network coordination,
using persistent homology to detect fragmentation, overconnection, and coverage gaps.
"""

import tempfile
from datetime import datetime
from typing import Dict, List, Optional

import networkx as nx
import numpy as np

try:
    from google.cloud import firestore, storage
    from ripser import ripser

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    firestore = None
    storage = None
    ripser = None


class TopologyOrchestrationManager:
    """
    TDA-based coordination with proper metric handling.

    Uses persistent homology to analyze agent networks and detect:
    - Fragmentation (disconnected components)
    - Overconnection (redundant pathways)
    - Coverage gaps (topological voids)
    """

    # Constants for normalization
    F_MAX = 100  # Max frequency in window
    PERSISTENCE_THRESHOLD = 0.1

    def __init__(
        self,
        firestore_client,
        storage_client,
        project_id: str,
        topology_bucket: Optional[str] = None,
    ):
        """
        Initialize the topology manager.

        Args:
            firestore_client: Firestore client instance
            storage_client: GCS client instance
            project_id: GCP project ID
            topology_bucket: GCS bucket for topology snapshots (defaults to {project_id}-agisa-sac-topology)
        """
        if not HAS_DEPS:
            raise ImportError(
                "google-cloud-firestore, google-cloud-storage, and ripser "
                "are required for TopologyOrchestrationManager"
            )

        self.db = firestore_client
        self.storage = storage_client
        self.project_id = project_id
        self.topology_bucket = topology_bucket or f"{project_id}-agisa-sac-topology"
        self.agent_registry: Dict = {}
        self.interaction_graph = nx.DiGraph()

        # Cache for performance
        self._distance_cache: Dict = {}
        self._cache_expiry = None

    def register_agent(self, agent):
        """
        Register agent in topology system.

        Args:
            agent: AGISAAgent instance to register
        """
        self.agent_registry[agent.agent_id] = agent
        self.interaction_graph.add_node(
            agent.agent_id,
            name=agent.name,
            tools=list(agent.tools.keys()),
            model=agent.model,
        )

        # Invalidate cache
        self._distance_cache = {}

    def agent_distance(self, agent_i, agent_j, eps: float = 1e-6) -> float:
        """
        Proper metric distance between agents.
        Ensures: d(i,j) = d(j,i), d(i,i) = 0, triangle inequality (approximately)

        Args:
            agent_i: First agent
            agent_j: Second agent
            eps: Small epsilon to prevent division by zero

        Returns:
            Distance value in [0, 1]
        """
        # Check cache
        cache_key = tuple(sorted([agent_i.agent_id, agent_j.agent_id]))
        if cache_key in self._distance_cache:
            return self._distance_cache[cache_key]

        # Tool overlap (Jaccard distance)
        tools_i = set(agent_i.tools.keys())
        tools_j = set(agent_j.tools.keys())
        intersection = len(tools_i & tools_j)
        union = len(tools_i | tools_j)
        J = intersection / max(union, 1)
        tool_d = 1.0 - J  # [0, 1]

        # Interaction frequency (normalized)
        f = self._get_interaction_frequency(agent_i.agent_id, agent_j.agent_id)
        f_norm = min(f / (self.F_MAX + eps), 1.0)
        freq_d = 1.0 - f_norm  # [0, 1]

        # Handoff success rate
        s = self._get_handoff_success_rate(agent_i.agent_id, agent_j.agent_id)
        success_d = 1.0 - s  # [0, 1]

        # Weighted combination
        d = 0.4 * tool_d + 0.3 * freq_d + 0.3 * success_d
        d = max(0.0, min(1.0, d))  # Clamp to [0, 1]

        # Cache
        self._distance_cache[cache_key] = d
        return d

    async def compute_coordination_topology(self) -> Dict:
        """
        Compute persistence diagrams with proper metric handling.

        Returns:
            Dictionary with:
            - diagrams: Persistence diagrams (H0, H1, H2)
            - features: Extracted topological features
            - coordination_quality: Quality score [0, 1]
            - suggested_optimizations: List of actionable suggestions
            - snapshot_id: Firestore snapshot ID
        """
        agents = list(self.agent_registry.values())
        n = len(agents)

        if n < 2:
            return {
                "diagrams": [],
                "features": {},
                "coordination_quality": 0.0,
                "suggested_optimizations": ["Need at least 2 agents"],
            }

        # Build distance matrix
        D = np.zeros((n, n), dtype=float)
        for i in range(n):
            for j in range(i + 1, n):
                d = self.agent_distance(agents[i], agents[j])
                D[i, j] = d
                D[j, i] = d  # Ensure symmetry

        # Diagonal is zero by construction
        np.fill_diagonal(D, 0.0)

        # Symmetrize (redundant but explicit)
        D = 0.5 * (D + D.T)

        # Verify metric properties
        assert np.allclose(D, D.T), "Distance matrix not symmetric"
        assert np.all(np.diag(D) == 0), "Diagonal not zero"

        # Compute persistence
        result = ripser(D, distance_matrix=True, maxdim=2)
        diagrams = result["dgms"]

        # Extract features
        features = self._extract_topological_features(diagrams)

        # Assess quality
        quality = self._assess_coordination_quality(features)

        # Generate suggestions
        suggestions = self._suggest_optimizations(features, D, agents)

        # Store snapshot
        snapshot_id = await self._store_topology_snapshot(
            diagrams, features, quality, D, n
        )

        return {
            "diagrams": diagrams,
            "features": features,
            "coordination_quality": quality,
            "suggested_optimizations": suggestions,
            "snapshot_id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
        }

    def _extract_topological_features(self, diagrams: List[np.ndarray]) -> Dict:
        """
        Extract persistent features above threshold.

        Args:
            diagrams: List of persistence diagrams

        Returns:
            Dictionary with H0, H1, H2 features
        """
        features = {"h0_components": [], "h1_loops": [], "h2_voids": []}

        for dim, diagram in enumerate(diagrams):
            if len(diagram) == 0:
                continue

            # Filter by persistence
            persistence = diagram[:, 1] - diagram[:, 0]
            mask = persistence > self.PERSISTENCE_THRESHOLD
            persistent = diagram[mask]

            if dim == 0:
                features["h0_components"] = persistent.tolist()
            elif dim == 1:
                features["h1_loops"] = persistent.tolist()
            elif dim == 2:
                features["h2_voids"] = persistent.tolist()

        return features

    def _assess_coordination_quality(self, features: Dict) -> float:
        """
        Quality scoring:
        - Fewer H0 components = better connectivity
        - Moderate H1 loops = good redundancy
        - Fewer H2 voids = better coverage

        Args:
            features: Extracted topological features

        Returns:
            Quality score in [0, 1]
        """
        h0_count = len(features["h0_components"])
        h1_count = len(features["h1_loops"])
        h2_count = len(features["h2_voids"])

        h0_score = 1.0 / (1.0 + h0_count)
        h1_score = min(h1_count / 5.0, 1.0)  # Target ~5 loops
        h2_score = 1.0 / (1.0 + h2_count)

        quality = 0.5 * h0_score + 0.3 * h1_score + 0.2 * h2_score
        return quality

    def _suggest_optimizations(
        self, features: Dict, distance_matrix: np.ndarray, agents: List
    ) -> List[str]:
        """
        Actionable topology-informed suggestions.

        Args:
            features: Extracted features
            distance_matrix: Distance matrix between agents
            agents: List of agents

        Returns:
            List of actionable suggestions
        """
        suggestions = []

        h0_count = len(features["h0_components"])
        h1_count = len(features["h1_loops"])
        h2_count = len(features["h2_voids"])

        # FRAGMENTATION
        if h0_count > 2:
            # Find bridges between disconnected components using clustering
            from sklearn.cluster import AgglomerativeClustering

            # Use agglomerative clustering to identify components
            clustering = AgglomerativeClustering(
                n_clusters=h0_count,
                metric="precomputed",
                linkage="average",
            )
            labels = clustering.fit_predict(distance_matrix)

            # Find closest pair between different clusters
            n = len(agents)
            min_cross_dist = float("inf")
            bridge_pair = None

            for i in range(n):
                for j in range(i + 1, n):
                    # Only consider pairs in different clusters
                    if labels[i] != labels[j]:
                        if distance_matrix[i, j] < min_cross_dist:
                            min_cross_dist = distance_matrix[i, j]
                            bridge_pair = (
                                agents[i].name,
                                agents[j].name,
                                labels[i],
                                labels[j],
                            )

            if bridge_pair:
                suggestions.append(
                    f"FRAGMENTATION: {h0_count} disconnected clusters detected. "
                    f"Consider adding cross-cluster handoffs between {bridge_pair[0]} "
                    f"(cluster {bridge_pair[2]}) and {bridge_pair[1]} "
                    f"(cluster {bridge_pair[3]}) - distance: {min_cross_dist:.3f}"
                )

        # OVERCONNECTION
        if h1_count > 10:
            suggestions.append(
                f"OVERCONNECTION: {h1_count} redundant pathways detected. "
                "Consider consolidating overlapping capabilities into shared service agents."
            )

        # COVERAGE GAPS
        if h2_count > 0:
            suggestions.append(
                f"COVERAGE GAPS: {h2_count} topological voids detected. "
                "Consider adding specialized agents for uncovered capability domains."
            )

        return suggestions

    async def _store_topology_snapshot(
        self,
        diagrams: List[np.ndarray],
        features: Dict,
        quality: float,
        distance_matrix: np.ndarray,
        n: int,
    ) -> str:
        """
        Store topology snapshot to Firestore + GCS.

        Args:
            diagrams: Persistence diagrams
            features: Extracted features
            quality: Quality score
            distance_matrix: Distance matrix
            n: Number of agents

        Returns:
            Snapshot ID
        """
        timestamp = datetime.now()
        snapshot_id = timestamp.strftime("%Y%m%d_%H%M%S")

        # Store metadata in Firestore
        self.db.collection("topology_snapshots").document(snapshot_id).set(
            {
                "timestamp": firestore.SERVER_TIMESTAMP,
                "n_agents": n,
                "coordination_quality": quality,
                "features": features,
                "persistence_threshold": self.PERSISTENCE_THRESHOLD,
                "diag_uri": f"gs://{self.topology_bucket}/{snapshot_id}/diagrams.npz",
            }
        )

        # Store diagrams in GCS
        bucket = self.storage.bucket(self.topology_bucket)
        blob = bucket.blob(f"{snapshot_id}/diagrams.npz")

        # Save to temporary file then upload
        with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as tmp:
            np.savez_compressed(
                tmp.name,
                h0=diagrams[0],
                h1=diagrams[1] if len(diagrams) > 1 else np.array([]),
                h2=diagrams[2] if len(diagrams) > 2 else np.array([]),
                distance_matrix=distance_matrix,
            )
            blob.upload_from_filename(tmp.name)

        return snapshot_id

    def _get_interaction_frequency(self, agent_i_id: str, agent_j_id: str) -> int:
        """
        Get interaction count from Firestore.

        Args:
            agent_i_id: First agent ID
            agent_j_id: Second agent ID

        Returns:
            Interaction count
        """
        query = (
            self.db.collection("runs")
            .where("agent_id", "==", agent_i_id)
            .where("exit", "==", "handoff")
            .limit(1000)
        )

        count = 0
        for doc in query.stream():
            data = doc.to_dict()
            if data.get("handoff_to") == agent_j_id:
                count += 1

        return count

    def _get_handoff_success_rate(self, agent_i_id: str, agent_j_id: str) -> float:
        """
        Compute handoff success rate.

        Args:
            agent_i_id: First agent ID
            agent_j_id: Second agent ID

        Returns:
            Success rate in [0, 1]
        """
        total = self._get_interaction_frequency(agent_i_id, agent_j_id)
        if total == 0:
            return 0.5  # Neutral prior

        # Count successful handoffs
        query = (
            self.db.collection("runs")
            .where("agent_id", "==", agent_j_id)
            .where("status", "==", "completed")
            .limit(1000)
        )

        success = 0
        for doc in query.stream():
            data = doc.to_dict()
            if data.get("handoff_from") == agent_i_id:
                success += 1

        return success / max(total, 1)
