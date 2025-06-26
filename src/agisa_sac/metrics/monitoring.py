import numpy as np
import math
from typing import Dict, Any

try:
    from ..analysis.analyzer import AgentStateAnalyzer
except ImportError:
    AgentStateAnalyzer = Any  # type: ignore


def compute_sri(analyzer: AgentStateAnalyzer, threshold: float = 0.88) -> float:
    """Calculate overall Satori Resonance Index (SRI)."""
    ratio = analyzer.compute_satori_wave_ratio(threshold=threshold)
    mean_strength = analyzer.compute_mean_resonance_strength()
    return float(ratio * mean_strength)


def compute_nds(analyzer: AgentStateAnalyzer) -> float:
    """Calculate normalized diversity score (NDS) of archetypes."""
    dist = analyzer.compute_archetype_distribution()
    if not dist:
        return 0.0
    entropy = analyzer.compute_archetype_entropy(dist)
    max_entropy = math.log2(len(dist)) if len(dist) > 1 else 1.0
    return float(entropy / max_entropy) if max_entropy > 0 else 0.0


def compute_vsd(analyzer: AgentStateAnalyzer) -> float:
    """Calculate voice style diversity (VSD) across agents."""
    vectors = []
    for agent in analyzer.agents.values():
        if hasattr(agent, "voice"):
            vec = agent.voice.linguistic_signature.get("style_vector")
            if isinstance(vec, np.ndarray):
                vectors.append(vec)
    if len(vectors) < 2:
        return 0.0
    mat = np.vstack(vectors)
    norms = np.linalg.norm(mat, axis=1)
    valid = norms > 1e-6
    if np.sum(valid) < 2:
        return 0.0
    mat = mat[valid]
    normed = mat / norms[valid][:, None]
    sims = np.dot(normed, normed.T)
    idx = np.triu_indices(sims.shape[0], 1)
    return float(1.0 - np.mean(sims[idx]))


def compute_mce(analyzer: AgentStateAnalyzer, confidence_threshold: float = 0.5) -> float:
    """Estimate memory coherence (MCE) across agents."""
    ratios = []
    for agent in analyzer.agents.values():
        if hasattr(agent, "memory") and isinstance(agent.memory.memories, dict):
            mems = list(agent.memory.memories.values())
            if not mems:
                continue
            high = sum(1 for m in mems if getattr(m, "confidence", 0.0) >= confidence_threshold)
            ratios.append(high / len(mems))
    return float(np.mean(ratios)) if ratios else 0.0


def generate_monitoring_metrics(analyzer: AgentStateAnalyzer, threshold: float = 0.88) -> Dict[str, float]:
    """Return all monitoring metrics as a dictionary."""
    return {
        "sri": compute_sri(analyzer, threshold),
        "nds": compute_nds(analyzer),
        "vsd": compute_vsd(analyzer),
        "mce": compute_mce(analyzer),
    }
