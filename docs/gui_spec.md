# AGI-SAC GUI Application Specification

## Overview
A comprehensive web-based GUI application for configuring, running, and monitoring AGI-SAC multi-agent simulations in real-time.

## User Stories

### US-1: Configuration Management
**As a** researcher
**I want to** configure simulation parameters via a GUI
**So that** I can run experiments without editing JSON files or using CLI

**Acceptance Criteria:**
- User can select from existing presets (quick_test, default, medium, large)
- User can modify any parameter: num_agents (1-1000), num_epochs (1-1000), agent_capacity, etc.
- Parameter validation occurs in real-time with helpful error messages
- User can save custom configurations for later use
- User can load existing config JSON files via file upload

### US-2: Simulation Execution Control
**As a** researcher
**I want to** start/stop/pause simulations and see progress
**So that** I can manage long-running experiments efficiently

**Acceptance Criteria:**
- Single-click simulation start with selected configuration
- Real-time progress bar showing current epoch / total epochs
- Display of time elapsed and estimated time remaining
- Pause button that preserves simulation state
- Resume button to continue from paused state
- Stop button that gracefully terminates simulation
- Status indicators (idle/running/paused/completed/error)

### US-3: Real-Time Metrics Visualization
**As a** researcher
**I want to** see live metrics during simulation execution
**So that** I can monitor system behavior and detect anomalies early

**Acceptance Criteria:**
- Live updating charts for key metrics (refreshes every 1-2 seconds)
- Agent count, interactions/epoch, memory usage displayed
- TDA features (H0, H1) shown as line graphs over epochs
- Social graph density and clustering coefficient tracking
- Satori wave ratio (temporal resonance) visualization
- CPU and memory usage monitoring
- Metrics continue updating during simulation without blocking UI

### US-4: Results Analysis and Export
**As a** researcher
**I want to** analyze completed simulations and export data
**So that** I can document findings and compare experiments

**Acceptance Criteria:**
- Post-simulation dashboard with comprehensive metrics summary
- Archetype distribution visualization (bar chart or pie chart)
- Satori event timeline showing coordination regime changes
- Export results to JSON with all metrics and agent states
- Export CSV for time-series data (metrics per epoch)
- Generate HTML report with embedded visualizations
- Compare two simulation runs side-by-side with difference highlighting

### US-5: Simulation State Management
**As a** researcher
**I want to** save and load simulation states
**So that** I can checkpoint long experiments and resume later

**Acceptance Criteria:**
- Save button that serializes full orchestrator state to JSON
- Load button that restores simulation from saved state
- State includes all agents, memory, social graph, and TDA history
- Clear indication of loaded state (epoch, config summary)
- Resume simulation from loaded checkpoint

## Technical Requirements

### TR-1: Backend Integration
- Must use existing SimulationOrchestrator (no reimplementation)
- Async/threaded execution to keep GUI responsive during simulation
- Hook-based architecture for real-time metric updates
- Proper error handling and logging

### TR-2: Performance
- GUI must remain responsive during 1000-agent, 1000-epoch simulations
- Metrics updates should not block simulation execution
- Memory-efficient streaming of metrics (don't accumulate unbounded history)
- Graceful degradation if TDA computation is slow

### TR-3: Usability
- Single-page application layout with organized tabs/sections
- Mobile-responsive design (Gradio default)
- Tooltips explaining advanced parameters
- Sensible defaults for all parameters
- Clear error messages with actionable guidance

### TR-4: Testing
- Unit tests for all backend components (>80% coverage)
- Integration tests for orchestrator hooks
- Manual testing checklist for GUI interactions
- Test simulations with various configs (quick, medium, large)

### TR-5: Documentation
- User guide with screenshots explaining each section
- Developer guide explaining architecture and extension points
- Example workflows for common research tasks
- API documentation for programmatic access (if applicable)

## Non-Functional Requirements

### NFR-1: Reliability
- Simulation crashes should not crash GUI
- State corruption should be prevented (atomic saves)
- Errors displayed in GUI with recovery suggestions

### NFR-2: Maintainability
- Clean separation: GUI layer, simulation backend, metrics collection
- Modular components that can be tested independently
- Configuration via environment variables where appropriate
- Code follows AGI-SAC project conventions (Black, Ruff)

### NFR-3: Extensibility
- Easy to add new visualization charts
- Hook system allows new metrics without GUI changes
- Export formats can be extended
- Plugin architecture for custom analysis modules (future)

## Out of Scope (Phase 1)

- Multi-user collaboration features
- Database-backed result storage (file-based only)
- Distributed simulation across multiple machines
- Real-time collaborative editing of configs
- Advanced protocol injection UI (CLI-based for now)
- Custom visualization DSL

## Success Metrics

1. Researchers can configure and run simulations without CLI knowledge
2. 90%+ of common workflows achievable via GUI
3. Real-time metrics update smoothly (<1s latency) during simulation
4. Zero data loss on graceful shutdown or pause
5. User guide comprehensible to non-technical users
6. Test coverage >80% for all new code
