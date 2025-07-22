from agisa_sac.core.components.memory import MemoryContinuumLayer
from agisa_sac.core.components.cognitive import CognitiveDiversityEngine


def test_cognitive_decision():
    mem = MemoryContinuumLayer(agent_id="a1", capacity=5, use_semantic=False)
    engine = CognitiveDiversityEngine(
        agent_id="a1",
        personality={"openness": 0.5, "consistency": 0.5, "conformity": 0.5, "curiosity": 0.5},
        memory_layer=mem,
    )
    decision = engine.decide("test query", peer_influence={})
    assert isinstance(decision, str)
    assert decision
