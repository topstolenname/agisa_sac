# In cognee/memory/hierarchical/core.py
import asyncio
from collections import deque
from datetime import datetime
from typing import Optional, Dict, Any
from cognee.memory.hierarchical.config import MemoryGenome
from cognee.memory.hierarchical.decay import MemoryDecayModel


class CircularBuffer:
    """Async-safe circular buffer for sensory input using deque."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.lock = asyncio.Lock()

    async def add(self, item: Dict[str, Any]):
        async with self.lock:
            self.buffer.append(
                {"timestamp": datetime.utcnow(), "access_count": 0, **item}
            )


class TemporalGraph:
    """Async-safe graph for storing salient episodic memories."""

    def __init__(self, salience_threshold: float):
        self.salience_threshold = salience_threshold
        self.graph = {}
        self.lock = asyncio.Lock()

    async def add_memory(self, experience: Dict, emotional_valence: float):
        if emotional_valence < self.salience_threshold:
            return  # Strategic forgetting

        async with self.lock:
            timestamp = experience.get("timestamp", datetime.utcnow())
            self.graph[f"memory_{timestamp.isoformat()}"] = {
                "experience": experience,
                "emotional_valence": emotional_valence,
                "consolidated": False,
            }


class HierarchicalMemory:
    """Main orchestrator for cognitive memory systems."""

    def __init__(self, genome: MemoryGenome):
        self.genome = genome
        self.sensory = CircularBuffer(capacity=genome.sensory_buffer_capacity)
        self.working = asyncio.Queue(maxsize=genome.working_memory_limit)
        self.episodic = TemporalGraph(
            salience_threshold=genome.episodic_salience_threshold
        )
        self.semantic = {}  # KnowledgeGraph placeholder
        self.procedural = {}  # SkillLibrary placeholder

        self.decay_model = MemoryDecayModel(genome)
        self.consolidation_task: Optional[asyncio.Task] = None

    async def start(self):
        """Begin background consolidation loop."""
        if self.consolidation_task is None:
            self.consolidation_task = asyncio.create_task(self._consolidation_loop())

    async def stop(self):
        """Stop the background consolidation loop."""
        if self.consolidation_task:
            self.consolidation_task.cancel()
            try:
                await self.consolidation_task
            except asyncio.CancelledError:
                pass
            self.consolidation_task = None

    async def _consolidation_loop(self, interval: int = 300):
        """Consolidates working memory to long-term every 5 minutes."""
        try:
            while True:
                await asyncio.sleep(interval)
                await self.consolidate()
        except asyncio.CancelledError:
            # Clean shutdown
            pass

    async def consolidate(self):
        """
        Moves memories from working queue to long-term episodic/procedural
        storage based on salience.
        """
        while not self.working.empty():
            experience = await self.working.get()
            emotional_valence = await self._assess_emotion(experience)
            await self.episodic.add_memory(experience, emotional_valence)

            if emotional_valence > self.genome.procedural_learning_threshold:
                await self._update_procedural_skills(experience)

            self.working.task_done()

    async def _assess_emotion(self, experience: Dict) -> float:
        """Placeholder for emotional valence assessment."""
        return experience.get("emotional_valence", 0.5)

    async def _update_procedural_skills(self, experience: Dict):
        """Placeholder for procedural skill reinforcement."""
        pass
