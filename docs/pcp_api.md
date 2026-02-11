# PCP API Design

This document sketches the Programmatic Containment Protocol (PCP) endpoints used for monitoring agents.

## Endpoints

- `GET /pcp/agent/telemetry` – retrieve basic agent telemetry data.
- `POST /pcp/resonance-scan` – trigger a resonance scan on active agents.

Authentication and request thresholds should be enforced by the orchestrator layer. This draft does not implement security but notes that API keys and rate limiting are required for real deployments.
