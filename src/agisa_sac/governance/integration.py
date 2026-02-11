"""Integration hooks for MCX governance with the AGI-SAC simulation pipeline.

This module provides the "Governance Plane" that can be optionally attached
to a SimulationOrchestrator to enforce governance checks on agent actions.

Usage:
    from agisa_sac.governance.integration import attach_governance

    orchestrator = SimulationOrchestrator(config)
    engine = attach_governance(orchestrator, mode="mcx")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def attach_governance(
    orchestrator: Any,
    mode: str = "mcx",
    cs: Optional[Any] = None,
    cm: Optional[Any] = None,
) -> Any:
    """Attach MCX governance to a SimulationOrchestrator.

    This hooks governance checks into the orchestrator's hook system
    so that agent actions are verified against the governance plane.

    Args:
        orchestrator: The SimulationOrchestrator instance.
        mode: "mcx" for Meta-Concord, "legacy" for no governance.
        cs: Optional ConstraintSet override.
        cm: Optional CapabilityManifest override.

    Returns:
        The GovernanceEngine instance (or None if mode="legacy").
    """
    if mode != "mcx":
        logger.info("Governance mode '%s': no governance attached", mode)
        return None

    from agisa_sac.governance.engine import GovernanceEngine
    from agisa_sac.governance.types import CapabilityManifest, ConstraintSet

    engine = GovernanceEngine(
        cs=cs or ConstraintSet(),
        cm=cm or CapabilityManifest(),
    )

    # Register governance hooks
    def pre_agent_step_hook(
        orchestrator: Any, epoch: int, agent_id: str = "", **kwargs: Any
    ) -> None:
        """Check governance before each agent step."""
        result = engine.check_action(
            action=f"agent_step:{agent_id}",
            context={"scope": agent_id, "actor_id": agent_id, "epoch": epoch},
        )
        if not result.legitimate:
            logger.warning(
                "Governance blocked agent %s step at epoch %d: %s",
                agent_id,
                epoch,
                result.reason,
            )

    def post_epoch_hook(
        orchestrator: Any, epoch: int, **kwargs: Any
    ) -> None:
        """Post-epoch governance check: verify emergency auto-expiry."""
        engine.emergency_manager.check_auto_expiry()

    orchestrator.register_hook("pre_agent_step", pre_agent_step_hook)
    orchestrator.register_hook("post_epoch", post_epoch_hook)

    logger.info("MCX governance attached to orchestrator")
    return engine
