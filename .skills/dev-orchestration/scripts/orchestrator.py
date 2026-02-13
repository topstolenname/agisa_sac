#!/usr/bin/env python3
"""
Dev Team Orchestration - interactive multi-agent workflow helper.

This script is designed to be run inside a project directory. It persists a
`.dev-team-state.json` file and guides you through an iterative workflow:

Planning (Architect-PM) -> per-component Implementation (Developer/QA loop)
-> Documentation (Tech-Writer).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Literal


Role = Literal["architect-pm", "developer", "qa-critic", "tech-writer"]
Phase = Literal["planning", "implementation", "documentation", "done"]


STATE_FILENAME = ".dev-team-state.json"
DEFAULT_DESIGN_MD = "design.md"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_text_if_exists(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _json_dump(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _slugify_component(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    return slug or "component"


def parse_components_from_design_md(markdown: str) -> list[str]:
    """
    Extract component names from a design.md "## Components" section.

    Supports these patterns:
    - Numbered lists: "1. **database-layer** - ..."
    - Bullets: "- **cli-interface** - ..."
    - Plain lists: "- database-layer - ..."
    """

    if not markdown.strip():
        return []

    # Grab the "## Components" section up to the next "## "
    section_re = re.compile(r"(?ms)^\s*##\s+Components\s*\n(.*?)(?=^\s*##\s+|\Z)")
    match = section_re.search(markdown)
    if not match:
        return []
    section = match.group(1)

    component_names: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Common markdown list prefixes
        line = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", line)

        # Prefer bolded names: **name**
        bold = re.search(r"\*\*(.+?)\*\*", line)
        if bold:
            name = bold.group(1).strip()
            if name:
                component_names.append(name)
            continue

        # Fall back to first token before dash/colon
        head = re.split(r"\s[-–—:]\s", line, maxsplit=1)[0].strip()
        if head:
            component_names.append(head)

    # De-dupe in order; keep original names but normalized equality
    seen: set[str] = set()
    ordered: list[str] = []
    for name in component_names:
        key = _slugify_component(name)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(name)
    return ordered


def _print_block(title: str, body: str) -> None:
    bar = "=" * 52
    print()
    print(bar)
    print(title)
    print(bar)
    print(body.rstrip())
    print(bar)


def _wait_for_enter(enabled: bool) -> None:
    if not enabled:
        return
    try:
        input("\nPress Enter when this task is complete...")
    except EOFError:
        # Non-interactive stdin; just proceed.
        return


def _which(cmd: str) -> str | None:
    return shutil.which(cmd)


def _run_pytest(test_path: Path) -> tuple[bool, str]:
    """
    Run pytest for a single test file (if it exists).
    Returns (passed, output).
    """

    if not test_path.exists():
        return False, f"Missing expected test file: {test_path.as_posix()}"

    if _which("pytest") is None:
        return False, "pytest is not available on PATH; cannot auto-run tests."

    proc = subprocess.run(
        ["pytest", "-q", test_path.as_posix()],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    out = (proc.stdout or "") + (("\n" + proc.stderr) if proc.stderr else "")
    passed = proc.returncode == 0
    return passed, out.strip()


@dataclass(frozen=True)
class NextTurn:
    role: Role
    phase: Phase
    component: str | None
    message: str


class DevTeamOrchestrator:
    def __init__(
        self,
        cwd: Path,
        project_name: str,
        *,
        state_path: Path | None = None,
        design_md: str = DEFAULT_DESIGN_MD,
        interactive: bool = True,
        auto_discover: bool = True,
        auto_run_pytest: bool = True,
    ) -> None:
        self.cwd = cwd
        self.project_name = project_name
        self.state_path = state_path or (cwd / STATE_FILENAME)
        self.design_md = design_md
        self.interactive = interactive
        self.auto_discover = auto_discover
        self.auto_run_pytest = auto_run_pytest

        self.state: dict[str, Any] = {}

    def load_or_init_state(self) -> None:
        if self.state_path.exists():
            self.state = _json_load(self.state_path)
            # If project name differs, keep existing state project_name as truth.
            self.project_name = str(self.state.get("project_name") or self.project_name)
            return

        self.state = {
            "project_name": self.project_name,
            "phase": "planning",
            "current_component": None,
            "completed_components": [],
            "qa_failures": 0,
            "discovered_components": [],
            "history": [],
            "last_qa_output": None,
            "created_at": _utc_now_iso(),
            "updated_at": _utc_now_iso(),
        }
        self.save_state()

    def save_state(self) -> None:
        self.state["updated_at"] = _utc_now_iso()
        _json_dump(self.state_path, self.state)

    def reset_state(self) -> None:
        if self.state_path.exists():
            self.state_path.unlink()
        self.load_or_init_state()

    def _history_add(self, role: Role, task: str, *, component: str | None = None) -> None:
        self.state.setdefault("history", []).append(
            {
                "ts": _utc_now_iso(),
                "role": role,
                "task": task,
                "component": component,
            }
        )
        self.save_state()

    def _ensure_components_discovered(self) -> None:
        if self.state.get("discovered_components"):
            return

        components: list[str] = []
        if self.auto_discover:
            design_path = self.cwd / self.design_md
            md = _read_text_if_exists(design_path)
            if md:
                components = parse_components_from_design_md(md)

        if not components and self.interactive:
            raw = input(
                "\nNo components discovered. Enter components (comma-separated): "
            ).strip()
            components = [c.strip() for c in raw.split(",") if c.strip()]

        components = components or ["integration"]
        self.state["discovered_components"] = components
        self.state["current_component"] = components[0]
        self.save_state()

    def _next_incomplete_component(self) -> str | None:
        completed = {_slugify_component(c) for c in self.state.get("completed_components", [])}
        for comp in self.state.get("discovered_components", []):
            if _slugify_component(comp) not in completed:
                return comp
        return None

    def _advance_component(self) -> None:
        nxt = self._next_incomplete_component()
        self.state["current_component"] = nxt
        self.save_state()

    def compute_next_turn(self) -> NextTurn:
        phase: Phase = self.state.get("phase", "planning")

        if phase == "planning":
            return NextTurn(
                role="architect-pm",
                phase="planning",
                component=None,
                message=(
                    "Review the user request. Create:\n"
                    "1. spec.md - user stories, acceptance criteria\n"
                    "2. design.md - architecture, component list in a '## Components' section\n"
                    "3. schema.sql (optional, if a database is needed)\n"
                ),
            )

        if phase == "documentation":
            return NextTurn(
                role="tech-writer",
                phase="documentation",
                component=None,
                message=(
                    "Create or update README.md:\n"
                    "- installation steps\n"
                    "- usage examples\n"
                    "- project structure\n"
                    "- copy/paste-friendly commands\n"
                ),
            )

        if phase == "done":
            return NextTurn(
                role="tech-writer",
                phase="done",
                component=None,
                message="All phases complete.",
            )

        # implementation
        self._ensure_components_discovered()
        component = self.state.get("current_component") or self._next_incomplete_component()
        if not component:
            return NextTurn(
                role="tech-writer",
                phase="documentation",
                component=None,
                message="No remaining components. Proceed to documentation.",
            )

        last = self.state.get("history", [])[-1] if self.state.get("history") else None
        last_role: Role | None = (last.get("role") if last else None)
        last_component = last.get("component") if last else None

        # default: developer goes first for a component
        if last_role == "developer" and last_component == component:
            msg = (
                f"Test component: {component}\n"
                f"1. Write test file: tests/test_{_slugify_component(component)}.py\n"
                "2. Execute tests using pytest (auto-run if available)\n"
                "3. Analyze failures and report actionable details\n"
            )
            if self.state.get("last_qa_output"):
                msg += "\nLast QA output (for context):\n" + str(self.state["last_qa_output"])
            return NextTurn(role="qa-critic", phase="implementation", component=component, message=msg)

        if last_role == "qa-critic" and last_component == component:
            # If QA was last, we decide what comes next at runtime after running tests.
            # Here we just send developer back by default (fail) unless state says it passed.
            # The step() method will handle pass/fail transitions.
            msg = (
                f"Implement (or fix) component: {component}\n"
                "- Follow spec.md + design.md\n"
                "- Keep scope limited to this component\n"
                "- Ensure code is structured for tests\n"
            )
            if self.state.get("last_qa_output"):
                msg += "\nMost recent QA output:\n" + str(self.state["last_qa_output"])
            return NextTurn(role="developer", phase="implementation", component=component, message=msg)

        # Otherwise assume developer turn.
        return NextTurn(
            role="developer",
            phase="implementation",
            component=component,
            message=(
                f"Implement component: {component}\n"
                "- Follow spec.md + design.md\n"
                "- Implement only this component\n"
                "- Add docstrings and keep code testable\n"
            ),
        )

    def step(self) -> None:
        nxt = self.compute_next_turn()

        title = f"AGENT: {nxt.role.upper()}  |  PHASE: {nxt.phase.upper()}"
        if nxt.component:
            title += f"  |  COMPONENT: {nxt.component}"
        _print_block(title, "TASK:\n" + nxt.message)

        if nxt.phase == "planning":
            _wait_for_enter(self.interactive)
            self._history_add("architect-pm", "Create planning documents", component=None)
            self.state["phase"] = "implementation"
            self.save_state()
            # After planning, discover components (from design.md by default).
            self._ensure_components_discovered()
            return

        if nxt.phase == "documentation":
            _wait_for_enter(self.interactive)
            self._history_add("tech-writer", "Create documentation", component=None)
            self.state["phase"] = "done"
            self.save_state()
            return

        if nxt.phase == "done":
            print("\nDone. No further actions required.")
            return

        # Implementation turn
        assert nxt.component is not None
        component = nxt.component

        if nxt.role == "developer":
            _wait_for_enter(self.interactive)
            self._history_add("developer", f"Implement {component}", component=component)
            return

        if nxt.role == "qa-critic":
            # Give the QA a chance to create tests if missing.
            _wait_for_enter(self.interactive)
            self._history_add("qa-critic", f"Test {component}", component=component)

            test_path = self.cwd / "tests" / f"test_{_slugify_component(component)}.py"
            if not self.auto_run_pytest:
                print("\nAuto-run is disabled; run pytest manually if desired.")
                return

            passed, out = _run_pytest(test_path)
            self.state["last_qa_output"] = out
            self.save_state()

            if passed:
                completed = self.state.setdefault("completed_components", [])
                completed.append(component)
                self.state["last_qa_output"] = None
                self.save_state()
                print("\nQA RESULT: PASS")
                self._advance_component()
                if self.state.get("current_component") is None:
                    self.state["phase"] = "documentation"
                    self.save_state()
                return

            # Fail -> kick back to developer
            self.state["qa_failures"] = int(self.state.get("qa_failures") or 0) + 1
            self.save_state()
            print("\nQA RESULT: FAIL")
            print("\nCaptured pytest output:\n")
            print(out)
            if self.state["qa_failures"] > 3:
                print(
                    "\nComponent has failed 3+ times. Consider splitting scope or revisiting design.md."
                )
            return

        raise RuntimeError(f"Unexpected role: {nxt.role}")

    def status(self) -> None:
        phase = self.state.get("phase")
        comp = self.state.get("current_component")
        completed = self.state.get("completed_components", [])
        discovered = self.state.get("discovered_components", [])
        failures = self.state.get("qa_failures", 0)

        print(f"Project: {self.project_name}")
        print(f"State file: {self.state_path.as_posix()}")
        print(f"Phase: {phase}")
        print(f"Current component: {comp}")
        print(f"Completed components: {completed}")
        print(f"Discovered components: {discovered}")
        print(f"QA failures: {failures}")

        nxt = self.compute_next_turn()
        who = nxt.role
        what = nxt.component or "(n/a)"
        print(f"Next: {who} -> {what}")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="dev-orchestration",
        description="Coordinate a 4-agent dev-team workflow with persisted state.",
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        help="Project name (used for new state). If omitted, uses current directory name.",
    )
    parser.add_argument(
        "--state-file",
        default=STATE_FILENAME,
        help=f"Path to state file (default: {STATE_FILENAME})",
    )
    parser.add_argument(
        "--design-md",
        default=DEFAULT_DESIGN_MD,
        help=f"design.md path used for component discovery (default: {DEFAULT_DESIGN_MD})",
    )
    parser.add_argument("--reset", action="store_true", help="Reset state and start over.")
    parser.add_argument("--status", action="store_true", help="Print current status and exit.")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Do not wait for Enter prompts; useful for automation.",
    )
    parser.add_argument(
        "--no-auto-discover",
        action="store_true",
        help="Disable design.md component discovery.",
    )
    parser.add_argument(
        "--no-auto-pytest",
        action="store_true",
        help="Disable automatic pytest execution during QA turns.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(argv or sys.argv[1:])
    cwd = Path.cwd()
    project_name = ns.project_name or cwd.name
    orchestrator = DevTeamOrchestrator(
        cwd=cwd,
        project_name=project_name,
        state_path=cwd / str(ns.state_file),
        design_md=str(ns.design_md),
        interactive=not bool(ns.non_interactive),
        auto_discover=not bool(ns.no_auto_discover),
        auto_run_pytest=not bool(ns.no_auto_pytest),
    )
    orchestrator.load_or_init_state()
    if ns.reset:
        orchestrator.reset_state()
    if ns.status:
        orchestrator.status()
        return 0

    orchestrator.step()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

