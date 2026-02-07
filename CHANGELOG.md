# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-07

### Changed
- Promoted version from 1.0.0-alpha to 1.0.0 stable release
- Applied Black formatting across all source and test files
- Fixed Ruff auto-fixable lint violations
- Moved `CLAUDE.md` to project root for discoverability

### Added
- Production readiness audit documentation (`PRODUCTION_READINESS_AUDIT.md`)
- Validation infrastructure: `validation/serialization_audit.py`, `validation/cli_validator.py`, `validation/preset_validator.py`
- Comprehensive serialization compliance audit (13/13 components pass)
- CLI command validation (7/7 commands pass)

### Validated
- All 10 core components implement `to_dict()`/`from_dict()` with `FRAMEWORK_VERSION` tracking
- All CLI entry points (`agisa-sac`, `agisa-federation`, `agisa-chaos`) operational
- Configuration presets (`QUICK_TEST`, `DEFAULT`, `MEDIUM`, `LARGE`) loadable
- Test suite collects 399 tests successfully

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

## [1.0.0-alpha] - 2025-12-01

### Added
- Initial multi-agent simulation framework
- Core components: CognitiveDiversityEngine, MemoryContinuumLayer, VoiceEngine, TemporalResonanceTracker, ResonanceLiturgy, ReflexivityLayer, DynamicSocialGraph, CRDTMemoryLayer, EnhancedSemanticAnalyzer, EnhancedContinuityBridgeProtocol
- CLI tools: `agisa-sac`, `agisa-federation`, `agisa-chaos`, `agisa-dev`, `agisa-sac-gui`
- Federation server for multi-node simulations
- Chaos engineering framework
- CONCORD ethics extension
- GCP deployment support
- MkDocs-based documentation
- Poetry-based dependency management
- Pre-commit hooks (Black, Ruff, Mypy)
- Lazy import system for fast CLI startup
- MessageBus pub/sub for component communication
- Mandatory serialization protocol with version tracking
- Golden master regression tests
- Gradio-based GUI
- Transcript converter CLI command

### Initial Project Structure
- `src/agisa_sac/` - Main package with lazy loading
- `src/agisa_sac/core/` - Orchestrator and component architecture
- `src/agisa_sac/agents/` - EnhancedAgent implementation
- `src/agisa_sac/federation/` - Multi-node coordination
- `src/agisa_sac/chaos/` - Chaos engineering tools
- `src/agisa_sac/extensions/concord/` - Ethics framework
- `tests/` - Unit, integration, and chaos tests
- `docs/` - MkDocs documentation source
