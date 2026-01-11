# AGI-SAC GUI Application Design

## Technology Stack

### Primary Framework: Gradio
- **Why Gradio**: Python-native, async-friendly, minimal boilerplate, built-in real-time updates
- **Version**: >=4.0.0
- **Deployment**: Local development server (production deployment optional)

### Supporting Libraries
- **Threading**: Python `threading` module for async simulation execution
- **Queue**: `queue.Queue` for thread-safe metric streaming
- **Matplotlib**: Embedded chart generation for static exports
- **Pandas**: Data manipulation for export and comparison features

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Gradio Web UI                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Config Tab   │ │ Monitor Tab  │ │ Results Tab  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
└────────────┬────────────────────────────────┬───────────┘
             │                                │
             ▼                                ▼
┌─────────────────────────────────────────────────────────┐
│              GUI Controller Layer                       │
│  - SimulationRunner (threading)                         │
│  - ConfigManager (validation, presets)                  │
│  - MetricsCollector (hook-based streaming)              │
│  - ExportManager (formats: JSON, CSV, HTML)             │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│         AGI-SAC Core (Existing Codebase)                │
│  - SimulationOrchestrator                               │
│  - AgentStateAnalyzer                                   │
│  - PrometheusMetrics                                    │
│  - PersistentHomologyTracker                            │
└─────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Component 1: GUI Layout Module (`gui/layout.py`)
**Responsibility**: Define Gradio interface structure and component organization
**Size Estimate**: ~150 lines
**Key Functions:**
- `create_config_tab()`: Parameter inputs, preset selector, validation display
- `create_monitor_tab()`: Progress bar, live charts, status indicators
- `create_results_tab()`: Summary dashboard, export buttons, comparison tool
- `build_interface()`: Assemble all tabs into single Gradio Blocks interface

**Interface:**
```python
def build_interface() -> gr.Blocks:
    """Create complete Gradio interface with all tabs."""
    pass
```

**Dependencies**: None (pure UI definition)

---

### Component 2: Configuration Manager (`gui/config_manager.py`)
**Responsibility**: Handle config validation, presets, and custom config management
**Size Estimate**: ~200 lines
**Key Functions:**
- `validate_parameters(params: Dict[str, Any]) -> Tuple[bool, List[str]]`
- `load_preset(name: str) -> SimulationConfig`
- `save_custom_config(config: SimulationConfig, filepath: str) -> bool`
- `parse_uploaded_config(file: bytes) -> SimulationConfig`

**Interface:**
```python
class ConfigManager:
    def __init__(self):
        self.current_config: Optional[SimulationConfig] = None

    def validate_parameters(self, **kwargs) -> Tuple[bool, List[str]]:
        """Validate simulation parameters, return (is_valid, error_messages)"""
        pass

    def get_preset(self, preset_name: str) -> SimulationConfig:
        """Load configuration preset"""
        pass

    def to_orchestrator_dict(self) -> Dict[str, Any]:
        """Convert to format expected by SimulationOrchestrator"""
        pass
```

**Dependencies**: `agisa_sac.config.SimulationConfig`, `agisa_sac.config.PRESETS`

---

### Component 3: Simulation Runner (`gui/simulation_runner.py`)
**Responsibility**: Execute simulations in background thread with lifecycle control
**Size Estimate**: ~250 lines
**Key Functions:**
- `start_simulation(config: Dict) -> str` (returns run_id)
- `pause_simulation() -> bool`
- `resume_simulation() -> bool`
- `stop_simulation() -> bool`
- `get_status() -> SimulationStatus`

**Interface:**
```python
class SimulationStatus(TypedDict):
    state: Literal["idle", "running", "paused", "completed", "error"]
    current_epoch: int
    total_epochs: int
    elapsed_time: float
    error_message: Optional[str]

class SimulationRunner:
    def __init__(self, metrics_queue: queue.Queue):
        self.orchestrator: Optional[SimulationOrchestrator] = None
        self.thread: Optional[threading.Thread] = None
        self.status: SimulationStatus = {...}
        self.metrics_queue = metrics_queue

    def start(self, config: Dict[str, Any]) -> bool:
        """Start simulation in background thread"""
        pass

    def pause(self) -> bool:
        """Pause simulation (set orchestrator.is_running = False)"""
        pass

    def stop(self) -> bool:
        """Gracefully stop simulation"""
        pass

    def get_status(self) -> SimulationStatus:
        """Get current simulation status"""
        pass
```

**Dependencies**: `agisa_sac.core.orchestrator.SimulationOrchestrator`

---

### Component 4: Metrics Collector (`gui/metrics_collector.py`)
**Responsibility**: Hook-based real-time metrics streaming from orchestrator to GUI
**Size Estimate**: ~200 lines
**Key Functions:**
- Register hooks with orchestrator for `post_epoch`, `tda_phase_transition`
- Collect metrics snapshot after each epoch
- Push metrics to thread-safe queue for GUI consumption
- Manage metric history (windowed buffer to prevent unbounded growth)

**Interface:**
```python
class MetricSnapshot(TypedDict):
    epoch: int
    timestamp: float
    agent_count: int
    satori_ratio: float
    tda_features: Dict[str, int]  # {dim: count}
    social_density: float
    cpu_percent: float
    memory_mb: float

class MetricsCollector:
    def __init__(self, metrics_queue: queue.Queue, max_history: int = 1000):
        self.metrics_queue = metrics_queue
        self.history: List[MetricSnapshot] = []
        self.max_history = max_history

    def setup_hooks(self, orchestrator: SimulationOrchestrator):
        """Register orchestrator hooks for metric collection"""
        orchestrator.register_hook("post_epoch", self._on_epoch_complete)
        orchestrator.register_hook("tda_phase_transition", self._on_tda_transition)

    def _on_epoch_complete(self, orchestrator, epoch, **kwargs):
        """Hook callback: collect metrics after epoch"""
        snapshot = self._capture_snapshot(orchestrator, epoch)
        self.history.append(snapshot)
        self.metrics_queue.put(snapshot)

    def get_history(self) -> List[MetricSnapshot]:
        """Return all collected metrics"""
        return self.history
```

**Dependencies**: `agisa_sac.core.orchestrator.SimulationOrchestrator`, `agisa_sac.utils.metrics.PrometheusMetrics`

---

### Component 5: Visualization Generator (`gui/visualization.py`)
**Responsibility**: Generate charts and plots for real-time display and export
**Size Estimate**: ~250 lines
**Key Functions:**
- `plot_metrics_timeseries(history: List[MetricSnapshot]) -> plt.Figure`
- `plot_tda_features(history) -> plt.Figure`
- `plot_satori_ratio(history) -> plt.Figure`
- `plot_archetype_distribution(analyzer: AgentStateAnalyzer) -> plt.Figure`
- `create_summary_dashboard(analyzer, history) -> Dict[str, plt.Figure]`

**Interface:**
```python
class VisualizationGenerator:
    @staticmethod
    def create_live_dashboard(history: List[MetricSnapshot]) -> Dict[str, Any]:
        """Create Gradio-compatible plot objects for live monitoring"""
        return {
            "progress": {"current": epoch, "total": total},
            "satori_plot": gr.LinePlot(...),
            "tda_plot": gr.LinePlot(...),
            "resource_plot": gr.LinePlot(...)
        }

    @staticmethod
    def create_static_plots(analyzer: AgentStateAnalyzer,
                           history: List[MetricSnapshot]) -> Dict[str, plt.Figure]:
        """Create matplotlib figures for export/results tab"""
        pass
```

**Dependencies**: `matplotlib`, `pandas`, Gradio plotting components

---

### Component 6: Export Manager (`gui/export_manager.py`)
**Responsibility**: Export simulation results in multiple formats
**Size Estimate**: ~200 lines
**Key Functions:**
- `export_json(orchestrator, history, filepath) -> bool`
- `export_csv(history, filepath) -> bool`
- `export_html_report(orchestrator, history, filepath) -> bool`
- `compare_runs(run1_path, run2_path) -> ComparisonReport`

**Interface:**
```python
class ExportManager:
    @staticmethod
    def export_json(orchestrator: SimulationOrchestrator,
                    metrics_history: List[MetricSnapshot],
                    output_path: str) -> bool:
        """Export full simulation state and metrics to JSON"""
        pass

    @staticmethod
    def export_csv(metrics_history: List[MetricSnapshot],
                   output_path: str) -> bool:
        """Export metrics time-series to CSV"""
        pass

    @staticmethod
    def export_html_report(orchestrator: SimulationOrchestrator,
                          metrics_history: List[MetricSnapshot],
                          output_path: str) -> bool:
        """Generate comprehensive HTML report with embedded charts"""
        pass

    @staticmethod
    def compare_runs(run1_data: Dict, run2_data: Dict) -> Dict[str, Any]:
        """Compare two simulation runs and generate difference report"""
        pass
```

**Dependencies**: `json`, `csv`, `pandas`, `matplotlib`, Jinja2 (for HTML templating)

---

### Component 7: Main Application (`gui/app.py`)
**Responsibility**: Wire all components together and launch Gradio server
**Size Estimate**: ~150 lines
**Key Functions:**
- Initialize all managers and runners
- Connect GUI callbacks to backend functions
- Handle state synchronization between tabs
- Launch Gradio interface

**Interface:**
```python
class AGISACGuiApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.metrics_queue = queue.Queue()
        self.runner = SimulationRunner(self.metrics_queue)
        self.collector = MetricsCollector(self.metrics_queue)
        self.export_manager = ExportManager()
        self.viz = VisualizationGenerator()

    def build_and_launch(self, share: bool = False, server_port: int = 7860):
        """Build Gradio interface and launch server"""
        interface = self._build_interface()
        interface.launch(share=share, server_port=server_port)

    def _build_interface(self) -> gr.Blocks:
        """Construct Gradio interface with all callbacks wired"""
        pass

    # Callback methods
    def _on_start_clicked(self, config_params):
        """Handle Start Simulation button"""
        pass

    def _on_pause_clicked(self):
        """Handle Pause button"""
        pass

    def _update_live_metrics(self):
        """Gradio.Timer callback for live metric updates"""
        pass
```

**Dependencies**: All other GUI components

## Data Flow

### Simulation Start Flow
1. User configures parameters in Config Tab → ConfigManager validates
2. User clicks "Start" → `app.py` receives callback
3. App creates orchestrator config dict via `ConfigManager.to_orchestrator_dict()`
4. `SimulationRunner.start()` creates SimulationOrchestrator in new thread
5. `MetricsCollector.setup_hooks()` registers hooks with orchestrator
6. Simulation runs, hooks fire → metrics pushed to queue
7. Gradio timer polls queue → updates live charts

### Pause/Resume Flow
1. User clicks "Pause" → `SimulationRunner.pause()` sets `orchestrator.is_running = False`
2. Orchestrator's `run_epoch()` checks flag, stops processing
3. User clicks "Resume" → `SimulationRunner.resume()` sets flag back to True, continues

### Export Flow
1. Simulation completes → status changes to "completed"
2. User navigates to Results Tab
3. User selects export format and clicks "Export" button
4. `ExportManager.export_*()` method called with orchestrator and metrics history
5. File saved to disk, success message shown in GUI

## Configuration Schema

```yaml
gui_settings:
  default_port: 7860
  share_public: false
  theme: "default"  # Gradio theme
  max_metrics_history: 1000  # max epochs to keep in memory
  live_update_interval: 2.0  # seconds between chart refreshes
  enable_debug_mode: false

simulation_defaults:
  preset: "default"
  auto_save_state: true
  save_interval_epochs: 50
```

## Error Handling Strategy

### Simulation Errors
- Catch exceptions in `SimulationRunner` thread
- Set status to "error" with descriptive message
- Display error in Monitor Tab with traceback (if debug mode)
- Offer "Reset" button to return to idle state

### Validation Errors
- Real-time validation in Config Tab
- Display error messages inline next to invalid fields
- Disable "Start" button until all fields valid

### Export Errors
- Show error modal with specific failure reason
- Suggest remediation (e.g., check disk space, file permissions)
- Log full error to file for debugging

## Testing Strategy

### Unit Tests
- Each component class tested independently
- Mock orchestrator and metrics queue for isolated testing
- Test edge cases: empty history, invalid configs, thread crashes

### Integration Tests
- Full simulation run with quick_test preset
- Verify metrics collection through hooks
- Test pause/resume functionality
- Validate export formats (JSON parseable, CSV loadable)

### Manual Testing Checklist
- [ ] Load each preset and verify parameters populate correctly
- [ ] Start simulation and verify progress bar updates
- [ ] Pause simulation and verify can resume
- [ ] Stop simulation and verify graceful shutdown
- [ ] Export to each format and verify files are valid
- [ ] Upload custom config JSON and verify loads correctly
- [ ] Test with large simulation (100 agents, 100 epochs)
- [ ] Verify memory usage doesn't grow unbounded

## Deployment

### Development
```bash
poetry install --with visualization
poetry run agisa-sac-gui
```

### Production (Optional)
- Package as standalone executable with PyInstaller
- Deploy as web service with nginx reverse proxy
- Docker container with Gradio server

## Future Enhancements (Post-MVP)

1. **Multi-Run Management**: Database-backed storage for multiple runs
2. **Advanced Visualization**: 3D TDA plots, interactive network graphs
3. **Protocol Injection UI**: GUI for divergence_stress, satori_probe
4. **Collaborative Features**: Share runs via URLs, comment system
5. **Hyperparameter Optimization**: Integrate with Hyperopt for auto-tuning
6. **Federation GUI**: Monitor distributed simulations across nodes

## Component Dependencies Graph

```
app.py (Component 7)
  ├── layout.py (Component 1)
  ├── config_manager.py (Component 2)
  ├── simulation_runner.py (Component 3)
  │     └── [AGI-SAC Core]
  ├── metrics_collector.py (Component 4)
  │     └── [AGI-SAC Core]
  ├── visualization.py (Component 5)
  └── export_manager.py (Component 6)
```

**Implementation Order**: 2 → 3 → 4 → 5 → 6 → 1 → 7

This order ensures each component can be tested with its dependencies already working.

## Definition of Done (per component)

- [ ] Implementation complete with all key functions
- [ ] Unit tests written with >80% coverage
- [ ] Docstrings for all public methods
- [ ] Integration test passes (if applicable)
- [ ] QA validation passes
- [ ] No blocking issues
