{ pkgs, inputs, ... }:
{
  perSystem =
    { system, ... }:
    let
      python313Packages = pkgs.python313Packages;
    in
    {
      packages = {
        # Uses pkgs with our overlay (rich-click 1.9.4)
        # Also receives nix-select for advanced Nix attribute selection
        arda-cli = python313Packages.callPackage ./arda-cli/default.nix {
          inherit (inputs) nix-select;
        };
      };
    };
}
