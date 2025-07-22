"""Example Multi-Agent Voice System (Colab-style) using AGI-SAC components."""

import asyncio
import json
import os
import random
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

import numpy as np

# ---------------------------------------------------------------------------
# VoiceEngine
# ---------------------------------------------------------------------------
FRAMEWORK_VERSION = "1.0.0"


class VoiceEngine:
    """Agent voice/style engine with simple evolution logic."""

    def __init__(self, agent_id: str, initial_style: Optional[Dict] = None):
        self.agent_id = agent_id
        self.linguistic_signature = {
            "style_vector": np.random.rand(64) * 0.5 + 0.25,
            "archetype": "neutral",
            "sentence_structure": "declarative",
            "vocabulary_richness": 0.5,
            "personality_traits": ["analytical", "curious"],
            "communication_style": "formal",
            "emotional_baseline": 0.5,
        }
        if initial_style:
            if "style_vector" in initial_style and isinstance(initial_style["style_vector"], list):
                initial_style["style_vector"] = np.array(initial_style["style_vector"])
            self.linguistic_signature.update(initial_style)

    def generate_response(self, prompt: str, context: Dict | None = None) -> str:
        style = self.linguistic_signature.get("archetype", "unknown")
        structure = self.linguistic_signature.get("sentence_structure", "simple")
        personality = ", ".join(self.linguistic_signature.get("personality_traits", []))
        context_lines = [line.strip() for line in prompt.strip().splitlines() if line.strip()]
        context_text = context_lines[-1] if context_lines else "prompt"
        response = f"[Agent {self.agent_id}] [{style}/{structure}] "
        response += f"As a {personality} agent: {context_text[:100]}..."
        return response

    def evolve_style(self, influence: Dict):
        if "archetype" in influence and isinstance(influence["archetype"], str):
            self.linguistic_signature["archetype"] = influence["archetype"]
        if "sentence_structure" in influence and isinstance(influence["sentence_structure"], str):
            self.linguistic_signature["sentence_structure"] = influence["sentence_structure"]
        if "vocabulary_richness" in influence and isinstance(
            influence["vocabulary_richness"], (int, float)
        ):
            self.linguistic_signature["vocabulary_richness"] = np.clip(
                influence["vocabulary_richness"], 0.0, 1.0
            )
        if "new_traits" in influence and isinstance(influence["new_traits"], list):
            current = set(self.linguistic_signature.get("personality_traits", []))
            new_traits = set(influence["new_traits"])
            self.linguistic_signature["personality_traits"] = list(current.union(new_traits))[:5]
        shift = influence.get("shift_magnitude", 0.1)
        if influence.get("archetype") == "enlightened":
            shift = 0.2
        vec = self.linguistic_signature["style_vector"]
        if isinstance(vec, np.ndarray):
            noise = (np.random.rand(*vec.shape) - 0.5) * shift
            vec += noise
            norm = np.linalg.norm(vec)
            if norm > 1.0:
                vec /= norm

    def get_style_similarity(self, other: "VoiceEngine") -> float:
        vec1 = self.linguistic_signature["style_vector"]
        vec2 = other.linguistic_signature["style_vector"]
        dot = float(np.dot(vec1, vec2))
        norms = float(np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return dot / norms if norms else 0.0

    def to_dict(self) -> Dict:
        sig = self.linguistic_signature.copy()
        if isinstance(sig.get("style_vector"), np.ndarray):
            sig["style_vector"] = sig["style_vector"].tolist()
        return {"version": FRAMEWORK_VERSION, "linguistic_signature": sig}

    @classmethod
    def from_dict(cls, data: Dict[str, Any], agent_id: str) -> "VoiceEngine":
        instance = cls(agent_id=agent_id)
        sig = data.get("linguistic_signature", {})
        if isinstance(sig.get("style_vector"), list):
            sig["style_vector"] = np.array(sig["style_vector"])
        instance.linguistic_signature.update(sig)
        return instance


# ---------------------------------------------------------------------------
# MultiAPIManager
# ---------------------------------------------------------------------------


@dataclass
class APIResponse:
    content: str
    provider: str
    model: str
    timestamp: datetime
    token_count: Optional[int] = None


class MultiAPIManager:
    """Simplified multi-provider interface."""

    def __init__(self) -> None:
        self.providers = {}
        self.usage_stats = {
            "openai": {"calls": 0, "tokens": 0},
            "anthropic": {"calls": 0, "tokens": 0},
            "google": {"calls": 0, "tokens": 0},
            "local": {"calls": 0, "tokens": 0},
        }

    async def generate_response(
        self, prompt: str, provider: str = "local", model: str = "default"
    ) -> APIResponse:
        self.usage_stats[provider]["calls"] += 1
        if provider == "local" or provider not in self.providers:
            options = [
                f"Local AI response to: {prompt[:50]}...",
                f"Mock AI says something about: {prompt[:50]}...",
            ]
            content = random.choice(options)
            return APIResponse(content, "local", "mock", datetime.now(), len(content.split()))
        try:
            if provider == "openai":
                response = self.providers[provider].chat.completions.create(
                    model=model or "gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                )
                content = response.choices[0].message.content
                tokens = response.usage.total_tokens
            elif provider == "anthropic":
                response = self.providers[provider].messages.create(
                    model=model or "claude-3-sonnet-20240229",
                    max_tokens=150,
                    messages=[{"role": "user", "content": prompt}],
                )
                content = response.content[0].text
                tokens = response.usage.input_tokens + response.usage.output_tokens
            elif provider == "google":
                response = self.providers[provider].generate_content(prompt)
                content = response.text
                tokens = len(content.split())
            else:
                content = "Unsupported provider"
                tokens = 0
            self.usage_stats[provider]["tokens"] += tokens
            return APIResponse(content, provider, model, datetime.now(), tokens)
        except Exception:
            return await self.generate_response(prompt, "local", "fallback")


# ---------------------------------------------------------------------------
# Agent and System
# ---------------------------------------------------------------------------


class Agent:
    def __init__(
        self, agent_id: str, voice_style: Optional[Dict] = None, preferred_api: str = "local"
    ):
        self.agent_id = agent_id
        self.voice = VoiceEngine(agent_id, voice_style)
        self.preferred_api = preferred_api
        self.memory: List[str] = []
        self.interaction_history: List[Dict[str, Any]] = []
        self.creation_time = datetime.now()
        self.last_evolution = datetime.now()

    async def respond_to(
        self, prompt: str, api_manager: MultiAPIManager, context: Dict | None = None
    ) -> str:
        api_response = await api_manager.generate_response(prompt, self.preferred_api, "default")
        styled = self.voice.generate_response(api_response.content, context)
        self.interaction_history.append(
            {
                "timestamp": datetime.now(),
                "prompt": prompt,
                "raw_response": api_response.content,
                "styled_response": styled,
                "api_used": api_response.provider,
            }
        )
        self.memory.append(f"Responded to: {prompt[:50]}...")
        return styled

    def interact_with_agent(self, other: "Agent", topic: str) -> Dict[str, Any]:
        similarity = self.voice.get_style_similarity(other.voice)
        if similarity > 0.7:
            influence = {"shift_magnitude": 0.05, "new_traits": ["collaborative", "harmonious"]}
        elif similarity < 0.3:
            influence = {
                "shift_magnitude": 0.15,
                "new_traits": ["diverse", "adaptive"],
                "archetype": "eclectic",
            }
        else:
            influence = {"shift_magnitude": 0.1, "new_traits": ["balanced"]}
        self.voice.evolve_style(influence)
        other.voice.evolve_style(influence)
        self.last_evolution = datetime.now()
        other.last_evolution = datetime.now()
        return {
            "agents": [self.agent_id, other.agent_id],
            "topic": topic,
            "style_similarity": similarity,
            "timestamp": datetime.now(),
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "archetype": self.voice.linguistic_signature.get("archetype"),
            "personality_traits": self.voice.linguistic_signature.get("personality_traits"),
            "interactions_count": len(self.interaction_history),
            "memory_size": len(self.memory),
            "preferred_api": self.preferred_api,
            "age_hours": (datetime.now() - self.creation_time).total_seconds() / 3600,
            "last_evolution": self.last_evolution.strftime("%Y-%m-%d %H:%M:%S"),
        }


class MultiAgentSystem:
    def __init__(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.api_manager = MultiAPIManager()
        self.system_interactions: List[Dict[str, Any]] = []
        self.evolution_history: List[Dict[str, Any]] = []

    def create_agent(
        self, agent_id: str, archetype: str = "neutral", api_provider: str = "local"
    ) -> Agent:
        styles = {
            "analytical": {
                "archetype": "analytical",
                "sentence_structure": "complex",
                "vocabulary_richness": 0.8,
                "personality_traits": ["logical", "methodical", "precise"],
                "communication_style": "formal",
            },
            "creative": {
                "archetype": "creative",
                "sentence_structure": "flowing",
                "vocabulary_richness": 0.9,
                "personality_traits": ["imaginative", "expressive", "intuitive"],
                "communication_style": "casual",
            },
            "practical": {
                "archetype": "practical",
                "sentence_structure": "simple",
                "vocabulary_richness": 0.6,
                "personality_traits": ["efficient", "direct", "solution-focused"],
                "communication_style": "informal",
            },
            "empathetic": {
                "archetype": "empathetic",
                "sentence_structure": "supportive",
                "vocabulary_richness": 0.7,
                "personality_traits": ["caring", "understanding", "emotional"],
                "communication_style": "warm",
            },
            "explorer": {
                "archetype": "explorer",
                "sentence_structure": "questioning",
                "vocabulary_richness": 0.75,
                "personality_traits": ["curious", "adventurous", "open-minded"],
                "communication_style": "enthusiastic",
            },
        }
        style = styles.get(archetype, styles["analytical"])
        agent = Agent(agent_id, style, api_provider)
        self.agents[agent_id] = agent
        return agent

    async def run_simulation(self, steps: int = 5, topics: Optional[List[str]] = None) -> None:
        if not topics:
            topics = [
                "artificial intelligence ethics",
                "climate change solutions",
                "future of work",
                "space exploration",
                "quantum computing",
            ]
        agents = list(self.agents.values())
        if len(agents) < 2:
            return
        for step in range(steps):
            a1, a2 = random.sample(agents, 2)
            topic = random.choice(topics)
            interaction = a1.interact_with_agent(a2, topic)
            self.system_interactions.append(interaction)
            r1 = await a1.respond_to(f"Thoughts on {topic}?", self.api_manager)
            r2 = await a2.respond_to(f"Thoughts on {topic}?", self.api_manager)
            print(f"{a1.agent_id}: {r1}")
            print(f"{a2.agent_id}: {r2}\n")
            self.evolution_history.append(
                {
                    "step": step + 1,
                    "agents_state": {aid: ag.get_stats() for aid, ag in self.agents.items()},
                }
            )
            time.sleep(0.2)

    def get_system_stats(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.agents),
            "total_interactions": len(self.system_interactions),
            "api_usage": self.api_manager.usage_stats,
            "agents": [ag.get_stats() for ag in self.agents.values()],
            "evolution_steps": len(self.evolution_history),
        }


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def export_system_state(system: MultiAgentSystem, filename: str = "agent_system_state.json") -> str:
    data = {
        "timestamp": datetime.now().isoformat(),
        "framework_version": FRAMEWORK_VERSION,
        "agents": {
            aid: {"voice_engine": ag.voice.to_dict(), "stats": ag.get_stats()}
            for aid, ag in system.agents.items()
        },
        "interactions": [
            {
                "agents": i["agents"],
                "topic": i["topic"],
                "similarity": i["style_similarity"],
                "timestamp": i["timestamp"].isoformat(),
            }
            for i in system.system_interactions
        ],
        "evolution_history": system.evolution_history,
        "api_usage": system.api_manager.usage_stats,
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    return filename


async def run_demo() -> MultiAgentSystem:
    system = MultiAgentSystem()
    system.create_agent("Alice", "analytical")
    system.create_agent("Bob", "creative")
    system.create_agent("Charlie", "practical")
    await system.run_simulation(steps=3)
    export_system_state(system)
    stats = system.get_system_stats()
    print(json.dumps(stats, indent=2))
    return system


if __name__ == "__main__":
    asyncio.run(run_demo())
