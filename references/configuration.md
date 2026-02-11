# Configuration

Per-project customization via `.dev-team-config.yml`. All settings have sensible
defaults — configuration is optional but recommended for production projects.

## Table of Contents

1. [Config File Format](#config-file-format)
2. [All Settings](#all-settings)
3. [Loading & Validation](#loading--validation)
4. [Security Track Configuration](#security-track-configuration)
5. [Dry-Run Mode](#dry-run-mode)
6. [Project Export](#project-export)

---

## Config File Format

Place `.dev-team-config.yml` in the project root. The orchestrator reads it at
startup and merges with defaults.

### Minimal Example

```yaml
# .dev-team-config.yml
min_coverage: 85.0
max_component_attempts: 4
```

### Full Example

```yaml
# .dev-team-config.yml — all available settings

# Quality thresholds
min_coverage: 85.0              # Minimum test coverage percentage
max_component_attempts: 4       # QA failures before escalation
coverage_fail_is_error: true    # Treat low coverage as QA failure

# Human-in-the-loop gates
auto_approve_low_risk: true     # Skip Gate 2 for low-risk components
low_risk_components:            # Components that auto-approve
  - config-parser
  - utils
  - models
require_review_components:      # Components that always need review
  - authentication
  - payment
  - data-migration

# Git settings
git_default_branch: main        # Default branch name
conventional_commits: true      # Enforce conventional commit format
auto_merge: true                # Auto-merge component branches

# Testing
test_timeout_seconds: 60        # Per-test timeout
test_framework: pytest          # pytest | unittest | jest | mocha
lint_command: "ruff check src/" # Linter command
type_check_command: "mypy src/" # Type checker command

# Time tracking
track_time: true                # Enable component time tracking
size_estimates:                 # Override default time estimates (minutes)
  XS: 10
  S: 20
  M: 30
  L: 60
  XL: 120

# Dry-run mode
dry_run: false                  # Simulate without execution

# Security Track
enable_security_track: true     # Enable Threat-Modeler + Gatekeeper pipeline
security_required_components: [] # Allow-list (empty = all components)
security_skip_components:       # Skip-list (overrides required)
  - utils
  - config-parser
security_denied_patterns:       # Extend baseline deny-list
  - "\\bpayload\\b"
  - "\\bshellcode\\b"
max_security_gate_attempts: 2   # Gatekeeper retries before escalation

# Output
project_layout: standard        # standard | flat | monorepo
```

---

## All Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `min_coverage` | float | 80.0 | Minimum test coverage % |
| `max_component_attempts` | int | 3 | QA failures before escalation |
| `coverage_fail_is_error` | bool | true | Low coverage = QA failure |
| `auto_approve_low_risk` | bool | false | Auto-approve Gate 2 for low-risk |
| `low_risk_components` | list | [] | Components that auto-approve |
| `require_review_components` | list | [] | Components requiring human review |
| `git_default_branch` | str | "main" | Default git branch |
| `conventional_commits` | bool | true | Enforce commit format |
| `auto_merge` | bool | true | Auto-merge on QA pass |
| `test_timeout_seconds` | int | 60 | Per-test timeout |
| `test_framework` | str | "pytest" | Testing framework |
| `lint_command` | str | "ruff check src/" | Lint command |
| `type_check_command` | str | "mypy src/" | Type check command |
| `track_time` | bool | true | Enable time tracking |
| `size_estimates` | dict | see above | Minutes per size category |
| `dry_run` | bool | false | Simulate without execution |
| `enable_security_track` | bool | true | Enable Threat-Modeler + Gatekeeper pipeline |
| `security_required_components` | list | [] | Allow-list — if non-empty, only these get security review |
| `security_skip_components` | list | [] | Skip-list — these never get security review |
| `security_denied_patterns` | list | [] | Additional regex patterns for artifact hygiene gate |
| `max_security_gate_attempts` | int | 2 | Gatekeeper retries before escalating to Threat-Modeler |
| `project_layout` | str | "standard" | Directory layout style |

---

## Loading & Validation

### Implementation

```python
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

@dataclass
class DevTeamConfig:
    """Project configuration with sensible defaults."""
    # Quality
    min_coverage: float = 80.0
    max_component_attempts: int = 3
    coverage_fail_is_error: bool = True

    # Human gates
    auto_approve_low_risk: bool = False
    low_risk_components: List[str] = field(default_factory=list)
    require_review_components: List[str] = field(default_factory=list)

    # Git
    git_default_branch: str = "main"
    conventional_commits: bool = True
    auto_merge: bool = True

    # Testing
    test_timeout_seconds: int = 60
    test_framework: str = "pytest"
    lint_command: str = "ruff check src/"
    type_check_command: str = "mypy src/"

    # Time tracking
    track_time: bool = True
    size_estimates: Dict[str, int] = field(
        default_factory=lambda: {
            "XS": 10, "S": 20, "M": 30, "L": 60, "XL": 120
        }
    )

    # Modes
    dry_run: bool = False
    project_layout: str = "standard"

    # Security Track
    enable_security_track: bool = True
    security_required_components: List[str] = field(default_factory=list)
    security_skip_components: List[str] = field(default_factory=list)
    security_denied_patterns: List[str] = field(default_factory=list)
    max_security_gate_attempts: int = 2

    @classmethod
    def load(cls, project_root: Path) -> "DevTeamConfig":
        """Load config from .dev-team-config.yml, falling back to defaults."""
        config_path = project_root / ".dev-team-config.yml"
        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

        # Validate and merge with defaults
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                print(f"⚠️  Unknown config key: {key}")

        config.validate()
        return config

    def validate(self) -> None:
        """Validate configuration values."""
        if not (0 <= self.min_coverage <= 100):
            raise ValueError(f"min_coverage must be 0-100, got {self.min_coverage}")
        if self.max_component_attempts < 1:
            raise ValueError("max_component_attempts must be >= 1")
        if self.test_timeout_seconds < 1:
            raise ValueError("test_timeout_seconds must be >= 1")
        valid_frameworks = {"pytest", "unittest", "jest", "mocha"}
        if self.test_framework not in valid_frameworks:
            raise ValueError(
                f"test_framework must be one of {valid_frameworks}, "
                f"got '{self.test_framework}'"
            )
```

---

## Security Track Configuration

The Security Track inserts Threat-Modeler and Security-Gatekeeper agents between
Developer and QA-Critic. It is **enabled by default** for production-ready projects.

### Behavior Summary

| Setting | Effect |
|---------|--------|
| `enable_security_track: true` | All components go through security review (default) |
| `enable_security_track: false` | Developer routes directly to QA-Critic |
| `security_required_components: [auth, api]` | Only listed components get security review |
| `security_skip_components: [utils]` | Listed components skip security (overrides required) |
| `security_denied_patterns: [...]` | Additional regex patterns appended to baseline deny-list |
| `max_security_gate_attempts: 2` | Gatekeeper retries before escalating to Threat-Modeler rewrite |

### Resolution Order

The orchestrator resolves security routing per component as follows:

1. If `enable_security_track` is `false` → skip security
2. If component is in `security_skip_components` → skip security
3. If `security_required_components` is non-empty and component is NOT in it → skip security
4. Otherwise → run security (Threat-Modeler → Gatekeeper → QA-Critic)

### Example: Mixed Security Policy

```yaml
enable_security_track: true
security_required_components: []  # Empty = all components
security_skip_components:
  - config-parser
  - utils
  - models
max_security_gate_attempts: 3
security_denied_patterns:
  - "\\bpayload\\b"
  - "\\bshellcode\\b"
  - "\\bexfiltrat\\w+\\b"
```

This runs security review for all components except `config-parser`, `utils`,
and `models`. The gatekeeper gets 3 attempts before escalating.

---

## Dry-Run Mode

Simulate the entire workflow without writing files, running tests, or
committing to git. Useful for validating a project plan.

### Behavior

| Operation | Normal Mode | Dry-Run Mode |
|-----------|-------------|--------------|
| Create files | Writes to disk | Prints "would create: path" |
| Run tests | Executes pytest | Prints "would run: pytest ..." |
| Git commit | Commits changes | Prints "would commit: message" |
| State save | Writes JSON | Updates in-memory only |
| Human gates | Pauses for approval | Auto-approves |

### Usage

```yaml
# .dev-team-config.yml
dry_run: true
```

Or via CLI:
```bash
dev-orchestrator plan --dry-run my-project
```

### Output

```
🔍 DRY RUN MODE — no files will be modified

Phase 1: Planning
  📝 Would create: planning/spec.md
  📝 Would create: planning/design.md
  📝 Would create: planning/dependencies.mermaid
  ✅ Would request: Human approval (auto-approved in dry-run)

Phase 2: Implementation
  Component 1/5: database-layer (Size: M, Est: 30 min)
    📝 Would create: src/database_layer.py
    🧪 Would run: pytest tests/test_database_layer.py
    ✅ Would commit: feat(db): implement database layer

  Component 2/5: business-logic (Size: S, Est: 20 min)
    📝 Would create: src/business_logic.py
    🧪 Would run: pytest tests/test_business_logic.py
    ✅ Would commit: feat(logic): implement business logic
  ...

Phase 3: Integration
  🧪 Would run: pytest tests/integration/
  ✅ Would request: Human validation (auto-approved in dry-run)

Phase 4: Documentation
  📝 Would create: README.md, docs/ARCHITECTURE.md
  ✅ Would request: Human final review (auto-approved in dry-run)

Summary:
  Components: 5
  Estimated time: 160 minutes
  Files to create: 12
  Tests to write: ~25
```

---

## Project Export

Export project state and metrics for external tooling or reporting.

### Export Formats

```python
def export_state(project_root: Path, format: str = "json") -> str:
    """Export project state in various formats."""
    state = load_state(project_root)

    if format == "json":
        return json.dumps(state, indent=2)

    elif format == "markdown":
        return format_markdown_report(state)

    elif format == "csv":
        return format_csv_metrics(state)

    else:
        raise ValueError(f"Unknown format: {format}")
```

### Markdown Report

```bash
dev-orchestrator export --format=markdown my-project > report.md
```

Produces a human-readable summary with component status table, quality
metrics, time tracking data, and revision history.

### CSV Metrics

```bash
dev-orchestrator export --format=csv my-project > metrics.csv
```

Columns: component, status, size, estimated_min, actual_min, attempts,
coverage, tests_passed, tests_failed, commit_hash
