# Dev Orchestration Agent for AGI-SAC

The AGI-SAC project now includes a powerful dev orchestration agent powered by Claude Agent SDK. This agent can help you manage development workflows, run tests, analyze code quality, and more.

## Features

The dev agent provides:

- **Task Planning & Tracking** - Break down complex tasks and track progress
- **Test Execution** - Run pytest or unittest test suites
- **Build Automation** - Execute build commands
- **Code Quality Analysis** - Run linters (pylint, mypy, flake8, black)
- **File Operations** - Intelligent read, write, and edit capabilities
- **Git Operations** - Manage version control workflows
- **Project Status** - Comprehensive project health reports

## Installation

The dev agent is included as part of the AGI-SAC installation. Make sure you have:

1. **Poetry installed** (for dependency management)
2. **Python 3.9+**
3. **Anthropic API key** ([get one here](https://console.anthropic.com/))

Install dependencies:

```bash
cd agisa_sac
poetry install
```

## Setup

1. **Set your API key**:

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=your-api-key-here
```

Or export it directly:

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

## Usage

The dev agent can be run in two modes:

### 1. Single Task Mode

Run a specific task and get results:

```bash
# Using the installed CLI command
poetry run agisa-dev "Run all tests and report results"

# Or directly with Python
poetry run python -m agisa_sac.dev_agent "Analyze code quality in src/"
```

### 2. Interactive Mode

Start an interactive session for continuous conversation:

```bash
poetry run agisa-dev --interactive
```

In interactive mode, you can have ongoing conversations:
```
[0] You: What files are in the src directory?
[1] Agent: [Responds with file listing]

[1] You: Run the tests for the orchestration module
[2] Agent: [Runs tests and reports results]

[2] You: Create a summary of test coverage
[3] Agent: [Analyzes and summarizes coverage]
```

### 3. Auto-Edit Mode

Allow the agent to automatically edit files without prompting:

```bash
poetry run agisa-dev --allow-edits "Refactor the base_agent module"
```

## Available Custom Tools

The dev agent has access to these specialized tools:

### execute_tests
Run your test suite with pytest or unittest

```bash
poetry run agisa-dev "Run tests in tests/unit/ with verbose output"
```

### build_project
Execute build commands

```bash
poetry run agisa-dev "Build the project and install dependencies"
```

### analyze_code_quality
Run linters and static analysis

```bash
poetry run agisa-dev "Analyze code quality in src/ using pylint and mypy"
```

### get_project_status
Get comprehensive project health report

```bash
poetry run agisa-dev "Give me a project status report"
```

## Example Workflows

### Run Full Test Suite
```bash
poetry run agisa-dev "Run all tests and create a coverage report"
```

### Code Quality Check
```bash
poetry run agisa-dev "Run pylint, mypy, and black on the entire codebase"
```

### Git Workflow
```bash
poetry run agisa-dev "Show git status and summarize uncommitted changes"
```

### Interactive Development
```bash
poetry run agisa-dev --interactive
# > "What are the main modules in this project?"
# > "Find all TODO comments in the codebase"
# > "Run the tests for the memory continuum module"
```

### Automated Refactoring
```bash
poetry run agisa-dev --allow-edits "Update all imports to use absolute paths"
```

## Configuration

The dev agent is configured in `src/agisa_sac/dev_agent.py`. You can customize:

- **Model**: Change the Claude model (default: claude-sonnet-4-5-20251101)
- **Tools**: Add/remove available tools
- **System Prompt**: Modify agent behavior and personality
- **Permission Mode**: Control file edit permissions

## Integration with AGI-SAC

The dev agent integrates seamlessly with the existing AGI-SAC tooling:

- Uses the same Poetry environment
- Respects project structure and conventions
- Can analyze AGI-SAC specific code (agents, orchestration, topology analysis)
- Works alongside existing CLI commands (agisa-sac, agisa-federation, agisa-chaos)

## Troubleshooting

### API Key Issues
```bash
# Verify your key is set
echo $ANTHROPIC_API_KEY

# Or check .env file
cat .env
```

### Poetry Issues
```bash
# Reinstall dependencies
poetry install --no-cache

# Update dependencies
poetry update
```

### Import Errors
```bash
# Make sure you're using poetry run
poetry run agisa-dev "your task"

# Or activate the shell
poetry shell
agisa-dev "your task"
```

## Learn More

- [Claude Agent SDK Documentation](https://platform.claude.com/docs/en/api/agent-sdk/overview)
- [Python SDK Reference](https://platform.claude.com/docs/en/api/agent-sdk/python)
- [AGI-SAC Main README](README.md)

## CLI Help

```bash
poetry run agisa-dev --help
```

## Examples in Context of AGI-SAC

Since AGI-SAC is a research framework for multi-agent alignment, the dev agent can help with:

### Analyzing Agent Code
```bash
poetry run agisa-dev "Analyze the base_agent.py module and suggest improvements"
```

### Running Specific Tests
```bash
poetry run agisa-dev "Run only the orchestration tests and report failures"
```

### Documentation
```bash
poetry run agisa-dev "Generate a summary of the memory continuum layer implementation"
```

### Refactoring
```bash
poetry run agisa-dev --allow-edits "Add type hints to the cognition module"
```

---

**Note**: The dev agent is a development tool powered by Claude's Agent SDK. It has access to file operations and command execution, so use `--allow-edits` mode carefully in production environments.
