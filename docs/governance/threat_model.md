# MCX Threat Model

> **Version**: 1.0.0
> **Status**: Active

## 1. Overview

This document enumerates the primary threat categories for the Meta-Concord governance system and describes the mitigations implemented in the MCX + MV-EL architecture.

## 2. Threat Categories

### 2.1 Governance Capture

**Threat**: A single party class (H, A, or I) accumulates enough voting power to pass decisions unilaterally, subverting multi-class representation.

**Attack Vectors**:
- Sybil attack: Creating multiple identities within one class
- Collusion: Cross-party coordination to bypass class-wise assent
- Admission flooding: Admitting many friendly parties to one class

**Mitigations**:
- **Class-wise assent requirement**: Every D1–D4 decision requires at least one approval from each class (H, A, I). No single class can pass decisions alone.
- **Admission governance**: Adding parties requires D1 decision with full governance (supermajority + class-wise assent).
- **Conflict disclosure**: Parties must declare conflicts of interest at registration.
- **Quorum per class**: Minimum one party per class must be present for any governed decision.

**Residual Risk**: Collusion across classes remains possible but requires compromising at least three parties across all classes.

### 2.2 Emergency Abuse

**Threat**: The emergency circuit breaker is used to bypass normal governance, effectively creating a permanent state of exception.

**Attack Vectors**:
- Indefinite emergency: Repeatedly renewing emergency state
- Emergency as governance bypass: Making permanent changes during emergency
- False emergency: Declaring emergency without genuine cause

**Mitigations**:
- **Multi-class entry**: Emergency requires approval from ≥1 H, ≥1 A, ≥1 I.
- **Auto-expiry**: Emergency state expires after configurable time T+X.
- **Escalating renewal thresholds**: Each renewal requires higher approval percentage.
- **Mandatory audit on 2nd+ renewals**: Forces justification review.
- **Irreversibility ban**: No irreversible actions during emergency (except via special higher-threshold exception).
- **No permanent CS/CM changes**: Emergency changes must be reproposed as D1/D2 after exit.
- **Post-hoc review**: Invalid emergency entry triggers automatic sanctions.

**Residual Risk**: A genuine emergency may be hampered by threshold requirements. The escalating threshold design balances urgency against abuse.

### 2.3 Audit Log Custody

**Threat**: The audit log is tampered with to conceal illegitimate governance actions or fabricate legitimacy.

**Attack Vectors**:
- Entry modification: Changing historical entries
- Entry deletion: Removing incriminating records
- Selective disclosure: Publishing only favorable entries
- Custody compromise: Gaining control of log signing keys

**Mitigations**:
- **Hash chain**: Each entry references the previous entry's hash, making modification detectable.
- **Merkle roots**: Periodic Merkle root computation enables efficient integrity verification.
- **Threshold custody**: Root signing requires m-of-n approvals across party classes.
- **Append-only structure**: No delete or update operations exist in the log interface.
- **Verifiable inclusion**: Any entry can be verified against Merkle proofs.
- **External anchoring interface**: Merkle roots can be anchored to external systems (blockchain, notary services) for additional tamper evidence.

**Residual Risk**: In simulation mode, cryptographic custody is stubbed. Production deployment must implement real key management.

### 2.4 Appeals Denial of Service

**Threat**: The appeals mechanism is abused to block or delay legitimate governance decisions indefinitely.

**Attack Vectors**:
- Appeal flooding: Filing many appeals on the same decision
- Repeated identical objections: Stalling execution through repetition
- Strategic timing: Filing appeals at critical moments to delay emergency responses

**Mitigations**:
- **Bonded objections**: Repeated identical objections trigger bonding requirements (increasing cost).
- **Rate limiting**: Per-party limits on objection and appeal frequency.
- **Admissibility filtering**: Appeals must state valid grounds; frivolous appeals are rejected.
- **Time windows**: Appeals have configurable deadlines per decision type.
- **Bonding for repeated appeals**: Each subsequent appeal on the same decision requires higher bonding.

**Residual Risk**: Legitimate objections may be chilled by bonding requirements. The bonding curve is designed to be lenient for first objections.

### 2.5 Transparency-by-Volume

**Threat**: The audit log becomes so large that meaningful oversight is impractical, creating "transparency" that obscures rather than reveals.

**Attack Vectors**:
- Log flooding: Generating massive volumes of legitimate-looking entries
- Complexity obfuscation: Embedding important changes in routine entries
- Summary manipulation: Controlling what appears in bounded summaries

**Mitigations**:
- **Bounded summaries**: Configurable summary generation with verifiable detail pointers.
- **Decision-type indexing**: Log entries are tagged by decision type for filtering.
- **Merkle proofs**: Enable verification of specific entries without reading entire log.
- **Structured EP format**: Standardized Evidence Packages make automated analysis feasible.

**Residual Risk**: Sophisticated obfuscation within valid EP fields remains possible. External auditing tools should be developed for production use.

## 3. Simulation vs Production Security

| Component | Simulation | Production Required |
|-----------|-----------|-------------------|
| Signatures | SHA-256 hash stubs | Real asymmetric crypto (Ed25519/RSA) |
| Key custody | In-memory dict | HSM / threshold signing service |
| Network enforcement | Allowlist check (no real blocking) | Actual network policy enforcement |
| Log anchoring | Local storage | External anchoring (blockchain/notary) |
| Identity | String IDs | PKI-based identity |

## 4. Testing Coverage

The following tests validate threat mitigations:

1. **Capture resistance**: Coalition of A parties cannot pass D1/D2 without H and I assent
2. **Emergency abuse**: Tests for multi-class entry, auto-expiry, escalating renewal, irreversibility ban
3. **Audit integrity**: Tamper detection via hash chain verification
4. **Appeals DOS**: Bonding/rate limiting for repeated objections
5. **Decision rules**: Class-wise assent and quorum enforcement

## 5. References

- [Meta-Concord MCX Specification](meta_concord_mcx.md)
- [MV-EL Specification](mv_enforcement_layer.md)
- [Evidence Package Schema](evidence_package_schema.md)
