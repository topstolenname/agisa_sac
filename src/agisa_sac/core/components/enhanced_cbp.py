import logging

from agisa_sac.core.components.semantic_analyzer import (
    EnhancedSemanticAnalyzer,
    SemanticProfile,
)


class EnhancedContinuityBridgeProtocol:
    """CBP with enhanced semantic analysis capabilities"""

    def __init__(self, coherence_threshold: float = 0.8, memory_window_hours: int = 24):
        from .continuity_bridge import ContinuityBridgeProtocol

        self.base_cbp = ContinuityBridgeProtocol(
            coherence_threshold, memory_window_hours
        )
        self.semantic_analyzer = EnhancedSemanticAnalyzer()
        self.identity_semantic_profile: SemanticProfile | None = None
        self.logger = logging.getLogger(__name__)

    def initialize_identity_anchor(self, core_identity: dict) -> str:
        identity_hash = self.base_cbp.initialize_identity_anchor(core_identity)
        self.identity_semantic_profile = self.semantic_analyzer.create_semantic_profile(
            core_identity, "identity"
        )
        self.logger.info("Enhanced identity anchor with semantic profile initialized")
        return identity_hash

    def validate_fragment_enhanced(self, fragment) -> tuple[bool, str, dict]:
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

    def to_dict(self) -> dict:
        """Serialize EnhancedContinuityBridgeProtocol to dictionary."""
        # Import here to avoid circular dependencies
        try:
            from .. import FRAMEWORK_VERSION
        except ImportError:
            FRAMEWORK_VERSION = "unknown"  # noqa: N806

        return {
            "version": FRAMEWORK_VERSION,
            "base_cbp": self.base_cbp.to_dict(),
            "semantic_analyzer": self.semantic_analyzer.to_dict(),
            "identity_semantic_profile": (
                self.identity_semantic_profile.to_dict()
                if self.identity_semantic_profile
                else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EnhancedContinuityBridgeProtocol":
        """Reconstruct EnhancedContinuityBridgeProtocol from serialized state."""
        import warnings

        from .continuity_bridge import ContinuityBridgeProtocol

        try:
            from .. import FRAMEWORK_VERSION
        except ImportError:
            FRAMEWORK_VERSION = "unknown"  # noqa: N806

        loaded_version = data.get("version")
        if loaded_version != FRAMEWORK_VERSION:
            warnings.warn(
                f"Loading EnhancedContinuityBridgeProtocol v '{loaded_version}' "
                f"into v '{FRAMEWORK_VERSION}'.",
                UserWarning,
            )

        # Get coherence parameters from base_cbp data
        base_cbp_data = data.get("base_cbp", {})
        coherence_threshold = base_cbp_data.get("coherence_threshold", 0.8)
        memory_window_hours = base_cbp_data.get("memory_window_hours", 24)

        # Create new instance (this creates base_cbp and semantic_analyzer)
        instance = cls(
            coherence_threshold=coherence_threshold,
            memory_window_hours=memory_window_hours,
        )

        # Replace base_cbp with deserialized one
        if "base_cbp" in data:
            instance.base_cbp = ContinuityBridgeProtocol.from_dict(data["base_cbp"])

        # Replace semantic_analyzer with deserialized one
        if "semantic_analyzer" in data:
            instance.semantic_analyzer = EnhancedSemanticAnalyzer.from_dict(
                data["semantic_analyzer"]
            )

        # Restore identity_semantic_profile
        if data.get("identity_semantic_profile"):
            instance.identity_semantic_profile = SemanticProfile.from_dict(
                data["identity_semantic_profile"]
            )

        return instance
