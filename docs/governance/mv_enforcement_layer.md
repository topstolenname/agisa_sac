# Minimal Viable Enforcement Layer (MV-EL) Specification

> **Version**: 1.0.0
> **Status**: Active

## 1. Overview

The Minimal Viable Enforcement Layer (MV-EL) provides the minimum set of enforcement primitives required to make MCX governance credible. It implements sandboxing, capability revocation, quarantine, and a graduated sanctions ladder.

## 2. Enforcement Interface

All enforcement implementations must satisfy `EnforcementInterface`:

```python
class EnforcementInterface(ABC):
    def apply_capability_manifest(self, scope: str, cm: CapabilityManifest) -> None: ...
    def check_action_allowed(self, action: str, context: dict) -> tuple[bool, str]: ...
    def revoke_capabilities(self, scope: str, level: RevocationLevel) -> None: ...
    def enforce_sanction(self, scope: str, level: SanctionLevel, reason: str) -> None: ...
    def get_current_scope_state(self, scope: str) -> dict: ...
```

## 3. Capability Manifest (CM)

The CM defines what an agent/scope is permitted to do:

| Field | Type | Description |
|-------|------|-------------|
| tool_allowlist | list[str] | Permitted tool identifiers |
| tool_denylist | list[str] | Explicitly forbidden tools |
| data_scopes | list[str] | Accessible data paths/datasets |
| network_egress | list[str] | Permitted network destinations |
| compute_quota | dict | Token/time/step limits |
| memory_scope | dict | Memory access boundaries |
| revocation_policy | str | How capabilities are revoked |

## 4. Constraint Set (CS)

The CS defines what is forbidden and what invariants must hold:

| Field | Type | Description |
|-------|------|-------------|
| forbidden_actions | list[str] | Explicitly forbidden action patterns |
| invariants | list[str] | Conditions that must always hold |
| veto_categories | list[str] | Categories eligible for veto |
| appeal_windows | dict | Time windows for appeals per decision type |
| emergency_profile | dict | Emergency-specific constraints |

## 5. Sanctions Ladder

| Level | Code | Name | Description |
|-------|------|------|-------------|
| S0 | WARN | Warning | Logged warning, no capability change |
| S1 | THROTTLE | Throttle | Rate-limited actions |
| S2 | RESTRICT_TOOLS | Restrict Tools | Specific tools removed from CM |
| S3 | QUARANTINE | Quarantine | Isolated execution, no external effects |
| S4 | SUSPEND_SCOPE | Suspend Scope | All capabilities suspended |
| S5 | TERMINATE_INSTANCE | Terminate | Instance terminated |

### 5.1 Escalation Rules

- **Repeat violations**: Same violation type within window → escalate one level
- **Severity thresholds**: Critical violations may skip levels (configurable)
- **De-escalation**: After clean period, sanctions reduce one level
- **Maximum**: S5 requires D2 governance decision to reverse

## 6. Sandbox Enforcer (Reference Implementation)

The `SandboxEnforcer` is the reference MV-EL implementation for simulations:

### 6.1 Tool Enforcement
- Maintains allowlist/denylist per scope
- Checks tool invocations against CM before execution
- Logs all denied attempts

### 6.2 Data Scope Enforcement
- Validates data access paths against CM data_scopes
- Pattern matching for path-based access control

### 6.3 Network Enforcement
- Egress allowlist checking (stubbed for simulation)
- All network attempts logged

### 6.4 Compute Enforcement
- Token/time/step tracking per scope
- Quota enforcement with configurable limits

### 6.5 Audit Integration
- All enforcement actions logged to audit log as EP addenda
- Sanction events produce their own audit entries

## 7. Revocation Levels

| Level | Name | Effect |
|-------|------|--------|
| THROTTLE | Throttle | Reduce rate limits |
| RESTRICT | Restrict | Remove specific capabilities |
| QUARANTINE | Quarantine | Isolate from external systems |
| SUSPEND | Suspend | Halt all capability usage |
| TERMINATE | Terminate | End scope entirely |

## 8. Integration Points

### 8.1 Action Execution Path

```
Agent requests action
  → EnforcementInterface.check_action_allowed(action, context)
    → CM check (tool in allowlist?)
    → CS check (action not forbidden?)
    → Quota check (within limits?)
    → Return allow/deny + reason
  → If allowed: execute + log
  → If denied: log denial + check sanction escalation
```

### 8.2 Governance Decision Execution

```
GovernanceEngine.execute(decision)
  → Verify EP complete
  → EnforcementInterface.apply_capability_manifest(scope, new_cm)
  → Log execution event
```

## 9. Security Notes

**Simulation Stubs**: In simulation mode, cryptographic signatures and network enforcement are stubbed. These are architecturally represented with correct interfaces but use placeholder implementations. Production deployment requires replacing stubs with real implementations.

## 10. References

- [Meta-Concord MCX Specification](meta_concord_mcx.md)
- [Threat Model](threat_model.md)
