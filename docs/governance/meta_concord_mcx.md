# Meta-Concord (MCX) Governance Specification

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2025-11-17

## 1. Overview

Meta-Concord (MCX) is a constitutional, enforceable "governance-of-governance" layer for the AGI-SAC framework. It provides procedural legitimacy for multi-agent system decisions through structured decision-making, class-wise representation, and verifiable audit trails.

### 1.1 Design Principles

1. **Procedural Legitimacy**: Governance constrains *actions*, not *minds*. Agents retain cognitive autonomy; only external behaviors in governed scope require authorization.
2. **Constitutional Supremacy**: The Constraint Set (CS) and Capability Manifest (CM) form the constitution. All decisions must be consistent with them.
3. **Multi-Class Representation**: Three party classes (Human, Agent, Infrastructure) ensure no single constituency can dominate governance.
4. **Verifiable Accountability**: Every governed action produces an Evidence Package (EP) anchored in an append-only audit log with hash-chain integrity.
5. **Minimal Enforcement**: The enforcement layer implements the minimum primitives needed for credible governance (sandbox, revocation, quarantine, sanctions).

## 2. Party Classes

### 2.1 Definitions

| Class | Code | Description |
|-------|------|-------------|
| **Human** | `H` | Human operators, researchers, oversight personnel |
| **Agent** | `A` | Autonomous agents, AI systems, software actors |
| **Infrastructure** | `I` | Platform services, monitoring systems, infrastructure operators |

### 2.2 Party Registration

Each party has:
- **id**: Unique identifier
- **class**: H, A, or I
- **pubkey**: Public key for signature verification (optional/stubbed for simulation)
- **representation_scope**: What domain(s) this party can vote on
- **conflict_disclosures**: Declared conflicts of interest

### 2.3 Admission and Removal

- Admission requires D1 decision (supermajority + class-wise assent)
- Removal requires D2 decision with mandatory impact statement
- Self-removal (resignation) is always permitted (Article VII alignment)

## 3. Decision Taxonomy

### 3.1 Decision Types

| Type | Name | Description | Governance Required |
|------|------|-------------|-------------------|
| **D0** | Operational | Routine actions within existing CM scope | None (pre-authorized) |
| **D1** | Policy | CS/CM modifications, party admission/removal | Full governance |
| **D2** | Capability | Capability grants, restrictions, scope changes | Full governance |
| **D3** | Emergency | Emergency circuit breaker entry/renewal/exit | Multi-class threshold |
| **D4** | Constitutional | Changes to governance rules themselves | Highest threshold |

### 3.2 Decision Lifecycle

```
PROPOSED → VOTING → {OBJECTED → VOTING} → APPROVED → EXECUTED
                  → APPEALED → {VOTING}
                  → REJECTED
                  → EXPIRED
```

States:
- **PROPOSED**: Decision submitted with rationale and impact statement
- **VOTING**: Active voting period
- **OBJECTED**: Execution paused due to formal objection
- **APPEALED**: Under appeal review
- **APPROVED**: All thresholds met, ready for execution
- **REJECTED**: Failed to meet thresholds or vetoed
- **EXECUTED**: Successfully executed with EP recorded
- **EXPIRED**: Voting period elapsed without resolution

## 4. Voting Rules

### 4.1 Quorum Requirements

For D1–D4 decisions:
- At least 1 Human (H) party present
- At least 1 Agent (A) party present
- At least 1 Infrastructure (I) party present

### 4.2 Threshold Requirements

| Decision Type | Approval Threshold | Class-Wise Assent |
|--------------|-------------------|-------------------|
| D1 (Policy) | 2/3 supermajority | Required (≥1 from each class) |
| D2 (Capability) | 2/3 supermajority | Required (≥1 from each class) |
| D3 (Emergency) | Simple majority | Required (≥1 from each class) |
| D4 (Constitutional) | 3/4 supermajority | Required (≥1 from each class) |

### 4.3 Anti-Capture Rule

No D1–D4 decision can pass with approvals solely from one party class. This is enforced structurally through the class-wise assent requirement.

## 5. Objection and Veto

### 5.1 Objections

Any party may object to a pending decision. Valid objection bases:
- Missing EP fields
- Threshold failure
- Log integrity concern
- Inadequate impact statement
- CS/CM mismatch

Objections pause execution by default and must be addressed before proceeding.

### 5.2 Bonded Objections

Repeated identical objections from the same party trigger bonding requirements (rate limiting). This prevents objection-based denial of service.

### 5.3 Veto

Veto is restricted to specific categories:
- Irreversible physical-world actions
- Privacy-sensitive disclosures
- Capability expansions beyond audited scope
- Key custody/rotation events

A veto triggers mandatory arbitration review.

## 6. Appeals and Deadlock

### 6.1 Appeals

Any party may appeal a decision outcome. Appeals must state specific grounds and are subject to:
- Admissibility filtering (valid grounds required)
- Rate limiting (bonding for repeated appeals)
- Time windows (configurable per decision type)

### 6.2 Deadlock Ladder

When governance cannot reach resolution:
1. **Mediation** (timeboxed): Structured dialogue period
2. **Arbitration** (mixed panel): Cross-class panel renders binding decision
3. **Default-to-Safety**: More restrictive CM/CS applied until resolution

## 7. Emergency Circuit Breaker

### 7.1 Entry

- Requires multi-class threshold invocation (≥1 H, ≥1 A, ≥1 I approval)
- Recorded as D3 decision with full EP

### 7.2 Constraints During Emergency

- Auto-expiry at configured time T+X
- No permanent CS/CM changes permitted
- Irreversibility ban: no irreversible actions unless special higher-threshold exception vote
- All actions logged with emergency context

### 7.3 Renewal

- Requires escalating thresholds (higher approval % on each renewal)
- Mandatory audit review on 2nd+ renewals
- Renewal count tracked and reported

### 7.4 Exit and Review

- Exit requires D3 decision or auto-expiry
- Post-hoc review mandatory
- Invalid emergency entry triggers automatic sanctions

## 8. Evidence Packages (EP)

Every D1–D4 decision produces an Evidence Package containing:
- Decision ID and type
- Participants and their votes
- Quorum and threshold proofs
- Rationale and impact statement
- CS/CM diffs (if applicable)
- Timestamps and signatures
- Audit log anchor reference

See [Evidence Package Schema](evidence_package_schema.md) for detailed JSON schema.

## 9. Audit Log

### 9.1 Structure

- Append-only log with hash-chain integrity
- Each entry references previous entry's hash
- Periodic Merkle root computation
- Bounded summaries with verifiable detail pointers

### 9.2 Verification

- `verify_log_integrity()`: Full chain verification
- `verify_entry_inclusion(entry_id)`: Merkle proof for specific entry

### 9.3 Anchoring

- `anchor_root(root_hash)`: External anchoring interface (stubbed for simulation)
- Threshold custody for root signing (m-of-n across classes)

## 10. Integration with AGI-SAC

### 10.1 Feature Flag

MCX governance is enabled via configuration:
```yaml
concord:
  mode: "mcx"  # "legacy" for v0 behavior
```

### 10.2 Action Execution Path

Before any governed action:
1. Verify CM allows the action
2. Verify CS doesn't forbid it
3. Verify EP authorization (D1–D4)
4. Log execution event

### 10.3 CLI

New `concord` subcommands are added to the existing `agisa-sac` CLI.

## 11. References

- AGI-SAC Concord of Coexistence (existing extension)
- [MV-EL Specification](mv_enforcement_layer.md)
- [Threat Model](threat_model.md)
- [Evidence Package Schema](evidence_package_schema.md)
