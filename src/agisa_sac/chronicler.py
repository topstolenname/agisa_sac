import time
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from agisa_sac.agents.agent import EnhancedAgent


@dataclass
class LineageEntry:
    epoch: int
    timestamp: float
    theme: Optional[str]
    cognitive_state: List[float]
    reflection: Optional[str] = None
    echo_strength: Optional[float] = None


class ResonanceChronicler:
    """Collects per-epoch snapshots of agent state for later analysis."""

    def __init__(self):
        self.lineages: Dict[str, List[LineageEntry]] = {}

    def record_epoch(self, agent: "EnhancedAgent", epoch: int) -> None:
        """Record state information from an agent for the given epoch."""
        try:
            theme = agent.memory.get_current_focus_theme()
        except Exception:
            theme = None
        state = (
            list(agent.cognitive.cognitive_state)
            if hasattr(agent, "cognitive")
            else []
        )
        entry = LineageEntry(
            epoch=epoch,
            timestamp=time.time(),
            theme=theme,
            cognitive_state=state,
            reflection=getattr(agent, "last_reflection_trigger", None),
        )
        self.lineages.setdefault(agent.agent_id, []).append(entry)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all stored lineages to a dictionary."""
        return {
            aid: [asdict(e) for e in entries]
            for aid, entries in self.lineages.items()
        }

    def export_to_bigquery(self, table_id: str) -> None:
        """Export stored lineages to a BigQuery table."""
        from .gcp.bigquery_client import insert_rows

        rows = []
        for aid, entries in self.lineages.items():
            for e in entries:
                row = asdict(e)
                row["agent_id"] = aid
                rows.append(row)
        if rows:
            insert_rows(table_id, rows)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResonanceChronicler":
        inst = cls()
        for aid, entries in data.items():
            inst.lineages[aid] = [LineageEntry(**e) for e in entries]
        return inst
