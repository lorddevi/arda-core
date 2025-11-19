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

          # Include Python packages from overlaid python313Packages
          # This ensures rich-click 1.9.4 from our overlay is used
          pkgs.python313
          pkgs.python313Packages.pip
          pkgs.python313Packages.click
          pkgs.python313Packages.pyyaml
          pkgs.python313Packages.rich
          pkgs.python313Packages.pydantic
          pkgs.python313Packages.rich-click
        ];
      };
    };
}
