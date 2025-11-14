{ ... }:
{
  perSystem =
    { pkgs, ... }:
    {
      packages = {
        arda-cli = pkgs.callPackage ./arda-cli/default.nix { };
      };
    };
}
