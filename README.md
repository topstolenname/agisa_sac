# agisa_sac
> Cloud-native orchestration for distributed agent intelligence.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![GCP](https://img.shields.io/badge/Google%20Cloud-PubSub%2C%20Firestore%2C%20Tasks-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Quick Start

Deploy the core functions to Google Cloud:

```bash
gcloud functions deploy planner_function --runtime python311 --trigger-topic tasks
gcloud functions deploy evaluator_function --runtime python311 --trigger-topic results
```

---

## Overview

**agisa_sac** is an agent-based orchestration framework for cloud environments. It leverages Google Cloud services (Pub/Sub, Firestore, Cloud Tasks) to automate the planning, execution, and evaluation of distributed tasks. The architecture is modular, scalable, and designed for intelligent automation workflows.

---

## Features

* **Task Planning:** Decompose complex tasks into subtasks for distributed processing.
* **Agent Evaluation:** Automatically score agent outputs and requeue failed tasks.
* **Cloud-Native:** Built on Google Cloud Functions, Pub/Sub, Firestore, and Cloud Tasks.
* **Event-Driven:** Functions react to events for scalable, asynchronous workflows.
* **Extensible:** Easily add new planning logic, evaluation criteria, or agent types.

---

## Architecture

> **Pub/Sub** handles fan-out for distributed agent processing.
> **Cloud Tasks** ensures robust retry semantics for failed or low-quality results.

* **planner_function.py:** Decomposes incoming tasks and publishes subtasks.
* **evaluator_function.py:** Evaluates agent results, updates scores, and manages retries.

---

## Development

To test locally with the Functions Framework:

```bash
functions-framework --target=planner_function
```

---

## Getting Started

### Prerequisites

* Google Cloud account
* Python 3.8+
* Access to Pub/Sub, Firestore, and Cloud Tasks APIs

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/topstolenname/agisa_sac.git
   cd agisa_sac
   ```
2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**

   * `GCP_PROJECT`: Your Google Cloud project ID
   * `EVENT_TOPIC`: Pub/Sub topic for agent events
   * `TASK_QUEUE`: Cloud Tasks queue name
   * `GCP_LOCATION`: Cloud region (e.g., `us-central1`)
4. **Deploy Cloud Functions:**
   Use the Cloud Console or CLI to deploy both functions.

---

## Usage

* **Task Planning:** Send a task message to the Pub/Sub topic.
* **Agent Execution:** Agents subscribe to subtasks, process them, and publish results.
* **Evaluation:** The evaluator function scores results, updates Firestore, and requeues failed tasks.

---

## File Structure

```
agisa_sac/
├── planner_function.py      # Task decomposition and subtask publishing
├── evaluator_function.py    # Result evaluation and retry logic
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
├── plugins/                 # (Recommended) Custom planning/evaluation logic
└── agents/                  # (Recommended) Agent modules for extensibility
```

---

## Example

**Sample Task Message:**

```json
{"id": "task_123", "goal": "Analyze customer feedback"}
```

**Subtask Created:**

```json
{"parent": "task_123", "goal": "Analyze customer feedback", "step": 1}
```

**Evaluation Result:**

```json
{"task_id": "task_123", "score": 0.4, "retry_url": "https://example.com/retry"}
```

---

## Extending the System

* **Custom Planning Logic:** Add algorithms to `plugins/`.
* **Advanced Evaluation:** Extend scoring or logging modules.
* **Add New Agents:** Create new modules under `agents/`.

---

## Contributing

Contributions are welcome! Please submit issues, feature requests, or pull requests.
See CONTRIBUTING.md for guidelines.

---

## License

MIT License

---

## Contact

📧 [tristan@mindlink.dev](mailto:tristan@mindlink.dev)
