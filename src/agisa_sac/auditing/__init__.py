"""Auditing integration for AGI-SAC.

This package provides utilities for converting generic auditor transcripts
into AGI-SAC context blobs for distributed ingestion.
"""

from .transcript_converter import (
    load_transcript,
    transcript_to_artifact,
    write_context_blob,
)

__all__ = [
    "load_transcript",
    "transcript_to_artifact",
    "write_context_blob",
]
