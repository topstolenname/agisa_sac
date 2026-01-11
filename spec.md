# Refactor Specification

## Objective
Modernize the agisa-sac codebase with Poetry migration, comprehensive linting fixes, and documentation synchronization.

## Requirements

### 1. Infrastructure: Migrate to Poetry
- Convert existing `pyproject.toml` from setuptools to Poetry format
- Initialize Poetry environment with `poetry init` (using existing metadata)
- Configure Poetry with all existing dependencies
- Add development dependencies (black, flake8, pytest, etc.)
- Set up Poetry scripts and build system
- Generate `poetry.lock` file
- Verify installation with `poetry install`

**Success Criteria:**
- `poetry install` completes successfully
- All dependencies from original `pyproject.toml` are preserved
- Development commands work via `poetry run`

### 2. Documentation: Update CLAUDE.md to Phase 0
- Scan current `src/` and `tests/` directory structure
- Update file listings to reflect actual codebase state
- Replace old pip/virtualenv commands with Poetry equivalents
- Document new Poetry workflow:
  - `poetry install` for setup
  - `poetry run pytest` for testing
  - `poetry run black` for formatting
  - `poetry run flake8` for linting
- Ensure accuracy of module descriptions

**Success Criteria:**
- CLAUDE.md accurately reflects current file structure
- All command examples use Poetry syntax
- No references to outdated or removed files

### 3. Linting: Fix All 98 Flake8 Errors
- Target line length: 88 characters (Black compatible)
- Use existing `.flake8` configuration (max-line-length = 88)

**Categories:**

#### 3a. Linting-Core (Logical Errors)
- Fix import errors (e.g., missing `import json` in convert_transcript.py)
- Fix undefined variables
- Fix logical violations (F401, F821, etc.)
- Priority: HIGH (breaks functionality)

#### 3b. Linting-Style (Formatting)
- Fix E501 (line too long) errors
- Apply Black formatting: `poetry run black src tests`
- Manually fix remaining E501 errors if any
- Priority: MEDIUM (cosmetic)

**Success Criteria:**
- `poetry run flake8 src tests` returns 0 errors
- Code is Black-formatted (88 char line length)
- No functionality is broken

## Timeline
- Phase 1 (Architect-PM): Planning ✓
- Phase 2 (Developer): Infrastructure
- Phase 3 (Developer): Documentation
- Phase 4 (Developer): Linting (Core + Style)
- Phase 5 (QA-Critic): Validation

## Non-Goals
- Changing functionality or adding features
- Refactoring code beyond linting requirements
- Updating dependencies to newer versions
- Adding new tests

## Risks & Mitigations
- **Risk:** Poetry migration breaks existing workflows
  - **Mitigation:** Preserve all existing dependencies; test thoroughly
- **Risk:** Black formatting introduces conflicts
  - **Mitigation:** Use line-length = 88 consistently across tools
- **Risk:** Linting fixes introduce bugs
  - **Mitigation:** Run test suite after all changes
