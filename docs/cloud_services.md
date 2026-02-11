# Mindlink Cloud Services

This document provides a high level overview of the serverless components used to deploy Mindlink on Google Cloud Platform.

## Cloud Run Services

- **agent-runner** – Executes stateless agents in response to Pub/Sub push messages.
- **task-dispatcher** – HTTP endpoint that stores incoming tasks in Firestore and publishes them to the `agent-events` topic.
- **simulation-api** – REST API to inject agents and submit tasks.

## Cloud Functions

- **planner-function** – Listens for new tasks and decomposes them into subtasks using an LLM. Subtasks are published back to `agent-events`.
- **evaluator-function** – Scores agent results from `task-results` and queues retries via Cloud Tasks when needed.

## Messaging

Two Pub/Sub topics are created:

- `agent-events` for broadcasting tasks and agent communication.
- `task-results` for evaluation outcomes.

## Data Storage

Firestore collections maintain agent and task metadata:

- `agents` – Stored agent state and capabilities.
- `tasks` – Task documents including status and scores.

## Deployment

Infrastructure definitions are provided in `infra/terraform/main.tf`. Deploy using `terraform init && terraform apply` with the appropriate project ID and source bucket variables.
