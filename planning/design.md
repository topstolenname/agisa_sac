# Meta-Concord (MCX) Governance System Design

## Architecture Overview

The system follows a strict Controller-Enforcer pattern. The **Governance Engine** manages state and decision lifecycles, but actual changes to system capabilities are gated by the **Sandbox Enforcer**. All actions are immutable recorded in the **Audit Log**.

## Components

### 1. **governance-engine**
The core state machine for decisions, parties, and votes.
- **Responsibilities:**
    - Manage Decision Lifecycle (Propose -> Vote -> Enact -> Execute).
    - Maintain Party Registry (with Authentication checks).
    - Validate Voting Logic (Quorum, Pass Thresholds, Representation Scope).
    - Coordinate with Enforcer for execution.
- **Inputs:** Proposals, Votes, Party Registration Requests.
- **Outputs:** Decision Results, State Updates, Audit Events.
- **Dependencies:** audit-log, sandbox-enforcer, objection-manager
- **Size:** L (Critical Logic)

### 2. **sandbox-enforcer**
The security gatekeeper for all system actions.
- **Responsibilities:**
    - Manage Capability Manifest (CM) and Control State (CS).
    - Enforce Compute Quotas (time, steps, tokens).
    - Check actions against allowed/forbidden patterns.
    - Provide "Dry Run" capability for decision impacts.
- **Inputs:** Action Requests, CM/CS Updates.
- **Outputs:** Allowed/Denied verdicts, Usage Metrics.
- **Dependencies:** audit-log
- **Size:** M

### 3. **audit-log**
Cryptographically verifiable immutable ledger.
- **Responsibilities:**
    - Record all system events deterministically.
    - Compute Merkle Roots for integrity verification.
    - Prevent tampering with history (Wait, it's a log, it mostly just appends).
- **Inputs:** Events.
- **Outputs:** Hash Chains, Merkle Roots, Query Results.
- **Dependencies:** None
- **Size:** S

### 4. **cli-interface**
Command-line interface for human operators.
- **Responsibilities:**
    - Expose Governance Engine functions (register, vote, propose).
    - Format output for human readability.
    - Handle authentication tokens for CLI actions.
- **Inputs:** Shell commands.
- **Outputs:** JSON/Text output.
- **Dependencies:** governance-engine
- **Size:** S

### 5. **objection-manager**
Handles dissent and dispute resolution logic.
- **Responsibilities:**
    - Register objections.
    - Enforce rate limits on objections.
    - Track objection status.
- **Inputs:** Objections.
- **Outputs:** Objection Records.
- **Dependencies:** audit-log
- **Size:** S

## Security Architecture

1.  **Authorization:** All state-changing operations (Register, Remove, Execute) require a proof of authorization (Decision ID or Auth Token).
2.  **Determinism:** All logs use strictly sorted JSON serialization before hashing.
3.  **Least Privilege:** Enforcer defaults to "Deny" unless explicitly allowed by CS/CM.
4.  **Irreversibility:** Trusted mapping of `ActionType -> bool` prevents easy rollback of critical actions.

## Data Flow

1.  **Proposal:** Authenticated Party -> Engine -> (Validate Scope) -> Active Proposal.
2.  **Vote:** Party -> Engine -> (Check Quorum) -> (Check Threshold) -> Approved Decision.
3.  **Execution:** Engine -> (Get Decision Diff) -> Enforcer.apply(diff) -> (Verify) -> Engine.State = EXECUTED.
4.  **Enforcement:** Agent -> Payload -> Enforcer -> (Check Quota) -> (Check CS) -> Run/Block.
