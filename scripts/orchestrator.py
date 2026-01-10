#!/usr/bin/env python3
"""
AGISA-SAC Meta-Orchestrator
A turn-based development workflow orchestrator for multi-agent refactoring tasks.
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional


class Role(Enum):
    """Development team roles"""
    ARCHITECT_PM = "architect-pm"
    DEVELOPER = "developer"
    QA_CRITIC = "qa-critic"
    ORCHESTRATOR = "orchestrator"


class TaskStatus(Enum):
    """Task completion status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """Represents a development task"""
    id: str
    role: Role
    component: str
    description: str
    status: TaskStatus
    dependencies: List[str]
    artifacts: List[str]
    notes: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Session:
    """Orchestrator session state"""
    session_id: str
    created_at: str
    current_turn: int
    current_role: Optional[Role]
    tasks: List[Task]
    metadata: Dict


class Orchestrator:
    """Meta-orchestrator for coordinating development workflow"""

    def __init__(self, session_id: str, workspace: Path):
        self.session_id = session_id
        self.workspace = workspace
        self.state_file = workspace / f".orchestrator_{session_id}.json"
        self.session = self._load_or_create_session()

    def _load_or_create_session(self) -> Session:
        """Load existing session or create new one"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)
                tasks = []
                for t in data['tasks']:
                    task_data = {k: v for k, v in t.items() if k not in ['role', 'status']}
                    tasks.append(Task(
                        **task_data,
                        role=Role(t['role']),
                        status=TaskStatus(t['status'])
                    ))
                return Session(
                    session_id=data['session_id'],
                    created_at=data['created_at'],
                    current_turn=data['current_turn'],
                    current_role=Role(data['current_role']) if data['current_role'] else None,
                    tasks=tasks,
                    metadata=data['metadata']
                )

        return Session(
            session_id=self.session_id,
            created_at=datetime.now().isoformat(),
            current_turn=0,
            current_role=None,
            tasks=[],
            metadata={}
        )

    def _save_session(self):
        """Persist session state"""
        data = {
            'session_id': self.session.session_id,
            'created_at': self.session.created_at,
            'current_turn': self.session.current_turn,
            'current_role': self.session.current_role.value if self.session.current_role else None,
            'tasks': [
                {**asdict(t), 'role': t.role.value, 'status': t.status.value}
                for t in self.session.tasks
            ],
            'metadata': self.session.metadata
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)

    def reset(self):
        """Reset session to initial state"""
        if self.state_file.exists():
            self.state_file.unlink()
        self.session = self._load_or_create_session()
        print(f"🔄 Session {self.session_id} reset")

    def add_task(self, task: Task):
        """Add a new task to the session"""
        self.session.tasks.append(task)
        self._save_session()

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        for task in self.session.tasks:
            if task.id == task_id:
                return task
        return None

    def update_task_status(self, task_id: str, status: TaskStatus, notes: str = ""):
        """Update task status"""
        task = self.get_task(task_id)
        if task:
            task.status = status
            if notes:
                task.notes = notes
            if status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.now().isoformat()
            elif status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now().isoformat()
            self._save_session()

    def get_next_task(self) -> Optional[Task]:
        """Get next pending task with satisfied dependencies"""
        for task in self.session.tasks:
            if task.status != TaskStatus.PENDING:
                continue

            # Check if all dependencies are completed
            deps_completed = all(
                self.get_task(dep_id).status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )

            if deps_completed:
                return task

        return None

    def start_turn(self, role: Role):
        """Start a new turn for the given role"""
        self.session.current_turn += 1
        self.session.current_role = role
        self._save_session()

        print(f"\n{'='*70}")
        print(f"🎯 Turn {self.session.current_turn}: {role.value.upper()}")
        print(f"{'='*70}\n")

    def print_status(self):
        """Print current session status"""
        print(f"\n📊 Session Status: {self.session_id}")
        print(f"Turn: {self.session.current_turn}")
        print(f"Current Role: {self.session.current_role.value if self.session.current_role else 'None'}")
        print(f"\nTasks ({len(self.session.tasks)} total):")

        for task in self.session.tasks:
            status_icon = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.BLOCKED: "🚫"
            }[task.status]

            print(f"  {status_icon} [{task.role.value}] {task.id}: {task.description}")
            if task.notes:
                print(f"      Note: {task.notes}")

    def setup_default_tasks(self):
        """Setup default refactor tasks"""
        tasks = [
            Task(
                id="arch-01",
                role=Role.ARCHITECT_PM,
                component="planning",
                description="Create spec.md with refactor requirements",
                status=TaskStatus.PENDING,
                dependencies=[],
                artifacts=["spec.md"]
            ),
            Task(
                id="arch-02",
                role=Role.ARCHITECT_PM,
                component="planning",
                description="Create design.md with component breakdown",
                status=TaskStatus.PENDING,
                dependencies=["arch-01"],
                artifacts=["design.md"]
            ),
            Task(
                id="dev-01",
                role=Role.DEVELOPER,
                component="infrastructure",
                description="Migrate to Poetry (init, dependencies, config)",
                status=TaskStatus.PENDING,
                dependencies=["arch-02"],
                artifacts=["pyproject.toml", "poetry.lock"]
            ),
            Task(
                id="dev-02",
                role=Role.DEVELOPER,
                component="documentation",
                description="Update CLAUDE.md to reflect current state",
                status=TaskStatus.PENDING,
                dependencies=["dev-01"],
                artifacts=["docs/CLAUDE.md"]
            ),
            Task(
                id="dev-03",
                role=Role.DEVELOPER,
                component="linting-core",
                description="Fix logical/import linting errors",
                status=TaskStatus.PENDING,
                dependencies=["dev-01"],
                artifacts=[]
            ),
            Task(
                id="dev-04",
                role=Role.DEVELOPER,
                component="linting-style",
                description="Fix formatting/E501 style errors",
                status=TaskStatus.PENDING,
                dependencies=["dev-03"],
                artifacts=[]
            ),
            Task(
                id="qa-01",
                role=Role.QA_CRITIC,
                component="validation",
                description="Run flake8 validation",
                status=TaskStatus.PENDING,
                dependencies=["dev-04"],
                artifacts=[]
            ),
            Task(
                id="qa-02",
                role=Role.QA_CRITIC,
                component="validation",
                description="Run pytest test suite",
                status=TaskStatus.PENDING,
                dependencies=["dev-04"],
                artifacts=[]
            ),
        ]

        for task in tasks:
            self.add_task(task)


def main():
    parser = argparse.ArgumentParser(
        description="AGISA-SAC Meta-Orchestrator for turn-based development"
    )
    parser.add_argument(
        "session_id",
        help="Session identifier"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset session to initial state"
    )
    parser.add_argument(
        "--no-auto-discover",
        action="store_true",
        help="Don't auto-discover tasks (use default task list)"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="Workspace directory (default: current directory)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Print current status and exit"
    )

    args = parser.parse_args()

    orchestrator = Orchestrator(args.session_id, args.workspace)

    if args.reset:
        orchestrator.reset()

    if args.status:
        orchestrator.print_status()
        return

    # Setup tasks if this is a new session
    if orchestrator.session.current_turn == 0:
        print("🚀 Initializing new orchestration session")
        orchestrator.setup_default_tasks()
        orchestrator.start_turn(Role.ARCHITECT_PM)

        print("📋 Task queue initialized. Use --status to view all tasks.")
        print("\n🎯 NEXT ACTION:")
        next_task = orchestrator.get_next_task()
        if next_task:
            print(f"   Task: {next_task.id} - {next_task.description}")
            print(f"   Role: {next_task.role.value}")
            print(f"   Expected artifacts: {', '.join(next_task.artifacts)}")
            print(f"\n💡 When ready, update task status with:")
            print(f"   orchestrator.update_task_status('{next_task.id}', TaskStatus.IN_PROGRESS)")
    else:
        orchestrator.print_status()
        next_task = orchestrator.get_next_task()
        if next_task:
            print(f"\n🎯 NEXT TASK: {next_task.id} - {next_task.description}")


if __name__ == "__main__":
    main()
