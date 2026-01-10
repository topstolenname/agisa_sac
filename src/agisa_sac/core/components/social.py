import random
import warnings
from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, cast

import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix, lil_matrix

# Dependency checks
try:
    import cupy as cp

    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False
try:
    import community as community_louvain

    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False

# Import framework version
try:
    from .. import FRAMEWORK_VERSION
except ImportError:
    FRAMEWORK_VERSION = "unknown"

# Forward reference for MessageBus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.message_bus import MessageBus


class DynamicSocialGraph:
    """Manages dynamic influence network. Includes serialization."""

    def __init__(
        self,
        num_agents: int,
        agent_ids: List[str],
        use_gpu: bool = False,
        message_bus: Optional["MessageBus"] = None,
    ):  # Add message_bus
        self.num_agents = num_agents
        self.agent_ids = agent_ids
        self.id_to_index = {
            agent_id: i for i, agent_id in enumerate(self.agent_ids)
        }
        self.use_gpu = use_gpu and HAS_CUPY
        self.message_bus = message_bus  # Store reference
        # State
        self.influence_matrix = lil_matrix(
            (num_agents, num_agents), dtype=np.float32
        )
        for i in range(num_agents):
            for j in range(num_agents):
                if i != j:
                    self.influence_matrix[i, j] = random.uniform(0.05, 0.2)
        self.reputation = np.ones(num_agents, dtype=np.float32)
        self._convert_to_csr()
        self.influence_matrix_gpu = None
        self.reputation_gpu = None
        if self.use_gpu:
            self._transfer_to_gpu()
        self.edge_changes_since_last_community_check = 0
        self.last_communities: Optional[List[Set[str]]] = (
            None  # Store as set of agent IDs
        )

    def _convert_to_csr(self):
        self.influence_matrix_csr = self.influence_matrix.tocsr()

    def _transfer_to_gpu(self):
        if HAS_CUPY:
            try:
                self.influence_matrix_gpu = cp.sparse.csr_matrix(
                    (
                        cp.array(self.influence_matrix_csr.data),
                        cp.array(self.influence_matrix_csr.indices),
                        cp.array(self.influence_matrix_csr.indptr),
                    ),
                    shape=self.influence_matrix_csr.shape,
                    dtype=cp.float32,
                )
                self.reputation_gpu = cp.array(
                    self.reputation, dtype=cp.float32
                )
            except Exception as e:
                warnings.warn(
                    f"GPU transfer fail: {e}. CPU fallback.", RuntimeWarning
                )
                self.use_gpu = False
                self.influence_matrix_gpu = None
                self.reputation_gpu = None
        else:
            self.use_gpu = False

    # ... (update_influence, batch_update_influences, update_reputation methods as before) ...
    def update_influence(
        self, influencer: str, influenced: str, change: float
    ):
        if influencer in self.id_to_index and influenced in self.id_to_index:
            i, j = self.id_to_index[influencer], self.id_to_index[influenced]
            if i == j:
                return False
            self.influence_matrix = self.influence_matrix_csr.tolil()
            self.influence_matrix[i, j] = np.clip(
                self.influence_matrix[i, j] + change, 0, 1
            )
            self._convert_to_csr()
            self.edge_changes_since_last_community_check += 1
            if self.use_gpu:
                self._transfer_to_gpu()
            return True
        return False

    def batch_update_influences(self, updates: List[Tuple[str, str, float]]):
        if not updates:
            return
        self.influence_matrix = self.influence_matrix_csr.tolil()
        num_actual_updates = 0
        for influencer, influenced, change in updates:
            if (
                influencer in self.id_to_index
                and influenced in self.id_to_index
            ):
                i, j = (
                    self.id_to_index[influencer],
                    self.id_to_index[influenced],
                )
                if i != j:
                    self.influence_matrix[i, j] = np.clip(
                        self.influence_matrix[i, j] + change, 0, 1
                    )
                    num_actual_updates += 1
        self._convert_to_csr()
        if self.use_gpu:
            self._transfer_to_gpu()
        self.edge_changes_since_last_community_check += num_actual_updates

    def update_reputation(self, agent_id: str, change: float):
        if agent_id in self.id_to_index:
            idx = self.id_to_index[agent_id]
            self.reputation[idx] = np.clip(
                self.reputation[idx] + change, 0.1, 10.0
            )
            if self.use_gpu and self.reputation_gpu is not None:
                self.reputation_gpu[idx] = cp.float32(self.reputation[idx])
            return True
        return False

    def get_peer_influence_for_agent(
        self, agent_id: str, normalize: bool = True
    ) -> Dict[str, float]:
        # ... (logic as before) ...
        if agent_id in self.id_to_index:
            target_idx = self.id_to_index[agent_id]
            influence_on_agent = (
                self.influence_matrix_csr[:, target_idx].toarray().flatten()
            )
            influences = {}
            total_influence: float = 0.0
            for i in range(self.num_agents):
                if i != target_idx and influence_on_agent[i] > 1e-6:
                    influencer_id = self.agent_ids[i]
                    weight = float(influence_on_agent[i])
                    influences[influencer_id] = weight
                    total_influence += weight
            if normalize and total_influence > 1e-6:
                influences = {
                    aid: w / total_influence for aid, w in influences.items()
                }
            return influences
        return {}

    def get_influence_exerted_by_agent(
        self, agent_id: str
    ) -> Dict[str, float]:
        # ... (logic as before) ...
        if agent_id in self.id_to_index:
            influencer_idx = self.id_to_index[agent_id]
            influence_by_agent = (
                self.influence_matrix_csr[influencer_idx].toarray().flatten()
            )
            return {
                self.agent_ids[j]: float(influence_by_agent[j])
                for j in range(self.num_agents)
                if j != influencer_idx and influence_by_agent[j] > 1e-6
            }
        return {}

    def get_top_influencers(
        self, n: int = 5, based_on: str = "outgoing"
    ) -> List[Tuple[str, float]]:
        # ... (logic as before) ...
        n = min(n, self.num_agents)
        scores = None
        xp = (
            cp
            if self.use_gpu and self.influence_matrix_gpu is not None
            else np
        )
        matrix = (
            self.influence_matrix_gpu
            if self.use_gpu and self.influence_matrix_gpu is not None
            else self.influence_matrix_csr
        )
        if based_on == "reputation":
            scores = (
                self.reputation_gpu
                if self.use_gpu and self.reputation_gpu is not None
                else self.reputation
            )
        elif based_on == "incoming":
            scores = matrix.sum(axis=0)
            scores = (
                scores.flatten()
                if isinstance(scores, xp.ndarray)
                else scores.A1 if hasattr(scores, "A1") else scores
            )
        else:
            scores = matrix.sum(axis=1)
            scores = (
                scores.flatten()
                if isinstance(scores, xp.ndarray)
                else scores.A1 if hasattr(scores, "A1") else scores
            )
        if scores is None:
            return []
        scores_cpu = (
            cp.asnumpy(scores)
            if self.use_gpu and isinstance(scores, cp.ndarray)
            else np.asarray(scores).flatten()
        )
        if n < self.num_agents // 2:
            top_indices_unsorted = np.argpartition(scores_cpu, -n)[-n:]
            top_indices = top_indices_unsorted[
                np.argsort(scores_cpu[top_indices_unsorted])
            ][::-1]
        else:
            top_indices = np.argsort(scores_cpu)[-n:][::-1]
        return [(self.agent_ids[i], float(scores_cpu[i])) for i in top_indices]

    def detect_communities(
        self, force_update: bool = False, threshold: float = 0.3
    ) -> Optional[List[Set[str]]]:  # Return Set[str]
        recalculation_threshold = max(10, self.num_agents // 5)
        if (
            not force_update
            and self.last_communities is not None
            and self.edge_changes_since_last_community_check
            < recalculation_threshold
        ):
            return self.last_communities
        G = nx.Graph()
        G.add_nodes_from(self.agent_ids)
        rows, cols = self.influence_matrix_csr.nonzero()
        for i, j in zip(rows, cols):
            weight = self.influence_matrix_csr[i, j]
            if weight >= threshold:
                G.add_edge(
                    self.agent_ids[i], self.agent_ids[j], weight=float(weight)
                )
        communities = None
        if HAS_LOUVAIN:
            try:
                partition = community_louvain.best_partition(
                    G, weight="weight"
                )
                community_map: Dict[int, Set[str]] = defaultdict(set)

                # Use standard loop instead of list comprehension for side effects
                for node, comm_id in partition.items():
                    community_map[comm_id].add(node)

                communities = list(community_map.values())
            except Exception as e:
                warnings.warn(
                    f"Louvain failed: {e}. Fallback.", RuntimeWarning
                )
                # Fall through to greedy
        if communities is None:  # Fallback if Louvain failed or not available
            try:
                communities = [
                    set(c)
                    for c in nx.community.greedy_modularity_communities(G)
                ]
            except Exception as e:
                warnings.warn(
                    f"Community detection failed: {e}", RuntimeWarning
                )
        self.last_communities = communities
        self.edge_changes_since_last_community_check = 0
        if self.message_bus and communities is not None:
            self.message_bus.publish(
                "communities_detected",
                {
                    "num": len(communities),
                    "sizes": [len(c) for c in communities],
                },
            )
        return self.last_communities

    def to_dict(self) -> Dict:
        """Returns serializable state dictionary."""
        coo = self.influence_matrix_csr.tocoo()
        matrix_state = list(
            zip(coo.row.tolist(), coo.col.tolist(), coo.data.tolist())
        )
        return {
            "version": FRAMEWORK_VERSION,
            "influence_matrix_coo": matrix_state,
            "reputation": self.reputation.tolist(),
            "last_communities": (
                [list(c) for c in self.last_communities]
                if self.last_communities
                else None
            ),  # Save as list of lists
            "edge_changes": self.edge_changes_since_last_community_check,
        }

    def load_state(self, state: Dict):
        """Loads state from dictionary."""
        loaded_version = state.get("version")
        if loaded_version != FRAMEWORK_VERSION:
            warnings.warn(
                f"Loading social graph v '{loaded_version}' into v '{FRAMEWORK_VERSION}'.",
                UserWarning,
            )
        self.reputation = np.array(
            state.get("reputation", np.ones(self.num_agents)), dtype=np.float32
        )
        matrix_state = state.get("influence_matrix_coo")
        if matrix_state:
            try:
                rows, cols, data = zip(*matrix_state)
                self.influence_matrix_csr = csr_matrix(
                    (data, (rows, cols)),
                    shape=(self.num_agents, self.num_agents),
                    dtype=np.float32,
                )
                self.influence_matrix = self.influence_matrix_csr.tolil()
            except ValueError:  # Handle case where matrix_state might be empty
                warnings.warn(
                    "Could not reconstruct influence matrix from state "
                    "(empty or invalid COO data?). Reinitializing.",
                    RuntimeWarning,
                )
                self.influence_matrix = lil_matrix(
                    (self.num_agents, self.num_agents), dtype=np.float32
                )
                self._convert_to_csr()
        else:
            self.influence_matrix = lil_matrix(
                (self.num_agents, self.num_agents), dtype=np.float32
            )
            self._convert_to_csr()
        loaded_communities = state.get("last_communities")
        self.last_communities = (
            [set(c) for c in loaded_communities]
            if loaded_communities
            else None
        )  # Convert back to set
        self.edge_changes_since_last_community_check = state.get(
            "edge_changes", 0
        )
        if self.use_gpu:
            self._transfer_to_gpu()  # Refresh GPU state
