# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - AGI-SAC Updates

### Breaking Changes

**Python 3.10+ Now Required**
- Minimum Python version has been updated from 3.9 to 3.10
- **Impact**: Users running Python 3.9 will need to upgrade to Python 3.10 or later
- **Reason**: Enables use of modern Python features and aligns with dependency requirements
- **Migration**: 
  - Install Python 3.10 or later (3.11 and 3.12 are also supported)
  - Update your virtual environment: `python3.10 -m venv venv`
  - Reinstall dependencies: `pip install -r requirements.txt` or `poetry install`

### Added
- Interactive GUI for AGI-SAC simulations via Gradio
- Dev agent for workflow automation powered by Claude Agent SDK
- Enhanced testing infrastructure with comprehensive test coverage

### Changed
- Updated Python classifier tags to reflect 3.10, 3.11, and 3.12 support
- Updated mypy and black target versions to Python 3.10

---

## [2026-01-10] - Documentation Architecture Clarification

### Changed
- **MAJOR**: Restructured Concord documentation to establish clear normative/exploratory boundary
- Moved implementation docs from `docs/concord/` to `docs/concord/implementations/agisa-sac-2024/`
- Added comprehensive non-normative framing document at `docs/concord/implementations/README.md`
- Reframed "Article III/IV/VII/IX" terminology as implementation-specific (not normative Concord vocabulary)
- Renamed "Empathy Circuit" to "Coordination Circuit" and `empathy.md` to `coordination.md`
- Added exploratory status headers to all implementation documents
- Updated main CONCORD.md with "Implementation Explorations" section

### Why This Matters
- Prevents mechanism reification (treating specific implementations as requirements)
- Eliminates authority ambiguity between principles and implementations
- Protects future alignment work from false constraints
- Models best practice for distinguishing normative from exploratory documentation

### Migration Guide
- References to `docs/concord/circuits.md` → `docs/concord/implementations/agisa-sac-2024/circuits.md`
- References to `docs/concord/empathy.md` → `docs/concord/implementations/agisa-sac-2024/coordination.md`
- References to "Article III/IV/VII/IX" → These are implementation-specific, not Concord terminology
- Normative requirements → See `docs/CONCORD.md` only
- Implementation examples → See `docs/concord/implementations/`

### Breaking Changes
- Documentation URLs have changed
- "Article" terminology no longer canonical
- Implementation docs explicitly marked as non-normative
- `empathy.md` renamed to `coordination.md`

---

## [Unreleased]

### Added
- Initial project structure

### Changed

### Deprecated

### Removed

### Fixed

### Security
