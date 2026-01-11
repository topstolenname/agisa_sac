# In tests/cognee/test_decay.py
from cognee.memory.hierarchical.config import MemoryGenome
from cognee.memory.hierarchical.decay import MemoryDecayModel


def test_decay_monotonicity():
    """Test that memory strength decreases over time"""
    g = MemoryGenome()
    d = MemoryDecayModel(g)
    # Use lower emotional valence to avoid hitting the 1.0 cap
    mem = {"emotional_valence": 0.1}

    # Strength at t=10 should be greater than at t=100
    s1 = d.calculate_strength(mem, time_elapsed=10, access_count=0)
    s2 = d.calculate_strength(mem, time_elapsed=100, access_count=0)

    assert s1 > s2, f"Expected s1({s1}) > s2({s2})"
    assert 0.0 <= s1 <= 1.0
    assert 0.0 <= s2 <= 1.0


def test_usage_reinforcement():
    """Test that access count strengthens memories"""
    g = MemoryGenome()
    d = MemoryDecayModel(g)
    mem = {"emotional_valence": 0.0}

    # Same time, but different access counts
    s_no_access = d.calculate_strength(mem, time_elapsed=50, access_count=0)
    s_with_access = d.calculate_strength(mem, time_elapsed=50, access_count=10)

    assert s_with_access > s_no_access


def test_emotional_boost():
    """Test that emotional memories are stronger"""
    g = MemoryGenome()
    d = MemoryDecayModel(g)

    mem_neutral = {"emotional_valence": 0.0}
    mem_emotional = {"emotional_valence": 0.8}

    s_neutral = d.calculate_strength(mem_neutral, time_elapsed=50, access_count=0)
    s_emotional = d.calculate_strength(mem_emotional, time_elapsed=50, access_count=0)

    assert s_emotional > s_neutral
