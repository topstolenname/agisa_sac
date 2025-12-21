# Poetry Migration Guide for AGI-SAC

This document describes the migration from setuptools to Poetry for the AGI-SAC project.

## 🎯 Migration Summary

The project has been successfully migrated from setuptools to Poetry for better dependency management and development workflow.

## 📦 Key Changes

### 1. Dependency Management
- **Before**: Used `setuptools` with `pyproject.toml` and optional dependencies
- **After**: Uses Poetry with dependency groups for better organization

### 2. Dependency Groups
The migration organizes dependencies into logical groups:

#### Core Dependencies (always installed)
- `numpy`, `scipy`, `networkx` - Scientific computing
- `torch`, `scikit-learn` - Machine learning
- `fastapi`, `httpx` - Web framework and HTTP client
- `sentence-transformers` - NLP embeddings
- `pydantic` - Data validation
- `hyperopt` - Hyperparameter optimization
- `anthropic` - Claude API integration

#### Optional Dependency Groups
- **dev**: Development tools (pytest, black, ruff, mypy, pre-commit)
- **monitoring**: Prometheus, psutil, uvicorn
- **docs**: MkDocs, material theme, docstrings
- **visualization**: Matplotlib
- **federation**: Docker, Kubernetes
- **gcp**: Google Cloud Platform services
- **topology**: Topological data analysis (ripser, persim)
- **chaos**: Chaos engineering (locust, chaostoolkit)
- **tracing**: OpenTelemetry integration

### 3. CLI Commands
The CLI entry points are preserved:
- `agisa-sac` - Main simulation CLI
- `agisa-federation` - Federation server CLI
- `agisa-chaos` - Chaos engineering CLI

## 🚀 Getting Started

### Prerequisites
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"
```

### Basic Setup
```bash
# Clone the repository
cd agisa_sac

# Install core dependencies
poetry install

# Test the installation
poetry run python run_cli_test.py
```

### Development Setup
```bash
# Install with development dependencies
poetry install --with dev

# Install with all optional dependencies
poetry install --all-extras

# Install specific groups
poetry install --with docs,visualization
```

## 🔧 Usage Examples

### List Available Presets
```bash
poetry run agisa-sac list-presets
```

### Run a Simulation
```bash
# Using a preset
poetry run agisa-sac run --preset quick_test

# With custom parameters
poetry run agisa-sac run --preset medium --agents 10 --epochs 20

# With GPU acceleration
poetry run agisa-sac run --preset large --gpu
```

### Convert Transcript
```bash
poetry run agisa-sac convert-transcript \
    --input examples/sample_transcript.json \
    --output output/context_blob.json
```

## 📊 Testing the Setup

### Basic Functionality Test
```bash
poetry run python run_cli_test.py
```

### Import Test
```bash
poetry run python -c "
import sys
sys.path.insert(0, 'src')
from agisa_sac.config import PRESETS
print('Available presets:')
for name, config in PRESETS.items():
    print(f'  {name}: {config.num_agents} agents, {config.num_epochs} epochs')
"
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Error**: Make sure you're running commands from the project root
2. **Missing Dependencies**: Run `poetry install` to install all dependencies
3. **CLI Not Found**: Use `poetry run` prefix for all commands

### Environment Check
```bash
# Check Poetry version
poetry --version

# Check installed packages
poetry show --tree

# Check virtual environment
poetry env info
```

## 📁 Project Structure

```
agisa_sac/
├── pyproject.toml          # Poetry configuration
├── poetry.lock            # Locked dependencies
├── src/agisa_sac/         # Source code
├── tests/                 # Test suite
├── examples/              # Example configurations
├── docs/                  # Documentation
└── README.md             # Project documentation
```

## 🔒 Dependency Locking

Poetry maintains a `poetry.lock` file that locks all dependencies to specific versions, ensuring reproducible builds:

```bash
# Update dependencies
poetry update

# Lock dependencies without updating
poetry lock --no-update
```

## 🧪 Development Workflow

### Code Quality
```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff src/ tests/

# Type checking
poetry run mypy src/agisa_sac --ignore-missing-imports
```

### Testing
```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/agisa_sac --cov-report=html
```

## 📋 Migration Benefits

1. **Better Dependency Management**: Clear separation of core vs optional dependencies
2. **Reproducible Builds**: Locked dependency versions
3. **Simplified Development**: Single command for setup and testing
4. **Better CI/CD**: Easier integration with GitHub Actions
5. **Virtual Environment Management**: Automatic venv creation and management

## 🔧 Configuration Presets

The following presets are available:

| Preset | Agents | Epochs | GPU | Semantic | Use Case |
|--------|--------|--------|-----|----------|----------|
| quick_test | 3 | 5 | No | No | Quick testing |
| default | 5 | 10 | No | Yes | Standard runs |
| medium | 20 | 50 | No | Yes | Development |
| large | 100 | 100 | No | Yes | Production |

## 🚀 Next Steps

1. **Run Your First Simulation**: Try `poetry run agisa-sac run --preset quick_test`
2. **Explore Configuration**: Check `examples/configs/` for sample configurations
3. **Extend Functionality**: Add new components following the existing patterns
4. **Contribute**: Follow the development guidelines in the main README

## 📚 Additional Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [AGI-SAC Research Mandate](docs/CLAUDE.md)
- [CLI Documentation](src/agisa_sac/cli.py)
- [Configuration Guide](src/agisa_sac/config.py)

---

**Migration Date**: December 2025  
**Poetry Version**: 2.2.1  
**Python Version**: 3.9+