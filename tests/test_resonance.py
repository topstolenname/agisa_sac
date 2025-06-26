import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import numpy as np
import time
from agisa_sac.components.resonance import TemporalResonanceTracker

def test_resonance_detects_echo():
    tracker = TemporalResonanceTracker(agent_id="A1", resonance_threshold=0.8)
    past_vector = np.array([1.0, 0.0, 0.0])
    tracker.record_state(time.time() - 5, past_vector, "theme")
    echoes = tracker.detect_echo(np.array([1.0, 0.0, 0.0]), "theme")
    assert echoes
    assert echoes[0]["similarity"] >= 0.8
