import json
import time
import uuid
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict
import logging


@dataclass
class VectorClock:
    """Vector clock for distributed timestamp ordering"""
    clocks: Dict[str, int] = field(default_factory=dict)

    def increment(self, node_id: str) -> 'VectorClock':
        new_clocks = self.clocks.copy()
        new_clocks[node_id] = new_clocks.get(node_id, 0) + 1
        return VectorClock(new_clocks)

    def update(self, other: 'VectorClock') -> 'VectorClock':
        new_clocks = self.clocks.copy()
        for node_id, clock in other.clocks.items():
            new_clocks[node_id] = max(new_clocks.get(node_id, 0), clock)
        return VectorClock(new_clocks)

    def compare(self, other: 'VectorClock') -> str:
        all_nodes = set(self.clocks.keys()) | set(other.clocks.keys())
        self_less = False
        self_greater = False
        for node in all_nodes:
            self_clock = self.clocks.get(node, 0)
            other_clock = other.clocks.get(node, 0)
            if self_clock < other_clock:
                self_less = True
            elif self_clock > other_clock:
                self_greater = True
        if not self_less and not self_greater:
            return 'equal'
        elif self_less and not self_greater:
            return 'before'
        elif self_greater and not self_less:
            return 'after'
        else:
            return 'concurrent'


@dataclass
class CRDTMemoryEntry:
    """Individual memory entry with CRDT metadata"""
    entry_id: str
    content: Dict[str, Any]
    vector_clock: VectorClock
    node_id: str
    created_at: datetime
    memory_type: str
    importance_score: float = 1.0
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.created_at


@dataclass
class MemoryMergeConflict:
    """Represents a conflict that occurred during memory merging"""
    conflict_id: str
    entry_id: str
    conflicting_entries: List[CRDTMemoryEntry]
    resolution_strategy: str
    resolved_entry: Optional[CRDTMemoryEntry] = None
    manual_review_required: bool = False


class CRDTMemoryLayer:
    """Conflict-free Replicated Data Type implementation for distributed memory."""

    def __init__(self, node_id: str, max_memory_size: int = 10000):
        self.node_id = node_id
        self.max_memory_size = max_memory_size
        self.memories: Dict[str, CRDTMemoryEntry] = {}
        self.vector_clock = VectorClock()
        self.tombstones: Set[str] = set()
        self.merge_conflicts: List[MemoryMergeConflict] = []
        self.resolution_strategies = {
            "last_writer_wins": self._resolve_last_writer_wins,
            "semantic_merge": self._resolve_semantic_merge,
            "importance_weighted": self._resolve_importance_weighted,
            "consensus_required": self._resolve_consensus_required,
        }
        self.sync_history: List[Dict] = []
        self.compression_ratio = 1.0
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"CRDT Memory Layer initialized for node {node_id}")

    def add_memory(self, content: Dict[str, Any], memory_type: str = "episodic", importance_score: float = 1.0) -> str:
        entry_id = f"{self.node_id}_{uuid.uuid4().hex[:12]}"
        self.vector_clock = self.vector_clock.increment(self.node_id)
        memory_entry = CRDTMemoryEntry(
            entry_id=entry_id,
            content=content,
            vector_clock=self.vector_clock,
            node_id=self.node_id,
            created_at=datetime.now(timezone.utc),
            memory_type=memory_type,
            importance_score=importance_score,
        )
        self.memories[entry_id] = memory_entry
        if len(self.memories) > self.max_memory_size:
            self._cleanup_old_memories()
        self.logger.debug(f"Added memory {entry_id} of type {memory_type}")
        return entry_id

    def update_memory(self, entry_id: str, content_updates: Dict[str, Any]) -> bool:
        if entry_id not in self.memories or entry_id in self.tombstones:
            self.logger.warning(f"Cannot update non-existent memory {entry_id}")
            return False
        self.vector_clock = self.vector_clock.increment(self.node_id)
        old_entry = self.memories[entry_id]
        updated_content = old_entry.content.copy()
        updated_content.update(content_updates)
        new_entry = CRDTMemoryEntry(
            entry_id=entry_id,
            content=updated_content,
            vector_clock=self.vector_clock,
            node_id=self.node_id,
            created_at=old_entry.created_at,
            memory_type=old_entry.memory_type,
            importance_score=old_entry.importance_score,
            access_count=old_entry.access_count + 1,
            last_accessed=datetime.now(timezone.utc),
        )
        self.memories[entry_id] = new_entry
        return True

    def delete_memory(self, entry_id: str) -> bool:
        if entry_id not in self.memories:
            return False
        self.tombstones.add(entry_id)
        del self.memories[entry_id]
        self.vector_clock = self.vector_clock.increment(self.node_id)
        self.logger.debug(f"Deleted memory {entry_id}")
        return True

    def get_memory(self, entry_id: str) -> Optional[CRDTMemoryEntry]:
        if entry_id not in self.memories or entry_id in self.tombstones:
            return None
        memory = self.memories[entry_id]
        memory.access_count += 1
        memory.last_accessed = datetime.now(timezone.utc)
        return memory

    def merge_remote_state(
        self,
        remote_memories: Dict[str, CRDTMemoryEntry],
        remote_vector_clock: VectorClock,
        remote_tombstones: Set[str],
    ) -> Dict[str, str]:
        merge_results: Dict[str, str] = {}
        conflicts_detected = 0
        self.vector_clock = self.vector_clock.update(remote_vector_clock)
        for entry_id, remote_entry in remote_memories.items():
            if entry_id in remote_tombstones:
                continue
            merge_status = self._merge_single_entry(entry_id, remote_entry)
            merge_results[entry_id] = merge_status
            if merge_status.startswith("conflict"):
                conflicts_detected += 1
        self.tombstones.update(remote_tombstones)
        for tombstone_id in remote_tombstones:
            if tombstone_id in self.memories:
                del self.memories[tombstone_id]
                merge_results[tombstone_id] = "deleted_by_remote"
        sync_stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "remote_node": remote_vector_clock.clocks,
            "entries_processed": len(remote_memories),
            "conflicts_detected": conflicts_detected,
            "merge_results": merge_results,
        }
        self.sync_history.append(sync_stats)
        self.logger.info(f"Merged state: {len(remote_memories)} entries, {conflicts_detected} conflicts")
        return merge_results

    def _merge_single_entry(self, entry_id: str, remote_entry: CRDTMemoryEntry) -> str:
        if entry_id not in self.memories:
            if entry_id not in self.tombstones:
                self.memories[entry_id] = remote_entry
                return "added_from_remote"
            return "ignored_tombstoned"
        local_entry = self.memories[entry_id]
        clock_relation = local_entry.vector_clock.compare(remote_entry.vector_clock)
        if clock_relation == "after":
            return "local_newer"
        elif clock_relation == "before":
            self.memories[entry_id] = remote_entry
            return "remote_newer"
        elif clock_relation == "equal":
            return "already_synchronized"
        else:
            return self._resolve_concurrent_conflict(entry_id, local_entry, remote_entry)

    def _resolve_concurrent_conflict(
        self, entry_id: str, local_entry: CRDTMemoryEntry, remote_entry: CRDTMemoryEntry
    ) -> str:
        strategy = self._select_resolution_strategy(local_entry, remote_entry)
        resolver = self.resolution_strategies.get(strategy, self._resolve_last_writer_wins)
        resolved_entry, needs_manual_review = resolver(local_entry, remote_entry)
        conflict = MemoryMergeConflict(
            conflict_id=f"conflict_{uuid.uuid4().hex[:8]}",
            entry_id=entry_id,
            conflicting_entries=[local_entry, remote_entry],
            resolution_strategy=strategy,
            resolved_entry=resolved_entry,
            manual_review_required=needs_manual_review,
        )
        self.merge_conflicts.append(conflict)
        if resolved_entry:
            self.memories[entry_id] = resolved_entry
            return f"conflict_resolved_{strategy}"
        else:
            return "conflict_manual_review_required"

    def _select_resolution_strategy(self, local_entry: CRDTMemoryEntry, remote_entry: CRDTMemoryEntry) -> str:
        if local_entry.memory_type == "core" or remote_entry.memory_type == "core":
            return "consensus_required"
        if local_entry.importance_score > 0.8 or remote_entry.importance_score > 0.8:
            return "importance_weighted"
        if local_entry.memory_type == "semantic" and remote_entry.memory_type == "semantic":
            return "semantic_merge"
        return "last_writer_wins"

    def _resolve_last_writer_wins(self, local_entry: CRDTMemoryEntry, remote_entry: CRDTMemoryEntry) -> Tuple[CRDTMemoryEntry, bool]:
        if remote_entry.created_at > local_entry.created_at:
            return remote_entry, False
        else:
            return local_entry, False

    def _resolve_semantic_merge(self, local_entry: CRDTMemoryEntry, remote_entry: CRDTMemoryEntry) -> Tuple[Optional[CRDTMemoryEntry], bool]:
        try:
            merged_content = local_entry.content.copy()
            for key, remote_value in remote_entry.content.items():
                if key not in merged_content:
                    merged_content[key] = remote_value
                elif merged_content[key] != remote_value:
                    merged_content[f"{key}_composite"] = {
                        "local": merged_content[key],
                        "remote": remote_value,
                        "merge_timestamp": datetime.now(timezone.utc).isoformat(),
                    }
            merged_entry = CRDTMemoryEntry(
                entry_id=local_entry.entry_id,
                content=merged_content,
                vector_clock=local_entry.vector_clock.update(remote_entry.vector_clock),
                node_id=f"merged_{local_entry.node_id}_{remote_entry.node_id}",
                created_at=min(local_entry.created_at, remote_entry.created_at),
                memory_type=local_entry.memory_type,
                importance_score=max(local_entry.importance_score, remote_entry.importance_score),
            )
            return merged_entry, False
        except Exception as e:
            self.logger.error(f"Semantic merge failed: {e}")
            return None, True

    def _resolve_importance_weighted(self, local_entry: CRDTMemoryEntry, remote_entry: CRDTMemoryEntry) -> Tuple[CRDTMemoryEntry, bool]:
        if remote_entry.importance_score > local_entry.importance_score:
            return remote_entry, False
        elif local_entry.importance_score > remote_entry.importance_score:
            return local_entry, False
        else:
            return self._resolve_last_writer_wins(local_entry, remote_entry)

    def _resolve_consensus_required(self, local_entry: CRDTMemoryEntry, remote_entry: CRDTMemoryEntry) -> Tuple[None, bool]:
        return None, True

    def _cleanup_old_memories(self):
        if len(self.memories) <= self.max_memory_size:
            return
        scored_memories = []
        for entry_id, memory in self.memories.items():
            time_decay = 1.0 / (1.0 + (datetime.now(timezone.utc) - memory.last_accessed).days)
            score = memory.importance_score * time_decay * memory.access_count
            scored_memories.append((score, entry_id))
        scored_memories.sort(reverse=True)
        keep_count = int(self.max_memory_size * 0.8)
        entries_to_keep = {entry_id for _, entry_id in scored_memories[:keep_count]}
        for entry_id in list(self.memories.keys()):
            if entry_id not in entries_to_keep:
                self.tombstones.add(entry_id)
                del self.memories[entry_id]
        self.logger.info(f"Cleaned up {len(self.memories) - keep_count} old memories")

    def get_sync_state(self) -> Dict[str, Any]:
        return {
            "memories": {
                entry_id: {
                    "entry_id": mem.entry_id,
                    "content": mem.content,
                    "vector_clock": mem.vector_clock.clocks,
                    "node_id": mem.node_id,
                    "created_at": mem.created_at.isoformat(),
                    "memory_type": mem.memory_type,
                    "importance_score": mem.importance_score,
                }
                for entry_id, mem in self.memories.items()
            },
            "vector_clock": self.vector_clock.clocks,
            "tombstones": list(self.tombstones),
            "node_id": self.node_id,
        }

    def load_sync_state(self, state_data: Dict[str, Any]) -> bool:
        try:
            remote_memories: Dict[str, CRDTMemoryEntry] = {}
            for entry_id, mem_data in state_data["memories"].items():
                memory = CRDTMemoryEntry(
                    entry_id=mem_data["entry_id"],
                    content=mem_data["content"],
                    vector_clock=VectorClock(mem_data["vector_clock"]),
                    node_id=mem_data["node_id"],
                    created_at=datetime.fromisoformat(mem_data["created_at"]),
                    memory_type=mem_data["memory_type"],
                    importance_score=mem_data["importance_score"],
                )
                remote_memories[entry_id] = memory
            remote_vector_clock = VectorClock(state_data["vector_clock"])
            remote_tombstones = set(state_data["tombstones"])
            self.merge_remote_state(remote_memories, remote_vector_clock, remote_tombstones)
            self.logger.info(f"Loaded sync state from {state_data['node_id']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load sync state: {e}")
            return False

    def get_memory_statistics(self) -> Dict[str, Any]:
        if not self.memories:
            return {"total_memories": 0}
        memory_types = defaultdict(int)
        importance_scores = []
        access_counts = []
        for memory in self.memories.values():
            memory_types[memory.memory_type] += 1
            importance_scores.append(memory.importance_score)
            access_counts.append(memory.access_count)
        return {
            "total_memories": len(self.memories),
            "memory_types": dict(memory_types),
            "tombstones": len(self.tombstones),
            "conflicts_total": len(self.merge_conflicts),
            "conflicts_manual_review": sum(1 for c in self.merge_conflicts if c.manual_review_required),
            "avg_importance": sum(importance_scores) / len(importance_scores) if importance_scores else 0,
            "avg_access_count": sum(access_counts) / len(access_counts) if access_counts else 0,
            "vector_clock": self.vector_clock.clocks,
            "node_id": self.node_id,
        }
