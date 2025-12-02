{
  description = "Arda world - infrastructure management with NixOS";

  inputs = {
    nixpkgs.url = "https://nixos.org/channels/nixpkgs-unstable/nixexprs.tar.xz";

    # Arda core - pin to the version that created this world
    arda-core.url = "github:lorddevi/arda-core";
  };

  outputs =
    inputs@{
      self,
      nixpkgs,
      arda-core,
      ...
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = f: nixpkgs.lib.genAttrs systems (system: f system);
    in
    {
      # NixOS configurations for all hosts
      nixosConfigurations = forAllSystems (
        system:
        import ./arda.nix {
          inherit inputs system;
          pkgs = import nixpkgs { inherit system; };
          lib = nixpkgs.lib;
        }
      );

      # Development shell with arda CLI
      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            buildInputs = [
              arda-core.packages.${system}.arda-cli
              pkgs.nix
              pkgs.git
            ];
          };
        }
      );

      # Arda packages (for reference)
      packages = forAllSystems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          # Example package - can be customized
          hello = nixpkgs.hello;
        }
      );
    };
}
