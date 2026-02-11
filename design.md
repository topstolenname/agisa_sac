# Design Document: AGISA-SAC Modernization

## Overview
Component-based approach to modernizing the agisa-sac codebase with minimal risk and clear verification at each step.

## Architecture

### Component Breakdown

#### Component 1: Infrastructure
**Responsibility:** Poetry migration and environment setup

**Files Modified:**
- `pyproject.toml` (convert to Poetry format)
- `poetry.lock` (generated)

**Implementation Steps:**
1. Backup existing `pyproject.toml`
2. Convert `[build-system]` to use Poetry backend
3. Preserve all existing dependencies
4. Configure Poetry tool sections (black, ruff, mypy, pytest)
5. Run `poetry lock` to generate lockfile
6. Run `poetry install` to verify

**Dependencies:** None

**Verification:**
```bash
poetry install
poetry run python -c "import agisa_sac; print('Success')"
```

---

#### Component 2: Documentation
**Responsibility:** Synchronize CLAUDE.md with current codebase state

**Files Modified:**
- `docs/CLAUDE.md`

**Implementation Steps:**
1. Scan `src/agisa_sac/` directory structure
2. Scan `tests/` directory structure
3. Update file tree in CLAUDE.md
4. Replace command examples:
   - `pip install -e .[dev]` → `poetry install`
   - `pytest` → `poetry run pytest`
   - `black .` → `poetry run black src tests`
5. Update module descriptions if needed

**Dependencies:** infrastructure (Poetry must be working)

**Verification:**
```bash
# Verify all documented files exist
# Verify all documented commands work
```

---

#### Component 3: Linting-Core
**Responsibility:** Fix logical/functional linting errors

**Files Modified:**
- Any files with F-series flake8 errors (imports, undefined vars)
- Known: May include `convert_transcript.py` (missing json import)

**Implementation Steps:**
1. Run `poetry run flake8 src tests --select=F,E9` to find critical errors
2. Fix import errors (F401 - unused, F821 - undefined)
3. Fix logical errors
4. Verify with `pytest` after each fix

**Dependencies:** infrastructure (Poetry for running flake8)

**Verification:**
```bash
poetry run flake8 src tests --select=F,E9
# Should return 0 errors
poetry run pytest
# All tests should pass
```

---

#### Component 4: Linting-Style
**Responsibility:** Fix formatting and E501 (line too long) errors

**Files Modified:**
- All Python files in `src/` and `tests/`

**Implementation Steps:**
1. Run `poetry run black src tests` (auto-format to 88 chars)
2. Run `poetry run flake8 src tests` to check remaining errors
3. Manually fix any remaining E501 errors:
   - Break long lines
   - Use implicit string concatenation
   - Use parentheses for line continuation
4. Re-run Black to ensure consistency

**Dependencies:** linting-core (logical errors must be fixed first)

**Verification:**
```bash
poetry run black --check src tests
# Should report no changes needed
poetry run flake8 src tests
# Should return 0 errors
```

---

#### Component 5: Validation (QA-Critic)
**Responsibility:** Final validation of all changes

**Files Modified:** None

**Implementation Steps:**
1. Run full flake8 check: `poetry run flake8 src tests`
2. Run full test suite: `poetry run pytest`
3. Verify Poetry commands work:
   - `poetry install`
   - `poetry run agisa-sac --help`
4. Check documentation accuracy (spot-check CLAUDE.md)

**Dependencies:** All development components

**Verification:**
```bash
# Zero linting errors
poetry run flake8 src tests | wc -l  # Should be 0

# All tests pass
poetry run pytest --tb=short

# Installation works
poetry install --no-root
```

---

## Execution Order

```
1. [Infrastructure] → Poetry migration
       ↓
2. [Documentation] → CLAUDE.md update
       ↓
3. [Linting-Core] → Fix logical errors
       ↓
4. [Linting-Style] → Fix formatting
       ↓
5. [Validation] → QA check
```

## Rollback Strategy

If any component fails:
1. Restore `pyproject.toml` from backup
2. Use git to revert changes: `git checkout -- <file>`
3. Document the failure in session notes
4. Fix the issue before proceeding

## Tool Configuration

**Flake8** (`.flake8`):
```ini
max-line-length = 88
extend-ignore = E203, W503
```

**Black** (`pyproject.toml`):
```toml
[tool.black]
line-length = 88
target-version = ['py39']
```

**Poetry** (`pyproject.toml`):
```toml
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

## Success Metrics

- ✅ Poetry installation works
- ✅ All 98 flake8 errors resolved
- ✅ Test suite passes
- ✅ CLAUDE.md is accurate
- ✅ No functionality broken
