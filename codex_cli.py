#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


DATA_FILE = Path(".codex_todo.json")


@dataclass
class Task:
    id: int
    title: str
    done: bool
    created_at: str
    completed_at: str | None

    @staticmethod
    def from_dict(data: dict) -> "Task":
        return Task(
            id=int(data["id"]),
            title=str(data["title"]),
            done=bool(data["done"]),
            created_at=str(data["created_at"]),
            completed_at=data.get("completed_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_tasks(path: Path) -> List[Task]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Task.from_dict(item) for item in data]


def save_tasks(path: Path, tasks: Iterable[Task]) -> None:
    payload = [task.to_dict() for task in tasks]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def next_id(tasks: Iterable[Task]) -> int:
    current = [task.id for task in tasks]
    return max(current, default=0) + 1


def add_task(path: Path, title: str) -> Task:
    tasks = load_tasks(path)
    task = Task(
        id=next_id(tasks),
        title=title,
        done=False,
        created_at=utc_now(),
        completed_at=None,
    )
    tasks.append(task)
    save_tasks(path, tasks)
    return task


def list_tasks(path: Path, include_done: bool) -> List[Task]:
    tasks = load_tasks(path)
    if include_done:
        return tasks
    return [task for task in tasks if not task.done]


def complete_task(path: Path, task_id: int) -> Task | None:
    tasks = load_tasks(path)
    for task in tasks:
        if task.id == task_id:
            task.done = True
            task.completed_at = utc_now()
            save_tasks(path, tasks)
            return task
    return None


def clear_tasks(path: Path, remove_all: bool) -> int:
    tasks = load_tasks(path)
    if remove_all:
        removed = len(tasks)
        save_tasks(path, [])
        return removed
    remaining = [task for task in tasks if not task.done]
    removed = len(tasks) - len(remaining)
    save_tasks(path, remaining)
    return removed


def format_task(task: Task) -> str:
    status = "✓" if task.done else "•"
    return f"[{status}] {task.id}. {task.title}"


def print_tasks(tasks: Iterable[Task]) -> None:
    tasks_list = list(tasks)
    if not tasks_list:
        print("No tasks yet.")
        return
    for task in tasks_list:
        print(format_task(task))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tiny todo CLI for Codex.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task.")
    add_parser.add_argument("title", help="Task description.")

    list_parser = subparsers.add_parser("list", help="List tasks.")
    list_parser.add_argument("--all", action="store_true", help="Include done tasks.")

    done_parser = subparsers.add_parser("done", help="Mark a task as done.")
    done_parser.add_argument("id", type=int, help="ID of the task.")

    clear_parser = subparsers.add_parser("clear", help="Clear tasks.")
    clear_group = clear_parser.add_mutually_exclusive_group(required=True)
    clear_group.add_argument("--done", action="store_true", help="Clear done tasks.")
    clear_group.add_argument("--all", action="store_true", help="Clear all tasks.")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "add":
        task = add_task(DATA_FILE, args.title)
        print(f"Added task {task.id}.")
        return

    if args.command == "list":
        tasks = list_tasks(DATA_FILE, include_done=args.all)
        print_tasks(tasks)
        return

    if args.command == "done":
        task = complete_task(DATA_FILE, args.id)
        if task is None:
            print(f"Task {args.id} not found.")
            return
        print(f"Completed task {task.id}.")
        return

    if args.command == "clear":
        removed = clear_tasks(DATA_FILE, remove_all=args.all)
        print(f"Removed {removed} task(s).")


if __name__ == "__main__":
    main()
