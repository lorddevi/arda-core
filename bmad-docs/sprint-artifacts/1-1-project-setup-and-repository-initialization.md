# Story 1.1: Project Setup and Repository Initialization

Status: review

## Story

As a developer,
I want to initialize the Arda project repository with proper structure and tooling,
So that I can begin building features in an organized, reproducible environment.

## Acceptance Criteria

1. [x] Repository contains proper directory structure (pkgs/arda-cli/, modules/nixos/, templates/, hosts/, lib/)
2. [x] GitHub repository is created with initial commit at <https://github.com/lorddevi/arda-core>
3. [x] Git hooks and pre-commit checks are configured for secrets detection and code formatting
4. [x] Development documentation explains the project structure and branch strategy

## Tasks / Subtasks

- [x] Task 1 (AC: 1)
  - [x] Create repository structure: pkgs/arda-cli/, modules/nixos/, templates/, hosts/, lib/
  - [x] Initialize with .gitignore for Nix projects and secrets
- [x] Task 2 (AC: 2)
  - [x] Create GitHub repository: <https://github.com/lorddevi/arda-core>
  - [x] Push initial commit with repository structure
- [x] Task 3 (AC: 3)
  - [x] Configure pre-commit hooks for secret detection
  - [x] Configure code formatting hooks (black, flake8)
- [x] Task 4 (AC: 4)
  - [x] Create README.md with project overview
  - [x] Create CONTRIBUTING.md with branch strategy documentation

## Dev Notes

### Architecture Patterns and Constraints

**Repository Structure Alignment:**
The repository structure follows the Arda architecture document specifications:

- `pkgs/arda-cli/` - CLI tool implementation (source: bmad-docs/architecture.md#Project-Structure)
- `modules/nixos/` - NixOS modules organized as Services/Features/Roles hierarchy
- `templates/` - Template system for disk layouts and configurations
- `hosts/` - Host configurations with auto-discovery support
- `lib/` - Arda core library and utilities

**Branch Strategy:**

- `main` (arda-v1) - Primary development branch per architecture
- `clan-core` - Reference branch for code extraction
- `feature/*`, `bugfix/*`, `experiment/*` - Standard branching model

**Repository Setup Requirements:**

- Private repository with controlled access per NFR security requirements
- .gitignore patterns for age keys and .sops.yaml files per secret management strategy
- Pre-commit hooks for secret detection (critical for Epic 6: Secret Management)

### Project Structure Notes

- Alignment with unified project structure from architecture.md
- Clear separation of concerns at each directory level
- Supports the Service/Feature/Role hierarchy (modules/nixos/profiles/services/, features/, roles/)
- Minimal subset extraction from clan-core (Epic 1 foundation approach)

### References

- [Source: bmad-docs/PRD.md#Installation--Setup-Success]
- [Source: bmad-docs/architecture.md#Project-Structure]
- [Source: bmad-docs/architecture.md#ADR-006-Package-Structure]
- [Source: bmad-docs/epics.md#Story-1.1-Project-Setup-and-Repository-Initialization]

## Dev Agent Record

### Context Reference

- bmad-docs/sprint-artifacts/1-1-project-setup-and-repository-initialization.context.xml

### Agent Model Used

minimax-m2

### Debug Log References

### Completion Notes List

**Implementation Summary (2025-11-14):**

✅ **Task 1: Repository Structure** - Created complete directory hierarchy following Service/Feature/Role architecture from bmad-docs/architecture.md. Includes pkgs/arda-cli/, modules/nixos/{profiles/{services,features,common},roles,lib}, templates/, hosts/, and lib/ directories. Added comprehensive .gitignore protecting Nix artifacts, secrets, Python builds, and editor configs.

✅ **Task 2: GitHub Repository** - Repository at <https://github.com/lorddevi/arda-core> initialized with arda-v1 branch. Committed and pushed repository structure, context files, and documentation. Branch strategy follows arda-v1 (main), clan-core (reference), feature/*, bugfix/*, experiment/* model.

✅ **Task 3: Pre-commit Hooks** - Configured comprehensive pre-commit suite including detect-secrets (critical for Epic 6 secret management), black (Python formatting), flake8 (Python linting), nixpkgs-fmt (Nix formatting), and markdownlint. Hooks tested and passing. Created .secrets.baseline for secret scanning baseline.

✅ **Task 4: Development Documentation** - Created comprehensive README.md with project overview, architecture innovation, repository structure, quick start guide, and branch strategy documentation. Created detailed CONTRIBUTING.md with development workflow, conventional commits, PR process, code style guidelines, testing requirements, and security practices. Configured markdownlint with appropriate rules (line length relaxed for readability).

**Key Achievements:** All 4 acceptance criteria fully satisfied. Repository structure aligns with Service/Feature/Role hierarchy specification. Pre-commit hooks provide security and quality gates. Documentation enables contributor onboarding and establishes development standards. Repository ready for feature development in Epic 1.

**Files Changed:** 20+ files created including directory structure, configuration files, and documentation. All changes committed with conventional commit messages and reviewed by pre-commit hooks.

### File List

**Created:**

- `.gitignore` - Git ignore patterns for Nix projects and secrets
- `README.md` - Project overview, quick start, and documentation index
- `CONTRIBUTING.md` - Development guidelines, branch strategy, and contribution process
- `.pre-commit-config.yaml` - Pre-commit hooks configuration (secret detection, code formatting)
- `.secrets.baseline` - Baseline file for detect-secrets
- `.markdownlint.json` - Markdown linting configuration
- `pkgs/arda-cli/` - CLI tool directory structure
- `modules/nixos/profiles/` - NixOS modules hierarchy (services, features, common)
- `modules/nixos/roles/` - Role composition directory
- `modules/nixos/lib/` - Nix utility functions directory
- `templates/` - Template system directory
- `hosts/` - Host configuration directory
- `lib/` - Arda core library directory
- `.venv/` - Python virtual environment for development tooling

**Modified:**

- No existing files modified in this story

## Change Log

- 2025-11-14: Repository initialization complete - All ACs satisfied (Story: 1-1)

- 2025-11-14: Initial story creation
