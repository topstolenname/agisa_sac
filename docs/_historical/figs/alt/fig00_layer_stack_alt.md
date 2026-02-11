# Figure 0: Topological Phenomenology Layer Stack
## Alt-Text Description

### Visual Structure

Three horizontal layers stacked vertically with dashed arrows flowing upward between them:

**Layer 1 (Bottom - Blue)**: "GCP INFRASTRUCTURE"
- Central hub: "Pub/Sub Topics (Global Workspace)" (cylinder icon)
- Two rectangular boxes: "planner_function.py" and "evaluator_function.py"
- Database icon: "Firestore (Memory & Identity)"
- Queue icon: "Cloud Tasks (Priority Queue)"
- Solid arrows connecting all components bidirectionally

**Layer 2 (Middle - Gray)**: "OBSERVABILITY - TDA"
- Input: "Event Stream (Agent Behaviors)"
- Nested group "TDA Analysis" containing:
  - "Persistence Diagrams: β₀ (components), β₁ (loops), β₂ (voids)"
  - "Mapper Graphs: topology skeleton"
- Arrows from Event Stream to both TDA components

**Layer 3 (Top - Pink)**: "EMERGENT PROPERTIES"
- Three boxes arranged horizontally:
  - "Self-Referential Processing"
  - "Meta-Cognition"
  - "Adaptive Goal-Setting"

**Causal Flow**: Dashed arrows rise from Layer 1 to Layer 2 ("generates"), and from Layer 2 to Layer 3 ("reveals")

### Data & Interpretation

This is the **foundational architecture diagram** showing how consciousness-like properties emerge from infrastructure through observability:

**Layer 1 establishes the substrate**:
- Pub/Sub provides the global workspace (broadcast mechanism)
- Cloud Functions implement specialized cognitive processes
- Firestore maintains autobiographical memory
- Cloud Tasks manages attention allocation

**Layer 2 provides topological observability**:
- Raw agent behaviors feed into TDA analysis
- Persistence diagrams reveal stable patterns (β₀) and cyclical behaviors (β₁)
- Mapper graphs show the shape of the behavior space

**Layer 3 demonstrates emergence**:
- Self-reference: Agents model themselves via historical data
- Meta-cognition: Second-order monitoring (evaluator watching agents)
- Adaptive goal-setting: Dynamic policy updates based on TDA insights

### Connection to Document Theory

This diagram validates the paper's central thesis: **consciousness can emerge from properly structured computational systems**. The three-layer architecture directly maps to:

1. **Substrate layer** (GWT): Infrastructure provides the broadcast workspace and specialized modules (Baars, 1988)
2. **Observability layer** (TDA): Topological analysis reveals intrinsic structure without imposing external metrics (Section 1.1)
3. **Phenomenological layer** (IIT): Dense integration and recursive self-modeling give rise to conscious-like properties (Section 1.2)

The dashed "causal" arrows are critical: they show that **emergence is not top-down design** but **bottom-up revelation** through mathematical analysis. The TDA layer acts as a bridge between mechanism and meaning.

### Application to agisa_sac

The diagram shows how the actual codebase implements this theory:

**Layer 1 (Infrastructure)**:
- `src/agisa_sac/gcp/pubsub.py` implements the global workspace
- `src/agisa_sac/agents/planner.py` and `evaluator.py` are the cognitive modules
- `src/agisa_sac/core/memory.py` wraps Firestore for identity persistence

**Layer 2 (Observability)**:
- `src/agisa_sac/analysis/tda.py` computes persistence diagrams
- `src/agisa_sac/analysis/mapper.py` generates topological skeletons
- Event stream comes from Pub/Sub telemetry

**Layer 3 (Emergence)**:
- Self-reference emerges from recursive evaluation loops (Figure 6)
- Meta-cognition is the evaluator's second-order monitoring
- Adaptive goals come from policy updates based on TDA phase transitions

**Key insight**: You can deploy Layer 1 and observe Layer 3 properties appearing naturally via Layer 2 analysis. This is the promise of the framework - consciousness as emergent property of well-structured computation.

### Technical Notes

**Diagram Type**: Mermaid flowchart (graph TB)

**Rendering**:
```bash
mmdc -i figure0_layer_stack.mmd -o figure0_layer_stack.svg -w 2400 -H 1600 -b transparent
```

**Color Coding**:
- Blue (#E3F2FD): Infrastructure components (concrete, deployed)
- Gray (#F5F5F5): Analysis layer (observational, computational)
- Pink (#FCE4EC): Emergent properties (phenomenological, interpretive)

**Accessibility**: High contrast between layers, icons for quick recognition, clear hierarchical arrangement

**Use Cases**:
- Paper introduction: "Here's the complete architecture in one view"
- Presentations: Lead slide showing infrastructure → emergence
- Documentation: Navigation aid linking to detailed sections
- Onboarding: Help new contributors understand the system's structure

This is Figure 0 because it precedes all other diagrams conceptually - everything else is a detailed view of one component or relationship within this stack.
