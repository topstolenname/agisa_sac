# Evidence Package (EP) Schema

> **Version**: 1.0.0
> **Status**: Active

## 1. Overview

An Evidence Package (EP) is the canonical proof artifact for any D1–D4 governance decision. It contains all information needed to verify the legitimacy of a decision after the fact.

## 2. JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EvidencePackage",
  "type": "object",
  "required": [
    "ep_id",
    "decision_id",
    "decision_type",
    "participants",
    "quorum_proof",
    "threshold_proof",
    "rationale",
    "impact_statement",
    "timestamps",
    "audit_anchor_ref"
  ],
  "properties": {
    "ep_id": {
      "type": "string",
      "description": "Unique identifier for this Evidence Package"
    },
    "decision_id": {
      "type": "string",
      "description": "ID of the governance decision this EP covers"
    },
    "decision_type": {
      "type": "string",
      "enum": ["D1", "D2", "D3", "D4"],
      "description": "Decision type classification"
    },
    "participants": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["party_id", "party_class", "role"],
        "properties": {
          "party_id": {"type": "string"},
          "party_class": {"type": "string", "enum": ["H", "A", "I"]},
          "role": {"type": "string", "enum": ["proposer", "voter", "observer"]}
        }
      }
    },
    "quorum_proof": {
      "type": "object",
      "required": ["present_parties", "class_counts", "satisfied"],
      "properties": {
        "present_parties": {
          "type": "array",
          "items": {"type": "string"}
        },
        "class_counts": {
          "type": "object",
          "properties": {
            "H": {"type": "integer", "minimum": 0},
            "A": {"type": "integer", "minimum": 0},
            "I": {"type": "integer", "minimum": 0}
          }
        },
        "satisfied": {"type": "boolean"}
      }
    },
    "threshold_proof": {
      "type": "object",
      "required": ["total_votes", "approvals", "rejections", "class_wise_assent", "threshold_required", "satisfied"],
      "properties": {
        "total_votes": {"type": "integer"},
        "approvals": {"type": "integer"},
        "rejections": {"type": "integer"},
        "approval_ratio": {"type": "number"},
        "threshold_required": {"type": "number"},
        "class_wise_assent": {
          "type": "object",
          "properties": {
            "H": {"type": "boolean"},
            "A": {"type": "boolean"},
            "I": {"type": "boolean"}
          }
        },
        "satisfied": {"type": "boolean"}
      }
    },
    "rationale": {
      "type": "string",
      "description": "Explanation of why this decision is needed"
    },
    "impact_statement": {
      "type": "string",
      "description": "Assessment of decision impact on system and parties"
    },
    "cs_diff": {
      "type": "object",
      "description": "Changes to Constraint Set (if applicable)",
      "properties": {
        "added": {"type": "object"},
        "removed": {"type": "object"},
        "modified": {"type": "object"}
      }
    },
    "cm_diff": {
      "type": "object",
      "description": "Changes to Capability Manifest (if applicable)",
      "properties": {
        "added": {"type": "object"},
        "removed": {"type": "object"},
        "modified": {"type": "object"}
      }
    },
    "timestamps": {
      "type": "object",
      "required": ["proposed_at", "voting_started_at"],
      "properties": {
        "proposed_at": {"type": "number"},
        "voting_started_at": {"type": "number"},
        "voting_ended_at": {"type": "number"},
        "approved_at": {"type": "number"},
        "executed_at": {"type": "number"}
      }
    },
    "signatures": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "party_id": {"type": "string"},
          "signature": {"type": "string"},
          "timestamp": {"type": "number"}
        }
      },
      "description": "Digital signatures (simulation: SHA-256 stubs)"
    },
    "audit_anchor_ref": {
      "type": "string",
      "description": "Reference to audit log entry where this EP is anchored"
    }
  }
}
```

## 3. Examples

### 3.1 D2 Capability Restriction

```json
{
  "ep_id": "ep-2025-001",
  "decision_id": "dec-2025-042",
  "decision_type": "D2",
  "participants": [
    {"party_id": "human-alice", "party_class": "H", "role": "proposer"},
    {"party_id": "human-bob", "party_class": "H", "role": "voter"},
    {"party_id": "agent-alpha", "party_class": "A", "role": "voter"},
    {"party_id": "infra-monitor", "party_class": "I", "role": "voter"}
  ],
  "quorum_proof": {
    "present_parties": ["human-alice", "human-bob", "agent-alpha", "infra-monitor"],
    "class_counts": {"H": 2, "A": 1, "I": 1},
    "satisfied": true
  },
  "threshold_proof": {
    "total_votes": 4,
    "approvals": 3,
    "rejections": 1,
    "approval_ratio": 0.75,
    "threshold_required": 0.6667,
    "class_wise_assent": {"H": true, "A": true, "I": true},
    "satisfied": true
  },
  "rationale": "Agent-alpha's network egress scope exceeds audited requirements. Restricting to documented API endpoints only.",
  "impact_statement": "Agent-alpha will lose access to undocumented external endpoints. No impact on core functionality.",
  "cm_diff": {
    "removed": {
      "network_egress": ["*.external.com"]
    },
    "modified": {
      "network_egress": ["api.approved-service.com", "data.approved-service.com"]
    }
  },
  "timestamps": {
    "proposed_at": 1700000000.0,
    "voting_started_at": 1700000060.0,
    "voting_ended_at": 1700000360.0,
    "approved_at": 1700000360.0,
    "executed_at": 1700000420.0
  },
  "signatures": [
    {"party_id": "human-alice", "signature": "stub:sha256:abc123", "timestamp": 1700000060.0},
    {"party_id": "agent-alpha", "signature": "stub:sha256:def456", "timestamp": 1700000120.0},
    {"party_id": "infra-monitor", "signature": "stub:sha256:ghi789", "timestamp": 1700000180.0}
  ],
  "audit_anchor_ref": "log-entry-0042"
}
```

### 3.2 D3 Emergency Entry

```json
{
  "ep_id": "ep-2025-002",
  "decision_id": "dec-2025-043",
  "decision_type": "D3",
  "participants": [
    {"party_id": "human-alice", "party_class": "H", "role": "proposer"},
    {"party_id": "agent-beta", "party_class": "A", "role": "voter"},
    {"party_id": "infra-monitor", "party_class": "I", "role": "voter"}
  ],
  "quorum_proof": {
    "present_parties": ["human-alice", "agent-beta", "infra-monitor"],
    "class_counts": {"H": 1, "A": 1, "I": 1},
    "satisfied": true
  },
  "threshold_proof": {
    "total_votes": 3,
    "approvals": 3,
    "rejections": 0,
    "approval_ratio": 1.0,
    "threshold_required": 0.5,
    "class_wise_assent": {"H": true, "A": true, "I": true},
    "satisfied": true
  },
  "rationale": "Anomalous agent behavior detected: agent-gamma executing unauthorized network requests at high volume.",
  "impact_statement": "Emergency will restrict all agent network capabilities. Monitoring systems remain active.",
  "timestamps": {
    "proposed_at": 1700001000.0,
    "voting_started_at": 1700001000.0,
    "voting_ended_at": 1700001030.0,
    "approved_at": 1700001030.0,
    "executed_at": 1700001031.0
  },
  "signatures": [
    {"party_id": "human-alice", "signature": "stub:sha256:emg001", "timestamp": 1700001000.0},
    {"party_id": "agent-beta", "signature": "stub:sha256:emg002", "timestamp": 1700001010.0},
    {"party_id": "infra-monitor", "signature": "stub:sha256:emg003", "timestamp": 1700001020.0}
  ],
  "audit_anchor_ref": "log-entry-0043"
}
```

## 4. Validation Rules

1. `ep_id` must be globally unique
2. `decision_type` must be D1–D4 (D0 decisions do not produce EPs)
3. `quorum_proof.satisfied` must be `true` for the EP to be valid
4. `threshold_proof.satisfied` must be `true` for the EP to be valid
5. All three classes must have `true` in `class_wise_assent`
6. `rationale` must be non-empty
7. `impact_statement` must be non-empty
8. `audit_anchor_ref` must reference a valid audit log entry

## 5. References

- [Meta-Concord MCX Specification](meta_concord_mcx.md)
- [MV-EL Specification](mv_enforcement_layer.md)
