# Contributing to Arda

Thank you for your interest in contributing to Arda! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branch Strategy](#branch-strategy)
- [Commit Messages](#commit-messages)
- [Pull Requests](#pull-requests)
- [Code Style](#code-style)
- [Testing](#testing)
- [Security](#security)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to the principles of open collaboration, respect, and constructive feedback. Please be professional and courteous in all interactions.

## Getting Started

### Prerequisites

- NixOS or Nix-enabled Linux distribution
- Git
- Age encryption tool (for secrets management development)

### Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/lorddevi/arda-core.git
cd arda-core

# Enter development environment (all tools auto-installed via Nix)
nix develop

# Verify the setup
nix flake check

# Format code before committing
nix fmt
```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch from `arda-v1` for your work:

```bash
# Update your local arda-v1 branch
git checkout arda-v1
git pull origin arda-v1

# Create a new feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/your-bugfix
# or
git checkout -b experiment/your-experiment
```

### 2. Make Changes

- Follow the coding standards (see [Code Style](#code-style))
- Write tests for new functionality
- Update documentation as needed
- Format code with `nix fmt` before committing

### 3. Commit Changes

We use conventional commits for clear history:

```bash
git add .
git commit -m "feat: add new service template for postgresql"
```

See [Commit Messages](#commit-messages) for more details.

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
# Then create a Pull Request on GitHub
```

## Branch Strategy

### Primary Branches

- **`arda-v1`**: Main development branch. All new features and fixes are merged here first.
- **`clan-core`**: Reference branch containing upstream clan-core code. Used for code extraction and comparison.

### Feature Branches

- **`feature/*`**: New features or significant enhancements
  - Examples: `feature/service-feature-role-hierarchy`, `feature/secret-rotation`
  - Merge strategy: Squash and merge to arda-v1

### Maintenance Branches

- **`bugfix/*`**: Bug fixes for specific issues
  - Examples: `bugfix/nix-build-failure`, `bugfix/secrets-decryption`
  - Merge strategy: Squash and merge to arda-v1

### Experimental Branches

- **`experiment/*`**: Proof-of-concept work or exploratory development
  - Examples: `experiment/zfs-support`, `experiment/argo-cd-integration`
  - May or may not be merged, depending on results

### Version Branches (when needed)

- **`release/vX.Y.Z`**: Release preparation branches
  - Only created when preparing official releases
  - Final release tags created from these branches

### Branch Naming Conventions

```bash
{type}/{short-description}

Types:
- feature: New functionality
- bugfix: Bug fixes
- hotfix: Critical production fixes
- experiment: Exploratory work
- docs: Documentation updates
- chore: Maintenance tasks
```

Examples:

- `feature/web-server-role`
- `bugfix/age-key-rotation`
- `docs/readme-improvements`

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear, consistent commit messages.

### Format

```bash
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools
- `perf`: A code change that improves performance
- `ci`: Changes to CI configuration files and scripts

### Examples

```bash
# Feature
feat(cli): add web-server role definition

# Bug fix
fix(secrets): handle age key rotation edge case

# Documentation
docs(readme): add quick start guide

# Refactoring
refactor(roles): simplify role composition logic

# Breaking change
feat(cli)!: remove deprecated host create command

# Multiple types
feat(cli): add new templates
docs: update API documentation
test: add integration tests for templates
```

## Pull Requests

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Pre-commit hooks pass
- [ ] Tests pass (`nix flake check`)
- [ ] Documentation is updated (if needed)
- [ ] Commit messages follow conventional commit format
- [ ] Branch is up-to-date with arda-v1

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #issue-number

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

### Review Process

1. **Automated Checks**: CI/CD runs automatically (Nix builds, tests, linters)
2. **Code Review**: At least one maintainer reviews for:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Security considerations
3. **Testing**: Manual testing may be required for complex changes
4. **Approval**: Changes must be approved before merging

### Merge Strategies

- **Feature/Bugfix Branches**: Squash and merge
- **Large Features**: May use merge commit for preserving history
- **Hotfixes**: Fast-forward or squash merge

## Code Style

### Python (arda-cli)

We use Nix-provided Python tools via treefmt-nix:

```bash
# Format and lint everything (Python, Nix, shell, etc.)
nix fmt

# Format only specific files
nix fmt --config treefmt.programs.ruff.includes 'pkgs/arda-cli/**/*.py'
```

**Tools used:**

- `ruff` - Python formatter and linter (faster alternative to black + flake8)
- `mypy` - Type checking
- `nixfmt` - Nix file formatting

All tools are automatically available in `nix develop` environment.

Configuration files:

- `pyproject.toml`: ruff, mypy, and project metadata
- `formatter.nix`: treefmt-nix configuration

### Nix

Nix files are formatted automatically via treefmt-nix:

```bash
nix fmt
```

No manual formatting needed!

### General Guidelines

- Follow PEP 8 for Python
- Use meaningful variable and function names
- Write docstrings for all public functions
- Keep functions small and focused
- Prefer composition over inheritance
- Write tests for new functionality

## Console Output System

Arda uses a centralized console output system that provides consistent, themed, and debuggable output across all commands. This system is implemented in `pkgs/arda-cli/arda_cli/lib/output.py` through the `OutputManager` class.

### Why This System?

The console output system ensures:

- **Consistency** - All commands use the same output style
- **User Experience** - Beautiful, themed output with helpful tags and metadata
- **Debuggability** - Verbosity levels help troubleshoot issues
- **Maintainability** - Single source of truth for all output logic

### Core Concepts

#### Message Types

Each output message has a specific type with a distinct tag and color:

| Message Type | Tag Format | Color | Usage Example |
|-------------|-----------|-------|---------------|
| Information | `[i INFO]` | Blue | General status updates |
| Success | `[✓ SUCCESS]` | Green | Successful operations |
| Warning | `[⚠ WARNING]` | Yellow | Non-critical issues |
| Error | `[✗ ERROR]` | Red | Critical failures |
| Debug | `[→ DEBUG]` | Dim | Detailed info (with `--verbose`) |
| Trace | `[⋙ TRACE]` | Dim | Execution traces (debug mode) |

**Example output:**

```
[i INFO] Starting deployment
[✓ SUCCESS] Configuration validated
[⚠ WARNING] 2 hosts need attention
[✗ ERROR] Connection failed to host3
```

#### Verbosity Levels

Use verbosity to control output detail:

1. **NORMAL** (default) - Standard user-facing messages
2. **VERBOSE** (`--verbose` flag) - Adds debug information for troubleshooting
3. **DEBUG** (future) - Full execution traces

**Examples:**

```bash
arda host                    # Shows only info/success/warning/error
arda --verbose host          # Also shows debug messages
arda --verbose --debug host  # Shows all debug and trace info
```

#### Themes

Arda uses rich-click's built-in themes for unified styling:

- Available: `dracula`, `forest`, `nord`, `quartz`, `solarized`, etc.
- Theme variants: `slim`, `modern`, `nu`, `robo` (e.g., `dracula-modern`)
- Default: `dracula`

**Examples:**

```bash
arda --theme nord host
arda --theme forest list
```

#### Timestamps

Optional timestamp prefix for tracking when messages were generated:

```bash
[2025-11-22 17:14:04] [INFO] Starting operation
```

Controlled via flags: `--timestamp` / `--no-timestamp`

### Using the Output System

#### Basic Usage in Commands

Every command should follow this pattern:

```python
@rclick.command(no_args_is_help=True)
@click.pass_context
def host(ctx: click.Context) -> None:
    """Host management commands."""
    output = get_output_manager(ctx)

    # Show user-facing messages
    output.info("Loading hosts...")
    output.success("Found 5 hosts")

    # Show warnings when needed
    if attention_needed:
        output.warning("2 hosts need attention")

    # Show debug info (only with --verbose)
    output.section("Available operations")
    output.debug("• List all hosts")
    output.debug("• Deploy configuration")
    output.debug("• Update host settings")
```

#### Available Methods

**Message Output:**

- `output.info(message)` - Information messages
- `output.success(message)` - Success confirmations
- `output.warning(message)` - Warnings
- `output.error(message)` - Errors
- `output.debug(message)` - Debug info (with `--verbose`)

**Layout Helpers:**

- `output.section(title)` - Create section headers with separators
- `output.spacer(count=1)` - Add empty lines
- `output.print_panel(content, title, border_style)` - Display in bordered panel

**Debugging Helpers:**

- `output.timer("operation")` - Context manager to time operations
- `output.trace_function_entry(name, **kwargs)` - Log function entry
- `output.trace_function_exit(name, result)` - Log function exit
- `output.step(message)` - Numbered execution steps

**Example with timing:**

```python
with output.timer("Host deployment"):
    deploy_hosts()
    # Output: "⏱ Starting Host deployment" (with --verbose)
    #        "✓ Host deployment complete (2.345s)" (with --verbose)
```

#### Configuration

Settings are sourced from (priority order):

1. Command-line flags
2. Config file locations (checked in this order):
   - `~/.config/arda/arda.toml` (XDG user config)
   - `etc/arda.toml` (project-level config)
   - `./arda.toml` (current directory)
   - Package default fallback
3. Default values

**Config file example:**

```toml
[theme]
default = "nord"

[output]
verbose = false
timestamp = true
```

### When to Use Each Message Type

#### Use `info()` for

- General status updates
- Progress indicators
- Informational messages
- Command descriptions

#### Use `success()` for

- Successful operations
- Validations passed
- Configuration checks
- Completion confirmations

#### Use `warning()` for

- Non-critical issues
- Missing optional dependencies
- Degraded functionality warnings
- Actions that need user attention

#### Use `error()` for

- Critical failures
- Failed validations
- Configuration errors
- Operations that cannot proceed

#### Use `debug()` for

- Detailed operation info
- Internal state
- Non-essential troubleshooting info
- Available operations lists

**Example guidance:**

```python
# Good
output.info("Reading configuration file")
output.success("Configuration valid")
output.warning("Optional dependency 'age' not found")
output.error("Configuration file not found")

# Avoid these anti-patterns:
output.info("Successfully opened file")  # Success, not info
output.error("Warning: disk space low")  # Warning, not error
output.debug("Starting function")        # Too verbose for debug
```

### Best Practices for Development

#### 1. Use `no_args_is_help=True`

All commands should show help by default when no arguments are provided:

```python
@rclick.command(no_args_is_help=True)
@click.pass_context
def host(ctx: click.Context) -> None:
```

This gives users immediate feedback on command usage.

#### 2. Think About Verbosity When Adding Features

When implementing new features, consider:

- What would users need to debug issues?
- What internal steps might be helpful with `--verbose`?
- What errors might occur and how should they be communicated?

**Example:**

```python
# Show progress to all users
output.info("Validating configuration")

# Show detailed checks with --verbose
if verbose:
    output.debug("Checking syntax...")
    output.debug("Validating schema...")
    output.debug("Verifying dependencies...")

# Show results to all users
if validation_passed:
    output.success("Configuration is valid")
else:
    output.error("Configuration validation failed")
```

#### 3. Group Related Information with `section()`

Use section headers to organize output:

```python
output.section("Configuration")
output.info(f"Theme: {theme}")
output.info(f"Verbose: {verbose}")

output.section("Results")
output.success("Operation completed")
```

#### 4. Use Timesters for Performance Debugging

When investigating performance issues:

```python
with output.timer("Host discovery"):
    hosts = discover_hosts()
# Shows: "⏱ Starting Host discovery" and "✓ Host discovery complete (1.234s)"
```

#### 5. Leverage Trace Helpers for Complex Operations

For debugging complex flows:

```python
def deploy_role(hostname: str, role: str) -> None:
    output.trace_function_entry("deploy_role", hostname=hostname, role=role)

    with output.step("Checking prerequisites"):
        check_prerequisites()

    with output.step("Applying configuration"):
        apply_config(hostname, role)

    output.trace_function_exit("deploy_role", result="success")
```

### Example: Complete Command Implementation

```python
@rclick.command(no_args_is_help=True)
@click.pass_context
@click.option("--dry-run", is_flag=True, help="Show what would be deployed")
def deploy(ctx: click.Context, dry_run: bool) -> None:
    """Deploy configuration to hosts."""
    output = get_output_manager(ctx)

    output.info("Starting deployment...")

    if dry_run:
        output.warning("DRY RUN MODE - No changes will be made")
        output.debug("Skipping actual deployment")
        return

    with output.timer("Full deployment"):
        output.section("Phase 1: Validation")
        output.debug("Validating configuration...")
        if not validate_config():
            output.error("Configuration validation failed")
            return

        output.section("Phase 2: Deployment")
        for host in get_hosts():
            output.info(f"Deploying to {host}")
            if deploy_to_host(host):
                output.success(f"Successfully deployed to {host}")
            else:
                output.error(f"Failed to deploy to {host}")

        output.success("Deployment complete")
```

### Testing Output

When testing commands, verify both normal and verbose modes:

```bash
# Test normal output
arda host

# Test verbose output
arda --verbose host

# Test different themes
arda --theme nord host
arda --theme dracula host
```

### Troubleshooting Output Issues

If output doesn't appear as expected:

1. **Check verbosity level** - Some messages only show with `--verbose`
2. **Verify theme** - Colors might not be visible in certain themes
3. **Check timestamps** - Enabled/disabled via flags
4. **Review config** - Check `~/.config/arda/arda.toml`

For debugging the output system itself:

```python
# Add temporary debug output
output.debug(f"Current verbosity: {output.verbosity}")
output.debug(f"Current theme: {output.theme}")
output.debug(f"Timestamps enabled: {output.timestamps}")
```

## Testing

### Test Structure

```bash
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
└── e2e/              # End-to-end tests
```

### Running Tests

```bash
# All tests
nix flake check

# Specific test suite
pytest tests/unit/

# With coverage
pytest --cov=pkgs/arda-cli tests/
```

### Writing Tests

- Unit tests should be fast and isolated
- Integration tests should test component interactions
- End-to-end tests should verify complete workflows
- Use pytest fixtures for setup/teardown
- Mock external dependencies

## Security

### Secret Detection

Nix-based projects rely on proper `.gitignore` patterns and repository hygiene:

```bash
# Follow the .gitignore patterns for secrets
# - Do not commit .sops.yaml files
# - Do not commit *.age key files
# - Do not commit secrets/ directory

# Review changes before committing
git diff --staged
```

### Reporting Security Issues

**Do not** create public issues for security vulnerabilities.

Instead:

- Email: [your-secure-email@example.com]
- Include: Description, steps to reproduce, potential impact
- You will receive acknowledgment within 48 hours

### Secure Development Practices

- Never commit secrets, keys, or passwords
- Use the secret management system for all secrets
- Review code before committing for potential data leaks
- Follow the principle of least privilege

## Documentation

### Types of Documentation

1. **API Documentation**: Docstrings in code
2. **User Guides**: How-to guides in `docs/user/`
3. **Architecture**: Design documents in `docs/architecture/`
4. **Development**: Developer guides (this document)

### Writing Documentation

- Use clear, concise language
- Provide examples for complex concepts
- Keep documentation up-to-date with code changes
- Use markdown formatting consistently
- Include diagrams where helpful

### Documentation Tools

- Markdown for most documentation
- Mermaid for diagrams
- Sphinx for API documentation (future)

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for general questions
- Review existing issues and discussions first

## Recognition

Contributors will be recognized in:

- README.md contributors section
- CHANGELOG.md
- Release notes

Thank you for contributing to Arda! 🎉
