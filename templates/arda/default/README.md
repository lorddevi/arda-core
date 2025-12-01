# Arda World

Welcome to your new Arda world! This directory contains your NixOS infrastructure managed by Arda.

## Quick Start

1. **Enter development shell** (provides `arda` CLI):
   ```bash
   nix develop
   ```

2. **Get help**:
   ```bash
   arda --help
   ```

3. **Add a host**:
   ```bash
   # Edit arda.nix to add hosts to the inventory.hosts section
   # Then build and deploy:
   nix build .#nixosConfigurations.your-host
   nixos-rebuild switch --target-root /mnt --flake .#your-host
   ```

## Directory Structure

- `arda.nix` - Main configuration (inventory, services, roles)
- `flake.nix` - Nix flake configuration
- `modules/` - Custom NixOS modules (optional)
- `.sops/age/` - SOPS age keys for secrets (auto-generated)

## Configuration

Edit `arda.nix` to define your infrastructure:

### Adding Hosts

```nix
inventory.hosts."my-host" = {
  role = "basic-workstation";
  settings = {
    # Host-specific settings
  };
};
```

### Defining Services

Services will be added as Arda's service system is developed.

### Defining Features and Roles

Features group services together, roles combine features:

```nix
features.web-server = {
  services = [ "nginx" "certbot" ];
};

roles.basic-workstation = {
  features = [ "desktop" "development" ];
};
```

## Secrets Management

Arda uses SOPS with age encryption for secrets:

1. **Initialize SOPS** (done automatically on world creation):
   ```bash
   # Age keys are in .sops/age/
   ls -la .sops/age/keys.txt
   ```

2. **Add secrets**:
   ```bash
   # Edit secrets
   sops arda.yaml

   # Deploy to hosts
   arda secrets deploy
   ```

## Updating

To update Arda itself:

```bash
nix flake update
git add .
git commit -m "Update flake"
```

This updates to the latest version of arda-core and all inputs.

## Learn More

- [Arda Documentation](https://github.com/lorddevi/arda-core)
- [NixOS Manual](https://nixos.org/manual/nixos/stable/)
- [Nix Flakes](https://nixos.wiki/wiki/Nix_Flakes)

## Common Commands

```bash
# Build a host configuration
nix build .#nixosConfigurations.your-host

# Enter development shell
nix develop

# Update flake inputs
nix flake update

# Build all configurations
nix build .#nixosConfigurations

# Show configuration for a host
nix eval .#nixosConfigurations.your-host.config
```
