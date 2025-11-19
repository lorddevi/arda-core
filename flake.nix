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
  };

  outputs =
    inputs@{
      nixpkgs,
      systems,
      flake-parts,
      ...
    }:
    let
      # Apply the overlay to nixpkgs
      pkgs = import nixpkgs {
        system = "x86_64-linux";
        overlays = [ ];
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
