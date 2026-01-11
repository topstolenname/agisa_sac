# AGI-SAC GUI User Guide

## Overview

The AGI-SAC GUI provides a web-based interface for configuring, running, and monitoring multi-agent simulations. Built with Gradio, it offers:

- **Configuration Management**: Preset selection and parameter controls
- **Simulation Control**: Start/pause/resume/stop lifecycle management
- **Real-Time Visualization**: Live metrics and TDA plots during execution
- **Export & Analysis**: Results download and post-simulation analysis

## Installation

### Install Dependencies

```bash
# Install with Poetry (recommended)
poetry install

# Or install with pip
pip install -e .
```

The GUI requires these main dependencies (already in `pyproject.toml`):
- `gradio >= 4.0.0`
- `matplotlib >= 3.5.0`
- All standard AGI-SAC dependencies

## Launching the GUI

### Method 1: Command Line (Recommended)

```bash
# Launch on default port (7860)
agisa-sac-gui

# Launch with custom port
agisa-sac-gui --server-port 8080

# Create shareable public link
agisa-sac-gui --share

# Enable debug mode
agisa-sac-gui --debug
```

### Method 2: Python Module

```python
from agisa_sac.gui.app import main

main(server_port=7860, debug=False)
```

### Method 3: Direct Script

```bash
python src/agisa_sac/gui/app.py --server-port 7860
```

## Using the GUI

### Tab 1: Configuration

**Preset Selection:**
- Choose from: `quick_test`, `default`, `medium`, `large`
- Click "Load Preset" to populate all parameters

**Main Parameters:**
- **Number of Agents** (1-1000): Total agents in simulation
- **Number of Epochs** (1-1000): Simulation duration
- **Agent Memory Capacity** (10-1000): Max memories per agent
- **Random Seed**: For reproducible results

**Feature Flags:**
- **Use Semantic Memory**: Enable embedding-based retrieval
- **Use GPU Acceleration**: Requires CUDA setup

**Advanced Settings:**
- **Satori Threshold** (0.0-1.0): Detection sensitivity
- **TDA Max Dimension** (0-3): Homology dimensions to compute
- **Community Check Frequency**: Epochs between graph analysis
- **Epoch Log Frequency**: Log message interval

**File Operations:**
- Upload JSON config file
- Save current config to file

### Tab 2: Control

**Simulation Controls:**
- **▶️ Start Simulation**: Begin new simulation with current config
- **⏸️ Pause**: Temporarily pause execution
- **▶️ Resume**: Continue paused simulation
- **⏹️ Stop**: Terminate simulation gracefully

**Status Display:**
- Current state (IDLE/RUNNING/PAUSED/COMPLETED/ERROR)
- Progress: Current epoch / Total epochs
- Elapsed time in seconds

**Quick Metrics:**
- Agent count
- Satori wave ratio (real-time)

**Logs Viewer:**
- Recent log entries (expandable accordion)

### Tab 3: Visualization

**Metrics Time Series:**
- Select metrics to display (SRI, NDS, VSD, MCE, Satori Wave Ratio)
- View plots updating in real-time during simulation

**TDA Visualization:**
- Use epoch slider to browse persistence diagrams
- View topological features at any epoch

**Auto-Refresh:**
- Enable/disable automatic plot updates
- Configure refresh rate (1-10 seconds)
- Manual refresh button

### Tab 4: Export & Analysis

**Export Results:**
- Select formats: JSON, CSV, Markdown, HTML
- Download simulation results

**Summary Statistics:**
- System-wide metrics table
- Agent count, epochs completed
- Satori wave ratio, archetype entropy

**State Persistence:**
- Save simulation state to checkpoint file
- Load previous state to resume simulation

## Architecture

```
┌─────────────────────────────────────┐
│         Gradio Web UI               │
├─────────────────────────────────────┤
│ Config Tab | Control | Viz | Export │
└──────────────┬──────────────────────┘
               │
        ┌──────▼────────┐
        │ ConfigManager │
        │ MetricsCollector │
        │ VisualizationManager │
        └──────┬────────┘
               │
        ┌──────▼────────┐
        │ SimulationRunner │
        │ (Background Thread) │
        └──────┬────────┘
               │
        ┌──────▼────────┐
        │ Orchestrator  │
        │ (Hook System) │
        └───────────────┘
```

## Key Features

### Thread-Safe Execution
- Simulation runs in background daemon thread
- GUI remains responsive during long simulations
- Queue-based metrics passing (non-blocking)

### Real-Time Updates
- Hook-based metrics collection at each epoch
- Configurable update frequency (1-10 seconds)
- Live progress tracking

### State Management
- Save/load simulation checkpoints
- Resume from any epoch
- Full state serialization (agents, graph, TDA)

### Configuration Validation
- Real-time parameter validation
- Constraint checking (ranges, types)
- Clear error messages

## Troubleshooting

### GUI Won't Launch

**Issue**: `ModuleNotFoundError: No module named 'gradio'`

**Solution**:
```bash
poetry install
# or
pip install gradio>=4.0.0
```

### Port Already in Use

**Issue**: `OSError: [Errno 98] Address already in use`

**Solution**:
```bash
# Use a different port
agisa-sac-gui --server-port 7861

# Or kill the process using the port
lsof -ti:7860 | xargs kill -9
```

### Simulation Won't Start

**Issue**: Validation errors or configuration problems

**Solution**:
1. Check validation output in Configuration tab
2. Verify all parameters are within valid ranges
3. Try loading a known-good preset (e.g., "quick_test")
4. Check logs in Control tab for detailed error messages

### No Metrics Displayed

**Issue**: Plots remain empty during simulation

**Solution**:
1. Ensure auto-refresh is enabled in Visualization tab
2. Check that simulation is actually running (RUNNING state)
3. Wait for first epoch to complete
4. Click "Refresh Now" button manually

## Performance Tips

### For Large Simulations (100+ agents, 100+ epochs):

1. **Disable expensive features initially:**
   - Set TDA Max Dimension to 0 or 1
   - Increase Community Check Frequency to 20-50
   - Disable auto-refresh in visualization

2. **Use appropriate presets:**
   - `quick_test`: 3 agents, 5 epochs (testing)
   - `default`: 5 agents, 10 epochs (development)
   - `medium`: 20 agents, 50 epochs (standard)
   - `large`: 100 agents, 100 epochs (production)

3. **Monitor resources:**
   - GUI overhead is typically <500MB
   - Main memory usage from agent states
   - CPU usage spikes during TDA computation

## Next Steps

### Current Features (MVP)
✅ Configuration management with presets
✅ Simulation lifecycle controls (start/pause/resume/stop)
✅ Real-time status monitoring
✅ Basic visualization framework
✅ Export structure

### Coming Soon
🔜 Actual metrics plotting with live updates
🔜 TDA persistence diagram display
🔜 Social graph visualization
🔜 Chronicle export (echo manifestos)
🔜 Multi-simulation comparison
🔜 Protocol injection controls

## Contributing

The GUI is built with these core modules:

- `src/agisa_sac/gui/app.py` - Main application entry point
- `src/agisa_sac/gui/metrics_collector.py` - Hook-based metrics aggregation
- `src/agisa_sac/gui/visualization_manager.py` - Matplotlib figure generation
- `src/agisa_sac/gui/config_manager.py` - Configuration validation
- `src/agisa_sac/gui/simulation_runner.py` - Threading wrapper
- `src/agisa_sac/gui/tabs/` - Individual tab implementations

To extend the GUI:
1. Add new visualization functions to `visualization_manager.py`
2. Create new tab modules in `tabs/`
3. Wire up event handlers in tab creation functions
4. Use `MetricsCollector` hooks for real-time data

## Support

- **Issues**: https://github.com/topstolenname/agisa_sac/issues
- **Documentation**: See `/docs/` directory
- **Email**: tristan@mindlink.dev

## License

MIT License - See LICENSE file for details
