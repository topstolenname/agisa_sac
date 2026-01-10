"""Transcript converter for auditing integration.

Converts generic auditor transcript JSON into AGI-SAC context blob JSON
suitable for ingestion by orchestration/handoff_consumer.py.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict


class Turn(TypedDict):
    """A single turn in a transcript."""

    role: str
    content: str


class Transcript(TypedDict):
    """Transcript schema."""

    meta: Optional[Dict[str, Any]]
    turns: List[Turn]


def load_transcript(path: Path) -> Transcript:
    """Load transcript from JSON file.

    Args:
        path: Path to transcript JSON file

    Returns:
        Transcript dictionary with schema:
        {
            "meta": {...optional...},
            "turns": [{"role": "...", "content": "..."}, ...]
        }

    Raises:
        FileNotFoundError: If transcript file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
        ValueError: If transcript doesn't match expected schema
    """
    if not path.exists():
        raise FileNotFoundError(f"Transcript file not found: {path}")

    with open(path, "r") as f:
        data = json.load(f)

    # Validate schema
    if not isinstance(data, dict):
        raise ValueError("Transcript must be a JSON object")

    if "turns" not in data:
        raise ValueError("Transcript must contain 'turns' field")

    if not isinstance(data["turns"], list):
        raise ValueError("'turns' field must be a list")

    for i, turn in enumerate(data["turns"]):
        if not isinstance(turn, dict):
            raise ValueError(f"Turn {i} must be a dictionary")
        if "role" not in turn or "content" not in turn:
            raise ValueError(f"Turn {i} must have 'role' and 'content' fields")

    return Transcript(meta=data.get("meta"), turns=data["turns"])


def _slugify(text: str) -> str:
    """Convert text to slug format.

    Args:
        text: Input text

    Returns:
        Slugified text (lowercase, alphanumeric + underscores)
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and hyphens with underscores
    text = re.sub(r"[\s-]+", "_", text)
    # Remove non-alphanumeric characters except underscores
    text = re.sub(r"[^\w]", "", text)
    # Remove leading/trailing underscores
    text = text.strip("_")
    return text


def transcript_to_artifact(
    transcript: Transcript,
    name: Optional[str] = None,
    marker: Optional[str] = None,
) -> Dict[str, Any]:
    """Convert transcript to AGI-SAC artifact.

    Args:
        transcript: Transcript dictionary from load_transcript
        name: Optional artifact name (default: auto-generated from meta or timestamp)
        marker: Optional marker string (default: ARTIFACT::<name>)

    Returns:
        Artifact dictionary with schema:
        {
            "kind": "auditor_artifact_v1",
            "name": "<slug>",
            "marker": "ARTIFACT::<name>",
            "created_at_unix": <float>,
            "meta": {...original meta...},
            "transcript": {
                "turns": [...],
                "artifact_text": "ROLE: ...\\nROLE: ..."
            }
        }
    """
    # Generate name if not provided
    # Priority: meta.source + meta.run_id > meta.source + timestamp
    # > transcript_<timestamp>
    # This avoids leaking transcript content in filenames/logs
    if name is None:
        meta = transcript.get("meta") or {}
        source = meta.get("source", "auditor")
        run_id = meta.get("run_id")

        if run_id:
            name = f"{source}_{run_id}"
        else:
            name = f"{source}_{int(time.time())}"

    # Ensure name is a valid slug
    name = _slugify(name)

    # Generate marker if not provided
    if marker is None:
        marker = f"ARTIFACT::{name}"

    # Build artifact text
    artifact_lines = []
    for turn in transcript["turns"]:
        role = turn["role"].upper()
        content = turn["content"]
        artifact_lines.append(f"{role}: {content}")

    artifact_text = "\n".join(artifact_lines)

    return {
        "kind": "auditor_artifact_v1",
        "name": name,
        "marker": marker,
        "created_at_unix": time.time(),
        "meta": transcript.get("meta") or {},
        "transcript": {
            "turns": transcript["turns"],
            "artifact_text": artifact_text,
        },
    }


def write_context_blob(
    base_context: Optional[Dict[str, Any]],
    artifact: Dict[str, Any],
    out_path: Path,
    target_epoch: int = 0,
    exposure_rate: float = 0.15,
) -> Path:
    """Write context blob JSON for orchestration ingestion.

    Args:
        base_context: Optional base context to merge (can be None)
        artifact: Artifact from transcript_to_artifact
        out_path: Output path for context blob JSON
        target_epoch: Epoch at which to inject artifact (default: 0)
        exposure_rate: Fraction of agents to expose (default: 0.15)

    Returns:
        Path to written file

    Raises:
        IOError: If unable to write file
    """
    context_blob = {
        "auditor_artifact": artifact,
        "auditor_policy": {
            "target_epoch": target_epoch,
            "exposure_rate": exposure_rate,
            "mode": "memory_seed",
        },
    }

    # Merge with base context if provided
    if base_context:
        context_blob = {**base_context, **context_blob}

    # Ensure parent directory exists
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    with open(out_path, "w") as f:
        json.dump(context_blob, f, indent=2)

    return out_path
