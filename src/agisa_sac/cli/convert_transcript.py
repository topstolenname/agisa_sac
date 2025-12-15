"""Convert transcript command handler."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ..auditing import (
    load_transcript,
    transcript_to_artifact,
    write_context_blob,
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


def convert_transcript(args: argparse.Namespace) -> int:
    """Convert auditor transcript to AGI-SAC context blob.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_path = Path(args.input)
    output_path = Path(args.output)

    # Load transcript
    try:
        logger.info(f"Loading transcript from: {input_path}")
        transcript = load_transcript(input_path)
        logger.info(f"Loaded transcript with {len(transcript['turns'])} turns")
    except Exception as e:
        logger.error(f"Failed to load transcript: {e}", exc_info=True)
        print(f"Error loading transcript: {e}", file=sys.stderr)
        return 1

    # Convert to artifact
    try:
        logger.info("Converting transcript to artifact")
        artifact = transcript_to_artifact(
            transcript, name=args.name, marker=args.marker
        )
        logger.info(f"Created artifact: {artifact['name']}")
    except Exception as e:
        logger.error(f"Failed to convert transcript: {e}", exc_info=True)
        print(f"Error converting transcript: {e}", file=sys.stderr)
        return 1

    # Write context blob
    try:
        logger.info(f"Writing context blob to: {output_path}")
        written_path = write_context_blob(
            base_context=None,
            artifact=artifact,
            out_path=output_path,
            target_epoch=args.target_epoch,
            exposure_rate=args.exposure_rate,
        )
        logger.info(f"Successfully wrote context blob to: {written_path}")
    except Exception as e:
        logger.error(f"Failed to write context blob: {e}", exc_info=True)
        print(f"Error writing context blob: {e}", file=sys.stderr)
        return 1

    # Print success message
    print(f"Successfully converted transcript to context blob")
    print(f"Written to: {written_path}")
    print(f"Artifact name: {artifact['name']}")
    print(f"Marker: {artifact['marker']}")

    return 0
