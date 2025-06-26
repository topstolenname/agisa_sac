import numpy as np
from agisa_sac.components.resonance import TemporalResonanceTracker


def test_resonance_detection():
    tracker = TemporalResonanceTracker(agent_id="a1", resonance_threshold=0.5)
    vec = np.array([1.0, 0.0, 0.0])
    tracker.record_state(0.0, vec, "test")
    echoes = tracker.detect_echo(vec, "test")
    assert echoes
    assert echoes[0]["similarity"] >= 0.5
