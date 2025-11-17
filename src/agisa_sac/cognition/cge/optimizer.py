# In agisa_sac/cognition/cge/optimizer.py
import asyncio
from datetime import datetime
from typing import Dict, Any
from hyperopt import fmin, tpe, hp, Trials, space_eval
from cognee.memory.hierarchical.config import MemoryGenome
from agisa_sac.cognition.cge.evaluation import evaluate_memory_system


class CognitiveGradientEngine:
    """
    Optimizes an agent's MemoryGenome using Bayesian optimization (TPE).

    This engine searches over constrained genome parameter spaces to find
    configurations that minimize a loss function (improve task performance).
    """

    def __init__(self, agent_id: str, max_evals: int = 8):
        """
        Initialize the CGE optimizer.

        Args:
            agent_id: Unique identifier for the agent being optimized
            max_evals: Maximum number of evaluations (reduced for fast cycles)
        """
        self.agent_id = agent_id
        self.max_evals = max_evals
        self.trials = Trials()

        # Define search space with biological constraints
        self.space = {
            "sensory_buffer_capacity": hp.quniform("sbc", 50, 500, 25),
            "working_memory_limit": hp.choice("wml", [5, 7, 9, 11]),
            "decay_constant": hp.quniform("dc", 100, 1000, 50),
            "emotional_weight_multiplier": hp.uniform("ewm", 1.0, 5.0),
            "episodic_salience_threshold": hp.uniform("est", 0.1, 0.9),
        }

    async def optimize(self) -> MemoryGenome:
        """
        Run async hyperparameter optimization to find the best genome.

        Returns:
            An optimized MemoryGenome instance
        """
        loop = asyncio.get_event_loop()

        def objective(params):
            """Objective function compatible with hyperopt (synchronous)"""
            return asyncio.run_coroutine_threadsafe(
                evaluate_memory_system(self.agent_id, params), loop
            ).result()

        # Run optimization
        best_params = fmin(
            fn=objective,
            space=self.space,
            algo=tpe.suggest,
            max_evals=self.max_evals,
            trials=self.trials,
            show_progressbar=False,
        )

        # Evaluate the space to get actual values
        evaluated_params = space_eval(self.space, best_params)

        # Merge with defaults for any unoptimized parameters
        base_genome = MemoryGenome().model_dump()
        final_params = {**base_genome, **evaluated_params}

        # Create validated genome
        genome = MemoryGenome(**final_params)

        # Persist the optimized profile
        await self._save_profile(genome)

        return genome

    async def _save_profile(self, genome: MemoryGenome):
        """
        Persist the optimized genome to storage.

        Args:
            genome: The optimized MemoryGenome to persist
        """
        from agisa_sac.persistence.firestore import FirestoreClient

        client = FirestoreClient()
        await client.update_document(
            f"agents/{self.agent_id}",
            {
                "cognitive_profile": genome.model_dump(),
                "profile_version": datetime.utcnow().isoformat(),
            },
        )
