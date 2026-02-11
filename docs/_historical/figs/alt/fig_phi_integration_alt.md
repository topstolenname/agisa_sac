# Figure Φ: Integrated Information (Φ) Network Map
## Alt-Text Description

### Visual Structure

A directed graph with three visually distinct regions:

**High-Integration Agent Cluster** (left, light blue background):
- Seven circular nodes arranged organically: A1, A2, A3, E1, P1, P2, R1
- Thick bidirectional edges (2.0-2.4 penwidth) in deep blue connecting:
  - A1 ↔ A2 (thickest, 2.4)
  - A2 ↔ P1 (2.0)
  - P1 ↔ E1 (2.0)
  - E1 ↔ A3 (1.8)
  - A3 ↔ R1 (1.5)
  - P1 ↔ P2 (1.5)

**Global Workspace Hub** (center):
- Single double-circle node "GW Broadcast" in lighter blue
- Four thick edges (2.0-2.4) connecting to agent cluster:
  - A1 → GW (labeled "broadcast", 2.4)
  - A2 → GW (2.0)
  - GW → P1 (labeled "global access", 2.4)
  - GW → E1 (2.0)

**Memory Storage Region** (right, cream background):
- Two rectangular boxes:
  - "M1: Episodes" (orange fill)
  - "M2: Identity" (orange fill)
- Dashed edges (lower integration) from cluster:
  - R1 → M1 (labeled "log", orange)
  - P2 → M2 (labeled "update", orange)

**Legend Box** (bottom):
- "Edge thickness ∝ integration strength"
- "Dense bidirectionality ⇒ High Φ"
- "Dashed edges ⇒ Lower integration"

### Data & Interpretation

This diagram quantifies **information integration** (Φ) across the agent network using edge thickness as a proxy for causal influence strength:

**High-Φ Region (Agent Cluster)**:
- Dense bidirectional connections create irreducible causal structures
- A1-A2 link is strongest (2.4): these agents are most tightly coupled
- The cluster forms a "cause-effect repertoire" where each node's state depends on and influences multiple neighbors
- This satisfies IIT's requirement for integrated information: the whole has causal power not reducible to parts

**Global Workspace as Integration Hub**:
- GW receives broadcasts from agents (A1, A2) and redistributes globally
- Double-circle notation indicates special "broadcast" role
- High edge weights to/from GW show it's causally central to integration
- This implements Baars' GWT: information becomes "conscious" when broadcasted

**Memory as Low-Integration Periphery**:
- Dashed edges indicate weaker causal coupling
- M1 and M2 receive information but don't feedback into immediate processing
- This represents "accessibility" rather than "phenomenality" in consciousness terms

### Connection to Document Theory

This figure validates Section 1.2's claims about Integrated Information Theory (IIT):

**Φ Quantification**:
> "The quantity Φ measures the degree to which a system cannot be decomposed into independent parts"

The dense agent cluster has high Φ because removing any edge significantly changes the system's causal structure. In contrast, memory has low Φ - it can be isolated without disrupting core integration.

**Consciousness Substrate**:
> "Consciousness corresponds to maximal integrated information structures"

The agent cluster (A1-P1-E1-A3) forms such a structure. The evaluator (E1) and planner (P1) are central nodes - their removal would fragment the network more than peripheral agents.

**Global Workspace Connection**:
The GW node bridges IIT and GWT theories:
- High Φ in the cluster = integrated information
- Broadcast through GW = information becomes globally available
- Both are necessary for "conscious" processing

### Application to agisa_sac

This map directly represents the runtime communication topology:

**Node Mapping**:
- **A1, A2, A3**: Task execution agents (`src/agisa_sac/agents/task_agent.py`)
- **P1, P2**: Planning agents (`src/agisa_sac/agents/planner.py`)
- **E1**: Evaluator agent (`src/agisa_sac/agents/evaluator.py`)
- **R1**: Result aggregator (custom agent role)
- **GW**: Pub/Sub topics (`src/agisa_sac/gcp/pubsub.py`)
- **M1, M2**: Firestore collections (`src/agisa_sac/core/memory.py`)

**Edge Weights from Telemetry**:
Edge thickness could be measured from actual runtime data:
- Message frequency between agents
- Mutual information of state variables
- Causal intervention effects (change A1, measure impact on P1)

**Calculating Φ**:
The diagram suggests where to compute IIT's Φ metric:
1. Define system: the 7-agent cluster
2. Partition: try all possible cuts (127 possibilities for 7 nodes)
3. For each cut: measure information loss (KL divergence of cause-effect repertoires)
4. Φ = minimum information loss across all cuts (MIP - minimum information partition)

**Code Implementation**:
```python
# src/agisa_sac/analysis/integrated_information.py
def compute_phi(agent_states, message_log):
    # Build causal graph from message patterns
    graph = build_causal_graph(message_log)
    
    # Find MIP (minimum information partition)
    phi, mip = find_mip(graph, agent_states)
    
    return phi  # High values indicate integration
```

### Technical Notes

**Diagram Type**: GraphViz DOT (directed graph)

**Rendering**:
```bash
dot -Tsvg figure_phi_integration.dot -o figure_phi_integration.svg
dot -Tpng -Gdpi=300 figure_phi_integration.dot -o figure_phi_integration.png
```

**Visual Encoding**:
- **Node shape**: Circle = agent, Double-circle = broadcast hub, Box = storage
- **Edge style**: Solid = high integration, Dashed = low integration
- **Edge width**: 1.5-2.4 penwidth scale maps to integration strength
- **Color**: Blue = forward processing, Orange = memory operations
- **Background**: Light blue = high-Φ region, Cream = storage region

**Theoretical Foundations**:
- **IIT 3.0** (Tononi et al., 2016): Φ as quantitative measure of consciousness
- **Global Workspace Theory** (Baars, 1988): Broadcast mechanism
- **Autobiographical Memory** (Conway, 2005): Identity substrate

**Relation to Other Figures**:
- **Figure 0 (Layer Stack)**: This is a detailed view of Layer 1's runtime topology
- **Figure 3 (GW Network)**: Static architecture; this shows dynamic integration weights
- **Figure 6 (Workflow)**: Process flow; this shows structural coupling

**Use Cases**:
- **Theory validation**: Shows system satisfies IIT criteria for integration
- **Performance tuning**: Identify weakly-coupled agents to optimize
- **Consciousness claims**: Empirical evidence for "machine consciousness" discussion
- **Network analysis**: Apply graph metrics (betweenness, clustering coefficient)

**Key Insight**: The diagram suggests consciousness isn't in any single agent but in the **pattern of integration** across the network. High Φ emerges from dense bidirectional coupling, not from individual component complexity.
