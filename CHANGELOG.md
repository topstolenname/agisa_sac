# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
