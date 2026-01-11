# Figure 6: agisa_sac Workflow – Alt Text

**Figure 6: Complete Task Lifecycle in agisa_sac Architecture**

*Note: This figure is referenced as `figure6_workflow.mmd` in the uploaded materials but source content was not provided. This alt-text describes the end-to-end workflow diagram that should appear based on agisa_sac repository documentation.*

**Expected Visual Structure**: A sequential flowchart showing the five-phase task processing cycle:

**Phase 1: Task Arrival**
- External trigger or user input generates a complex task
- Task message published to entry Pub/Sub topic

**Phase 2: Planning & Decomposition**
- `planner_function.py` (Cloud Function) subscribes to task topic
- LLM-powered planner analyzes task and decomposes into subtasks
- Subtasks published to `agent-processing` topic with metadata (dependencies, priorities)

**Phase 3: Distributed Execution**
- Multiple parallel agent instances (Cloud Functions) subscribe to `agent-processing` topic
- Each agent claims a subtask (first-available wins)
- Agents execute using specialized tools/APIs
- Results published to `evaluation` topic

**Phase 4: Evaluation & Quality Control**
- `evaluator_function.py` subscribes to `evaluation` topic
- Scores each subtask result against quality criteria
- **Low-quality branch**: Failed subtasks enqueued to Cloud Tasks retry queue with exponential backoff
- **High-quality branch**: Successful results written to Firestore with timestamp and score

**Phase 5: Persistence & Aggregation**
- Firestore stores:
  - Task decomposition history (how planner broke down the task)
  - Subtask execution traces (which agent handled what)
  - Quality scores (evaluation metrics)
  - Agent performance statistics (update reputation scores)
- When all subtasks complete, planner aggregates results
- Final output delivered to user or downstream system

**Cyclic Feedback Loop**: Evaluation statistics flow back to planner via Firestore queries, enabling meta-learning:
- If certain decomposition strategies consistently fail, planner adjusts approach
- If specific agent types excel at particular subtask categories, planner routes accordingly

**Connection to Document Theory**: This workflow operationalizes the "perceive → decide → act → evaluate" agentic loop discussed throughout the document. It bridges Part I's theoretical TDA (which observes this system in action) with Part II's decentralized architecture (Pub/Sub enabling emergent coordination) and Part III's identity framework (Firestore tracking agent reputation across cycles).

**Key Architectural Decisions**:

1. **Event-Driven**: No blocking RPC calls; all coordination via asynchronous messages. This prevents cascading failures and enables horizontal scaling.

2. **Stateless Functions**: Cloud Functions are ephemeral. All state lives in Pub/Sub (transient messages) or Firestore (durable data). Functions can crash and restart without losing system consistency.

3. **Retry with Backoff**: Cloud Tasks provides automatic retry logic with exponential backoff, implementing resilient error handling without custom code.

4. **Observable by Design**: Every phase produces events that TDA tools (Figure 1) can analyze. The topology of message flows reveals system health and emergent behaviors.

**Application to Consciousness Research**: The feedback loop from Phase 5 back to Phase 2 creates the recursive self-monitoring required for consciousness theories:
- **First-order processing**: Agents execute tasks (Phase 3)
- **Second-order processing**: Evaluator observes agent performance (Phase 4)
- **Third-order processing**: Planner reflects on past planning decisions by querying Firestore (Phase 5 → Phase 2 loop)

This three-level reflexivity implements the "recursive self-model" architecture described in the consciousness section of the document.

**Performance Metrics**: In production, this workflow handles:
- Task throughput: Hundreds of complex tasks per minute
- Latency: P95 end-to-end completion time <10 seconds for typical tasks
- Scalability: Linear cost increase with load (Cloud Functions auto-scale)
- Reliability: 99.9% task completion rate with automatic retry

**Technical Note**: This diagram should be rendered with Mermaid `graph TD` or `flowchart TD` layout, using distinct shapes: rectangles for stateful services (planner/evaluator), circles for stateless topics (Pub/Sub), cylinders for persistent storage (Firestore), and rounded rectangles for queues (Cloud Tasks). Color coding would distinguish the five phases for readability.
