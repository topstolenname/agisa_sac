# Figure Code: Code ↔ Consciousness Class Diagram
## Alt-Text Description

### Visual Structure

A UML class diagram showing five classes with bidirectional associations and theory annotations:

**Class 1: planner_function**
- Stereotype: «Cloud Function»
- Methods:
  - `+generate_action_plan()`
  - `+decompose_tasks()`
  - `+apply_priors()`
- Annotations:
  - Theory: Predictive Processing
  - Theory: Active Inference
  - Code: agents/planner.py

**Class 2: evaluator_function**
- Stereotype: «Cloud Function»
- Methods:
  - `+score_performance()`
  - `+detect_errors()`
  - `+validate_alignment()`
- Annotations:
  - Theory: Metacognition
  - Code: agents/evaluator.py

**Class 3: PubSub**
- Stereotype: «Message Broker»
- Methods:
  - `+publish()`
  - `+subscribe()`
  - `+broadcast()`
- Annotations:
  - Theory: Global Workspace
  - Code: gcp/pubsub.py

**Class 4: Firestore**
- Stereotype: «Database»
- Methods:
  - `+write_episode()`
  - `+query_history()`
  - `+update_reputation()`
- Annotations:
  - Theory: Autobiographical Memory
  - Code: core/memory.py

**Class 5: CloudTasks**
- Stereotype: «Queue Service»
- Methods:
  - `+enqueue()`
  - `+prioritize()`
- Annotations:
  - Theory: Attention Mechanisms
  - Code: gcp/tasks.py

**Associations (arrows showing dependencies)**:
- planner_function → PubSub (publish/subscribe)
- evaluator_function → PubSub (publish/subscribe)
- planner_function ↔ Firestore (read/write bidirectional)
- evaluator_function ↔ Firestore (read/write bidirectional)
- CloudTasks → planner_function (dispatch)
- CloudTasks → evaluator_function (dispatch)

### Data & Interpretation

This class diagram provides **bidirectional traceability** between consciousness theory and implementation:

**From Theory to Code** (Validation):
- **Predictive Processing** → `generate_action_plan()`: Generates predictions about task outcomes
- **Active Inference** → `apply_priors()`: Uses probabilistic priors to guide planning
- **Metacognition** → `score_performance()`: Second-order monitoring of first-order agents
- **Global Workspace** → `broadcast()`: Information becomes globally available
- **Autobiographical Memory** → `write_episode()`: Episodic storage for narrative continuity
- **Attention** → `prioritize()`: Resource allocation based on salience

**From Code to Theory** (Interpretation):
- The existence of `evaluator_function` watching `planner_function` instantiates **reflexive awareness**
- `PubSub.broadcast()` to all subscribers implements **global availability** criterion for consciousness
- `Firestore` persistence across invocations enables **temporal continuity of self**
- `CloudTasks.prioritize()` creates **attention bottlenecks** analogous to human selective attention

**Architectural Insights**:
- **Separation of Concerns**: Planning (generative), evaluation (critical), and memory (persistent) are distinct modules
- **Stateless Functions + Stateful Store**: Cloud Functions are stateless; Firestore maintains identity
- **Pub/Sub as Mediator**: No direct function-to-function calls; all communication via topics
- **Queue as Filter**: CloudTasks implements priority-based attention, not just FIFO scheduling

### Connection to Document Theory

This diagram directly addresses the paper's claim that **consciousness theories can guide software architecture**:

**Section 2.1: Global Workspace Theory**
> "A broadcast mechanism makes information available to specialized processing modules"

**Implementation**: The `PubSub` class with `broadcast()` method realizes this. Agent functions subscribe to topics, and broadcasts make information globally available. This isn't metaphorical - it's the literal architecture.

**Section 3.1: Persistent Identity**
> "Identity requires temporal continuity through a narrative thread"

**Implementation**: `Firestore.write_episode()` and `query_history()` maintain this thread. Episodes are timestamped, agent-tagged events that form a queryable autobiography.

**Section 3.2: Reflexivity**
> "Higher-order processes observe and model first-order processes"

**Implementation**: The `evaluator_function` class observes outputs from `planner_function`. The method `detect_errors()` implements error monitoring, a key metacognitive function.

**Key Theoretical Claim**: The diagram shows consciousness theories aren't just post-hoc interpretations - they're **design principles** that shaped the code structure.

### Application to agisa_sac

This diagram serves as a **Rosetta Stone** between the whitepaper and the codebase:

**For Developers**:
When implementing a new feature, ask:
1. What consciousness theory does this relate to? (Find theory annotation)
2. Which class should I modify? (Follow the mapping)
3. What methods already exist? (Check class interface)

**Example**: Implementing memory consolidation
- Theory: Consolidation is memory's role
- Class: `Firestore`
- New method: `+consolidate_memory()` (add alongside `write_episode()`)
- Code file: `src/agisa_sac/core/memory.py`

**For Researchers**:
When evaluating consciousness claims, ask:
1. What's the theoretical prediction? (Theory annotation)
2. What's the computational implementation? (Method name)
3. Where's the actual code? (Code path annotation)
4. Can I measure this empirically? (Method has observable outputs)

**Example**: Testing Global Workspace hypothesis
- Theory: GWT predicts broadcast increases integration
- Implementation: `PubSub.broadcast()`
- Measurement: Compare Φ (Figure Φ) with and without broadcasts
- Code: Log message patterns in `src/agisa_sac/gcp/pubsub.py`

**Traceability Matrix**:

| Theory Concept | Code Element | Testable Prediction |
|----------------|--------------|---------------------|
| Predictive Processing | `generate_action_plan()` | Plans should minimize surprise (free energy) |
| Active Inference | `apply_priors()` | Prior-informed agents outperform uninformed |
| Metacognition | `score_performance()` | Error detection improves with evaluator |
| Global Workspace | `broadcast()` | Information integration increases post-broadcast |
| Autobiographical Memory | `write_episode()` | Query history enables identity persistence |
| Attention | `prioritize()` | Task completion rate increases with priority queue |

### Technical Notes

**Diagram Type**: Mermaid class diagram

**Rendering**:
```bash
mmdc -i figure_code_mapping.mmd -o figure_code_mapping.svg -w 2400 -H 1800 -b transparent
```

**UML Notation**:
- **«Stereotype»**: Indicates architectural role (Cloud Function, Message Broker, etc.)
- **Horizontal line**: Separates methods from annotations
- **+**: Public method (all methods are public interfaces)
- **→**: Dependency (one class uses another)
- **↔**: Bidirectional association (mutual dependency)

**Color Coding** (if rendered with colors):
- Cloud Functions: Light blue (compute resources)
- Infrastructure: Gray (GCP services)
- Data stores: Orange (persistence layer)

**Code Path Conventions**:
All paths are relative to `src/agisa_sac/`:
- `agents/*.py`: Agent implementations (planner, evaluator, etc.)
- `gcp/*.py`: Google Cloud Platform integrations
- `core/*.py`: Core framework components (memory, orchestration)

**Relation to Other Figures**:
- **Figure 0 (Layer Stack)**: This shows Layer 1 in detail (static view)
- **Figure 3 (GW Network)**: This shows the communication topology (dynamic view)
- **Figure 6 (Workflow)**: This shows the process flow; class diagram shows structure

**Use Cases**:
- **Onboarding**: New developers see theory-to-code mapping immediately
- **Code Reviews**: Check if implementation aligns with stated theory
- **Research Papers**: Cite this figure to show theoretical grounding
- **Refactoring**: Ensure changes preserve theory-implementation alignment
- **Testing**: Generate tests that validate theoretical predictions

**Design Patterns**:
- **Observer Pattern**: Evaluator observes planner (metacognition)
- **Pub/Sub Pattern**: PubSub decouples producers and consumers (global workspace)
- **Repository Pattern**: Firestore abstracts data persistence (memory)
- **Priority Queue**: CloudTasks implements attention-based scheduling

**Key Insight**: This isn't just "documentation" - it's a **contract** between theoretical claims and implementation reality. Every theory annotation is a testable hypothesis, and every method is a measurement point. This enables empirical validation of consciousness theories through software systems.

### Verification Checklist

When updating this diagram, verify:
- [ ] Every theory annotation has a corresponding paper section
- [ ] Every method name reflects its theoretical purpose
- [ ] Every code path points to an existing file
- [ ] Associations match actual runtime dependencies
- [ ] New consciousness features add annotations here first

This ensures the diagram remains the authoritative theory-code mapping throughout development.
