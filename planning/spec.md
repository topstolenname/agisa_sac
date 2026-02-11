# Meta-Concord (MCX) Governance System Specification

## Overview
A secure, audit-logged governance system that manages party registration, decision execution, and enforcement through a constraint-based sandbox. This system must be resilient to Sybil attacks and ensure all operational changes are authorized by valid governance decisions.

## User Stories

### 1. Party Management
- As a **Governance Administrator**, I want to register new parties only after a D1 decision is approved, so that the network is protected from unauthorized actors.
- As a **Party**, I want to leave the network (remove myself) securely, without allowing others to remove me without authorization.
- As a **Governance System**, I want to prevent the removal of Critical Parties (e.g., human operators) to maintain system integrity.

### 2. Decision Execution & Enforcement
- As a **System Enforcer**, I want governance decisions to automatically update the Capability Manifest (CM) and Control State (CS) so that policies are technically enforced.
- As a **Stakeholder**, I want "irreversible" actions to be strictly defined by the system (not the proposer) to prevent abuse of emergency powers.
- As an **Auditor**, I want a cryptographically verifiable audit log where every entry is deterministic and forms an unbroken hash chain.

### 3. Voting & Governance
- As a **Voter**, I want to cast votes only on decisions within my `representation_scope`, ensuring competence and authority alignment.
- As a **Dissenter**, I want to register objections to decisions, with rate limiting to prevent DOS attacks.
- As a **Proposer**, I want the voting process to handle quorum failures gracefully (non-terminal state) so that proposals can be refined or discarded properly.

### 4. Resource Control
- As a **Resource Manager**, I want compute quotas (steps, tokens, time) to be strictly enforced and logged when exceeded, preventing resource exhaustion.

## Acceptance Criteria

### Critical Security Requirements (Must Fix)
- [ ] **Auth-001 (Registration):** `register_party()` MUST verify a valid D1 decision exists for the target party.
- [ ] **Auth-002 (Removal):** `remove_party()` MUST verify a valid D2 decision OR prove the caller is the target party (self-removal).
- [ ] **Auth-003 (Critical Parties):** Removal of designated Critical Parties MUST be blocked regardless of D2 decision unless a specific "System Reset" condition is met (TBD).
- [ ] **Log-001 (Determinism):** Audit log hashes MUST be deterministic. All dictionary data MUST be sorted by key before hashing.
- [ ] **Exec-001 (Enforcement):** `execute_decision()` MUST apply `decision.cs_diff` and `decision.cm_diff` to the `SandboxEnforcer`.
- [ ] **Exec-002 (Verification):** The system MUST verify that enforcement changes were applied before transitioning decision to `EXECUTED`.
- [ ] **Safe-001 (Irreversibility):** The `irreversible` flag MUST be derived from a trusted system mapping of Action Types, appearing in the proposal payload. Proposer-provided flags MUST be ignored.

### High Priority Requirements
- [ ] **Vote-001 (Scope):** `cast_vote()` MUST validate that the decision target falls within the voter's `representation_scope`. Returns `legitimate=False` if invalid.
- [ ] **Res-001 (Time Quota):** `SandboxEnforcer` MUST abort execution if `used.time_seconds >= quota.max_time_seconds`.
- [ ] **Log-002 (Quota Auditing):** All quota denials (steps, tokens, time) MUST create an `action_denied` audit entry with reason and metrics.

### Medium Priority Requirements
- [ ] **Config-001 (Renewals):** `EmergencyManager` MUST track renewal counts and reject if `>= max_renewals` (default 5).
- [ ] **Rate-001 (Objections):** `register_objection()` MUST enforce `max_objections_per_window`. Raise `ValueError` if exceeded.
- [ ] **Data-001 (Objection IDs):** Objection IDs MUST be unique globally (e.g., include timestamp or UUID, or `decision-party-basis-count`).
- [ ] **State-001 (Quorum):** Quorum failure MUST NOT be a terminal state; or it must transition specifically to `REJECTED`/`EXPIRED`, not leave the decision hanging.
- [ ] **Code-001 (DRY Enforcement):** The Governance Engine MUST NOT duplicate checks performed by `SandboxEnforcer`. Delegate all action allowance checks to the Enforcer.

### Performance Optimization (Low Priority)
- [ ] **Perf-001 (Merkle):** Merkle root computation SHOULD occur at optimized intervals (e.g., powers of two), not on every entry.
- [ ] **Perf-002 (Pattern Matching):** Use `fnmatch` for CS pattern globbing (`*/danger`).

## Constraints
- **Language:** Python 3.9+
- **Testing:** Pytest with >80% coverage.
- **Security:** No "trust me" flags in payloads.
- **Data:** JSON-serializable structures for all logs and states.
