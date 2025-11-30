# Testing Framework Guide

**Version**: 1.0
**Last Updated**: 2025-11-29
**Status**: Active Development

This document serves as a complete reference and guide for the arda-core testing framework. It covers test organization, execution, writing guidelines, and best practices for all contributors.

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Test Types](#test-types)
4. [Test Execution](#test-execution)
5. [Writing Tests](#writing-tests)
6. [VM Testing Guide](#vm-testing-guide)
7. [CI/CD Integration](#cicd-integration)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Quick Reference](#quick-reference)

---

## Overview

The arda-core testing framework is a multi-layered approach designed to ensure code quality through:

- **Fast Unit Tests**: Isolated function testing (< 10ms each)
- **Integration Tests**: Component interaction testing (10-100ms each)
- **VM Tests**: End-to-end testing in isolated virtual machines (2-5 minutes)
- **CI/CD Integration**: Automated testing on every push/PR

### Testing Philosophy

1. **Speed**: Fast tests run on every build and commit
2. **Isolation**: Tests don't interfere with each other
3. **Coverage**: Multiple test types for comprehensive coverage
4. **Automation**: Tests run automatically in CI/CD
5. **Developer Experience**: Easy to run, write, and debug

---

## Directory Structure

The testing framework is distributed across multiple directories:

```
/home/ld/src/arda-core/
├── docs/                          # This document (tracked by git)
│   └── TEST-FRAMEWORK.md         # Testing framework guide
│
├── bmad-docs/                     # Development docs (not tracked)
│   └── plan-testing.md           # Implementation plan & deviations
│
├── pkgs/arda-cli/arda_cli/tests/  # Main pytest test suite
│   ├── unit/                     # Fast unit tests
│   │   ├── cli/
│   │   │   └── test_cli_integration.py
│   │   ├── config/
│   │   │   └── test_parses_valid_toml.py
│   │   ├── overlay/
│   │   │   └── test_rich_click_version.py
│   │   └── themes/
│   │       └── test_theme_validation.py
│   │
│   └── integration/              # Slow integration tests
│       ├── config/
│       │   └── test_config_workflow.py
│       ├── nix/
│       │   └── test_nix_operations.py
│       └── vm/
│           └── test_vm_operations.py
│
├── tests/                        # NixOS VM tests (isolated VMs)
│   └── nixos/
│       └── cli/                  # CLI command tests in VM
│           ├── help/
│           │   └── test-help-output.nix
│           ├── config/
│           │   ├── test-config-operations.nix
│           │   └── test-config-priority.nix
│           └── themes/
│               └── test-theme-commands.nix
│
├── pkgs/testing/                 # Test infrastructure
│   ├── helpers/
│   │   ├── pytest_helpers.py
│   │   └── __init__.py
│   ├── run-tests.nix
│   └── verify-overlay.sh         # Executable verification script
│
├── checks/                       # Flake check orchestration
│   └── flake-module.nix
│
├── pytest.ini                   # Pytest configuration
├── justfile                      # Test execution shortcuts
├── flake.nix                     # Nix flake configuration
└── .github/
    ├── workflows/
    │   └── test.yml              # CI/CD pipeline
    └── CI.md                     # CI/CD documentation
```

### Directory Responsibilities

| Directory | Purpose | Test Type | Execution |
|-----------|---------|-----------|-----------|
| `pkgs/arda-cli/arda_cli/tests/unit/` | Fast unit tests | pytest | Build, pre-commit, CI |
| `pkgs/arda-cli/arda_cli/tests/integration/` | Slow integration tests | pytest | CI only |
| `tests/nixos/cli/*/` | VM tests | NixOS VM | CI, manual |
| `pkgs/testing/` | Test utilities | N/A | Shared by all tests |
| `checks/` | VM test orchestration | Nix flake | CI |

---

## Test Types

The framework uses multiple test types for different purposes:

### 1. Fast Unit Tests

**Location**: `pkgs/arda-cli/arda_cli/tests/unit/`

**Purpose**: Test individual functions and classes in isolation

**Characteristics**:

- Execution time: < 10ms per test
- No file I/O (or minimal/mock file I/O)
- No network calls
- No external dependencies
- Can run during build

**Markers**: `@pytest.mark.fast`, `@pytest.mark.unit`

**Example**:

```python
@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_parse_bool_converts_various_formats():
    """Test that parse_bool handles different boolean representations."""
    from arda_cli.lib.config import parse_bool

    assert parse_bool("true") is True
    assert parse_bool("false") is False
```

**When to Write**:

- Testing pure functions
- Testing configuration parsing
- Testing utility functions
- Testing error handling logic

---

### 2. Integration Tests

**Location**: `pkgs/arda-cli/arda_cli/tests/integration/`

**Purpose**: Test component interaction and workflows

**Characteristics**:

- Execution time: 10-100ms per test
- May use file I/O
- May test CLI commands via CliRunner
- Tests real-world scenarios
- NOT run during build (marked slow)

**Markers**: `@pytest.mark.slow`, `@pytest.mark.integration`

**Example**:

```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
def test_config_set_cli_command():
    """Test 'arda config set theme.name dracula' via CLI."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(main, ['config', 'set', 'theme.name', 'dracula'])

        assert result.exit_code == 0
        assert Path('arda.toml').exists()
```

**When to Write**:

- Testing CLI command workflows
- Testing file operations
- Testing component integration
- Testing real-world user scenarios

---

### 3. VM Tests

**Location**: `tests/nixos/cli/*/`

**Purpose**: Test CLI in isolated virtual machines

**Characteristics**:

- Execution time: 2-5 minutes per test
- Tests real binary execution
- Complete system isolation
- Tests actual user experience
- Only run in CI or manually

**Framework**: NixOS `runNixOSTest` (native NixOS testing)

**Example**:

```nix
testScript = ''
  machine.start()
  machine.wait_for_unit("default.target")

  # Test arda --help
  result = machine.succeed("/tmp/arda-test/arda --help")
  assert "Arda" in result
  assert "config" in result
  print("✅ arda --help works correctly")
'';
```

**When to Write**:

- Testing actual CLI commands
- Testing config file creation
- Testing theme application
- Testing user workflows end-to-end
- Testing behavior in clean environment

---

### 4. System Tests

**Location**: Varies (marked with `@pytest.mark.system`)

**Purpose**: Tests requiring special infrastructure

**Characteristics**:

- Require external services
- Require special hardware
- Require setup/teardown
- Excluded from regular test runs

**Markers**: `@pytest.mark.system`

**When to Write**:

- Tests needing libvirt
- Tests needing real VMs
- Tests needing network services
- Long-running benchmarks

---

### 5. Overlay Regression Tests

**Location**: `pkgs/arda-cli/arda_cli/tests/unit/overlay/`

**Purpose**: Prevent regression of critical system configurations

**Current Focus**: Rich-click overlay version management

**Example**:

```python
@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.overlay
def test_rich_click_version_is_overlaid():
    """Verify rich-click is the overlaid version (1.9.4), not nixpkgs (1.8.9)."""
    import rich_click

    # The overlay upgrades from nixpkgs 1.8.9 to 1.9.4
    assert rich_click.__version__ == "1.9.4", \
        f"Expected rich-click 1.9.4, got {rich_click.__version__}"
```

**When to Write**:

- Critical system configurations
- Package version dependencies
- Overlay configurations
- Build-time dependencies

---

## Test Markers

Pytest markers categorize tests for selective execution:

```ini
# pytest.ini
markers = [
    "fast: Unit tests that run quickly (< 10ms)",
    "slow: Tests that take longer (> 100ms)",
    "unit: Unit tests for isolated functions/classes",
    "integration: Integration tests for component interaction",
    "cli: CLI command tests",
    "theme: Theme system tests",
    "config: Configuration system tests",
    "nix: Nix integration tests",
    "vm: Tests requiring virtual machine",
    "system: System tests needing infrastructure",
    "e2e: End-to-end workflow tests",
    "overlay: Overlay regression tests"
]
```

### Marker Usage Guide

| Marker | Purpose | Run In | Example |
|--------|---------|--------|---------|
| `fast` | Quick tests | Build, CI, pre-commit | Unit tests, validation |
| `slow` | Long tests | CI only | Integration tests |
| `unit` | Isolated tests | Build, CI | Function testing |
| `integration` | Component tests | CI | Workflow testing |
| `config` | Config tests | All levels | Configuration logic |
| `theme` | Theme tests | All levels | Theme system |
| `cli` | CLI tests | All levels | Command execution |
| `vm` | VM tests | Manual, CI | End-to-end testing |
| `system` | Infrastructure tests | Manual | Tests needing setup |
| `overlay` | Regression tests | Build, CI | Critical configurations |

### Running Tests by Marker

```bash
# Fast tests only
pytest -m "fast"

# Config tests only
pytest -m "config"

# Fast AND unit tests
pytest -m "fast and unit"

# Config OR theme tests
pytest -m "config or theme"

# Everything except slow tests
pytest -m "not slow"

# Everything except system tests
pytest -m "not system"
```

---

## Test Execution

There are multiple ways to run tests depending on your needs:

### Method 1: Justfile (Recommended)

The justfile provides convenient shortcuts for common test operations:

```bash
# Quick validation - runs in < 30 seconds
just test-fast

# All unit tests (50 tests) - runs in 2-3 minutes
just test-all

# Integration tests only
just test-integration

# All CLI VM tests - runs in 5-10 minutes
just test-vm-cli

# Specific VM test
just test-vm-cli-help
just test-vm-cli-config-operations
just test-vm-cli-config-priority
just test-vm-cli-theme-commands

# Component-specific tests
just test-config        # All config tests
just test-themes        # All theme tests
just test-cli          # All CLI tests
just test-nix          # All Nix tests

# Overlay verification
just verify-overlay

# Clear VM test cache for fresh builds
just clear-vm-test-cache
```

**Benefits**:

- No need to remember nix commands
- Consistent interface
- Organizes tests logically
- Documented in `justfile` itself

---

### Method 2: Direct Pytest

Run pytest directly for maximum control:

```bash
# Run all tests
pytest -v

# Run specific test file
pytest pkgs/arda-cli/arda_cli/tests/unit/config/test_parses_valid_toml.py -v

# Run with coverage
pytest --cov=pkgs/arda-cli/arda_cli --cov-report=html

# Run in parallel
pytest -n auto

# Run with specific markers
pytest -m "fast" -v
pytest -m "config and not slow" -v

# Run only failing tests
pytest --lf  # Last failed
pytest --ff  # Failed first

# Drop into debugger on failure
pytest --pdb

# Verbose output with short traceback
pytest -v --tb=short
```

**Best For**:

- Debugging specific tests
- Custom test selection
- Development and iteration
- Maximum control

---

### Method 3: Nix Commands

Run tests through the Nix build system:

```bash
# Build arda-cli (runs tests during build)
nix build .#arda-cli

# Run specific VM test
nix build .#checks.x86_64-linux.arda-cli-vm-help

# Run all VM tests
nix build .#checks.x86_64-linux.arda-cli-vm-config-operations
nix build .#checks.x86_64-linux.arda-cli-vm-config-priority
nix build .#checks.x86_64-linux.arda-cli-vm-theme-commands

# Run flake check (includes VM tests)
nix flake check

# Run without cache for debugging
nix build .#checks.x86_64-linux.arda-cli-vm-help --no-out-link

# Run with verbose output
nix build .#arda-cli --verbose 2>&1 | tee /tmp/build.log
```

**Best For**:

- Build-time testing
- CI/CD validation
- Testing in clean environment
- Flake integration

---

### Method 4: CI/CD (Automated)

Tests run automatically in GitHub Actions:

**Workflow**: `.github/workflows/test.yml`

**Jobs**:

1. **validate** (1-2 min)
   - `nix flake check`
   - pre-commit validation
   - Fast feedback

2. **test-fast** (2-3 min)
   - Build package
   - Run fast tests
   - Generate coverage

3. **test-all** (3-5 min)
   - All unit tests
   - All integration tests

4. **test-vm** (5-10 min)
   - All VM tests
   - Scheduled nightly
   - Manual dispatch

5. **build-docs** (2-3 min)
   - Build CLI binary
   - Archive artifacts

6. **summary** (< 1 min)
   - Aggregate results

**Triggers**:

- Push to `master`, `main`, `testing`
- Pull requests
- Manual dispatch (VM tests)
- Nightly schedule (VM tests)

---

### Test Execution Quick Reference

| Scenario | Command | Time |
|----------|---------|------|
| Pre-commit check | `just test-fast` | < 30s |
| Full validation | `just test-all` | 2-3 min |
| Component testing | `just test-config` | 30-60s |
| VM testing | `just test-vm-cli` | 5-10 min |
| Debug build | `nix build .#arda-cli` | 2-5 min |
| Fresh VM test | `just clear-vm-test-cache && nix build .#checks.x86_64-linux.arda-cli-vm-help` | 5-15 min |
| CI simulation | `nix flake check` | 3-5 min |

---

## Writing Tests

This section guides you through writing tests for the framework.

### Writing Fast Unit Tests

**Location**: `pkgs/arda-cli/arda_cli/tests/unit/<component>/`

**Template**:

```python
"""Description of what these tests verify."""
import pytest
from unittest.mock import patch

from arda_cli.lib.config import load_config


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_function_name():
    """Test description: what is being tested and expected."""
    # Arrange
    # Set up test data, mocks, etc.

    # Act
    # Call the function being tested

    # Assert
    # Verify the results
    assert expected_result == actual_result


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_edge_case_handling():
    """Test edge cases and error conditions."""
    # Test that function handles edge cases correctly
    pass
```

**Guidelines**:

1. **One test per behavior**: Each test should verify one specific behavior
2. **Clear test names**: `test_should_do_something_when_condition`
3. **AAA pattern**: Arrange, Act, Assert
4. **Use appropriate markers**: Always include `fast` and `unit`
5. **Add component marker**: Include `config`, `theme`, `cli`, etc.
6. **Avoid external dependencies**: Mock external calls
7. **Keep tests isolated**: Tests should not depend on each other

**Example**:

```python
@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_parse_bool_converts_various_formats():
    """Test that parse_bool handles different boolean representations."""
    from arda_cli.lib.config import parse_bool

    # Test true values
    assert parse_bool(True) is True
    assert parse_bool("true") is True
    assert parse_bool("True") is True
    assert parse_bool("yes") is True
    assert parse_bool("1") is True

    # Test false values
    assert parse_bool(False) is False
    assert parse_bool("false") is False
    assert parse_bool("False") is False
    assert parse_bool("no") is False
    assert parse_bool("0") is False
```

---

### Writing Integration Tests

**Location**: `pkgs/arda-cli/arda_cli/tests/integration/<component>/`

**Template**:

```python
"""Description of integration tests."""
import tempfile
from pathlib import Path
from click.testing import CliRunner

from arda_cli.main import main


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
def test_workflow_description():
    """Test complete workflow with real components."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Test using real file system
        result = runner.invoke(main, ['command', 'arg'])

        # Verify command succeeded
        assert result.exit_code == 0, f"Command failed: {result.output}"

        # Verify file was created
        assert Path('file.toml').exists()

        # Verify content
        content = Path('file.toml').read_text()
        assert "expected" in content
```

**Guidelines**:

1. **Mark as slow**: Integration tests are slow and should be marked accordingly
2. **Use CliRunner**: For testing CLI commands
3. **Isolated filesystem**: Use `runner.isolated_filesystem()` for tests that create files
4. **Real I/O**: Integration tests can use real file operations
5. **Component marker**: Include component-specific marker
6. **Clear assertions**: Verify outcomes clearly

**Example**:

```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
def test_config_set_cli_command():
    """Test 'arda config set theme.name dracula' via CLI."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # Run config set command
        result = runner.invoke(main, ['config', 'set', 'theme.name', 'dracula'])

        # Verify it succeeded
        assert result.exit_code == 0, f"Config set failed: {result.output}"

        # Verify config file was created
        config_file = Path('arda.toml')
        assert config_file.exists(), "Config file should be created"

        # Verify content
        content = config_file.read_text()
        assert "dracula" in content, "Config should contain theme setting"
```

---

### Writing VM Tests

**Location**: `tests/nixos/cli/<category>/test-<name>.nix`

**Template**:

```nix
{ config, pkgs, lib, ... }:
{
  name = "arda-cli-vm-<name>";

  nodes.machine =
    { config, pkgs, lib, ... }:
    {
      # VM configuration
      environment.systemPackages = [
        # Add packages needed for tests
      ];
    };

  testScript = ''
    # Start the VM
    machine.start()
    machine.wait_for_unit("default.target")

    # Test 1: Description
    print("=== Testing: description ===")
    result = machine.succeed("/tmp/arda-test/arda command")
    assert "expected" in result
    print("✅ Test passed")

    # Test 2: Another test
    print("\n=== Testing: another test ===")
    machine.succeed("/tmp/arda-test/arda another-command")
    print("✅ Test passed")

    # Print success message
    print("\n" + "="*60)
    print("✅ All tests PASSED")
    print("="*60)
  '';

  meta.maintainers = [ "Lord Devi" ];
}
```

**Guidelines**:

1. **Always start VM**: `machine.start()` is mandatory
2. **Wait for startup**: `machine.wait_for_unit("default.target")`
3. **Use machine.succeed/fail**:
   - `machine.succeed()` - Command should succeed
   - `machine.fail()` - Command should fail
   - `machine.succeed()` returns output
4. **Print progress**: Use `print()` to show test progress
5. **Assert outcomes**: Use `assert` to verify results
6. **Test isolation**: Each test is independent

**Available Machine Methods**:

- `machine.start()` - Start the VM
- `machine.wait_for_unit("default.target")` - Wait for systemd
- `machine.succeed("command")` - Execute command, expect success, return output
- `machine.fail("command")` - Execute command, expect failure
- `machine.log("message")` - Log a message
- `machine.wait_for_file("/path")` - Wait for file to exist
- `machine.wait_for_text("text")` - Wait for text to appear

**Example**:

```nix
testScript = ''
  # Start the VM
  machine.start()
  machine.wait_for_unit("default.target")

  # Test 1: arda --help
  print("=== Testing: arda --help ===")
  result = machine.succeed("/tmp/arda-test/arda --help")
  assert "Arda" in result
  assert "config" in result
  print("✅ arda --help works correctly")

  # Test 2: Config operations
  print("\n=== Testing: arda config init ===")
  machine.succeed("/tmp/arda-test/arda config --local init --force")
  machine.succeed("test -f etc/arda.toml")
  print("✅ arda config init creates file")
''

  meta.maintainers = [ "Lord Devi" ];
}
```

---

### Test File Organization

**Unit Tests**:

```
pkgs/arda-cli/arda_cli/tests/unit/
├── cli/
│   └── test_cli_integration.py          # CLI-specific unit tests
├── config/
│   └── test_parses_valid_toml.py        # Config parsing tests
├── overlay/
│   └── test_rich_click_version.py       # Overlay regression tests
└── themes/
    └── test_theme_validation.py         # Theme validation tests
```

**Integration Tests**:

```
pkgs/arda-cli/arda_cli/tests/integration/
├── config/
│   └── test_config_workflow.py          # Config workflow tests
├── nix/
│   └── test_nix_operations.py           # Nix integration tests
└── vm/
    └── test_vm_operations.py            # VM integration tests
```

**VM Tests**:

```
tests/nixos/cli/
├── help/
│   └── test-help-output.nix             # Help command tests
├── config/
│   ├── test-config-operations.nix       # Config operations tests
│   └── test-config-priority.nix         # Config priority tests
└── themes/
    └── test-theme-commands.nix          # Theme command tests
```

### Naming Conventions

**Python Test Files**: `test_<what>.py`

- Lowercase
- Underscores for spaces
- Descriptive of what's being tested

**Python Test Functions**: `test_<behavior>_when_<condition>`

- Lowercase
- Underscores
- Describes expected behavior

**Nix Test Files**: `test-<name>.nix`

- Lowercase
- Hyphens for spaces
- Descriptive

**Nix Test Names**: `"arda-cli-vm-<category>"`

- Lowercase
- Hyphens
- Follows pattern: `component-type-scope`

---

## VM Testing Guide

VM tests run the CLI in isolated virtual machines to verify real-world behavior.

### What is VM Testing?

VM tests use the NixOS testing framework to:

1. Create an isolated virtual machine
2. Install the CLI binary in the VM
3. Run commands and verify behavior
4. Test in a clean, minimal environment

### Benefits

1. **Real Binary**: Tests the actual compiled binary, not mocked functions
2. **Complete Isolation**: No contamination from development environment
3. **Real File System**: Tests actual file I/O operations
4. **User Experience**: Tests how users actually use the CLI
5. **Clean Environment**: Tests with minimal dependencies

### How It Works

1. **NixOS VM Framework**: Uses `runNixOSTest` from `pkgs/testers`
2. **Test Script**: Python code that controls the VM
3. **Commands**: Executes real CLI commands
4. **Assertions**: Verifies expected outcomes

### VM Test Structure

```nix
{ config, pkgs, lib, ... }:
{
  name = "arda-cli-vm-<category>";

  # VM definition
  nodes.machine =
    { config, pkgs, lib, ... }:
    {
      # VM configuration
      environment.systemPackages = [
        # Packages available in VM
      ];
    };

  # Test script
  testScript = ''
    # Boot VM
    machine.start()
    machine.wait_for_unit("default.target")

    # Run tests
    result = machine.succeed("/tmp/arda-test/arda command")
    assert "expected" in result

    print("✅ Test passed")
  '';

  meta.maintainers = [ "Lord Devi" ];
}
```

### VM Test Execution Flow

1. **Nix builds test**: Creates VM test derivation
2. **Test driver starts**: Python test driver boots VM
3. **VM boots**: VM starts with minimal NixOS
4. **Binary available**: CLI binary copied to `/tmp/arda-test/`
5. **Tests run**: Test script executes commands
6. **Assertions check**: Verifies expected behavior
7. **VM destroyed**: Cleanup after tests complete

### Writing Effective VM Tests

**DO**:

- ✅ Use `machine.start()` to boot VM
- ✅ Use `machine.succeed()` for commands that should work
- ✅ Use `machine.fail()` for commands that should fail
- ✅ Print progress with `print()`
- ✅ Test actual user workflows
- ✅ Verify file creation and content
- ✅ Test error handling

**DON'T**:

- ❌ Forget `machine.start()`
- ❌ Test implementation details
- ❌ Use mocks (VM tests are for real testing)
- ❌ Run too many commands (keep tests focused)
- ❌ Leave VM running after test

### Common VM Test Patterns

**Testing Help Output**:

```nix
result = machine.succeed("/tmp/arda-test/arda --help")
assert "Arda" in result
assert "config" in result
print("✅ Help output is correct")
```

**Testing Config File Creation**:

```nix
machine.succeed("/tmp/arda-test/arda config --local init --force")
machine.succeed("test -f etc/arda.toml")
result = machine.succeed("cat etc/arda.toml")
assert "theme" in result
print("✅ Config file created")
```

**Testing Config Set Operations**:

```nix
machine.succeed("/tmp/arda-test/arda config --local set theme nord")
result = machine.succeed("cat etc/arda.toml")
assert "nord" in result
print("✅ Config set works")
```

**Testing Theme Application**:

```nix
result = machine.succeed("/tmp/arda-test/arda theme list")
assert "dracula" in result
assert "nord" in result
print("✅ Theme list works")
```

**Testing Error Handling**:

```nix
machine.fail("/tmp/arda-test/arda --theme invalid-theme --help")
print("✅ Invalid theme rejected")
```

### Running VM Tests

```bash
# Run all VM tests
just test-vm-cli

# Run specific VM test
just test-vm-cli-help
just test-vm-cli-config-operations
just test-vm-cli-config-priority
just test-vm-cli-theme-commands

# Run via Nix
nix build .#checks.x86_64-linux.arda-cli-vm-help

# Run without cache (for debugging)
just clear-vm-test-cache
nix build .#checks.x86_64-linux.arda-cli-vm-help --no-out-link

# Run with verbose output
nix build .#checks.x86_64-linux.arda-cli-vm-help --verbose
```

### VM Test Debugging

**Problem**: Tests are cached and run too fast

```bash
# Solution: Clear cache for fresh build
just clear-vm-test-cache
nix build .#checks.x86_64-linux.arda-cli-vm-help
```

**Problem**: VM hangs during boot

```bash
# Solution: Clear cache and rebuild
just clear-vm-test-cache
nix build .#checks.x86_64-linux.arda-cli-vm-help --no-out-link 2>&1 | tee /tmp/vm-debug.log
```

**Problem**: Test fails intermittently

```bash
# Solution: Run multiple times
for i in {1..5}; do
    echo "Run $i:"
    nix build .#checks.x86_64-linux.arda-cli-vm-help
done
```

**Problem**: Need to see VM output

```bash
# Solution: Build without cache
just clear-vm-test-cache
nix build .#checks.x86_64-linux.arda-cli-vm-help --no-out-link
# Check result/ directory for test logs
```

---

## CI/CD Integration

Tests run automatically in GitHub Actions for every push and pull request.

### Workflow Overview

**File**: `.github/workflows/test.yml`

**Jobs**:

1. **validate** - Fast validation (flake check, pre-commit)
2. **test-fast** - Build package + run fast tests
3. **test-all** - Complete test suite (all pytest tests)
4. **test-vm** - VM tests (scheduled/manual only)
5. **build-docs** - Build CLI binary
6. **summary** - Aggregate results

### Job Details

#### validate Job (1-2 minutes)

**Purpose**: Fast feedback on code quality

**Steps**:

1. Check out code
2. Setup Nix
3. Run `nix flake check`
4. Run pre-commit hooks

**When**: Every push/PR

#### test-fast Job (2-3 minutes)

**Purpose**: Build package and run fast tests

**Steps**:

1. Check out code
2. Setup Nix
3. Build `arda-cli` package
4. Tests run in build (fast unit tests)
5. Upload coverage report

**When**: Every push/PR

#### test-all Job (3-5 minutes)

**Purpose**: Run complete test suite

**Steps**:

1. Check out code
2. Setup Nix
3. Run `just test-all`
4. Upload test report

**When**: Every push/PR
**Excludes**: VM tests (too slow)

#### test-vm Job (5-10 minutes)

**Purpose**: Run VM tests

**Steps**:

1. Check out code
2. Setup Nix
3. Run VM tests
4. Upload test logs

**When**:

- Manual dispatch
- Nightly schedule (00:00 UTC)
- Push to `testing` branch

**Why separate**: VM tests are slow and resource-intensive

#### build-docs Job (2-3 minutes)

**Purpose**: Build and archive CLI binary

**Steps**:

1. Check out code
2. Setup Nix
3. Build `arda-cli`
4. Archive binary

**When**: Every push/PR
**Artifact**: CLI binary available for download

#### summary Job (< 1 minute)

**Purpose**: Aggregate test results

**Steps**:

1. Collect results from all jobs
2. Post comment on PR
3. Update check status

**When**: After all test jobs complete

### CI Triggers

**Automatic Triggers**:

- Push to `master`, `main`, `testing` branches
- Pull requests to `master`, `main`, `testing` branches

**Manual Triggers**:

- `workflow_dispatch` - Run workflow manually
- VM tests can be dispatched manually

**Scheduled Triggers**:

- Nightly at 00:00 UTC - Run VM tests

### CI Artifacts

**Available for Download**:

1. **Coverage Reports** (HTML, XML)
2. **Test Reports** (JUnit XML)
3. **CLI Binary**
4. **VM Test Logs**

**Access**: Go to Actions tab → Select workflow run → Scroll to Artifacts

### Local CI Simulation

**Install act** (for local CI testing):

```bash
curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

**Run workflow locally**:

```bash
# Run specific job
act -j validate

# Run all jobs
act

# Run with input
act -j test-vm --input vm_test=true
```

### Branch Protection

**Recommended Settings**:

- Require status checks to pass
- Require `validate`, `test-fast`, `test-all` to pass
- VM tests optional (can be required for release)
- Require branches to be up to date

### CI Best Practices

1. **Fast Feedback**: validate job runs in ~2 minutes
2. **Cache Management**: Nix caching enabled
3. **Concurrency**: Cancel in-progress runs on new push
4. **Artifacts**: Save logs and reports
5. **Documentation**: See `.github/CI.md` for details

---

## Best Practices

This section covers best practices for writing and maintaining tests.

### Test Organization

1. **One Behavior Per Test**

   ```python
   # Good
   def test_parse_bool_true_values():
       assert parse_bool("true") is True
       assert parse_bool("yes") is True

   # Bad - testing multiple behaviors
   def test_parse_bool():
       # Too many assertions, multiple behaviors
   ```

2. **Clear Test Names**

   ```python
   # Good
   def test_load_config_returns_empty_dict_when_no_file():
       pass

   # Bad
   def test_config():
       pass
   ```

3. **Proper Markers**

   ```python
   # Good
   @pytest.mark.fast
   @pytest.mark.unit
   @pytest.mark.config
   def test_something():
       pass

   # Bad - missing markers
   def test_something():
       pass
   ```

### Test Isolation

1. **No Test Dependencies**

   ```python
   # Good - each test is independent
   def test_first():
       # Test A

   def test_second():
       # Test B, doesn't depend on test_first
   ```

2. **Mock External Dependencies**

   ```python
   # Good
   @pytest.mark.fast
   def test_config_parsing():
       with patch('arda_cli.lib.config.get_config_path') as mock:
           mock.return_value = None
           config = load_config()
   ```

3. **Isolated Filesystem**

   ```python
   # Good - for integration tests
   def test_file_creation():
       runner = CliRunner()
       with runner.isolated_filesystem():
           # Tests run in temporary directory
           pass
   ```

### Performance

1. **Mark Slow Tests**

   ```python
   # Good
   @pytest.mark.slow
   @pytest.mark.integration
   def test_full_workflow():
       # Slow test marked appropriately
   ```

2. **Keep Fast Tests Fast**

   ```python
   # Good - no network calls, minimal I/O
   @pytest.mark.fast
   def test_parse_bool():
       assert parse_bool("true") is True
   ```

3. **Parallel Execution**

   ```bash
   # Run tests in parallel
   pytest -n auto
   ```

### Coverage

1. **Focus on Critical Paths**
   - Configuration parsing
   - Error handling
   - CLI commands

2. **Don't Chase 100%**
   - 15% minimum for unit tests
   - 30% minimum for integration tests
   - Quality over quantity

3. **Test Edge Cases**

   ```python
   # Test normal case
   def test_normal_case():
       assert function("valid") == expected

   # Test edge cases
   def test_edge_cases():
       assert function("") == default
       assert function(None) == default
   ```

### VM Tests

1. **Test User Workflows**

   ```nix
   # Good - test what user actually does
   machine.succeed("/tmp/arda-test/arda config init")
   machine.succeed("/tmp/arda-test/arda config set theme dracula")
   ```

2. **Boot VM First**

   ```nix
   # Always start with this
   machine.start()
   machine.wait_for_unit("default.target")
   ```

3. **Verify File Creation**

   ```nix
   # Verify files are created
   machine.succeed("test -f etc/arda.toml")

   # Verify file content
   result = machine.succeed("cat etc/arda.toml")
   assert "dracula" in result
   ```

### CI/CD

1. **Keep validate Job Fast**
   - Use for flake check and pre-commit
   - Should complete in < 2 minutes

2. **Separate Slow Tests**
   - VM tests run on schedule
   - Not on every PR

3. **Cache Dependencies**
   - Nix caching enabled
   - Speeds up builds

### Debugging

1. **Use --tb=short for Clear Errors**

   ```bash
   pytest --tb=short
   ```

2. **Drop into Debugger on Failure**

   ```bash
   pytest --pdb
   ```

3. **Run Last Failed**

   ```bash
   pytest --lf
   ```

4. **Clear VM Test Cache When Debugging**

   ```bash
   just clear-vm-test-cache
   ```

### Maintenance

1. **Keep Tests Updated**
   - Update tests when code changes
   - Remove obsolete tests

2. **Regular Test Runs**
   - Run `just test-fast` before commits
   - Run full suite before releases

3. **Document Test Purpose**

   ```python
   """Test that valid TOML configuration files are parsed correctly."""
   # Explain what these tests verify
   ```

4. **Review Test Coverage**

   ```bash
   pytest --cov=pkgs/arda-cli/arda_cli --cov-report=term-missing
   ```

---

## Troubleshooting

Common issues and solutions:

### Tests Are Too Slow

**Problem**: Tests take too long to run

**Solution**:

1. Mark integration tests as slow

   ```python
   @pytest.mark.slow
   @pytest.mark.integration
   def test_slow_workflow():
       pass
   ```

2. Run only fast tests for development

   ```bash
   just test-fast
   ```

### VM Tests Hanging

**Problem**: VM tests hang at boot

**Solution**:

1. Clear VM test cache

   ```bash
   just clear-vm-test-cache
   ```

2. Rebuild test

   ```bash
   nix build .#checks.x86_64-linux.arda-cli-vm-help --no-out-link
   ```

3. Check for `machine.start()` in test

   ```nix
   testScript = ''
     machine.start()  # This is required!
     machine.wait_for_unit("default.target")
   ```

### Interactive Prompt Hang

**Problem**: Test hangs waiting for input

**Solution**: Use `--force` flag

```nix
machine.succeed("/tmp/arda-test/arda config --local init --force")
# The --force flag prevents interactive prompts
```

### Tests Pass Locally But Fail in CI

**Possible Causes**:

1. Environment differences
2. Missing dependencies
3. Timing issues
4. File system differences

**Solutions**:

1. Check CI logs
2. Ensure all dependencies are declared
3. Use `runner.isolated_filesystem()` for file tests
4. Check for race conditions

### Coverage Too Low

**Problem**: Coverage below threshold (15% unit, 30% integration)

**Solutions**:

1. Add more unit tests

   ```bash
   # Check what's not covered
   pytest --cov=pkgs/arda-cli/arda_cli --cov-report=term-missing
   ```

2. Increase thresholds gradually
   - Update `pkgs/arda-cli/default.nix`
   - Raise from 15% to 20% to 30%, etc.

### Import Errors

**Problem**: `ModuleNotFoundError` when running tests

**Solution**:

1. Run from project root

   ```bash
   cd /home/ld/src/arda-core
   pytest
   ```

2. Check PYTHONPATH

   ```bash
   export PYTHONPATH="$PYTHONPATH:/home/ld/src/arda-core"
   ```

### Nix Build Failures

**Problem**: `nix build` fails with errors

**Solutions**:

1. Check flake is locked

   ```bash
   nix flake check
   ```

2. Update flake

   ```bash
   nix flake update
   nix build .#arda-cli
   ```

### Test Discovery Issues

**Problem**: Tests not being discovered

**Solution**:

1. Check pytest configuration

   ```bash
   cat pytest.ini
   ```

2. Run with verbose output

   ```bash
   pytest --collect-only -v
   ```

3. Check file naming
   - Test files: `test_*.py`
   - Test functions: `test_*()`

---

## Quick Reference

### Command Cheat Sheet

| Task | Command |
|------|---------|
| Run fast tests | `just test-fast` |
| Run all tests | `just test-all` |
| Run integration tests | `just test-integration` |
| Run VM tests | `just test-vm-cli` |
| Run specific VM test | `just test-vm-cli-help` |
| Build with tests | `nix build .#arda-cli` |
| Run flake check | `nix flake check` |
| Clear VM cache | `just clear-vm-test-cache` |
| Verify overlay | `just verify-overlay` |
| Generate coverage | `pytest --cov=pkgs/arda-cli/arda_cli --cov-report=html` |

### Directory Quick Reference

| Directory | Purpose |
|-----------|---------|
| `pkgs/arda-cli/arda_cli/tests/unit/` | Fast unit tests |
| `pkgs/arda-cli/arda_cli/tests/integration/` | Integration tests |
| `tests/nixos/cli/*/` | VM tests |
| `pkgs/testing/` | Test utilities |
| `checks/` | Flake checks |
| `pytest.ini` | Pytest configuration |
| `justfile` | Test shortcuts |

### Marker Quick Reference

| Marker | Run In |
|--------|--------|
| `fast` | Build, CI, pre-commit |
| `slow` | CI only |
| `unit` | All levels |
| `integration` | CI |
| `vm` | Manual, CI |
| `system` | Never (requires special setup) |

### Test File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Unit test file | `test_*.py` | `test_config_parsing.py` |
| Unit test function | `test_*()` | `test_loads_valid_toml()` |
| VM test file | `test-*.nix` | `test-help-output.nix` |
| VM test name | `"arda-cli-vm-*"` | `"arda-cli-vm-help"` |

### Common Assertions

**Unit Tests**:

```python
assert result == expected
assert value is True
assert value is False
assert "text" in result
assert len(items) == 5
```

**VM Tests**:

```nix
assert "expected" in result
machine.succeed("test -f /path/file")
machine.succeed("test -d /path/dir")
machine.fail("invalid-command")
```

### Useful Pytest Flags

| Flag | Purpose |
|------|---------|
| `-v` | Verbose output |
| `-s` | Show print statements |
| `--tb=short` | Short traceback |
| `--pdb` | Drop into debugger on failure |
| `--lf` | Run last failed tests |
| `--ff` | Run failed tests first |
| `-n auto` | Run in parallel |
| `--cov` | Generate coverage |

### Useful Nix Commands

| Command | Purpose |
|---------|---------|
| `nix build .#arda-cli` | Build package with tests |
| `nix flake check` | Run all flake checks |
| `nix build .#checks.x86_64-linux.arda-cli-vm-help` | Run specific VM test |
| `nix build --no-out-link` | Build without creating symlink |
| `nix build --verbose` | Verbose output |
| `nix flake update` | Update flake inputs |
| `nix-store --delete /path` | Delete from Nix store |

### Getting Help

1. **Justfile**: `just help` - Lists all test commands
2. **pytest**: `pytest --help` - Pytest options
3. **CI docs**: `.github/CI.md` - CI/CD documentation
4. **Implementation plan**: `bmad-docs/plan-testing.md` - Full history

---

## Conclusion

The arda-core testing framework provides comprehensive test coverage through multiple layers:

1. **Fast Unit Tests** - Quick validation during development
2. **Integration Tests** - Component interaction testing
3. **VM Tests** - End-to-end testing in isolated VMs
4. **CI/CD Integration** - Automated testing on every push

**Key Principles**:

- Speed for fast tests
- Isolation for all tests
- Comprehensive coverage
- Automated execution
- Excellent developer experience

**Getting Started**:

```bash
# Run fast tests (do this before every commit)
just test-fast

# Run all unit tests
just test-all

# Run VM tests (when needed)
just test-vm-cli
```

**Questions or Issues**:

- See troubleshooting section above
- Check `.github/CI.md` for CI issues
- Review `bmad-docs/plan-testing.md` for historical context

**Contributing**:

- Follow the test organization guidelines
- Write tests for new features
- Update tests when code changes
- Maintain test quality and coverage

---

**Document maintained by**: Development Team
**Last updated**: 2025-11-29
**Next review**: As needed with framework changes
