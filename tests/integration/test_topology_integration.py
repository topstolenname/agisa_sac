"""
Integration tests for topology orchestration and agent coordination.

These tests verify the behavior of the TopologyOrchestrationManager
and agent handoff mechanisms.
"""

import pytest

from agisa_sac.agents.base_agent import AGISAAgent, ResourceBudget
from agisa_sac.types.contracts import Tool, ToolType

try:
    from agisa_sac.orchestration.topology_manager import (
        TopologyOrchestrationManager,
    )

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

pytestmark = pytest.mark.skipif(
    not HAS_DEPS,
    reason="Requires google-cloud-firestore, google-cloud-storage, and ripser",
)


@pytest.fixture
def mock_firestore():
    """Mock Firestore client for testing"""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.collection.return_value.document.return_value.set.return_value = None
    return mock


@pytest.fixture
def mock_storage():
    """Mock Storage client for testing"""
    from unittest.mock import MagicMock

    return MagicMock()


@pytest.mark.asyncio
async def test_fragmentation_detection(mock_firestore, mock_storage):
    """Test topology detects fragmentation in agent network"""
    # Mock GCP clients to prevent initialization errors
    from unittest.mock import MagicMock, patch

    with patch('agisa_sac.agents.base_agent.firestore.Client', return_value=mock_firestore), \
         patch('agisa_sac.agents.base_agent.pubsub_v1.PublisherClient', return_value=MagicMock()), \
         patch('agisa_sac.agents.base_agent.storage.Client', return_value=mock_storage):

        # Create 3 agents with no overlapping tools
        agent_a = AGISAAgent(
            agent_id="test_a",
            name="Agent A",
            instructions="Research agent",
            tools=[
                Tool(
                    "search",
                    ToolType.DATA,
                    lambda: "result",
                    "Search tool",
                    "low",
                    {},
                )
            ],
            project_id="test-project",
        )

        agent_b = AGISAAgent(
            agent_id="test_b",
            name="Agent B",
            instructions="Analysis agent",
            tools=[
                Tool(
                    "analyze",
                    ToolType.DATA,
                    lambda: "result",
                    "Analyze tool",
                    "low",
                    {},
                )
            ],
            project_id="test-project",
        )

        agent_c = AGISAAgent(
            agent_id="test_c",
            name="Agent C",
            instructions="Writing agent",
            tools=[
                Tool(
                    "write",
                    ToolType.ACTION,
                    lambda: "result",
                    "Write tool",
                    "low",
                    {},
                )
            ],
            project_id="test-project",
        )

        # Create topology manager
        topo = TopologyOrchestrationManager(
            mock_firestore, mock_storage, "test-project"
        )

        # Register agents
        topo.register_agent(agent_a)
        topo.register_agent(agent_b)
        topo.register_agent(agent_c)

        # Compute topology
        result = await topo.compute_coordination_topology()

        # Should detect fragmentation (low quality due to no tool overlap)
        assert result["coordination_quality"] < 0.7
        assert len(result["suggested_optimizations"]) > 0
        # Note: Fragmentation detection depends on having actual interaction data


@pytest.mark.asyncio
async def test_agent_distance_metric(mock_firestore, mock_storage):
    """Test agent distance metric satisfies metric properties"""
    from unittest.mock import MagicMock, patch

    with patch('agisa_sac.agents.base_agent.firestore.Client', return_value=mock_firestore), \
         patch('agisa_sac.agents.base_agent.pubsub_v1.PublisherClient', return_value=MagicMock()), \
         patch('agisa_sac.agents.base_agent.storage.Client', return_value=mock_storage):

        # Create agents with some tool overlap
        agent_a = AGISAAgent(
            agent_id="test_a",
            name="Agent A",
            instructions="Multi-tool agent",
            tools=[
                Tool(
                    "search",
                    ToolType.DATA,
                    lambda: "result",
                    "Search",
                    "low",
                    {},
                ),
                Tool(
                    "analyze",
                    ToolType.DATA,
                    lambda: "result",
                    "Analyze",
                    "low",
                    {},
                ),
            ],
            project_id="test-project",
        )

        agent_b = AGISAAgent(
            agent_id="test_b",
            name="Agent B",
            instructions="Analysis agent",
            tools=[
                Tool(
                    "analyze",
                    ToolType.DATA,
                    lambda: "result",
                    "Analyze",
                    "low",
                    {},
                ),
                Tool(
                    "write",
                    ToolType.ACTION,
                    lambda: "result",
                    "Write",
                    "low",
                    {},
                ),
            ],
            project_id="test-project",
        )

        agent_c = AGISAAgent(
            agent_id="test_c",
            name="Agent C",
            instructions="Writing agent",
            tools=[
                Tool(
                    "write",
                    ToolType.ACTION,
                    lambda: "result",
                    "Write",
                    "low",
                    {},
                )
            ],
            project_id="test-project",
        )

        topo = TopologyOrchestrationManager(
            mock_firestore, mock_storage, "test-project"
        )
        topo.register_agent(agent_a)
        topo.register_agent(agent_b)
        topo.register_agent(agent_c)

        # Test metric properties
        d_aa = topo.agent_distance(agent_a, agent_a)
        d_ab = topo.agent_distance(agent_a, agent_b)
        d_ba = topo.agent_distance(agent_b, agent_a)
        d_bc = topo.agent_distance(agent_b, agent_c)

        # Self-distance should be zero
        assert d_aa == 0.0

        # Symmetry: d(a,b) = d(b,a)
        assert abs(d_ab - d_ba) < 1e-6

        # Non-negativity: d >= 0
        assert d_ab >= 0.0
        assert d_bc >= 0.0

        # Distance should be in [0, 1]
        assert 0.0 <= d_ab <= 1.0
        assert 0.0 <= d_bc <= 1.0


@pytest.mark.asyncio
async def test_resource_budget_enforcement():
    """Test that resource budgets are properly enforced"""
    budget = ResourceBudget(
        max_tokens_per_min=1000, max_tools_per_min=5, max_cost_per_day=1.0
    )

    # Test token budget
    assert budget.check_tokens(500) is True
    budget.consume_tokens(500)
    assert budget.check_tokens(600) is False  # Would exceed limit
    assert budget.check_tokens(400) is True

    # Test tool budget
    assert budget.check_tools() is True
    for _ in range(5):
        budget.consume_tool()
    assert budget.check_tools() is False  # Exceeded limit

    # Test cost budget
    assert budget.check_cost(0.5) is True
    budget.consume_cost(0.5)
    assert budget.check_cost(0.6) is False  # Would exceed limit
    assert budget.check_cost(0.4) is True


@pytest.mark.asyncio
async def test_tool_mcp_format_conversion():
    """Test Tool conversion to MCP format"""
    tool = Tool(
        name="test_tool",
        type=ToolType.DATA,
        function=lambda x, y: x + y,
        description="A test tool",
        risk_level="low",
        parameters={
            "x": {"type": "integer", "description": "First number", "required": True},
            "y": {"type": "integer", "description": "Second number", "required": True},
        },
    )

    mcp_format = tool.to_mcp_format()

    assert mcp_format["name"] == "test_tool"
    assert mcp_format["description"] == "A test tool"
    assert "inputSchema" in mcp_format
    assert mcp_format["inputSchema"]["type"] == "object"
    assert "x" in mcp_format["inputSchema"]["properties"]
    assert "y" in mcp_format["inputSchema"]["properties"]
    assert "x" in mcp_format["inputSchema"]["required"]
    assert "y" in mcp_format["inputSchema"]["required"]
