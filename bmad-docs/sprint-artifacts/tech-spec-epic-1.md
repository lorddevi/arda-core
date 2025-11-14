# Epic Technical Specification: Foundation & Development Environment

Date: 2025-11-14
Author: Lord
Epic ID: epic-1
Status: Draft

---

## Overview

Epic 1 establishes the essential development infrastructure for the Arda project, a minimal, sustainable infrastructure management tool for NixOS that introduces a Service/Feature/Role hierarchy as its core differentiator. This epic creates the foundation for rapid, testable development of the CLI automation framework that will enable users to manage NixOS infrastructure without manual configuration complexity.

The development environment setup enables the extraction of proven code from clan-core while building the innovative Service/Feature/Role architecture from day one. This foundation supports the project's aggressive days/weeks MVP timeline while ensuring decade-scale maintainability through proper tooling, documentation, and reproducibility.

The epic addresses the critical need for a standardized development environment that allows parallel development of infrastructure components (CLI, Nix modules, templates) with proper testing, version control, and documentation from the start.

## Objectives and Scope

### In Scope

- Project repository initialization with GitHub integration
- Nix development shell configuration with all required tools
- Branch management workflow for arda-v1 development
- Flake configuration with dependency pinning and lock management
- Testing framework setup for validation of all components
- Documentation structure for development guidelines
- CI/CD pipeline basics for build validation

### Out of Scope

- Actual implementation of Arda features (handled in epics 2-10)
- User-facing installation workflow (Epic 2)
- Machine deployment capabilities (Epic 3)
- Service/Feature/Role module implementation (Epic 4)
- Secret management infrastructure (Epic 6)

## System Architecture Alignment

This epic aligns with the foundational architecture decisions established in the architecture document:

**Foundation Extraction Strategy:** Following the decision to "Extract minimal subset from clan-core," this epic creates the development infrastructure necessary to safely extract and adapt proven code (machines, secrets, templates, vars, state modules) while building new capabilities.

**Project Structure Implementation:** The repository structure defined in the architecture (pkgs/arda-cli/, modules/nixos/, templates/, hosts/, lib/arda.nix) is established in this epic, providing the scaffolding for all subsequent development.

**Technology Stack Enablement:** The epic implements the core technology decisions: NixOS/Nix flakes for configuration management, Python 3.13 for CLI implementation, and proper flake input pinning for reproducible builds.

**CLI-First Automation Support:** While the actual CLI commands are not implemented in this epic, the development environment sets up the foundation for the command structure (commands/host.py, commands/roles.py, commands/services.py, etc.) defined in the architecture.

## Detailed Design

### Services and Modules

The foundation implementation consists of the following primary components:

| Component | Responsibility | Inputs | Outputs | Owner |
| --------- | -------------- | ------ | ------- | ----- |
| **Repository Structure** | Establishes standardized project layout per architecture | Initial project requirements | Directory structure, initial files | Development team |
| **Development Shell** | Provides `nix develop` environment with all tools | flake.nix, shell.nix | Python 3.13, arda-cli (dev), testing tools | Dev team |
| **Branch Management** | Enforces git workflow conventions | Git repository | Branch strategy, merge policies | Dev team |
| **Flake Management** | Ensures reproducible builds and updates | External flake inputs | Locked dependencies, build reproducibility | Dev team |
| **Testing Framework** | Validates component functionality | Test specifications | Test execution, coverage reports | Dev team |

### Data Models and Contracts

**Project Configuration Model:**

```nix
# flake.nix structure
{
  description = "Arda - Minimal NixOS infrastructure management";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/<version>";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        # Development shell
        devShells.default = pkgs.callPackage ./shell.nix { };

        # Packages
        packages.arda-cli = pkgs.callPackage ./pkgs/arda-cli { };

        # NixOS modules
        nixosModules.arda-core = import ./modules/nixos;
      }
    );
}
```

**Testing Configuration Model:**

```python
# pytest configuration (pyproject.toml)
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=pkgs/arda-cli --cov-report=term-missing --cov-report=html"
```

### APIs and Interfaces

**Development Shell Interface:**

The `nix develop` command provides access to:

- Python 3.13+ runtime with pip
- arda-cli in editable mode (symlinked to working directory)
- Development tools: git, gh, pytest, black, flake8
- Nix tools: nix, nix-build, nix-shell
- Testing utilities: coverage, tox

**Git Workflow Interface:**

Branches follow standard conventions:

- `main` (arda-v1): Primary development branch
- `clan-core`: Reference branch for code extraction
- `feature/*`: Feature development branches
- `bugfix/*`: Bug fix branches
- `experiment/*`: Experimental branches

**Flake Update Interface:**

Standard `nix flake update` command with:

- Automated lock file updates
- Dependency version tracking
- Rollback capability via git

### Workflows and Sequencing

**Repository Initialization Workflow:**

1. Create GitHub repository (lorddevi/arda-core)
2. Initialize with .gitignore for Nix projects and secrets
3. Set up branch protection for main
4. Add initial commit with README.md
5. Document branch strategy in CONTRIBUTING.md

**Development Shell Activation:**

1. Developer runs `nix develop` in project root
2. Shell activates with all required tools in PATH
3. arda-cli command available in development mode
4. Python environment configured with all dependencies

**Branch Management Workflow:**

1. Create feature branch from main
2. Develop and test features
3. Create pull request to main
4. Code review and merge
5. Delete feature branch

**Flake Update Workflow:**

1. Review current dependencies
2. Run `nix flake update`
3. Resolve any conflicts
4. Test build in development shell
5. Commit updated lock file

## Non-Functional Requirements

### Performance

- **Development Environment Activation:** `nix develop` shell should activate in <30 seconds on initial load
- **Build Performance:** Flake builds should complete within 5 minutes for full project
- **Test Execution:** Full test suite should run in <2 minutes
- **IDE Integration:** Shell should provide LSP support for Python development

### Security

- **GitHub Repository:** Private repository with controlled access
- **Git Hooks:** Pre-commit hooks for secret detection (no secrets in code)
- **Dependency Pinning:** All dependencies pinned via flake.lock for reproducibility
- **File Permissions:** Sensitive files (age keys, .sops.yaml) protected with proper permissions

### Reliability/Availability

- **Reproducible Builds:** Flake ensures same inputs produce same outputs
- **Rollback Capability:** All dependency updates can be reverted via git
- **Branch Protection:** Main branch requires PR reviews before merging
- **Test Coverage:** Critical paths must have automated tests

### Observability

- **Test Reports:** Generate coverage reports for all test runs
- **Build Logs:** CI/CD pipeline captures and reports build status
- **Dependency Tracking:** flake.lock provides clear dependency version history
- **Error Reporting:** Development shell provides clear error messages

## Dependencies and Integrations

| Dependency | Version | Constraint | Purpose |
| ---------- | ------- | ---------- | ------- |
| **NixOS/nixpkgs** | 24.11 (or latest stable) | Pinned in flake | Base Nix packages and libraries |
| **numtide/flake-utils** | Latest | ^1.0.0 | Multi-system flake support |
| **Python** | 3.13+ | ^3.13.0 | CLI implementation language |
| **pytest** | Latest | ^7.0.0 | Testing framework |
| **pytest-cov** | Latest | ^4.0.0 | Coverage reporting |
| **black** | Latest | ^23.0.0 | Code formatting |
| **flake8** | Latest | ^6.0.0 | Linting |
| **GitHub CLI** | Latest | ^2.0.0 | Repository management |
| **direnv** | Latest | ^2.0.0 | Development environment automation |

**Integration Points:**

- **Clan-core:** Reference branch for code extraction patterns
- **GitHub:** Repository hosting, PR workflows, branch protection
- **Nix Ecosystem:** Standard flake integration compatible with existing workflows

## Acceptance Criteria (Authoritative)

1. Repository initialized at <https://github.com/lorddevi/arda-core> with proper .gitignore
2. Branch strategy documented: main (arda-v1), clan-core (reference), feature/* branches
3. `nix develop` provides Python 3.13+, arda-cli (editable), pytest, black, flake8
4. flake.nix configured with pinned nixpkgs and flake-utils inputs
5. `nix flake update` completes without conflicts and maintains buildability
6. Testing framework runs: `pytest` executes successfully with coverage reporting
7. Git hooks configured: pre-commit checks for secrets and code formatting
8. Development documentation in README.md explains setup and workflow
9. CI/CD pipeline validates builds on every PR to main branch
10. Shell prompt clearly indicates development environment status

## Traceability Mapping

| AC | Spec Section | Component/API | Test Strategy |
| --- | ------------ | ------------- | ------------- |
| 1 | Detailed Design > Services | Repository Structure | Unit test: directory structure validation |
| 2 | Detailed Design > Workflows | Branch Management | Integration test: branch creation and PR workflow |
| 3 | NFR > Performance, APIs | Development Shell Interface | Performance test: shell activation time |
| 4 | Dependencies | flake.nix model | Unit test: flake validation and build |
| 5 | NFR > Reliability | Flake Update Interface | Integration test: update and rollback workflow |
| 6 | APIs, NFR > Observability | Testing Framework | Integration test: pytest execution and coverage |
| 7 | System Architecture | Git hooks | Unit test: pre-commit hook validation |
| 8 | Detailed Design > Workflows | Documentation | Review: documentation completeness |
| 9 | Observability | CI/CD pipeline | Integration test: build validation on PR |
| 10 | NFR > Performance | Shell configuration | Manual verification: prompt display |

## Risks, Assumptions, Open Questions

**Risks:**

1. **Risk:** Dependency conflicts during flake updates
   **Mitigation:** Comprehensive testing after each update, rollback capability via git

2. **Risk:** Development environment complexity detracting from productivity
   **Mitigation:** Clear documentation, examples, and simplified defaults

3. **Risk:** Clan-core extraction patterns don't transfer cleanly
   **Mitigation:** Reference branch for comparison, incremental extraction approach

4. **Risk:** Nix learning curve slowing foundation development
   **Mitigation:** Focus on proven patterns from clan-core, extensive documentation

**Assumptions:**

1. Team has NixOS development environment available
2. GitHub access permissions configured for repository creation
3. No existing code to migrate (greenfield development)
4. Development will happen primarily on NixOS or Nix-enabled systems

**Open Questions:**

1. Should development shell be optimized for specific IDEs (VS Code, Neovim)?
2. How often should flake dependencies be updated during development?
3. What level of test coverage is required before merging to main?
4. Should clang-format or other language-specific formatters be added?

## Test Strategy Summary

**Test Levels:**

1. **Unit Tests:** Validate individual components (directory creation, file generation)
2. **Integration Tests:** Verify workflows (flake update, test execution, branch management)
3. **System Tests:** End-to-end validation (nix develop → build → test → deploy)

**Testing Frameworks:**

- **Python:** pytest for CLI testing, pytest-cov for coverage
- **Nix:** nix flake check for validation, nixos-rebuild build-only for module validation
- **Git:** Pre-commit hooks for secret detection and code quality

**Coverage Strategy:**

- Minimum 80% test coverage for arda-cli code
- Integration tests for all documented workflows
- Test coverage reports generated and reviewed on each PR

**Edge Cases to Test:**

- Flake update with transient failures
- Development shell activation in CI environment
- Concurrent branch development and merges
- Dependency version conflicts and resolution
- Network failures during GitHub operations

**Test Execution Plan:**

1. **Local Development:** Run `pytest` on code changes
2. **Pre-commit:** Validate formatting, secrets, flake check
3. **CI/CD:** Full test suite on every PR
4. **Manual Testing:** Documentation workflow validation
