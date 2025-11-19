{ pkgs, ... }:
{
  perSystem =
    { ... }:
    {
      devShells.default = pkgs.mkShell {
        name = "arda";
        pure = true;
        packages = [
          pkgs.nix
          pkgs.git
          pkgs.gh
          pkgs.age

          # Include Python packages
          pkgs.python3
          pkgs.python3Packages.pip
          pkgs.python3Packages.click
          pkgs.python3Packages.pyyaml
          pkgs.python3Packages.rich
          pkgs.python3Packages.pydantic
          pkgs.python3Packages.rich-click
        ];
        shellHook = ''
          echo "Welcome to Arda development environment"
          echo "Type 'nix fmt' to format code"
          echo "Type 'nix build' to build packages"
          echo "See README.md for more information"
          echo ""
          # Upgrade rich-click to version 1.9.4 for theming support
          python3 -m pip install --upgrade --no-input rich-click==1.9.4 --quiet
          echo "Upgraded rich-click to version 1.9.4"
        '';
      };
    };
}
