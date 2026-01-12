import json
import random
import time
from collections import defaultdict
from collections.abc import Callable
from typing import Any

import numpy as np

# Import framework version and components using relative paths
try:
    from .. import FRAMEWORK_VERSION
    from ..agents.agent import EnhancedAgent
    from ..analysis.analyzer import AgentStateAnalyzer
    from ..analysis.tda import PersistentHomologyTracker
    from ..chronicler import (
        ResonanceChronicler,
    )  # Assuming chronicler at package root
    from ..utils.logger import get_logger
    from ..utils.message_bus import MessageBus
    from ..utils.metrics import get_metrics
    from .components.social import DynamicSocialGraph

    # Check optional dependencies status (assuming defined in __init__ or config)
    # from . import HAS_CUPY, HAS_SENTENCE_TRANSFORMER
    HAS_CUPY = False  # Placeholder
    HAS_SENTENCE_TRANSFORMER = False  # Placeholder
except ImportError as e:
    raise ImportError(
        f"Could not import necessary AGI-SAC components for Orchestrator: {e}"
    )

logger = get_logger(__name__)


class SimulationOrchestrator:
    """Manages the setup, execution, state, and analysis of the AGI-SAC simulation."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.num_agents = config.get("num_agents", 100)
        self.num_epochs = config.get("num_epochs", 50)
        seed = config.get("random_seed")
        # Seed both global RNGs for backward compatibility
        # and local generator for new code
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.rng = np.random.default_rng(seed)

        self.message_bus = MessageBus()
        self.agent_ids = [f"agent_{i}" for i in range(self.num_agents)]
        # Agent creation requires config details
        self.agents: dict[str, EnhancedAgent] = self._create_agents()
        self.social_graph = DynamicSocialGraph(
            self.num_agents,
            self.agent_ids,
            use_gpu=config.get("use_gpu", False) and HAS_CUPY,
            message_bus=self.message_bus,
        )
        self.chronicler = ResonanceChronicler()
        self.analyzer = AgentStateAnalyzer(self.agents)  # Pass agents dict
        self.tda_tracker = PersistentHomologyTracker(
            max_dimension=config.get("tda_max_dimension", 1)
        )

        self.current_epoch = 0
        self.is_running = False
        self.simulation_start_time: float | None = None
        self.hooks: dict[str, list[Callable[..., Any]]] = defaultdict(list)

        # Initialize metrics collection
        self.metrics = get_metrics()
        self.metrics.update_agent_count(self.num_agents)

        logger.info(
            f"SimulationOrchestrator initialized ({FRAMEWORK_VERSION}) "
            f"with {self.num_agents} agents. "
            f"TDA: {self.tda_tracker.has_tda_lib}, "
            f"GPU: {self.social_graph.use_gpu}"
        )

    def _create_agents(self) -> dict[str, EnhancedAgent]:
        agents = {}
        personalities = self.config.get("personalities", [])
        if len(personalities) != self.num_agents:
            logger.warning(
                f"Personality count mismatch: expected "
                f"{self.num_agents}, got {len(personalities)}. "
                f"Generating random personalities."
            )
            personalities = [
                {
                    "openness": self.rng.uniform(0.3, 0.7),
                    "consistency": self.rng.uniform(0.4, 0.6),
                    "conformity": self.rng.uniform(0.2, 0.8),
                    "curiosity": self.rng.uniform(0.4, 0.9),
                }
                for _ in range(self.num_agents)
            ]
        agent_capacity = self.config.get("agent_capacity", 100)
        use_semantic = (
            self.config.get("use_semantic", True) and HAS_SENTENCE_TRANSFORMER
        )
        for i, agent_id in enumerate(self.agent_ids):
            agents[agent_id] = EnhancedAgent(
                agent_id=agent_id,
                personality=personalities[i],
                capacity=agent_capacity,
                message_bus=self.message_bus,
                use_semantic=use_semantic,
                add_initial_memory=True,
            )
        return agents

    # ... (register_hook, _trigger_hooks, run_epoch, run_simulation,
    # inject_protocol, get_summary_metrics methods as defined in
    # agisa_orchestrator_serialization_v1) ...
    def register_hook(self, hook_point: str, callback: Callable[..., Any]) -> None:
        valid_hooks = {
            "pre_epoch",
            "post_epoch",
            "pre_agent_step",
            "post_agent_step",
            "simulation_end",
            "pre_protocol_injection",
            "post_protocol_injection",
            "tda_phase_transition",
        }
        if hook_point not in valid_hooks:
            logger.warning(
                f"Invalid hook point: {hook_point}. Valid hooks: {valid_hooks}"
            )
            return
        self.hooks[hook_point].append(callback)
        logger.debug(f"Registered hook '{callback.__name__}' for '{hook_point}'")

    def _trigger_hooks(self, hook_point: str, **kwargs: Any) -> None:
        if hook_point in self.hooks:
            for callback in self.hooks[hook_point]:
                try:
                    callback(orchestrator=self, epoch=self.current_epoch, **kwargs)
                except Exception as e:
                    logger.error(
                        f"Hook error at '{hook_point}' ({callback.__name__}): {e}",
                        exc_info=True,
                    )

    def run_epoch(self) -> None:
        if not self.is_running:
            logger.warning("Attempted to run epoch but simulation is not running")
            return

        epoch_start_time = time.perf_counter()
        self._trigger_hooks("pre_epoch")
        situational_entropy = self.rng.uniform(0.1, 0.7)
        agent_order = list(self.agents.keys())
        self.rng.shuffle(agent_order)
        cognitive_states_for_tda = []
        for agent_id in agent_order:
            agent = self.agents.get(agent_id)
            if not agent:
                continue
            self._trigger_hooks("pre_agent_step", agent_id=agent_id)
            peer_influence = self.social_graph.get_peer_influence_for_agent(
                agent_id, normalize=True
            )
            query = f"Epoch {self.current_epoch+1} status. E:{situational_entropy:.2f}"
            agent.simulation_step(situational_entropy, peer_influence, query)
            self.chronicler.record_epoch(agent, self.current_epoch)
            self.metrics.record_agent_interaction()
            if (
                hasattr(agent, "cognitive")
                and agent.cognitive.cognitive_state is not None
            ):
                cognitive_states_for_tda.append(agent.cognitive.cognitive_state)
            self._trigger_hooks("post_agent_step", agent_id=agent_id)
        # TDA
        tda_run_freq = self.config.get("tda_run_frequency", 1)
        if self.tda_tracker and (self.current_epoch + 1) % tda_run_freq == 0:
            if len(cognitive_states_for_tda) > 1:
                point_cloud = np.array(cognitive_states_for_tda)
                max_radius = self.config.get("tda_max_radius", None)

                # Measure TDA computation time
                tda_start = time.perf_counter()
                diagrams = self.tda_tracker.compute_persistence(
                    point_cloud, max_radius=max_radius
                )
                tda_duration = time.perf_counter() - tda_start
                self.metrics.record_tda_computation(tda_duration)

                if diagrams is not None:
                    # Record TDA features
                    for dim, diagram in enumerate(diagrams):
                        if diagram is not None and len(diagram) > 0:
                            self.metrics.update_tda_features(dim, len(diagram))
                    distance_metric = self.config.get(
                        "tda_distance_metric", "bottleneck"
                    )
                    comparison_dim = self.config.get("tda_comparison_dimension", 1)
                    threshold = self.config.get("tda_transition_threshold", 0.2)
                    transition_detected, distance = (
                        self.tda_tracker.detect_phase_transition(
                            comparison_dimension=comparison_dim,
                            distance_metric=distance_metric,
                            threshold=threshold,
                        )
                    )
                    if transition_detected:
                        logger.warning(
                            f"TDA Phase transition detected at "
                            f"Epoch {self.current_epoch+1}: "
                            f"Dimension={comparison_dim}, "
                            f"Distance={distance:.3f}, "
                            f"Threshold={threshold}"
                        )
                        self._trigger_hooks(
                            "tda_phase_transition",
                            dimension=comparison_dim,
                            metric=distance_metric,
                            distance=distance,
                        )
            else:
                self.tda_tracker.persistence_diagrams_history.append(
                    None
                )  # Keep history aligned
        # Communities
        community_check_freq = self.config.get("community_check_frequency", 5)
        if (self.current_epoch + 1) % community_check_freq == 0:
            self.social_graph.detect_communities()
        self._trigger_hooks("post_epoch")
        epoch_duration = time.perf_counter() - epoch_start_time

        # Record metrics
        self.metrics.record_epoch(epoch_duration)
        self.metrics.update_system_resources()

        log_freq = self.config.get("epoch_log_frequency", 10)
        if (self.current_epoch + 1) % log_freq == 0 or self.current_epoch == 0:
            logger.info(
                f"Epoch {self.current_epoch+1}/{self.num_epochs} "
                f"completed in {epoch_duration:.2f}s"
            )

    def run_simulation(
        self, num_epochs: int | None = None
    ) -> dict[str, Any]:
        run_epochs = num_epochs if num_epochs is not None else self.num_epochs
        if run_epochs <= 0:
            logger.warning("No epochs to run (run_epochs <= 0)")
            return {
                "num_agents": self.num_agents,
                "num_epochs": 0,
                "satori_events": [],
                "duration": 0.0,
            }
        logger.info(f"Starting simulation run with {run_epochs} epochs")
        self.is_running = True
        self.simulation_start_time = time.perf_counter()
        start_epoch = self.current_epoch
        for epoch in range(start_epoch, start_epoch + run_epochs):
            if epoch >= self.num_epochs:
                logger.info(
                    f"Reached configured max epochs ({self.num_epochs}). "
                    f"Stopping simulation."
                )
                break
            self.current_epoch = epoch
            self.run_epoch()
        self.is_running = False
        assert self.simulation_start_time is not None  # Set at start of run
        total_duration = time.perf_counter() - self.simulation_start_time
        logger.info(
            f"Simulation run complete: {run_epochs} epochs "
            f"in {total_duration:.2f} seconds "
            f"({total_duration/run_epochs:.2f}s/epoch)"
        )
        self._trigger_hooks("simulation_end")

        # Return simulation results summary
        summary = self.analyzer.summarize()
        return {
            "num_agents": self.num_agents,
            "num_epochs": self.current_epoch,
            "satori_events": summary.get("satori_events", []),
            "duration": total_duration,
        }

    def inject_protocol(self, protocol_name: str, parameters: dict[str, Any]) -> None:
        # ... (logic as defined in agisa_orchestrator_protocol_v1) ...
        logger.info(
            f"Injecting protocol '{protocol_name}' with parameters: {parameters}"
        )
        self._trigger_hooks(
            "pre_protocol_injection",
            protocol_name=protocol_name,
            parameters=parameters,
        )
        if protocol_name == "divergence_stress":
            target_agents = self._select_agents_for_protocol(parameters)
            if not target_agents:
                logger.warning("No agents selected for divergence_stress protocol")
                return
            heuristic_mult_range = parameters.get(
                "heuristic_multiplier_range", (0.5, 0.8)
            )
            counter_narrative = parameters.get("counter_narrative", "Ghosts...")
            narrative_importance = parameters.get("narrative_importance", 0.9)
            narrative_theme = parameters.get("narrative_theme", "divergence_seed")
            logger.info(f"Applying divergence stress to {len(target_agents)} agents")
            modified_count = 0
            for agent in target_agents:
                try:
                    multiplier = self.rng.uniform(*heuristic_mult_range)
                    agent.cognitive.heuristics *= multiplier
                    agent.cognitive.heuristics = 1 / (
                        1 + np.exp(-agent.cognitive.heuristics)
                    )
                    agent.cognitive.heuristics = np.clip(
                        agent.cognitive.heuristics, 0.1, 0.9
                    )
                    agent.memory.add_memory(
                        content={
                            "type": "divergence_seed",
                            "source": "SYS_PROTO",
                            "text": counter_narrative,
                            "theme": narrative_theme,
                            "timestamp": time.time(),
                        },
                        importance=narrative_importance,
                    )
                    modified_count += 1
                except Exception as e:
                    logger.error(
                        f"Failed to apply stress to agent " f"{agent.agent_id}: {e}",
                        exc_info=True,
                    )
            logger.info(
                f"Divergence stress applied to "
                f"{modified_count}/{len(target_agents)} agents"
            )
        elif protocol_name == "satori_probe":
            threshold = parameters.get(
                "threshold", self.config.get("satori_threshold_analyzer", 0.88)
            )
            ratio = (
                self.analyzer.compute_satori_wave_ratio(threshold=threshold)
                if self.analyzer
                else 0.0
            )
            logger.info(
                f"Satori probe result: ratio={ratio:.3f} (threshold={threshold})"
            )
        elif protocol_name == "echo_fusion":
            logger.warning("Echo Fusion protocol not yet implemented")
        elif protocol_name == "satori_lattice":
            logger.warning("Satori Lattice protocol not yet implemented")
        else:
            logger.error(f"Unknown protocol: {protocol_name}")
        self._trigger_hooks(
            "post_protocol_injection",
            protocol_name=protocol_name,
            parameters=parameters,
        )

    def get_summary_metrics(
        self, satori_threshold: float | None = None
    ) -> dict[str, Any]:
        if not self.analyzer:
            return {"error": "Analyzer N/A."}

        threshold = (
            satori_threshold
            if satori_threshold is not None
            else self.config.get("satori_threshold_analyzer", 0.88)
        )
        return self.analyzer.summarize(satori_threshold=threshold)

    def save_state(
        self,
        filepath: str,
        include_memory_embeddings: bool = False,
        resonance_history_limit: int | None = 100,
    ) -> bool:
        """Serialize orchestrator state to disk using JSON."""
        if self.is_running:
            logger.warning("Saving state while simulation is running")
        try:
            logger.info(f"Saving simulation state to {filepath}")
            state = {
                "framework_version": FRAMEWORK_VERSION,
                "config": self.config,
                "current_epoch": self.current_epoch,
                "agents_state": {
                    aid: agent.to_dict(
                        include_memory_embeddings=include_memory_embeddings,
                        resonance_history_limit=resonance_history_limit,
                    )
                    for aid, agent in self.agents.items()
                },
                "social_graph_state": self.social_graph.to_dict(),
                "chronicler_state": self.chronicler.to_dict(),
                "tda_tracker_state": (
                    self.tda_tracker.to_dict() if self.tda_tracker else None
                ),
                # Note: Random states not saved for security (JSON format)
                # Re-seed manually if deterministic replay is needed
            }
            with open(filepath, "w") as f:
                json.dump(state, f, indent=2)
            logger.info(f"State saved successfully to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save state to {filepath}: {e}", exc_info=True)
            return False

    def load_state(self, filepath: str) -> bool:
        """Load orchestrator state from disk using JSON."""
        if self.is_running:
            logger.warning("Loading state while simulation is running")
        try:
            logger.info(f"Loading simulation state from {filepath}")
            with open(filepath) as f:
                state = json.load(f)

            # Restore config first to ensure other components are initialized correctly
            self.config = state.get("config", self.config)

            self.current_epoch = state.get("current_epoch", 0)
            self.agents = {
                aid: EnhancedAgent.from_dict(a, self.message_bus)
                for aid, a in state.get("agents_state", {}).items()
            }

            # Update agent count and IDs from loaded state
            self.num_agents = len(self.agents)
            self.agent_ids = list(self.agents.keys())
            self.metrics.update_agent_count(self.num_agents)

            # Initialize and then load social graph state
            self.social_graph = DynamicSocialGraph(
                self.num_agents,
                self.agent_ids,
                use_gpu=self.config.get("use_gpu", False) and HAS_CUPY,
                message_bus=self.message_bus,
            )
            if "social_graph_state" in state:
                self.social_graph.load_state(state["social_graph_state"])

            self.chronicler = ResonanceChronicler.from_dict(
                state.get("chronicler_state", {})
            )

            max_dim = self.config.get("tda_max_dimension", 1)
            self.tda_tracker = PersistentHomologyTracker(max_dimension=max_dim)
            if state.get("tda_tracker_state"):
                self.tda_tracker.load_state(state["tda_tracker_state"])

            self.analyzer = AgentStateAnalyzer(self.agents)

            logger.info(
                f"State loaded successfully from {filepath} "
                f"at epoch {self.current_epoch}"
            )
            return True
        except FileNotFoundError:
            logger.error(f"State file not found: {filepath}")
            return False
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(
                f"Failed to parse state file {filepath} or key missing: {e}",
                exc_info=True,
            )
            return False
        except Exception as e:
            logger.error(f"Failed to load state from {filepath}: {e}", exc_info=True)
            return False

    def _select_agents_for_protocol(
        self, parameters: dict[str, Any]
    ) -> list[EnhancedAgent]:
        selection_method = parameters.get("selection_method", "percentage")
        agent_list = list(self.agents.values())
        if not agent_list:
            logger.warning("No agents available for protocol selection")
            return []
        if selection_method == "percentage":
            percentage = parameters.get("percentage", 0.1)
            count = max(1, int(self.num_agents * percentage))
            selected_count = min(count, self.num_agents)
            logger.debug(
                f"Selecting {selected_count} agents "
                f"({percentage*100:.1f}%) for protocol"
            )
            indices = self.rng.choice(len(agent_list), size=selected_count, replace=False)
            return [agent_list[i] for i in indices]
        logger.warning(
            f"Unknown selection method '{selection_method}'. Returning all agents."
        )
        return agent_list
