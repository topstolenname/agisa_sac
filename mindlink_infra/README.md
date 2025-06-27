# Mindlink Infrastructure

This directory contains infrastructure helpers for scalable agent injection.
It exposes a FastAPI API for spawning agents and registering new agent
implementations at runtime. A minimal Redis-based pub/sub wrapper is provided
for distributed communication between agents or services.

### Key Features

- **Dynamic registry** – Agent classes can be loaded from dotted paths using the
  API or programmatically via ``AgentRegistry.load_agent_class``.
- **Spawn API** – ``/spawn_agent`` creates new agents on the fly.
- **Type registration API** – ``/register_agent_type`` allows plugging in custom
  agent classes without redeploying the service.
