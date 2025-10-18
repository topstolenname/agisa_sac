# The Agentic Swarm: Visual Documentation Implementation Guide

This package contains production-ready visualizations linking theoretical consciousness research, cloud-native implementation, and topological observability frameworks for "The Agentic Swarm" document and the agisa_sac repository.

## Package Contents

### Core Documentation Files
- `CITATION_GUIDE.md` - Complete academic citation formats (APA, Chicago, MLA, BibTeX)
- `FIGURE_CATALOG.md` - Comprehensive figure matrix with metadata and links
- This `README.md` - Implementation guide and quick start

### Alt-Text Descriptions (Accessibility)
- `fig01_persistence_alt.md` - Topological persistence analysis
- `fig02_mapper_alt.md` - Mapper graph topology
- `fig03_network_alt.md` - Decentralized agent architecture
- `fig04_convergence_alt.md` - Instrumental convergence flow
- `fig05_identity_alt.md` - Three-tier identity stack
- `fig06_workflow_alt.md` - Complete task lifecycle
- `fig07_dashboard_alt.md` - Consciousness metrics dashboard

### Enhanced Diagram Sources
- `figure3_network_enhanced.mmd` - Styled Pub/Sub global workspace
- `figure4_convergence_enhanced.mmd` - Styled instrumental convergence
- `figure5_identity_enhanced.mmd` - Styled identity layers
- `figure6_workflow_enhanced.mmd` - Styled complete workflow

---

## Quick Start

### 1. Copy Files to Your Repository

```bash
# Clone or download this package
cd your-repo

# Create directory structure
mkdir -p docs/figs/{src,svg,png,alt}

# Copy alt-text files
cp fig*_alt.md docs/figs/alt/

# Copy enhanced diagram sources
cp figure*_enhanced.mmd docs/figs/src/

# Copy documentation
cp CITATION_GUIDE.md FIGURE_CATALOG.md docs/
```

### 2. Set Up Rendering Pipeline

#### Install Dependencies

```bash
# Mermaid CLI (for .mmd files)
npm install -g @mermaid-js/mermaid-cli

# Graphviz (for .dot files)
# Ubuntu/Debian:
sudo apt-get install graphviz
# macOS:
brew install graphviz

# Python dependencies (for figure1_persistence.py)
pip install matplotlib
```

#### Render Diagrams Locally

```bash
# Mermaid diagrams
mmdc -i docs/figs/src/figure3_network_enhanced.mmd \
     -o docs/figs/svg/figure3.svg \
     -w 1200 -s 2

# Graphviz diagrams
dot -Tsvg docs/figs/src/figure2_mapper.dot \
    -o docs/figs/svg/figure2.svg \
    -Gdpi=300

# Python figures
python docs/figs/src/figure1_persistence.py
```

### 3. Set Up GitHub Actions (Automated Rendering)

Copy the provided `diagram-build.yml` to `.github/workflows/`:

```bash
mkdir -p .github/workflows
cp diagram-build.yml .github/workflows/
```

This workflow automatically:
- Triggers on pushes to `docs/figs/src/**`
- Renders all Mermaid, Graphviz, and Python diagrams
- Uploads SVG artifacts
- Commits rendered outputs back to repository

### 4. Embed in Documents

#### Markdown (GitHub README, Jekyll, Hugo)

```markdown
![Figure 3: Decentralized Agent Network](docs/figs/svg/figure3.svg)

**Figure 3**: Pub/Sub topics function as a global workspace enabling emergent 
coordination. For detailed description, see 
[alt-text](docs/figs/alt/fig03_network_alt.md).
```

#### LaTeX (Academic Papers)

```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=0.9\textwidth]{docs/figs/svg/figure3.svg}
  \caption{Decentralized Agent Network. Pub/Sub topics function as a global 
           workspace, enabling emergent coordination without centralized control.}
  \label{fig:network}
\end{figure}

As illustrated in Figure~\ref{fig:network}, the event-driven architecture...
```

#### HTML (with Accessibility)

```html
<figure id="fig3">
  <img src="docs/figs/svg/figure3.svg" 
       alt="Decentralized Agent Network: Pub/Sub Global Workspace"
       aria-describedby="fig3-desc">
  <figcaption>
    <strong>Figure 3</strong>: Pub/Sub topics as global workspace
  </figcaption>
  <div id="fig3-desc" class="sr-only">
    <!-- Copy content from fig03_network_alt.md -->
  </div>
</figure>
```

---

## Enhanced Diagram Features

The enhanced versions (`*_enhanced.mmd`) include:

### Comprehensive Styling
- **Consistent color scheme** across all diagrams
  - Blue (#1c7ed6, #5b8def): Infrastructure/Communication
  - Orange (#e8590c, #f08c00): Memory/Identity persistence
  - Pink (#d63384, #fff0f6): Consciousness/Emergence properties
  - Green (#2f9e44, #ebfbee): Attention/Priority mechanisms
  - Yellow (#f08c00, #fff9db): Safety/Warning indicators

### Accessibility Enhancements
- **High contrast ratios** (>4.5:1 for text, >3:1 for graphics)
- **Shape + color** coding (never color alone)
- **Descriptive labels** for all nodes and connections

### Theory Integration
- **Annotation boxes** linking visuals to document concepts
- **Consciousness theory mappings** (GWT, IIT, HOT)
- **Implementation references** to agisa_sac code

### Educational Clarity
- **Subgraph grouping** for related concepts
- **Dashed borders** for conceptual containers
- **Varied line styles** (solid=flow, dashed=observation, thick=high-volume)

---

## Customization Guide

### Modify Color Scheme

Edit `classDef` statements in `.mmd` files:

```mermaid
%% Change infrastructure color from blue to purple
classDef module fill:#e7d5ff,stroke:#7c3aed,stroke-width:2px
```

### Add New Annotations

```mermaid
%% Add consciousness theory note
note4["Global Workspace Theory:\nBroadcast enables global\navailability"]:::annotation
GW -.-> note4
```

### Adjust Layout

```mermaid
%% Change from top-down to left-right
flowchart LR  %% was: flowchart TD
```

### Export at Different Scales

```bash
# High-resolution for print (2100px width, 2x scale)
mmdc -i source.mmd -o output.svg -w 2100 -s 2

# Mobile-friendly (600px width, 1x scale)
mmdc -i source.mmd -o output-mobile.svg -w 600 -s 1
```

---

## Integration with agisa_sac Repository

### Recommended Directory Structure

```
agisa_sac/
├── docs/
│   ├── The_Agentic_Swarm.docx         # Main document
│   ├── The_Conscious_Machine.pdf       # Co-authored whitepaper
│   ├── CITATION_GUIDE.md               # From this package
│   ├── FIGURE_CATALOG.md               # From this package
│   └── figs/
│       ├── src/                        # Source diagrams
│       │   ├── figure1_persistence.py
│       │   ├── figure2_mapper.dot
│       │   ├── figure3_network_enhanced.mmd
│       │   ├── figure4_convergence_enhanced.mmd
│       │   ├── figure5_identity_enhanced.mmd
│       │   ├── figure6_workflow_enhanced.mmd
│       │   └── figure7_dashboard.jsx
│       ├── svg/                        # Rendered SVG (auto-generated)
│       ├── png/                        # Raster exports (auto-generated)
│       ├── alt/                        # Alt-text from this package
│       └── captions.yaml               # Metadata (optional)
├── .github/
│   └── workflows/
│       └── diagram-build.yml           # From uploads
├── src/
│   └── agisa_sac/                  # Python package
└── README.md                           # Main repo README
```

### Link Figures in Main README

```markdown
# agisa_sac: Agentic Intelligence Swarm Architecture

## Architecture Overview

![System Architecture](docs/figs/svg/figure3.svg)

The agisa_sac framework implements decentralized agent coordination through 
event-driven messaging. See [Figure 3 details](docs/figs/alt/fig03_network_alt.md).

## Identity Framework

![Identity Layers](docs/figs/svg/figure5.svg)

Agent identity builds hierarchically from cryptographic primitives through 
verifiable credentials to relational reputation. See 
[Figure 5 details](docs/figs/alt/fig05_identity_alt.md).

## Complete Documentation
- [Figure Catalog](docs/FIGURE_CATALOG.md) - All diagrams with metadata
- [Citation Guide](docs/CITATION_GUIDE.md) - Academic reference formats
```

---

## Troubleshooting

### Mermaid Rendering Errors

**Problem**: `mmdc` fails with syntax error

**Solutions**:
1. Check for unclosed subgraphs or quotes
2. Validate node IDs don't contain special characters
3. Ensure `classDef` comes before `class` usage
4. Try rendering with lower width/scale: `-w 800 -s 1`

### Graphviz Layout Issues

**Problem**: Nodes overlap or edges cross excessively

**Solutions**:
1. Add `rankdir=LR` for left-to-right layout
2. Increase `ranksep` and `nodesep`:
   ```dot
   graph G {
     rankdir=LR;
     ranksep=2.0;
     nodesep=1.0;
     ...
   }
   ```
3. Force node positions with `pos` attribute

### Color Contrast Failures

**Problem**: Text unreadable on background

**Solutions**:
1. Use online checker: https://webaim.org/resources/contrastchecker/
2. Lighten background or darken text:
   ```mermaid
   classDef myclass fill:#f8f9ff,stroke:#495057,color:#000
   ```
3. Add white/black text outline in CSS post-processing

### Alt-Text Too Long

**Problem**: Screen readers truncate descriptions

**Solutions**:
1. Keep primary alt attribute concise (<150 chars)
2. Use `aria-describedby` for extended description
3. Link to separate HTML page with full description
4. Provide both "quick summary" and "detailed" versions

---

## Citation Examples

### In Academic Paper

```latex
The system architecture (Figure 3; Jessup, 2025) demonstrates how Pub/Sub 
topics implement Global Workspace Theory, with specialized modules broadcasting 
to shared information spaces.
```

**References section**:
```
Jessup, T. J. (2025). Pub/Sub topics as global workspace [Figure]. 
    In The agentic swarm: Emergence, ethics, and identity in 
    next-generation artificial intelligence (Supplementary Material). 
    https://github.com/topstolenname/agisa_sac/blob/main/docs/figs/svg/figure3.svg
```

### In Presentation

```
[Slide with Figure 3]

"¢ Decentralized architecture
"¢ No centralized orchestration
"¢ Emergent coordination through message passing

Source: Jessup (2025), "The Agentic Swarm," 
https://github.com/topstolenname/agisa_sac
```

---

## Maintenance

### Updating Figures

1. Edit source file in `docs/figs/src/`
2. Commit changes to trigger CI/CD rendering
3. Update caption in `captions.yaml` if needed
4. Verify alt-text still accurate in `docs/figs/alt/`
5. Update version in `FIGURE_CATALOG.md` if breaking changes

### Version Tagging

Follow semantic versioning:

```bash
# After completing figure updates
git add docs/figs/
git commit -m "feat(docs): enhance Figure 3 with consciousness annotations"
git tag -a docs-v1.1.0 -m "Add consciousness theory mappings to figures"
git push origin main --tags
```

### Quality Checklist

Before releasing new figure versions:

- [ ] All diagrams render without errors locally
- [ ] Alt-text descriptions updated if visual changed
- [ ] Color contrast validated (WCAG 2.1 AA)
- [ ] Captions updated in `captions.yaml`
- [ ] Figure references in main document verified
- [ ] Citation examples added to `CITATION_GUIDE.md`
- [ ] `FIGURE_CATALOG.md` version incremented
- [ ] Git tag created for release

---

## Support

**Primary Maintainer**: Tristan J. Jessup

**Contact**: 
- Email: tristan@mindlink.dev
- GitHub: @topstolenname
- Repository: https://github.com/topstolenname/agisa_sac

**Issues**: https://github.com/topstolenname/agisa_sac/issues

**Contributing**: See repository CONTRIBUTING.md

---

## License

All figures and documentation released under MIT License.

```
MIT License

Copyright (c) 2025 Tristan J. Jessup

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full MIT License text...]
```

---

## Acknowledgments

Visual design inspired by:
- Neuroscience EEG dashboards (Figure 7)
- TDA visualization best practices (Figures 1-2)
- Google Cloud architecture diagrams (Figures 3, 6)
- Consciousness research frameworks (all figures)

Theoretical foundations from:
- "The Agentic Swarm" document (primary source)
- "The Conscious Machine" whitepaper (co-authored)
- Integrated Information Theory (Tononi et al.)
- Global Workspace Theory (Baars, Dehaene)

---

*Implementation Guide Version: 1.0.0*  
*Last Updated: October 15, 2025*
