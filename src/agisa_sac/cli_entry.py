#!/usr/bin/env python3
"""Entry point for agisa-sac CLI to avoid circular imports."""

import sys
from agisa_sac.cli import main

if __name__ == "__main__":
    sys.exit(main())