import importlib
from fastapi.testclient import TestClient


def test_imports():
    modules = [
        'cloud.run.agent_runner',
        'cloud.run.task_dispatcher',
        'cloud.functions.planner_function',
        'cloud.functions.evaluator_function',
        'cloud.api.simulation_api',
    ]
    for mod in modules:
        importlib.import_module(mod)


def test_simulation_api_endpoints():
    from cloud.api.simulation_api import app
    client = TestClient(app)
    response = client.post('/inject-agent', json={'id': 'a1'})
    assert response.status_code == 200
    response = client.get('/agent/a1')
    assert response.status_code in (200, 404)
