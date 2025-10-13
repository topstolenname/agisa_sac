import base64

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.agisa_sac.federation.server import (
    app,
    authenticate_edge_node,
    cbp,
    cbp_middleware,
)

# --- Test Fixtures ---


@pytest.fixture
def client():
    """
    Provides a FastAPI TestClient for making requests to the app.
    This fixture also cleans up dependency overrides after tests.
    """
    with TestClient(app) as c:
        yield c
    # Clean up dependency overrides after the test finishes
    app.dependency_overrides = {}


@pytest.fixture
def authenticated_client():
    """
    Provides a TestClient where the authentication dependency is overridden
    to always succeed with a fixed node_id.
    """

    def override_authenticate_edge_node():
        return "test_node_123"

    app.dependency_overrides[authenticate_edge_node] = (
        override_authenticate_edge_node
    )
    with TestClient(app) as c:
        yield c
    # Clean up dependency overrides
    app.dependency_overrides = {}


@pytest.fixture(autouse=True)
def reset_cbp_state():
    """
    Fixture to automatically reset the state of the ContinuityBridgeProtocol
    before each test, ensuring test isolation.
    """
    cbp.trust_graph.clear()
    cbp.quarantined_fragments.clear()
    # Re-initialize with a simple identity anchor for predictability
    cbp.initialize_identity_anchor(
        {
            "values": {"cooperation": "test"},
            "ethics": ["test ethic"],
        }
    )


# --- Unit Tests for API Endpoints ---


def test_agent_telemetry(client: TestClient):
    """Tests the public telemetry endpoint for basic availability."""
    response = client.get("/pcp/agent/telemetry")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_edge_node_success(authenticated_client: TestClient):
    """Tests successful registration of a new edge node with mocked authentication."""
    registration_data = {
        "node_type": "desktop",
        "capabilities": ["processing", "storage"],
        "trust_endorsements": ["endorser_A"],
    }
    response = authenticated_client.post(
        "/api/v1/edge/register", json=registration_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "registered"
    assert data["node_id"] == "test_node_123"
    assert "initial_trust" in data
    assert cbp.trust_graph.get("test_node_123") == data["initial_trust"]


def test_register_edge_node_unauthorized(client: TestClient):
    """Tests that the registration endpoint fails without a valid token."""
    registration_data = {
        "node_type": "desktop",
        "capabilities": ["processing", "storage"],
    }
    # The default client has no auth headers
    response = client.post("/api/v1/edge/register", json=registration_data)
    assert response.status_code == 401
    assert "Missing or invalid authorization" in response.json()["detail"]


def test_submit_cognitive_fragment_unregistered(
    authenticated_client: TestClient,
):
    """Tests submitting a fragment from a node that is not yet registered."""
    update_data = {
        "type": "observation",
        "content": {"data": "some data"},
        "timestamp": "2024-01-01T12:00:00Z",
        "signature": "abc",
    }
    response = authenticated_client.post(
        "/api/v1/edge/submit", json=update_data
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Node not registered"


def test_submit_cognitive_fragment_success(
    authenticated_client: TestClient, monkeypatch
):
    """Tests successful submission of a fragment from a registered node."""
    # 1. Register the node first
    cbp.trust_graph["test_node_123"] = 0.5

    # 2. Mock the middleware processing to isolate the endpoint logic
    def mock_process_edge_update(node_id, update):
        return {
            "status": "integrated",
            "fragment_id": "frag-1",
            "trust_score": 0.51,
            "coherence_metrics": {"score": 0.9},
        }

    monkeypatch.setattr(
        cbp_middleware, "process_edge_update", mock_process_edge_update
    )

    # 3. Submit the fragment
    update_data = {
        "type": "observation",
        "content": {"data": "some data"},
        "timestamp": "2024-01-01T12:00:00Z",
        "signature": "abc",
    }
    response = authenticated_client.post(
        "/api/v1/edge/submit", json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["fragment_status"] == "integrated"
    assert data["fragment_id"] == "frag-1"


def test_get_trust_metrics_not_found(authenticated_client: TestClient):
    """Tests retrieving trust metrics for a node that doesn't exist."""
    response = authenticated_client.get("/api/v1/edge/trust-metrics")
    assert response.status_code == 404
    assert response.json()["detail"] == "Node not found"


def test_admin_trust_override(client: TestClient):
    """Tests the admin endpoint for overriding a node's trust score."""
    node_id = "node_to_override"
    cbp.trust_graph[node_id] = 0.5

    response = client.post(
        f"/api/v1/admin/trust-override?node_id={node_id}&new_trust=0.95"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "updated"
    assert data["node_id"] == node_id
    assert data["old_trust"] == 0.5
    assert data["new_trust"] == 0.95
    assert cbp.trust_graph[node_id] == 0.95


def test_admin_trust_override_invalid_score(client: TestClient):
    """Tests that the trust override endpoint rejects out-of-range values."""
    response = client.post(
        "/api/v1/admin/trust-override?node_id=any_node&new_trust=1.1"
    )
    assert response.status_code == 400
    assert "must be between 0.0 and 1.0" in response.json()["detail"]


# --- Unit Tests for Authentication Logic ---


@pytest.mark.asyncio
async def test_authenticate_edge_node_success():
    """Tests the authentication dependency directly with a valid token."""
    node_id = "my_test_node"
    token = base64.b64encode(node_id.encode()).decode()
    auth_header = f"Bearer {token}"

    result_node_id = await authenticate_edge_node(authorization=auth_header)
    assert result_node_id == node_id


@pytest.mark.asyncio
async def test_authenticate_edge_node_no_header():
    """Tests authentication with a missing Authorization header."""
    with pytest.raises(HTTPException) as excinfo:
        await authenticate_edge_node(authorization=None)
    assert excinfo.value.status_code == 401
    assert "Missing or invalid authorization" in excinfo.value.detail


@pytest.mark.asyncio
async def test_authenticate_edge_node_invalid_base64():
    """Tests authentication with a token that is not valid base64."""
    with pytest.raises(HTTPException) as excinfo:
        await authenticate_edge_node(authorization="Bearer not-base64-token")
    assert excinfo.value.status_code == 401
    assert "Invalid token format" in excinfo.value.detail
