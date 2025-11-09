import hashlib
import json
import math
import random
import time
import warnings
from collections import defaultdict
from typing import Any, Dict, List, Optional

import numpy as np

# Dependency check for SentenceTransformer
try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMER = True
except ImportError:
    HAS_SENTENCE_TRANSFORMER = False
    # Warning is handled within MemoryContinuumLayer __init__

# Import framework version (assuming it's accessible, e.g., from top-level __init__)
try:
    from .. import FRAMEWORK_VERSION
except ImportError:
    FRAMEWORK_VERSION = "unknown"

# Forward reference for MessageBus if needed for type hints
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.message_bus import MessageBus


class MemoryEncapsulation:
    """Encapsulates a memory with state and methods. Includes serialization."""

    # --- Content from agisa_framework_serialization_v1 ---
    def __init__(
        self,
        memory_id: str,
        content: Dict,
        importance: float = 0.5,
        confidence: float = 1.0,
        encoding_strength: float = 0.8,
        created_at: Optional[float] = None,
        last_accessed: Optional[float] = None,
        access_count: int = 0,
        embedding: Optional[np.ndarray] = None,
        theme: Optional[str] = None,
    ):
        self.memory_id = memory_id
        self.content = content
        self.importance = np.clip(importance, 0.0, 1.0)
        self.confidence = np.clip(confidence, 0.0, 1.0)
        self.encoding_strength = np.clip(encoding_strength, 0.1, 1.0)
        self.created_at = created_at if created_at is not None else time.time()
        self.last_accessed = (
            last_accessed if last_accessed is not None else self.created_at
        )
        self.access_count = access_count
        self.verification_hash = self._generate_hash(content)
        self.embedding = embedding
        self.theme = (
            theme if theme is not None else content.get("theme", "general")
        )

    def access(self) -> Dict:
        self.last_accessed = time.time()
        self.access_count += 1
        return self.content

    def is_corrupted(self) -> bool:
        return self._generate_hash(self.content) != self.verification_hash

    def attempt_modification(
        self, new_content: Dict, external_influence: float
    ) -> bool:
        protection = (self.importance * 0.4 + self.encoding_strength * 0.6) * (
            1 - np.clip(external_influence, 0.0, 1.0)
        )
        if random.random() > protection:
            self.content = new_content
            self.verification_hash = self._generate_hash(new_content)
            self.confidence *= 0.8
            self.theme = new_content.get("theme", self.theme)
            return True
        return False

    def reinforce(self, strength_increase: float = 0.1):
        self.encoding_strength = min(
            1.0, self.encoding_strength + strength_increase
        )

    def decay(self, decay_rate: float = 0.05) -> float:
        time_since_access = (time.time() - self.last_accessed) / 86400  # Days
        decay_amount = (
            decay_rate * time_since_access * (1 - self.importance * 0.5)
        )
        self.encoding_strength = max(
            0.1, self.encoding_strength - min(decay_amount, 0.2)
        )
        return decay_amount

    def calculate_retrieval_strength(self) -> float:
        recency = math.exp(-0.1 * (time.time() - self.last_accessed) / 86400)
        return (
            recency * 0.3
            + self.importance * 0.3
            + self.encoding_strength * 0.4
        )

    def set_embedding(self, embedding: np.ndarray):
        self.embedding = embedding

    def _generate_hash(self, content: Dict) -> str:
        try:
            content_string = json.dumps(content, sort_keys=True).encode()
        except TypeError:
            content_string = str(content).encode()
        return hashlib.md5(content_string).hexdigest()

    def to_dict(self, include_embedding: bool = False) -> Dict:
        state = {
            "memory_id": self.memory_id,
            "content": self.content,
            "theme": self.theme,
            "importance": self.importance,
            "confidence": self.confidence,
            "encoding_strength": self.encoding_strength,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "verification_hash": self.verification_hash,
        }
        if include_embedding and self.embedding is not None:
            state["embedding"] = self.embedding.tolist()
        return state

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEncapsulation":
        embedding = (
            np.array(data["embedding"])
            if "embedding" in data and data["embedding"] is not None
            else None
        )
        instance = cls(
            memory_id=data["memory_id"],
            content=data["content"],
            importance=data.get("importance", 0.5),
            confidence=data.get("confidence", 1.0),
            encoding_strength=data.get("encoding_strength", 0.8),
            created_at=data.get("created_at"),
            last_accessed=data.get("last_accessed"),
            access_count=data.get("access_count", 0),
            embedding=embedding,
            theme=data.get("theme"),
        )
        loaded_hash = data.get("verification_hash")
        if (
            loaded_hash
            and instance._generate_hash(instance.content) != loaded_hash
        ):
            warnings.warn(
                f"Memory {instance.memory_id}: Hash mismatch on load.",
                RuntimeWarning,
            )
            instance.confidence *= 0.5
        return instance


class MemoryContinuumLayer:
    """Enhanced memory system for an agent. Includes serialization."""

    # --- Content from agisa_framework_serialization_v1 ---
    def __init__(
        self,
        agent_id: str,
        capacity: int = 100,
        use_semantic: bool = True,
        message_bus: Optional["MessageBus"] = None,
    ):  # Use forward ref string
        self.agent_id = agent_id
        self.capacity = capacity
        self.use_semantic = use_semantic and HAS_SENTENCE_TRANSFORMER
        self.message_bus = message_bus
        self.memories: Dict[str, MemoryEncapsulation] = {}
        self.memory_indices = {"term": defaultdict(list)}
        self.last_update = time.time()
        self.encoder = None
        if self.use_semantic:
            self._initialize_encoder()

    def _initialize_encoder(self):
        if self.use_semantic and self.encoder is None:
            try:
                self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                warnings.warn(
                    f"Agent {self.agent_id}: No ST model: {e}. Semantic off.",
                    RuntimeWarning,
                )
                self.use_semantic = False

    def add_memory(self, content: Dict, importance: float = 0.5) -> str:
        if self.use_semantic and self.encoder is None:
            self._initialize_encoder()
        memory_id = f"mem_{self.agent_id}_{int(time.time())}_{random.randint(1000, 9999)}"
        memory = MemoryEncapsulation(memory_id, content, importance)
        if self.use_semantic and self.encoder:
            try:
                content_str = json.dumps(content, sort_keys=True)
                embedding = self.encoder.encode([content_str])[0]
                memory.set_embedding(embedding)
            except Exception as e:
                warnings.warn(
                    f"Agent {self.agent_id}: Mem encode fail {memory_id}: {e}",
                    RuntimeWarning,
                )
        self.memories[memory_id] = memory
        self._update_indices(memory_id, content)
        if len(self.memories) > self.capacity:
            self._remove_weakest_memory()
        if self.message_bus:
            self.message_bus.publish(
                "memory_added",
                {
                    "agent_id": self.agent_id,
                    "memory_id": memory_id,
                    "importance": importance,
                    "theme": memory.theme,
                },
            )
        return memory_id

    def retrieve_memory(
        self, query: str, threshold: float = 0.3, limit: int = 10
    ) -> List[Dict]:
        if self.use_semantic and self.encoder is None:
            self._initialize_encoder()
        matches = {}  # Code combines term and semantic search results
        # Term search
        query_terms = set(query.lower().split())
        term_relevance_scores = defaultdict(float)
        if query_terms:
            for term in query_terms:
                for memory_id in self.memory_indices["term"].get(term, []):
                    term_relevance_scores[memory_id] += 0.1
            for memory_id, term_relevance in term_relevance_scores.items():
                if memory_id in self.memories:
                    memory = self.memories[memory_id]
                    score = memory.calculate_retrieval_strength() * (
                        1 + term_relevance
                    )
                    if score >= threshold:
                        match_data = memory.to_dict()
                        match_data["relevance_score"] = score
                        match_data["match_type"] = "term"
                        matches[memory_id] = match_data
        # Semantic search
        if self.use_semantic and self.encoder and query.strip():
            try:
                query_embedding = self.encoder.encode([query])[0]
                query_norm = np.linalg.norm(query_embedding)
                if query_norm > 1e-6:
                    mem_ids = [
                        mid
                        for mid, mem in self.memories.items()
                        if mem.embedding is not None
                    ]
                    if mem_ids:
                        mem_embeddings = np.array(
                            [self.memories[mid].embedding for mid in mem_ids]
                        )
                        mem_norms = np.linalg.norm(mem_embeddings, axis=1)
                        valid_indices = mem_norms > 1e-6
                        if np.any(valid_indices):
                            mem_embeddings_valid = mem_embeddings[
                                valid_indices
                            ]
                            mem_norms_valid = mem_norms[valid_indices]
                            mem_ids_valid = np.array(mem_ids)[valid_indices]
                            similarities = np.dot(
                                mem_embeddings_valid, query_embedding
                            ) / (mem_norms_valid * query_norm)
                            for i, memory_id in enumerate(mem_ids_valid):
                                similarity = similarities[i]
                                if similarity >= threshold:
                                    memory = self.memories[memory_id]
                                    score = (
                                        memory.calculate_retrieval_strength()
                                        * similarity
                                    )
                                    match_type = "semantic"
                                    if memory_id in matches:
                                        if (
                                            score
                                            > matches[memory_id][
                                                "relevance_score"
                                            ]
                                        ):
                                            matches[memory_id][
                                                "relevance_score"
                                            ] = score
                                            matches[memory_id][
                                                "match_type"
                                            ] = "hybrid"
                                    else:
                                        match_data = memory.to_dict()
                                        match_data["relevance_score"] = score
                                        match_data["match_type"] = match_type
                                        matches[memory_id] = match_data
            except Exception as e:
                warnings.warn(
                    f"Agent {self.agent_id}: Semantic fail query '{query}': {e}",
                    RuntimeWarning,
                )
        # Combine and finalize
        sorted_matches = sorted(
            matches.values(), key=lambda x: x["relevance_score"], reverse=True
        )
        for match in sorted_matches[:limit]:
            if match["memory_id"] in self.memories:
                self.memories[match["memory_id"]].access()
        return sorted_matches[:limit]

    def update_all_memories(self):
        removed_count = 0
        corrupted_count = 0
        memory_ids_to_remove = []
        for memory_id, memory in list(self.memories.items()):
            memory.decay()
            if memory.is_corrupted():
                corrupted_count += 1
                memory_ids_to_remove.append(memory_id)
                continue
            if memory.encoding_strength < 0.15:
                memory_ids_to_remove.append(memory_id)
        for memory_id in memory_ids_to_remove:
            if self._remove_memory(memory_id):
                removed_count += 1
        self.last_update = time.time()
        if self.message_bus and (removed_count > 0 or corrupted_count > 0):
            self.message_bus.publish(
                "memory_maintenance",
                {
                    "agent_id": self.agent_id,
                    "removed": removed_count,
                    "corrupted": corrupted_count,
                    "remain": len(self.memories),
                },
            )

    def reinforce_memory(self, memory_id: str, strength: float = 0.1) -> bool:
        if memory_id in self.memories:
            self.memories[memory_id].reinforce(strength)
            return True
        return False

    def get_memory_by_id(self, memory_id: str) -> Optional[Dict]:
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            memory.access()
            return memory.to_dict()
        return None

    def link_memories(
        self, source_id: str, target_id: str, link_type: str = "related"
    ) -> bool:
        if source_id in self.memories and target_id in self.memories:
            source_memory = self.memories[source_id]
            source_content = source_memory.content
            if "links" not in source_content:
                source_content["links"] = []
            link_exists = any(
                link.get("target_id") == target_id
                for link in source_content.get("links", [])
            )
            if link_exists:
                return False
            source_content["links"].append(
                {
                    "target_id": target_id,
                    "link_type": link_type,
                    "created_at": time.time(),
                }
            )
            source_memory.content = source_content
            source_memory.verification_hash = source_memory._generate_hash(
                source_content
            )
            return True
        return False

    def _update_indices(self, memory_id: str, content: Dict):
        text_to_index = ""

        def extract_strings(item):
            nonlocal text_to_index
            (
                [extract_strings(v) for v in item.values()]
                if isinstance(item, dict)
                else (
                    [extract_strings(v) for v in item]
                    if isinstance(item, list)
                    else None
                )
            )
            text_to_index += item + " " if isinstance(item, str) else ""

        extract_strings(content)
        terms = set(text_to_index.lower().split())
        for term in terms:
            if memory_id not in self.memory_indices["term"][term]:
                self.memory_indices["term"][term].append(memory_id)

    def _remove_memory(self, memory_id: str) -> bool:
        if memory_id in self.memories:
            content = self.memories[memory_id].content
            text_to_index = ""

            def extract_strings(item):
                nonlocal text_to_index
                (
                    [extract_strings(v) for v in item.values()]
                    if isinstance(item, dict)
                    else (
                        [extract_strings(v) for v in item]
                        if isinstance(item, list)
                        else None
                    )
                )
                text_to_index += item + " " if isinstance(item, str) else ""

            extract_strings(content)
            terms = set(text_to_index.lower().split())
            for term in terms:
                if term in self.memory_indices["term"]:
                    if memory_id in self.memory_indices["term"][term]:
                        self.memory_indices["term"][term].remove(memory_id)
                    if not self.memory_indices["term"][term]:
                        del self.memory_indices["term"][term]
            del self.memories[memory_id]
            return True
        return False

    def _remove_weakest_memory(self):
        if not self.memories:
            return
        try:
            weakest_id = min(
                self.memories,
                key=lambda mid: self.memories[
                    mid
                ].calculate_retrieval_strength(),
            )
            self._remove_memory(weakest_id)
        except ValueError:
            warnings.warn(
                f"Agent {self.agent_id}: Weakest memory fail.", RuntimeWarning
            )

    def get_current_focus_theme(self) -> str:
        latest_focus_mem = None
        latest_ts = 0
        for mem in self.memories.values():
            if (
                mem.content.get("type") == "current_focus"
                and mem.created_at > latest_ts
            ):
                latest_focus_mem = mem
                latest_ts = mem.created_at
        if latest_focus_mem:
            return latest_focus_mem.theme
        if self.memories:
            try:
                latest_mem_id = max(
                    self.memories,
                    key=lambda mid: self.memories[mid].created_at,
                )
                return self.memories[latest_mem_id].theme
            except ValueError:
                return "general"
        return "general"

    def _rebuild_indices(self):
        self.memory_indices = {"term": defaultdict(list)}
        for memory_id, memory in self.memories.items():
            self._update_indices(memory_id, memory.content)

    def to_dict(self, include_embeddings: bool = False) -> Dict:
        return {
            "version": FRAMEWORK_VERSION,
            "agent_id": self.agent_id,
            "capacity": self.capacity,
            "use_semantic_config": self.use_semantic,
            "last_update": self.last_update,
            "memories": {
                mid: mem.to_dict(include_embedding=include_embeddings)
                for mid, mem in self.memories.items()
            },
        }

    def backup_to_gcs(self, bucket: str, path: str) -> None:
        """Serialize and upload memory state to Google Cloud Storage."""
        import json
        import tempfile

        from ..gcp.gcs_io import upload_file

        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            json.dump(self.to_dict(include_embeddings=True), tmp)
            tmp_path = tmp.name
        upload_file(bucket, tmp_path, path)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], message_bus: Optional["MessageBus"] = None
    ) -> "MemoryContinuumLayer":
        loaded_version = data.get("version")
        agent_id = data["agent_id"]
        if loaded_version != FRAMEWORK_VERSION:
            warnings.warn(
                f"Agent {agent_id}: Loading memory v '{loaded_version}' into v '{FRAMEWORK_VERSION}'.",
                UserWarning,
            )
        instance = cls(
            agent_id=agent_id,
            capacity=data.get("capacity", 100),
            use_semantic=data.get("use_semantic_config", True),
            message_bus=message_bus,
        )
        instance.last_update = data.get("last_update", time.time())
        instance.memories = {}
        memories_data = data.get("memories", {})
        for mid, mem_data in memories_data.items():
            try:
                mem_instance = MemoryEncapsulation.from_dict(mem_data)
                instance.memories[mid] = mem_instance
                # Optional immediate hash check
                # loaded_hash = mem_data.get('verification_hash');
                # if loaded_hash and mem_instance._generate_hash(
                #     mem_instance.content) != loaded_hash:
                #     warnings.warn(
                #         f"Mem {mid} hash mismatch.", RuntimeWarning)
            except Exception as e:
                warnings.warn(
                    f"Failed load mem {mid} for {agent_id}: {e}",
                    RuntimeWarning,
                )
        instance._rebuild_indices()  # Rebuild after loading all
        return instance
