# Clan Core - Project Documentation Index

**Primary Entry Point for AI-Assisted Development**

This index provides comprehensive navigation of the Clan Core project, the foundational repository for the [clan.lol](https://clan.lol/) project.

---

## Project Overview

### Project Summary

- **Type:** Monorepo with 4 parts
- **Primary Language:** Nix, Python 3.13, TypeScript
- **Architecture:** Modular infrastructure with service-oriented architecture
- **Project Purpose:** NixOS-based system management and deployment platform

---

## Quick Reference

### Part-Based Navigation

#### Infrastructure (infrastructure) - NixOS/Flake

- **Type:** Infrastructure-as-Code
- **Tech Stack:** NixOS, Nix Flakes, flake-parts, sops-nix, disko
- **Root Path:** `/home/ld/src/clan-core`
- **Architecture:** [architecture-infrastructure.md](./architecture-infrastructure.md)

#### Clan App (clan-app) - Desktop Application

- **Type:** Desktop Application
- **Tech Stack:** Python 3.13 (backend), SolidJS + TypeScript + Vite (frontend)
- **Root Path:** `/home/ld/src/clan-core/pkgs/clan-app`
- **Architecture:** [architecture-clan-app.md](./architecture-clan-app.md)

#### Clan CLI (clan-cli) - CLI Tool

- **Type:** CLI Tool
- **Tech Stack:** Python 3.13, argparse, pytest, mypy
- **Root Path:** `/home/ld/src/clan-core/pkgs/clan-cli`
- **Architecture:** [architecture-clan-cli.md](./architecture-clan-cli.md)

#### VM Manager (clan-vm-manager) - CLI Tool

- **Type:** CLI Tool (VM Management)
- **Tech Stack:** Python 3.13, QEMU/KVM, setuptools
- **Root Path:** `/home/ld/src/clan-core/pkgs/clan-vm-manager`
- **Architecture:** [architecture-clan-vm-manager.md](./architecture-clan-vm-manager.md)

### Integration Architecture

- **Cross-Part Communication:** [integration-architecture.md](./integration-architecture.md)
  - Data flow patterns
  - Service dependencies
  - API contracts
  - Error handling

---

## Generated Documentation

### Core Documentation

- **[Project Overview](./project-overview.md)**
  - Executive summary
  - Tech stack per part
  - Repository structure
  - Getting started guide

- **[Source Tree Analysis](./source-tree-analysis.md)**
  - Complete directory tree with annotations
  - Critical folders explained
  - Entry points documented
  - Integration points

### Architecture Documentation

- **[Architecture - Infrastructure](./architecture-infrastructure.md)**
  - NixOS module system
  - Service ecosystem (20+ services)
  - Secret management (SOPS)
  - Network overlay system

- **[Architecture - Clan App](./architecture-clan-app.md)**
  - Multi-layer desktop architecture
  - Frontend (SolidJS + TypeScript)
  - Backend (Python 3.13)
  - State management

- **[Architecture - Clan CLI](./architecture-clan-cli.md)**
  - Layered CLI architecture
  - Command hierarchy
  - Service layer integration
  - API design

- **[Architecture - VM Manager](./architecture-clan-vm-manager.md)**
  - VM lifecycle management
  - QEMU/KVM integration
  - Network configuration
  - State tracking

### Integration Documentation

- **[Integration Architecture](./integration-architecture.md)**
  - System integration patterns
  - API contracts
  - Service dependencies
  - Data flow patterns

---

## Existing Documentation

### Main Project Documentation

- **[Project README](/home/ld/src/clan-core/README.md)**
  - Main project documentation
  - Mission and vision
  - Feature overview
  - Community links

- **[Contributing Guide](/home/ld/src/clan-core/docs/CONTRIBUTING.md)**
  - Contribution guidelines
  - Code style rules
  - PR process
  - Testing requirements

- **[Main Documentation Site](/home/ld/src/clan-core/docs/)**
  - Complete mkdocs site
  - Code examples
  - Nix documentation
  - Getting started guides

### Part-Specific Documentation

- **[Clan CLI Docs](/home/ld/src/clan-core/pkgs/clan-cli/README.md)**
  - CLI usage guide
  - Command reference
  - Configuration options

- **[Clan App Docs](/home/ld/src/clan-core/pkgs/clan-app/README.md)**
  - Desktop app documentation
  - UI component guide
  - Development setup

- **[Clan App UI Docs](/home/ld/src/clan-core/pkgs/clan-app/ui/README.md)**
  - Frontend development
  - Component library
  - Build process

- **[VM Manager Docs](/home/ld/src/clan-core/pkgs/clan-vm-manager/README.md)**
  - VM management guide
  - Lifecycle operations
  - Configuration

- **[Library Docs](/home/ld/src/clan-core/lib/README.md)**
  - Shared library code
  - Test utilities
  - Common modules

### Service Documentation

The following services have individual README files:

- **[Borg Backup](/home/ld/src/clan-core/clanServices/borgbackup/README.md)**
- **[Certificates](/home/ld/src/clan-core/clanServices/certificates/README.md)**
- **[CoreDNS](/home/ld/src/clan-core/clanServices/coredns/README.md)**
- **[Garage S3](/home/ld/src/clan-core/clanServices/garage/README.md)**
- **[Matrix Synapse](/home/ld/src/clan-core/clanServices/matrix-synapse/README.md)**
- **[Monitoring](/home/ld/src/clan-core/clanServices/monitoring/README.md)**
- **[WireGuard](/home/ld/src/clan-core/clanServices/wireguard/README.md)**
- **[ZeroTier](/home/ld/src/clan-core/clanServices/zerotier/README.md)**

[See all services...](/home/ld/src/clan-core/clanServices/)

---

## Getting Started

### Prerequisites

1. **Nix Package Manager**

   ```bash
   # Install Nix
   sh <(curl -L https://nixos.org/nix/install) --daemon
   ```

2. **Python 3.13+** (for CLI and desktop app development)

   ```bash
   # Install Python
   # Usually comes with Nix devShell
   ```

3. **Node.js + npm** (for UI components)

   ```bash
   # Install Node.js
   # Usually comes with Nix devShell
   ```

### Development Setup

```bash
# Clone the repository
git clone https://git.clan.lol/clan/clan-core.git
cd clan-core

# Enter development shell (includes all dependencies)
nix develop

# Verify installation
clan --help
```

### Building Components

```bash
# Build all components
nix build .

# Build specific components
nix build .#clan-cli
nix build .#clan-app
nix build .#clan-vm-manager

# Build infrastructure configuration
nix build .
```

### Development Commands

```bash
# CLI Development
cd pkgs/clan-cli
python -m pytest
mypy clan_cli/

# Desktop App Development
cd pkgs/clan-app/ui
npm install
npm run dev

# VM Manager Development
cd pkgs/clan-vm-manager
python -m pytest

# Infrastructure Testing
nix flake check
nixos-rebuild test --flake .#<hostname>
```

---

## System Architecture Summary

### Repository Structure

```
clan-core/
├── .bmad/                   # BMAD framework
├── bmad-docs/               # Generated docs (this folder)
├── checks/                  # Validation modules
├── clanModules/             # Clan NixOS modules
├── clanServices/            # Service definitions (20+)
│   ├── borgbackup/
│   ├── certificates/
│   ├── coredns/
│   ├── garage/
│   ├── matrix-synapse/
│   ├── monitoring/
│   ├── wireguard/
│   ├── yggdrasil/
│   └── [12+ more]
├── docs/                    # Documentation site
├── flake.nix                # ⭐ Main entry point
├── lib/                     # Shared library
├── nixosModules/            # NixOS modules
│   └── clanCore/            # ⭐ Core infrastructure
└── pkgs/                    # Applications
    ├── clan-app/            # Desktop application
    ├── clan-cli/            # CLI tool
    └── clan-vm-manager/     # VM manager
```

### Technology Stack

| Component | Language | Framework | Purpose |
|-----------|----------|-----------|---------|
| **Infrastructure** | Nix | NixOS | System configuration |
| **CLI** | Python 3.13 | argparse | Command-line interface |
| **Desktop App** | Python/TS | SolidJS | Graphical interface |
| **VM Manager** | Python 3.13 | QEMU/KVM | VM lifecycle |

### Key Files

- **Entry Points:**
  - `flake.nix` - Primary flake configuration
  - `nixosModules/clanCore/default.nix` - Core NixOS module
  - `pkgs/clan-cli/clan_cli/cli.py` - CLI entry
  - `pkgs/clan-app/clan_app/__main__.py` - Desktop app entry
  - `pkgs/clan-vm-manager/clan_vm_manager/__main__.py` - VM manager entry

---

## Common Tasks

### Deploy a Machine

```bash
# Using CLI
clan deploy <machine-name>

# Using desktop app
# Run: clan-app
# Navigate to: Machines → Select Machine → Deploy
```

### Manage Services

```bash
# List services
clan services list

# Start service
clan services start <service-name>

# Check status
clan services status <service-name>
```

### Create and Manage VMs

```bash
# Create VM
clan-vm-manager create <vm-name> --cpus 2 --memory 2048

# Start VM
clan-vm-manager start <vm-name>

# Deploy to VM
clan deploy <vm-name>
```

### Build and Test

```bash
# Build everything
nix build .

# Run tests
nix flake check

# Format code
nix run .#fmt
```

---

## AI-Assisted Development Tips

### When Working on Infrastructure

1. Start with: [architecture-infrastructure.md](./architecture-infrastructure.md)
2. Reference: [flake.nix](/home/ld/src/clan-core/flake.nix)
3. Check: [nixosModules/clanCore/](/home/ld/src/clan-core/nixosModules/clanCore/)
4. Study: [clanServices/](/home/ld/src/clan-core/clanServices/)

### When Working on CLI

1. Start with: [architecture-clan-cli.md](./architecture-clan-cli.md)
2. Reference: [pkgs/clan-cli/](/home/ld/src/clan-core/pkgs/clan-cli/)
3. Check: [pyproject.toml](/home/ld/src/clan-core/pkgs/clan-cli/pyproject.toml)
4. Study: [clan_cli/cli.py](/home/ld/src/clan-core/pkgs/clan-cli/clan_cli/cli.py)

### When Working on Desktop App

1. Start with: [architecture-clan-app.md](./architecture-clan-app.md)
2. Reference: [pkgs/clan-app/](/home/ld/src/clan-core/pkgs/clan-app/)
3. Check: [package.json](/home/ld/src/clan-core/pkgs/clan-app/ui/package.json)
4. Study: [app.py](/home/ld/src/clan-core/pkgs/clan-app/clan_app/app.py)

### When Working on VM Manager

1. Start with: [architecture-clan-vm-manager.md](./architecture-clan-vm-manager.md)
2. Reference: [pkgs/clan-vm-manager/](/home/ld/src/clan-core/pkgs/clan-vm-manager/)
3. Check: [pyproject.toml](/home/ld/src/clan-core/pkgs/clan-vm-manager/pyproject.toml)
4. Study: [vm_ops.py](/home/ld/src/clan-core/pkgs/clan-vm-manager/clan_vm_manager/vm_ops.py)

### When Integrating Components

1. Start with: [integration-architecture.md](./integration-architecture.md)
2. Review: Service dependencies
3. Check: API contracts
4. Test: Integration workflows

---

## File Count Summary

**Generated Documentation:** 8 files

- project-overview.md
- source-tree-analysis.md
- architecture-infrastructure.md
- architecture-clan-app.md
- architecture-clan-cli.md
- architecture-clan-vm-manager.md
- integration-architecture.md
- index.md (this file)

**Existing Documentation:** 30+ files

- Main README
- 20+ service READMEs
- Per-part documentation
- MkDocs site
- Contributing guide

**Total Lines:** ~15,000+ lines of documentation

---

## Next Steps

1. **For New Contributors:**
   - Read: [Project Overview](./project-overview.md)
   - Read: [Contributing Guide](/home/ld/src/clan-core/docs/CONTRIBUTING.md)
   - Review: [Source Tree Analysis](./source-tree-analysis.md)

2. **For Brownfield PRD:**
   - Use: This index as primary reference
   - Check: [Architecture docs](./architecture-infrastructure.md) for infrastructure
   - Review: [Integration Architecture](./integration-architecture.md)

3. **For Feature Development:**
   - Identify the component (infrastructure, CLI, app, VM)
   - Read corresponding architecture doc
   - Study existing code patterns
   - Check service integration points

4. **For Testing:**
   - Check: [checks/](/home/ld/src/clan-core/checks/) directory
   - Run: `nix flake check`
   - Execute: Component-specific tests

---

## Support and Community

- **Matrix Channel:** [#clan:clan.lol](https://matrix.to/#/#clan:clan.lol)
- **IRC Bridge:** [hackint#clan](https://chat.hackint.org/#/connect?join=clan)
- **Website:** [https://clan.lol](https://clan.lol/)
- **Documentation:** [https://docs.clan.lol](https://docs.clan.lol/)
- **Repository:** [https://git.clan.lol/clan/clan-core](https://git.clan.lol/clan/clan-core)

---

## Maintenance

This index and all generated documentation were created on **2025-11-14** using an exhaustive scan of the Clan Core repository.

To regenerate or update documentation, run:

```bash
# (This workflow - document-project)
# Documentation is auto-generated based on codebase state
```

**Document Scan Report:** [project-scan-report.json](./project-scan-report.json)

---

**Last Updated:** 2025-11-14T16:56:29.234Z
**Scan Level:** Exhaustive
**Workflow Mode:** Initial Scan
**Project Classification:** Monorepo with 4 parts
