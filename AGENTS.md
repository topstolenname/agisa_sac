# AGENTS.md – AGI-SAC

## Quick Commands

```bash
# Install dependencies
poetry install
poetry install --with dev,docs

# Run tests
poetry run pytest
poetry run pytest --cov=src/agisa_sac --cov-report=term

# Code quality
poetry run black src/ tests/
poetry run ruff src/ tests/
poetry run mypy src/agisa_sac --ignore-missing-imports
poetry run pre-commit run --all-files

# CLI
agisa-sac run --preset medium --agents 50 --epochs 100
agisa-sac list-presets
agisa-sac convert-transcript --input transcript.json --output context.json

# Documentation
poetry run mkdocs build --strict
poetry run mkdocs serve
```

## Project Structure

- **Source**: `src/agisa_sac/`
- **Tests**: `tests/` (pytest)
- **Docs**: `docs/`
- **Build**: Poetry (`pyproject.toml`)

## Code Style

- **Formatter**: black (line-length=88)
- **Linter**: ruff, flake8
- **Types**: mypy (Python 3.9+)
- **No print()**: Use `from agisa_sac.utils.logger import get_logger`

## Key Conventions

1. **Serialization required**: All stateful components must implement `to_dict()` and `from_dict()`
2. **Version tracking**: Include `FRAMEWORK_VERSION` in serialized state
3. **Optional deps**: Gracefully degrade (check `HAS_*` flags before using optional libraries)
4. **MessageBus**: Use pub/sub for cross-component communication
5. **Type hints**: Required on all public functions

## Key Imports

```python
from agisa_sac import FRAMEWORK_VERSION
from agisa_sac.core.orchestrator import SimulationOrchestrator
from agisa_sac.agents.agent import EnhancedAgent
from agisa_sac.config import SimulationConfig, PRESETS
from agisa_sac.utils.logger import get_logger
from agisa_sac.utils.message_bus import MessageBus
```

## Testing

- Disable heavy deps in tests: `use_semantic=False`, `use_gpu=False`
- Small agent counts: 3-10 for unit tests
- Always test serialization round-trips

## Documentation

See `docs/CLAUDE.md` for comprehensive architecture and patterns guide.
