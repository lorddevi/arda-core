# Suggested Commands for Arda Development

## Development Environment

```bash
nix develop          # Enter development shell
```

## Build Commands

```bash
just build-arda-cli  # Build arda CLI (result at ./results/arda-cli)
just build-ea-cli    # Build ea CLI
just build-all       # Build all CLI tools
```

## Testing Commands

```bash
# Phase-based testing (fast to slow)
just test-without-core    # Phase 1: Fast, isolated tests (~180 tests)
just test-with-core       # Phase 2: Tests requiring arda-core (~45 tests)
just test-two-phase       # Both phases sequentially

# Single test
pytest pkgs/arda-cli/arda_cli/tests/unit/commands/test_<module>.py::test_<name> -v

# VM tests (NixOS native)
just test-vm-cli          # All CLI VM tests
just test-vm-cli-help     # Help output tests
just test-vm-cli-config   # Config tests

# Full suite
just test-all             # Everything (pytest + build + VM + pre-commit + flake)
```

## Coverage

```bash
just coverage             # Terminal coverage report
just coverage-detailed    # Terminal + HTML (htmlcov/index.html)
just coverage-check       # Fail if below 75%
just coverage-html        # HTML report only
```

## Linting & Formatting

```bash
ruff check .              # Lint
ruff format .             # Format
pre-commit run --all-files # All pre-commit hooks
nix flake check           # Nix flake validation
```

## Issue Tracking (bd/beads)

```bash
bd ready                  # Show unblocked issues
bd list --status=open     # All open issues
bd create "Title" -t task # Create issue
bd update <id> --status in_progress  # Claim work
bd close <id>             # Complete
bd sync                   # Sync with git
```

## Git Workflow

```bash
git status
git add <files>
bd sync
git commit -m "..."
git push
```

## Utility

```bash
just clean                # Remove result symlinks
just help                 # Show all just commands
```
