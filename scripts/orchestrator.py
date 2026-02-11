#!/usr/bin/env python3
"""
Dev Team Orchestrator v2.1 — Production-ready state machine for
coordinating AI agent workflows.

Features:
- Atomic state persistence with backup & file locking
- Dependency graph validation (topological sort)
- Per-project configuration via .dev-team-config.yml
- Rollback command for failed components
- Enhanced error context with actionable suggestions
- Component time tracking (estimated vs actual)
- Progressive QA feedback (streaming test output)
- Dry-run mode for plan validation

Usage:
    python orchestrator.py <project-name>     # Start or resume
    python orchestrator.py status <project>   # Show status
    python orchestrator.py rollback <comp>    # Rollback component
    python orchestrator.py --reset            # Start fresh
    python orchestrator.py --dry-run <name>   # Simulate
"""
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Set, Tuple

import re

# Conditional import for config
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ─── Constants ───────────────────────────────────────────────────────
STATE_FILE = ".dev-team-state.json"
CONFIG_FILE = ".dev-team-config.yml"
LOCK_FILE = ".dev-team-state.lock"
PERSONAS_FILE = Path(__file__).parent.parent / "references" / "agent-personas.md"


# ─── Enums ───────────────────────────────────────────────────────────
class AgentRole(str, Enum):
    ARCHITECT = "architect-pm"
    DEVELOPER = "developer"
    THREAT_MODELER = "threat-modeler"
    SECURITY_GATEKEEPER = "security-gatekeeper"
    QA_CRITIC = "qa-critic"
    WRITER = "tech-writer"

class ComponentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    QA_PASSED = "qa_passed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class Phase(str, Enum):
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    INTEGRATION = "integration"
    DOCUMENTATION = "documentation"
    COMPLETE = "complete"


# ─── Configuration ───────────────────────────────────────────────────
@dataclass
class DevTeamConfig:
    """Project configuration with sensible defaults."""
    min_coverage: float = 80.0
    max_component_attempts: int = 3
    coverage_fail_is_error: bool = True
    auto_approve_low_risk: bool = False
    low_risk_components: List[str] = field(default_factory=list)
    require_review_components: List[str] = field(default_factory=list)
    git_default_branch: str = "main"
    conventional_commits: bool = True
    auto_merge: bool = True
    test_timeout_seconds: int = 60
    test_framework: str = "pytest"
    lint_command: str = "ruff check src/"
    type_check_command: str = "mypy src/"
    track_time: bool = True
    size_estimates: Dict[str, int] = field(
        default_factory=lambda: {"XS": 10, "S": 20, "M": 30, "L": 60, "XL": 120}
    )
    dry_run: bool = False
    # Security Track
    enable_security_track: bool = True
    security_required_components: List[str] = field(default_factory=list)
    security_skip_components: List[str] = field(default_factory=list)
    security_denied_patterns: List[str] = field(default_factory=list)
    max_security_gate_attempts: int = 2

    @classmethod
    def load(cls, project_root: Path) -> "DevTeamConfig":
        config_path = project_root / CONFIG_FILE
        if not config_path.exists() or not HAS_YAML:
            return cls()
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                print(f"⚠️  Unknown config key: {key}")
        return config


# ─── Atomic State Persistence ────────────────────────────────────────
@contextmanager
def state_lock(lock_path: Path) -> Generator[None, None, None]:
    """Exclusive file lock to prevent concurrent instances."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(lock_path, "w")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    except IOError:
        f.close()
        raise RuntimeError(
            "Another orchestrator instance is running.\n"
            f"Wait for it to finish or remove {lock_path}"
        )
    finally:
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        f.close()


def atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    """Write JSON atomically using temp file + rename."""
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=path.parent, prefix=".tmp_state_", suffix=".json"
    )
    try:
        with os.fdopen(tmp_fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        Path(tmp_path).rename(path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def save_state(state: dict, project_root: Path) -> None:
    """Save state with backup and file locking."""
    state_file = project_root / STATE_FILE
    backup_file = state_file.with_suffix(".json.backup")
    lock_file = project_root / LOCK_FILE

    with state_lock(lock_file):
        if state_file.exists():
            state_file.rename(backup_file)
        try:
            atomic_write_json(state_file, state)
            backup_file.unlink(missing_ok=True)
        except Exception as e:
            if backup_file.exists():
                backup_file.rename(state_file)
            raise RuntimeError(f"State save failed: {e}")


def load_state(project_root: Path) -> dict:
    """Load state from file or return default."""
    state_file = project_root / STATE_FILE
    if state_file.exists():
        return json.loads(state_file.read_text())
    return {
        "schema_version": "2.0",
        "project": {"name": "unknown", "root": str(project_root), "created_at": None},
        "phase": Phase.PLANNING,
        "current_component": None,
        "components": [],
        "quality_metrics": {
            "total_tests": 0, "passing_tests": 0,
            "coverage": 0.0, "qa_failures_total": 0,
        },
        "human_approvals": {
            "design_approved": False,
            "integration_approved": False,
            "release_approved": False,
        },
        "history": [],
    }


# ─── Git Operations ──────────────────────────────────────────────────
class GitOperationError(Exception):
    def __init__(self, operation: str, stderr: str, suggestion: str):
        self.suggestion = suggestion
        super().__init__(f"{operation} failed: {stderr}\n💡 {suggestion}")


def run_git(args: list, cwd: Path) -> Tuple[bool, str, str]:
    result = subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()


def diagnose_git_error(operation: str, stderr: str, cwd: Path) -> str:
    if "user.name" in stderr or "user.email" in stderr:
        return (
            "Configure git:\n"
            "  git config user.name 'Dev Orchestrator'\n"
            "  git config user.email 'orchestrator@localhost'"
        )
    elif "CONFLICT" in stderr:
        return f"Resolve conflicts: cd {cwd} && git status"
    elif "not a git repository" in stderr:
        return f"Init git: cd {cwd} && git init -b main"
    elif "nothing to commit" in stderr:
        return "No changes — this is usually fine."
    return f"Check: cd {cwd} && git status"


def ensure_git(cwd: Path, branch: str = "main") -> None:
    """Initialize git repo if needed."""
    if not (cwd / ".git").exists():
        run_git(["init", "-b", branch], cwd)
        run_git(["config", "user.name", "Dev Orchestrator"], cwd)
        run_git(["config", "user.email", "orchestrator@localhost"], cwd)


# ─── Dependency Validation ───────────────────────────────────────────
def validate_and_sort(components: List[Dict]) -> Tuple[List[str], List[str]]:
    """Validate DAG and return topological implementation order."""
    all_names = {c["name"] for c in components}
    graph: Dict[str, Set[str]] = {}
    errors = []

    for comp in components:
        name = comp["name"]
        deps = set(comp.get("dependencies", []))
        graph[name] = deps
        missing = deps - all_names
        if missing:
            errors.append(
                f"'{name}' depends on undefined: {', '.join(sorted(missing))}. "
                f"Available: {', '.join(sorted(all_names))}"
            )

    if errors:
        return [], errors

    # Kahn's algorithm
    in_degree = {n: len(d) for n, d in graph.items()}
    queue = sorted([n for n, d in in_degree.items() if d == 0])
    order = []

    while queue:
        node = queue.pop(0)
        order.append(node)
        for name, deps in graph.items():
            if node in deps:
                in_degree[name] -= 1
                if in_degree[name] == 0:
                    queue.append(name)
        queue.sort()

    if len(order) != len(all_names):
        remaining = all_names - set(order)
        cycle_info = [
            f"  {n} → {', '.join(sorted(graph[n] & remaining))}"
            for n in sorted(remaining)
        ]
        errors.append(
            "Circular dependency detected:\n" + "\n".join(cycle_info) +
            "\n💡 Extract shared logic or use dependency injection."
        )
        return [], errors

    return order, []


# ─── Component Discovery ────────────────────────────────────────────
def extract_components_from_design(design_path: Path) -> List[Dict]:
    """Parse design.md for component definitions."""
    if not design_path.exists():
        return []

    content = design_path.read_text()
    components = []
    in_section = False
    current = None

    for line in content.splitlines():
        if line.strip().startswith("## Component"):
            in_section = True
            continue
        elif line.strip().startswith("## ") and in_section:
            break

        if not in_section:
            continue

        comp_match = re.match(r"\d+\.\s+\*\*(.+?)\*\*\s*[-—]\s*(.+)", line)
        if comp_match:
            if current:
                components.append(current)
            current = {
                "name": comp_match.group(1).strip().lower().replace(" ", "-"),
                "description": comp_match.group(2).strip(),
                "dependencies": [],
                "size": "M",
                "status": ComponentStatus.PENDING,
                "attempts": 0,
                "started_at": None,
                "completed_at": None,
                "commit_hash": None,
                "security_status": "pending",
                "security_gate_attempts": 0,
                "security_last_gate_result": None,
            }
            continue

        if current:
            if line.strip().startswith("- Dependencies:"):
                deps_str = line.split(":", 1)[1].strip()
                if deps_str.lower() not in ("none", ""):
                    current["dependencies"] = [
                        d.strip().lower().replace(" ", "-")
                        for d in deps_str.split(",")
                    ]
            elif line.strip().startswith("- Size:"):
                current["size"] = line.split(":", 1)[1].strip().upper()

    if current:
        components.append(current)
    return components


# ─── Security Artifact Validation ────────────────────────────────────
DENIED_PATTERNS = [
    r"\battacker\b", r"\badversary\b", r"\bexploit\b",
    r"\bhack\b", r"\bbreach\b", r"\bbypass\b",
    r"\binjection attack\b", r"\bescalat\w+\b",
    r"step\s*\d", r"first.*then.*finally",
    r"\bif an attacker\b", r"\ba malicious\b",
]


def validate_security_artifacts(
    project_root: Path, config: Optional["DevTeamConfig"] = None
) -> Tuple[bool, List[str]]:
    """
    Validate security artifacts contain no procedural/narrative language.
    Returns (is_valid, list_of_violations).
    """
    violations = []
    findings_path = project_root / "security" / "security-findings.json"
    requirements_path = project_root / "security" / "security-requirements.md"

    files_to_check: List[Path] = []
    if findings_path.exists():
        files_to_check.append(findings_path)
    if requirements_path.exists():
        files_to_check.append(requirements_path)

    if not files_to_check:
        return True, []  # No security artifacts yet — OK

    # Load additional denied patterns from config
    extra_patterns = []
    if config:
        extra_patterns = config.security_denied_patterns
    else:
        config_path = project_root / CONFIG_FILE
        if config_path.exists() and HAS_YAML:
            with open(config_path) as f:
                data = yaml.safe_load(f) or {}
            extra_patterns = data.get("security_denied_patterns", [])

    all_patterns = DENIED_PATTERNS + extra_patterns

    for filepath in files_to_check:
        content = filepath.read_text().lower()
        for pattern in all_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violations.append(
                    f"  {filepath.name}: denied pattern '{pattern}' "
                    f"matched {len(matches)}× — rewrite as invariant"
                )

    # Schema validation for findings JSON
    if findings_path.exists():
        try:
            findings = json.loads(findings_path.read_text())
            if not isinstance(findings, list):
                violations.append(
                    "  security-findings.json: must be a JSON array"
                )
            else:
                required_keys = {"id", "severity", "component", "category",
                                 "required_invariant", "verification"}
                for i, finding in enumerate(findings):
                    missing = required_keys - set(finding.keys())
                    if missing:
                        violations.append(
                            f"  security-findings.json[{i}]: missing keys: "
                            f"{', '.join(sorted(missing))}"
                        )
        except json.JSONDecodeError as e:
            violations.append(f"  security-findings.json: invalid JSON — {e}")

    return len(violations) == 0, violations


# ─── Progressive Test Execution ──────────────────────────────────────
def run_tests_streaming(
    test_file: str, component: str, config: DevTeamConfig
) -> Dict[str, Any]:
    """Execute tests with real-time streaming output."""
    cmd = ["python", "-m", "pytest", test_file, "-v"]
    if config.test_framework == "pytest":
        cmd += [
            "--cov", f"src/{component.replace('-', '_')}",
            "--cov-report", "term-missing",
            f"--timeout={config.test_timeout_seconds}",
        ]

    if config.dry_run:
        print(f"  🔍 Would run: {' '.join(cmd)}")
        return {"exit_code": 0, "output": "DRY RUN", "passed": True}

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        )
    except FileNotFoundError:
        return {
            "exit_code": 1,
            "output": f"Command not found: {cmd[0]}",
            "passed": False,
        }

    output_lines = []
    print(f"  🧪 Running tests for {component}...")
    for line in proc.stdout:
        sys.stdout.write(f"    {line}")
        sys.stdout.flush()
        output_lines.append(line)

    proc.wait()
    return {
        "exit_code": proc.returncode,
        "output": "".join(output_lines[-100:]),
        "passed": proc.returncode == 0,
    }


# ─── Rollback ────────────────────────────────────────────────────────
def rollback_component(project_root: Path, component_name: str) -> None:
    """Reset a failed component to pending state."""
    state = load_state(project_root)
    comp = next(
        (c for c in state["components"] if c["name"] == component_name), None
    )
    if not comp:
        print(f"❌ Component '{component_name}' not found.")
        sys.exit(1)

    # Clean up git branch
    branch = f"component/{component_name}"
    try:
        run_git(["checkout", state["project"].get("git_branch", "main")], project_root)
        run_git(["branch", "-D", branch], project_root)
    except Exception:
        pass  # Branch may not exist

    comp["status"] = ComponentStatus.PENDING
    comp["attempts"] = 0
    comp["started_at"] = None
    comp["completed_at"] = None
    comp["commit_hash"] = None

    if state.get("current_component") == component_name:
        state["current_component"] = None

    save_state(state, project_root)
    print(f"✅ Rolled back: {component_name}")


# ─── Status Display ─────────────────────────────────────────────────
def show_status(project_root: Path) -> None:
    """Print project status dashboard."""
    state = load_state(project_root)
    components = state.get("components", [])
    metrics = state.get("quality_metrics", {})

    total = len(components)
    done = sum(1 for c in components if c["status"] == ComponentStatus.QA_PASSED)
    progress = int((done / total * 20)) if total > 0 else 0

    print(f"\n{'═' * 52}")
    print(f"  DEV TEAM ORCHESTRATION STATUS")
    print(f"{'═' * 52}")
    print(f"  Project: {state['project']['name']}")
    print(f"  Phase:   {state['phase']} ({done}/{total} components)")
    print(f"  Progress: {'█' * progress}{'░' * (20 - progress)} {done}/{total}")
    print(f"{'─' * 52}")

    status_icons = {
        ComponentStatus.QA_PASSED: "✅",
        ComponentStatus.IN_PROGRESS: "🔧",
        ComponentStatus.PENDING: "⏳",
        ComponentStatus.FAILED: "❌",
        ComponentStatus.ROLLED_BACK: "🔄",
    }

    sec_icons = {
        "pending": "⏳", "modeled": "🔍", "sanitized": "🧹",
        "gated": "🔒", None: "—",
    }

    for comp in components:
        icon = status_icons.get(comp["status"], "?")
        sec = sec_icons.get(comp.get("security_status"), "—")
        extra = ""
        if comp.get("completed_at") and comp.get("started_at"):
            try:
                start = datetime.fromisoformat(comp["started_at"])
                end = datetime.fromisoformat(comp["completed_at"])
                mins = (end - start).total_seconds() / 60
                extra = f" ({mins:.1f}m)"
            except (ValueError, TypeError):
                pass
        gate_info = ""
        gate_attempts = comp.get("security_gate_attempts", 0)
        if gate_attempts > 0:
            gate_info = f" [gate: {comp.get('security_last_gate_result', '?')}, {gate_attempts}×]"
        print(f"    {icon} {sec} {comp['name']}{extra}{gate_info}")

    print(f"{'─' * 52}")
    print(f"  Tests: {metrics.get('passing_tests', 0)} passing")
    print(f"  Coverage: {metrics.get('coverage', 0):.1f}%")
    print(f"  QA Failures: {metrics.get('qa_failures_total', 0)} total")
    print(f"{'═' * 52}\n")


# ─── Persona Loader ─────────────────────────────────────────────────
def load_personas() -> Dict[str, str]:
    """Extract agent prompts from markdown file."""
    if not PERSONAS_FILE.exists():
        return {}
    content = PERSONAS_FILE.read_text()
    personas = {}
    current_role = None
    current_content = []

    for line in content.splitlines():
        if line.startswith("# Role:"):
            if current_role:
                personas[current_role] = "\n".join(current_content)
            current_role = line.split(":", 1)[1].strip().lower()
            current_content = []
        elif current_role:
            current_content.append(line)

    if current_role:
        personas[current_role] = "\n".join(current_content)
    return personas


# ─── Main Orchestrator ───────────────────────────────────────────────
class Orchestrator:
    def __init__(self, project_name: str, project_root: Optional[Path] = None):
        self.root = project_root or Path.cwd()
        self.config = DevTeamConfig.load(self.root)
        self.state = load_state(self.root)
        self.personas = load_personas()

        if self.state["project"]["name"] == "unknown":
            self.state["project"]["name"] = project_name
            self.state["project"]["created_at"] = datetime.now().isoformat()

    def save(self) -> None:
        save_state(self.state, self.root)

    def _should_run_security(self, component_name: str) -> bool:
        """Determine if security track should run for this component."""
        if not self.config.enable_security_track:
            return False
        if component_name in self.config.security_skip_components:
            return False
        if self.config.security_required_components:
            return component_name in self.config.security_required_components
        return True  # Default: security enabled for all components

    def get_next_task(self) -> Tuple[Optional[AgentRole], str]:
        """Core state machine: determine next agent and task."""
        phase = self.state["phase"]

        # ── PLANNING ──
        if phase == Phase.PLANNING:
            spec = self.root / "planning" / "spec.md"
            design = self.root / "planning" / "design.md"

            if spec.exists() and design.exists():
                print("✅ Planning artifacts detected")
                components = extract_components_from_design(design)
                if components:
                    order, errors = validate_and_sort(components)
                    if errors:
                        for e in errors:
                            print(f"❌ {e}")
                        return AgentRole.ARCHITECT, (
                            "Fix dependency errors in design.md:\n" +
                            "\n".join(errors)
                        )
                    print(f"📋 Implementation order: {' → '.join(order)}")
                    # Reorder components
                    comp_map = {c["name"]: c for c in components}
                    self.state["components"] = [comp_map[n] for n in order]

                self.state["phase"] = Phase.IMPLEMENTATION
                self.save()
                return self.get_next_task()

            return AgentRole.ARCHITECT, (
                "Review the user request. Create:\n"
                "1. planning/spec.md — User stories, acceptance criteria\n"
                "2. planning/design.md — Architecture, components, dependencies\n"
                "3. planning/dependencies.mermaid — Dependency graph\n\n"
                "Signal: PLANNING COMPLETE"
            )

        # ── IMPLEMENTATION ──
        elif phase == Phase.IMPLEMENTATION:
            current = self.state.get("current_component")
            components = self.state.get("components", [])

            if not current:
                remaining = [
                    c for c in components
                    if c["status"] in (ComponentStatus.PENDING, ComponentStatus.ROLLED_BACK)
                ]
                if not remaining:
                    self.state["phase"] = Phase.INTEGRATION
                    self.save()
                    return self.get_next_task()

                next_comp = remaining[0]
                next_comp["status"] = ComponentStatus.IN_PROGRESS
                next_comp["started_at"] = datetime.now().isoformat()
                next_comp["attempts"] = (next_comp.get("attempts") or 0) + 1
                self.state["current_component"] = next_comp["name"]
                self.save()

                done = sum(1 for c in components if c["status"] == ComponentStatus.QA_PASSED)
                print(f"🎯 Component: {next_comp['name']} ({done + 1}/{len(components)})")

                return AgentRole.DEVELOPER, (
                    f"Implement component: {next_comp['name']}\n"
                    f"Description: {next_comp.get('description', 'See design.md')}\n"
                    f"Size: {next_comp.get('size', 'M')}\n"
                    f"Dependencies: {', '.join(next_comp.get('dependencies', [])) or 'none'}\n"
                    f"Refer to planning/spec.md and planning/design.md.\n"
                    f"If security/security-requirements.md exists, read it for "
                    f"constraints — but do NOT read security/security-findings.json."
                )

            # Component in progress — check last action
            last = self.state["history"][-1]["role"] if self.state["history"] else None
            comp = next((c for c in components if c["name"] == current), None)

            # ── Developer done → route to Threat-Modeler or QA ──
            if last == AgentRole.DEVELOPER:
                if self._should_run_security(current):
                    comp["security_status"] = "pending"
                    self.save()
                    return AgentRole.THREAT_MODELER, (
                        f"SECURITY REVIEW for component: {current}\n\n"
                        f"Analyze the implementation in src/ for security invariants.\n"
                        f"Produce ONLY:\n"
                        f"  1. security/security-requirements.md (invariant assertions)\n"
                        f"  2. security/security-findings.json (structured findings)\n\n"
                        f"CONSTRAINTS:\n"
                        f"- Express risks ONLY as violated invariants\n"
                        f"- Do NOT describe attacker actions or sequences\n"
                        f"- Do NOT use procedural or narrative language\n\n"
                        f"Signal: SECURITY REVIEW COMPLETE: {current}"
                    )
                else:
                    # Security skipped — go straight to QA
                    return AgentRole.QA_CRITIC, (
                        f"Test component: {current}\n"
                        f"Write: tests/test_{current.replace('-', '_')}.py\n"
                        f"Execute with coverage.\n"
                        f"Report: QA RESULT: PASS or QA RESULT: FAIL — [reason]"
                    )

            # ── Threat-Modeler done → route to Security-Gatekeeper ──
            elif last == AgentRole.THREAT_MODELER:
                comp["security_status"] = "modeled"
                self.save()

                # Check artifacts exist
                sec_dir = self.root / "security"
                reqs = sec_dir / "security-requirements.md"
                findings = sec_dir / "security-findings.json"

                missing = []
                if not reqs.exists():
                    missing.append("security/security-requirements.md")
                if not findings.exists():
                    missing.append("security/security-findings.json")

                if missing:
                    return AgentRole.THREAT_MODELER, (
                        f"MISSING ARTIFACTS for {current}:\n"
                        + "\n".join(f"  - {m}" for m in missing) + "\n\n"
                        f"Create the missing artifacts and signal again.\n"
                        f"Signal: SECURITY REVIEW COMPLETE: {current}"
                    )

                return AgentRole.SECURITY_GATEKEEPER, (
                    f"SANITIZE security artifacts for component: {current}\n\n"
                    f"Validate:\n"
                    f"  1. security/security-requirements.md — invariants only, no narratives\n"
                    f"  2. security/security-findings.json — schema-valid, no procedural language\n\n"
                    f"REJECT if artifacts contain:\n"
                    f"- Attacker narratives or causal chains\n"
                    f"- Procedural/stepwise descriptions\n"
                    f"- Disallowed terms (see denied patterns list)\n\n"
                    f"If valid: rewrite sanitized versions in-place.\n"
                    f"Produce test specifications for QA-Critic (constraint assertions only).\n"
                    f"Signal: SECURITY GATE PASSED: {current}\n"
                    f"If invalid: SECURITY GATE FAILED: {current} — [reasons]"
                )

            # ── Security-Gatekeeper done → validate then route to QA ──
            elif last == AgentRole.SECURITY_GATEKEEPER:
                sec_valid, sec_violations = validate_security_artifacts(
                    self.root, self.config
                )

                if not sec_valid:
                    comp["security_gate_attempts"] = comp.get("security_gate_attempts", 0) + 1
                    comp["security_last_gate_result"] = "fail"
                    self.save()

                    attempts = comp["security_gate_attempts"]
                    print(f"  🚨 SECURITY GATE FAILED for {current} (attempt {attempts})")
                    for v in sec_violations:
                        print(v)

                    if attempts >= self.config.max_security_gate_attempts:
                        # Escalate back to Threat-Modeler for full rewrite
                        comp["security_status"] = "pending"
                        self.save()
                        return AgentRole.THREAT_MODELER, (
                            f"SECURITY GATE ESCALATION: {current}\n\n"
                            f"Gatekeeper rejected artifacts {attempts}× with:\n"
                            + "\n".join(sec_violations) + "\n\n"
                            f"Rewrite ALL security artifacts from scratch.\n"
                            f"Use ONLY invariant assertions.\n"
                            f"Signal: SECURITY REVIEW COMPLETE: {current}"
                        )

                    return AgentRole.SECURITY_GATEKEEPER, (
                        f"SECURITY GATE FAILURE: {current} (attempt {attempts})\n\n"
                        f"Violations found:\n"
                        + "\n".join(sec_violations) + "\n\n"
                        f"Sanitize the artifacts: remove all prohibited content.\n"
                        f"Rewrite as invariant assertions.\n"
                        f"Signal: SECURITY GATE PASSED: {current}"
                    )

                # Gate passed
                comp["security_status"] = "gated"
                comp["security_last_gate_result"] = "pass"
                self.save()
                print(f"  🔒 Security gate PASSED for {current}")

                return AgentRole.QA_CRITIC, (
                    f"Test component: {current}\n"
                    f"Write: tests/test_{current.replace('-', '_')}.py\n"
                    f"Write: tests/test_{current.replace('-', '_')}_security.py "
                    f"(constraint tests from sanitized security specs)\n"
                    f"Execute with coverage.\n"
                    f"Report: QA RESULT: PASS or QA RESULT: FAIL — [reason]"
                )

            # ── QA-Critic done → pass/fail routing ──
            elif last == AgentRole.QA_CRITIC:
                test_file = f"tests/test_{current.replace('-', '_')}.py"
                result = run_tests_streaming(test_file, current, self.config)

                if result["passed"]:
                    print(f"  ✅ {current} PASSED")
                    comp["status"] = ComponentStatus.QA_PASSED
                    comp["completed_at"] = datetime.now().isoformat()
                    self.state["current_component"] = None
                    self.save()
                    return self.get_next_task()
                else:
                    attempts = comp.get("attempts", 1)
                    self.state["quality_metrics"]["qa_failures_total"] += 1

                    if attempts >= self.config.max_component_attempts:
                        print(f"  🚨 ESCALATION: {current} failed {attempts}× — design review")
                        return AgentRole.ARCHITECT, (
                            f"DESIGN REVIEW: {current} failed QA {attempts} times.\n"
                            f"Last error:\n{result['output'][:500]}\n\n"
                            f"Analyze failure patterns. Update design.md with:\n"
                            f"- Root cause analysis\n"
                            f"- Revised approach\n"
                            f"- ## Revision History entry"
                        )

                    print(f"  ❌ {current} FAILED (attempt {attempts})")
                    comp["attempts"] = attempts + 1
                    self.save()
                    return AgentRole.DEVELOPER, (
                        f"Fix component: {current} (attempt {attempts + 1})\n"
                        f"Test output:\n{result['output'][:500]}\n"
                        f"Fix the root cause, not just the symptom."
                    )

            return AgentRole.DEVELOPER, f"Implement component: {current}"

        # ── INTEGRATION ──
        elif phase == Phase.INTEGRATION:
            self.state["phase"] = Phase.DOCUMENTATION
            self.save()
            return self.get_next_task()

        # ── DOCUMENTATION ──
        elif phase == Phase.DOCUMENTATION:
            if (self.root / "README.md").exists():
                self.state["phase"] = Phase.COMPLETE
                self.save()
                return None, "PROJECT COMPLETE"

            completed = [
                c["name"] for c in self.state.get("components", [])
                if c["status"] == ComponentStatus.QA_PASSED
            ]
            return AgentRole.WRITER, (
                "Generate documentation:\n"
                "1. README.md — Installation, usage, examples\n"
                "2. docs/ARCHITECTURE.md — System overview\n"
                "3. Verify all docstrings\n"
                f"Completed components: {', '.join(completed)}\n"
                "Signal: DOCUMENTATION COMPLETE"
            )

        return None, "PROJECT COMPLETE"

    def run_turn(self) -> Optional[AgentRole]:
        """Execute one turn of the state machine."""
        role, instructions = self.get_next_task()
        if role is None:
            print(f"\n🎉 {instructions}")
            return None

        persona = self.personas.get(role, "You are a helpful AI assistant.")

        print(f"\n{'═' * 60}")
        print(f"🤖 AGENT: {role.value.upper()}")
        print(f"{'═' * 60}")
        print(f"📋 TASK:\n{instructions}")
        print(f"{'═' * 60}")

        if self.config.dry_run:
            print(f"  🔍 DRY RUN — would execute {role.value}")
        else:
            input("\nPress Enter when agent has completed this task...")

        self.state["history"].append({
            "role": role,
            "task": instructions[:100],
            "timestamp": datetime.now().isoformat(),
        })
        self.save()
        return role


# ─── CLI ─────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        project_name = input("📝 Project name: ").strip() or "unknown"
    elif sys.argv[1] == "--reset":
        Path(STATE_FILE).unlink(missing_ok=True)
        Path(LOCK_FILE).unlink(missing_ok=True)
        print("🔄 State reset.")
        return
    elif sys.argv[1] == "status":
        show_status(Path.cwd())
        return
    elif sys.argv[1] == "rollback" and len(sys.argv) > 2:
        rollback_component(Path.cwd(), sys.argv[2])
        return
    elif sys.argv[1] == "--dry-run":
        project_name = sys.argv[2] if len(sys.argv) > 2 else "dry-run"
        orch = Orchestrator(project_name)
        orch.config.dry_run = True
        while orch.run_turn() is not None:
            pass
        return
    else:
        project_name = sys.argv[1]

    orch = Orchestrator(project_name)
    ensure_git(orch.root, orch.config.git_default_branch)

    while True:
        result = orch.run_turn()
        if result is None:
            break
        cont = input("\n▶ Continue? (y/n/quit): ").strip().lower()
        if cont in ("n", "q", "quit"):
            print("⏸️  Paused. Run again to resume.")
            break


if __name__ == "__main__":
    main()
