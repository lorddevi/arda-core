# Task Completion Checklist

## Before Marking Task Complete

### 1. Run Tests

```bash
just test-without-core    # Fast isolated tests
just test-with-core       # If touching core functionality
```

### 2. Run Linting

```bash
ruff check .
ruff format .
```

### 3. Type Checking (if strict)

```bash
mypy pkgs/arda-cli/arda_cli/
```

### 4. Pre-commit Hooks

```bash
pre-commit run --all-files
```

## Session Close Protocol (CRITICAL)

**NEVER skip this before saying "done":**

```bash
git status              # Check what changed
git add <files>         # Stage code changes
bd sync                 # Commit beads changes
git commit -m "..."     # Commit code
bd sync                 # Any new beads changes
git push                # Push to remote
```

## Issue Tracking

- Update `bd` issue status throughout work
- Close issues with `bd close <id> --reason "..."`
- Link discovered issues: `bd create --deps discovered-from:<parent-id>`
- Run `bd sync` at session end
