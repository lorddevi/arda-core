# Architecture - Infrastructure

## Executive Summary

The **Infrastructure** part is the foundational layer of Clan Core, implementing a comprehensive **NixOS-based Infrastructure-as-Code** system. It provides system configuration, service management, and deployment orchestration through a modular flake-based architecture.

## Technology Stack

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| **Build System** | Nix Flakes | Latest | Declarative, reproducible builds |
| **OS Framework** | NixOS | 24.11+ | Linux distribution with atomic updates |
| **Module System** | NixOS Modules | - | Declarative system configuration |
| **Flake Plugin** | flake-parts | - | Modular flake architecture |
| **Secret Management** | sops-nix | Latest | GitOps-secret management |
| **Disk Management** | disko | Latest | Declarative disk partitioning |
| **Fact Gathering** | nixos-facter-modules | - | System introspection |
| **Code Formatting** | treefmt-nix | - | Consistent code formatting |
| **Network** | ZeroTier, WireGuard, Yggdrasil | Latest | Multiple networking options |
| **Storage** | ZFS, bcachefs | Latest | Advanced filesystem support |

## Architecture Pattern

**Modular Infrastructure-as-Code with Service-Oriented Architecture**

- **Declarative Configuration** - All system state defined in Nix code
- **Composable Modules** - 25+ independent, composable modules
- **Service Mesh** - 20+ interconnected services
- **Multi-Network Support** - ZeroTier, WireGuard, Yggdrasil overlays
- **Secret-First Design** - SOPS-integrated secret management

## Data Architecture

### Module Structure

```
nixosModules/clanCore/
├── Core System Modules
│   ├── metadata.nix           # System metadata
│   ├── options.nix            # Module options interface
│   ├── defaults.nix           # Default configurations
│   ├── vars/                  # Variable definitions
│   └── inventory/             # System inventory tracking
│
├── System Configuration
│   ├── networking.nix         # Network configuration
│   ├── nix-settings.nix       # Nix package manager settings
│   ├── machine-id/            # Machine identification
│   ├── state-version/         # NixOS state version management
│   └── postgresql/            # PostgreSQL integration
│
├── Service Management
│   ├── backups.nix            # Backup orchestration
│   ├── facts/                 # System facts gathering
│   └── sops.nix               # Secret management (SOPS)
│
├── Virtualization
│   ├── vm.nix                 # Virtual machine support
│   └── machine-id/            # VM-specific machine ID handling
│
├── Desktop Integration
│   └── wayland-proxy-virtwl.nix # Wayland proxy for VMs
│
├── Networking
│   ├── zerotier/              # ZeroTier mesh networking
│   └── zfs.nix                # ZFS filesystem support
│
└── Advanced Features
    ├── outputs.nix            # Output definitions
    └── bcachefs.nix           # bcachefs filesystem
```

### Service Ecosystem (clanServices/)

| Service | Purpose | Category |
|---------|---------|----------|
| **borgbackup** | Automated backups | Storage |
| **certificates** | PKI certificate management | Security |
| **coredns** | DNS server | Network |
| **garage** | S3-compatible object storage | Storage |
| **matrix-synapse** | Matrix homeserver | Communication |
| **monitoring** | System monitoring | Observability |
| **wireguard** | VPN solution | Network |
| **yggdrasil** | Mesh networking | Network |
| **zerotier** | Software-defined networking | Network |
| **users** | User management | System |
| **wifi** | WiFi configuration | Network |

### Configuration Management

**Key Configuration Areas:**

1. **Network Configuration**
   - ZeroTier network definitions
   - WireGuard tunnel configurations
   - Yggdrasil mesh setup
   - WiFi profiles

2. **Storage Configuration**
   - ZFS pool definitions
   - bcachefs setup
   - Backup policies (borgbackup)
   - Object storage (garage/S3)

3. **Service Orchestration**
   - Service dependencies
   - Startup order
   - Resource limits
   - Health checks

4. **Secret Management (SOPS)**
   - Encrypted secret files
   - Age/PGP key support
   - GitOps integration
   - Selective decryption

## API Design

### Module Interface

**Main Interface:** `nixosModules/clanCore/default.nix`

```nix
{
  # System configuration
  config = {
    # Enable clanCore
    clanCore = {
      enable = true;
      # Configure features
      backups.enable = true;
      networking.enable = true;
      secrets.enable = true;
      # Service selection
      services = {
        borgbackup.enable = true;
        wireguard.enable = true;
        # ... more services
      };
    };
  };
}
```

### Flake Interface

**Entry Point:** `flake.nix`

```nix
{
  outputs = inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake {
      inherit inputs;
    } {
        clan = {
          # NixOS module
          nixosModules.clanCore = import ./nixosModules/clanCore;

          # Applications
          apps.clan-cli = clan-cli.packages.x86_64-linux.default;
          apps.clan-app = clan-app.packages.x86_64-linux.default;
          apps.clan-vm-manager = clan-vm-manager.packages.x86_64-linux.default;

          # Packages
          packages = {
            clan-cli = ...;
            clan-app = ...;
            clan-vm-manager = ...;
          };
        };
    };
}
```

## Component Overview

### 1. Core Module System

**Technology:** NixOS module system
**Purpose:** Declarative system configuration

**Key Files:**

- `nixosModules/clanCore/default.nix` - Main module entry point
- `nixosModules/clanCore/options.nix` - Public interface
- `nixosModules/clanCore/meta/interface.nix` - Module metadata

**Architecture:**

- Import-based composition
- Type-checked option declarations
- Config/state separation
- Debuggable with `nixos-option`

### 2. Service Architecture

**Technology:** Service modules
**Purpose:** Independent, composable services

**Pattern:**

- Each service = independent NixOS module
- Service configuration in `clanServices/<service>/`
- Service documentation in `clanServices/<service>/README.md`
- Lazy loading (only enabled if configured)

**Service Dependencies:**

```
borgbackup ← certificates (for backup encryption)
coredns ← certificates (for TLS)
matrix-synapse ← certificates (for TLS)
garage ← certificates (for TLS)
```

### 3. Secret Management (SOPS)

**Technology:** sops-nix
**Purpose:** GitOps-secret management

**Features:**

- Encrypted at rest
- Decrypted at build/runtime
- GitOps workflow compatible
- Age/PGP key support
- Per-environment secrets

**Usage:**

```nix
{
  config = {
    sops.defaultGpgKey = "0xDEADBEEF";
    sops.secrets."service/password" = {};
  };
}
```

### 4. Network Overlay System

**Technology:** ZeroTier + WireGuard + Yggdrasil
**Purpose:** Multiple networking paradigms

**ZeroTier:**

- Software-defined networking
- Earth-wide L2 network
- No VPN server required

**WireGuard:**

- Modern VPN protocol
- Site-to-site or host-to-host
- High performance

**Yggdrasil:**

- Mesh networking
- End-to-end encryption
- Self-organizing topology

## Development Workflow

### Prerequisites

- Nix package manager
- Access to flake input channels

### Development Commands

```bash
# Enter development environment
nix develop

# Build infrastructure
nix build .

# Build specific package
nix build .#clan-cli
nix build .#clan-app

# Run tests
nix flake check

# Update flake inputs
nix flake update

# Evaluate configuration
nixos-repl .

# Test configuration
nixos-rebuild test --flake .#<hostname>
```

### Build Process

1. **Flake Evaluation**
   - Resolve inputs (nixpkgs, flake-parts, etc.)
   - Evaluate all modules
   - Type-check configurations

2. **Module Compilation**
   - Convert Nix to NixOS module format
   - Resolve all imports
   - Generate systemd units

3. **Service Configuration**
   - Generate service configurations
   - Create systemd unit files
   - Set up dependencies

4. **Build Verification**
   - Type checking
   - Dependency resolution
   - Circle-free evaluation

## Deployment Architecture

### Deployment Model

**Single Flake, Multiple Targets:**

```bash
# Deploy to specific machine
nixos-rebuild switch --flake .#test-machine

# Build for specific system
nix build .#nixosConfigurations.test-machine.config.system.build.toplevel

# Deploy across machines
nixos-rebuild switch --flake .#<machine-name>
```

### Configuration Hierarchy

1. **Base Module** (clanCore)
   - Common configuration
   - All systems get this by default

2. **Service Modules**
   - Optional services
   - Enabled per-system

3. **Machine-Specific**
   - Hostname, hardware config
   - Per-deployment customizations

4. **User Overrides**
   - User-level customizations
   - Can extend base config

### State Management

**NixOS State Version:**

- Tracks upgrade history
- Automatic migrations
- Rollback support

**Machine ID:**

- Unique per system
- Persistent across reboots
- Used for inventory

**Facts Gathering:**

- Hardware inventory
- Software inventory
- Network topology
- Service status

## Testing Strategy

### Validation Layers

1. **Static Analysis**
   - `nix flake check` - Lint and validate
   - `nix eval` - Type checking
   - `treefmt-nix` - Code formatting

2. **Unit Tests**
   - Per-module tests (checks/)
   - Service validation
   - Configuration testing

3. **Integration Tests**
   - Multi-service scenarios
   - Network topology tests
   - Deployment validation

4. **Manual Testing**
   - `nixos-rebuild test`
   - VM testing
   - Hardware-in-loop

### Test Commands

```bash
# Run all checks
nix flake check

# Format code
nix run .#fmt

# Build with debug info
nix build . --debug

# Enter REPL for debugging
nix repl

# Evaluate specific option
nixos-repl .#config.clanCore.backups.enable
```

## Performance Characteristics

### Build Performance

- **Cold Build:** 5-15 minutes (full system)
- **Incremental Build:** 30-120 seconds (changed modules)
- **Cache Hits:** 90%+ (using binary caches)

### Runtime Performance

- **Boot Time:** Fast (systemd optimizations)
- **Service Startup:** Parallel by default
- **Update Time:** Atomic (NixOS)

### Scalability

- **Modules:** Tested with 25+ modules
- **Services:** Tested with 20+ services
- **Systems:** Scales to hundreds of machines

## Security Considerations

### Secret Management

- SOPS encryption (age/PGP keys)
- No secrets in source code
- Selective decryption per system
- Audit trail via git history

### Network Security

- WireGuard for VPN (modern cryptography)
- ZeroTier for SDN (encryption)
- Yggdrasil for mesh (E2E encryption)

### System Security

- NixOS sandboxing
- Declarative configurations
- Reproducible builds
- Immutable system paths

## Integration with Other Parts

### From Clan CLI

- Reads configuration from deployed systems
- Queries facts/inventory
- Manages services
- Triggers deployments

### From Clan App (Desktop)

- Displays system information
- Shows service status
- Manages configuration
- Triggers deployments

### From Clan VM Manager

- Provisions VM configurations
- Manages VM lifecycle
- Handles VM networking
- Coordinates with clanCore modules

## Known Limitations

1. **Nix Learning Curve** - Requires Nix knowledge for deep customization
2. **Build Time** - Full system builds can take minutes
3. **Debugging** - Error messages can be cryptic
4. **Binary Caches** - Dependency on external caches for fast builds

## Future Enhancements

1. **Enhanced Fact Gathering** - More comprehensive system introspection
2. **Service Templates** - Easier service creation
3. **Monitoring Integration** - Better observability
4. **CI/CD Integration** - Automated testing and deployment
5. **Multi-Cloud Support** - Cloud provider integration

## References

- [NixOS Manual](https://nixos.org/manual/nixos/stable/)
- [Flakes Documentation](https://nixos.org/manual/nix/stable/command-ref/new-cli/nix3-flake.html)
- [sops-nix](https://github.com/Mic92/sops-nix)
- [disko](https://github.com/nix-community/disko)
- [Project README](../README.md)
- [Flake Configuration](../flake.nix)
