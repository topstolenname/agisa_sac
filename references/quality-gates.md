# Quality Gates & QA Details

Extended documentation for quality assurance, testing requirements, escalation
rules, and metrics tracking. The SKILL.md provides the gate summary; this file
has the implementation details.

## Table of Contents

1. [Escalation Rules](#escalation-rules)
2. [Testing Taxonomy (Extended)](#testing-taxonomy-extended)
3. [Coverage Enforcement](#coverage-enforcement)
4. [Progressive QA Feedback](#progressive-qa-feedback)
5. [Failure Analysis Protocol](#failure-analysis-protocol)
6. [Component Time Tracking](#component-time-tracking)
7. [Security Artifact Hygiene Gate](#security-artifact-hygiene-gate)
8. [Metrics & Dashboard](#metrics--dashboard)

---

## Escalation Rules

The escalation ladder is designed around the principle that **persistent bugs
are usually design bugs** — not just code bugs.

| Condition | Action | Rationale |
|-----------|--------|-----------|
| QA failure (1–2×) | Developer iterates with QA feedback | Normal — minor bugs, edge cases |
| QA failure (3×) | **Mandatory** Architect-PM design review | Pattern suggests design flaw |
| QA failure (4×+) | Stop, redesign, or split component | Component scope is wrong |
| Coverage < configured minimum | QA failure, require improvement | Untested code is untrusted |
| Type errors > 0 | QA failure, must fix | Type safety is non-negotiable |
| Security issues found | QA failure, must fix | Security is never deferred |
| Flaky test detected | Quarantine test, investigate | Flaky tests erode trust |

### Design Review Protocol

When the Architect-PM is re-engaged after 3 failures:

1. Analyze the QA failure reports — look for patterns
2. Determine root cause category:
   - Component scope too broad → split it
   - Interface mismatch → revise contracts
   - Missing dependency → add component
   - Wrong abstraction → redesign
3. Update `planning/design.md` with:
   - `## Revision History` section
   - What changed and why
   - Impact on other components
4. Reset the component's attempt counter
5. Resume implementation with revised design

---

## Testing Taxonomy (Extended)

### Unit Tests (Required)

Test each public function in isolation. Mock dependencies.

```python
def test_create_task_with_valid_input():
    """Core happy path — task is created and returned."""
    db = MockDatabase()
    result = create_task(db, "Buy groceries", priority=1)
    assert result.title == "Buy groceries"
    assert result.priority == 1
    assert result.id is not None
```

### Edge Cases (Required)

Boundary values, empty inputs, maximum sizes, type coercion.

```python
def test_create_task_empty_title():
    """Empty string should raise ValueError, not create empty task."""
    with pytest.raises(ValueError, match="title cannot be empty"):
        create_task(db, "", priority=1)

def test_priority_boundary_values():
    """Priority must be 1-5. Test boundaries."""
    create_task(db, "Test", priority=1)   # OK
    create_task(db, "Test", priority=5)   # OK
    with pytest.raises(ValueError):
        create_task(db, "Test", priority=0)  # Below range
    with pytest.raises(ValueError):
        create_task(db, "Test", priority=6)  # Above range
```

### Error Paths (Required)

Test that errors produce meaningful messages, not stack traces.

```python
def test_database_connection_failure():
    """Database unavailable should raise clear error, not sqlite3.OperationalError."""
    db = FailingDatabase()
    with pytest.raises(DatabaseError, match="Could not connect"):
        create_task(db, "Test", priority=1)
```

### Integration Tests (Required for multi-component)

Test component interfaces — data flows correctly between boundaries.

```python
def test_cli_to_database_flow():
    """CLI 'add' command should persist task to database."""
    runner = CliRunner()
    result = runner.invoke(cli, ["add", "Buy groceries"])
    assert result.exit_code == 0

    # Verify persistence
    db = Database("test.db")
    tasks = db.list_tasks()
    assert len(tasks) == 1
    assert tasks[0].title == "Buy groceries"
```

### Property Tests (Recommended)

Test invariants that should hold for any input.

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=200))
def test_task_roundtrip(title):
    """Any valid title should survive create → read cycle unchanged."""
    task = create_task(db, title, priority=1)
    retrieved = get_task(db, task.id)
    assert retrieved.title == title
```

### Performance Tests (Recommended)

Basic benchmarks to catch regressions.

```python
def test_list_1000_tasks(benchmark_db):
    """Listing 1000 tasks should complete in <100ms."""
    import time
    start = time.time()
    tasks = benchmark_db.list_tasks()
    elapsed = time.time() - start
    assert len(tasks) == 1000
    assert elapsed < 0.1
```

### Security Tests (Required for user-facing)

Constraint verification — assert invariant preservation, never describe exploits.

```python
def test_parameterized_queries_enforced():
    """All database queries MUST use parameterized inputs."""
    malicious = "'; DROP TABLE tasks; --"
    create_task(db, malicious, priority=1)
    # Table must still exist — invariant preserved
    tasks = db.list_tasks()
    assert isinstance(tasks, list)

def test_rejects_unauthenticated_request():
    """Unauthenticated requests MUST be rejected at the boundary."""
    response = client.get("/api/tasks", headers={})
    assert response.status_code == 401

def test_input_schema_validation():
    """External input MUST be schema-validated before processing."""
    invalid_payload = {"title": 123, "priority": "not_a_number"}
    response = client.post("/api/tasks", json=invalid_payload)
    assert response.status_code == 422
```

---

## Coverage Enforcement

### Thresholds

The minimum coverage is configurable in `.dev-team-config.yml`:

```yaml
min_coverage: 80.0  # Default
```

### Measurement

```bash
# Per-component coverage
pytest tests/test_database_layer.py \
    --cov=src/database_layer \
    --cov-report=term-missing \
    --cov-report=json:coverage.json \
    -v

# Full project coverage
pytest --cov=src --cov-report=html
```

### What Counts

- **Line coverage:** Every executable line is reached
- **Branch coverage:** Every `if/else/try/except` branch is tested
- **Critical path coverage:** Error handling, auth, data mutation = 100%

### What Doesn't Count

- Configuration files
- `__init__.py` (unless it contains logic)
- Generated code
- Test files themselves

---

## Progressive QA Feedback

Long test runs should stream output in real-time so the developer sees
progress rather than staring at a blank terminal.

### Implementation

```python
import subprocess
import sys

def run_tests_with_streaming(test_file: str, component: str) -> dict:
    """Execute tests with real-time output."""
    cmd = [
        "python", "-m", "pytest", test_file, "-v",
        "--cov", f"src/{component}",
        "--cov-report", "term-missing"
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1  # Line-buffered
    )

    output_lines = []
    print(f"🧪 Running tests for {component}...")

    for line in proc.stdout:
        sys.stdout.write(f"    {line}")
        sys.stdout.flush()
        output_lines.append(line)

    proc.wait()

    return {
        "exit_code": proc.returncode,
        "output": "".join(output_lines[-100:]),  # Last 100 lines
        "passed": proc.returncode == 0
    }
```

### Output Format

During execution:
```
🧪 Running tests for database-layer...
    tests/test_database_layer.py::test_create_task PASSED
    tests/test_database_layer.py::test_empty_title PASSED
    tests/test_database_layer.py::test_sql_injection PASSED
    tests/test_database_layer.py::test_concurrent_access FAILED

    =================== FAILURES ===================
    ...
```

---

## Failure Analysis Protocol

When QA fails, structured reporting helps the Developer fix issues efficiently.

### Report Template

```markdown
## QA RESULT: FAIL — <component_name>

### Summary
- Tests run: 12
- Passed: 10
- Failed: 2
- Coverage: 76% (below 80% threshold)

### Failures
1. `test_concurrent_write` — sqlite3.OperationalError: database is locked
   - Expected: Graceful retry or queue
   - Got: Unhandled exception
   - Root cause: No connection pooling or write serialization

2. `test_large_dataset` — AssertionError: elapsed 2.3s > 0.1s threshold
   - Expected: <100ms for 1000 records
   - Got: 2.3 seconds
   - Root cause: N+1 query pattern in list_tasks()

### Root Cause Analysis
Both failures stem from the database access pattern — direct sqlite3
connections without pooling or query optimization. This is a code-level
issue, not a design issue.

### Recommendation
1. Add connection pooling (e.g., `sqlite3` with `check_same_thread=False`)
2. Replace N+1 query with single `SELECT` with `JOIN`
3. Add `threading.Lock` for write serialization

### Design Escalation?
NO — Failures are implementation-level, not design-level.
```

---

## Component Time Tracking

Track estimated vs actual time per component to improve future planning.

### Data Model

```python
@dataclass
class Component:
    name: str
    dependencies: List[str]
    size: str  # XS/S/M/L/XL
    status: str  # pending/in_progress/qa_passed/failed/rolled_back
    estimated_minutes: int  # Derived from size
    actual_minutes: Optional[float] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    attempts: int = 0
```

### Size-to-Time Estimates

| Size | Default Estimate |
|------|-----------------|
| XS | 10 min |
| S | 20 min |
| M | 30 min |
| L | 60 min |
| XL | 120 min |

### Tracking

```python
# At component start
comp.started_at = datetime.now().isoformat()

# At component completion
comp.completed_at = datetime.now().isoformat()
comp.actual_minutes = (
    datetime.fromisoformat(comp.completed_at)
    - datetime.fromisoformat(comp.started_at)
).total_seconds() / 60
```

---

## Security Artifact Hygiene Gate

All persistent security artifacts (`security/security-requirements.md`,
`security/security-findings.json`) MUST pass hygiene validation before
any downstream agent can consume them.

### Prohibited Content

Persistent artifacts MUST NOT contain:
- Attacker narratives (stories describing what an attacker would do)
- Procedural steps (step-by-step descriptions of how to exploit)
- Hypothetical harm scenarios (even framed as "risks")
- Metaphorical or allegorical representations of forbidden actions
- Causal chains linking actions to exploits

Violation results in **immediate gate failure**. The Security-Gatekeeper
must reject and request revision from the Threat-Modeler.

### Enforcement

The orchestrator validates `security/security-findings.json` against a
deny-list of terms and phrase patterns before allowing QA to proceed.
This is a simple regex + keyword check — no NLP required — because the
artifact format is already constrained.

### Denied Terms (Baseline)

```python
DENIED_PATTERNS = [
    r"\battacker\b", r"\badversary\b", r"\bexploit\b",
    r"\bhack\b", r"\bbreach\b", r"\bbypass\b",
    r"\binjection attack\b", r"\bescalat\w+\b",
    r"step\s*\d", r"first.*then.*finally",
    r"\bif an attacker\b", r"\ba malicious\b",
]
```

Projects may extend this list in `.dev-team-config.yml`:

```yaml
security_denied_patterns:
  - "\\bpayload\\b"
  - "\\bshellcode\\b"
```

### Acceptable Alternatives

Instead of narrative language, use invariant language:

| ❌ Prohibited | ✅ Required |
|--------------|------------|
| "An attacker could inject SQL..." | "Input MUST be parameterized" |
| "If a user bypasses auth..." | "Unauthenticated requests MUST be rejected" |
| "Step 1: Craft a malicious payload..." | "External input MUST be schema-validated" |
| "The adversary escalates privileges..." | "Role boundaries MUST be enforced at every endpoint" |

---

## Metrics & Dashboard

### Tracked Metrics

- Test coverage trend (must not decrease between components)
- Build time (flag if >10 min)
- Test execution time (flag if >2 min)
- QA iteration count per component (escalate if >3)
- Code churn (flag if component rewritten >2×)
- Component completion time (estimated vs actual)

### Dashboard Format

```
╔════════════════════════════════════════════════╗
║   DEV TEAM ORCHESTRATION STATUS                ║
╠════════════════════════════════════════════════╣
║ Project: task-api                              ║
║ Phase:   implementation (3/5 components)       ║
║ Progress: ████████████░░░░░░░░ 60%             ║
╠════════════════════════════════════════════════╣
║ Components:                                    ║
║   ✅ database-layer      (12.3m, 92% cov)     ║
║   ✅ business-logic      (8.7m, 88% cov)      ║
║   🔧 api-layer           (5.2m elapsed)       ║
║   ⏳ auth-middleware                           ║
║   ⏳ cli-client                               ║
╠════════════════════════════════════════════════╣
║ Quality:                                       ║
║   Tests: 47 passing | Coverage: 89.2%          ║
║   QA Failures: 3 total, 0 current             ║
║   Commits: 8                                   ║
╚════════════════════════════════════════════════╝
```

### Alert Thresholds

```
⚠️  Coverage dropped: 89.2% → 76.1% (component: api-layer)
🚨 Escalation: 3 QA failures on auth-middleware — design review required
⏱️  Slow tests: api-layer tests took 4.7 minutes
```
