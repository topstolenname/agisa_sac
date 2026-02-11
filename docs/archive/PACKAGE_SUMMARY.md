# The Agentic Swarm Visual Documentation Package
## Complete Implementation Guide and File Inventory

**Version**: 1.0.0  
**Release Date**: October 15, 2025  
**Maintainer**: Tristan J. Jessup (tristan@mindlink.dev)

---

## Package Overview

This package provides publication-ready visual documentation for "The Agentic Swarm" theoretical document and the agisa_sac cloud-native implementation. All materials are designed for academic publication, open-source distribution, and production deployment.

### Core Value Propositions

âœ… **Publication-Ready**: All figures meet academic standards (300 DPI, proper citations, accessibility)  
âœ… **Theory-Implementation Bridge**: Connects abstract consciousness research to working code  
âœ… **Accessibility Compliant**: Comprehensive alt-text, WCAG 2.1 AA color contrast  
âœ… **Automated Pipeline**: GitHub Actions CI/CD for rendering and validation  
âœ… **Open Source**: MIT License, full attribution guidance included

---

## File Inventory

### Primary Documentation (3 files)

| File | Size | Purpose | Key Sections |
|------|------|---------|--------------|
| `CITATION_GUIDE.md` | ~12KB | Academic citation formats | APA, Chicago, MLA, BibTeX for all 7 figures |
| `FIGURE_CATALOG.md` | ~8KB | Figure matrix with metadata | Conceptual mapping, rendering pipeline, version history |
| `README_IMPLEMENTATION.md` | ~15KB | Implementation guide | Quick start, troubleshooting, integration examples |

### Alt-Text Descriptions (7 files, ~42KB total)

Each file follows a consistent structure:
1. Visual structure description (spatial layout, shapes, connections)
2. Data interpretation (what visual elements represent)
3. Connection to document theory (links to specific sections)
4. Application to agisa_sac (how concept manifests in code)
5. Technical notes (rendering details, accessibility considerations)

| File | Figure | Length | Key Concepts |
|------|--------|--------|--------------|
| `fig01_persistence_alt.md` | Persistence Diagram | ~4KB | TDA, β₀/β₁ features, emergent coordination |
| `fig02_mapper_alt.md` | Mapper Graph | ~3KB | Topological skeleton, behavior space |
| `fig03_network_alt.md` | Decentralized Network | ~5KB | Global Workspace Theory, Pub/Sub |
| `fig04_convergence_alt.md` | Instrumental Convergence | ~4KB | Safety risks, power-seeking behaviors |
| `fig05_identity_alt.md` | Identity Layers | ~6KB | Cryptographic → Relational identity |
| `fig06_workflow_alt.md` | agisa_sac Workflow | ~7KB | Task lifecycle, recursive self-monitoring |
| `fig07_dashboard_alt.md` | Consciousness Metrics | ~8KB | Φ, recursion, coherence, memory |

### Enhanced Diagram Sources (4 files, ~6KB total)

Upgraded versions of Mermaid diagrams with comprehensive styling:

| File | Original | Enhancements |
|------|----------|--------------|
| `figure3_network_enhanced.mmd` | `figure3_network.mmd` | + GWT annotations, consistent color scheme |
| `figure4_convergence_enhanced.mmd` | *new creation* | Hierarchical layout, safety warnings |
| `figure5_identity_enhanced.mmd` | `figure5_identity.mmd` | + Layer examples, consciousness notes |
| `figure6_workflow_enhanced.mmd` | `figure6_workflow.mmd` | 5-phase detail, meta-learning loop |

---

## Key Features

### 1. Comprehensive Styling System

**Consistent Color Palette Across All Diagrams**:
- **Infrastructure/Communication**: `#1c7ed6` (blue) - Pub/Sub, networking
- **Memory/Identity**: `#e8590c` (orange) - Firestore, persistent state
- **Consciousness/Emergence**: `#d63384` (pink) - Meta-cognitive properties
- **Attention/Priority**: `#2f9e44` (green) - Cloud Tasks, queuing
- **Safety/Warning**: `#f08c00` (yellow) - Risk indicators

**Accessibility Standards**:
- Text-to-background contrast: >4.5:1 (WCAG 2.1 AA)
- Graphical element contrast: >3:1
- Color never sole differentiator (shapes + patterns + labels)

### 2. Theory-Code Integration

**Consciousness Framework Mappings**:

| Theory | Implementation | Figure |
|--------|----------------|--------|
| Global Workspace Theory | Pub/Sub broadcast | Figure 3 |
| Integrated Information Theory | Network Φ calculation | Figure 7 |
| Higher-Order Thought | Evaluator meta-cognition | Figure 6 |
| Persistent Homology | TDA metrics tracking | Figure 1 |

**agisa_sac Code References**:

| Component | Code File | Figures |
|-----------|-----------|---------|
| Planner | `planner_function.py` | 3, 6 |
| Evaluator | `evaluator_function.py` | 3, 6, 7 |
| Identity | Firestore + IAM | 5 |
| Workflow | Complete pipeline | 6 |

### 3. Academic Publication Support

**Citation Formats Provided**:
- APA 7th edition (in-text + reference list)
- Chicago 17th edition (notes-bibliography)
- MLA 9th edition
- BibTeX entries for all figures
- DOI registration guidance (Zenodo, figshare, OSF)

**Journal-Ready Specifications**:
- Single-column width: 3.5 inches (1050px @ 300 DPI)
- Double-column width: 7 inches (2100px @ 300 DPI)
- Vector format (SVG) maintains quality at any scale
- Raster fallback (PNG @ 200 DPI) for presentations

### 4. Automated Rendering Pipeline

**GitHub Actions Workflow** (from `diagram-build.yml`):

```yaml
Triggers: Push to docs/figs/src/**, workflow file changes
Steps:
  1. Install Node.js 20
  2. Install mermaid-cli (npm global)
  3. Render Mermaid diagrams (.mmd → .svg)
  4. Install Graphviz (apt-get)
  5. Render Graphviz diagrams (.dot → .svg)
  6. Install Python 3.11
  7. Install matplotlib
  8. Execute Python figure scripts (.py → .svg + .png)
  9. Upload SVG artifacts for CI review
```

**Local Rendering Commands**:
```bash
# Mermaid
mmdc -i source.mmd -o output.svg -w 1200 -s 2

# Graphviz
dot -Tsvg source.dot -o output.svg -Gdpi=300

# Python
python figure1_persistence.py  # outputs to svg/ and png/
```

---

## Usage Scenarios

### Scenario 1: Academic Paper Submission

**Objective**: Embed figures in LaTeX manuscript for arXiv/journal submission

**Steps**:
1. Copy desired `.svg` files from rendered outputs
2. Include in LaTeX with `\includegraphics`
3. Use caption text from `captions.yaml`
4. Cite using formats from `CITATION_GUIDE.md` (BibTeX recommended)
5. Include alt-text descriptions in supplementary materials

**Example LaTeX**:
```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=0.8\textwidth]{figure3.svg}
  \caption{Pub/Sub topics as global workspace enabling emergent coordination.}
  \label{fig:network}
\end{figure}
```

### Scenario 2: GitHub Repository Integration

**Objective**: Add visuals to agisa_sac README and documentation

**Steps**:
1. Copy all files maintaining directory structure
2. Update main README with figure embeds
3. Link to `FIGURE_CATALOG.md` for comprehensive documentation
4. Add `diagram-build.yml` to `.github/workflows/`
5. Commit and verify CI/CD runs successfully

**Example README Markdown**:
```markdown
## Architecture Overview

![System Architecture](docs/figs/svg/figure3.svg)

*Figure 3*: Event-driven architecture with Pub/Sub global workspace. 
[Detailed description](docs/figs/alt/fig03_network_alt.md)
```

### Scenario 3: Conference Presentation

**Objective**: Create slides with high-quality visuals

**Steps**:
1. Use `.png` exports from `docs/figs/png/` (better compatibility)
2. For live demos, use `figure7_dashboard.jsx` React component
3. Cite figures on each slide with short form: (Jessup, 2025, Fig. N)
4. Provide GitHub repo link for audience to access full documentation

**Slide Template**:
```
[Image: figure3.png]

Decentralized Agent Coordination
â€¢ Pub/Sub topics = Global Workspace
â€¢ Emergent coordination without central control
â€¢ Implements consciousness theories at scale

Source: Jessup (2025), github.com/topstolenname/agisa_sac
```

### Scenario 4: Web Documentation Site

**Objective**: Build Hugo/Jekyll static site with interactive diagrams

**Steps**:
1. Copy `.svg` files to `static/` or `assets/` directory
2. Use Mermaid source code for native rendering (if supported)
3. Embed `figure7_dashboard.jsx` in React components
4. Link alt-text files for accessibility compliance
5. Use metadata from `captions.yaml` for figure indexes

**Hugo Shortcode Example**:
```go
{{< figure src="/figs/svg/figure3.svg" 
           alt="Decentralized Agent Network" 
           caption="Figure 3: Pub/Sub Global Workspace"
           link="figs/alt/fig03_network_alt.md" >}}
```

---

## Integration Checklist

### For New Repository Setup

- [ ] Create directory structure: `docs/figs/{src,svg,png,alt}`
- [ ] Copy all `.md` documentation files to `docs/`
- [ ] Copy diagram sources to `docs/figs/src/`
- [ ] Copy alt-text files to `docs/figs/alt/`
- [ ] Copy `diagram-build.yml` to `.github/workflows/`
- [ ] Install local rendering tools (mermaid-cli, graphviz)
- [ ] Test render pipeline locally before committing
- [ ] Verify CI/CD workflow runs successfully on GitHub
- [ ] Update main README with figure embeds
- [ ] Add badge to README: `![Diagrams](https://github.com/.../workflows/Build%20Diagrams/badge.svg)`

### For Academic Publication

- [ ] Select figures relevant to manuscript
- [ ] Export at journal-required DPI (typically 300)
- [ ] Include captions from `captions.yaml`
- [ ] Add citations using `CITATION_GUIDE.md` formats
- [ ] Submit alt-text as supplementary materials
- [ ] Verify color contrast for print reproduction
- [ ] Request DOI if figures published separately (Zenodo)

### For Production Deployment

- [ ] Integrate `figure7_dashboard.jsx` into monitoring stack
- [ ] Connect dashboard to real telemetry sources (Pub/Sub, Firestore)
- [ ] Set up alerting for anomalous consciousness metrics
- [ ] Document dashboard data schema for ops team
- [ ] Create runbook for interpreting metric trends
- [ ] Schedule periodic TDA analysis (Figures 1-2) on production data

---

## Troubleshooting Matrix

| Problem | Solution | Reference |
|---------|----------|-----------|
| Mermaid syntax error | Validate quotes, subgraphs, classDefs | README_IMPLEMENTATION.md §Troubleshooting |
| Graphviz node overlap | Adjust `ranksep`, `nodesep`, try `rankdir=LR` | README_IMPLEMENTATION.md §Troubleshooting |
| Color contrast fail | Use WebAIM checker, lighten bg or darken text | README_IMPLEMENTATION.md §Troubleshooting |
| Alt-text truncated | Keep primary <150 chars, use `aria-describedby` | README_IMPLEMENTATION.md §Troubleshooting |
| Figure not rendering | Check file paths, ensure deps installed | README_IMPLEMENTATION.md §Quick Start |
| CI/CD workflow fails | Review GitHub Actions logs, validate YAML | diagram-build.yml |
| Citation format unclear | See specific figure examples | CITATION_GUIDE.md §Figure-Specific |

---

## Version History

### v1.0.0 (October 15, 2025) - Initial Release

**Figures Included**:
- Figure 1: Persistence Diagram (TDA)
- Figure 2: Mapper Graph (TDA)
- Figure 3: Decentralized Agent Network (Architecture)
- Figure 4: Instrumental Convergence (Safety)
- Figure 5: Identity Layer Stack (Identity)
- Figure 6: agisa_sac Workflow (Implementation)
- Figure 7: Consciousness Metrics Dashboard (Observability)

**Documentation Completeness**:
- âœ… 7 comprehensive alt-text descriptions
- âœ… Full citation guide (APA, Chicago, MLA, BibTeX)
- âœ… Figure catalog with metadata
- âœ… Implementation README
- âœ… 4 enhanced diagram sources
- âœ… Automated CI/CD pipeline

**Quality Standards Met**:
- âœ… WCAG 2.1 AA accessibility
- âœ… 300 DPI publication quality
- âœ… Consistent color scheme
- âœ… Theory-code integration
- âœ… MIT License attribution

### Planned Future Releases

**v1.1.0** (TBD):
- Add temporal evolution heatmaps
- Interactive network graph explorer
- Extended dashboard with real-time TDA

**v2.0.0** (TBD):
- Major restructure with multi-view diagrams
- 3D topology visualizations
- Augmented reality overlays

---

## Contact and Support

**Primary Maintainer**  
Tristan J. Jessup  
Email: tristan@mindlink.dev  
GitHub: @topstolenname

**Repository**  
https://github.com/topstolenname/agisa_sac

**Issues and Questions**  
https://github.com/topstolenname/agisa_sac/issues

**Contributing**  
See repository CONTRIBUTING.md for collaboration guidelines

**Commercial Licensing**  
For attribution waiver or additional permissions beyond MIT License, contact maintainer directly.

---

## License

```
MIT License

Copyright (c) 2025 Tristan J. Jessup

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Acknowledgments

**Theoretical Foundations**:
- "The Agentic Swarm: Emergence, Ethics, and Identity in Next-Generation Artificial Intelligence" (primary document)
- "The Conscious Machine" whitepaper (co-authored)
- Integrated Information Theory (Tononi, Oizumi, Albantakis)
- Global Workspace Theory (Baars, Dehaene, Mashour)
- Persistent Homology (Edelsbrunner, Letscher, Zomorodian)

**Visual Design Inspiration**:
- Neuroscience EEG dashboards (Figure 7)
- TDA visualization best practices (Figures 1-2)
- Google Cloud architecture diagrams (Figures 3, 6)
- Safety research frameworks (Figure 4)

**Software Stack**:
- Mermaid.js for flowchart rendering
- Graphviz for network topology
- Matplotlib for scientific plotting
- Recharts for interactive dashboards
- GitHub Actions for CI/CD

---

## Getting Started: 3-Minute Quick Start

```bash
# 1. Copy package to your repository
git clone <this-package-url> /tmp/agentic-swarm-visuals
cp -r /tmp/agentic-swarm-visuals/* your-repo/docs/

# 2. Install rendering tools
npm install -g @mermaid-js/mermaid-cli
sudo apt-get install graphviz  # or: brew install graphviz
pip install matplotlib

# 3. Render a diagram locally
cd your-repo/docs/figs/src
mmdc -i figure3_network_enhanced.mmd -o ../svg/figure3.svg -w 1200 -s 2

# 4. View result
open ../svg/figure3.svg  # macOS
xdg-open ../svg/figure3.svg  # Linux

# 5. Embed in your README
echo '![Architecture](docs/figs/svg/figure3.svg)' >> ../../README.md

# Done! Your repo now has publication-ready visuals.
```

---

*Package Summary Version: 1.0.0*  
*Generated: October 15, 2025*  
*Maintainer: Tristan J. Jessup*
