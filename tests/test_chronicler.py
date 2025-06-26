import sys
from pathlib import Path
import unittest

# Ensure package src is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agisa_sac.chronicler import ResonanceChronicler


class DummyMemory:
    def get_current_focus_theme(self):
        return "test_theme"


class DummyResonance:
    def detect_echo(self, vector, theme):
        return [{"similarity": 0.9}]


class DummyAgent:
    def __init__(self):
        self.agent_id = "agent_test"
        self.memory = DummyMemory()
        self.cognitive = type("cog", (), {"cognitive_state": [0.25, 0.25, 0.25, 0.25]})()
        self.voice = type("voice", (), {"linguistic_signature": {"style_vector": [1, 1, 1, 1, 1]}})()
        self.temporal_resonance = DummyResonance()
        self.last_reflection_trigger = "dummy"

class TestResonanceChronicler(unittest.TestCase):
    def setUp(self):
        self.agent = DummyAgent()

    def test_record_and_serialize(self):
        chronicler = ResonanceChronicler()
        chronicler.record_epoch(self.agent, 0)
        data = chronicler.to_dict()
        self.assertIn("version", data)
        self.assertIn("lineages", data)
        self.assertIn("agent_test", data["lineages"])
        entry = data["lineages"]["agent_test"][0]
        self.assertEqual(entry["epoch"], 0)
        self.assertIsNotNone(entry["timestamp"])

if __name__ == "__main__":
    unittest.main()
