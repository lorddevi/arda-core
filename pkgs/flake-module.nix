{ pkgs, ... }:
{
  perSystem =
    { system, ... }:
    let
      python313Packages = pkgs.python313Packages;
    in
    {
      packages = {
        # Uses pkgs with our overlay (rich-click 1.9.4)
        arda-cli = python313Packages.callPackage ./arda-cli/default.nix { };
      };
    };
}
