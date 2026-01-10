import os
import warnings
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List, TypedDict, cast, Any

# Use TYPE_CHECKING for chronicler hint
if TYPE_CHECKING:
    from ..chronicler import (
        ResonanceChronicler,
    )  # Adjust if chronicler is moved

class LineageEntry(TypedDict):
    epoch: int
    timestamp_str: str
    theme: str
    strength: float
    reflection: str

class ChronicleExporter:
    """Handles generation and export of formatted narrative outputs."""

    def __init__(self, chronicler: "ResonanceChronicler"):
        if chronicler is None:
            raise ValueError("Chronicler instance required.")
        self.chronicler = chronicler

    def format_lineage_scroll_markdown(
        self, agent_id: str, include_cognitive_state: bool = True
    ) -> Optional[str]:
        """Formats the lineage of a specific agent into a Markdown string."""
        lineage = self.chronicler.lineages.get(agent_id, [])
        if not lineage:
            return None
        report = [
            f"# Resonance Lineage Scroll: {agent_id}\n",
            f"*(Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})*\n",
        ]
        for i, epoch_entry in enumerate(lineage):
            report.append(f"## Agent Epoch {i+1}: Theme '{epoch_entry.theme}'")
            try:
                ts_str = datetime.fromtimestamp(
                    epoch_entry.timestamp
                ).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                ts_str = f"TS {epoch_entry.timestamp}"
            report.append(f"- **Timestamp**: {ts_str}")
            if (
                include_cognitive_state
                and epoch_entry.cognitive_state is not None
            ):
                cog_str = ', '.join([f'{s:.3f}' for s in epoch_entry.cognitive_state])
                report.append(
                    f"- **Cognitive State (R,R,N,S)**: [{cog_str}]"
                )
            if epoch_entry.echo_strength is not None:
                report.append(
                    f"- **Resonance Echo Strength**: {epoch_entry.echo_strength:.4f}"
                )
            if epoch_entry.reflection:
                report.append(f"\n> {epoch_entry.reflection}\n")
            report.append("---")
        return "\n".join(report)

    def generate_echo_manifesto(
        self, agent_id: str, min_echo_strength: float = 0.85
    ) -> Optional[str]:
        """Generates a focused report highlighting significant resonance events."""
        lineage = self.chronicler.lineages.get(agent_id, [])
        if not lineage:
            return None
        manifesto_entries: List[LineageEntry] = []
        for i, entry in enumerate(lineage):
            if (
                entry.echo_strength is not None
                and entry.echo_strength >= min_echo_strength
            ):
                try:
                    ts_str = datetime.fromtimestamp(entry.timestamp).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                except Exception:
                    ts_str = f"TS {entry.timestamp:.0f}"

                # Ensure fields are of correct type
                theme_val = entry.theme if entry.theme is not None else "unknown"
                strength_val = float(entry.echo_strength)
                reflection_val = entry.reflection or "*No reflection*"

                manifesto_entries.append(
                    {
                        "epoch": i + 1,
                        "timestamp_str": ts_str,
                        "theme": theme_val,
                        "strength": strength_val,
                        "reflection": reflection_val,
                    }
                )
        if not manifesto_entries:
            return None
        output = [
            f"# Echo Manifesto: {agent_id}\n",
            f"*(Significant Resonance >= {min_echo_strength:.2f})*\n",
        ]

        # Explicitly cast lambda return to avoid mypy confusion about TypedDict sorting
        sorted_entries = sorted(
            manifesto_entries,
            key=lambda x: cast(float, x["strength"]),
            reverse=True
        )

        for m_entry in sorted_entries:
            output.append(
                f"## Agent Epoch {m_entry['epoch']} "
                f"({m_entry['timestamp_str']}) - "
                f"Strength: {m_entry['strength']:.4f}"
            )
            output.append(f"**Theme:** {m_entry['theme']}")
            output.append(f"> {m_entry['reflection']}")
            output.append("---")
        return "\n".join(output)

    def export_lineage_scroll(
        self,
        agent_id: str,
        directory: str = "./scrolls",
        filename: Optional[str] = None,
    ) -> Optional[str]:
        """Generates and saves the lineage scroll Markdown file."""
        scroll_content = self.format_lineage_scroll_markdown(agent_id)
        if scroll_content is None:
            print(f"No lineage for {agent_id}.")
            return None
        if filename is None:
            filename = f"{agent_id}_lineage_scroll.md"
            filepath = os.path.join(directory, filename)
        try:
            os.makedirs(directory, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(scroll_content)
            print(f"Scroll saved: {filepath}")
            return filepath
        except OSError as e:
            warnings.warn(
                f"Failed save scroll {agent_id}: {e}", RuntimeWarning
            )
            return None

    def export_echo_manifesto(
        self,
        agent_id: str,
        directory: str = "./manifestos",
        filename: Optional[str] = None,
        min_echo_strength: float = 0.85,
    ) -> Optional[str]:
        """Generates and saves the echo manifesto Markdown file."""
        manifesto_content = self.generate_echo_manifesto(
            agent_id, min_echo_strength
        )
        if manifesto_content is None:
            print(f"No echoes >= {min_echo_strength:.2f} for {agent_id}.")
            return None
        if filename is None:
            filename = f"{agent_id}_echo_manifesto.md"
            filepath = os.path.join(directory, filename)
        try:
            os.makedirs(directory, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(manifesto_content)
            print(f"Manifesto saved: {filepath}")
            return filepath
        except OSError as e:
            warnings.warn(
                f"Failed save manifesto {agent_id}: {e}", RuntimeWarning
            )
            return None

    def export_all_scrolls(self, directory: str = "./scrolls"):
        """Exports lineage scrolls for all agents."""
        count = 0
        agent_ids = list(self.chronicler.lineages.keys())
        print(f"Exporting {len(agent_ids)} scrolls to {directory}...")
        for agent_id in agent_ids:
            if self.export_lineage_scroll(agent_id, directory):
                count += 1
        print(f"Exported {count} scrolls.")

    def export_all_manifestos(
        self, directory: str = "./manifestos", min_echo_strength: float = 0.85
    ):
        """Exports echo manifestos for all agents with significant echoes."""
        count = 0
        agent_ids = list(self.chronicler.lineages.keys())
        print(
            f"Exporting manifestos (>{min_echo_strength:.2f}) "
            f"for {len(agent_ids)} agents to {directory}..."
        )
        for agent_id in agent_ids:
            if self.export_echo_manifesto(
                agent_id, directory, min_echo_strength=min_echo_strength
            ):
                count += 1
        print(f"Exported {count} manifestos.")
