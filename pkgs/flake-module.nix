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
        # Explicitly pass python from overlaid packages to ensure rich-click 1.9.4 is used
        arda-cli = pythonPkgs.callPackage ./arda-cli/default.nix {
          python = pkgs.python313;
        };
      };
    };
}
