"""Tests for audit log integrity.

Validates:
- Append-only hash chain
- Tamper detection (modify entry -> verify fails)
- Merkle root computation
- Entry inclusion verification
"""

from __future__ import annotations

import pytest

from agisa_sac.governance.auditlog import GENESIS_HASH, AuditLog


class TestHashChain:
    """Test hash chain integrity."""

    def test_empty_log_valid(self):
        log = AuditLog()
        assert log.verify_log_integrity() is True

    def test_single_entry_valid(self):
        log = AuditLog()
        log.append(event_type="test", data={"key": "value"})
        assert log.verify_log_integrity() is True

    def test_multiple_entries_valid(self):
        log = AuditLog()
        for i in range(20):
            log.append(event_type=f"event_{i}", data={"i": i})
        assert log.verify_log_integrity() is True

    def test_first_entry_references_genesis(self):
        log = AuditLog()
        entry = log.append(event_type="first", data={})
        assert entry.previous_hash == GENESIS_HASH

    def test_entries_chain_correctly(self):
        log = AuditLog()
        e1 = log.append(event_type="first", data={})
        e2 = log.append(event_type="second", data={})
        assert e2.previous_hash == e1.entry_hash

    def test_tamper_entry_hash_detected(self):
        """Modify an entry's hash -> integrity check fails."""
        log = AuditLog()
        log.append(event_type="event_1", data={"x": 1})
        log.append(event_type="event_2", data={"x": 2})
        log.append(event_type="event_3", data={"x": 3})

        # Tamper with middle entry's hash
        log._entries[1].entry_hash = "tampered_hash_value"

        assert log.verify_log_integrity() is False

    def test_tamper_entry_data_detected(self):
        """Modify an entry's data -> hash mismatch detected."""
        log = AuditLog()
        log.append(event_type="event_1", data={"x": 1})
        log.append(event_type="event_2", data={"x": 2})

        # Tamper with data (hash will no longer match)
        log._entries[0].data = {"x": 999}

        assert log.verify_log_integrity() is False

    def test_tamper_previous_hash_detected(self):
        """Modify an entry's previous_hash -> chain broken."""
        log = AuditLog()
        log.append(event_type="event_1", data={"x": 1})
        log.append(event_type="event_2", data={"x": 2})
        log.append(event_type="event_3", data={"x": 3})

        # Break chain by modifying previous_hash
        log._entries[2].previous_hash = "broken_chain"
        # Also recompute entry_hash to match new previous_hash
        log._entries[2].entry_hash = log._entries[2].compute_hash()

        assert log.verify_log_integrity() is False


class TestEntryInclusion:
    """Test entry inclusion verification."""

    def test_valid_entry_included(self):
        log = AuditLog()
        entry = log.append(event_type="test", data={"k": "v"})
        assert log.verify_entry_inclusion(entry.entry_id) is True

    def test_nonexistent_entry_not_included(self):
        log = AuditLog()
        log.append(event_type="test", data={})
        assert log.verify_entry_inclusion("nonexistent-id") is False

    def test_tampered_entry_fails_inclusion(self):
        log = AuditLog()
        entry = log.append(event_type="test", data={"original": True})
        entry.data = {"tampered": True}
        assert log.verify_entry_inclusion(entry.entry_id) is False


class TestMerkleRoots:
    """Test Merkle root computation."""

    def test_merkle_root_computed_at_interval(self):
        log = AuditLog(merkle_interval=5)
        for i in range(10):
            log.append(event_type=f"event_{i}", data={"i": i})
        roots = log.get_merkle_roots()
        assert len(roots) == 2  # At entries 5 and 10

    def test_merkle_root_has_hash(self):
        log = AuditLog(merkle_interval=3)
        for i in range(3):
            log.append(event_type=f"event_{i}", data={})
        roots = log.get_merkle_roots()
        assert len(roots) == 1
        assert "root_hash" in roots[0]
        assert len(roots[0]["root_hash"]) == 64  # SHA-256 hex

    def test_anchor_root(self):
        log = AuditLog(merkle_interval=3)
        for i in range(3):
            log.append(event_type=f"event_{i}", data={})
        roots = log.get_merkle_roots()
        ref = log.anchor_root(roots[0]["root_hash"])
        assert ref.startswith("anchor-")


class TestBoundedSummary:
    """Test bounded summary for transparency-by-volume mitigation."""

    def test_summary_bounded(self):
        log = AuditLog()
        for i in range(100):
            log.append(event_type=f"event_{i}", data={"i": i})

        summary = log.get_bounded_summary(max_entries=10)
        assert len(summary) == 10

    def test_summary_contains_required_fields(self):
        log = AuditLog()
        log.append(event_type="test", data={}, summary="Test summary")
        summary = log.get_bounded_summary()
        assert len(summary) == 1
        entry = summary[0]
        assert "entry_id" in entry
        assert "event_type" in entry
        assert "summary" in entry
        assert "entry_hash" in entry

    def test_empty_log_summary(self):
        log = AuditLog()
        summary = log.get_bounded_summary()
        assert len(summary) == 0


class TestDecisionAudit:
    """Test audit entries filtered by decision ID."""

    def test_get_entries_by_decision(self):
        log = AuditLog()
        log.append(event_type="proposed", data={}, decision_id="dec-1")
        log.append(event_type="voted", data={}, decision_id="dec-1")
        log.append(event_type="proposed", data={}, decision_id="dec-2")
        log.append(event_type="executed", data={}, decision_id="dec-1")

        entries = log.get_entries_by_decision("dec-1")
        assert len(entries) == 3
        assert all(e.decision_id == "dec-1" for e in entries)
