#!/usr/bin/env python3
"""
AGI-SAC: Dev Orchestration Agent
A Claude-powered agent for managing development workflows including:
- Task planning and execution
- Code execution and testing
- Build automation
- Git operations
- File management
"""

import asyncio
import sys
from typing import Any

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    CLIJSONDecodeError,
    CLINotFoundError,
    ProcessError,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)


# Custom tools for dev orchestration
@tool(
    "execute_tests",
    "Run test suite for the project using pytest or unittest",
    {"test_path": str, "verbose": bool}
)
async def execute_tests(args: dict[str, Any]) -> dict[str, Any]:
    """Execute tests and return results."""
    import subprocess

    test_path = args.get("test_path", "tests/")
    verbose = args.get("verbose", False)

    try:
        # Try pytest first
        cmd = ["pytest", test_path]
        if verbose:
            cmd.append("-v")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

        return {
            "content": [{
                "type": "text",
                "text": f"Test execution completed (exit code: {result.returncode})\n\n{output}"
            }],
            "is_error": result.returncode != 0
        }
    except FileNotFoundError:
        # Fallback to unittest
        try:
            result = subprocess.run(
                ["python", "-m", "unittest", "discover", test_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            return {
                "content": [{
                    "type": "text",
                    "text": f"Test execution completed (exit code: {result.returncode})\n\n{output}"
                }],
                "is_error": result.returncode != 0
            }
        except Exception as e:
            return {
                "content": [{
                    "type": "text",
                    "text": f"Failed to run tests: {str(e)}"
                }],
                "is_error": True
            }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error executing tests: {str(e)}"
            }],
            "is_error": True
        }


@tool(
    "build_project",
    "Build the project using common build tools (pip, setup.py, etc.)",
    {"build_command": str}
)
async def build_project(args: dict[str, Any]) -> dict[str, Any]:
    """Execute build commands for the project."""
    import shlex
    import subprocess

    build_command = args.get("build_command", "pip install -e .")

    try:
        # Use shlex.split for safer command execution
        result = subprocess.run(
            shlex.split(build_command),
            shell=False,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

        return {
            "content": [{
                "type": "text",
                "text": f"Build completed (exit code: {result.returncode})\n\n{output}"
            }],
            "is_error": result.returncode != 0
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Build failed: {str(e)}"
            }],
            "is_error": True
        }


@tool(
    "analyze_code_quality",
    "Analyze code quality using linters and static analysis tools",
    {"path": str, "tools": str}
)
async def analyze_code_quality(args: dict[str, Any]) -> dict[str, Any]:
    """Run code quality analysis tools."""
    import subprocess

    path = args.get("path", ".")
    tools_str = args.get("tools", "pylint,mypy")
    tools = [t.strip() for t in tools_str.split(",")]

    results = []

    for tool_name in tools:
        try:
            if tool_name == "pylint":
                result = subprocess.run(
                    ["pylint", path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            elif tool_name == "mypy":
                result = subprocess.run(
                    ["mypy", path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            elif tool_name == "flake8":
                result = subprocess.run(
                    ["flake8", path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            elif tool_name == "black":
                result = subprocess.run(
                    ["black", "--check", path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
            else:
                results.append(f"\n{tool_name}: Tool not recognized")
                continue

            output = f"\n=== {tool_name.upper()} ===\n"
            output += f"Exit code: {result.returncode}\n"
            output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"

            results.append(output)

        except FileNotFoundError:
            results.append(f"\n{tool_name}: Not installed")
        except Exception as e:
            results.append(f"\n{tool_name}: Error - {str(e)}")

    return {
        "content": [{
            "type": "text",
            "text": "Code Quality Analysis Results:\n" + "\n".join(results)
        }]
    }


@tool(
    "get_project_status",
    "Get comprehensive status of the project (git, dependencies, tests)",
    {}
)
async def get_project_status(args: dict[str, Any]) -> dict[str, Any]:
    """Get comprehensive project status."""
    import os
    import subprocess

    status_parts = []

    # Git status
    try:
        git_status = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=30
        )
        git_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=30
        )
        status_parts.append(
            f"=== GIT STATUS ===\n"
            f"Branch: {git_branch.stdout.strip()}\n"
            f"Changes:\n{git_status.stdout if git_status.stdout else 'No changes'}"
        )
    except Exception:
        status_parts.append("=== GIT STATUS ===\nNot a git repository or git not available")

    # Python environment
    try:
        python_version = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        status_parts.append(f"\n=== PYTHON ENVIRONMENT ===\n{python_version.stdout}")
    except Exception as e:
        status_parts.append(f"\n=== PYTHON ENVIRONMENT ===\nError: {str(e)}")

    # Project structure
    try:
        file_count = 0
        py_count = 0
        for root, dirs, files in os.walk("."):
            # Skip common ignored directories
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules", ".venv", "venv"}]
            file_count += len(files)
            py_count += sum(1 for f in files if f.endswith(".py"))

        status_parts.append(
            f"\n=== PROJECT STRUCTURE ===\n"
            f"Total files: {file_count}\n"
            f"Python files: {py_count}"
        )
    except Exception as e:
        status_parts.append(f"\n=== PROJECT STRUCTURE ===\nError: {str(e)}")

    return {
        "content": [{
            "type": "text",
            "text": "\n".join(status_parts)
        }]
    }


async def run_orchestration_agent(prompt: str, allow_edits: bool = False):
    """
    Run the dev orchestration agent with the specified prompt.

    Args:
        prompt: The task or question for the agent
        allow_edits: Whether to allow the agent to edit files automatically
    """
    # Create SDK MCP server with custom dev tools
    dev_tools_server = create_sdk_mcp_server(
        name="dev-tools",
        version="1.0.0",
        tools=[
            execute_tests,
            build_project,
            analyze_code_quality,
            get_project_status,
        ]
    )

    # Configure agent options
    options = ClaudeAgentOptions(
        # Model selection
        model="claude-sonnet-4-5-20251101",
        # Built-in tools for file operations and execution
        allowed_tools=[
            "Read",           # Read files
            "Write",          # Create new files
            "Edit",           # Edit existing files
            "Bash",           # Execute commands
            "Glob",           # Find files by pattern
            "Grep",           # Search file contents
            "TodoWrite",      # Task management
            # Custom dev tools via MCP
            "mcp__dev-tools__execute_tests",
            "mcp__dev-tools__build_project",
            "mcp__dev-tools__analyze_code_quality",
            "mcp__dev-tools__get_project_status",
        ],
        # MCP servers
        mcp_servers={"dev-tools": dev_tools_server},
        # Permission mode
        permission_mode="acceptEdits" if allow_edits else "default",
        # System prompt for dev orchestration
        system_prompt=(
            "You are AGI-SAC, an expert dev orchestration agent. Your role is to help manage "
            "development workflows including:\n"
            "- Planning and tracking tasks\n"
            "- Running tests and builds\n"
            "- Analyzing code quality\n"
            "- Managing git operations\n"
            "- File operations (read, write, edit)\n\n"
            "When given a task, break it down into steps, use the available tools effectively, "
            "and provide clear status updates. Always verify your work and report results."
        ),
    )

    print("🚀 Starting AGI-SAC Dev Orchestration Agent...\n")
    print(f"📋 Task: {prompt}\n")
    print("=" * 80)

    try:
        async for message in query(prompt=prompt, options=options):
            # Display assistant text responses
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"\n💬 Agent: {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"\n🔧 Using tool: {block.name}")

            # Display final result
            elif isinstance(message, ResultMessage):
                print("\n" + "=" * 80)
                print("\n✅ Task completed!")
                print(f"⏱️  Duration: {message.duration_ms / 1000:.2f}s")
                print(f"🔄 Turns: {message.num_turns}")
                if message.total_cost_usd:
                    print(f"💰 Cost: ${message.total_cost_usd:.4f}")
                if message.result:
                    print(f"\n📊 Result:\n{message.result}")

                if message.is_error:
                    print("\n❌ Task completed with errors")
                    return 1

                return 0

        return 0

    except CLINotFoundError as e:
        print(f"\n❌ Claude Code CLI not found: {e}", file=sys.stderr)
        print("\nPlease install Claude Code:", file=sys.stderr)
        print("  npm install -g @anthropic-ai/claude-code", file=sys.stderr)
        print("  or visit: https://code.claude.com/docs/en/setup", file=sys.stderr)
        return 1
    except ProcessError as e:
        print(f"\n❌ Process error (exit code {e.exit_code}): {e}", file=sys.stderr)
        if e.stderr:
            print(f"\nStderr output:\n{e.stderr}", file=sys.stderr)
        return 1
    except CLIJSONDecodeError as e:
        print(f"\n❌ Failed to parse CLI response: {e}", file=sys.stderr)
        print(f"Problematic line: {e.line}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}", file=sys.stderr)
        return 1


async def interactive_mode():
    """Run the agent in interactive mode for continuous conversations."""
    from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

    # Create SDK MCP server with custom dev tools
    dev_tools_server = create_sdk_mcp_server(
        name="dev-tools",
        version="1.0.0",
        tools=[
            execute_tests,
            build_project,
            analyze_code_quality,
            get_project_status,
        ]
    )

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5-20251101",
        allowed_tools=[
            "Read", "Write", "Edit", "Bash", "Glob", "Grep", "TodoWrite",
            "mcp__dev-tools__execute_tests",
            "mcp__dev-tools__build_project",
            "mcp__dev-tools__analyze_code_quality",
            "mcp__dev-tools__get_project_status",
        ],
        mcp_servers={"dev-tools": dev_tools_server},
        permission_mode="default",
        system_prompt=(
            "You are AGI-SAC, an expert dev orchestration agent. Help manage development "
            "workflows effectively and provide clear updates."
        ),
    )

    print("🚀 AGI-SAC Interactive Mode")
    print("=" * 80)
    print("Commands: 'exit' to quit, 'new' to start fresh session")
    print("=" * 80)

    async with ClaudeSDKClient(options=options) as client:
        turn = 0
        while True:
            try:
                user_input = input(f"\n[{turn}] You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "exit":
                    print("👋 Goodbye!")
                    break

                if user_input.lower() == "new":
                    print("🔄 Starting new session...")
                    await client.disconnect()
                    await client.connect()
                    turn = 0
                    continue

                # Send query
                await client.query(user_input)
                turn += 1

                # Process response
                print(f"\n[{turn}] Agent: ", end="")
                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                print(block.text, end="")
                            elif isinstance(block, ToolUseBlock):
                                print(f"\n🔧 [{block.name}]", end="")
                    elif isinstance(message, ResultMessage):
                        if message.is_error:
                            print("\n❌ Error occurred")

                print()  # New line after response

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except CLINotFoundError as e:
                print(f"\n❌ Claude Code CLI not found: {e}", file=sys.stderr)
                print("Install with: npm install -g @anthropic-ai/claude-code", file=sys.stderr)
                break
            except ProcessError as e:
                print(f"\n❌ Process error (exit code {e.exit_code}): {e}", file=sys.stderr)
            except CLIJSONDecodeError as e:
                print(f"\n❌ Failed to parse response: {e}", file=sys.stderr)
            except Exception as e:
                print(f"\n❌ Error: {str(e)}", file=sys.stderr)


def main():
    """Main entry point for the AGI-SAC dev orchestration agent."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AGI-SAC: Dev Orchestration Agent powered by Claude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a specific task
  python main.py "Run all tests and report results"

  # Interactive mode
  python main.py --interactive

  # Allow automatic file edits
  python main.py --allow-edits "Refactor the auth module"

  # Analyze project
  python main.py "Analyze the codebase and suggest improvements"
        """
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Task or question for the agent"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode for continuous conversation"
    )
    parser.add_argument(
        "--allow-edits",
        action="store_true",
        help="Allow the agent to automatically edit files without prompting"
    )

    args = parser.parse_args()

    # Verify API key is set
    import os
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        print("\nPlease set your API key:", file=sys.stderr)
        print("  export ANTHROPIC_API_KEY=your-api-key-here", file=sys.stderr)
        print("\nGet your API key from: https://console.anthropic.com/", file=sys.stderr)
        sys.exit(1)

    if args.interactive:
        return asyncio.run(interactive_mode())
    elif args.prompt:
        return asyncio.run(run_orchestration_agent(args.prompt, args.allow_edits))
    else:
        parser.print_help()
        print("\n💡 Tip: Use --interactive for a conversation or provide a prompt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
