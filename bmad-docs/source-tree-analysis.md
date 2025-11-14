# Source Tree Analysis

## Repository Structure Overview

The Clan Core repository follows a **monorepo** structure with clear separation of concerns across 4 main parts and comprehensive infrastructure support.

## Annotated Directory Tree

```
clan-core/                     # Project root
│
├── .bmad/                     # BMAD development framework
│   ├── bmm/                   # BMM (Business Model Method) agents
│   ├── bmb/                   # BMB (Build-Method-Build) modules
│   └── core/                  # Core BMAD workflows
│
├── .github/                   # GitHub configuration
│   └── workflows/
│       └── repo-sync.yml      # GitHub↔Gitea synchronization (cron: hourly)
│
├── bmad-docs/                 # Generated documentation (this folder)
│
├── checks/                    # System validation modules
│   ├── app-ocr/              # OCR application checks
│   ├── assets/               # Asset validation
│   ├── borgbackup/           # Borg backup system tests
│   ├── container/            # Container validation
│   ├── devshell/             # Development shell checks
│   ├── flash/                # Flash storage checks
│   ├── installation/         # Installation tests
│   ├── llm/                  # Language model tests
│   ├── mycelium/             # Mycelium network checks
│   ├── service-dummy-test/   # Service testing framework
│   ├── systemd-abstraction/  # Systemd test utilities
│   ├── user-firewall/        # Firewall configuration tests
│   └── wayland-proxy-virtwl/ # Wayland proxy tests
│
├── clanModules/               # Clan-specific NixOS modules
│   └── flake-module.nix      # Module definition
│
├── clanServices/              # Service definitions (20+ services)
│   ├── admin/                # System administration tools
│   ├── borgbackup/           # Borg backup service
│   ├── certificates/         # Certificate management
│   ├── coredns/              # CoreDNS service
│   ├── data-mesher/          # Data meshing network
│   ├── dyndns/               # Dynamic DNS
│   ├── emergency-access/     # Emergency access service
│   ├── garage/               # Garage S3-compatible storage
│   ├── hello-world/          # Example/test service
│   ├── importer/             # Data import service
│   ├── internet/             # Internet gateway
│   ├── kde/                  # KDE desktop integration
│   ├── localbackup/          # Local backup service
│   ├── matrix-synapse/       # Matrix homeserver
│   ├── monitoring/           # System monitoring
│   ├── mycelium/             # Mycelium networking
│   ├── packages/             # Package management
│   ├── sshd/                 # SSH daemon configuration
│   ├── syncthing/            # Syncthing file sync
│   ├── tor/                  # Tor integration
│   ├── trusted-nix-caches/   # Trusted Nix cache configuration
│   ├── users/                # User management
│   ├── wifi/                 # WiFi configuration
│   ├── wireguard/            # WireGuard VPN
│   ├── yggdrasil/            # Yggdrasil mesh networking
│   └── zerotier/             # ZeroTier network
│
├── docs/                     # Documentation site
│   ├── code-examples/        # Code examples
│   ├── nix/                  # Nix documentation
│   ├── site/                 # Built documentation
│   ├── _internal/            # Internal docs
│   ├── mkdocs.yml            # MkDocs configuration
│   ├── CONTRIBUTING.md       # Contribution guidelines
│   └── README.md             # Docs README
│
├── flake.nix                 # ⭐ Main flake entry point
│                             # Defines: inputs, outputs, packages, apps
│
├── lib/                      # Shared library code
│   ├── README.md             # Library documentation
│   └── test/                 # Test utilities
│
├── machines/                 # Machine configurations
│
├── modules/                  # NixOS modules
│
├── nixosModules/             # Additional NixOS modules
│   ├── bcachefs.nix          # Bcachefs filesystem module
│   ├── clanCore/             # ⭐ Main Clan NixOS module
│   │   ├── backups.nix       # Backup configuration
│   │   ├── defaults.nix      # Default settings
│   │   ├── facts/            # System facts gathering
│   │   ├── inventory/        # System inventory
│   │   ├── meta/interface.nix # Module interface
│   │   ├── metadata.nix      # Metadata handling
│   │   ├── networking.nix    # Network configuration
│   │   ├── nix-settings.nix  # Nix configuration
│   │   ├── options.nix       # Module options
│   │   ├── outputs.nix       # Output definitions
│   │   ├── sops.nix          # SOPS secret management
│   │   ├── vars/             # Variable definitions
│   │   ├── nixos-facter.nix  # Fact gathering
│   │   ├── vm.nix            # Virtual machine support
│   │   ├── postgresql/       # PostgreSQL integration
│   │   ├── machine-id/       # Machine identification
│   │   ├── state-version/    # NixOS state version
│   │   ├── wayland-proxy-virtwl.nix # Wayland proxy
│   │   ├── zerotier/         # ZeroTier integration
│   │   └── zfs.nix           # ZFS filesystem module
│   ├── hidden-ssh-announce.nix # SSH announcement
│   ├── installer/            # Installer modules
│   ├── machineModules/       # Machine-specific modules
│   └── user-firewall/        # User firewall
│
└── pkgs/                     # ⭐ Packaged applications
    ├── clan-app/             # Desktop application ⭐
    │   ├── clan_app/         # Python backend
    │   │   ├── __main__.py   # Entry point
    │   │   ├── app.py        # Main application
    │   │   ├── api/          # API endpoints
    │   │   ├── backends/     # Backend implementations
    │   │   │   ├── http/     # HTTP server
    │   │   │   └── webview/  # Webview backend
    │   │   ├── middleware/   # Request middleware
    │   │   └── ui/           # UI integration
    │   ├── tests/            # Test suite
    │   ├── ui/               # SolidJS frontend ⭐
    │   │   ├── package.json  # npm dependencies
    │   │   ├── src/          # Source code
    │   │   ├── public/       # Static assets
    │   │   └── ...           # Vite + TypeScript setup
    │   ├── default.nix       # Nix package definition
    │   └── flake-module.nix  # Flake module
    │
    ├── clan-cli/             # CLI tool ⭐
    │   ├── clan_cli/         # CLI implementation
    │   ├── clan_lib/         # Shared library
    │   ├── api.py            # API definitions
    │   ├── docs.py           # Documentation generator
    │   ├── openapi.py        # OpenAPI specifications
    │   ├── conftest.py       # Pytest configuration
    │   ├── pyproject.toml    # Python metadata
    │   ├── default.nix       # Nix package definition
    │   └── flake-module.nix  # Flake module
    │
    ├── clan-vm-manager/      # VM manager ⭐
    │   ├── clan_vm_manager/  # Implementation
    │   ├── pyproject.toml    # Python metadata
    │   ├── default.nix       # Nix package definition
    │   └── flake-module.nix  # Flake module
    │
    ├── builders/             # Build systems
    ├── classgen/             # Class generation
    ├── docs-from-code/       # Documentation from code
    ├── editor/               # Editor configuration
    ├── icon-update/          # Icon update utilities
    ├── installer/            # Installer scripts
    ├── merge-after-ci/       # CI merge utilities
    ├── minifakeroot/         # Minifakeroot support
    ├── option-search/        # Option search tools
    ├── run-vm-test-offline/  # VM test runner
    ├── scripts/              # Utility scripts
    ├── tea-create-pr/        # PR creation tools
    ├── testing/              # Testing utilities
    └── [20+ more packages]   # Supporting packages
```

## Critical Folders Explained

### Infrastructure Components

**1. flake.nix** - Main entry point

- Defines all inputs (nixpkgs, flake-parts, disko, sops-nix, etc.)
- Exports packages, apps, and NixOS modules
- Uses flake-parts for modular architecture

**2. nixosModules/clanCore/** - Core system module

- Comprehensive NixOS module providing 25+ sub-modules
- Handles: backups, facts, inventory, metadata, networking, secrets
- Includes VM support, PostgreSQL integration, ZFS, ZeroTier

**3. clanServices/** - Service ecosystem

- 20+ independent services (backup, DNS, storage, networking, etc.)
- Each service is a self-contained module
- Services:borgbackup, certificates, coredns, garage, matrix-synapse, monitoring, wireguard, etc.

### Application Components

**4. pkgs/clan-cli/** - Primary CLI tool

- Python-based command-line interface
- Uses argparse + custom middleware architecture
- Provides `clan` command for system management

**5. pkgs/clan-app/** - Desktop application

- **Backend:** Python 3.13 with HTTP server and webview backend
- **Frontend:** SolidJS + TypeScript + Vite build system
- Modern UI with storybook, testing, and comprehensive tooling

**6. pkgs/clan-vm-manager/** - VM lifecycle management

- Python CLI for VM operations
- Includes history tracking and management commands

### Development & Quality

**7. checks/** - Automated validation

- Module-specific validation tests
- Infrastructure: borgbackup, container, devshell checks
- Application: OCR, flash, systemd tests

**8. docs/** - Documentation site

- MkDocs-based documentation
- Includes code examples, Nix docs
- Community and contribution guides

## Entry Points

### System-Level Entry Points

- **flake.nix** - Primary flake entry point
- **nixosModules/clanCore/default.nix** - Core NixOS module

### Application Entry Points

- **pkgs/clan-cli/clan_cli/cli.py** - `clan` command entry
- **pkgs/clan-app/clan_app/**main**.py** - Desktop app entry
- **pkgs/clan-vm-manager/clan_vm_manager/**main**.py** - VM manager entry

## Integration Points

### Multi-Part Architecture

- **Shared Infrastructure:** All parts use Nix/flake system
- **Shared Services:** clanServices provides system-level capabilities
- **Shared Libraries:** lib/ and pkgs/*/clan_lib/ for common code
- **Unified Build:** Single `nix develop` for entire environment

### Service Dependencies

```
clan-cli
  ↓ uses
clanServices (borgbackup, certificates, etc.)
  ↓ configured by
nixosModules/clanCore
  ↓ managed via
flake.nix (infrastructure level)
```

### Application Dependencies

```
clan-app (UI)
  ↓ communicates with
clan-cli (command execution)
  ↓ manages
clanServices (system services)
  ↓ provision
nixosModules/clanCore (system configuration)
```

## Notable Patterns

1. **Consistent Nix Integration** - Every component has default.nix + flake-module.nix
2. **Service-Oriented Design** - 20+ independent, composable services
3. **Modular Architecture** - Clear separation between infrastructure, CLI, and desktop app
4. **Testing Integration** - checks/ + pytest for comprehensive validation
5. **Documentation-First** - Extensive docs/ + generated documentation

## Summary Statistics

- **Total Directories:** 100+
- **Service Modules:** 20+
- **NixOS Modules:** 25+ (in clanCore alone)
- **Python Packages:** 4 primary (clan-cli, clan-app, clan-vm-manager, clan_lib)
- **Programming Languages:** Nix, Python 3.13, TypeScript
- **Build Systems:** Nix flakes, setuptools, Vite
