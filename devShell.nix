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

          # Include Python packages from overlaid python313Packages
          # This ensures rich-click 1.9.4 from our overlay is used
          pkgs.python313
          pkgs.python313Packages.pip
          pkgs.python313Packages.setuptools
          pkgs.python313Packages.wheel
          pkgs.python313Packages.click
          pkgs.python313Packages.pyyaml
          pkgs.python313Packages.rich
          pkgs.python313Packages.pydantic
          pkgs.python313Packages.rich-click

          # Python development and testing tools
          pkgs.python313Packages.pytest
          pkgs.python313Packages.pytest-cov
          pkgs.python313Packages.ruff
          pkgs.python313Packages.mypy
          pkgs.python313Packages.bandit
        ];
      };
    };
}
