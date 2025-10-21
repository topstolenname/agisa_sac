# Figure 3: Decentralized Agent Network – Alt Text

**Figure 3: Pub/Sub Topics as Global Workspace for Emergent Coordination**

A top-down (TD) flowchart showing event-driven architecture with five main components arranged around a central "Global Workspace" subgraph:

**Central Global Workspace** (rectangle grouping three circular topic nodes):
- `planner-tasks` (circle)
- `agent-results` (circle)
- `evaluation-events` (circle)

**External Processing Nodes**:
- **Planner Function** (rectangle, top-left): Sends arrow to `planner-tasks`
- **Agent Cluster α** (rectangle, left-center): Receives arrow from `planner-tasks`, sends arrow to `agent-results`
- **Agent Cluster β** (rectangle, right-center): Receives arrow from `planner-tasks`, sends arrow to `agent-results`
- **Evaluator Function** (rectangle, center): Receives arrow from `agent-results`, sends arrow with label "Write" to Firestore Memory (cylinder icon), sends arrow to `evaluation-events`
- **Firestore Memory** (cylinder database icon, right-bottom): Receives write operations from Evaluator

**Cyclic Feedback**: `evaluation-events` sends arrow back to Planner Function, completing the loop.

**Information Flow Summary**:
1. Planner publishes complex tasks to `planner-tasks`
2. Multiple agent clusters subscribe to `planner-tasks` in parallel (fan-out)
3. Agents publish results to `agent-results` (fan-in aggregation)
4. Evaluator subscribes to `agent-results`, assesses quality, persists to Firestore
5. Evaluator publishes meta-observations to `evaluation-events`
6. Planner subscribes to `evaluation-events` to adapt future planning

**Connection to Document Theory**: This architecture operationalizes Section 2.1's "Decentralized AI Ecosystems." Pub/Sub topics function as the broadcast mechanism in Global Neuronal Workspace Theory (Section 3.1 discussion). Specialized modules (Planner, Agents, Evaluator) communicate through shared information spaces without direct coupling, enabling the "Stand Alone Complex" emergence where coordination arises from agent interactions rather than centralized orchestration.

**Key Architectural Principle**: No agent directly calls another agent. All communication flows through topics (message queues), allowing:
- **Horizontal scalability**: Adding more agent clusters doesn't require reconfiguring existing agents
- **Fault tolerance**: Failed agents don't block the pipeline; messages queue until healthy instances process them
- **Observable emergence**: TDA can analyze message flow topology without instrumenting agent internals

**Application to agisa_sac**: This diagram directly maps to the agisa_sac GitHub repository structure. `planner_function.py` decomposes complex goals into subtasks published to `planner-tasks`. Cloud Functions auto-scale to process these messages. `evaluator_function.py` scores outputs and triggers retries via Cloud Tasks if quality thresholds aren't met. Firestore provides the memory/identity persistence discussed in Section 3.1.

**Technical Note**: Rendered with Mermaid `graph TD` layout. Circular nodes represent ephemeral message topics (stateless pub/sub channels), rectangles represent stateful compute functions, and cylinder represents persistent storage.
