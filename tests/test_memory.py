import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import time
from agisa_sac.components.memory import MemoryContinuumLayer

def test_memory_retrieval_term_search():
    mem = MemoryContinuumLayer(agent_id="A1", capacity=10, use_semantic=False)
    mid = mem.add_memory({"text": "the cat jumped over the moon", "type": "note"})
    results = mem.retrieve_memory("cat")
    assert any(r["memory_id"] == mid for r in results)
    assert mem.memories[mid].access_count == 1
