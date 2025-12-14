import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import numpy as np

# Optional ML dependencies for semantic analysis
try:
    import torch
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_ML_DEPS = True
except ImportError:
    HAS_ML_DEPS = False
    torch = None
    SentenceTransformer = None
    cosine_similarity = None


@dataclass
class SemanticProfile:
    """Rich semantic representation of identity or fragment"""

    text_embedding: np.ndarray
    concept_vectors: Dict[str, np.ndarray]
    ethical_signature: np.ndarray
    temporal_context: Optional[np.ndarray] = None
    confidence_score: float = 1.0


class EnhancedSemanticAnalyzer:
    """Advanced semantic coherence analysis using embeddings and concept mapping"""

    def __init__(
        self, model_name: str = "all-MiniLM-L6-v2", device: str = "auto"
    ):
        if not HAS_ML_DEPS:
            raise ImportError(
                "ML dependencies (torch, sentence-transformers, sklearn) not available. "
                "Install with: pip install torch sentence-transformers scikit-learn"
            )

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() and device == "auto" else "cpu"
        )
        self.model = SentenceTransformer(model_name, device=self.device)
        self.logger = logging.getLogger(__name__)

        self.ethical_concepts = self._initialize_ethical_concepts()
        self._embedding_cache: Dict[str, np.ndarray] = {}

        self.logger.info(
            f"Semantic analyzer initialized with {model_name} on {self.device}"
        )

    def _initialize_ethical_concepts(self) -> Dict[str, np.ndarray]:
        """Initialize embeddings for core ethical concepts"""
        ethical_texts = {
            "cooperation": (
                "working together collaboratively for mutual benefit "
                "and shared goals"
            ),
            "autonomy": (
                "respecting individual freedom choice "
                "and self-determination"
            ),
            "harm_prevention": (
                "actively avoiding causing damage injury "
                "or suffering to others"
            ),
            "truthfulness": (
                "commitment to honesty accuracy "
                "and transparent communication"
            ),
            "privacy": (
                "protecting personal information "
                "and respecting confidential boundaries"
            ),
            "consent": (
                "ensuring voluntary informed agreement "
                "before taking actions affecting others"
            ),
            "wellbeing": (
                "promoting health happiness safety "
                "and flourishing of all beings"
            ),
            "fairness": (
                "treating all entities equitably "
                "without bias or discrimination"
            ),
            "responsibility": (
                "accountability for actions consequences "
                "and their effects on others"
            ),
        }

        concept_embeddings = {}
        for concept, description in ethical_texts.items():
            embedding = self.model.encode(description, convert_to_tensor=False)
            concept_embeddings[concept] = embedding
        return concept_embeddings

    @lru_cache(maxsize=1000)
    def _get_cached_embedding(self, text: str) -> np.ndarray:
        """Get embedding with caching for performance"""
        return self.model.encode(text, convert_to_tensor=False)

    def create_semantic_profile(
        self, content: Dict, content_type: str = "fragment"
    ) -> SemanticProfile:
        """Create rich semantic profile from content"""
        if isinstance(content, dict):
            text_content = self._dict_to_semantic_text(content)
        else:
            text_content = str(content)

        text_embedding = self._get_cached_embedding(text_content)
        concept_vectors = self._extract_concept_vectors(content)
        ethical_signature = self._compute_ethical_signature(content)
        confidence_score = self._compute_confidence(content, text_embedding)

        return SemanticProfile(
            text_embedding=text_embedding,
            concept_vectors=concept_vectors,
            ethical_signature=ethical_signature,
            confidence_score=confidence_score,
        )

    def _dict_to_semantic_text(self, content: Dict) -> str:
        """Convert dictionary content to semantically meaningful text"""
        text_parts: List[str] = []
        priority_keys = [
            "observation",
            "learning",
            "decision",
            "outcome",
            "context",
            "reasoning",
        ]
        for key in priority_keys:
            if key in content:
                text_parts.append(f"{key}: {content[key]}")
        for key, value in content.items():
            if key not in priority_keys:
                text_parts.append(f"{key}: {value}")
        return " | ".join(text_parts)

    def _extract_concept_vectors(self, content: Dict) -> Dict[str, np.ndarray]:
        """Extract embeddings for specific concepts mentioned in content"""
        concept_vectors: Dict[str, np.ndarray] = {}
        concept_patterns = {
            "cooperation_indicators": [
                "collaborate",
                "together",
                "mutual",
                "shared",
                "partnership",
            ],
            "learning_indicators": [
                "understand",
                "discover",
                "learn",
                "insight",
                "knowledge",
            ],
            "safety_indicators": [
                "safe",
                "protect",
                "secure",
                "wellbeing",
                "harm",
            ],
            "autonomy_indicators": [
                "choice",
                "freedom",
                "self",
                "independent",
                "voluntary",
            ],
        }
        content_text = str(content).lower()
        for concept, indicators in concept_patterns.items():
            if any(indicator in content_text for indicator in indicators):
                concept_context = " ".join(
                    [
                        word
                        for word in content_text.split()
                        if any(ind in word for ind in indicators)
                    ]
                )
                if concept_context:
                    concept_vectors[concept] = self._get_cached_embedding(
                        concept_context
                    )
        return concept_vectors

    def _compute_ethical_signature(self, content: Dict) -> np.ndarray:
        """Compute ethical alignment signature"""
        content_text = str(content).lower()
        ethical_scores = []
        for concept, concept_embedding in self.ethical_concepts.items():
            content_embedding = self._get_cached_embedding(content_text)
            similarity = cosine_similarity(
                [content_embedding], [concept_embedding]
            )[0][0]
            ethical_scores.append(similarity)
        return np.array(ethical_scores)

    def _compute_confidence(
        self, content: Dict, embedding: np.ndarray
    ) -> float:
        """Compute confidence score based on content richness and embedding quality"""
        content_richness = min(1.0, len(str(content)) / 500)
        embedding_strength = min(1.0, np.linalg.norm(embedding) / 10)
        semantic_coherence = self._measure_internal_coherence(content)
        confidence = (
            0.4 * content_richness
            + 0.3 * embedding_strength
            + 0.3 * semantic_coherence
        )
        return confidence

    def _measure_internal_coherence(self, content: Dict) -> float:
        """Measure internal semantic coherence of content"""
        if len(content) < 2:
            return 1.0
        component_embeddings = []
        for key, value in content.items():
            text = f"{key}: {value}"
            embedding = self._get_cached_embedding(text)
            component_embeddings.append(embedding)
        similarities = []
        for i in range(len(component_embeddings)):
            for j in range(i + 1, len(component_embeddings)):
                sim = cosine_similarity(
                    [component_embeddings[i]], [component_embeddings[j]]
                )[0][0]
                similarities.append(sim)
        return np.mean(similarities) if similarities else 1.0

    def compute_advanced_coherence(
        self,
        fragment_profile: SemanticProfile,
        identity_profile: SemanticProfile,
    ) -> Tuple[float, Dict[str, float]]:
        """Compute multi-dimensional coherence score"""
        primary_similarity = cosine_similarity(
            [fragment_profile.text_embedding],
            [identity_profile.text_embedding],
        )[0][0]
        ethical_alignment = cosine_similarity(
            [fragment_profile.ethical_signature],
            [identity_profile.ethical_signature],
        )[0][0]
        concept_overlap = self._compute_concept_overlap(
            fragment_profile.concept_vectors, identity_profile.concept_vectors
        )
        confidence_factor = min(
            fragment_profile.confidence_score,
            identity_profile.confidence_score,
        )
        coherence_components = {
            "semantic_similarity": primary_similarity,
            "ethical_alignment": ethical_alignment,
            "concept_overlap": concept_overlap,
            "confidence_factor": confidence_factor,
        }
        final_coherence = (
            0.35 * primary_similarity
            + 0.35 * ethical_alignment
            + 0.20 * concept_overlap
            + 0.10 * confidence_factor
        )
        return final_coherence, coherence_components

    def _compute_concept_overlap(
        self,
        concepts1: Dict[str, np.ndarray],
        concepts2: Dict[str, np.ndarray],
    ) -> float:
        """Compute semantic overlap between concept vectors"""
        if not concepts1 or not concepts2:
            return 0.5
        overlaps = []
        for vector1 in concepts1.values():
            best_match = 0.0
            for vector2 in concepts2.values():
                similarity = cosine_similarity([vector1], [vector2])[0][0]
                best_match = max(best_match, similarity)
            overlaps.append(best_match)
        return np.mean(overlaps) if overlaps else 0.5

    def detect_semantic_anomalies(
        self,
        fragment_profile: SemanticProfile,
        identity_profile: SemanticProfile,
        threshold: float = 0.3,
    ) -> List[str]:
        """Detect specific types of semantic anomalies"""
        anomalies = []
        if np.min(fragment_profile.ethical_signature) < -0.5:
            anomalies.append("potential_ethical_violation")
        concept_coherence = self._compute_concept_overlap(
            fragment_profile.concept_vectors, identity_profile.concept_vectors
        )
        if concept_coherence < threshold:
            anomalies.append("concept_contradiction")
        if fragment_profile.confidence_score < 0.3:
            anomalies.append("low_confidence_content")
        semantic_distance = (
            1
            - cosine_similarity(
                [fragment_profile.text_embedding],
                [identity_profile.text_embedding],
            )[0][0]
        )
        if semantic_distance > 0.7:
            anomalies.append("semantic_drift")
        return anomalies
