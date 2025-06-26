import pytest
from agisa_sac.chronicler import ResonanceChronicler
from agisa_sac.agent import EnhancedAgent


def make_agent(agent_id="a1"):
    personality = {"openness": 0.5, "consistency": 0.5, "conformity": 0.5, "curiosity": 0.5}
    return EnhancedAgent(agent_id=agent_id, personality=personality, capacity=10, use_semantic=False)


def test_chronicler_serialization():
    agent = make_agent()
    chron = ResonanceChronicler()
    chron.record_epoch(agent, 0)
    data = chron.to_dict()
    assert agent.agent_id in data
    assert len(data[agent.agent_id]) == 1
    loaded = ResonanceChronicler.from_dict(data)
    assert loaded.lineages[agent.agent_id][0].epoch == 0
