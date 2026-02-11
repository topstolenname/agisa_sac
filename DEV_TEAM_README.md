# Dev Team Agents

This directory contains a multi-agent development team orchestrated by a central script.

## Structure
- `scripts/`: Contains the orchestration logic.
- `references/`: Contains agent personas, configuration docs, and quality gates.
- `dev-team`: Wrapper script to launch the team.

## Usage

To start or resume a project:

```bash
./dev-team my-new-project
```

To see available commands:

```bash
./dev-team --help
```

To check the status of a project:

```bash
./dev-team status my-new-project
```

## Configuration

You can customize the team's behavior by creating a `.dev-team-config.yml` file in your project directory. See `references/configuration.md` for details.
