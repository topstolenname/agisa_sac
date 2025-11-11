# AGISA-SAC Observability Stack

Complete observability infrastructure for monitoring Concord of Coexistence agent swarms.

## Architecture

```
┌─────────────────────┐
│  Concord Agents     │
│  (ConcordCompliant) │
└──────────┬──────────┘
           │
           │ Metrics
           ▼
┌─────────────────────┐
│  FastAPI Exporter   │
│  (port 8000)        │
└──────────┬──────────┘
           │
           │ /metrics
           ▼
┌─────────────────────┐
│  Prometheus         │
│  (port 9090)        │
└──────────┬──────────┘
           │
           │ PromQL
           ▼
┌─────────────────────┐
│  Grafana            │
│  (port 3000)        │
└─────────────────────┘
```

## Quick Start

### 1. Launch Stack

```bash
# From repository root
docker-compose -f docker-compose.observability.yml up -d

# Check services
docker-compose -f docker-compose.observability.yml ps
```

### 2. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **Exporter** | http://localhost:8000 | - |

### 3. View Dashboard

1. Navigate to http://localhost:3000
2. Login with admin/admin
3. Go to Dashboards → "Agentic Swarm Overview"

### 4. Simulate Data

```bash
# Trigger agent interaction cycle
curl -X POST http://localhost:8000/tick

# View raw metrics
curl http://localhost:8000/metrics
```

## Metrics Reference

### Consciousness Metrics

| Metric | Type | Description | Labels |
|--------|------|-------------|--------|
| `agisa_phi_integration` | Gauge | Φ integration (GWT consciousness) | `agent_id` |
| `agisa_cmni_mean` | Gauge | Mean CMNI across swarm | - |

### Topology Metrics (TDA)

| Metric | Type | Description |
|--------|------|-------------|
| `agisa_beta0_components` | Gauge | Connected components (β₀) |
| `agisa_beta1_loops` | Gauge | Feedback loops (β₁) |

### Coexistence Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `agisa_coexistence_score` | Gauge | Harmony index (0-1) |
| `agisa_agent_count` | Gauge | Active agent count |

## Exporter API

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "agisa-sac-exporter"
}
```

### `POST /tick`

Simulate one agent interaction cycle (for testing).

**Response:**
```json
{
  "timestamp": 1234567890.0,
  "agent_count": 3,
  "mean_phi": 0.23,
  "mean_cmni": 0.42,
  "beta0": 2,
  "beta1": 1,
  "coexistence_score": 0.67
}
```

### `GET /metrics`

Prometheus metrics exposition format.

## Configuration

### Prometheus

Edit `observability/prometheus/prometheus.yml` to customize:

- Scrape interval
- Target endpoints
- Alert rules

### Grafana

Dashboards are auto-provisioned from `observability/grafana/dashboards/`.

To customize:
1. Edit dashboard in Grafana UI
2. Export JSON
3. Replace `observability/grafana/dashboards/agisa_swarm_overview.json`

## Integration with Production Agents

Replace the simulated exporter with real agent metrics:

```python
from prometheus_client import Gauge, start_http_server

# Define metrics
phi_gauge = Gauge("agisa_phi_integration", "Phi integration", ["agent_id"])
cmni_gauge = Gauge("agisa_cmni_mean", "Mean CMNI")

# In your agent code
from agisa_sac.extensions.concord import ConcordCompliantAgent

agent = ConcordCompliantAgent(agent_id="prod-agent-1")

# After each interaction
result = agent.process_interaction(context)
phi_gauge.labels(agent_id=agent.agent_id).set(agent.phi_integration)
cmni_gauge.set(agent.empathy_module.cmni_tracker.current_cmni)

# Start metrics server
start_http_server(8000)
```

## Troubleshooting

### Exporter Not Starting

```bash
# Check logs
docker-compose -f docker-compose.observability.yml logs exporter

# Common issues:
# - Port 8000 already in use
# - Python dependencies missing in Dockerfile
```

### Prometheus Not Scraping

```bash
# Check Prometheus targets
# Navigate to: http://localhost:9090/targets

# Verify exporter endpoint
curl http://localhost:8000/metrics
```

### Grafana Dashboard Empty

1. Verify Prometheus datasource: Configuration → Data Sources
2. Check metric names match in queries
3. Generate data: `curl -X POST http://localhost:8000/tick`

### Port Conflicts

If ports are already in use, edit `docker-compose.observability.yml`:

```yaml
services:
  grafana:
    ports:
      - "3001:3000"  # Change external port
```

## Production Deployment

### GCP Cloud Monitoring

For production, use Google Cloud Monitoring:

```python
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project_id}"

# Write custom metric
series = monitoring_v3.TimeSeries()
series.metric.type = "custom.googleapis.com/concord/cmni"
# ... configure and write
```

### Kubernetes

Deploy on GKE:

```bash
# Apply Kubernetes manifests
kubectl apply -f observability/k8s/

# Access Grafana
kubectl port-forward svc/grafana 3000:3000
```

## Development

### Modify Exporter

Edit `observability/exporter_fastapi/app.py`, then:

```bash
# Rebuild and restart
docker-compose -f docker-compose.observability.yml up -d --build exporter
```

### Add Custom Metrics

```python
from prometheus_client import Gauge

new_metric = Gauge("agisa_custom_metric", "Description")
new_metric.set(42)
```

## References

- [Concord Framework Documentation](../docs/concord/index.md)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
