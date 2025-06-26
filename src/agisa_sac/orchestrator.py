import numpy as np
import time
import json
import pickle
import random
import warnings
from collections import defaultdict
from typing import Dict, List, Optional, Any, Callable

# Import framework version and components using relative paths
try:
    from . import FRAMEWORK_VERSION
    from .agent import EnhancedAgent
    from .utils.message_bus import MessageBus
    from .components.social import DynamicSocialGraph
    from .chronicler import ResonanceChronicler # Assuming chronicler moved to top level
    from .analysis.analyzer import AgentStateAnalyzer
    from .analysis.tda import PersistentHomologyTracker
    # Check optional dependencies status (assuming defined in __init__ or config)
    # from . import HAS_CUPY, HAS_SENTENCE_TRANSFORMER
    HAS_CUPY = False # Placeholder
    HAS_SENTENCE_TRANSFORMER = False # Placeholder
except ImportError as e:
    raise ImportError(f"Could not import necessary AGI-SAC components for Orchestrator: {e}")


class SimulationOrchestrator:
    """ Manages the setup, execution, state, and analysis of the AGI-SAC simulation. """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.num_agents = config.get('num_agents', 100)
        self.num_epochs = config.get('num_epochs', 50)
        seed = config.get('random_seed')
        if seed is not None: random.seed(seed); np.random.seed(seed)

        self.message_bus = MessageBus()
        self.agent_ids = [f"agent_{i}" for i in range(self.num_agents)]
        # Agent creation requires config details
        self.agents: Dict[str, EnhancedAgent] = self._create_agents()
        self.social_graph = DynamicSocialGraph(self.num_agents, self.agent_ids, use_gpu=config.get('use_gpu', False) and HAS_CUPY, message_bus=self.message_bus)
        self.chronicler = ResonanceChronicler()
        self.analyzer = AgentStateAnalyzer(self.agents) # Pass agents dict
        self.tda_tracker = PersistentHomologyTracker(max_dimension=config.get('tda_max_dimension', 1))

        self.current_epoch = 0; self.is_running = False; self.simulation_start_time = None
        self.hooks: Dict[str, List[Callable]] = defaultdict(list)
        print(f"SimulationOrchestrator initialized ({FRAMEWORK_VERSION}) with {self.num_agents} agents. TDA: {self.tda_tracker.has_tda_lib}, GPU: {self.social_graph.use_gpu}")


    def _create_agents(self) -> Dict[str, EnhancedAgent]:
        agents = {}; personalities = self.config.get('personalities', [])
        if len(personalities) != self.num_agents:
             warnings.warn(f"Personality count mismatch. Generating random.", RuntimeWarning); personalities = [{"openness": random.uniform(0.3, 0.7), "consistency": random.uniform(0.4, 0.6),"conformity": random.uniform(0.2, 0.8), "curiosity": random.uniform(0.4, 0.9)} for _ in range(self.num_agents)]
        agent_capacity = self.config.get('agent_capacity', 100); use_semantic = self.config.get('use_semantic', True) and HAS_SENTENCE_TRANSFORMER
        for i, agent_id in enumerate(self.agent_ids):
             agents[agent_id] = EnhancedAgent(agent_id=agent_id, personality=personalities[i], capacity=agent_capacity, message_bus=self.message_bus, use_semantic=use_semantic, add_initial_memory=True)
        return agents

    # ... (register_hook, _trigger_hooks, run_epoch, run_simulation, inject_protocol, get_summary_metrics methods as defined in agisa_orchestrator_serialization_v1) ...
    def register_hook(self, hook_point: str, callback: Callable):
        valid_hooks = {'pre_epoch', 'post_epoch', 'pre_agent_step', 'post_agent_step', 'simulation_end', 'pre_protocol_injection', 'post_protocol_injection', 'tda_phase_transition'};
        if hook_point not in valid_hooks:
            warnings.warn(f"Invalid hook point: {hook_point}", RuntimeWarning)
            return
        self.hooks[hook_point].append(callback)
    def _trigger_hooks(self, hook_point: str, **kwargs):
        if hook_point in self.hooks:
            for callback in self.hooks[hook_point]:
                try:
                    callback(orchestrator=self, epoch=self.current_epoch, **kwargs)
                except Exception as e:
                    warnings.warn(
                        f"Hook error '{hook_point}' ({callback.__name__}): {e}",
                        RuntimeWarning,
                    )
    def run_epoch(self):
        if not self.is_running: warnings.warn("Sim not running.", RuntimeWarning); return; epoch_start_time = time.time(); self._trigger_hooks('pre_epoch'); situational_entropy = random.uniform(0.1, 0.7)
        agent_order = list(self.agents.keys()); random.shuffle(agent_order); cognitive_states_for_tda = []
        for agent_id in agent_order:
            agent = self.agents.get(agent_id);
            if not agent: continue
            self._trigger_hooks('pre_agent_step', agent_id=agent_id); peer_influence = self.social_graph.get_peer_influence_for_agent(agent_id, normalize=True); query = f"Epoch {self.current_epoch+1} status. E:{situational_entropy:.2f}"
            agent.simulation_step(situational_entropy, peer_influence, query); self.chronicler.record_epoch(agent, self.current_epoch);
            if hasattr(agent, 'cognitive') and agent.cognitive.cognitive_state is not None: cognitive_states_for_tda.append(agent.cognitive.cognitive_state)
            self._trigger_hooks('post_agent_step', agent_id=agent_id)
        # TDA
        tda_run_freq = self.config.get('tda_run_frequency', 1)
        if self.tda_tracker and (self.current_epoch + 1) % tda_run_freq == 0:
            if len(cognitive_states_for_tda) > 1:
                 point_cloud = np.array(cognitive_states_for_tda); max_radius = self.config.get('tda_max_radius', None)
                 diagrams = self.tda_tracker.compute_persistence(point_cloud, max_radius=max_radius)
                 if diagrams is not None:
                      distance_metric = self.config.get('tda_distance_metric', 'bottleneck'); comparison_dim = self.config.get('tda_comparison_dimension', 1); threshold = self.config.get('tda_transition_threshold', 0.2)
                      transition_detected, distance = self.tda_tracker.detect_phase_transition(comparison_dimension=comparison_dim, distance_metric=distance_metric, threshold=threshold)
                      if transition_detected: print(f"!!! Epoch {self.current_epoch+1}: TDA Phase transition (Dim={comparison_dim}, Dist={distance:.3f} > {threshold}) !!!"); self._trigger_hooks('tda_phase_transition', dimension=comparison_dim, metric=distance_metric, distance=distance)
            else: self.tda_tracker.persistence_diagrams_history.append(None) # Keep history aligned
        # Communities
        community_check_freq = self.config.get('community_check_frequency', 5)
        if (self.current_epoch + 1) % community_check_freq == 0: self.social_graph.detect_communities()
        self._trigger_hooks('post_epoch'); epoch_duration = time.time() - epoch_start_time
        log_freq = self.config.get('epoch_log_frequency', 10)
        if (self.current_epoch + 1) % log_freq == 0 or self.current_epoch == 0: print(f"--- Epoch {self.current_epoch+1}/{self.num_epochs} completed [{epoch_duration:.2f}s] ---")
    def run_simulation(self, num_epochs: Optional[int] = None): # Allow overriding num_epochs
        run_epochs = num_epochs if num_epochs is not None else self.num_epochs
        if run_epochs <= 0: print("No epochs to run."); return
        print(f"\n--- Starting Simulation Run ({run_epochs} Epochs) ---"); self.is_running = True; self.simulation_start_time = time.time(); start_epoch = self.current_epoch
        for epoch in range(start_epoch, start_epoch + run_epochs):
             if epoch >= self.num_epochs: print(f"Reached configured max epochs ({self.num_epochs}). Stopping."); break
             self.current_epoch = epoch; self.run_epoch()
        self.is_running = False; total_duration = time.time() - self.simulation_start_time; print(f"\n--- Simulation Run Complete ({total_duration:.2f} seconds) ---"); self._trigger_hooks('simulation_end')
    def inject_protocol(self, protocol_name: str, parameters: Dict):
        # ... (logic as defined in agisa_orchestrator_protocol_v1) ...
        print(f"Injecting protocol '{protocol_name}'")
        self._trigger_hooks('pre_protocol_injection', protocol_name=protocol_name, parameters=parameters)
        if protocol_name == "divergence_stress":
            target_agents = self._select_agents_for_protocol(parameters)
            if not target_agents:
                print("No agents selected.")
                return
            heuristic_mult_range = parameters.get("heuristic_multiplier_range", (0.5, 0.8))
            counter_narrative = parameters.get("counter_narrative", "Ghosts...")
            narrative_importance = parameters.get("narrative_importance", 0.9)
            narrative_theme = parameters.get("narrative_theme", "divergence_seed")
            print(f"Applying stress to {len(target_agents)} agents...")
            modified_count = 0
            for agent in target_agents:
                try:
                    multiplier = random.uniform(*heuristic_mult_range)
                    agent.cognitive.heuristics *= multiplier
                    agent.cognitive.heuristics = 1 / (1 + np.exp(-agent.cognitive.heuristics))
                    agent.cognitive.heuristics = np.clip(agent.cognitive.heuristics, 0.1, 0.9)
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
                    warnings.warn(f"Stress failed for {agent.agent_id}: {e}", RuntimeWarning)
            print(f"Stress applied to {modified_count} agents.")
        elif protocol_name == "satori_probe": threshold = parameters.get('threshold', self.config.get('satori_threshold_analyzer', 0.88)); ratio = self.analyzer.compute_satori_wave_ratio(threshold=threshold) if self.analyzer else 0.0; print(f"Satori Probe (Thresh {threshold}): {ratio:.3f}");
        elif protocol_name == "echo_fusion": print("Echo Fusion TBD."); pass;
        elif protocol_name == "satori_lattice": print("Satori Lattice TBD."); pass;
        else: warnings.warn(f"Unknown protocol: {protocol_name}", RuntimeWarning);
        self._trigger_hooks('post_protocol_injection', protocol_name=protocol_name, parameters=parameters)
    def get_summary_metrics(self, satori_threshold: Optional[float] = None) -> Dict[str, Any]:
        if not self.analyzer: return {"error": "Analyzer N/A."}; threshold = satori_threshold if satori_threshold is not None else self.config.get('satori_threshold_analyzer', 0.88); return self.analyzer.summarize(satori_threshold=threshold)
    def save_state(self, filepath: str, include_memory_embeddings: bool = False, resonance_history_limit: Optional[int] = 100) -> bool:
        """Serialize orchestrator state to disk."""
        if self.is_running:
            warnings.warn("Saving state while running.", RuntimeWarning)
        try:
            print(f"Saving state to {filepath}...")
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
                "tda_tracker_state": self.tda_tracker.to_dict() if self.tda_tracker else None,
                "random_state": random.getstate(),
                "numpy_random_state": np.random.get_state(),
            }
            with open(filepath, "wb") as f:
                pickle.dump(state, f)
            print("State saved.")
            return True
        except Exception as e:
            warnings.warn(f"Save failed: {e}", category=RuntimeWarning)
            import traceback
            traceback.print_exc()
            return False
        selection_method = parameters.get("selection_method", "percentage"); target_agents = []; agent_list = list(self.agents.values())
        if not agent_list: return []
        if selection_method == "percentage":
            percentage = parameters.get("percentage", 0.1); count = max(1, int(self.num_agents * percentage)); basis = parameters.get("selection_basis", "random")
            if basis == "random": target_agents = random.sample(agent_list, min(count, self.num_agents))
            else: warnings.warn(f"Unsupported basis '{basis}'. Default random.", RuntimeWarning); target_agents = random.sample(agent_list, min(count, self.num_agents))
        else: warnings.warn(f"Unknown selection method '{selection_method}'.", RuntimeWarning)
        print(f"Selected {len(target_agents)} agents for protocol via '{selection_method}'.")
        return target_agents







    def load_state(self, filepath: str) -> bool:
        """Load orchestrator state from disk."""
        if self.is_running:
            warnings.warn("Loading state while running.", RuntimeWarning)
        try:
            print(f"Loading state from {filepath}...")
            with open(filepath, "rb") as f:
                state = pickle.load(f)
            self.current_epoch = state.get("current_epoch", 0)
            self.agents = {
                aid: EnhancedAgent.from_dict(a, self.message_bus)
                for aid, a in state.get("agents_state", {}).items()
            }
            self.social_graph = DynamicSocialGraph(self.num_agents, list(self.agents.keys()), use_gpu=False, message_bus=self.message_bus)
            self.chronicler = ResonanceChronicler.from_dict(state.get("chronicler_state", {}))
            self.tda_tracker = PersistentHomologyTracker(max_dimension=self.config.get('tda_max_dimension', 1))
            if state.get("tda_tracker_state"):
                self.tda_tracker.load_state(state["tda_tracker_state"])
            self.analyzer = AgentStateAnalyzer(self.agents)
            print("State loaded.")
            return True
        except FileNotFoundError:
            warnings.warn(f"Load failed: file not found {filepath}", RuntimeWarning)
            return False
        except Exception as e:
            warnings.warn(f"Load failed: {e}", RuntimeWarning)
            import traceback
            traceback.print_exc()
            return False

    def _select_agents_for_protocol(self, parameters: Dict) -> List[EnhancedAgent]:
        selection_method = parameters.get("selection_method", "percentage")
        agent_list = list(self.agents.values())
        if not agent_list:
            return []
        if selection_method == "percentage":
            percentage = parameters.get("percentage", 0.1)
            count = max(1, int(self.num_agents * percentage))
            return random.sample(agent_list, min(count, self.num_agents))
        warnings.warn(f"Unknown selection method '{selection_method}'.", RuntimeWarning)
        return agent_list
