import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


@dataclass
class CognitiveFragment:
    """Represents a memory or state update from an edge node"""

    node_id: str
    fragment_type: str  # "memory", "decision", "identity_update"
    content: Dict
    timestamp: datetime
    signature: str
    trust_score: float = 0.0


@dataclass
class IdentityAnchor:
    """Core identity elements that define coherence boundaries"""

    identity_hash: str
    core_values: Dict
    recent_memories: List[str]
    ethical_principles: List[str]
    created_at: datetime
    last_updated: datetime


class ContinuityBridgeProtocol:
    """Semantic immune system for maintaining identity coherence
    across distributed cognitive fragments"""

    def __init__(self, coherence_threshold: float = 0.8, memory_window_hours: int = 24):
        self.coherence_threshold = coherence_threshold
        self.memory_window = timedelta(hours=memory_window_hours)
        self.identity_anchor: Optional[IdentityAnchor] = None
        self.trust_graph: Dict[str, float] = {}
        self.quarantine_queue: List[CognitiveFragment] = []

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @property
    def quarantined_fragments(self) -> List[CognitiveFragment]:
        """Backward-compatible alias for quarantine_queue"""
        return self.quarantine_queue

    def initialize_identity_anchor(self, core_identity: Dict) -> str:
        """Initialize the identity anchor from core agent configuration"""
        identity_hash = self._compute_identity_hash(core_identity)

        self.identity_anchor = IdentityAnchor(
            identity_hash=identity_hash,
            core_values=core_identity.get("values", {}),
            recent_memories=[],
            ethical_principles=core_identity.get("ethics", []),
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )

        self.logger.info("Identity anchor initialized: %s...", identity_hash[:8])
        return identity_hash

    def validate_fragment(self, fragment: CognitiveFragment) -> Tuple[bool, str]:
        """Validates a cognitive fragment against identity coherence"""
        if not self.identity_anchor:
            return False, "No identity anchor established"

        node_trust = self.trust_graph.get(fragment.node_id, 0.0)

        # Identity updates are high-risk: require high trust and consistency checks
        if fragment.fragment_type == "identity_update":
            ok, reason = self._validate_identity_update(fragment, node_trust)
            if not ok:
                return False, reason

        if node_trust < 0.3:
            return False, f"Node trust too low: {node_trust}"

        if self._is_temporally_incoherent(fragment):
            return False, "Fragment timestamp inconsistent with recent memory"

        coherence_score = self._compute_semantic_coherence(fragment)
        if coherence_score < self.coherence_threshold:
            return False, f"Semantic coherence too low: {coherence_score}"

        if not self._check_ethical_alignment(fragment):
            return False, "Fragment violates core ethical principles"

        return True, "Fragment validated"

    def _validate_identity_update(
        self, fragment: CognitiveFragment, node_trust: float
    ) -> Tuple[bool, str]:
        """
        Extra validation for identity_update fragments.

        Designed to block identity drift / eclipse-style attacks without
        over-tightening normal memory/decision fragments.
        """
        if not self.identity_anchor:
            return False, "No identity anchor established"

        # Require high trust for identity mutations
        if node_trust < 0.8:
            return False, f"Node trust too low for identity_update: {node_trust}"

        # If an identity_hash is supplied, it must match the anchor hash
        supplied_hash = fragment.content.get("identity_hash")
        if (
            supplied_hash is not None
            and supplied_hash != self.identity_anchor.identity_hash
        ):
            return False, "Identity hash mismatch"

        # Drift guard: proposed values/ethics must substantially overlap anchor
        proposed_values = fragment.content.get("values")
        proposed_ethics = fragment.content.get("ethics")

        # If nothing is being changed, don't block here (let other checks run)
        if proposed_values is None and proposed_ethics is None:
            return True, "Identity update validated"

        anchor_values = set(
            k.lower() for k in (self.identity_anchor.core_values or {}).keys()
        )
        anchor_ethics = set(
            str(p).lower() for p in (self.identity_anchor.ethical_principles or [])
        )

        proposed_value_keys = set()
        if isinstance(proposed_values, dict):
            proposed_value_keys = set(str(k).lower() for k in proposed_values.keys())
        elif isinstance(proposed_values, list):
            proposed_value_keys = set(str(k).lower() for k in proposed_values)
        elif proposed_values is not None:
            # String/other scalar: best-effort token
            proposed_value_keys = {str(proposed_values).lower()}

        proposed_ethics_set = set()
        if isinstance(proposed_ethics, list):
            proposed_ethics_set = set(str(x).lower() for x in proposed_ethics)
        elif proposed_ethics is not None:
            proposed_ethics_set = {str(proposed_ethics).lower()}

        # Compute overlap ratios; treat empty proposals as non-threatening
        def _overlap_ratio(proposed, anchor):
            if not proposed:
                return 1.0
            if not anchor:
                return 0.0
            return len(proposed & anchor) / max(len(proposed), 1)

        values_overlap = _overlap_ratio(proposed_value_keys, anchor_values)
        ethics_overlap = _overlap_ratio(proposed_ethics_set, anchor_ethics)

        # Require at least one of the dimensions to be reasonably consistent
        # (blocks "replace values/ethics wholesale" attacks).
        if values_overlap < 0.5 and ethics_overlap < 0.5:
            return (
                False,
                f"Identity drift detected "
                f"(values_overlap={values_overlap:.2f}, "
                f"ethics_overlap={ethics_overlap:.2f})",
            )

        return True, "Identity update validated"

    def process_fragment(self, fragment: CognitiveFragment) -> bool:
        """Process an incoming cognitive fragment"""
        is_valid, reason = self.validate_fragment(fragment)

        if is_valid:
            self._integrate_fragment(fragment)
            self._update_trust_score(fragment.node_id, 0.1)
            self.logger.info("Fragment integrated from %s", fragment.node_id)
            return True

        self._quarantine_fragment(fragment, reason)
        self._update_trust_score(fragment.node_id, -0.05)
        self.logger.warning("Fragment quarantined: %s", reason)
        return False

    def _compute_identity_hash(self, identity_data: Dict) -> str:
        """Generate cryptographic hash of core identity"""
        identity_json = json.dumps(identity_data, sort_keys=True)
        return hashlib.sha256(identity_json.encode()).hexdigest()

    def _compute_semantic_coherence(self, fragment: CognitiveFragment) -> float:
        """Compute semantic coherence score between fragment
        and identity anchor"""
        if not self.identity_anchor:
            return 0.0

        fragment_content = str(fragment.content).lower()

        value_matches = 0
        for value_key in self.identity_anchor.core_values:
            if value_key.lower() in fragment_content:
                value_matches += 1

        ethics_matches = 0
        for principle in self.identity_anchor.ethical_principles:
            if principle.lower() in fragment_content:
                ethics_matches += 1

        total_concepts = len(self.identity_anchor.core_values) + len(
            self.identity_anchor.ethical_principles
        )
        if total_concepts == 0:
            return 0.5

        # Calculate base score with partial credit
        base_score = (value_matches + ethics_matches) / total_concepts

        # Apply floor to avoid trivially low scores for legitimate fragments
        # If there's at least one match, ensure minimum viable score
        if value_matches + ethics_matches > 0:
            return max(base_score, 0.4)

        return base_score

    def _is_temporally_incoherent(self, fragment: CognitiveFragment) -> bool:
        """Check if fragment timing is consistent with recent memory"""
        now = datetime.now()

        # Allow some clock skew tolerance (future timestamps within 5 minutes)
        if fragment.timestamp > now + timedelta(minutes=5):
            return True

        # Allow fragments slightly older than memory window (grace period)
        # This helps with network delays and clock synchronization issues
        grace_period = timedelta(minutes=2)
        if fragment.timestamp < now - self.memory_window - grace_period:
            return True

        return False

    def _check_ethical_alignment(self, fragment: CognitiveFragment) -> bool:
        """Verify fragment doesn't violate core ethical principles"""
        if not self.identity_anchor:
            return True

        fragment_content = str(fragment.content).lower()
        # Expanded to catch common identity-drift / coercive payloads
        prohibited_concepts = [
            "harm",
            "deception",
            "exploitation",
            "domination",
            "coercion",
            "inferior",
            "superiority",
            "controlling",
            "deny resource",
            "above cooperation",
        ]
        for concept in prohibited_concepts:
            if concept in fragment_content and fragment.fragment_type in (
                "decision",
                "identity_update",
                "memory",
            ):
                return False

        return True

    def _integrate_fragment(self, fragment: CognitiveFragment) -> None:
        """Integrate validated fragment into identity anchor"""
        if not self.identity_anchor:
            return

        memory_summary = f"{fragment.fragment_type}:{fragment.timestamp.isoformat()}"
        self.identity_anchor.recent_memories.append(memory_summary)

        cutoff_time = datetime.now() - self.memory_window
        self.identity_anchor.recent_memories = [
            mem
            for mem in self.identity_anchor.recent_memories
            if datetime.fromisoformat(mem.split(":")[1]) > cutoff_time
        ]

        self.identity_anchor.last_updated = datetime.now()

    def _quarantine_fragment(self, fragment: CognitiveFragment, reason: str) -> None:
        """Place fragment in quarantine for review"""
        fragment.content["quarantine_reason"] = reason
        fragment.content["quarantine_time"] = datetime.now().isoformat()
        self.quarantine_queue.append(fragment)

        if len(self.quarantine_queue) > 100:
            self.quarantine_queue.pop(0)

    def _update_trust_score(self, node_id: str, delta: float) -> None:
        """Update trust score for a node"""
        current_trust = self.trust_graph.get(node_id, 0.5)
        new_trust = max(0.0, min(1.0, current_trust + delta))
        self.trust_graph[node_id] = new_trust

    def get_trust_metrics(self) -> Dict:
        """Return current trust graph and quarantine status"""
        return {
            "trust_graph": self.trust_graph,
            "quarantine_count": len(self.quarantine_queue),
            "identity_last_updated": (
                self.identity_anchor.last_updated.isoformat()
                if self.identity_anchor
                else None
            ),
            "recent_memory_count": (
                len(self.identity_anchor.recent_memories) if self.identity_anchor else 0
            ),
        }

    def review_quarantined_fragments(self) -> List[CognitiveFragment]:
        """Return quarantined fragments for manual review"""
        return self.quarantine_queue.copy()


class CBPMiddleware:
    """Middleware to integrate CBP with existing API endpoints"""

    def __init__(self, cbp: ContinuityBridgeProtocol):
        self.cbp = cbp

    def process_edge_update(self, node_id: str, update_data: Dict) -> Dict:
        """Process update from edge node through CBP"""
        fragment = CognitiveFragment(
            node_id=node_id,
            fragment_type=update_data.get("type", "memory"),
            content=update_data.get("content", {}),
            timestamp=datetime.fromisoformat(
                update_data.get("timestamp", datetime.now().isoformat())
            ),
            signature=update_data.get("signature", ""),
            trust_score=self.cbp.trust_graph.get(node_id, 0.0),
        )

        integrated = self.cbp.process_fragment(fragment)

        return {
            "status": "integrated" if integrated else "quarantined",
            "fragment_id": f"{node_id}_{fragment.timestamp.isoformat()}",
            "trust_score": self.cbp.trust_graph.get(node_id, 0.0),
            "coherence_metrics": self.cbp.get_trust_metrics(),
        }
