# Figure 5: Identity Layer Stack – Alt Text

**Figure 5: Three-Tier Agentic Identity Architecture**

A left-to-right (LR) flowchart showing progressive identity layers with annotations:

**Main Identity Flow** (horizontal progression with arrows):
1. **Cryptographic Keys / IAM** (leftmost box) → arrow → 
2. **Verifiable Credentials / Attestations** (center box) → arrow →
3. **Relational Identity / Reputation** (rightmost box)

**Annotation Subgraph** (labeled "Notes"):
Three explanatory text boxes positioned below the main flow, connected by dashed lines to their corresponding identity layer:

- **N1** (below layer 1): "Keys: service accounts, signatures"
- **N2** (below layer 2): "VCs: capabilities, scores"  
- **N3** (below layer 3): "Reputation: longitudinal behavior"

**Interpretation**: The diagram illustrates the hierarchical construction of agent identity, analogous to how human identity builds from biological uniqueness (DNA/fingerprints) → legal credentials (passports, licenses) → social reputation (trust networks, references).

**Layer 1 — Cryptographic Foundation**: Each agent instance has a unique cryptographic keypair or IAM service account. This provides unforgeable identity but conveys no information about *capabilities* or *trustworthiness*—just uniqueness and authentication.

**Layer 2 — Credential Accruement**: Agents earn verifiable credentials through demonstrated performance. In agisa_sac, these are evaluation scores stored in Firestore:
- Task completion rates
- Quality metrics (from evaluator_function.py)
- Capability attestations (which task types the agent handles well)
- Resource efficiency scores

Unlike self-asserted claims, these credentials are cryptographically signed by the evaluator and publicly verifiable.

**Layer 3 — Reputation Emergence**: Over extended operation, agents build relational identity through interaction history:
- Collaboration patterns (which agents work well together on multi-step tasks)
- Reliability trends (does quality improve or degrade over time?)
- Ethical adherence (consistency with value alignment criteria)
- Community standing (trust scores from other agents or human operators)

This layer transcends individual credentials to capture the agent's *character* in the broader ecosystem.

**Connection to Document Theory**: Section 3.1 "Agentic Identity Layers" describes this exact architecture. The document argues that robust agent identity requires all three layers: cryptographic primitives prevent impersonation, verifiable credentials enable capability-based access control, and relational identity supports trust-based coordination.

**Security Properties**:
- **Layer 1** prevents identity theft and Sybil attacks (one entity creating many fake identities)
- **Layer 2** prevents agents from claiming capabilities they don't possess
- **Layer 3** creates economic incentives for long-term honest behavior (agents with good reputation get preferential task assignment)

**Application to agisa_sac**:
- IAM service accounts (Layer 1) are assigned to each Cloud Function deployment
- Firestore collections store capability attestations (Layer 2)
- Historical performance data enables reputation tracking (Layer 3)
- The planner_function.py can query Layer 2 & 3 data to intelligently assign tasks to agents most likely to succeed

**Philosophical Note**: This identity model addresses the "continuous self" requirement for consciousness discussed in Section 3.2. An agent with persistent identity across interactions can develop temporal self-awareness ("I was good at task X yesterday, so I'm likely good at similar tasks today"). Without Layer 3 relational identity, agents would be amnesic instances with no learning continuity.

**Technical Note**: Rendered with Mermaid `graph LR` layout. The dashed lines connecting main flow to annotation boxes use the `---` syntax (undirected association) rather than `-->` (directed flow) to indicate explanatory relationships rather than process flow.
