{ pkgs, ... }:
{
  perSystem =
    { ... }:
    {
      devShells.default = pkgs.mkShell {
        name = "arda";
        packages = [
          pkgs.nix
          pkgs.git
          pkgs.gh
          pkgs.age
          pkgs.direnv
          pkgs.coreutils
          pkgs.which
          pkgs.just

          # Python development environment
          # Direct references to overlaid python313Packages to ensure rich-click 1.9.4 is used
          pkgs.python313
          pkgs.python313Packages.pip
          pkgs.python313Packages.setuptools
          pkgs.python313Packages.wheel
          pkgs.python313Packages.click
          pkgs.python313Packages.pyyaml
          pkgs.python313Packages.rich
          pkgs.python313Packages.pydantic
          pkgs.python313Packages.rich-click
          pkgs.python313Packages.toml

          # Testing and linting tools
          pkgs.python313Packages.pytest
          pkgs.python313Packages.pytest-cov
          pkgs.python313Packages.ruff
          pkgs.python313Packages.mypy
          pkgs.python313Packages.bandit
          pkgs.python313Packages.detect-secrets

          # Development tools
          pkgs.pre-commit # Git hooks framework
          pkgs.treefmt # Code formatter (includes nixfmt)
        ];
      };
    };
}
