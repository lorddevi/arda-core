{
  description = "arda - minimal infrastructure management for NixOS";

  inputs = {
    nixpkgs.url = "https://nixos.org/channels/nixpkgs-unstable/nixexprs.tar.xz";

    flake-parts.url = "github:hercules-ci/flake-parts";
    flake-parts.inputs.nixpkgs.follows = "nixpkgs";

    treefmt-nix.url = "github:numtide/treefmt-nix";
    treefmt-nix.inputs.nixpkgs.follows = "nixpkgs";

    systems.url = "github:nix-systems/default";

    # Include sops-nix for secret management (critical for Epic 6)
    sops-nix.url = "github:Mic92/sops-nix";
    sops-nix.inputs.nixpkgs.follows = "nixpkgs";

    # Pin rich-click to 1.9.4 for theming support
    rich-click = {
      url = "github:ewels/rich-click/v1.9.4";
      flake = false;
    };
  };

  outputs =
    inputs@{
      nixpkgs,
      systems,
      flake-parts,
      ...
    }:
    let
      # Import our custom overlay that upgrades rich-click to 1.9.4
      # Pass inputs to the overlay
      customOverlay = import ./overlays/default.nix { inherit inputs; };

      # Apply the overlay to nixpkgs
      pkgs = import nixpkgs {
        system = "x86_64-linux";
        overlays = [ customOverlay ];
      };
    in
    flake-parts.lib.mkFlake
      {
        inherit inputs;
        # Pass the modified pkgs with our overlay to all modules
        specialArgs = { inherit pkgs; };
      }
      (
        { ... }:
        {
          systems = import systems;

          imports = [
            ./devShell.nix
            ./formatter.nix
            ./pkgs/flake-module.nix
          ];
        }
      );
}
