# Testing Framework Guide

**Version**: 2.0
**Last Updated**: 2025-11-30
**Status**: Active Development

This document serves as a complete reference and guide for the arda-core testing framework. It covers test organization, execution, writing guidelines, and best practices for all contributors.

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Test Types](#test-types)
4. [Two-Phase Testing Pattern](#two-phase-testing-pattern)
5. [Test Execution](#test-execution)
6. [Writing Tests](#writing-tests)
7. [VM Testing Guide](#vm-testing-guide)
8. [CI/CD Integration](#cicd-integration)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)
11. [Quick Reference](#quick-reference)

---

## Overview

The arda-core testing framework is a comprehensive, multi-layered approach following the clan-core pattern:

- **Phase 1 (without-core)**: Fast isolated tests (180 tests)
- **Phase 2 (with-core)**: Comprehensive integration tests (45 tests)
- **VM Tests**: End-to-end testing in isolated virtual machines (4 test suites)
- **CI/CD Integration**: Automated testing on every push/PR

### Testing Philosophy

1. **Speed**: Fast tests run on every build and commit
2. **Isolation**: Tests don't interfere with each other
3. **Two-Phase Pattern**: Separate fast isolated tests from comprehensive integration tests
4. **Coverage**: Multiple test types for comprehensive coverage
5. **Automation**: Tests run automatically in CI/CD
6. **Developer Experience**: Easy to run, write, and debug

### Current Test Statistics

**Total Tests**: 225 tests

**Phase 1 (without-core)**: 180 tests

- Unit tests for isolated functions/classes
- Config parsing and validation
- Theme system tests
- CLI integration tests
- Overlay regression tests (rich-click)
- Network utility tests (port management, SSH)

**Phase 2 (with-core)**: 45 tests

- CLI workflow tests
- Config file workflow tests
- Nix operations tests
- VM integration tests

**VM Tests**: 4 test suites

- Help output tests (10 tests)
- Config operations tests (8 tests)
- Config priority tests (8 tests)
- Theme command tests (9 tests)

---

## Directory Structure

The testing framework is distributed across multiple directories:

```
/home/ld/src/arda-core/
├── docs/                          # Current documentation (tracked by git)
│   └── TEST-FRAMEWORK.md         # This document
│
├── bmad-docs/                     # Development docs (not tracked)
│   ├── plan-testing.md           # Implementation plan & deviations
│   ├── phase-a-b-complete.md     # Phase A & B completion report
│   └── binary-fix-report.md      # Binary runtime issue resolution
│
├── pkgs/arda-cli/arda_cli/tests/  # Main pytest test suite
│   ├── conftest.py               # Pytest fixtures (14 fixtures)
│   ├── unit/                     # Fast unit tests
│   │   ├── cli/
│   │   │   └── test_cli_integration.py
│   │   ├── config/
│   │   │   └── test_parses_valid_toml.py
│   │   ├── lib/
│   │   │   ├── test_config.py       # Config library tests
│   │   │   ├── test_output.py       # Output library tests
│   │   │   └── test_theme.py        # Theme library tests
│   │   ├── overlay/
│   │   │   └── test_rich_click_version.py  # Overlay regression tests
│   │   └── themes/
│   │       └── test_theme_validation.py
│   │
│   └── integration/              # Slow integration tests
│       ├── cli/
│       │   └── test_main_cli.py     # CLI workflow tests
│       ├── config/
│       │   └── test_config_workflow.py  # Config workflow tests
│       ├── network/
│       │   └── test_network_utils.py    # Port/SSH utilities
│       ├── nix/
│       │   └── test_nix_operations.py   # Nix integration tests
│       └── vm/
│           └── test_vm_operations.py    # VM integration tests
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
│   ├── fixtures_arda.py          # Two-phase testing fixtures
│   ├── helpers/
│   │   ├── pytest_helpers.py    # Test helper utilities
│   │   └── __init__.py
│   ├── nix_isolation.nix         # Nix store isolation utilities
│   ├── nixos_test_lib/           # Python NixOS test library
│   ├── run-tests.nix             # Test runner
│   ├── run-vm-tests.nix          # VM test runner with caching
│   └── vm-prebuild.nix           # VM pre-building infrastructure
│
├── checks/                       # Flake check orchestration
│   └── flake-module.nix
│
├── pytest.ini                   # Pytest configuration
├── justfile                      # Test execution shortcuts
├── flake.nix                     # Nix flake configuration
└── .github/
    ├── workflows/
    │   └── test.yml              # CI/CD pipeline (6 jobs)
    └── CI.md                     # CI/CD documentation
```

### Directory Responsibilities

| Directory | Purpose | Test Type | Execution |
|-----------|---------|-----------|-----------|
| `pkgs/arda-cli/arda_cli/tests/unit/` | Fast unit tests (Phase 1) | pytest | Build, pre-commit, CI |
| `pkgs/arda-cli/arda_cli/tests/integration/` | Integration tests (Phase 2) | pytest | CI |
| `tests/nixos/cli/*/` | VM tests (isolated VMs) | NixOS VM | CI, manual |
| `pkgs/testing/` | Test utilities & fixtures | N/A | Shared by all tests |
| `checks/` | VM test orchestration | Nix flake | CI |

---

## Test Types

The framework uses multiple test types organized into two phases:

### Phase 1: Without-Core Tests (Fast, Isolated)

**Location**: `pkgs/arda-cli/arda_cli/tests/unit/`

**Purpose**: Test individual functions and classes in isolation

**Characteristics**:

- Execution time: < 10ms per test
- No external dependencies on arda-core
- No file I/O (or minimal/mock file I/O)
- No network calls
- Can run during build
- **180 tests total**

**Markers**: `@pytest.mark.fast`, `@pytest.mark.unit`, `@pytest.mark.without_core`

**Categories**:

1. **Unit Tests**: Test isolated functions/classes
   - Config parsing and validation
   - Theme system functions
   - Output formatting
   - CLI option parsing

2. **Overlay Regression Tests**: Prevent critical configuration regressions
   - Rich-click overlay version verification
   - Package dependency validation
   - Build-time configuration checks

3. **Network Utility Tests**: Port management and SSH utilities
   - Port allocation and validation
   - SSH connection management
   - Network connectivity testing

**Example**:

```python
@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.without_core
@pytest.mark.config
def test_parse_bool_converts_various_formats():
    """Test that parse_bool handles different boolean representations."""
    from arda_cli.lib.config import parse_bool

    assert parse_bool("true") is True
    assert parse_bool("false") is False
```

---

### Phase 2: With-Core Tests (Comprehensive)

**Location**: `pkgs/arda-cli/arda_cli/tests/integration/`

**Purpose**: Test component interaction and workflows

**Characteristics**:

- Execution time: 10-100ms per test
- May use file I/O
- May test CLI commands via CliRunner
- Tests real-world scenarios
- Requires arda-core infrastructure
- **45 tests total**

**Markers**: `@pytest.mark.slow`, `@pytest.mark.integration`, `@pytest.mark.with_core`

**Categories**:

1. **CLI Workflow Tests**: End-to-end CLI command testing
   - Command routing and help display
   - Theme application via CLI
   - Config management via CLI
   - Error handling in CLI

2. **Config Workflow Tests**: File-based configuration operations
   - Config file discovery and loading
   - Config writing and persistence
   - XDG compliance
   - Priority order (local vs global)

3. **Nix Integration Tests**: Nix operations
   - Nix build operations
   - Nix eval operations
   - Flake handling

4. **VM Integration Tests**: VM management operations
   - VM lifecycle operations
   - Snapshot management
   - Network configuration

**Example**:

```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.with_core
@pytest.mark.config
def test_config_set_cli_command():
    """Test 'arda config set theme.name dracula' via CLI."""
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(main, ['config', 'set', 'theme.name', 'dracula'])

        assert result.exit_code == 0
        assert Path('arda.toml').exists()
```

---

### VM Tests

**Location**: `tests/nixos/cli/*/`

**Purpose**: Test CLI in isolated virtual machines

**Characteristics**:

- Execution time: 2-5 minutes per test
- Tests real binary execution
- Complete system isolation
- Tests actual user experience
- Only run in CI or manually
- **4 test suites, ~35 tests total**

**Framework**: NixOS `runNixOSTest` (native NixOS testing)

**Test Suites**:

1. **Help Tests** (`help/test-help-output.nix`)
   - arda --help display
   - Subcommand help
   - Theme application in help
   - Verbose mode

2. **Config Operations** (`config/test-config-operations.nix`)
   - Config file creation
   - Config set/get operations
   - Default value handling

3. **Config Priority** (`config/test-config-priority.nix`)
   - Local vs global config priority
   - XDG Base Directory compliance
   - Multiple config file handling

4. **Theme Commands** (`themes/test-theme-commands.nix`)
   - Theme listing
   - Theme switching
   - Theme validation

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

---

## Two-Phase Testing Pattern

The framework follows clan-core's two-phase testing pattern for better isolation and performance:

### Phase 1: Without-Core (Fast, Isolated)

**What**: Tests that don't need arda-core infrastructure
**When**: Every build, commit, and PR
**Marker**: `@pytest.mark.without_core`
**Run**: `just test-without-core` or `pytest -m "without_core"`

**Includes**:

- Unit tests for individual functions
- Overlay regression tests
- Network utility tests
- Pure library tests

**Execution**: ~30 seconds

### Phase 2: With-Core (Comprehensive)

**What**: Tests that need arda-core infrastructure
**When**: Full test runs, CI
**Marker**: `@pytest.mark.with_core`
**Run**: `just test-with-core` or `pytest -m "with_core"`

**Includes**:

- CLI workflow tests
- Config file operations
- Nix integration tests
- VM integration tests

**Execution**: ~1-2 minutes

### Why Two Phases?

1. **Speed**: Developers get fast feedback (Phase 1) before waiting for full suite
2. **Isolation**: Phase 1 tests are truly isolated
3. **CI Efficiency**: Phase 1 can run on every commit, Phase 2 on PRs
4. **Clear Intent**: Markers clearly indicate test requirements
5. **Parallel Execution**: Phases can run in parallel in CI

### Fixtures

**File**: `pkgs/testing/fixtures_arda.py`

Provides fixtures for the two-phase pattern:

- `with_core` - Enable arda-core infrastructure
- `without_core` - Disable arda-core infrastructure
- `create_test_flake` - Create temporary test flake
- `temporary_home` - Isolated home directory

### Usage

```python
# For Phase 1 tests
@pytest.mark.without_core
def test_function():
    # Test without arda-core dependencies
    pass

# For Phase 2 tests
@pytest.mark.with_core
def test_workflow():
    # Test with arda-core infrastructure
    pass
```

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
    "system: System-level tests (real VMs/containers)",
    "service_runner: Tests requiring service runner",
    "impure: Tests requiring network or system state",
    "with_core: Tests requiring arda-core infrastructure",
    "without_core: Tests that run without arda-core (fast, isolated)",
    "network: Network utilities tests (port management, SSH)",
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
| `with_core` | Phase 2 tests | CI | arda-core integration |
| `without_core` | Phase 1 tests | Build, CI | Isolated testing |
| `network` | Network tests | All levels | Port/SSH utilities |

### Running Tests by Marker

```bash
# Fast tests only
pytest -m "fast"

# Phase 1 (without-core) tests
pytest -m "without_core"

# Phase 2 (with-core) tests
pytest -m "with_core"

# All tests except slow
pytest -m "not slow"

# Config tests in Phase 1
pytest -m "config and without_core"

# Network tests
pytest -m "network"

# CLI tests (all phases)
pytest -m "cli"
```

---

## Test Execution

Multiple ways to run tests depending on your needs:

### Method 1: Justfile (Recommended)

The justfile provides convenient shortcuts for common test operations:

```bash
# =================
# Quick Tests
# =================

# Fast unit tests (pre-commit compatible) - ~30 seconds
just test-fast

# Component-specific tests - ~30-60 seconds each
just test-config        # Config tests (unit + integration)
just test-themes        # Theme tests
just test-cli          # CLI tests
just test-nix          # Nix integration tests
just test-network      # Network utility tests

# =================
# Two-Phase Testing
# =================

# Phase 1: Without arda-core (fast, isolated) - ~30 seconds
just test-without-core

# Phase 2: With arda-core (comprehensive) - ~1-2 minutes
just test-with-core

# Both phases sequentially (full test suite) - ~2-3 minutes
just test-two-phase

# =================
# VM Tests
# =================

# All CLI VM tests - ~5-10 minutes
just test-vm-cli

# Specific VM test category - ~2-3 minutes each
just test-vm-cli-help          # Help output tests
just test-vm-cli-config        # Config tests
just test-vm-cli-themes        # Theme tests

# Individual VM tests - ~2-3 minutes each
just test-vm-cli-help-output
just test-vm-cli-config-operations
just test-vm-cli-config-priority
just test-vm-cli-theme-commands

# Clear VM test cache for fresh builds - ~5-15 minutes
just clear-vm-test-cache

# =================
# Coverage Testing
# =================

# Run tests with coverage report (shows missing lines)
just coverage

# Run coverage check (fails if below threshold)
just coverage-check

# Generate HTML coverage report
just coverage-html

# =================
# Build Testing
# =================

# Build arda-cli (runs tests during build) - ~2-5 minutes
just build-arda-cli

# Run arda-cli build-time tests - ~2-5 minutes
just test-arda-cli

# =================
# Utility
# =================

# Run tests in watch mode (requires pytest-watch)
just test-watch
```

**Benefits**:

- No need to remember pytest/nix commands
- Consistent interface
- Organizes tests logically
- Documented in justfile itself

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

# Run Phase 1 (without-core) tests
pytest -m "without_core" -v

# Run Phase 2 (with-core) tests
pytest -m "with_core" -v

# Run network tests only
pytest -m "network" -v

# Run fast tests only
pytest -m "fast" -v

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
# Build arda-cli (runs Phase 1 tests during build)
nix build .#arda-cli

# Run specific VM test
nix build .#checks.x86_64-linux.arda-cli-vm-help

# Run all VM tests
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

**Jobs** (6 total):

1. **validate** (1-2 min)
   - `nix flake check`
   - pre-commit validation
   - Fast feedback

2. **test-fast** (2-3 min)
   - Build package
   - Run fast tests
   - Generate coverage

3. **test-all** (3-5 min)
   - Run `just test-all` (both phases)
   - All unit and integration tests
   - Upload test reports

4. **test-vm** (5-10 min)
   - All VM tests
   - Scheduled nightly
   - Manual dispatch only

5. **build-docs** (2-3 min)
   - Build CLI binary
   - Archive artifacts

6. **summary** (< 1 min)
   - Aggregate results
   - Update check status

**Triggers**:

- Push to `main`, `master`, `testing`
- Pull requests
- Manual dispatch (VM tests)
- Nightly schedule (VM tests)

---

### Test Execution Quick Reference

| Scenario | Command | Time |
|----------|---------|------|
| Pre-commit check | `just test-fast` | < 30s |
| Phase 1 validation | `just test-without-core` | ~30s |
| Full validation | `just test-two-phase` | 2-3 min |
| Component testing | `just test-config` | 30-60s |
| VM testing | `just test-vm-cli` | 5-10 min |
| Debug build | `nix build .#arda-cli` | 2-5 min |
| Fresh VM test | `just clear-vm-test-cache && nix build .#checks.x86_64-linux.arda-cli-vm-help` | 5-15 min |
| CI simulation | `nix flake check` | 3-5 min |

---

## Writing Tests

This section guides you through writing tests for the framework.

### Writing Phase 1 Tests (without-core)

**Location**: `pkgs/arda-cli/arda_cli/tests/unit/<component>/`

**Template**:

```python
"""Description of what these tests verify."""
import pytest
from unittest.mock import patch

from arda_cli.lib.config import load_config


@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.without_core
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
```

**Guidelines**:

1. **Always mark with `@pytest.mark.without_core`** - This is Phase 1!
2. **One test per behavior**: Each test should verify one specific behavior
3. **Clear test names**: `test_should_do_something_when_condition`
4. **AAA pattern**: Arrange, Act, Assert
5. **Use appropriate markers**: Always include `fast`, `unit`, and `without_core`
6. **Add component marker**: Include `config`, `theme`, `cli`, `network`, etc.
7. **Avoid external dependencies**: Mock external calls
8. **Keep tests isolated**: Tests should not depend on each other

---

### Writing Phase 2 Tests (with-core)

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
@pytest.mark.with_core
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

1. **Always mark with `@pytest.mark.with_core`** - This is Phase 2!
2. **Mark as slow**: Integration tests are slow and should be marked accordingly
3. **Use CliRunner**: For testing CLI commands
4. **Isolated filesystem**: Use `runner.isolated_filesystem()` for tests that create files
5. **Real I/O**: Integration tests can use real file operations
6. **Component marker**: Include component-specific marker
7. **Clear assertions**: Verify outcomes clearly

---

### Writing Overlay Regression Tests

**Location**: `pkgs/arda-cli/arda_cli/tests/unit/overlay/`

**Purpose**: Prevent regression of critical system configurations

**Current Focus**: Rich-click overlay version management

**Example**:

```python
@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.without_core
def test_rich_click_version_is_overlaid():
    """Verify rich-click is the overlaid version (1.9.4), not nixpkgs (1.8.9).

    The overlay upgrades from nixpkgs 1.8.9 to 1.9.4 which includes
    theming support required by arda-cli.
    """
    import rich_click

    # The overlay version (1.9.4) vs nixpkgs version (1.8.9)
    expected_version = "1.9.4"
    actual_version = rich_click.__version__

    assert actual_version == expected_version, (
        f"Expected rich-click {expected_version} "
        f"(custom overlay version with theming), "
        f"but got {actual_version} (nixpkgs version without theming support). "
    )
```

**Guidelines**:

1. **Always in Phase 1** - Overlay tests verify arda-cli's build dependencies
2. **No filesystem navigation** - Don't try to navigate to repo root in Nix stores
3. **Runtime verification only** - Check that the overlay actually works
4. **Test in both devShell and Nix builds** - These tests run in both environments

---

### Writing Network Utility Tests

**Location**: `pkgs/arda-cli/arda_cli/tests/integration/network/`

**Purpose**: Test port management and SSH connection utilities

**Example**:

```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.without_core
@pytest.mark.network
def test_find_free_port():
    """Test that find_free_port returns an available port."""
    from arda_cli.testing.network import find_free_port

    port = find_free_port(start=8000, end=9000)

    # Port should be in the specified range
    assert 8000 <= port <= 9000

    # Port should actually be free
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()

    # Should not be able to connect (port is free)
    assert result != 0
```

**Guidelines**:

1. **Mark with `@pytest.mark.network`** - Identifies network utility tests
2. **Mark with `@pytest.mark.without_core`** - These don't need arda-core
3. **Use real network operations** - Network tests use actual sockets/SSH
4. **Clean up resources** - Close sockets, terminate connections

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
    # Start the VM (REQUIRED!)
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

---

### Test File Organization

**Phase 1 Tests (without-core)**:

```
pkgs/arda-cli/arda_cli/tests/unit/
├── cli/
│   └── test_cli_integration.py          # CLI-specific unit tests
├── config/
│   └── test_parses_valid_toml.py        # Config parsing tests
├── lib/
│   ├── test_config.py                   # Config library tests
│   ├── test_output.py                   # Output library tests
│   └── test_theme.py                    # Theme library tests
├── overlay/
│   └── test_rich_click_version.py       # Overlay regression tests
└── themes/
    └── test_theme_validation.py         # Theme validation tests
```

**Phase 2 Tests (with-core)**:

```
pkgs/arda-cli/arda_cli/tests/integration/
├── cli/
│   └── test_main_cli.py                 # CLI workflow tests
├── config/
│   └── test_config_workflow.py          # Config workflow tests
├── network/
│   └── test_network_utils.py            # Port/SSH utility tests
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

### VM Test Structure

```nix
{ config, pkgs, lib, ... }:
{
  name = "arda-cli-vm-help";

  nodes.machine =
    { config, pkgs, lib, ... }:
    {
      environment.systemPackages = [
        pkgs.bash
      ];
    };

  testScript = ''
    # Boot VM
    machine.start()
    machine.wait_for_unit("default.target")

    # Run tests
    result = machine.succeed("/tmp/arda-test/arda --help")
    assert "Arda" in result
    assert "config" in result
    assert "theme" in result

    print("✅ All tests PASSED")
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
- ✅ Use `--force` flag for config init to avoid interactive prompts

**DON'T**:

- ❌ Forget `machine.start()` (causes hang)
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
assert "theme" in result
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
assert "forest" in result
print("✅ Theme list works")
print(f"Total themes: {result.count(chr(10))}")
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

**Problem**: Tests are cached and run too fast (no output)

**Solution**: Clear cache for fresh build

```bash
just clear-vm-test-cache
nix build .#checks.x86_64-linux.arda-cli-vm-help
```

**Problem**: VM hangs during boot

**Solution**: Clear cache and rebuild with verbose output

```bash
just clear-vm-test-cache
nix build .#checks.x86_64-linux.arda-cli-vm-help --no-out-link 2>&1 | tee /tmp/vm-debug.log
```

**Problem**: Test fails intermittently

**Solution**: Run multiple times

```bash
for i in {1..5}; do
    echo "Run $i:"
    nix build .#checks.x86_64-linux.arda-cli-vm-help
done
```

**Problem**: Need to see VM output

**Solution**: Build without cache

```bash
just clear-vm-test-cache
nix build .#checks.x86_64-linux.arda-cli-vm-help --no-out-link
# Check result/ directory for test logs
```

---

## CI/CD Integration

Tests run automatically in GitHub Actions for every push and pull request.

### Workflow Overview

**File**: `.github/workflows/test.yml`

**Jobs** (6 total):

1. **validate** - Fast validation (flake check, pre-commit)
2. **test-fast** - Build package + run fast tests
3. **test-all** - Complete test suite (both phases)
4. **test-vm** - VM tests (scheduled/manual only)
5. **build-docs** - Build CLI binary
6. **summary** - Aggregate results

### Job Details

#### validate Job (1-2 minutes)

**Purpose**: Fast feedback on code quality

**Steps**:

1. Check out code
2. Install Nix
3. Setup cachix (optional)
4. Run `nix flake check`
5. Run pre-commit hooks

**When**: Every push/PR

#### test-fast Job (2-3 minutes)

**Purpose**: Build package and run fast tests

**Steps**:

1. Check out code
2. Install Nix
3. Setup cachix (optional)
4. Build `arda-cli` package (runs Phase 1 tests during build)
5. Upload coverage report

**When**: Every push/PR

#### test-all Job (3-5 minutes)

**Purpose**: Run complete test suite

**Steps**:

1. Check out code
2. Install Nix
3. Setup cachix (optional)
4. Run `just test-all` (runs both Phase 1 and Phase 2)
5. Upload test reports

**When**: Every push/PR

#### test-vm Job (5-10 minutes)

**Purpose**: Run VM tests

**Steps**:

1. Check out code
2. Install Nix
3. Run VM tests via `just test-vm`
4. Upload test logs

**When**:

- Manual dispatch only (workflow_dispatch)
- Nightly schedule (00:00 UTC)
- Push to `testing` branch

**Why separate**: VM tests are slow and resource-intensive

#### build-docs Job (2-3 minutes)

**Purpose**: Build and archive CLI binary

**Steps**:

1. Check out code
2. Install Nix
3. Build `arda-cli`
4. Archive binary

**When**: Every push/PR
**Artifact**: CLI binary available for download

#### summary Job (< 1 minute)

**Purpose**: Aggregate test results

**Steps**:

1. Download all artifacts
2. Post summary to PR
3. Update check status

**When**: After all test jobs complete

### CI Triggers

**Automatic Triggers**:

- Push to `main`, `master`, `testing` branches
- Pull requests to `main`, `master`, `testing` branches

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
   @pytest.mark.without_core
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
   @pytest.mark.without_core
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

### Two-Phase Pattern

1. **Choose the Right Phase**

   **Phase 1 (without_core)**:
   - Testing pure functions
   - Testing library code
   - Testing configuration parsing
   - Testing overlay/configurations

   **Phase 2 (with_core)**:
   - Testing CLI workflows
   - Testing file operations
   - Testing component integration
   - Testing arda-core dependencies

2. **Mark Appropriately**

   ```python
   # For Phase 1
   @pytest.mark.without_core

   # For Phase 2
   @pytest.mark.with_core
   ```

### Performance

1. **Mark Slow Tests**

   ```python
   # Good
   @pytest.mark.slow
   @pytest.mark.integration
   @pytest.mark.with_core
   def test_full_workflow():
       # Slow test marked appropriately
   ```

2. **Keep Fast Tests Fast**

   ```python
   # Good - no network calls, minimal I/O
   @pytest.mark.fast
   @pytest.mark.without_core
   def test_parse_bool():
       assert parse_bool("true") is True
   ```

3. **Parallel Execution**

   ```bash
   # Run tests in parallel
   pytest -n auto
   ```

### Coverage

**Current Thresholds**:

- Phase 1 (without-core): 30% minimum
- Phase 2 (with-core): 30% minimum

1. **Focus on Critical Paths**
   - Configuration parsing
   - Error handling
   - CLI commands
   - Theme system

2. **Don't Chase 100%**
   - Quality over quantity
   - 30% minimum is reasonable for both phases
   - Focus on critical code paths

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

1. Run only Phase 1 (without-core) for development

   ```bash
   just test-without-core
   ```

2. Run only fast tests

   ```bash
   just test-fast
   ```

3. Mark integration tests as slow

   ```python
   @pytest.mark.slow
   @pytest.mark.integration
   @pytest.mark.with_core
   def test_slow_workflow():
       pass
   ```

### VM Tests Hanging

**Problem**: VM tests hang at boot

**Solution**:

1. Ensure `machine.start()` is in test

   ```nix
   testScript = ''
     machine.start()  # This is required!
     machine.wait_for_unit("default.target")
   ```

2. Clear VM test cache

   ```bash
   just clear-vm-test-cache
   ```

3. Rebuild test without cache

   ```bash
   nix build .#checks.x86_64-linux.arda-cli-vm-help --no-out-link
   ```

### Interactive Prompt Hang

**Problem**: Test hangs waiting for input

**Solution**: Use `--force` flag to avoid prompts

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

**Problem**: Coverage below threshold (30%)

**Solutions**:

1. Add more tests

   ```bash
   # Check what's not covered
   pytest --cov=pkgs/arda-cli/arda_cli --cov-report=term-missing
   ```

2. Focus on critical paths
   - Config parsing
   - Error handling
   - CLI workflows

3. Update thresholds if needed
   - Edit `pkgs/arda-cli/default.nix`
   - Update `--cov-fail-under` values

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

3. Use justfile commands

   ```bash
   just test-fast
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

3. Clear Nix store if needed

   ```bash
   nix store gc
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

### Phase Selection Issues

**Problem**: Tests not running in the right phase

**Solution**:

1. Check test markers

   ```bash
   # Check which markers a test has
   pytest --collect-only -m "test_name"
   ```

2. Ensure Phase 1 tests have `@pytest.mark.without_core`

3. Ensure Phase 2 tests have `@pytest.mark.with_core`

4. Run specific phase

   ```bash
   # Phase 1 only
   pytest -m "without_core"

   # Phase 2 only
   pytest -m "with_core"
   ```

---

## Quick Reference

### Command Cheat Sheet

| Task | Command |
|------|---------|
| Run fast tests | `just test-fast` |
| Run Phase 1 tests | `just test-without-core` |
| Run Phase 2 tests | `just test-with-core` |
| Run all tests | `just test-two-phase` |
| Run network tests | `just test-network` |
| Run VM tests | `just test-vm-cli` |
| Run specific VM test | `just test-vm-cli-help` |
| Build with tests | `nix build .#arda-cli` |
| Run flake check | `nix flake check` |
| Clear VM cache | `just clear-vm-test-cache` |
| Generate coverage | `just coverage` |
| Check coverage | `just coverage-check` |

### Directory Quick Reference

| Directory | Purpose |
|-----------|---------|
| `pkgs/arda-cli/arda_cli/tests/unit/` | Phase 1: Fast unit tests |
| `pkgs/arda-cli/arda_cli/tests/integration/` | Phase 2: Integration tests |
| `tests/nixos/cli/*/` | VM tests |
| `pkgs/testing/` | Test utilities & fixtures |
| `checks/` | Flake checks |
| `pytest.ini` | Pytest configuration |
| `justfile` | Test shortcuts |

### Marker Quick Reference

| Marker | Run In |
|--------|--------|
| `fast` | Build, CI, pre-commit |
| `slow` | CI only |
| `without_core` | All levels (Phase 1) |
| `with_core` | CI (Phase 2) |
| `unit` | All levels |
| `integration` | CI |
| `cli` | All levels |
| `config` | All levels |
| `theme` | All levels |
| `network` | All levels |
| `nix` | CI |
| `vm` | Manual, CI |
| `system` | Never (requires special setup) |

### Test File Naming

| Type | Pattern | Example |
|------|---------|---------|
| Unit test file | `test_*.py` | `test_config_parsing.py` |
| Unit test function | `test_*()` | `test_loads_valid_toml()` |
| Integration test file | `test_*workflow*.py` | `test_config_workflow.py` |
| VM test file | `test-*.nix` | `test-help-output.nix` |
| VM test name | `"arda-cli-vm-*"` | `"arda-cli-vm-help"` |

### Phase Selection

| Phase | Marker | Tests | Run With |
|-------|--------|-------|----------|
| Phase 1 | `without_core` | 180 tests | `just test-without-core` |
| Phase 2 | `with_core` | 45 tests | `just test-with-core` |
| Both | N/A | 225 tests | `just test-two-phase` |

### Common Assertions

**Unit Tests**:

```python
assert result == expected
assert value is True
assert value is False
assert "text" in result
assert len(items) == 5
```

**Integration Tests**:

```python
assert result.exit_code == 0
assert Path('file.toml').exists()
assert "expected" in result.output
```

**VM Tests**:

```nix
assert "expected" in result
machine.succeed("test -f /path/file")
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
| `nix store gc` | Garbage collect Nix store |

### Test Statistics

**Current Test Counts**:

- Total: 225 tests
- Phase 1 (without-core): 180 tests
- Phase 2 (with-core): 45 tests
- Network tests: 12 tests
- VM test suites: 4 suites (~35 tests)
- Overlay tests: 4 tests

### Coverage Thresholds

| Phase | Threshold |
|-------|-----------|
| Phase 1 (without-core) | 30% |
| Phase 2 (with-core) | 30% |

### Getting Help

1. **Justfile**: `just help` - Lists all test commands
2. **pytest**: `pytest --help` - Pytest options
3. **CI docs**: `.github/CI.md` - CI/CD documentation
4. **Implementation plan**: `bmad-docs/plan-testing.md` - Full history

---

## Conclusion

The arda-core testing framework provides comprehensive test coverage through a multi-layered, two-phase approach:

### Key Components

1. **Phase 1 (without-core)** - Fast isolated tests (180 tests)
   - Unit tests for isolated functions
   - Overlay regression tests
   - Network utility tests
   - Config and theme tests

2. **Phase 2 (with-core)** - Comprehensive integration tests (45 tests)
   - CLI workflow tests
   - Config file operations
   - Nix integration tests
   - VM integration tests

3. **VM Tests** - End-to-end testing (4 test suites)
   - Help output tests
   - Config operations tests
   - Config priority tests
   - Theme command tests

4. **CI/CD Integration** - Automated testing (6 jobs)
   - validate (fast feedback)
   - test-fast (build + fast tests)
   - test-all (both phases)
   - test-vm (scheduled/manual)
   - build-docs (binary build)
   - summary (result aggregation)

### Key Principles

- **Speed for Phase 1**: Fast feedback for developers
- **Isolation**: Tests don't interfere with each other
- **Two-Phase Pattern**: Clear separation of concerns
- **Comprehensive Coverage**: Multiple test types
- **Automated Execution**: CI/CD on every push/PR
- **Excellent Developer Experience**: Easy commands, clear documentation

### Getting Started

```bash
# Run fast tests (do this before every commit)
just test-fast

# Run Phase 1 tests
just test-without-core

# Run all tests
just test-two-phase

# Run VM tests (when needed)
just test-vm-cli
```

### Recent Changes

**Version 2.0 (2025-11-30)**:

- ✅ Implemented two-phase testing pattern (without_core / with_core)
- ✅ Moved overlay tests to Phase 1 (without_core)
- ✅ Removed verify-overlay.sh (tests integrated into Phase 1)
- ✅ Added network utility tests (port management, SSH)
- ✅ Updated coverage thresholds to 30% for both phases
- ✅ Created fixtures_arda.py for two-phase pattern
- ✅ Added comprehensive VM test suite (4 test suites)

### Questions or Issues

- See troubleshooting section above
- Check `.github/CI.md` for CI issues
- Review `bmad-docs/plan-testing.md` for historical context

### Contributing

- Follow the two-phase testing pattern
- Mark tests appropriately (`without_core` or `with_core`)
- Write tests for new features
- Update tests when code changes
- Maintain test quality and coverage
- Use justfile commands for consistency

---

**Document maintained by**: Development Team
**Last updated**: 2025-11-30
**Version**: 2.0
**Next review**: As needed with framework changes
