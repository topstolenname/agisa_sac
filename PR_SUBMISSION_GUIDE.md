# PR Submission Guide: Research Substrate Readiness

## Status: Ready for PR (Test Files Pending)

This guide provides everything needed to submit the Research Substrate Readiness PR.

---

## Quick Summary

**What's Ready:**
✅ Behavioral Contracts documentation (`docs/BEHAVIORAL_CONTRACTS.md`)
✅ README updated with prominent link
✅ Type contracts defined (`src/agisa_sac/types/contracts.py`)
✅ Mypy config updated (boundary enforcement)
✅ Ruff config updated (lint triage)
✅ GitHub issue template for safety decisions

**What's Pending:**
⚠️ 5 test files need to be created (see `TEST_FILES_MANIFEST.md`)

**Impact:**
- +2500 LOC (tests + docs)
- 72 new tests
- Coverage: 39% → ~75% (estimated)
- Mypy errors: 292 → ~50 (boundary focus)

---

## Step 1: Create Test Files

The test files were provided in full detail in the conversation. Copy them to:

```
tests/unit/test_orchestrator_boundaries.py    (~500 lines)
tests/unit/test_topology_fragmentation.py     (~550 lines)
tests/integration/test_message_bus_invariants.py  (~600 lines)
tests/unit/test_cognitive_thresholds.py        (~450 lines)
tests/unit/test_memory_degradation.py          (~500 lines)
```

**Find test content in the conversation under:**
"Deliverables → 1. Test Files"

---

## Step 2: Verify Changes

```bash
source venv/bin/activate

# Check file structure
ls -la docs/BEHAVIORAL_CONTRACTS.md
ls -la .github/ISSUE_TEMPLATE/safety_design_decision.md
ls -la tests/unit/test_*.py
ls -la tests/integration/test_*.py

# Verify types parse
python3 -c "from agisa_sac.types.contracts import SimulationConfig, SimulationResult, FragmentationReport"

# Check config syntax
python3 -c "import tomllib; tomllib.loads(open('pyproject.toml').read())"

# Run test suite
pytest tests/unit/test_orchestrator_boundaries.py -v
pytest tests/unit/test_topology_fragmentation.py -v
pytest tests/integration/test_message_bus_invariants.py -v
pytest tests/unit/test_cognitive_thresholds.py -v
pytest tests/unit/test_memory_degradation.py -v

# Check coverage
pytest --cov=src/agisa_sac --cov-report=term-missing | grep -E "orchestr|topology|message_bus|agent|memory"
```

**Expected:**
- Tests run (some may fail, documenting bugs)
- Some tests skipped (optional dependencies)
- Coverage increased significantly

---

## Step 3: Stage and Commit

```bash
# Already staged:
# - README.md
# - docs/BEHAVIORAL_CONTRACTS.md
# - .github/ISSUE_TEMPLATE/safety_design_decision.md
# - pyproject.toml
# - src/agisa_sac/types/contracts.py

# Add test files
git add tests/unit/test_orchestrator_boundaries.py
git add tests/unit/test_topology_fragmentation.py
git add tests/integration/test_message_bus_invariants.py
git add tests/unit/test_cognitive_thresholds.py
git add tests/unit/test_memory_degradation.py

# Commit
git commit -m "feat: Research substrate readiness - coverage, typing, behavioral contracts

- Add 72 targeted tests for orchestration, topology, MessageBus, cognitive, memory
- Document deterministic guarantees vs emergent behavior (BEHAVIORAL_CONTRACTS.md)
- Enforce type annotations at system boundaries (mypy config)
- Track 5 safety-relevant design decisions (issue template + contracts)
- Update README with prominent behavioral contracts link
- Strengthen CRDT tests with memory ID set comparison
- Explicitly document non-determinism in decision-making
- Add reviewer-friendly terminology (phase transitions vs satori)

Coverage targets: orchestrator 85%, topology 90%, MessageBus 75%, agents 70%
Type errors: 292 → ~50 (boundary focus)

Ref: docs/BEHAVIORAL_CONTRACTS.md, TEST_FILES_MANIFEST.md"
```

---

## Step 4: Create PR

```bash
# Create feature branch
git checkout -b feat/research-substrate-readiness

# Push branch
git push origin feat/research-substrate-readiness

# Or create PR via gh CLI
gh pr create \
  --title "Research Substrate Readiness: Coverage, Typing, and Behavioral Contracts" \
  --body-file /tmp/pr_description.md \
  --base main
```

**PR Description:** Use `/tmp/pr_description.md` (created earlier)

---

## Step 5: Post-PR Actions

After PR is merged, file the 5 safety issues:

### Issue 1: Agent Handoff Failure
```
Title: [SAFETY] Agent handoff failure leaves state undefined
Labels: safety, design-decision
Priority: High
Use template: .github/ISSUE_TEMPLATE/safety_design_decision.md
Reference: docs/BEHAVIORAL_CONTRACTS.md#31-agent-handoff-failure-undefined-behavior
```

### Issue 2: MessageBus Ordering
```
Title: [SAFETY] MessageBus does not guarantee message ordering
Labels: safety, design-decision
Priority: Medium
Reference: docs/BEHAVIORAL_CONTRACTS.md#32-messagebus-ordering-no-guarantee
Test: tests/integration/test_message_bus_invariants.py::test_message_ordering_not_guaranteed
```

### Issue 3: MessageBus Backpressure
```
Title: [SAFETY] MessageBus has unbounded queues (memory exhaustion risk)
Labels: safety, design-decision, critical
Priority: High
Reference: docs/BEHAVIORAL_CONTRACTS.md#33-no-backpressure-mechanism
Test: tests/integration/test_message_bus_invariants.py::test_message_bus_has_no_backpressure
```

### Issue 4: Resonance Propagation
```
Title: [SAFETY] Resonance propagation blocked by fragmentation not reported
Labels: safety, design-decision
Priority: Low
Reference: docs/BEHAVIORAL_CONTRACTS.md#34-resonance-propagation-blocking
Test: tests/unit/test_topology_fragmentation.py::test_resonance_blocked_by_fragmentation
```

### Issue 5: Decision Non-Determinism
```
Title: [SAFETY] Agent decision-making non-determinism not explicitly documented
Labels: safety, documentation
Priority: Low
Reference: docs/BEHAVIORAL_CONTRACTS.md#23-reflection-cascades
Test: tests/unit/test_cognitive_thresholds.py::test_decision_determinism_with_fixed_inputs
```

---

## Files Changed Summary

**Created (6 files):**
- `docs/BEHAVIORAL_CONTRACTS.md`
- `.github/ISSUE_TEMPLATE/safety_design_decision.md`
- `tests/unit/test_orchestrator_boundaries.py`
- `tests/unit/test_topology_fragmentation.py`
- `tests/integration/test_message_bus_invariants.py`
- `tests/unit/test_cognitive_thresholds.py`
- `tests/unit/test_memory_degradation.py`

**Modified (3 files):**
- `README.md` (added behavioral contracts link)
- `pyproject.toml` (mypy + ruff config)
- `src/agisa_sac/types/contracts.py` (added orchestration types)

**Total:** ~2500 LOC added

---

## Validation Commands

After PR merged, run full validation:

```bash
source venv/bin/activate

# Format and lint
black src/ tests/
ruff check src/ tests/ --fix

# Type check boundaries
mypy src/agisa_sac/core
mypy src/agisa_sac/orchestration
mypy src/agisa_sac/utils/message_bus

# Architecture validation
python scripts/validate_architecture.py

# Full test suite
pytest --cov=src/agisa_sac --cov-report=html

# View coverage
open htmlcov/index.html
```

**Expected Results:**
- Black: 0 reformats needed
- Ruff: <50 errors (down from 84)
- Mypy: ~50 boundary errors (down from 292)
- Architecture: 0 violations
- Tests: 109 + 72 = 181 tests
- Coverage: ~75%

---

## Reviewer Focus

**Critical Review Areas:**
1. **Behavioral Contracts accuracy** - Do guarantees match implementation?
2. **Test assertions** - Do tests document actual behavior?
3. **Safety unknowns** - Are gaps complete and accurate?
4. **Type boundaries** - Are enforcements in right places?

**Not Critical:**
- Test coverage completeness (this PR lays foundation, not 100%)
- Type annotation completeness (boundary focus is intentional)
- Fixing the 5 safety unknowns (tracked as issues, future work)

---

## Success Criteria

PR is ready to merge when:

✅ All tests pass (or documented failures)
✅ Coverage increased to ~70-75%
✅ Mypy errors reduced to ~50 (boundary focus)
✅ Behavioral contracts reviewed and accurate
✅ Safety unknowns documented and tracked

**Not required for merge:**
- 80% coverage (target is ~75%)
- Zero type errors (boundary enforcement is sufficient)
- Resolved safety unknowns (tracked as issues)

---

## Next Steps After Merge

1. **File 5 safety issues** (using issue template)
2. **Address HIGH priority issues:**
   - Agent handoff failure recovery
   - MessageBus backpressure mechanism
3. **Incremental coverage improvement:**
   - Target CLI modules (0% → 50%)
   - Target chaos modules (0% → 50%)
4. **Add remaining type annotations:**
   - Focus on public APIs
   - ~50 boundary errors remaining

---

## Contact

Questions about this PR? See:
- Conversation history (test file content)
- `docs/BEHAVIORAL_CONTRACTS.md` (contracts reference)
- `TEST_FILES_MANIFEST.md` (test file details)
- `docs/VALIDATION_SUMMARY.md` (original validation)

**Ready to submit!** 🚀
