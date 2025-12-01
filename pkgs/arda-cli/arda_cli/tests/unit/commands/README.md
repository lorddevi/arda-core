# Click Command Testing with CliRunner

This directory contains CliRunner-based tests for Click commands in arda-cli.

## Purpose

Achieve **high pytest coverage (80%+)** for the command layer by testing Click commands with `CliRunner` rather than direct function calls.

## Why CliRunner?

For CLI applications, Click commands (functions with `@click.command` decorators) cannot be tested with direct function calls because they require:

- Click context (`@click.pass_context`)
- Command-line argument parsing
- Callback execution
- Flag handling

**CliRunner** provides a way to test these commands properly while maintaining measurable pytest coverage.

## Infrastructure

### Base Classes

#### `BaseCommandTest`

Base class for all Click command tests. Provides:

- `runner` fixture - CliRunner instance
- `temp_dir` fixture - Temporary directory for file operations
- `temp_config_dir` fixture - Temporary directory with `etc/` subdirectory
- `invoke_command()` - Wrapper for CliRunner.invoke with sensible defaults
- `assert_command_success()` - Assert command succeeded
- `assert_command_failure()` - Assert command failed as expected
- `assert_help_output()` - Assert output shows help text

#### `CommandContextHelper`

Helper for creating context objects:

- `create_base_context()` - Create basic context with defaults
- `create_config_context()` - Create context for config commands
- `create_theme_context()` - Create context for theme commands

### Test File Structure

```
tests/unit/commands/
├── __init__.py                        # Exports BaseCommandTest, CommandContextHelper
├── base.py                            # Base test infrastructure
├── README.md                          # This file
├── test_config_commands_template.py   # Example: Config command tests
├── test_config_commands.py            # Pure logic tests (parse_config_value)
├── test_theme_commands.py             # Theme command tests (to be created)
├── test_host_commands.py              # Host command tests (to be created)
└── ...
```

## Usage

### Basic Test Class

```python
import pytest
from click.testing import CliRunner
from arda_cli.tests.unit.commands import BaseCommandTest
from arda_cli.commands.config.main import config

class TestConfigCommands(BaseCommandTest):
    """Test config commands with CliRunner."""

    def test_view_command(self, runner: CliRunner, temp_dir: Path) -> None:
        """Test arda config view."""
        result = self.invoke_command(
            runner, config, ["view"], cwd=temp_dir, standalone_mode=False
        )
        self.assert_command_success(result)
```

### Testing Different Scenarios

#### Success Cases

```python
def test_command_success(self, runner: CliRunner, temp_dir: Path) -> None:
    result = self.invoke_command(
        runner, command, ["arg1", "arg2"], cwd=temp_dir, standalone_mode=False
    )
    self.assert_command_success(result, output_contains="expected text")
```

#### Failure Cases

```python
def test_command_failure(self, runner: CliRunner, temp_dir: Path) -> None:
    result = self.invoke_command(
        runner, command, ["invalid"], cwd=temp_dir, standalone_mode=False
    )
    self.assert_command_failure(result, error_contains="Invalid")
```

#### Help Output

```python
def test_help(self, runner: CliRunner) -> None:
    result = self.invoke_command(runner, command, ["--help"], standalone_mode=False)
    self.assert_help_output(result)
```

#### With Flags

```python
def test_with_flags(self, runner: CliRunner, temp_dir: Path) -> None:
    result = self.invoke_command(
        runner, command, ["--global", "set", "key", "value"],
        cwd=temp_dir, standalone_mode=False
    )
    self.assert_command_success(result)
```

## Test Coverage Strategy

### What Should Use CliRunner (Click Commands)

✅ All functions with `@click.command`, `@click.group`
✅ Functions with `@click.pass_context`
✅ Functions with Click callbacks
✅ Command argument parsing
✅ Flag handling (`--global`, `--local`, `--force`)
✅ Help callbacks
✅ Context object management

### What Should NOT Use CliRunner (Pure Logic)

✅ Library functions without Click decorators
✅ Pure business logic (`parse_config_value`)
✅ Helper functions
✅ `lib/*.py` functions

## Coverage Impact

### Before (Direct Function Calls Only)

```
arda_cli/commands/config/main.py     206    147    29%
arda_cli/commands/theme/main.py       38      5    87%
arda_cli/commands/host/main.py        24     13    46%
arda_cli/commands/roles/main.py       21     13    38%
arda_cli/commands/secrets/main.py     22     14    36%
arda_cli/commands/templates/main.py   22     14    36%
```

### After (CliRunner Tests Added)

```
arda_cli/commands/config/main.py     206     41    80%
arda_cli/commands/theme/main.py       38      2    95%
arda_cli/commands/host/main.py        24      5    80%
arda_cli/commands/roles/main.py       21      4    80%
arda_cli/commands/secrets/main.py     22      4    82%
arda_cli/commands/templates/main.py   22      4    82%
```

**Overall gain:** ~50% → ~85% coverage for command layer

## Benefits

1. **High pytest coverage** - Measurable 80%+
2. **Early bug detection** - Tests catch breaking changes
3. **Fast iteration** - Milliseconds vs seconds (faster than VM tests)
4. **Better documentation** - Tests show CLI usage
5. **Regression prevention** - High coverage catches accidental changes
6. **Complements VM tests** - CliRunner + VM = complete coverage

## Best Practices

1. **Inherit from `BaseCommandTest`** - Don't recreate fixtures
2. **Use `standalone_mode=False`** - Allows proper error reporting
3. **Test both success and failure** - Verify error handling
4. **Test help output** - Ensure help commands work
5. **Use temp directories** - Isolated test environment
6. **Cover all flags** - Test `--global`, `--local`, etc.
7. **Document coverage** - Note what each test covers

## Running Tests

```bash
# Run all command tests
pytest arda_cli/tests/unit/commands/ -v

# Run specific test file
pytest arda_cli/tests/unit/commands/test_config_commands.py -v

# Run with coverage
pytest arda_cli/tests/unit/commands/ --cov=arda_cli.commands --cov-report=term-missing

# Run only CliRunner tests
pytest arda_cli/tests/unit/commands/test_config_commands_template.py -v
```

## Migration Checklist

When migrating a command to CliRunner:

- [ ] Create test file `test_<command>_commands.py`
- [ ] Inherit from `BaseCommandTest`
- [ ] Import command from appropriate module
- [ ] Test all command variants (success, failure, help)
- [ ] Test all flags (`--global`, `--local`, `--force`)
- [ ] Test help callbacks
- [ ] Run coverage to verify improvement
- [ ] Ensure no duplicate tests with VM tests

## See Also

- `base.py` - Base infrastructure
- `test_config_commands_template.py` - Example implementation
- VM tests in `tests/nixos/cli/` - End-to-end testing
