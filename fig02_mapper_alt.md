# Figure 2: Mapper Graph â€" Alt Text

**Figure 2: Topological Skeleton Revealing High-Dimensional Data Structure**

An undirected network graph with left-to-right (LR) layout showing three overlapping cover regions labeled A, B, and C. Each region contains circular nodes representing data point clusters:

**Region A** (leftmost): Contains three nodes (A1, A2, A3) connected linearly A1â€"A2â€"A3.

**Region B** (center): Contains two nodes (B1, B2) connected linearly B1â€"B2.

**Region C** (rightmost): Contains four nodes (C1, C2, C3, C4) forming a linear chain C1â€"C2â€"C3â€"C4.

**Inter-region connections** (indicated by edges between clusters): A3 connects to B1 (overlap between regions A and B), B2 connects to C2 (overlap between B and C), and A2 connects to C3 (overlap between A and C). These cross-region edges arise from data points that fall into multiple overlapping covers, creating the topological skeleton.

**Interpretation**: The Mapper algorithm creates this simplified representation of high-dimensional agent behavior space. Each node represents a cluster of similar system states (e.g., agent configurations, task distributions). Connections between nodes indicate state transitions or shared characteristics. The three-region structure reveals that the system exhibits distinct operational modes with gradual transitions between them, rather than discrete jumps.

**Connection to Document Theory**: This visualization implements the Mapper algorithm discussed in Section 1.1. The graph structure provides intuition about the "shape" of the high-dimensional data manifold where the agent swarm operates. Flares (linear chains like Region C) suggest directional evolution paths, while loops (none present in this simplified example, but possible in real data) indicate cyclical behaviors or homeostatic regulation.

**Application to agisa_sac**: In production, nodes would represent task decomposition strategies, and edges would show which strategies share common subtask patterns. Analyzing this graph over time tracks how the planner_function's strategy space evolves, revealing meta-learning and adaptation.

**Technical Note**: Rendered from Graphviz DOT format. The layout algorithm automatically positions nodes to minimize edge crossings. All nodes have white fill to ensure legibility regardless of background theme.
