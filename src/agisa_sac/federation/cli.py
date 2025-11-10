"""Command-line interface for AGI-SAC federation services.

Usage:
    agisa-federation server --host 0.0.0.0 --port 8000
    agisa-federation status --url http://localhost:8000
"""

from __future__ import annotations

import argparse
import sys


def start_server(args: argparse.Namespace) -> int:
    """Start the federation server."""
    try:
        import uvicorn

        from .server import app

        print("Starting AGI-SAC Federation Server")
        print(f"Host: {args.host}")
        print(f"Port: {args.port}")
        print("-" * 60)

        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            log_level="info" if args.verbose else "warning",
        )
        return 0

    except ImportError as e:
        print(
            f"Error: Missing dependencies for federation server: {e}",
            file=sys.stderr,
        )
        print(
            "Install with: pip install agisa-sac[federation]", file=sys.stderr
        )
        return 1
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


def check_status(args: argparse.Namespace) -> int:
    """Check federation server status."""
    try:
        import httpx

        url = args.url.rstrip("/")
        print(f"Checking status of: {url}")

        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{url}/health")
            if response.status_code == 200:
                print("✓ Server is running")
                data = response.json()
                if data:
                    print(f"  Status: {data}")
                return 0
            else:
                print(f"✗ Server returned status code: {response.status_code}")
                return 1

    except ImportError:
        print("Error: httpx not installed", file=sys.stderr)
        print("Install with: pip install httpx", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Could not connect to server: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point for federation services."""
    parser = argparse.ArgumentParser(
        prog="agisa-federation",
        description="AGI-SAC Federation Services - Distributed agent coordination",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Server command
    server_parser = subparsers.add_parser(
        "server", help="Start federation server"
    )
    server_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    server_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose logging",
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Check server status")
    status_parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Server URL (default: http://localhost:8000)",
    )

    # Parse arguments
    args = parser.parse_args()

    if args.command == "server":
        return start_server(args)
    elif args.command == "status":
        return check_status(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
