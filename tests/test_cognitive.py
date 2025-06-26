import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from agisa_sac.components.memory import MemoryContinuumLayer
from agisa_sac.components.cognitive import CognitiveDiversityEngine

def test_cognitive_decide_adds_memory():
    memory = MemoryContinuumLayer(agent_id="A2", capacity=10, use_semantic=False)
    engine = CognitiveDiversityEngine(
        agent_id="A2",
        personality={"curiosity":0.5,"conformity":0.5,"openness":0.5,"consistency":0.5},
        memory_layer=memory
    )
    prev_count = len(memory.memories)
    response = engine.decide("future plans", {"peer": 1.0})
    assert response in [
        "Approach A: Systematic",
        "Approach B: Creative",
        "Approach C: Balanced",
        "Approach D: Efficient",
    ]
    assert len(memory.memories) == prev_count + 1
    assert any(mem.content.get("type") == "decision_context" for mem in memory.memories.values())
