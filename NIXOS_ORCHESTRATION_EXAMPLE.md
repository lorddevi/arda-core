# NixOS Orchestration Example

This document demonstrates NixOS orchestration patterns for arda-core, created as a test of the enhanced MCP integration workflow.

## Overview

arda-core is a NixOS orchestration system. This example shows configuration patterns for managing multiple hosts.

## MCP Integration Test Results

### 1. NixOS MCP - Package Discovery
```bash
# Found SSH packages:
• ssh (0.3.2) - A pure-Haskell SSH server library
• ocaml5.3.0-awa-mirage (0.5.2) - SSH implementation in OCaml
• pssh (2.3.5) - Parallel SSH Tools
• tmate-ssh-server-unstable (2023-06-02) - tmate SSH Server
• tinyssh (20250201) - Minimalistic SSH server
```

### 2. Home Manager MCP - User Configuration
```bash
# Found Git configuration options:
• programs.git.enable - Whether to enable Git
• programs.bun.enableGitIntegration - Whether to enable Git integration
• programs.delta.enableGitIntegration - Whether to enable git integration for delta
```

### 3. Exa MCP - Research Examples
Found multiple orchestration patterns:
- Multi-host configurations with `mkHost` pattern
- AWS deployment configurations
- Cluster configurations (Avalon example)
- Nix-topology for global topology
- deploy-rs for server cluster deployment

## Sample Multi-Host NixOS Configuration

Based on research from Exa MCP:

```nix
{
  description = "arda-core: NixOS orchestration system";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    deploy-rs.url = "github:serokell/deploy-rs";
  };

  outputs = { self, nixpkgs, deploy-rs }: {
    # Define multiple host configurations
    nixosConfigurations = {
      # Master node - orchestrates other hosts
      arda-master = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          ./hosts/master/configuration.nix
          deploy-rs.nixosModules.default
        ];
      };

      # Worker nodes
      arda-worker-1 = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          ./hosts/worker-1/configuration.nix
        ];
      };

      arda-worker-2 = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          ./hosts/worker-2/configuration.nix
        ];
      };
    };

    # Deployment configuration
    deploy.nodes.arda-master = {
      hostname = "10.0.1.10";
      profiles.system = {
        user = "root";
        path = deploy-rs.lib.x86_64-linux.activate.nixos self.nixosConfigurations.arda-master;
      };
    };

    # Verify all deployments
    checks = builtins.mapAttrs (system: deployLib: deployLib.deployChecks self.deploy) deploy-rs.lib;
  };
}
```

## SSH Configuration Pattern

Using NixOS MCP results:

```nix
# In host configuration
{ config, pkgs, ... }: {
  services.openssh = {
    enable = true;
    permitRootLogin = "no";  # Security best practice
    passwordAuthentication = false;
    publicKeyAuthentication = true;
  };

  # For orchestration, we might want parallel SSH
  environment.systemPackages = [
    pkgs.openssh
    pkgs.pssh  # Parallel SSH tools (found via NixOS MCP)
  ];
}
```

## User Configuration Pattern

Using Home Manager MCP results:

```nix
# In home-manager configuration
{ pkgs, ... }: {
  programs.git = {
    enable = true;
    userName = "arda-core";
    userEmail = "admin@arda-core.local";
  };

  # Delta for better diff output
  programs.delta = {
    enable = true;
    enableGitIntegration = true;
  };
}
```

## Workflow Validation

### AGENTS.md Instructions Used:
1. ✅ Used `nixos_search` for package discovery
2. ✅ Used `home_manager_search` for user config
3. ✅ Used `exa get_code_context_exa` for orchestration research
4. ✅ Used `tokensNum=2000` for balanced context (as recommended)

### Key Insights:
- **NixOS MCP**: Excellent for finding specific packages and options
- **Home Manager MCP**: Great for user-level configuration
- **Exa MCP**: Perfect for researching real-world patterns and examples
- **Context efficiency**: `tokensNum=2000` provided sufficient examples without overload

## Next Steps

This test validates:
1. All MCP servers are operational
2. AGENTS.md guidance is actionable
3. Context efficiency recommendations work
4. Research workflow is effective for arda-core development

Ready for Phase 14 feature development!
