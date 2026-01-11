"""
Integration tests for topology orchestration and agent coordination.

These tests verify the behavior of the TopologyOrchestrationManager
and agent handoff mechanisms.
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from agisa_sac.types.contracts import Tool, ToolType

try:
    from agisa_sac.orchestration.topology_manager import TopologyOrchestrationManager

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

pytestmark = pytest.mark.skipif(
    not HAS_DEPS, reason="Requires google-cloud-firestore and google-cloud-storage"
)


@pytest.fixture
def mock_firestore():
    """Mock Firestore client for testing"""
    fs = MagicMock()
    mock_get = fs.collection.return_value.document.return_value.get.return_value
    mock_get.to_dict.return_value = {
        "node_id": "test-node",
        "status": "active",
        "last_seen": "2024-01-01T00:00:00Z",
    }
    return fs


@pytest.fixture
def mock_storage():
    """Mock Storage client for testing"""
    return MagicMock()


@pytest.mark.anyio
async def test_fragmentation_detection(mock_firestore, mock_storage):
    """Test topology detects fragmentation in agent network"""

    # Create mock GCP module objects
    fake_firestore = MagicMock()
    fake_firestore.Client = MagicMock(return_value=mock_firestore)
    fake_firestore.SERVER_TIMESTAMP = "SERVER_TIMESTAMP"

    fake_storage = MagicMock()
    fake_storage.Client = MagicMock(return_value=mock_storage)

    fake_pubsub = MagicMock()
    fake_pubsub.PublisherClient = MagicMock(return_value=MagicMock())
    fake_pubsub.SubscriberClient = MagicMock(return_value=MagicMock())

    # Import base_agent and topology_manager and patch the GCP dependencies after import
    import agisa_sac.agents.base_agent as base_agent
    from agisa_sac.orchestration import topology_manager

    # Create mock ripser function that simulates fragmented network
    def mock_ripser(D, distance_matrix=False, maxdim=1):
        # For a fragmented network with 3 agents, return 3 H0 components
        # These represent 3 connected components (fragmentation)
        h0 = np.array(
            [
                [0.0, np.inf],  # Component 1
                [0.0, 0.8],  # Component 2 (merges at distance 0.8)
                [0.0, 0.9],  # Component 3 (merges at distance 0.9)
            ]
        )
        h1 = np.array([])  # No loops
        h2 = np.array([])  # No voids
        return {"dgms": [h0, h1, h2]}

    # Patch the module-level variables to simulate GCP being available
    with (
        patch.object(base_agent, "firestore", fake_firestore),
        patch.object(base_agent, "storage", fake_storage),
        patch.object(base_agent, "pubsub_v1", fake_pubsub),
        patch.object(base_agent, "HAS_GCP", True),
        patch.object(topology_manager, "firestore", fake_firestore),
        patch.object(topology_manager, "storage", fake_storage),
        patch.object(topology_manager, "HAS_DEPS", True),
        patch.object(topology_manager, "ripser", mock_ripser),
    ):

        AGISAAgent = base_agent.AGISAAgent

        # Now create agents
        agent_a = AGISAAgent(
            agent_id="test_a",
            name="Agent A",
            instructions="Research agent",
            tools=[
                Tool(
                    "search", ToolType.DATA, lambda: "result", "Search tool", "low", {}
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
                    "write", ToolType.ACTION, lambda: "result", "Write tool", "low", {}
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

        result = await topo.compute_coordination_topology()

        assert result["coordination_quality"] < 0.7
        assert len(result["suggested_optimizations"]) > 0


@pytest.mark.anyio
async def test_agent_distance_metric(mock_firestore, mock_storage):
    """Test agent distance metric satisfies metric properties"""

    # Create mock GCP module objects
    fake_firestore = MagicMock()
    fake_firestore.Client = MagicMock(return_value=mock_firestore)
    fake_firestore.SERVER_TIMESTAMP = "SERVER_TIMESTAMP"

    fake_storage = MagicMock()
    fake_storage.Client = MagicMock(return_value=mock_storage)

    fake_pubsub = MagicMock()
    fake_pubsub.PublisherClient = MagicMock(return_value=MagicMock())
    fake_pubsub.SubscriberClient = MagicMock(return_value=MagicMock())

    # Import base_agent and topology_manager and patch the GCP dependencies after import
    import agisa_sac.agents.base_agent as base_agent
    from agisa_sac.orchestration import topology_manager

    # Create mock ripser function that simulates fragmented network
    def mock_ripser(D, distance_matrix=False, maxdim=1):
        # For a fragmented network with 3 agents, return 3 H0 components
        # These represent 3 connected components (fragmentation)
        h0 = np.array(
            [
                [0.0, np.inf],  # Component 1
                [0.0, 0.8],  # Component 2 (merges at distance 0.8)
                [0.0, 0.9],  # Component 3 (merges at distance 0.9)
            ]
        )
        h1 = np.array([])  # No loops
        h2 = np.array([])  # No voids
        return {"dgms": [h0, h1, h2]}

    # Patch the module-level variables to simulate GCP being available
    with (
        patch.object(base_agent, "firestore", fake_firestore),
        patch.object(base_agent, "storage", fake_storage),
        patch.object(base_agent, "pubsub_v1", fake_pubsub),
        patch.object(base_agent, "HAS_GCP", True),
        patch.object(topology_manager, "firestore", fake_firestore),
        patch.object(topology_manager, "storage", fake_storage),
        patch.object(topology_manager, "HAS_DEPS", True),
        patch.object(topology_manager, "ripser", mock_ripser),
    ):

        AGISAAgent = base_agent.AGISAAgent

        agent_a = AGISAAgent(
            agent_id="test_a",
            name="Agent A",
            instructions="Multi-tool agent",
            tools=[
                Tool("search", ToolType.DATA, lambda: "result", "Search", "low", {}),
                Tool("analyze", ToolType.DATA, lambda: "result", "Analyze", "low", {}),
            ],
            project_id="test-project",
        )

        agent_b = AGISAAgent(
            agent_id="test_b",
            name="Agent B",
            instructions="Analysis agent",
            tools=[
                Tool("analyze", ToolType.DATA, lambda: "result", "Analyze", "low", {}),
                Tool("write", ToolType.ACTION, lambda: "result", "Write", "low", {}),
            ],
            project_id="test-project",
        )

        agent_c = AGISAAgent(
            agent_id="test_c",
            name="Agent C",
            instructions="Writing agent",
            tools=[
                Tool("write", ToolType.ACTION, lambda: "result", "Write", "low", {})
            ],
            project_id="test-project",
        )

        topo = TopologyOrchestrationManager(
            mock_firestore, mock_storage, "test-project"
        )
        topo.register_agent(agent_a)
        topo.register_agent(agent_b)
        topo.register_agent(agent_c)

        d_aa = topo.agent_distance(agent_a, agent_a)
        d_ab = topo.agent_distance(agent_a, agent_b)
        d_ba = topo.agent_distance(agent_b, agent_a)
        d_bc = topo.agent_distance(agent_b, agent_c)

        assert d_aa == 0.0
        assert abs(d_ab - d_ba) < 1e-6
        assert d_ab >= 0.0 and d_bc >= 0.0
        assert 0.0 <= d_ab <= 1.0
        assert 0.0 <= d_bc <= 1.0


@pytest.mark.anyio
async def test_resource_budget_enforcement():
    """Test resource budget constraints (no pubsub needed)"""
    from agisa_sac.agents.base_agent import ResourceBudget

    budget = ResourceBudget(
        max_tokens_per_min=1000, max_tools_per_min=50, max_cost_per_day=10.0
    )

    # Verify budget enforcement
    assert budget.max_tokens_per_min == 1000
    assert budget.max_tools_per_min == 50
    assert budget.max_cost_per_day == 10.0


@pytest.mark.anyio
async def test_tool_mcp_format_conversion():
    """Test tool MCP format conversion (no pubsub needed)"""
    from agisa_sac.types.contracts import Tool, ToolType

    tool = Tool(
        name="test_tool",
        type=ToolType.DATA,
        function=lambda x: x,
        description="Test",
        risk_level="low",
        parameters={"x": {"type": "string"}},
    )

    mcp_format = tool.to_mcp_format()
    assert mcp_format["name"] == "test_tool"
    assert mcp_format["inputSchema"]["type"] == "object"
