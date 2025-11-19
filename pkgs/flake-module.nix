{ pkgs, ... }:
{
  perSystem =
    { system, ... }:
    let
      pythonPkgs = pkgs.python313Packages;
    in
    {
      packages = {
        # Uses pkgs with our overlay (rich-click 1.9.4)
        arda-cli = pythonPkgs.callPackage ./arda-cli/default.nix { };
      };
    };
}
