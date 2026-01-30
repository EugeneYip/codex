# Codex Todo CLI

A tiny command-line todo list that stores tasks in a local JSON file. It is meant
to be a simple, beginner-friendly project with real coding, a clear data model,
and immediate feedback from running commands.

## Quick start

```bash
python codex_cli.py add "Buy milk"
python codex_cli.py add "Write README"
python codex_cli.py list
python codex_cli.py done 1
python codex_cli.py list --all
```

## Commands

- `add "<task>"` - Add a new task.
- `list` - List open tasks.
- `list --all` - List all tasks, including completed ones.
- `done <id>` - Mark a task as complete.
- `clear --done` - Remove completed tasks.
- `clear --all` - Remove all tasks.

## Data storage

Tasks are stored in `.codex_todo.json` in the current working directory so you
can keep separate lists per folder.
