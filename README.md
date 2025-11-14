# Arda

> A minimal, sustainable infrastructure management tool for NixOS that organizes functionality through a Service/Feature/Role hierarchy.

[![NixOS](https://img.shields.io/badge/NixOS-23.11-blue.svg)](https://nixos.org)
[![Nix](https://img.shields.io/badge/Nix-2.28-green.svg)](https://nixos.org/nix/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Overview

Arda is a minimal, sustainable infrastructure management tool for NixOS that **forks the clan-core project**. It introduces a **Service/Feature/Role hierarchy** as its key differentiator from clan, providing composable functionality through explicit role compositions rather than direct service imports.

### Core Innovation

Unlike clan's service-only approach, Arda organizes functionality into:

- **Services**: Actual software components (e.g., nginx-server, postgresql-server)
- **Features**: Optional service groupings (e.g., web-feature = nginx + certbot + firewall)
- **Roles**: User-facing compositions (e.g., web-server role = nginx + certbot + firewall + monitoring)

This provides a more intuitive and composable architecture for infrastructure management.

### Key Features

- **CLI-First Automation**: All host management through `arda` commands - no manual configuration file editing
- **Auto-Discovery**: Automatic discovery from `hosts/` directory, eliminating merge conflicts
- **Secret Management**: Built-in sops-nix integration with age key distribution
- **Template System**: Extensible templates for common patterns
- **Decade-Scale Maintainability**: Opinionated simplicity for long-term sustainability

## Repository Structure

```bash
arda-core/
├── pkgs/                          # Package directory
│   └── arda-cli/                  # CLI tool implementation
│       ├── commands/              # Command implementations
│       │   ├── host.py            # host create, list, delete
│       │   ├── roles.py           # roles list, add, remove
│       │   ├── secrets.py         # secrets init, add, deploy
│       │   └── templates.py       # templates apply, list
│       └── lib/arda/              # Shared CLI utilities
│
├── modules/nixos/                 # NixOS modules
│   ├── profiles/
│   │   ├── services/              # Individual services
│   │   ├── features/              # Service groupings
│   │   └── common/                # Common configurations
│   ├── roles/                     # Role compositions
│   └── lib/arda.nix               # Utility functions
│
├── templates/                     # Template system
│   └── disk/                      # Disk layout templates
│
├── hosts/                         # Host configurations (auto-discovered)
│   └── {hostname}/                # Per-host configurations
│       └── default.nix
│
└── lib/                          # Arda core library
```

## Getting Started

### Prerequisites

- NixOS or Nix-enabled Linux distribution
- Git
- Age encryption tool for secrets management

### Quick Start

```bash
# Clone the repository
git clone https://github.com/lorddevi/arda-core.git
cd arda-core

# Set up development environment
nix develop

# Create your first machine configuration
arda host create myserver

# Add roles to your machine
arda roles add myserver web-server

# Initialize secrets (for secure secret management)
arda secrets init
```

### Branch Strategy

- **`arda-v1`**: Primary development branch (this repository)
- **`clan-core`**: Reference branch for code extraction from clan
- **`feature/*`**: Feature development branches
- **`bugfix/*`**: Bug fix branches
- **`experiment/*`**: Experimental branches

### Development

```bash
# Install pre-commit hooks (for code quality)
pre-commit install

# Run tests
nix flake check

# Format code
nix fmt
black .
flake8 .

# Build the CLI
nix build .#arda-cli
```

## Documentation

- [Architecture Overview](./bmad-docs/architecture.md)
- [Product Requirements](./bmad-docs/PRD.md)
- [Epic Breakdown](./bmad-docs/epics.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

## License

This project is a fork of [clan-core](https://git.clan.lol/clan/clan-core) with modifications for the Arda project.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Acknowledgments

- [clan-core](https://git.clan.lol/clan/clan-core) - The foundation project
- [NixOS](https://nixos.org) - The operating system and ecosystem
- [sops-nix](https://github.com/Mic92/sops-nix) - Secret management integration
