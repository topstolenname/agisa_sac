import importlib

import pytest

try:
    from fastapi.testclient import TestClient

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


def test_imports():
    # Test imports for cloud modules, skipping modules that require fastapi
    modules = [
        "cloud.functions.planner_function",
        "cloud.functions.evaluator_function",
    ]

    # Only test API and runner modules if fastapi is available
    if HAS_FASTAPI:
        modules.extend(
            [
                "cloud.run.agent_runner",
                "cloud.run.task_dispatcher",
                "cloud.api.simulation_api",
            ]
        )

    for mod in modules:
        importlib.import_module(mod)


@pytest.mark.skipif(not HAS_FASTAPI, reason="fastapi not available")
def test_simulation_api_endpoints():
    from cloud.api.simulation_api import app

    client = TestClient(app)
    response = client.post("/inject-agent", json={"id": "a1"})
    assert response.status_code == 200
    response = client.get("/agent/a1")
    assert response.status_code in (200, 404)
