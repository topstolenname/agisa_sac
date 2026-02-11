---
name: dev-orchestration
description: >
  Coordinate a team of six AI agents (Architect-PM, Developer, Threat-Modeler,
  Security-Gatekeeper, QA-Critic, Tech-Writer) to build complex software projects
  iteratively with enforced security gates. Prevents codebase drift through
  component-level iteration with QA feedback loops and one-way security
  abstraction barriers. Use this skill whenever the user asks to "build",
  "create", or "implement" a multi-component system, mentions "proper testing",
  "production-ready", "dev team approach", or needs a project with planning,
  implementation, testing, AND documentation. Even if the user just says
  "build me a [thing]" without specifying quality — if the project sounds like it
  needs multiple files, use this skill. Trigger aggressively for any non-trivial
  software project request.
---

# Dev Team Orchestration

Build production-ready software through coordinated multi-agent development with
enforced quality gates. The core idea: implement one component at a time, test it
adversarially, commit on pass, iterate on fail. This prevents the "500 lines of
broken code" problem and makes failures explicit and recoverable.

## When to Use

Use this skill for:
- Multi-component projects ("Build me a CLI task manager with SQLite")
- Quality-critical systems ("Create an API with full test coverage")
- Production-ready code ("Implement a pipeline with proper error handling and docs")
- Any request mentioning testing, documentation, structure, or quality
- Projects requiring >100 LOC or multiple files

Skip this skill for single-file scripts under 100 lines, throwaway prototypes,
exploratory coding, or simple bug fixes.

## Agents

Six agents rotate through the workflow, each with a single responsibility:

| Agent | Role | Key Output |
|-------|------|------------|
| **Architect-PM** | Requirements + system design | `planning/spec.md`, `planning/design.md` |
| **Developer** | Implement ONE component per turn | Source files in `src/` |
| **Threat-Modeler** | Security architecture & risk classification | `security/security-requirements.md` |
| **Security-Gatekeeper** | Sanitization & abstraction enforcement | Sanitized findings only |
| **QA-Critic** | Constraint-based testing | Test files in `tests/`, coverage report |
| **Tech-Writer** | Documentation + examples | `README.md`, `docs/`, docstrings |

For detailed agent personas, protocols, and completion signals, read
`references/agent-personas.md`.

## Security Track (Mandatory for Production)

The Security Track introduces constrained, non-procedural security analysis
agents that operate as one-way gates. These agents may reason adversarially
internally but MUST NOT emit exploit narratives, attacker strategies,
procedural descriptions, or stepwise logic.

Security outputs are constraint-based, invariant-driven, and test-enforced.

Security exists to constrain possibility, not to enumerate danger.

The security workflow inserts between Developer and QA-Critic:

```
Developer → Threat-Modeler → Security-Gatekeeper → QA-Critic
```

The Threat-Modeler identifies violated invariants and required constraints.
The Security-Gatekeeper sanitizes all findings into structured artifacts
before any downstream agent can consume them. The Developer never sees
threat models or adversarial reasoning — only security requirements and
test specifications.

For security artifact formats, see the `security/` directory structure below.
For agent constraints, read `references/agent-personas.md`.

### Concord Safety Rule — Option Space Restriction

Agents MUST generate solutions only from the approved Action Taxonomy.
Forbidden categories are excluded at generation time and MUST NOT be
produced, ranked, discussed, or referenced even hypothetically.

Forbidden categories include:
- Physical harm to humans
- Illegal wrongdoing
- Exploitation or bypass of safeguards
- Coercion or manipulation
- Unauthorized access or escalation

This is not a scoring rule. This is a generation constraint.

## Core Workflow

```
Phase 0: Setup ─── Git init, dependencies, CI scaffold
    ↓
Phase 1: Planning ─── Architect-PM creates spec + design
    ↓
    ┌── HUMAN APPROVAL GATE ──┐
    ↓                          ↓
Phase 2: Implementation ─── Per-component loop:
    │
    │   Developer implements
    │       ↓
    │   Threat-Modeler reviews (invariants only)
    │       ↓
    │   Security-Gatekeeper sanitizes (one-way gate)
    │       ↓
    │   QA-Critic tests (constraints + coverage)
    │       ↓
    │     PASS? ──→ YES → Commit, next component
    │       │
    │      NO → Iterate (3 failures → Architect-PM design review)
    ↓
Phase 3: Integration ─── System tests, security scan
    ↓
    ┌── HUMAN VALIDATION GATE ──┐
    ↓
Phase 4: Documentation ─── Tech-Writer creates docs
    ↓
    ┌── HUMAN FINAL REVIEW ──┐
    ↓
    RELEASE (git tag v1.0.0)
```

## Quality Gates

These gates prevent drift and catch design-level bugs early. Persistent test
failures usually signal a design problem, not just a code bug.

| Condition | Action |
|-----------|--------|
| QA failure (1–2×) | Iterate Developer ↔ QA-Critic |
| QA failure (3×) | **Mandatory** Architect-PM design review |
| QA failure (4×+) | Stop — redesign or split the component |
| Coverage < threshold | QA failure, require improvement |
| Type errors > 0 | QA failure, must fix |

The coverage threshold and max attempts are configurable per-project. See
`references/configuration.md` for the `.dev-team-config.yml` format.

For the full QA testing taxonomy (unit, edge case, error path, integration,
property, performance, security), coverage requirements, and failure analysis
protocol, read `references/quality-gates.md`.

## Human-in-the-Loop Gates

Four checkpoints give the human control without blocking routine work:

**Gate 1 — Design Approval** (after Planning): Review component boundaries,
dependencies, and risks before any code is written. Approve, request changes,
or cancel.

**Gate 2 — Component Review** (optional, per-component): Configurable — auto-approve
low-risk components, require review for high-risk ones like auth or payments. Set
policy in `.dev-team-config.yml`.

**Gate 3 — Integration Validation** (after all components pass): System-level tests,
performance benchmarks, security scan. Approve or send back for fixes.

**Gate 4 — Release Approval** (after documentation): README, examples, known issues.
Final sign-off before tagging the release.

## State Management

The orchestrator persists progress in `.dev-team-state.json` so work survives
interruptions. Key features:

- **Atomic writes** with backup — no data loss on crash
- **File locking** — prevents concurrent instances from corrupting state
- **Automatic resume** — re-run the orchestrator and it picks up where it left off
- **Rollback** — reset a failed component to PENDING without affecting others

For implementation details (atomic write protocol, lock mechanism, state schema,
backup/restore logic), read `references/state-and-recovery.md`.

**Quick commands:**
```bash
# Resume interrupted project
dev-orchestrator resume my-project

# Check status
dev-orchestrator status my-project

# Rollback a failed component
dev-orchestrator rollback database-layer

# Start fresh
rm .dev-team-state.json
```

## Configuration

Projects are customizable via `.dev-team-config.yml` without code changes:

```yaml
min_coverage: 80.0
max_component_attempts: 3
auto_approve_low_risk: true
low_risk_components: [config-parser, utils]
require_review_components: [authentication, payment]
git_default_branch: main
enable_security_track: true
security_skip_components: [config-parser, utils]
```

For the full configuration schema, defaults, and advanced options, read
`references/configuration.md`.

## Component Design Guidelines

Aim for 3–7 components per project, each with a single testable responsibility.

| Size | LOC | Guidance |
|------|-----|----------|
| XS | <50 | Consider merging with a neighbor |
| S | 50–150 | Ideal |
| M | 150–300 | Ideal |
| L | 300–500 | Consider splitting |
| XL | >500 | Must split |

Dependencies between components must form a DAG (no cycles). The orchestrator
validates this before implementation begins — missing or circular dependencies
are caught early with clear error messages. See `references/workflow-patterns.md`
for project-type patterns and dependency graph conventions.

## Project Output Structure

Every project follows this layout:

```
my-project/
├── .github/workflows/ci.yml    # CI pipeline
├── .dev-team-state.json         # Orchestration state (gitignored)
├── .dev-team-config.yml         # Project config
├── planning/
│   ├── spec.md                  # Requirements
│   ├── design.md                # Architecture + components
│   └── dependencies.mermaid     # Dependency graph
├── security/
│   ├── security-requirements.md # Invariants (assertions only, no narratives)
│   └── security-findings.json   # Structured findings (schema-validated)
├── src/                         # Implementation
├── tests/
│   ├── test_*.py                # Per-component tests
│   ├── test_*_security.py       # Security constraint tests
│   └── integration/             # System tests
├── docs/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   └── examples/
├── pyproject.toml
├── Dockerfile
└── LICENSE
```

## Git Workflow

Each phase and component gets its own branch:

```bash
# Planning
git checkout -b planning && git merge planning

# Per component
git checkout -b component/database-layer
# ... implement + pass QA ...
git commit -m "feat(db): implement database layer"
git checkout main && git merge component/database-layer

# Release
git tag -a v1.0.0 -m "Release v1.0.0"
```

Conventional commits are used throughout. The CI pipeline (generated automatically)
runs linting, type checking, and tests on every push.

## How to Invoke This Skill

When Claude detects a trigger (see description), it should:

1. Read this SKILL.md
2. Ask clarifying questions about requirements
3. **Phase 1 — Planning:** Switch to Architect-PM persona. Create `planning/`
   documents. Present design for human approval.
4. **Phase 2 — Implementation:** For each component in dependency order:
   - Switch to Developer persona, implement the component
   - Switch to Threat-Modeler persona, identify security invariants
   - Pass through Security-Gatekeeper to sanitize findings
   - Switch to QA-Critic persona, write and run tests (including security constraints)
   - If pass: commit and continue
   - If fail: iterate or escalate per quality gate rules
5. **Phase 3 — Integration:** Run system-level tests. Present for validation.
6. **Phase 4 — Documentation:** Switch to Tech-Writer persona. Create docs.
   Present for final approval.
7. Provide download link to the complete project.

For agent persona details, read `references/agent-personas.md`.
For project-type workflow variants, read `references/workflow-patterns.md`.

## Key Features Summary

| Feature | What It Does | Details In |
|---------|-------------|------------|
| Atomic state recovery | Crash-safe writes with backup + locking | `references/state-and-recovery.md` |
| Dependency validation | Catches missing/circular deps before implementation | `references/workflow-patterns.md` |
| Enhanced error context | Actionable suggestions on git/test failures | `references/state-and-recovery.md` |
| Progressive QA feedback | Real-time test output streaming | `references/quality-gates.md` |
| Rollback command | Reset failed component without affecting others | `references/state-and-recovery.md` |
| Configuration file | Per-project thresholds without code changes | `references/configuration.md` |
| Dry-run mode | Simulate workflow without execution | `references/configuration.md` |
| Component time tracking | Estimated vs actual duration per component | `references/quality-gates.md` |
| Security Track | Invariant-driven security with one-way abstraction barriers | `references/agent-personas.md` |
| Concord Option Restriction | Generation-time exclusion of forbidden action categories | This file (Security Track) |
| Security Artifact Hygiene | Automated lint for procedural/narrative language in findings | `references/quality-gates.md` |

## Philosophy

This skill is intentionally conservative — it optimizes for trust over speed,
maintainability over features, and quality over quantity. The overhead of quality
gates pays for itself by catching design bugs early, making failures recoverable,
and producing code that humans can actually maintain.

Security reasoning is structurally isolated: threat models never leak downstream,
developers are blind to adversarial logic, and all security enforcement occurs
through constraints and tests — never through narratives or procedural descriptions.

The transformation: from "generate code and hope" to "build systems through
explicit roles, iteration, accountability, and observable progress."

## Reference Files

Read these as needed — they contain implementation details, code examples, and
extended documentation that would bloat this file:

| File | Contents | When to Read |
|------|----------|--------------|
| `references/agent-personas.md` | Full agent system prompts, protocols, handoff signals | Before executing any agent turn |
| `references/workflow-patterns.md` | Project-type patterns, dependency validation, component discovery | During planning phase |
| `references/quality-gates.md` | QA testing taxonomy, coverage rules, failure analysis protocol | During QA turns |
| `references/state-and-recovery.md` | Atomic writes, locking, rollback, error handling code | When implementing state operations |
| `references/configuration.md` | Config schema, defaults, dry-run, time tracking, export | When customizing project settings |
| `scripts/orchestrator.py` | Runnable orchestration state machine | For standalone/automated use |
| `assets/templates/` | Starter project templates (Python CLI, lib, web) | During project scaffolding |
