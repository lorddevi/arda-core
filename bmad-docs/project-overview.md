# Clan Core Project Overview

## Project Name and Purpose

**Clan Core** - The foundational repository for the [clan.lol](https://clan.lol/) project, an open-source initiative aimed at restoring fun, freedom, and functionality to computing through NixOS-based system management.

## Executive Summary

Clan Core is a comprehensive monorepo that serves as the foundation for a revolutionary operating system and tooling ecosystem. The project leverages Nix's reliability to provide full-stack system deployment, overlay networks, VM integration, robust backup management, and intuitive secret management - putting the power back into users' hands.

## Tech Stack Summary

### Part 1: Infrastructure (infra)

- **Type:** Infrastructure-as-Code
- **Technology:** NixOS + Nix Flakes
- **Key Components:**
  - NixOS modules (nixosModules/clanCore/)
  - Flake-based packaging (flake.nix)
  - Infrastructure orchestration
  - System configuration management

### Part 2: Clan App (desktop)

- **Type:** Desktop Application
- **Technology:**
  - Backend: Python 3.13
  - Frontend: SolidJS + TypeScript + Vite
  - Architecture: Webview-based desktop application
- **Purpose:** User interface for Clan system management

### Part 3: Clan CLI (cli)

- **Type:** Command-Line Interface
- **Technology:**
  - Language: Python 3.13
  - Build System: Setuptools
  - Testing: Pytest with mypy type checking
- **Purpose:** Primary CLI tool for managing Clan systems

### Part 4: VM Manager (cli)

- **Type:** Command-Line Interface (VM Management)
- **Technology:**
  - Language: Python 3.13
  - Build System: Setuptools
  - Purpose: Virtual machine lifecycle management

## Architecture Type Classification

**Monorepo** - Single repository containing multiple distinct components with shared dependencies and coordinated releases.

## Repository Structure

```
clan-core/
├── .github/workflows/          # CI/CD pipelines
├── bmad/                      # BMAD development framework
├── checks/                    # System check modules
├── clanModules/               # Clan-specific NixOS modules
├── clanServices/              # Service definitions (20+ services)
│   ├── admin/
│   ├── borgbackup/
│   ├── certificates/
│   ├── coredns/
│   ├── garage/
│   ├── matrix-synapse/
│   ├── monitoring/
│   ├── wireguard/
│   └── ... (and more)
├── docs/                      # Documentation site (mkdocs)
├── flake.nix                  # Main flake configuration
├── lib/                       # Shared library code
├── machines/                  # Machine configurations
├── modules/                   # NixOS modules
├── nixosModules/              # Additional NixOS modules
└── pkgs/                      # Packaged applications
    ├── clan-app/              # Desktop application
    ├── clan-cli/              # CLI tool
    └── clan-vm-manager/       # VM management
```

## Quick Reference

- **Primary Language:** Nix, Python 3.13, TypeScript
- **Entry Point:**
  - Infrastructure: `flake.nix`
  - CLI: `clan` command
  - Desktop App: `clan-app` binary
- **Architecture Pattern:** Modular infrastructure with service-oriented architecture
- **Build System:** Nix flakes + Python setuptools
- **CI/CD:** GitHub Actions

## Links to Detailed Documentation

### Generated Documentation

- [Architecture - Infrastructure](./architecture-infrastructure.md)
- [Architecture - Clan App](./architecture-clan-app.md)
- [Architecture - Clan CLI](./architecture-clan-cli.md)
- [Architecture - VM Manager](./architecture-clan-vm-manager.md)
- [Source Tree Analysis](./source-tree-analysis.md)
- [Component Inventory](./component-inventory.md)
- [Development Guide](./development-guide.md)
- [Integration Architecture](./integration-architecture.md)

### Existing Documentation

- [Project README](../README.md) - Main project documentation
- [Contributing Guide](../docs/CONTRIBUTING.md) - Contribution guidelines
- [Main Documentation Site](../docs/) - Complete mkdocs site
- [Clan CLI Docs](../pkgs/clan-cli/README.md) - CLI documentation
- [Clan App Docs](../pkgs/clan-app/README.md) - Desktop app documentation

## Getting Started

### Prerequisites

- Nix package manager
- Python 3.13+ (for CLI and desktop app development)
- Node.js + npm (for UI components)

### Development Setup

```bash
# Clone the repository
git clone https://git.clan.lol/clan/clan-core.git
cd clan-core

# Enter development shell (includes all dependencies)
nix develop

# Build the CLI
nix build .#clan-cli

# Run tests
nix flake check
```

### Building Components

```bash
# Build infrastructure
nix build .

# Build CLI tool
nix build .#clan-cli

# Build desktop app
nix build .#clan-app

# Build VM manager
nix build .#clan-vm-manager
```

## Key Features

1. **Full-Stack System Deployment** - Utilize Clan's toolkit alongside Nix's reliability
2. **Overlay Networks** - Secure, private communication channels
3. **Virtual Machine Integration** - Seamless VM application management
4. **Robust Backup Management** - Long-term, self-hosted data preservation
5. **Intuitive Secret Management** - Simplified encryption and password handling

## Community and Support

- **Matrix Channel:** [#clan:clan.lol](https://matrix.to/#/#clan:clan.lol)
- **IRC Bridge:** [hackint#clan](https://chat.hackint.org/#/connect?join=clan)
- **Website:** [https://clan.lol](https://clan.lol/)
- **Documentation:** [https://docs.clan.lol](https://docs.clan.lol/)
