from typing import Dict

import numpy as np


def compute_sri(agent) -> float:
    """Self Reference Index: ratio of self-themed memories."""
    memories = getattr(agent, "memory", None)
    if not memories or not memories.memories:
        return 0.0
    total = len(memories.memories)
    self_refs = sum(1 for m in memories.memories.values() if "self" in m.theme)
    return self_refs / total if total else 0.0


def compute_nds(agent) -> float:
    """Narrative Divergence Score: count of unique themes."""
    memories = getattr(agent, "memory", None)
    if not memories or not memories.memories:
        return 0.0
    themes = {m.theme for m in memories.memories.values()}
    return float(len(themes))


def compute_vsd(agent) -> float:
    """Voice Style Drift: L2 distance between earliest and latest style vectors."""
    resonance = getattr(agent, "temporal_resonance", None)
    if not resonance or not resonance.history:
        return 0.0
    timestamps = sorted(resonance.history.keys())
    first = np.array(resonance.history[timestamps[0]]["vector"])
    last = np.array(resonance.history[timestamps[-1]]["vector"])
    return float(np.linalg.norm(first - last))


def compute_mce(agent) -> float:
    """Memory Coherence Error: proportion of corrupted memories."""
    memories = getattr(agent, "memory", None)
    if not memories or not memories.memories:
        return 0.0
    total = len(memories.memories)
    corrupted = sum(1 for m in memories.memories.values() if m.is_corrupted())
    return corrupted / total if total else 0.0


def generate_monitoring_metrics(agent) -> Dict[str, float]:
    return {
        "sri": compute_sri(agent),
        "nds": compute_nds(agent),
        "vsd": compute_vsd(agent),
        "mce": compute_mce(agent),
    }
