# Arda-Core Project Overview

## Purpose

Arda is a minimal infrastructure management system for NixOS. It provides CLI tools (`arda-cli`) for orchestrating NixOS configurations, managing hosts, and handling flake-based deployments.

## Tech Stack

- **Language**: Python 3.11+
- **CLI Framework**: Click + rich-click (themed CLI output)
- **Configuration**: Pydantic for validation, YAML/TOML for config files
- **Build System**: Nix flakes with setuptools
- **Testing**: pytest with markers, NixOS VM tests
- **Linting**: ruff, mypy (strict), bandit
- **Issue Tracking**: bd (beads) - dependency-aware JSONL-based tracker

## Project Structure

```
arda-core/
├── pkgs/
│   └── arda-cli/           # Main CLI package
│       ├── arda_cli/       # Python source
│       │   ├── commands/   # CLI command groups
│       │   ├── lib/        # Library utilities
│       │   ├── testing/    # Test utilities
│       │   └── tests/      # Test suites
│       └── pyproject.toml  # Python package config
├── modules/                # NixOS modules
├── hosts/                  # Host configurations
├── templates/              # Project templates
├── checks/                 # Nix flake checks
├── tests/                  # Nix-level tests
├── .beads/                 # Issue tracking database
├── flake.nix              # Nix flake definition
└── justfile               # Build automation
```

## Key Entry Points

- CLI: `arda` command (entry point: `arda_cli.main:main`)
- Build: `just build-arda-cli` → `./results/arda-cli`
