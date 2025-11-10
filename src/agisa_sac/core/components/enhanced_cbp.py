import logging
from typing import Dict, Optional, Tuple

from agisa_sac.core.components.semantic_analyzer import (
    EnhancedSemanticAnalyzer,
    SemanticProfile,
)


class EnhancedContinuityBridgeProtocol:
    """CBP with enhanced semantic analysis capabilities"""

    def __init__(
        self, coherence_threshold: float = 0.8, memory_window_hours: int = 24
    ):
        from .continuity_bridge import ContinuityBridgeProtocol

        self.base_cbp = ContinuityBridgeProtocol(
            coherence_threshold, memory_window_hours
        )
        self.semantic_analyzer = EnhancedSemanticAnalyzer()
        self.identity_semantic_profile: Optional[SemanticProfile] = None
        self.logger = logging.getLogger(__name__)

    def initialize_identity_anchor(self, core_identity: Dict) -> str:
        identity_hash = self.base_cbp.initialize_identity_anchor(core_identity)
        self.identity_semantic_profile = (
            self.semantic_analyzer.create_semantic_profile(
                core_identity, "identity"
            )
        )
        self.logger.info(
            "Enhanced identity anchor with semantic profile initialized"
        )
        return identity_hash

    def validate_fragment_enhanced(self, fragment) -> Tuple[bool, str, Dict]:
        base_valid, base_reason = self.base_cbp.validate_fragment(fragment)
        if not base_valid:
            return False, base_reason, {}
        if not self.identity_semantic_profile:
            return base_valid, base_reason, {}
        fragment_profile = self.semantic_analyzer.create_semantic_profile(
            fragment.content, "fragment"
        )
        coherence_score, coherence_components = (
            self.semantic_analyzer.compute_advanced_coherence(
                fragment_profile, self.identity_semantic_profile
            )
        )
        anomalies = self.semantic_analyzer.detect_semantic_anomalies(
            fragment_profile, self.identity_semantic_profile
        )
        if coherence_score < self.base_cbp.coherence_threshold:
            return (
                False,
                f"Enhanced semantic coherence too low: {coherence_score:.3f}",
                coherence_components,
            )
        if anomalies:
            return (
                False,
                f"Semantic anomalies detected: {', '.join(anomalies)}",
                coherence_components,
            )
        return True, "Enhanced validation passed", coherence_components
