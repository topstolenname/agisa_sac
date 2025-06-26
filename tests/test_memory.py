from agisa_sac.components.memory import MemoryContinuumLayer


def test_memory_retrieval_simple():
    mem = MemoryContinuumLayer(agent_id="a1", capacity=5, use_semantic=False)
    mem.add_memory({"type": "note", "text": "hello world", "theme": "test"}, importance=0.6)
    results = mem.retrieve_memory("hello")
    assert results
    assert results[0]["content"]["text"] == "hello world"
