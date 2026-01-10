"""Convert transcript command handler."""

from __future__ import annotations

import argparse
import json
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

    # Load transcript, convert, and write context blob
    try:
        logger.info(f"Loading transcript from: {input_path}")
        transcript = load_transcript(input_path)
        logger.info(f"Loaded transcript with {len(transcript['turns'])} turns")

        logger.info("Converting transcript to artifact")
        artifact = transcript_to_artifact(
            transcript, name=args.name, marker=args.marker
        )
        logger.info(f"Created artifact: {artifact['name']}")

        logger.info(f"Writing context blob to: {output_path}")
        written_path = write_context_blob(
            base_context=None,
            artifact=artifact,
            out_path=output_path,
            target_epoch=args.target_epoch,
            exposure_rate=args.exposure_rate,
        )
        logger.info(f"Successfully wrote context blob to: {written_path}")
    except FileNotFoundError:
        logger.error(f"Input file not found: {input_path}", exc_info=True)
        print(f"Error: Input file not found at '{input_path}'", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Invalid transcript file: {e}", exc_info=True)
        print(f"Error: Invalid transcript file format: {e}", file=sys.stderr)
        return 1
    except IOError as e:
        logger.error(f"Failed to write output file: {e}", exc_info=True)
        print(
            f"Error: Could not write to output file at '{output_path}'. {e}",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        return 1

    # Print success message
    print("Successfully converted transcript to context blob")
    print(f"Written to: {written_path}")
    print(f"Artifact name: {artifact['name']}")
    print(f"Marker: {artifact['marker']}")

    return 0
