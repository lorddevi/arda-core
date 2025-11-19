# Contributing to Arda CLI

Thank you for your interest in contributing to Arda CLI! This document provides guidelines and information for contributors.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Style](#code-style)
- [Theme System](#theme-system)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
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

```
arda_cli/
├── __init__.py              # Package initialization
├── main.py                  # CLI entry point with rich-click
├── theme.py                 # ThemeManager for YAML themes
├── themes/                  # YAML theme files (auto-generated)
│   ├── greyscale.yaml       # Default theme
│   ├── matrix.yaml          # Green theme
│   └── ocean.yaml           # Blue theme
├── styling/                 # Styling utilities
│   ├── __init__.py
│   ├── gradients.py         # Gradient text helpers
│   └── prefixes.py          # Hostname/timestamp prefixers
```

### Key Components

- **`main.py`**: Click CLI with rich-click integration
- **`theme.py`**: ThemeManager loads YAML themes
- **`styling/gradients.py`**: Gradient text rendering
- **`styling/prefixes.py`**: Hostname and timestamp prefixes

## Code Style

### Python Standards

- **Python Version**: 3.11+
- **Type Hints**: Required for all functions
- **Line Length**: 88 characters (configured in pyproject.toml)
- **Formatter**: `ruff` (configured via Nix)

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
   theme_manager = ThemeManager(themes_dir)

   # Bad
   tm = ThemeManager(td)
   ```

4. **Document public APIs**:
   ```python
   def get_console(theme_name: str) -> Console:
       """Get a Console instance with the specified theme."""
       ...
   ```

### Pre-commit Hooks (Optional)

For automated linting, install pre-commit:

```bash
# In devShell
pip install pre-commit
pre-commit install

# Now linting runs automatically on git commit!
```

Or use Nix to set up hooks (configured in `pyproject.toml`):

### Rich and Click Patterns

#### Using Rich for Output

```python
from rich.console import Console
from rich.panel import Panel

console = Console()

# Use panels for structured output
panel = Panel(
    "[bold]Header[/bold]\n\nContent here",
    border_style="cyan"
)
console.print(panel)

# Use styled text
console.print("[info]ℹ Information[/info]")
console.print("[success]✓ Success[/success]")
console.print("[warning]⚠ Warning[/warning]")
console.print("[error]✗ Error[/error]")
```

#### Using Click for CLI

```python
import click

@click.command()
@click.option('--verbose', '-v', is_flag=True)
@click.pass_context
def command(ctx: click.Context, verbose: bool):
    """Command description."""
    console = ctx.obj['console']

    if verbose:
        console.print("[info]Verbose mode enabled[/info]")
```

## Theme System

### Understanding Themes

Themes are defined in YAML files and loaded by `ThemeManager`.

### Theme File Format

```yaml
# themes/example.yaml
info: cyan              # Information messages
success: green          # Success states
warning: yellow         # Warnings
error: bold red         # Errors
command: bold blue      # Commands being run
accent: magenta         # Highlights
muted: dim white        # Secondary text
title: bold cyan        # Section headers
border: cyan            # Panel borders

# Prefix colors (future use)
hostname_brackets: dim white
hostname_name: cyan
hostname_colon: dim white
timestamp: dim white
output: white
debug: dim white
```

### Using Themes in Code

```python
from .theme import ThemeManager
from .styling import gradient_text

# Get themed console
console = theme_manager.get_console('greyscale')

# Get theme colors
colors = theme_manager.get_colors('matrix')

# Create gradient text
gradient = gradient_text("TEXT", "green", "bright_green")
console.print(gradient)
```

### Creating a New Theme

1. Create YAML file in `themes/`:
   ```yaml
   info: blue
   success: green
   warning: yellow
   error: red
   # ... other colors
   ```

2. Use in code:
   ```python
   console = theme_manager.get_console('my_theme')
   ```

3. Test:
   ```bash
   arda --theme my_theme host
   ```

### Adding New Theme Colors

When adding new color categories:

1. Update all theme YAML files
2. Update `ThemeManager._create_default_themes()` in `theme.py`
3. Document in this file

### Gradient System

Gradients are created using Rich's `Text` objects with character-by-character styling.

```python
from .styling import gradient_text, multi_color_gradient

# Simple gradient
gradient = gradient_text("HELLO", "red", "blue")

# Multi-color gradient
rainbow = multi_color_gradient("RAINBOW", "red", "yellow", "green", "cyan", "blue")
```

### Prefix System

Hostname and timestamp prefixes provide context for operations:

```python
from .styling import with_host_prefix, with_timestamp, with_full_context

# Hostname prefix
text = with_host_prefix("nixos-01", "Installing...", colors)
console.print(text)
# Output: [nixos-01]: Installing...

# Timestamp prefix
text = with_timestamp("Starting", colors, timestamp=True)
console.print(text)
# Output: [14:23:45] Starting

# Combined
text = with_full_context("web-01", "Updating...", colors, timestamp=True)
console.print(text)
# Output: [14:23:45] [web-01]: Updating...
```

## Adding New Features

### Command Structure

Commands follow this pattern:

```python
@main.command()
@click.option('--option', help='Option description')
@click.pass_context
def command_name(ctx: click.Context, option):
    """Command description."""
    console = ctx.obj['console']

    # Use themed output
    console.print("[info]Message[/info]")
```

### Theme Integration

All commands should:

1. Accept `ctx` parameter with `@click.pass_context`
2. Use `ctx.obj['console']` for output
3. Use theme-based styles (info, success, warning, error, etc.)
4. Support the `--theme` option automatically

### Example: Adding a New Command

```python
@main.command()
@click.option('--name', required=True, help='Host name')
@click.pass_context
def check(ctx: click.Context, name: str):
    """Check host status."""
    console = ctx.obj['console']

    console.print(f"[title]Checking {name}[/title]")

    # Use styled output
    console.print(f"[info]ℹ Checking host: {name}[/info]")
    console.print(f"[success]✓ Host {name} is online[/success]")
```

## Testing and Linting

### Development Tools

We use a comprehensive Python linting and testing suite:

- **Ruff**: Fast linter, formatter, and import sorter
- **mypy**: Static type checker
- **pytest**: Testing framework with coverage
- **Bandit**: Security linter
- **pre-commit**: Git hook framework (optional)

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
feat: add network-based theme support
fix: resolve hostname prefix color issue
docs: update theme system documentation
style: format code with ruff
refactor: simplify gradient text implementation
test: add tests for theme switching
```

### Pull Request Process

1. **Ensure code follows style guidelines** (type hints, 88-char lines)
2. **Test all themes** work correctly
3. **Update documentation** if needed
4. **Build succeeds** with `nix build .#arda-cli`
5. **Submit PR** with clear description

## Theme Color Reference

| Style | Usage |
|-------|-------|
| `info` | General information messages |
| `success` | Successful operations |
| `warning` | Warnings that need attention |
| `error` | Error messages and failures |
| `command` | Commands being executed |
| `output` | Command output |
| `accent` | Highlights and emphasis |
| `muted` | Secondary/descriptive text |
| `title` | Section headers and titles |
| `border` | Panel and box borders |
| `hostname_*` | Hostname prefix components |
| `timestamp` | Timestamp prefixes |
| `debug` | Debug output |

## Common Tasks

### Updating Dependencies

Edit `pyproject.toml` and rebuild:

```bash
# Edit dependencies
vim pyproject.toml

# Rebuild
nix build .#arda-cli
```

### Modifying Themes

Edit YAML files in `themes/` directory. Changes take effect on next build.

### Adding New Styling Utilities

1. Create function in appropriate `styling/` module
2. Export in `styling/__init__.py`
3. Document with docstring
4. Add example to this file

## Resources

- [Rich Documentation](https://rich.readthedocs.io/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Nixpkgs](https://nixos.org/nixpkgs/)
- [Ruff Linter](https://beta.ruff.rs/docs/)

## Questions?

Feel free to open an issue for questions about contributing!
