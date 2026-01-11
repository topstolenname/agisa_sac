#!/usr/bin/env python3
"""
Command-line interface for [PROJECT_NAME].

Replace [PROJECT_NAME] with your actual project name.
"""
import argparse
import sys
from .core import process_data
from .utils import setup_logging


def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="[PROJECT_NAME] - Brief description here",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Global options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Example: 'add' command
    add_parser = subparsers.add_parser("add", help="Add a new item")
    add_parser.add_argument("item", help="Item to add")
    
    # Example: 'list' command
    subparsers.add_parser("list", help="List all items")
    
    # Example: 'remove' command
    remove_parser = subparsers.add_parser("remove", help="Remove an item")
    remove_parser.add_argument("item_id", type=int, help="ID of item to remove")
    
    return parser


def main():
    """Main entry point for CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(verbose=args.verbose)
    
    # Handle commands
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "add":
            result = process_data(action="add", item=args.item)
            print(f"Added: {result}")
        
        elif args.command == "list":
            items = process_data(action="list")
            for item in items:
                print(f"  {item}")
        
        elif args.command == "remove":
            result = process_data(action="remove", item_id=args.item_id)
            print(f"Removed: {result}")
        
        else:
            print(f"Unknown command: {args.command}")
            return 1
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
