## Dev Team Orchestration Skill

This directory contains an **interactive orchestrator** for coordinating a 4-agent workflow:

- **Architect-PM**: planning (`spec.md`, `design.md`, optional `schema.sql`)
- **Developer**: implement one component at a time
- **QA-Critic**: write tests and run `pytest`
- **Tech-Writer**: write `README.md`

### Usage

From inside the project you want to build:

```bash
python /path/to/.skills/dev-orchestration/scripts/orchestrator.py "my-project"
```

The orchestrator will create a `.dev-team-state.json` file in the current directory and guide you.

### Key files

- `.dev-team-state.json`: persistent state (phase, current component, history)
- `spec.md`: requirements + acceptance criteria
- `design.md`: architecture + a `## Components` list

### Helpful flags

- `--reset`: start over (recreates `.dev-team-state.json`)
- `--status`: show current phase + next agent
- `--non-interactive`: don’t block waiting for Enter
- `--no-auto-discover`: don’t parse components from `design.md`
- `--no-auto-pytest`: don’t auto-run pytest for QA turns

