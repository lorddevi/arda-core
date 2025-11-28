{ pkgs, ... }:
{
  perSystem =
    { ... }:
    {
      devShells.default =
        let
          # Create a Python environment for development
          python-with-vm-support = pkgs.python313.withPackages (ps: [
            ps.pip
            ps.setuptools
            ps.wheel
            ps.click
            ps.pyyaml
            ps.rich
            ps.pydantic
            ps.rich-click
            ps.tomli-w
            ps.pytest
            ps.pytest-cov
            ps.ruff
            ps.mypy
            ps.bandit
            ps.detect-secrets
          ]);
        in
        pkgs.mkShell {
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
            python-with-vm-support

            # Development tools
            pkgs.pre-commit # Git hooks framework
            pkgs.treefmt # Code formatter (includes nixfmt)
          ];
        };
    };
}
