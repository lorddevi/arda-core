{ pkgs, ... }:
{
  perSystem =
    { config, ... }:
    {
      devShells.default = pkgs.mkShell {
        name = "arda";
        pure = true;
        packages = [
          pkgs.nix
          pkgs.git
          pkgs.gh
          pkgs.age
          config.treefmt.build.wrapper

          # Include overlaid Python packages with rich-click 1.9.4
          pkgs.python313
          pkgs.python313Packages.click
          pkgs.python313Packages.pyyaml
          pkgs.python313Packages.rich
          pkgs.python313Packages.pydantic
          pkgs.python313Packages.rich-click
        ];
        shellHook = ''
          echo "Welcome to Arda development environment"
          echo "Type 'nix fmt' to format code"
          echo "Type 'nix build' to build packages"
          echo "See README.md for more information"
        '';
      };
    };
}
