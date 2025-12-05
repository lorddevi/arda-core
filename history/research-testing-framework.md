# Testing Framework Research & Plan for arda-core

**Research Date**: 2025-11-26
**Last Updated**: 2025-11-27
**Current Status**: Comprehensive Design Phase
**Next Phase**: Implementation Planning

**Status**: This document has been updated with our finalized hybrid testing framework design, combining clan-core's proven patterns with arda-core's customizations based on detailed audit findings and user feedback.

---

## Executive Summary

This document outlines the comprehensive testing framework for arda-core and arda-cli, designed to ensure long-term stability, prevent regressions, and maintain code quality as the project evolves. Our approach follows a **hybrid design** that combines clan-core's proven testing patterns with arda-core's customizations for modularity and developer ergonomics.

**Finalized Approach**: After conducting a detailed audit of clan-core's testing infrastructure (see `/bmad-docs/research-testing-framework-clan.md`), we have adopted a hybrid strategy that:

- ✅ **Adopts clan-core's patterns**: Build-time testing, direct function calls, QEMU/KVM VMs, NixOS containers
- ✅ **Adds arda-core customizations**: Custom `arda` namespace, one-test-per-file structure, fast/slow markers, optional orchestration
- ✅ **Provides multiple execution levels**: Build-time (automatic) → Nix namespace (discoverable) → Orchestration scripts (convenience) → Justfile (ergonomics)

This balanced approach ensures rapid feedback during development while maintaining comprehensive validation for production quality.

## Table of Contents

1. [Why We Need a Comprehensive Testing Framework](#why-we-need-a-comprehensive-testing-framework)
2. [Our Goals and Principles](#our-goals-and-principles)
3. [Problems We're Solving](#problems-were-solving)
4. [Proposed Testing Framework Structure](#proposed-testing-framework-structure)
5. [Test Types and Scope](#test-types-and-scope)
6. [Naming Conventions and Organization](#naming-conventions-and-organization)
7. [Integration with Development Workflow](#integration-with-development-workflow)
8. [Lessons from Clan-Core](#lessons-from-clan-core)
9. [Our Finalized Hybrid Design](#our-finalized-hybrid-design)
10. [Testing Tools and Techniques](#testing-tools-and-techniques)
11. [Initial Thoughts on Test Orchestration and Dev Ergonomics](#initial-thoughts-on-test-orchestration-and-dev-ergonomics)
12. [Next Steps](#next-steps)
13. [Known Things to Test For](#known-things-to-test-for)

---

## Why We Need a Comprehensive Testing Framework

arda-core and arda-cli implement several complex systems that are critical to the user experience:

### Complex Systems Requiring Testing

1. **Theme and Coloring System**
   - Dynamic color generation for CLI output
   - Multiple theme support (dracula, monokai, etc.)
   - Terminal compatibility (256-color, truecolor, ANSI)
   - Color contrast validation
   - Rendering across different terminal emulators

2. **Configuration Management**
   - TOML file parsing and validation
   - XDG base directory specification compliance
   - Project-level vs user-level configuration precedence
   - Environment variable overrides
   - Configuration migration and defaults

3. **Nix Integration**
   - nix-select hash baking and verification
   - Flake reference construction and validation
   - Nix command wrappers (eval, build, shell, store)
   - Error handling for Nix operations
   - Package allowlist security model

4. **CLI Interface**
   - Command parsing and argument validation
   - Multi-command workflows
   - Error messaging and user feedback
   - Exit code correctness

### Risk Assessment

Without comprehensive testing, we risk:

- **Silent Regressions**: Bugs introduced without detection
- **Color Display Issues**: Themes breaking across terminals
- **Configuration Corruption**: User settings becoming inaccessible
- **Nix Integration Failures**: Breakage during Nix operations
- **Poor User Experience**: CLI commands failing unpredictably

---

## Our Goals and Principles

### Primary Goals

1. **Regression Prevention**
   - Catch bugs before they reach users
   - Ensure changes don't break existing functionality
   - Maintain backward compatibility

2. **Rapid Feedback**
   - Fast test execution for immediate feedback during development
   - Progressive test layers (unit → integration → system)
   - Parallel execution support

3. **Comprehensive Coverage**
   - Test all critical code paths
   - Validate edge cases and error conditions
   - Cover various runtime environments

4. **Maintainability**
   - Easy to understand and modify tests
   - Clear test structure reduces cognitive load
   - Isolated tests prevent cascade failures

5. **Developer Productivity**
   - Tests serve as documentation for expected behavior
   - Easy to run relevant tests during development
   - Clear failure messages for quick debugging

### Design Principles

1. **Modularity**: One test per file, organized by functional area
2. **Isolation**: Each test runs independently without side effects
3. **Clarity**: Descriptive test names explain what is being tested
4. **Speed**: Prioritize fast unit tests for frequent execution
5. **Realism**: Integration and VM tests validate real-world scenarios
6. **Automation**: Tests run automatically in CI/CD pipeline

---

## Problems We're Solving

### Historical Problems in Software Projects

Many software projects suffer from:

1. **Monolithic Test Files**
   - Single test file containing dozens of unrelated tests
   - Merge conflicts when multiple developers work on different features
   - Difficult to run specific tests
   - Tests become tightly coupled and brittle

2. **Incomplete Test Coverage**
   - Critical systems lack tests (configuration, error handling)
   - Edge cases are untested
   - Integration between components is unverified

3. **Slow Test Execution**
   - All tests run sequentially
   - No separation between unit and integration tests
   - Development slow down due to long test runs

4. **Unreliable Tests**
   - Tests depend on external state (filesystem, environment)
   - Non-deterministic behavior
   - Difficult to debug failures

### Our Solutions

1. **Modular Structure**
   - One test per file
   - Files organized by functional domain
   - Easy to add, remove, or modify tests
   - Clear ownership boundaries

2. **Multi-Layer Testing**
   - Unit tests for isolated logic (fast)
   - Integration tests for component interaction (medium)
   - System/VM tests for end-to-end workflows (slow)
   - Progressive execution based on needs

3. **Isolation and Determinism**
   - Temporary directories for filesystem tests
   - Mocked external dependencies
   - Seeded random values for reproducibility
   - Clean test environment setup and teardown

4. **Performance Optimization**
   - Unit tests execute in milliseconds
   - Parallel test execution where possible
   - Selective test execution by directory or pattern
   - CI caching for faster builds

---

## Proposed Testing Framework Structure

### Directory Layout (Hybrid: Clan-Core Pattern + arda-core Customization)

Based on clan-core's proven structure with arda-core's requirements for modularity and discoverability:

```
arda-core/
├── pkgs/
│   ├── arda-cli/
│   │   ├── arda_lib/              # Shared library
│   │   │   └── tests/             # Tests for arda_lib modules
│   │   │       ├── unit/          # Unit tests (individual functions/classes)
│   │   │       ├── integration/   # Integration tests (multi-component)
│   │   │       └── nix/           # Nix-specific tests (library validation)
│   │   ├── arda_cli/              # CLI-specific code
│   │   │   └── tests/             # Tests for CLI modules
│   │   │       ├── unit/          # Unit tests (CLI logic)
│   │   │       ├── integration/   # Integration tests (CLI workflows)
│   │   │       └── cli/           # CLI command tests (direct function calls)
│   │   └── default.nix            # Package definition with build-time tests
│   └── testing/                   # Shared testing infrastructure
│       ├── run-tests.nix          # Test orchestration script
│       ├── fixtures/              # Test fixtures and data
│       └── helpers/               # Test helper utilities
│
├── tests/                         # Project-level tests
│   ├── unit/                      # Fast unit tests
│   │   ├── flake/                 # Flake configuration validation
│   │   ├── devshell/              # DevShell environment tests
│   │   └── overlay/               # Overlay functionality tests
│   ├── integration/               # Feature integration tests
│   │   ├── build-system/          # Justfile and build automation tests
│   │   └── package-build/         # Package building tests
│   └── nix/                       # Nix expression tests
│       ├── test_flake_structure.nix
│       ├── test_devshell_setup.nix
│       └── test_package_definitions.nix
│
└── vm-tests/                      # VM-based integration tests
    ├── test_user_workflow.nix     # Full user workflow in NixOS VM
    ├── test_nix_integration.nix   # Nix operations in VM
    └── test_configuration.nix     # Configuration management in VM
```

### Key Organizational Principles

#### 1. **Multi-Directory Pattern (Following Clan-Core)**

- `pkgs/arda-cli/arda_lib/tests/`: Tests for shared library components
- `pkgs/arda-cli/arda_cli/tests/`: Tests for CLI-specific functionality
- `pkgs/testing/`: Shared infrastructure (orchestration scripts, helpers)
- `tests/`: Project-level tests (flake, devshell, overlays)

#### 2. **One Test Per File (arda-core Requirement)**

- Each Python file contains exactly one `test_*` function
- Filename describes specific behavior: `test_parses_valid_toml.py`
- Easier maintenance: atomic updates, fewer merge conflicts
- Maximum flexibility: run individually or in groups

#### 3. **Test Categories via Markers (Inspired by Clan-Core)**

```python
# pytest markers for categorization
@pytest.mark.fast      # Unit tests, run with every build
@pytest.mark.slow      # Integration tests, VM tests
@pytest.mark.unit      # Unit test classification
@pytest.mark.integration # Integration test classification
@pytest.mark.vm        # Tests requiring VM
@pytest.mark.theme     # Theme-specific tests
@pytest.mark.config    # Configuration-specific tests
@pytest.mark.nix       # Nix integration tests
@pytest.mark.cli       # CLI-specific tests
```

#### 4. **Custom arda Namespace for Discovery**

Tests are exposed via custom Nix namespace for discoverability with **component context**

**Critical Requirement**: All test namespaces **MUST** include component context to avoid ambiguity

```nix
# In flake.nix - arda namespace with hierarchical organization
arda = {
  # Test groups by component and category (component context REQUIRED)
  tests = {
    "arda-cli.unit" = runTests ./pkgs/arda-cli/arda_cli/tests/unit/;
    "arda-cli.themes.unit" = runTests ./pkgs/arda-cli/arda_cli/tests/unit/themes/;
    "arda-cli.config.unit" = runTests ./pkgs/arda-cli/arda_cli/tests/unit/config/;
    "arda-cli.cli.unit" = runTests ./pkgs/arda-cli/arda_cli/tests/cli/;
    "arda-lib.nix.unit" = runTests ./pkgs/arda-cli/arda_lib/tests/unit/;
    "arda-lib.nix.integration" = runTests ./pkgs/arda-cli/arda_lib/tests/integration/;
  };

  # Test runners for convenience
  runners = {
    fast = runTestGroup "fast";
    unit = runTestGroup "all-unit";
    arda-cli = runTestGroup "arda-cli";
    arda-lib = runTestGroup "arda-lib";
    themes = runTestGroup "arda-cli-themes";
    config = runTestGroup "arda-cli-config";
    all = runTestGroup "all";
  };

  # Test helpers
  helpers = {
    "run-tests" = createTestRunner ./pkgs/testing/run-tests.nix;
  };

  # Metadata
  info = {
    totalTests = ...;
    categories = [...];
    byComponent = {
      arda-cli = ["unit" "integration" "cli"];
      arda-lib = ["unit" "nix" "integration"];
    };
  };
};
```

**Discovery via Nix Flake**:

```bash
# See all tests
nix flake show

# Query test inventory
nix eval .#arda.info.totalTests
nix eval .#arda.tests | jq 'keys'

# Run tests via namespace (WITH component context)
nix build .#arda.tests.arda-cli.unit
nix build .#arda.tests.arda-cli.themes.unit
nix build .#arda.tests.arda-lib.nix.unit
nix run .#arda.helpers.run-tests -- arda-cli-themes
```

### Why Component Context is Critical

❌ **Without component context**, test namespaces are ambiguous:

- `arda.tests.themes.unit` - Which component has themes? arda-cli? arda-lib? Future component?
- `arda.tests.config.unit` - Config for which component?
- `arda.tests.nix.unit` - Nix helpers for which component?

✅ **With component context**, everything is clear:

- `arda.tests.arda-cli.themes.unit` - Unambiguous: arda-cli's theme tests
- `arda.tests.arda-cli.config.unit` - Unambiguous: arda-cli's config tests
- `arda.tests.arda-lib.nix.unit` - Unambiguous: arda-lib's Nix helper tests

**Future-Proofing**: Even though currently only arda-cli has themes, when we add future components (e.g., `arda-web-ui`, `arda-api-server`), the namespace will already be properly namespaced to avoid confusion.

#### 5. **Build-Time Test Execution (Clan-Core Pattern)**

Following clan-core's approach of testing during package build:

### In `pkgs/arda-cli/default.nix`

```nix
{
  # Fast tests run with every package build (required)
  checkPhase = ''
    pytest -m "fast" -n auto \
      ./pkgs/arda-cli/arda_cli/tests/ \
      ./pkgs/arda-cli/arda_lib/tests/
  '';

  # Slow tests as separate optional derivations
  arda-cli-tests-slow = runCommand "arda-cli-tests-slow" { ... }
  ''
    pytest -m "slow"
    touch $out
  '';

  # Individual test derivations (for targeted testing)
  arda-cli-tests-config = runCommand "test-config" { ... }
  ''
    pytest ./pkgs/arda-cli/arda_cli/tests/unit/config/ -v
    touch $out
  '';
}
```

**Benefits**:

- ✅ Fast tests guaranteed to run (prevent regressions)
- ✅ Slow tests optional (explicit `nix build`)
- ✅ Individual test derivations (fine-grained control)
- ✅ No justfile required for test execution

#### 6. **Test Execution Hierarchy**

```bash
# Level 1: Automatic (fast tests in build)
nix build .#arda-cli  # ✓ Fast tests run automatically

# Level 2: Nix namespace (targeted)
nix build .#arda.tests."clan-cli.unit"
nix build .#arda.runners.themes

# Level 3: Orchestration script (convenience)
nix run .#arda.helpers.run-tests -- themes

# Level 4: Justfile (developer ergonomics)
just test          # runs: nix build .#arda-cli
just test-themes   # runs: nix run .#arda.helpers.run-tests -- themes
just test-all      # runs: nix build .#arda.runners.all
```

#### 7. **NixOS VM Tests (System-Level)**

For system-level integration testing, following clan-core's pattern:

- Location: `vm-tests/` directory
- Framework: NixOS test framework (QEMU/KVM)
- Purpose: End-to-end workflows, system integration
- Execution: `nix build .#vm-tests.test-user-workflow`
- Examples: Full user workflow, Nix operations, configuration management

#### 8. **Test Organization Benefits**

| Aspect | Approach | Benefit |
|--------|----------|---------|
| **Structure** | Per-package test directories | Tests near code they test |
| **Execution** | Build-time + optional derivations | Guaranteed quality + flexibility |
| **Discovery** | Custom `arda` namespace | Full visibility via `nix flake show` |
| **Modularity** | One test per file | Easy maintenance, atomic changes |
| **Orchestration** | Nix-native + helpers | Power + convenience |
| **Speed** | Fast/slow markers | Quick feedback + comprehensive testing |
| **Markers** | Category + speed classification | Flexible test selection |

#### 9. **Comparison with Clan-Core**

| Feature | Clan-Core | arda-core |
|---------|-----------|-----------|
| Build-time tests | ✅ Yes | ✅ Yes (fast only) |
| Test markers | ✅ Yes | ✅ Yes (more granular) |
| One-test-per-file | ❌ Monolithic | ✅ Modular |
| Custom namespace | ❌ No | ✅ `arda.tests.*` |
| Test discovery | ⚠️ Limited | ✅ Full via `nix flake show` |
| Test orchestration | ❌ None | ✅ `pkgs/testing` + helpers |
| VM tests | ✅ Yes | ✅ Yes (system-level) |
| Test derivation granularity | Categories only | Individual + groups |

**arda-core improves on clan-core** by adding:

- Better test discoverability (custom namespace)
- More granular test organization (one-test-per-file)
- Developer-friendly orchestration (optional helpers)
- Clear separation of fast/slow tests

---

## Test Types and Scope

### Test Markers (Clan-Core Pattern)

All tests use **pytest markers** for categorization and selection:

```python
# Speed markers (control when tests run)
@pytest.mark.fast      # Unit tests, run with every build
@pytest.mark.slow      # Integration/VM tests, run explicitly

# Category markers (group tests by functionality)
@pytest.mark.unit        # Unit tests
@pytest.mark.integration # Integration tests
@pytest.mark.vm          # Tests requiring VM
@pytest.mark.theme       # Theme system tests
@pytest.mark.config      # Configuration tests
@pytest.mark.nix         # Nix integration tests
@pytest.mark.cli         # CLI-specific tests

# Example usage
@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_parses_valid_toml():
    """Unit test for config parsing - runs with every build"""
    ...
```

**Marker Usage**:

- `pytest -m "fast"` - Run fast tests only
- `pytest -m "slow"` - Run slow tests only
- `pytest -m "theme"` - Run theme tests only
- `pytest -m "fast and unit"` - Fast unit tests
- `pytest -m "not vm"` - Exclude VM tests

---

### Unit Tests

**Locations**:

- `pkgs/arda-cli/arda_cli/tests/unit/`
- `pkgs/arda-cli/arda_lib/tests/unit/`
- `tests/unit/` (project-level)

**Markers**: `@pytest.mark.fast`, `@pytest.mark.unit`

**Purpose**: Validate individual components in isolation

**Scope**:

- Single functions or classes
- No external file system access
- No network calls
- Mocked Nix operations (subprocess.run)
- Mocked file I/O
- All dependencies injected
- **Direct function calls** (no CliRunner - following clan-core pattern)

**Example**: `pkgs/arda-cli/arda_cli/tests/unit/config/test_parses_valid_toml.py`

```python
"""Test that valid TOML configuration files are parsed correctly."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Markers for categorization and execution control
@pytest.mark.fast
@pytest.mark.unit
@pytest.mark.config
def test_parses_valid_toml():
    """Given a valid TOML string, parse_config should return parsed data"""
    # Mock file I/O
    with patch('arda_cli.lib.config.get_config_path', return_value=None):
        from arda_cli.lib.config import parse_config

        valid_toml = """
        [theme]
        name = "dracula"
        primary_color = "#282936"
        """
        config = parse_config(valid_toml)
        assert config["theme"]["name"] == "dracula"
        assert config["theme"]["primary_color"] == "#282936"
```

**Build Integration**: Run automatically during `nix build .#arda-cli`

```nix
checkPhase = ''
  pytest -m "fast" -n auto \
    ./pkgs/arda-cli/arda_cli/tests/ \
    ./pkgs/arda-cli/arda_lib/tests/
'';
```

**Runtime**: < 1ms per test
**Total Suite Runtime**: < 10 seconds (all unit tests)
**Execution Frequency**: On every `nix build`

---

### Integration Tests

**Locations**:

- `pkgs/arda-cli/arda_cli/tests/integration/`
- `pkgs/arda-cli/arda_lib/tests/integration/`
- `tests/integration/` (project-level)

**Markers**: `@pytest.mark.slow`, `@pytest.mark.integration`

**Purpose**: Verify components work together correctly

**Scope**:

- Multiple components interacting
- Real file system operations (in temp directories)
- Actual Nix commands using `nix eval` (may require Nix installation)
- Configuration files
- **Direct function calls** (following clan-core, not CliRunner)

**Example**: `pkgs/arda-cli/arda_cli/tests/integration/config/test_full_config_command_workflow.py`

```python
"""Test end-to-end config command workflow."""
import tempfile
from pathlib import Path

@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.config
def test_full_config_command_workflow():
    """Running 'arda config set theme.name dracula' should persist the configuration"""
    # Following clan-core pattern: direct function call, not CliRunner
    from arda_cli.commands.config.main import set_config

    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / 'config.toml'

        # Call function directly
        set_config('theme.name', 'dracula', config_file=str(config_path))

        # Verify persistence
        assert config_path.exists()
        with open(config_path) as f:
            content = f.read()
            assert 'name = "dracula"' in content
```

**Build Integration**: Optional derivation for slow tests

```nix
arda-cli-tests-slow = runCommand "arda-cli-tests-slow"
{
  nativeBuildInputs = testDependencies;
}
''
  pytest -m "slow" -n auto
  touch $out
'';
# Run with: nix build .#arda-cli-tests-slow
```

**Runtime**: 10-100ms per test
**Total Suite Runtime**: 30-60 seconds (all integration tests)
**Execution Frequency**: Explicit (not in regular build)
**Execution Frequency**: On every pull request, nightly builds

---

### CLI Tests

**Location**: `pkgs/arda-cli/arda_cli/tests/cli/`

**Purpose**: Test CLI commands using Click's CliRunner

**Scope**:

- Individual commands and subcommands
- Help text generation
- Exit code validation
- Argument parsing
- Error handling

**Example**: `pkgs/arda-cli/arda_cli/tests/cli/test_arda_help.py`

```python
"""Test CLI help commands."""
from click.testing import CliRunner
from arda_cli.main import main

def test_arda_help():
    """Test that 'arda --help' displays help correctly"""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "config" in result.output
    assert "theme" in result.output

def test_config_help():
    """Test that 'arda config --help' shows config options"""
    runner = CliRunner()
    result = runner.invoke(main, ['config', '--help'])

    assert result.exit_code == 0
    assert "view" in result.output
    assert "set" in result.output
    assert "init" in result.output
```

**Runtime**: 5-50ms per test
**Total Suite Runtime**: 10-20 seconds
**Execution Frequency**: On every commit

---

### Nix Tests

**Locations**:

- `pkgs/arda-cli/arda_lib/tests/nix/`
- `tests/nix/` (project-level)

**Purpose**: Validate Nix expressions and library functions

**Scope**:

- Nix expression evaluation
- nix-select selector parsing
- Hash baking verification
- Flake reference construction
- Library function correctness

**Example**: `test_selector_parsing.nix`

```nix
{ pkgs, nix-select, ... }:

{
  test_selector_parsing = pkgs.runCommand "test-selector-parsing"
    { nativeBuildInputs = [ nix-select ]; }
    ''
      # Test that selector parsing works correctly
      selector="{packages,tests}"

      # Parse selector using nix-select
      result=$(nix-select parse "$selector")

      # Verify expected structure
      if [[ "$result" == *"packages"* ]] && [[ "$result" == *"tests"* ]]; then
        echo "SUCCESS: Selector parsed correctly"
      else
        echo "FAILURE: Selector parsing failed"
        exit 1
      fi

      touch $out
    '';

  # ... more Nix tests ...
}
```

**Runtime**: 5-30 seconds
**Total Suite Runtime**: 30 seconds (all Nix tests)
**Execution Frequency**: On every pull request, integration builds

---

### VM Tests (`tests/vm/`)

**Purpose**: Validate complete system behavior in real environment

**Scope**:

- Full application lifecycle
- Real NixOS installation
- Multi-user scenarios
- System integration
- Real-world usage patterns

**Example**: `test_user_workflow.nix`

```nix
{ config, pkgs, ... }:

{
  test_user_workflow = pkgs.vmTest.makeTest {
    name = "arda-user-workflow";

    machine = { config, pkgs, ... }: {
      environment.systemPackages = [
        pkgs.arda-cli
        pkgs.nix
      ];

      # Test script runs in VM
      testScript = ''
        machine.succeed("arda --help")
        machine.succeed("arda config set theme.name dracula")
        machine.succeed("arda config list")
        machine.succeed("test -f ~/.config/arda/config.toml")
      '';
    };
  };
}
```

**Runtime**: 2-5 minutes per test
**Total Suite Runtime**: 5-15 minutes (all VM tests)
**Execution Frequency**: On main branch commits, release candidates, nightly

---

## Naming Conventions and Organization

### Test File Naming

**Format**: `test_{behavior_being_tested}.py`

Guidelines:

- Use snake_case
- Describe the specific behavior or scenario
- Start with `test_` (pytest convention)
- Be descriptive but concise

Examples:

- ✅ Good: `test_parses_valid_toml.py`, `test_theme_switching.py`
- ❌ Bad: `test_config.py` (too broad), `test_1.py` (not descriptive)

### Test Function Naming

**Format**: `test_{scenario}_{expected_outcome}`

Examples:

```python
def test_given_valid_toml_when_parsing_then_returns_config_object():
    """Test parsing valid TOML returns correct config structure"""

def test_when_config_file_missing_then_creates_with_defaults():
    """Test that missing config file creates default configuration"""

def test_given_dracula_theme_when_rendering_text_then_applies_purple():
    """Test that dracula theme applies correct colors to text output"""
```

### Directory Naming

**Format**: `{domain_or_component}/`

Examples:

- `config/` - Configuration management
- `themes/` - Theme and color system
- `nix_helpers/` - Nix integration utilities
- `cli/` - Command-line interface
- `nix_operations/` - Nix workflow integration

### Test Documentation

Each test file should include:

1. **Module docstring** (optional): Brief description of what is being tested
2. **Function docstring** (required): Clear description of scenario and expectation
3. **Inline comments**: Clarify complex logic or edge cases

---

## Integration with Development Workflow

### Test Execution Patterns

### During Development (Fast Feedback)

```bash
# Run all unit tests for CLI
pytest pkgs/arda-cli/arda_cli/tests/unit/

# Run all unit tests for library
pytest pkgs/arda-cli/arda_lib/tests/unit/

# Run specific test file
pytest pkgs/arda-cli/arda_cli/tests/unit/config/test_parses_valid_toml.py

# Run tests for a specific feature
pytest pkgs/arda-cli/arda_cli/tests/unit/themes/

# Run CLI tests specifically
pytest pkgs/arda-cli/arda_cli/tests/cli/

# Run with coverage
pytest pkgs/arda-cli/arda_cli/tests/unit/ --cov=arda_cli
```

### Before Commit (Local Validation)

```bash
# Run unit and integration tests for CLI
pytest pkgs/arda-cli/arda_cli/tests/

# Run unit and integration tests for library
pytest pkgs/arda-cli/arda_lib/tests/

# Run CLI tests
pytest pkgs/arda-cli/arda_cli/tests/cli/

# Run project-level tests
pytest tests/unit/ tests/integration/

# Run Nix tests
nix eval --file tests/nix/test_flake_structure.nix
```

### CI/CD Pipeline (Comprehensive)

```bash
# Stage 1: Fast feedback (unit tests)
pytest pkgs/arda-cli/arda_cli/tests/unit/ --cov=arda_cli
pytest pkgs/arda-cli/arda_lib/tests/unit/ --cov=arda_lib
pytest tests/unit/

# Stage 2: CLI and integration tests
pytest pkgs/arda-cli/arda_cli/tests/cli/
pytest pkgs/arda-cli/arda_cli/tests/integration/
pytest pkgs/arda-cli/arda_lib/tests/integration/
pytest tests/integration/

# Stage 3: Nix tests
nix eval --file tests/nix/

# Stage 4: Container/VM tests (slower, run on main branch)
# These will be researched and implemented based on clan-core's approach
```

### When to Write Tests

### New Feature

1. Write unit tests for core logic
2. Write integration tests for workflows
3. Write VM tests if system-level behavior changes

### Bug Fix

1. Write regression test that catches the bug
2. Verify fix with existing tests
3. Add edge case tests if applicable

### Refactoring

1. Ensure existing tests pass
2. Add tests for new/refactored code
3. Remove obsolete tests

### Performance Changes

1. Add benchmarks if critical
2. Ensure no regression in test execution time

### Test Review Process

1. **Unit Tests**: Review with code review
2. **Integration Tests**: Review with feature changes
3. **Nix Tests**: Review with library changes
4. **VM Tests**: Review for architecture changes

---

## Lessons from Clan-Core

### Clan-Core's Testing Approach

Based on documentation at `/home/ld/src/clan-core/docs/site/guides/contributing/testing.md` and our audit:

### Multi-Directory Structure

```
clan-core/
├── pkgs/
│   ├── clan-cli/
│   │   ├── clan_lib/          # Shared library
│   │   │   └── tests/         # Tests for library
│   │   ├── clan_cli/          # CLI-specific code
│   │   │   └── tests/         # Tests for CLI
│   │   └── clan_cli.nix       # Package definition
│   └── testing/               # Shared testing infrastructure
│       └── (test helpers, fixtures)
├── checks/                    # VM tests (project root)
│   └── x86_64-linux.{test-name}.nix
└── tests/                     # Python tests (some projects)
    ├── unit/
    └── integration/
```

### Testing Methods

1. **NixOS VM Tests** (Primary)
   - Located in `/checks/` directory
   - Each test exported as `checks.x86_64-linux.{test-name}`
   - Full system validation in virtual machines
   - Tests real-world usage scenarios

2. **Python pytest** (Supporting)
   - Unit/integration tests in package directories
   - Coverage reporting with pytest-cov
   - Tests for library and CLI components

3. **Nix eval tests** (Library Functions)
   - Direct evaluation of Nix expressions
   - Library function testing
   - Flake validation

### What We Can Learn

1. **VM Tests as Primary Validation**: Clan relies heavily on VM tests for system-level correctness
2. **Realistic Testing**: Tests run in actual NixOS environments, not mocks
3. **Exported Check Functions**: VM tests are Nix packages that can be built and run
4. **Multi-Directory Pattern**: Tests are organized near the code they test
5. **Shared Infrastructure**: `pkgs/testing` provides common test utilities

### Adaptation for arda

### Structure Adaptations

- Follow clan-core's multi-directory pattern
- Add `tests/` at project root (instead of `checks/`)
- Maintain separate test directories for `arda_lib` and `arda_cli`
- Create `pkgs/testing/` for shared infrastructure

### Testing Approach Adaptations

- **VM Tests**: Like clan-core, for system-level validation
- **Container Tests**: NEW - For faster isolation than VMs when full VM isn't needed
- **More Unit Tests**: Faster feedback during development
- **One-Test-Per-File**: Better maintainability than clan-core's approach

### Our Approach Combines

- **Clan's Multi-Directory Pattern**: Tests organized with code
- **Clan's VM Testing**: System-level validation
- **Clan's Realism**: Actual Nix environments, not mocks
- **Modern Python Practices**: Comprehensive unit/integration test suite
- **Maintainability Focus**: Modular, one-test-per-file structure

---

## Our Finalized Hybrid Design

Based on the clan-core audit and our requirements, we have designed a hybrid testing framework that **adopts clan-core's proven patterns while adding arda-core customizations** for enhanced discoverability and maintainability.

### Design Philosophy

**We asked ourselves**: How can we combine clan-core's proven build-time testing approach with arda-core's need for modularity and discoverability?

**Our answer**: Adopt what works (build-time execution, VM testing, direct function calls) and enhance what we need (namespace discovery, one-test-per-file, orchestration convenience).

### Key Design Decisions

#### 1. Adopt Clan-Core's Build-Time Testing ✅

**Why**: Clan runs tests during `nix build`, ensuring code quality is maintained with every build.

**How We Implement**:

```nix
# In pkgs/arda-cli/default.nix
checkPhase = ''
  pytest -m "fast" -n auto \
    ./pkgs/arda-cli/arda_cli/tests/unit/ \
    ./pkgs/arda-cli/arda_lib/tests/
'';
```

**Our Enhancement**: We add fast/slow markers to ensure only fast tests run in build:

```python
@pytest.mark.fast  # Only fast tests run in build
@pytest.mark.unit
def test_config_parsing():
    ...
```

---

#### 2. Reject Clan-Core's "No Orchestration" Philosophy

**Clan's approach**: No test orchestration - run individual `nix build .#checks.x86_64-linux.{test-name}` or nothing

**Our approach**: Optional test orchestration via custom namespace + orchestration scripts

**Why**: While clan-core's approach is simple, it doesn't scale well for:

- Running related tests together (e.g., all config tests)
- Developer ergonomics during active development
- CI/CD pipelines needing categorized execution

**Our Implementation**:

```nix
# Custom arda namespace in flake.nix
arda = {
  tests = {
    "arda-cli.unit" = runTestGroup "arda-cli unit tests";
    "arda-cli.config.unit" = runTestGroup "config unit tests";
    "arda-cli.themes.unit" = runTestGroup "theme tests";
    "arda-lib.nix.unit" = runTestGroup "nix helper unit tests";
  };
  runners = {
    fast = runAllFastTests;
    all = runAllTests;
  };
};
```

**Usage**:

```bash
# Simple: Run all fast tests (like clan)
nix build .#arda-cli  # Fast tests run automatically

# Discoverable: See all tests
nix flake show # Shows arda.tests.*

# Categorized: Run theme tests WITH component context
nix build .#arda.tests.arda-cli.themes.unit

# Categorized: Run config tests WITH component context
nix build .#arda.tests.arda-cli.config.unit

# Orchestrated: Run via helper script
nix run .#arda.helpers.run-tests -- themes
```

---

#### 3. Enhance Discoverability with Custom Namespace

**Clan's limitation**: Tests are hidden in `checks.*` namespace, discoverable only by knowing exact names

**Our solution**: Custom `arda` namespace with hierarchical organization including component context

**Critical Requirement**: All test namespaces **MUST** include component context to avoid ambiguity

- ❌ Bad: `arda.tests.themes.unit` (what component has themes?)
- ✅ Good: `arda.tests.arda-cli.themes.unit` (clear: arda-cli's theme unit tests)
- ❌ Bad: `arda.tests.config.unit` (what component's config?)
- ✅ Good: `arda.tests.arda-cli.config.unit` (clear: arda-cli's config unit tests)

**Namespace Pattern**: `arda.tests.{component}.{subcategory}.{type}`

**MUST INCLUDE COMPONENT CONTEXT** - No exceptions:

- ✅ `arda.tests.arda-cli.unit` - All unit tests for arda-cli
- ✅ `arda.tests.arda-cli.themes.unit` - Unit tests for arda-cli's theme system
- ✅ `arda.tests.arda-cli.config.unit` - Unit tests for arda-cli's config system
- ✅ `arda.tests.arda-lib.nix.unit` - Unit tests for arda-lib's Nix helpers
- ❌ `arda.tests.themes.unit` - **NEVER** - Ambiguous, no component context
- ❌ `arda.tests.config.unit` - **NEVER** - Ambiguous, no component context
- ❌ `arda.tests.nix.unit` - **NEVER** - Ambiguous, no component context

**Rule**: Every test namespace path MUST start with a component name (arda-cli, arda-lib, etc.)

**Benefits**:

```bash
# See all tests at a glance
nix flake show

# Query test inventory
nix eval .#arda.info.totalTests
nix eval .#arda.info.categories

# Run by category WITH component context
nix build .#arda.tests.arda-cli.config.unit
nix build .#arda.tests.arda-cli.themes.unit
nix build .#arda.tests.arda-lib.nix.unit
nix build .#arda.runners.fast

# Discover and run related tests with component filter
nix eval .#arda.tests | jq 'keys[] | select(startswith("arda-cli"))'
```

---

#### 4. Modularize Test Structure

**Clan's pattern**: Tests organized with code, but typically multiple tests per file

**Our enhancement**: One-test-per-file for maximum modularity

**Benefits**:

- Easier to run specific tests: `pytest test_config_parsing.py`
- Fewer merge conflicts (atomic changes)
- Clearer test purpose (filename describes behavior)
- Easier to disable/test individual scenarios

**Structure**:

```
tests/
├── unit/
│   ├── config/
│   │   ├── test_parses_valid_toml.py
│   │   ├── test_missing_config_handling.py
│   │   ├── test_config_priority.py
│   │   └── test_invalid_toml_error.py
│   ├── themes/
│   │   ├── test_theme_color_mapping.py
│   │   ├── test_theme_validation.py
│   │   └── test_rich_click_integration.py
```

---

#### 5. Adopt Clan-Core's CLI Testing Pattern

**Clan's approach**: Direct function calls (not CliRunner or subprocess)

**Example from clan-core**:

```python
# clan tests use direct imports and function calls
from clan_cli.lib.config import parse_config
result = parse_config(valid_toml)
assert result["theme"]["name"] == "dracula"
```

**Why this works**:

- Faster (no process spawn)
- Easier to mock dependencies
- Tests business logic, not Click plumbing
- Aligns with clan-core's philosophy

**Our adoption**: Following clan-core's pattern for unit/integration tests

- Unit tests: Direct function imports + mocking
- Integration tests: Direct function calls in temp directories
- CLI tests: Still use CliRunner for command testing (where needed)

---

### Execution Hierarchy

We provide **four levels of test execution** for different needs:

#### Level 1: Automatic (Build-Time) - Like Clan-Core

```bash
nix build .#arda-cli  # Fast tests run automatically
```

**Purpose**: Guarantee code quality with every build
**Tests**: Only `@pytest.mark.fast` tests
**Who Uses**: CI/CD, automatic quality gates

#### Level 2: Discoverable (Nix Namespace) - Our Enhancement

```bash
nix flake show  # See all tests
nix build .#arda.tests.arda-cli.themes.unit  # Component context included
nix build .#arda.tests.arda-cli.config.unit  # Component context included
```

**Purpose**: Easy discovery and selective execution
**Tests**: Any test or test group
**Who Uses**: Developers exploring test suite
**Critical**: All namespaces include component context (arda-cli, arda-lib, etc.)

#### Level 3: Orchestrated (Scripts) - Our Enhancement

```bash
nix run .#arda.helpers.run-tests -- arda-cli-themes
```

**Purpose**: Convenient categorized execution
**Tests**: Groups (themes, config, all unit, all fast)
**Who Uses**: Daily development workflows
**Naming**: Scripts use component-prefixed names (e.g., `arda-cli-themes`, `arda-lib-nix`)

#### Level 4: Ergonomic (Justfile) - Our Enhancement

```bash
just test           # Run fast tests
just test-themes    # Run theme tests
just test-all       # Run everything
```

**Purpose**: Developer convenience
**Tests**: Any
**Who Uses**: Quick commands during development

**Why Four Levels?**:

1. **Automatic** ensures quality (like clan-core)
2. **Discoverable** makes tests visible (our improvement)
3. **Orchestrated** provides convenience (our improvement)
4. **Ergonomic** supports rapid iteration (our improvement)

Each level serves a different need and audience.

---

### Clan-Core vs Arda-Core Comparison

| Aspect | Clan-Core | Arda-Core (Our Design) | Why We Changed |
|--------|-----------|------------------------|----------------|
| **Build-time tests** | ✅ Yes (all tests) | ✅ Yes (fast only) | Faster builds, clearer separation |
| **Test discovery** | ⚠️ Limited (`checks.*`) | ✅ Full (`arda` namespace) | Better visibility and exploration |
| **Test markers** | ✅ Yes (with_core, etc.) | ✅ Yes (fast, slow, unit, theme, etc.) | More granular categorization |
| **Test structure** | ⚠️ Multiple per file | ✅ One per file | Easier maintenance, fewer conflicts |
| **Orchestration** | ❌ None | ✅ Optional (namespace + scripts) | Developer ergonomics |
| **Execution levels** | 1 (build only) | 4 (build → namespace → scripts → justfile) | Different needs, different levels |
| **CLI testing** | Direct functions | Direct functions (adopted) | Proven pattern, faster tests |
| **VM testing** | ✅ Yes (checks/) | ✅ Yes (vm-tests/) | Adopted proven approach |
| **Namespace** | Standard (checks, packages) | Custom (`arda.tests.*`, `arda.runners.*`) | Enhanced discoverability |
| **CI integration** | Build-time only | Multi-level (fast in build, selective in CI) | Optimized CI pipelines |

**Bottom Line**: We keep what works (build-time, VMs, direct calls) and enhance what needs improvement (discoverability, modularity, ergonomics).

---

## Testing Tools and Techniques

### Click CliRunner - CLI Testing Framework

**Purpose**: Test Click-based CLI commands without spawning real processes

**Location**: `pkgs/arda-cli/arda_cli/tests/cli/`

**Example**: `test_arda_help.py`

```python
from click.testing import CliRunner
from arda_cli.main import main

def test_arda_help():
    """Test that 'arda --help' displays help correctly"""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "config" in result.output
    assert "theme" in result.output

def test_config_view():
    """Test config view command"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a config file
        Path("config.toml").write_text('[theme]\nname = "forest"')

        result = runner.invoke(main, ['config', 'view'])

        assert result.exit_code == 0
        assert "theme.name" in result.output
        assert "forest" in result.output
```

**Advantages**:

- Fast execution (no process spawn)
- Easy setup/teardown
- Captures output, exit codes, exceptions
- Can create temporary filesystems
- Tests Click context objects

**Use For**:

- Individual command testing
- Help text validation
- Argument parsing
- Exit code verification
- Error handling

---

### Visual Testing - FORCE_COLOR + hexdump

**Challenge**: Testing theme and color output without manual inspection

**Solution**: Use `FORCE_COLOR=1` environment variable + `hexdump -C` to verify ANSI codes

**Example**: `test_theme_colors.py`

```python
import subprocess
import os

def test_theme_applies_correct_colors():
    """Verify theme produces expected ANSI color codes"""
    # Run command with forced colors
    result = subprocess.run(
        ["arda", "config", "view"],
        env={**os.environ, "FORCE_COLOR": "1"},
        capture_output=True
    )

    # Check for ANSI escape sequences
    assert b"\x1b[" in result.stdout, "No ANSI escape codes found"

    # Check for truecolor (24-bit) indicator
    assert b"38;2" in result.stdout, "No truecolor codes found"

    # Alternative: pipe through hexdump to see exact codes
    hexdump = subprocess.run(
        ["hexdump", "-C"],
        input=result.stdout,
        capture_output=True
    )

    # Verify specific color codes are present
    # This makes color testing deterministic and verifiable
    assert b"1b[38;2" in hexdump.stdout
```

**Use For**:

- Theme color verification
- ANSI code validation
- Terminal compatibility testing
- Visual regression prevention

---

### Nix Testing - Container vs VM Approach

**Challenge**: Testing Nix operations requires real Nix installation

**Option A: NixOS Container Tests** (Faster)

```nix
# pkgs/testing/containers/test-nix-container.nix
{ pkgs, ... }:

pkgs.runCommand "test-nix-in-container"
  {
    buildInputs = [ pkgs.nix pkgs.arda-cli ];
  }
  ''
    # Test in container environment
    nix --version
    arda --version

    # Run arda commands with real Nix
    nix eval 'nixpkgs#hello' --raw

    touch $out
  ''
```

**Option B: NixOS VM Tests** (Slower, More Complete)

```nix
# tests/vm/test_user_workflow.nix
{ config, pkgs, ... }:

{
  test_user_workflow = pkgs.vmTest.makeTest {
    name = "arda-user-workflow";

    machine = { config, pkgs, ... }: {
      environment.systemPackages = [
        pkgs.arda-cli
        pkgs.nix
      ];
    };

    testScript = ''
      machine.succeed("arda --help")
      machine.succeed("arda config init")
      machine.succeed("arda config set theme.name dracula")
      machine.succeed("test -f ~/.config/arda/config.toml")
    '';
  };
}
```

**Decision Criteria**:

- **Use Containers When**:
  - Testing individual Nix operations
  - Speed is critical
  - Don't need full OS simulation
  - Testing library functions

- **Use VMs When**:
  - Testing complete workflows
  - Need full system integration
  - Testing user interactions
  - Testing on fresh NixOS

**Our Approach**:

- Start with containers for speed
- Use VMs for critical end-to-end workflows
- Research community tools: `nixcontainers`, `nixos-tests`

---

### Mocking Strategies

**Mock subprocess.run** (Nix Operations)

```python
from unittest.mock import patch, MagicMock

def test_nix_eval():
    """Test nix_eval function without calling real Nix"""
    mock_result = MagicMock()
    mock_result.stdout = b'{"result": "value"}'
    mock_result.returncode = 0

    with patch('subprocess.run', return_value=mock_result):
        from arda_lib.nix.nix import nix_eval
        result = nix_eval("nixpkgs#hello")

        assert result == {"result": "value"}
```

**Mock File I/O** (Configuration)

```python
from unittest.mock import patch
from pathlib import Path

def test_load_config_missing_file():
    """Test config loading when file is missing"""
    with patch('arda_cli.lib.config.get_config_path', return_value=None):
        from arda_cli.lib.config import load_config
        config = load_config()

        # Should fall back to defaults
        assert config["theme"]["name"] == "forest"
```

**Use For**:

- Fast unit tests
- Isolated component testing
- Error condition testing
- Avoiding external dependencies

---

## Initial Thoughts on Test Orchestration and Dev Ergonomics

**Status**: Preliminary Planning
**Requires**: Detailed audit of clan-core's testing infrastructure before finalization

This section captures our initial thinking about how developers will execute tests during daily workflows. The challenge is providing multiple levels of test execution while maintaining simplicity and ease of use.

### The Challenge

Developers need **multiple levels of test execution**:

1. **Fast Feedback** during development (unit tests for specific modules)
2. **Feature-Specific Testing** when working on particular systems (e.g., theme/output testing)
3. **Integration Testing** when combining components
4. **End-to-End Workflow Testing** simulating real user scenarios

These tests must be **easy to run** and **easy to remember** during active development.

### Preliminary Architecture Proposal

We are considering a **three-tier approach** to test execution:

#### Tier 1: Justfile (Developer Ergonomics)

**Purpose**: Quick commands for frequent use

```justfile
test:
    run-arda-tests unit

test-all:
    run-arda-tests all

test-themes:
    run-arda-tests themes

test-integration:
    run-arda-tests integration

test-workflow:
    run-arda-tests workflow
```

**Advantages**:

- Familiar interface
- Quick to type
- Natural for daily development
- Can be extended with new commands

**Limitations**:

- Limited categorization options
- Difficult to run test combinations
- No built-in reporting

---

#### Tier 2: pkgs/testing (Test Orchestration)

**Purpose**: Dedicated test execution infrastructure

**Hypothesis**: Based on clan-core's pattern, `pkgs/testing/` should contain:

1. **Test Runner Scripts** (executable via Nix)

   ```nix
   # pkgs/testing/run-tests.nix
   { pkgs, writeScriptBin, ... }:

   writeScriptBin "run-arda-tests" ''
     #!/bin/sh
     # Orchestrates test execution across multiple directories
     case "$1" in
       unit)
         pytest pkgs/arda-cli/arda_cli/tests/unit/
         pytest pkgs/arda-cli/arda_lib/tests/unit/
         pytest tests/unit/
         ;;
       themes)
         pytest pkgs/arda-cli/arda_cli/tests/unit/themes/
         pytest pkgs/arda-cli/arda_cli/tests/integration/themes/
         ;;
       cli)
         pytest pkgs/arda-cli/arda_cli/tests/cli/
         ;;
       nix)
         pytest pkgs/arda-cli/arda_lib/tests/nix/
         nix eval --file tests/nix/
         ;;
       integration)
         # Run all integration tests
         pytest pkgs/arda-cli/arda_cli/tests/integration/
         pytest pkgs/arda-cli/arda_lib/tests/integration/
         pytest tests/integration/
         ;;
       workflow)
         # Run container/VM tests
         nix build tests/vm/test_user_workflow.nix
         ;;
       all)
         run-arda-tests unit && \
         run-arda-tests integration && \
         run-arda-tests cli && \
         run-arda-tests nix && \
         run-arda-tests workflow
         ;;
     esac
   ''
   ```

2. **Test Reporting Infrastructure**
   - JUnit XML output for CI integration
   - HTML test reports
   - Coverage aggregation across packages
   - Failure summaries

3. **Test Helpers and Fixtures**
   - Shared test utilities
   - Test data generators
   - Common mock setups
   - Docker/VM orchestration utilities

4. **Container/VM Test Orchestration**
   - Scripts to spin up test environments
   - Test environment validation
   - Parallel test execution

**Advantages**:

- Centralized test orchestration
- Easy to categorize and run tests
- Built-in reporting and aggregation
- Can handle complex test workflows
- Reusable across development and CI

---

#### Tier 3: Direct pytest (Power Users)

**Purpose**: Fine-grained control for advanced testing

```bash
# Run specific test files
pytest pkgs/arda-cli/arda_cli/tests/unit/config/test_parses_valid_toml.py

# Run tests matching patterns
pytest pkgs/arda-cli/arda_cli/tests/ -k "theme"

# Run with coverage
pytest --cov=arda_cli pkgs/arda-cli/arda_cli/tests/

# Run in parallel
pytest -n auto pkgs/arda-cli/arda_cli/tests/
```

**Advantages**:

- Maximum flexibility
- Full pytest feature access
- Power user capabilities

---

### Proposed Developer Workflows

#### Development Scenario 1: Working on Configuration System

```bash
# Quick feedback loop
just test-unit-config

# Full validation
just test-integration

# Manual debugging
pytest pkgs/arda-cli/arda_cli/tests/unit/config/test_parses_valid_toml.py -v
```

#### Development Scenario 2: Working on Theming

```bash
# Verify theme changes
just test-themes

# Test theme + output together
just test-themes output

# Visual verification with hexdump
FORCE_COLOR=1 arda config view | hexdump -C
```

#### Development Scenario 3: Working on Nix Integration

```bash
# Test library functions
just test-nix

# Test with mocked operations
pytest pkgs/arda-cli/arda_lib/tests/unit/test_nix_eval.py

# Test with real Nix (if available)
just test-workflow-nix
```

#### Development Scenario 4: Full Validation Before Commit

```bash
# Run all fast tests
just test

# Or everything including slow tests
just test-all
```

---

### Potential Evolution: ea-cli Development Tool

**Future Consideration**: We may clone `arda-cli` to create `ea-cli` (Ergonomics/Developer Assistant CLI)

**Rationale**:

- clan-core doesn't have a dedicated developer ergonomics tool
- arda-core could benefit from a specialized developer CLI
- Could provide enhanced test orchestration
- Could include other development utilities (build automation, environment management, etc.)

**Potential Features**:

```bash
# Test orchestration
ea test run unit
ea test run themes --with-coverage
ea test run all --parallel

# Build automation
ea build arda-cli
ea build --clean

# Environment management
ea env setup
ea env validate

# Code quality
ea lint
ea format
```

**Important**: This is **not part of the initial plan**. This would be considered **after**:

1. Testing framework is fully implemented
2. Basic test suite is functional
3. clan-core's testing infrastructure is fully understood
4. arda-core's needs are better understood through actual usage

---

### What We Still Need to Research

Before finalizing this approach, we must examine:

1. **What exactly is in clan-core's `pkgs/testing/`?**
   - Structure and organization
   - Scripts and utilities
   - How tests are orchestrated

2. **How does clan-core handle test execution?**
   - Justfile usage
   - Direct Nix commands
   - Custom scripts

3. **How are tests organized in `checks/`?**
   - VM test patterns
   - Execution mechanisms
   - CI/CD integration

4. **What test reporting do they use?**
   - Coverage collection
   - Failure reporting
   - CI integration

5. **What container/VM testing approaches exist?**
   - `nixcontainers`
   - `nixos-tests`
   - Community tools

---

### Conclusion

This preliminary plan provides a framework for test orchestration that balances:

- **Simplicity**: Easy commands via justfile
- **Flexibility**: Categorized execution via `pkgs/testing`
- **Power**: Full control via direct pytest
- **Evolution**: Potential for ea-cli development tool

**Important Note**: This entire approach is **preliminary** and based on initial thinking. It cannot be finalized until we conduct a **thorough audit of clan-core's testing infrastructure** as planned in Phase 3. The actual implementation may differ significantly based on what we learn from clan-core's approach.

---

## Next Steps

This research document establishes the foundation for arda's testing framework. The following phases will refine and implement this plan:

### Phase 1: Framework Implementation (Next)

- [ ] Create multi-directory test structure (following clan-core pattern)
- [ ] Set up pytest configuration for all test directories
- [ ] Configure pytest-cov for coverage across packages
- [ ] Implement first unit tests for critical paths (config, themes, output)
- [ ] Set up CliRunner testing for CLI commands

### Phase 2: Critical Path Testing

- [ ] Write unit tests for configuration parsing
- [ ] Write unit tests for theme system (with FORCE_COLOR testing)
- [ ] Write unit tests for Nix helpers (with subprocess mocking)
- [ ] Implement integration tests for CLI workflows (CliRunner)
- [ ] Implement Nix eval tests for library functions

### Phase 3: System Testing

- [ ] Research container vs VM testing approach (based on clan-core)
- [ ] Create first container test for Nix operations
- [ ] Create first VM test for end-to-end workflows
- [ ] Verify hash baking in real environment
- [ ] Test on actual NixOS installation

### Phase 4: CI/CD Integration

- [ ] Configure GitHub Actions for multi-directory test execution
- [ ] Set up test parallelization by directory
- [ ] Implement coverage reporting across all packages
- [ ] Create test artifact retention

### Phase 5: Optimization

- [ ] Measure test execution times
- [ ] Optimize slow tests
- [ ] Implement test selection for faster CI
- [ ] Add performance benchmarks

### Immediate Action Items

1. **Create multi-directory structure**:
   - `pkgs/arda-cli/arda_cli/tests/{unit,integration,cli}/`
   - `pkgs/arda-cli/arda_lib/tests/{unit,integration,nix}/`
   - `pkgs/testing/{fixtures,helpers,containers,vm}/`
   - `tests/{unit,integration,nix}/`

2. **Write sample test files**: Demonstrate the structure with 2-3 examples

3. **Configure pytest**: Create `pytest.ini` or `pyproject.toml` configuration for all directories

4. **Research container/VM testing**: Examine clan-core's `pkgs/testing` and `checks/` in detail

5. **Set up CI pipeline**: GitHub Actions for automated test execution across multiple directories

---

## Known Things to Test For

**Audit Date**: 2025-11-26
**Audited By**: Comprehensive codebase analysis
**Total Components Identified**: 100+ individual testable items across 15+ modules

This section contains a complete inventory of all testable components discovered during the deep dive audit of arda-core's codebase. The audit focused on `pkgs/arda-cli` (the primary package) and extended to other project components including overlays, flake configuration, and development tooling.

---

### A. pkgs/arda-cli - Primary CLI Package

**Total Python Files**: 24
**Total Functions/Methods to Test**: 80+
**Total CLI Commands**: 6 with 15+ subcommands

#### A.1 Core Library Modules (`arda_cli/lib/`)

##### A.1.1 Configuration Module (`arda_cli/lib/config.py`)

**Testable Functions** (13 functions):

1. `get_active_config_path()` - Returns (Path|None, str)
2. `get_config_path()` - Finds first existing config file
3. `load_config()` - Loads config with fallback to defaults
4. `load_default_config()` - Loads package default config
5. `get_theme_from_config()` - Gets theme setting
6. `get_verbose_from_config()` - Gets verbose setting
7. `get_timestamp_from_config()` - Gets timestamp setting
8. `get_config_for_viewing()` - Merges configs in priority order
9. `get_config_for_writing()` - Gets path for writing config
10. `set_config_value()` - Sets config value in file
11. `get_valid_config_keys()` - Returns valid configuration keys
12. `_deep_merge()` - Private recursive dict merge function
13. `parse_bool()` - Parse various boolean representations

**Test Scenarios to Implement**:

- ✓ Config file priority: project > XDG > defaults
- ✓ Missing config files (graceful fallback to defaults)
- ✓ Invalid TOML syntax (error handling)
- ✓ Boolean parsing: true/false, yes/no, 1/0
- ✓ Force flags: --local, --global, --system
- ✓ Environment variable integration
- ✓ Deep merge behavior for nested configs
- ✓ Config value type conversion (string, bool, int)
- ✓ Permission errors when reading/writing
- ✓ Non-existent directories handling

**Import Dependencies to Mock**:

- `tomllib` - TOML parsing
- `pathlib.Path` - File path operations
- `os.getenv` - Environment variables
- `os.makedirs` - Directory creation

---

##### A.1.2 Theme System Module (`arda_cli/lib/theme.py`)

**Testable Functions** (5 functions):

1. `get_rich_click_themes()` - Returns list of available themes
2. `patch_rich_click()` - Patches Click with theme configuration
3. `get_current_theme()` - Returns currently active theme
4. `get_theme_color()` - Maps theme names to color values
5. Global `_GLOBAL_THEME` initialization

**Test Scenarios to Implement**:

- ✓ Theme validation (valid vs invalid names)
- ✓ Case-insensitive theme matching
- ✓ Theme color mapping for all theme families (forest, dracula, monokai, etc.)
- ✓ Rich-click integration (theme configuration)
- ✓ Environment variable handling (RICH_CLICK_THEME)
- ✓ Command-line theme parsing (--theme flag)
- ✓ Default theme fallback behavior
- ✓ Theme switching persistence

**Import Dependencies to Mock**:

- `sys.argv` - Command-line arguments
- `rich_click.rich_help_configuration` - Rich Click integration
- `arda_cli.lib.config` - Configuration loading

**Theme Color Mappings to Test**:

- forest, dracula, monokai, material, ayu, solarized-dark
- Each theme's: primary_color, secondary_color, accent_color
- Compatibility with 256-color and truecolor terminals

---

##### A.1.3 Output Management Module (`arda_cli/lib/output.py`)

**Testable Classes** (3 classes):

1. `OutputManager` - Centralized output management
2. `ExtraHelpPanelBuilder` - Help panel builder
3. `VerbosityLevel` (enum)
4. `MessageType` (enum)

**Testable Methods** (25+ methods):

**OutputManager Methods**:

- `info(), success(), warning(), error(), debug()` - Message output
- `section(), spacer(), tag(), step(), trace()` - Layout helpers
- `trace_function_entry(), trace_function_exit(), timer()` - Debugging helpers
- `align_command_comments()` - Help text alignment
- `create_extra_help_panel(), create_error_panel()` - Panel creation

**Test Scenarios to Implement**:

- ✓ Verbosity filtering (verbose_only messages)
- ✓ Timestamp formatting (enabled/disabled from config)
- ✓ Theme-aware color loading and application
- ✓ Tag formatting with square brackets
- ✓ Section separators (with/without titles)
- ✓ Timer context manager (duration calculation)
- ✓ Panel creation with theme colors
- ✓ Command-comment alignment in help text
- ✓ Message type differentiation (info, success, warning, error)
- ✓ Rich.Console integration
- ✓ Buffer flushing behavior

**Import Dependencies to Mock**:

- `rich.console.Console` - Terminal output
- `rich.panel.Panel` - Panel rendering
- `rich.text.Text` - Text formatting
- `arda_cli.lib.config` - Configuration access

---

#### A.2 CLI Commands (`arda_cli/commands/`)

**Total Commands**: 6 with 15+ subcommands

##### A.2.1 Config Commands (`commands/config/`)

**Commands to Test**:

1. `config view` - View configuration
2. `config set` - Set configuration value
3. `config init` - Initialize configuration file

**Testable Functions** (7 functions):

1. `show_config_help()` - Help panel display
2. `parse_config_value()` - Parse and validate values
3. `view_config()` - View all or specific config
4. `set_config()` - Set config value
5. `init_config()` - Initialize config file
6. `validate_config_key()` - Validate config keys
7. Main `@config.command()` Click group

**Test Scenarios to Implement**:

- ✓ View all settings (formatted output)
- ✓ View specific key (section.key format)
- ✓ View invalid key (error message)
- ✓ Set valid values (theme, verbose, timestamp)
- ✓ Set invalid values (wrong type, invalid key)
- ✓ Shorthand vs full key format (theme.name vs theme.name)
- ✓ Boolean value parsing (multiple formats)
- ✓ Init with --force flag (overwrite existing)
- ✓ Init to different locations (--local, --global, --system)
- ✓ Help display with extra panel

**Import Dependencies to Mock**:

- `click` - CLI framework
- `arda_cli.lib.config` - Config operations
- `arda_cli.lib.output` - Output formatting
- `pathlib.Path` - File operations

---

##### A.2.2 Theme Commands (`commands/theme/`)

**Commands to Test**:

1. `theme list` - List available themes
2. `theme preview` - Preview current theme

**Testable Functions** (4 functions):

1. `show_theme_help()` - Help panel
2. `list_themes()` - List all themes
3. `preview_theme()` - Preview with examples
4. Main `@theme.command()` Click groups

**Test Scenarios to Implement**:

- ✓ List all themes (formatting, accent colors)
- ✓ Theme count display in verbose mode
- ✓ Preview with current theme
- ✓ Preview with --theme flag override
- ✓ Message type examples (info, success, warning, error)
- ✓ Timestamp toggle examples
- ✓ Help text display with theme applied
- ✓ Empty theme list handling

**Import Dependencies to Mock**:

- `arda_cli.lib.theme` - Theme system
- `arda_cli.lib.output` - Output formatting
- `click` - CLI framework

---

##### A.2.3 Host Commands (`commands/host/`)

**Status**: Stub implementation
**Commands**: `host` - Host management

**Testable Functions** (2 functions):

1. Main `host` Click group
2. Placeholder handler function

**Test Scenarios to Implement**:

- ✓ Help display (consistent with other commands)
- ✓ "Coming soon" message formatting
- ✓ Verbose operations list output
- ✓ Error output consistency
- ✓ Exit code correctness

---

##### A.2.4 Role Commands (`commands/roles/`)

**Status**: Stub implementation
**Commands**: `roles` - Role management

**Testable Functions** (2 functions):

1. Main `roles` Click group
2. Placeholder handler function

**Test Scenarios to Implement**:

- ✓ Help display (consistent with other commands)
- ✓ "Coming soon" message formatting
- ✓ Verbose operations list output
- ✓ Error output consistency

---

##### A.2.5 Secret Commands (`commands/secrets/`)

**Status**: Stub implementation
**Commands**: `secrets` - Secret management

**Testable Functions** (2 functions):

1. Main `secrets` Click group
2. Placeholder handler function

**Test Scenarios to Implement**:

- ✓ Help display
- ✓ "Coming soon" message formatting
- ✓ Integration with sops-nix (when implemented)

---

##### A.2.6 Template Commands (`commands/templates/`)

**Status**: Stub implementation
**Commands**: `templates` - Template management

**Testable Functions** (2 functions):

1. Main `templates` Click group
2. Placeholder handler function

**Test Scenarios to Implement**:

- ✓ Help display
- ✓ "Coming soon" message formatting
- ✓ Template listing (when implemented)

---

##### A.2.7 Main Entry Point (`main.py`)

**Testable Functions** (6 functions):

1. `ensure_config_exists()` - Auto-create config if missing
2. `show_active_config()` - Display active config path
3. `validate_theme()` - Validate theme before proceeding
4. `show_help_with_config()` - Show help with config info
5. `show_welcome()` - Display welcome message
6. Main `main()` Click group

**Test Scenarios to Implement**:

- ✓ Config auto-creation in current directory
- ✓ Theme validation (valid/invalid themes)
- ✓ Help display with active configuration
- ✓ Context object population (theme, verbose, timestamp)
- ✓ Command registration (all subcommands present)
- ✓ Version flag handling
- ✓ Welcome message display
- ✓ Error handling and exit codes

**Import Dependencies to Mock**:

- `click` - CLI framework
- `arda_cli.lib.config` - Config operations
- `arda_cli.lib.theme` - Theme validation
- `arda_cli.lib.output` - Output formatting

---

#### A.3 Nix Integration Library (`arda_lib/`)

**Total Modules**: 2
**Total Classes**: 3 (Flake, Packages, plus exceptions)
**Total Functions**: 8 Nix command wrappers

##### A.3.1 Nix Operations Module (`arda_lib/nix/nix.py`)

**Testable Functions** (8 functions):

1. `nix_command()` - Builds nix command with options
2. `nix_eval()` - Evaluates Nix expression
3. `nix_build()` - Builds derivation
4. `nix_shell()` - Runs command in Nix shell
5. `nix_metadata()` - Gets flake metadata
6. `nix_config()` - Gets Nix configuration
7. `nix_store()` - Queries Nix store
8. `select.select()` - nix-select attribute selection

**Testable Classes** (5 classes):

1. `NixError` (exception) - Base Nix operation error
2. `FlakeError` (exception) - Flake-specific error
3. `BuildError` (exception) - Build-specific error
4. `Flake` - Flake introspection and operations
   - `__init__()` - Initialize flake
   - `get_metadata()` - Get cached metadata
   - `eval()` - Evaluate flake attribute
   - `select()` - Use nix-select for selection
   - `build()` - Build flake attribute
5. `Packages` - Package allowlist management
   - `is_allowed()` - Check if package allowed
   - `assert_allowed()` - Assert package allowed
   - `shell()` - Run shell with allowed packages

**Test Scenarios to Implement**:

- ✓ Command construction (adds --experimental-features)
- ✓ JSON parsing of Nix output
- ✓ Flake path handling and validation
- ✓ nix-select integration (import and usage)
- ✓ Package allowlist validation (substring matching)
- ✓ Default allowed packages list
- ✓ Error propagation (subprocess → NixError)
- ✓ JSON parsing errors handling
- ✓ Invalid flake references
- ✓ Timeout handling
- ✓ Cached metadata operations

**Import Dependencies to Mock**:

- `subprocess.run` - **Critical**: All Nix commands
- `select.select` - nix-select integration
- `json` - JSON parsing
- `pathlib.Path` - Path operations

**Critical Test Areas**:

- Hash baking verification (`NIX_SELECT_HASH` substitution)
- Error handling for all Nix operations
- Flake reference construction
- Package allowlist security model

---

### B. Project Infrastructure (Non-Python)

#### B.1 Flake Configuration (`flake.nix`)

**Testable Elements**:

1. **Input Validation**
   - ✓ All required inputs are present
   - ✓ Input URLs are valid
   - ✓ Pin versions are correct (rich-click 1.9.4, nix-select hash)

2. **Flake Structure**
   - ✓ Outputs function is correct
   - ✓ Systems import is valid
   - ✓ flake-parts integration works

3. **Overlay Integration**
   - ✓ customOverlay is properly constructed
   - ✓ Overlay is applied to nixpkgs correctly

**Test Approach**: `nix flake check`

---

#### B.2 DevShell Configuration (`devShell.nix`)

**Testable Elements**:

1. **Package Availability**
   - ✓ All listed packages are available in nixpkgs
   - ✓ Python 3.13 with all dependencies
   - ✓ Development tools (pytest, ruff, mypy, etc.)

2. **Shell Configuration**
   - ✓ Shell name is "arda"
   - ✓ All packages are included
   - ✓ Environment is properly configured

**Test Approach**: `nix develop` and verify environment

---

#### B.3 Formatter Configuration (`formatter.nix`)

**Testable Elements**:

1. **Treefmt Setup**
   - ✓ nixfmt is enabled
   - ✓ ruff is enabled
   - ✓ shellcheck is enabled
   - ✓ Exclude patterns are correct

2. **File Coverage**
   - ✓ All Python files are covered by ruff
   - ✓ All Nix files are covered by nixfmt
   - ✓ All shell files are covered by shellcheck

**Test Approach**: `nix fmt --dry-run`

---

#### B.4 Package Overlays (`overlays/`)

##### B.4.1 Python 3 Overlay (`overlays/python3/`)

**Testable Elements**:

1. **rich-click.nix**
   - ✓ Version override to 1.9.4
   - ✓ Source from inputs is correct
   - ✓ Override attributes are applied

2. **default.nix**
   - ✓ Imports all overlays correctly
   - ✓ Merges overlays using self: super pattern

**Test Approach**: Build Python packages in devShell and verify versions

---

##### B.4.2 Root Overlay (`overlays/default.nix`)

**Testable Elements**:

- ✓ Python 3 overlay is applied
- ✓ Final package set is correct

**Test Approach**: Build packages and verify rich-click version

---

#### B.5 Build System (`pkgs/`)

##### B.5.1 Flake Module (`pkgs/flake-module.nix`)

**Testable Elements**:

- ✓ arda-cli package is exported
- ✓ Correct inputs passed (nix-select, jq, runCommand)
- ✓ Package uses overlaid python313Packages

**Test Approach**: `nix build .#arda-cli`

---

##### B.5.2 Package Definition (`pkgs/arda-cli/default.nix`)

**Testable Elements** (covered in A.3):

- ✓ ardaSource function
- ✓ Hash baking logic
- ✓ Symlink creation
- ✓ Python package building

**Test Approach**: Full package build and verification

---

#### B.6 Build Automation (`justfile`)

**Testable Commands**:

1. `build-arda-cli` - Build arda-cli
2. `build-ea-cli` - Build ea-cli (future)
3. `build-all` - Build all CLIs
4. `clean` - Clean results
5. `help` - Show help

**Test Scenarios**:

- ✓ All commands execute successfully
- ✓ Result symlinks are created correctly
- ✓ Clean removes all symlinks
- ✓ Help output is correct

**Test Approach**: Manual testing or script automation

---

### C. Testing Strategy Summary

#### C.1 Priority Levels

### Priority 1 (Critical - Implement First)

- Configuration handling: 13 functions in `config.py`
- Theme system: 5 functions in `theme.py`
- Output formatting: 25+ methods in `output.py`
- Main entry point: 6 functions in `main.py`

### Priority 2 (High)

- Config commands: 7 functions in `commands/config/`
- Theme commands: 4 functions in `commands/theme/`
- Nix operations: 8 functions + 5 classes in `arda_lib/nix/`

### Priority 3 (Medium)

- Placeholder commands: 8 functions across 4 stub modules
- Flake configuration validation
- DevShell configuration

### Priority 4 (Low)

- Justfile automation
- Formatter configuration
- Overlay structure

#### C.2 Test Coverage Goals

| Module | Target Coverage | Rationale |
|--------|----------------|-----------|
| `arda_cli/lib/config.py` | 95%+ | Critical infrastructure |
| `arda_cli/lib/theme.py` | 90%+ | User-facing feature |
| `arda_cli/lib/output.py` | 85%+ | Complex formatting |
| `arda_cli/main.py` | 85%+ | Entry point |
| `arda_lib/nix/nix.py` | 80%+ | External integration |
| `commands/` modules | 75%+ | End-to-end workflows |
| Placeholder modules | 50%+ | Basic consistency |

#### C.3 Testing Tools Required

### Core Testing Framework

- `pytest` - Test runner
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking
- `click.testing` - CLI testing

### Specialized Tools

- `freezegun` - Time-based tests
- `pyfakefs` - Filesystem mocking
- `hypothesis` - Property-based testing

### Nix Testing

- `nix flake check` - Flake validation
- `nix eval` - Library evaluation
- `nix build` - Package building
- `nix vmTest` - VM testing

#### C.4 Test Data Requirements

### Configuration Test Fixtures

- Valid TOML files (various themes)
- Invalid TOML files (syntax errors)
- Missing config files
- Permission-denied scenarios

### Theme Test Fixtures

- All theme color mappings
- Valid/invalid theme names
- Rich theme configurations

### Nix Test Fixtures

- Valid flake references
- Invalid flake references
- Sample Nix expressions
- nix-select selectors

---

### D. Dependencies and Integration Points

#### D.1 External Dependencies

### Python Packages

```
click              # CLI framework - Mock in tests
rich_click         # Rich-themed Click - Mock/theme testing
rich               # Terminal formatting - Mock output
pyyaml             # YAML parsing - Mock/config testing
pydantic           # Data validation - Mock/validation testing
tomli-w            # TOML writing - File I/O testing
subprocess         # Process execution - Mock heavily
```

### Nix Packages

```
nix                # Package manager - Mock or real in integration tests
jq                 # JSON processing - Used in hash baking
nix-select         # Attribute selection - Mock import or real
```

#### D.2 Internal Dependencies

### Module Interaction Map

```
main.py
  ├── commands/* (all)
  ├── lib/config.py
  ├── lib/theme.py
  └── lib/output.py

lib/output.py
  └── lib/config.py (read-only)

lib/theme.py
  └── lib/config.py (read-only)

arda_lib/nix/nix.py
  └── (standalone - no arda_cli dependencies)
```

**Integration Test Requirements**:

- Test module interactions (main → lib, lib → lib)
- Test command workflows (config view → config.py)
- Test theme application (theme list → theme.py)
- Test Nix operations (arda_lib isolation)

---

### E. Future Considerations

#### E.1 Expanded Functionality

**Pending Features** (from stub commands)

- Host management system
- Role-based access control
- Secret management integration (sops-nix)
- Template system

**Testing Implications**:

- Each feature will add 10-20 new test functions
- VM tests required for system-level features
- Integration tests for inter-feature communication

#### E.2 Additional CLI Tools

**Future Package**: `ea-cli` (mentioned in justfile)

- Will require separate test suite
- May share some components with arda-cli
- Test structure can be replicated

#### E.3 Cross-Platform Testing

**Platform Coverage**:

- Linux (primary)
- macOS (if supported)
- Different terminal emulators (color handling)

**Testing Implications**:

- Theme rendering tests on multiple platforms
- Path handling tests (POSIX vs Windows)
- Terminal capability detection tests

---

### End of Known Things to Test For

This inventory represents the complete testing surface of arda-core as of 2025-11-26. It should be updated as new features are added and existing code is modified.

---

## Conclusion

This testing framework represents a **balanced hybrid approach** that combines:

- **Clan-Core's proven patterns**: Build-time testing, VM validation, direct function calls, Nix integration
- **Arda-Core's customizations**: Custom namespace discovery, one-test-per-file modularity, four-level execution hierarchy
- **Rapid feedback** through fast unit tests in build
- **Realistic validation** through integration and VM tests
- **Comprehensive coverage** across all critical systems

### Our Design Achievement

After conducting a detailed audit of clan-core's testing infrastructure, we have successfully designed a framework that:

✅ **Adopts what works**: Build-time execution (like clan-core)
✅ **Enhances discoverability**: Custom `arda` namespace (our innovation)
✅ **Improves maintainability**: One-test-per-file (our enhancement)
✅ **Provides ergonomics**: Four-level execution hierarchy (our solution)
✅ **Ensures quality**: Fast tests automatic, slow tests optional (our balance)

### Ready for Implementation

This document now contains a **complete, finalized design** that is ready to be implemented. The hybrid approach ensures:

1. **Quality is automatic** - Fast tests run with every build
2. **Tests are discoverable** - Full visibility via `nix flake show`
3. **Execution is flexible** - Four levels for different needs
4. **Maintenance is easy** - Modular, atomic test files
5. **Development is productive** - Fast feedback + comprehensive validation

The modular structure ensures that tests remain maintainable as the project grows, while the multi-layer approach provides both quick feedback for developers and thorough validation before releases.

---

**Document Version**: 2.1
**Last Updated**: 2025-11-27
**Status**: ✅ Finalized Design - Ready for Implementation

**Revision History**:

- v1.0 (2025-11-26): Initial planning phase
- v1.3 (2025-11-27): Added test orchestration and dev ergonomics
- v2.0 (2025-11-27): **Complete hybrid design** combining clan-core patterns with arda-core customizations based on clan-core audit findings
- v2.1 (2025-11-27): **Critical clarification** - Enforced component context requirement in all test namespaces

**Key Additions in v2.1**:

- **Component context requirement**: All test namespaces MUST include component (arda-cli, arda-lib, etc.)
- Updated all examples to use: `arda.tests.arda-cli.themes.unit` instead of `arda.tests.themes.unit`
- Added "Why Component Context is Critical" explanation with before/after examples
- Future-proofing note for when new components are added

**Critical Change in v2.1**:

- **Before**: `nix build .#arda.tests.themes.unit` ❌ (ambiguous)
- **After**: `nix build .#arda.tests.arda-cli.themes.unit` ✅ (clear component context)
- This ensures no ambiguity as the project grows with more components

**Next Phase**: Implementation Planning - Ready to proceed with creating test infrastructure and initial test suite
