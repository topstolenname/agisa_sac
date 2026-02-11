---
name: dev-orchestration
description: Coordinate a team of AI agents (Architect-PM, Developer, QA-Critic, Tech-Writer) to build complex software projects iteratively. Use when the user says "build me a [project]", "implement [feature] using the dev team approach", "create a [system] with proper testing and documentation", or requests a multi-component system that needs planning, implementation, testing, and documentation. Prevents "codebase drift" through component-level iteration with QA feedback loops.
---

# Dev Team Orchestration Skill

Transform complex software requests into production-ready code through coordinated multi-agent development.

## Overview

This skill orchestrates a **4-agent development team** that builds software iteratively:

1. **Architect-PM** - Requirements gathering and system design
2. **Developer** - Component implementation
3. **QA-Critic** - Testing and quality assurance
4. **Tech-Writer** - Documentation and usability

The key innovation is **component-level iteration** with tight QA feedback loops, preventing the "500 lines of broken code" problem common in AI-generated projects.

## When to Use

Trigger this skill for:
- **Multi-component projects**: "Build me a Python CLI for managing TODOs with SQLite"
- **Quality-critical systems**: "Create a web API with full test coverage"
- **Production-ready code**: "Implement a data pipeline with proper error handling and docs"
- **Team-style development**: "Use the dev team approach to build this"

**Do NOT use for:**
- Simple scripts (<100 lines, single file)
- Quick prototypes without testing requirements
- Exploratory coding or experiments

## Core Workflow

```
┌─────────────────────┐
│  PLANNING PHASE     │  Architect-PM creates spec.md, design.md
└──────────┬──────────┘
           ↓
┌─────────────────────────────────────┐
│  IMPLEMENTATION PHASE (per component)│
│  ┌──────────────┐                   │
│  │  Developer   │ Implement         │
│  └───────┬──────┘                   │
│          ↓                           │
│  ┌──────────────┐                   │
│  │  QA-Critic   │ Test              │
│  └───────┬──────┘                   │
│          ↓                           │
│     PASS? ──NO──→ Back to Developer │
│          │                           │
│         YES                          │
│          ↓                           │
│   Next component?                    │
└──────────┬──────────────────────────┘
           ↓
┌─────────────────────┐
│ DOCUMENTATION PHASE │  Tech-Writer creates README
└─────────────────────┘
```

## How to Use

### Option 1: Manual Orchestration (Recommended for Learning)

Run the orchestrator script manually and interact with each agent:

```bash
cd your-project-directory
python /path/to/.skills/dev-orchestration/scripts/orchestrator.py "my-project"
```

The script will:
1. Load or create `.dev-team-state.json` (persistent state)
2. Determine which agent should work next
3. Display the agent's system prompt and task
4. Wait for you to complete the task
5. Advance to the next agent

**Example session:**
```
📝 Project name: todo-cli

====================================================
🤖 AGENT: ARCHITECT-PM
====================================================
📋 TASK:
Review the user request. Create:
1. spec.md - User stories, acceptance criteria
2. design.md - Architecture, component list
3. schema.sql (if database needed)
====================================================

[You create the planning documents]
Press Enter when agent has completed this task...

====================================================
🤖 AGENT: DEVELOPER
====================================================
📋 TASK:
Implement component: database-layer
Refer to spec.md and design.md for requirements.
====================================================

[You implement the component]
Press Enter when agent has completed this task...

====================================================
🤖 AGENT: QA-CRITIC
====================================================
📋 TASK:
Test component: database-layer
1. Write test file: tests/test_database-layer.py
2. Execute tests using pytest
3. Analyze results
====================================================

[Tests run automatically if pytest is installed]
✅ database-layer PASSED quality checks

▶ Continue to next agent? (y/n/quit):
```

### Option 2: Automated Integration (For Production Use)

Integrate with your local LLM by modifying `orchestrator.py`:

```python
# In run_turn() method, replace the manual input:
response = call_your_llm(
    system_prompt=system_prompt,
    user_prompt=instructions,
    model="qwen2.5:7b"  # or your preferred model
)
```

This enables fully autonomous multi-agent development.

## Agent Roles & Responsibilities

### Architect-PM
**Files Created:** `spec.md`, `design.md`, optionally `schema.sql`

**Responsibilities:**
- Clarify ambiguous requirements with questions
- Write user stories and acceptance criteria
- Design system architecture and component breakdown
- Define database schemas if needed

**Success Criteria:**
- `design.md` contains a "## Components" section listing 3-7 components
- Each component has clear responsibilities
- Dependencies between components are documented

### Developer
**Files Modified/Created:** Source code files (`.py`, `.js`, etc.)

**Responsibilities:**
- Implement ONE component at a time
- Write clean, testable code with docstrings
- Follow specifications from `spec.md` and `design.md`
- Focus on correctness, not perfection

**Success Criteria:**
- Code runs without syntax errors
- Component implements required functionality
- Code is well-structured for testing

### QA-Critic
**Files Created:** Test files (`tests/test_*.py`)

**Responsibilities:**
- Write comprehensive tests for each component
- Test happy paths, edge cases, and error conditions
- Execute tests and analyze failures
- Report failures with actionable details

**Success Criteria:**
- Test file exists with multiple test cases
- Tests cover core functionality and edge cases
- All tests pass, or failures are clearly reported

### Tech-Writer
**Files Created/Modified:** `README.md`, docstrings in source files

**Responsibilities:**
- Create comprehensive README with installation and usage
- Ensure all functions have docstrings
- Write code examples that work
- Document project structure

**Success Criteria:**
- README includes installation, usage examples, and project structure
- All public functions have docstrings
- Documentation is clear and copy-pasteable

## State Management

The orchestrator maintains `.dev-team-state.json`:

```json
{
  "project_name": "todo-cli",
  "phase": "implementation",
  "current_component": "cli-interface",
  "completed_components": ["database-layer"],
  "qa_failures": 1,
  "discovered_components": ["database-layer", "cli-interface", "integration"],
  "history": [
    {"role": "architect-pm", "task": "Create planning documents"},
    {"role": "developer", "task": "Implement database-layer"},
    {"role": "qa-critic", "task": "Test database-layer"}
  ]
}
```

**Recovery:** If the process crashes or is interrupted, simply run the orchestrator again. It will resume from the last saved state.

**Reset:** To start over: `python orchestrator.py --reset`

## Advanced Features

### Auto-Component Discovery

The orchestrator can parse `design.md` to automatically extract the component list:

```markdown
## Components

1. **database-layer** - SQLite operations and schema management
2. **cli-interface** - Argument parsing and command handling  
3. **integration** - Glue code connecting components
```

Components are then processed in order automatically.

### Automatic QA Result Detection

If `pytest` is installed, the orchestrator automatically runs tests and detects pass/fail:

```python
# In orchestrator.py
status, error = self.check_test_result(component)
if status == "PASS":
    # Advance to next component
elif status == "FAIL":
    # Kick back to developer with error details
```

### Iteration Tracking

The orchestrator tracks how many times a component has failed QA:

```python
self.state["qa_failures"] += 1

# After 3 failures, suggest redesigning the component
if self.state["qa_failures"] > 3:
    print("⚠️  Component has failed 3+ times. Consider:")
    print("   1. Breaking into smaller sub-components")
    print("   2. Revisiting the design")
    print("   3. Re-engaging Architect-PM")
```

## Project Templates

Pre-built templates for common project types:

### Python CLI Template
```bash
cp -r assets/templates/python-cli/ ./my-cli-project/
```

Includes:
- `src/` directory with CLI, core logic, and utilities
- `tests/` directory with test templates
- `setup.py` for packaging
- `requirements.txt` with common dependencies

### Python Library Template
```bash
cp -r assets/templates/python-lib/ ./my-library/
```

Includes:
- Public API structure
- Test suite
- Documentation templates

### Web App Template  
```bash
cp -r assets/templates/web-app/ ./my-web-app/
```

Includes:
- MVC structure
- Route handlers
- Template system

## Workflow Customization

Different project types require different workflows. See `references/workflow-patterns.md` for:

- CLI Tool Pattern (3-5 components)
- Library/Package Pattern (4-8 components)
- Web Application Pattern (5-10 components)
- Data Pipeline Pattern (4-7 components)

Each pattern includes:
- Typical component breakdown
- Testing focus areas
- Special considerations

## Best Practices

### Component Sizing
- **Too small** (<50 lines): Consider merging related components
- **Good size** (50-300 lines): Easy to test, single responsibility
- **Too large** (>500 lines): Split into sub-components

### QA Iteration Limits
- **1-2 iterations**: Normal - minor bugs, edge cases
- **3 iterations**: Warning - may indicate design issues
- **4+ iterations**: Stop - redesign component or split into smaller pieces

### Agent Handoff Protocol
Each agent should clearly signal completion:
- Architect-PM: "PLANNING COMPLETE"
- Developer: "Implementation complete for [component]"
- QA-Critic: "QA RESULT: PASS" or "QA RESULT: FAIL - [reason]"
- Tech-Writer: "DOCUMENTATION COMPLETE"

## Troubleshooting

### "Component keeps failing QA"
**Solution:** 
1. Review the test failures carefully
2. Check if component scope is too large
3. Consider splitting into sub-components
4. Re-engage Architect-PM if design is flawed

### "Orchestrator asks for manual component selection"
**Solution:**
- Ensure `design.md` has a "## Components" section
- List components as numbered or bulleted items
- Or manually input component names when prompted

### "Tests don't auto-run"
**Solution:**
- Install pytest: `pip install pytest`
- Ensure test files follow naming: `tests/test_*.py`
- Check that test file paths match component names

## Integration Examples

### With Open Interpreter
```python
from interpreter import interpreter

# In orchestrator.py run_turn()
interpreter.system_message = system_prompt
result = interpreter.chat(instructions)
```

### With Ollama
```python
import ollama

response = ollama.chat(
    model='qwen2.5:7b',
    messages=[
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': instructions}
    ]
)
```

### With OpenAI-Compatible API
```python
import openai

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instructions}
    ]
)
```

## References

- **Agent Personas:** See `references/agent-personas.md` for detailed system prompts
- **Workflow Patterns:** See `references/workflow-patterns.md` for project type guides
- **Templates:** See `assets/templates/` for starter projects

## Credits

Architecture inspired by Claude's Agent Skills pattern with progressive disclosure and stateful orchestration for long-running development workflows.
