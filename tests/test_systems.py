from agisa_sac.systems import MultiAgentSystem


def test_system_stats_reflect_agents():
    system = MultiAgentSystem()
    system.create_agent("agent1")
    agent2 = system.create_agent("agent2")
    # Remove and re-add agent2 via add_agent to exercise both paths
    system.agents.pop(agent2.agent_id)
    system.add_agent(agent2)
    stats = system.get_system_stats()
    assert stats["total_agents"] == 2
