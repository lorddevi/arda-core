# Contributing to Arda CLI

Thank you for your interest in contributing to Arda CLI! This document provides guidelines and information for contributors.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Architecture Philosophy](#architecture-philosophy)
- [Commands Directory](#commands-directory)
- [Library (lib/) Directory](#library-lib-directory)
- [Code Style](#code-style)
- [Adding New Commands](#adding-new-commands)
- [Using Shared Helpers](#using-shared-helpers)
- [Theme System](#theme-system)
- [Testing](#testing)
- [Development Workflow](#development-workflow)
- [Submitting Changes](#submitting-changes)

## Development Setup

### Using Nix (Recommended)

Arda CLI uses Nix for reproducible development environments.

```bash
# Enter development shell with all dependencies
nix develop

# Build the CLI
nix build .#arda-cli

# Test the built binary
./result/bin/arda --help

# Format code
nix fmt
```

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd arda-core/pkgs/arda-cli

# Enter development environment
nix develop

# Test the build
nix build .#arda-cli
./result/bin/arda --version
```

## Project Structure

Arda CLI follows a **modular architecture** designed for maintainability, scalability, and learning.

```
arda_cli/
├── __init__.py              # Package initialization
├── main.py                  # CLI entry point (minimal)
├── commands/                # All command implementations
│   ├── __init__.py
│   ├── main.py             # Root: arda
│   ├── host/               # arda host commands
│   │   ├── __init__.py
│   │   ├── main.py         # arda host
│   │   └── deploy/         # arda host deploy commands
│   │       ├── __init__.py
│   │       ├── main.py     # arda host deploy
│   │       ├── day0.py     # arda host deploy day0
│   │       └── update.py   # arda host deploy update
│   ├── roles/              # arda roles commands
│   ├── secrets/            # arda secrets commands
│   ├── templates/          # arda templates commands
│   └── theme/              # arda theme commands
└── lib/                    # Shared helpers (DRY principle)
    ├── __init__.py
    ├── console.py          # Console creation, theming
    ├── styling.py          # Rich styling helpers
    ├── ssh.py              # SSH utilities
    ├── host.py             # Host operations
    ├── nix.py              # Nix operations
    ├── config.py           # Config file I/O
    ├── network.py          # Network utilities
    ├── logging.py          # Logging helpers
    └── exceptions.py       # Custom exceptions
```

### Key Principles

- **`commands/`**: "What the CLI does" - user-facing command implementations
- **`lib/`**: "How it does it" - reusable helper functions and utilities
- **DRY**: Don't Repeat Yourself - extract common logic to `lib/`
- **Modularity**: Each command = its own file or directory
- **Discoverability**: File structure mirrors command structure

## Architecture Philosophy

### Why This Structure?

1. **Learnable**: Code structure matches command structure
   - `commands/host/deploy/day0.py` → `arda host deploy day0`

2. **Maintainable**: Each command is self-contained
   - Changes to one command don't affect others
   - Easy to test individual commands

3. **Extensible**: Add new commands by adding files
   - No need to modify existing code
   - Just import and register the new command

4. **Testable**: Test helpers independently
   - `lib/ssh.py` tests don't need CLI context
   - `commands/host/` tests can focus on command logic

5. **DRY Principle**: Reuse code through `lib/`
   - Shared utilities live in `lib/`
   - All commands use the same helpers
   - Updates in one place affect all commands

### Command Hierarchy Pattern

Commands follow a consistent pattern:

```
<command> <subcommand> <action> [arguments] [options]

Examples:
arda host deploy day0 hostname --ip 192.168.1.1
arda host deploy update hostname --port 22
arda theme --list
```

Each level in the command hierarchy maps to a directory level in `commands/`.

## Commands Directory

The `commands/` directory contains all CLI command implementations. It mirrors the command hierarchy exactly.

### Command File Pattern

Each command file defines one or more Click commands:

```python
# commands/host/main.py
import click
from rich.console import Console

@click.group()
@click.pass_context
def host(ctx):
    """Host management commands."""
    ctx.ensure_object(dict)

@host.command()
@click.option('--verbose', '-v', is_flag=True)
@click.pass_context
def list(ctx, verbose):
    """List all hosts."""
    console = ctx.obj['console']
    if verbose:
        console.print("Verbose mode enabled")
    console.print("Listing hosts...")
```

### Command Registration

Commands are registered with their parent groups:

```python
# In commands/host/main.py
from .deploy.main import deploy  # Import deploy group
host.add_command(deploy)          # Register it

# In commands/host/deploy/main.py
from .day0 import day0
from .update import update
deploy.add_command(day0)
deploy.add_command(update)
```

This creates the hierarchy:
- `arda host list` → from `commands/host/main.py`
- `arda host deploy day0` → from `commands/host/deploy/day0.py`
- `arda host deploy update` → from `commands/host/deploy/update.py`

### Single Command Per File

For leaf commands (commands with no subcommands), use one file per command:

```python
# commands/host/deploy/day0.py
@click.command()
@click.argument('hostname')
@click.option('--ip', default='192.168.1.1')
@click.pass_context
def day0(ctx, hostname, ip):
    """Deploy day0 configuration to a host."""
    ...
```

### Group Commands Per Directory

For commands with subcommands, create a `main.py` in the directory:

```
commands/host/
├── main.py         # Defines the 'host' group
├── list.py         # arda host list
└── deploy/         # arda host deploy
    ├── main.py     # Defines the 'deploy' group
    ├── day0.py     # arda host deploy day0
    └── update.py   # arda host deploy update
```

## Library (lib/) Directory

The `lib/` directory contains shared helper functions - the **DRY principle** in action.

### Why lib/?

1. **Avoid Code Duplication**: Write logic once, use everywhere
2. **Test Independently**: Test helpers without CLI context
3. **Update in One Place**: Fix a bug, it fixes all uses
4. **Clear Dependencies**: Commands depend on lib, not vice versa

### lib/ File Organization

Each `lib/` file focuses on one purpose:

```
lib/
├── console.py      # Console creation and theming
├── styling.py      # Rich styling helpers (panels, colors)
├── ssh.py          # SSH connection and remote execution
├── host.py         # Host management operations
├── nix.py          # Nix operations (build, eval)
├── config.py       # Configuration file I/O
├── network.py      # Network utilities
├── logging.py      # Logging helpers
└── exceptions.py   # Custom exception classes
```

### Example lib/ File

```python
# lib/ssh.py
"""SSH and remote execution helpers."""
import subprocess
from typing import Optional

def test_ssh_connection(host: str, port: int = 22, timeout: int = 5) -> bool:
    """Test SSH connection to host.

    Args:
        host: Hostname or IP address
        port: SSH port (default: 22)
        timeout: Connection timeout in seconds

    Returns:
        True if connection successful, False otherwise
    """
    try:
        result = subprocess.run(
            ["ssh", "-p", str(port), host, "echo 'connected'"],
            capture_output=True,
            timeout=timeout
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False

def run_remote_command(host: str, command: str, port: int = 22) -> tuple[int, str, str]:
    """Run a command on remote host via SSH.

    Args:
        host: Hostname or IP address
        command: Command to run
        port: SSH port

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    result = subprocess.run(
        ["ssh", "-p", str(port), host, command],
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr
```

### Using lib/ in Commands

```python
# commands/host/deploy/day0.py
import click
from arda_cli.lib.styling import print_header, print_success, print_error
from arda_cli.lib.ssh import test_ssh_connection
from arda_cli.lib.host import load_hosts_config

@click.command()
@click.argument('hostname')
@click.option('--ip', help='Target IP address')
@click.pass_context
def day0(ctx, hostname, ip):
    """Deploy day0 configuration to a host."""
    console = ctx.obj['console']

    print_header(f"Day0 Deploy: {hostname}", console)

    # Use shared helpers
    if test_ssh_connection(hostname, 22):
        print_success("SSH connection successful", console)
    else:
        print_error("SSH connection failed", console)
```

## Code Style

### Python Standards

- **Python Version**: 3.11+
- **Type Hints**: Required for all functions
- **Line Length**: 88 characters (configured in pyproject.toml)
- **Formatter**: `ruff` (configured via pyproject.toml)

### Code Style Requirements

1. **Always use type hints**:
   ```python
   def function_name(param: str) -> bool:
       """Function description."""
       return True
   ```

2. **Use f-strings for formatting**:
   ```python
   message = f"Host {hostname}: {status}"
   ```

3. **Use descriptive names**:
   ```python
   # Good
   hosts_config = load_hosts_config(config_path)

   # Bad
   h = load_hosts_config(c)
   ```

4. **Document public APIs**:
   ```python
   def create_console(theme_name: str) -> Console:
       """Create a themed Console instance.

       Args:
           theme_name: Name of the rich-click theme to use

       Returns:
           Configured Console instance with theme
       """
       ...
   ```

5. **One function = one responsibility**:
   ```python
   # Good: Separate functions for separate concerns
   def test_ssh_connection(host: str, port: int) -> bool: ...
   def run_remote_command(host: str, command: str) -> tuple[int, str, str]: ...

   # Bad: Mixed concerns
   def ssh_operation(host, port, command, verbose): ...
   ```

### Pre-commit Hooks (Optional)

For automated linting, use the tools in devShell:

```bash
# In devShell
ruff check .          # Lint code
ruff format .         # Format code
mypy .                # Type check
bandit -r arda_cli/   # Security check
```

## Adding New Commands

To add a new command to Arda CLI:

### Step 1: Create the Command File

Decide where the command belongs in the hierarchy:

```bash
# New command: arda host install PACKAGE
# File: commands/host/install.py

import click

@click.command()
@click.argument('package')
@click.pass_context
def install(ctx, package):
    """Install a package on a host."""
    console = ctx.obj['console']
    console.print(f"Installing {package}...")
```

### Step 2: Register the Command

In the parent command file:

```python
# commands/host/main.py
from .install import install  # Import the new command
host.add_command(install)      # Register it
```

### Step 3: Extract Shared Logic to lib/

If the command uses logic that might be useful elsewhere:

```python
# lib/package.py
"""Package management helpers."""
def install_package(package: str, host: str) -> bool:
    """Install a package on a host via SSH."""
    ...
```

```python
# commands/host/install.py
from arda_cli.lib.package import install_package

@click.command()
@click.argument('package')
@click.pass_context
def install(ctx, package):
    """Install a package on a host."""
    console = ctx.obj['console']
    if install_package(package, ctx.obj['host']):
        console.print("[success]✓ Package installed[/success]")
    else:
        console.print("[error]✗ Installation failed[/error]")
```

### Step 4: Add Tests

Create test file matching command location:

```python
# tests/commands/host/test_install.py
from click.testing import CliRunner
from commands.host.install import install

def test_install_package():
    """Test package installation command."""
    runner = CliRunner()
    result = runner.invoke(install, ['vim'])
    assert result.exit_code == 0
    assert 'Installing vim' in result.output
```

## Using Shared Helpers

All commands should use shared helpers from `lib/` instead of duplicating logic.

### Common Helper Modules

**lib/console.py** - Console and theming:
```python
from arda_cli.lib.console import get_console_from_ctx

console = get_console_from_ctx(ctx)
```

**lib/styling.py** - Rich output helpers:
```python
from arda_cli.lib.styling import print_header, print_success, print_error

print_header("Operation", console)
print_success("Success!", console)
print_error("Failed!", console)
```

**lib/ssh.py** - SSH operations:
```python
from arda_cli.lib.ssh import test_ssh_connection, run_remote_command

if test_ssh_connection(hostname):
    exit_code, stdout, stderr = run_remote_command(hostname, "nixos-rebuild switch")
```

**lib/nix.py** - Nix operations:
```python
from arda_cli.lib.nix import build_host_config, eval_flake

system_path = build_host_config(hostname)
```

### When to Create a New lib/ Module

Create a new `lib/` module when:
1. You need functionality not provided by existing modules
2. The functionality is used by multiple commands
3. It's a cohesive set of utilities (e.g., all SSH-related helpers)

```python
# lib/vm.py - New module for VM operations
"""VM management helpers."""

def create_vm(name: str, memory: int) -> str:
    """Create a VM with specified memory."""
    ...

def start_vm(name: str) -> bool:
    """Start a VM."""
    ...
```

## Theme System

Arda CLI uses **rich-click's built-in theming** system (version 1.9.0+).

### Available Themes

24 built-in themes from rich-click:
- Dracula variants: `dracula`, `dracula-dark`, `dracula-slim`, `dracula-modern`
- Forest variants: `forest`, `forest-dark`, `forest-slim`, `forest-modern`
- Solarized variants: `solarized`, `solarized-dark`, `solarized-slim`, `solarized-modern`
- Nord variants: `nord`, `nord-dark`, `nord-slim`, `nord-modern`
- Quartz variants: `quartz`, `quartz-dark`, `quartz-slim`, `quartz-modern`
- Monokai variants: `monokai`, `monokai-dark`, `monokai-slim`, `monokai-modern`

### Using Themes in Commands

Themes are automatically inherited from the parent command. Just use the console:

```python
@click.command()
@click.pass_context
def my_command(ctx):
    """My command with automatic theming."""
    console = ctx.obj['console']
    console.print("[info]ℹ Information")
    console.print("[success]✓ Success")
    console.print("[warning]⚠ Warning")
    console.print("[error]✗ Error")
```

### Theme Configuration

The `--theme` option is automatically added to the main command and passed through context. Commands access it via:

```python
theme = ctx.obj['theme']  # e.g., 'dracula', 'forest', 'nord'
```

## Testing and Linting

### Development Tools

We use a comprehensive Python linting and testing suite:

- **Ruff**: Fast linter, formatter, and import sorter
- **mypy**: Static type checker
- **pytest**: Testing framework with coverage
- **Bandit**: Security linter

All tools are configured in `pyproject.toml` and available in the Nix devShell.

### Running Linters and Tests

```bash
# Enter development environment
nix develop

# Run all linters (Ruff checks everything)
ruff check .

# Auto-fix issues where possible
ruff check --fix .

# Format code
ruff format .

# Run type checking
mypy .

# Run security checks
bandit -r arda_cli/

# Run tests with coverage
pytest --cov=arda_cli --cov-report=term-missing

# Run a specific test
pytest tests/test_main.py -v
```

### Testing Structure

Tests mirror the source code structure:

```
tests/
└── commands/
    ├── test_main.py            # Test root command
    └── host/
        ├── test_host_main.py   # Test arda host
        └── deploy/
            ├── test_deploy_main.py  # Test arda host deploy
            └── test_day0.py         # Test arda host deploy day0

lib/
└── test_ssh.py                 # Test lib/ssh.py helpers
```

### Test Guidelines

1. **Test commands in isolation**:
   ```python
   from commands.host.deploy.day0 import day0
   result = runner.invoke(day0, ['hostname'])
   ```

2. **Test lib/ helpers without CLI context**:
   ```python
   from arda_cli.lib.ssh import test_ssh_connection
   assert test_ssh_connection('localhost') == True
   ```

3. **Mock external dependencies** (SSH, network, etc.):
   ```python
   @patch('subprocess.run')
   def test_ssh_connection(mock_run):
       mock_run.return_value.returncode = 0
       assert test_ssh_connection('test-host') == True
   ```

## Development Workflow

### Typical Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Write tests first** (TDD approach):
   ```bash
   # Create test file
   touch tests/commands/host/test_new_command.py
   # Write failing test
   pytest tests/commands/host/test_new_command.py  # Should fail
   ```

3. **Implement the feature**:
   - Create command in `commands/`
   - Extract shared logic to `lib/`
   - Run tests: `pytest tests/commands/host/test_new_command.py`

4. **Run all checks**:
   ```bash
   ruff check .
   ruff format .
   mypy .
   pytest
   nix build .#arda-cli
   ```

5. **Build and test the CLI**:
   ```bash
   nix build .#arda-cli
   ./result/bin/arda my-command --help
   ```

6. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: add new command"
   git push origin feature/my-new-feature
   ```

### Testing Workflow

Before submitting changes:

```bash
# 1. Check code style and linting
ruff check .
ruff format --check .

# 2. Run type checker
mypy .

# 3. Run tests
pytest

# 4. Security check
bandit -r arda_cli/

# 5. Build package
nix build .#arda-cli

# 6. Test built binary
./result/bin/arda --help
./result/bin/arda --theme forest host --help
```

### Manual Testing Checklist

When adding features, manually test:

1. ✅ Build succeeds without errors
2. ✅ All linters pass (`ruff check .`, `mypy .`)
3. ✅ Tests pass (`pytest`)
4. ✅ `--help` shows styled help text (rich-click)
5. ✅ `--theme` option works with all 24 rich-click themes
6. ✅ Theme commands (`theme --list`, `theme`) work correctly
7. ✅ All commands use themed output

## Submitting Changes

### Commit Message Format

Use conventional commits:

```
feat: add arda host deploy day0 command
fix: resolve SSH connection timeout issue
docs: update CONTRIBUTING.md with new lib/ structure
style: format code with ruff
refactor: extract SSH logic to lib/ssh.py
test: add tests for host deployment workflow
```

### Pull Request Process

1. **Ensure code follows style guidelines** (type hints, 88-char lines)
2. **All commands use lib/ helpers** (DRY principle)
3. **Tests for new features** (both commands and lib/ helpers)
4. **All linters pass** (`ruff check .`, `mypy .`)
5. **All tests pass** (`pytest`)
6. **Build succeeds** with `nix build .#arda-cli`
7. **Submit PR** with clear description

### Pull Request Description Template

```markdown
## Summary
Brief description of changes

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Type hints added
- [ ] Shared logic extracted to lib/
- [ ] Documentation updated
```

## Resources

- [Rich Documentation](https://rich.readthedocs.io/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Rich-Click Documentation](https://github.com/ewels/rich-click)
- [Nixpkgs](https://nixos.org/nixpkgs/)
- [Ruff Linter](https://beta.ruff.rs/docs/)
- [Python Type Hints Guide](https://docs.python.org/3/library/typing.html)

## Questions?

Feel free to open an issue for questions about:
- Project structure
- Adding new commands
- Using shared helpers
- Testing approach
- Architecture decisions

