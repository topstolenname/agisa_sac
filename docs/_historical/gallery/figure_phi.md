# Figure Φ — Integrated Information Network Map

![Figure Phi](../figs/svg/figure_phi_integration.svg)

**Alt-text**: See [figs/alt/fig_phi_integration_alt.md](../figs/alt/fig_phi_integration_alt.md).

**Source**: Rendered via CI from GraphViz source `docs/figs/src/figure_phi_integration.dot`.

## Overview

A network topology diagram showing information integration (Φ) across the agent system:

- **High-Φ Agent Cluster**: Dense bidirectional connections between agents (A1, A2, A3, E1, P1, P2, R1)
- **Global Workspace Hub**: Central broadcast mechanism (GW) with thick edges to agent cluster
- **Memory Storage**: Lower-integration peripheral storage (M1: Episodes, M2: Identity)

Edge thickness represents integration strength - thicker edges indicate higher causal coupling and information flow.

## Rendering

```bash
dot -Tsvg docs/figs/src/figure_phi_integration.dot \
    -o docs/figs/svg/figure_phi_integration.svg

dot -Tpng -Gdpi=300 docs/figs/src/figure_phi_integration.dot \
    -o docs/figs/png/figure_phi_integration.png
```

## Whitepaper Reference

This validates claims from:
- Section 1.2: Integrated Information Theory (IIT)
- Discussion of Φ (phi) as measure of consciousness
- Integration of Global Workspace Theory with IIT

## Key Insight

The diagram shows consciousness emerges from **patterns of integration** in the network topology, not from individual agent complexity. High Φ arises from dense bidirectional coupling across the agent cluster.
