from agisa_sac.multi_agent_system import MultiAgentSystem


def test_agent_count_tracking():
    system = MultiAgentSystem()
    p = {"openness": 0.5, "consistency": 0.5, "conformity": 0.5, "curiosity": 0.5}
    system.create_agent("a1", p)
    system.create_agent("a2", p)

    stats = system.get_system_stats()
    assert stats["total_agents"] == 2
    assert stats["created_agents"] == 2
