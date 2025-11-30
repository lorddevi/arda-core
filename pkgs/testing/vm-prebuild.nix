{
  pkgs,
  lib,
  system,
}:

let
  # Pre-build all VM test derivations
  prebuiltVMs = {
    help = pkgs.callPackage ../tests/nixos/cli/help/test-help-output.nix { };
    config-operations = pkgs.callPackage ../tests/nixos/cli/config/test-config-operations.nix { };
    config-priority = pkgs.callPackage ../tests/nixos/cli/config/test-config-priority.nix { };
    themes = pkgs.callPackage ../tests/nixos/cli/themes/test-theme-commands.nix { };
  };

  # Create closure info for fast copying
  vmClosureInfo = pkgs.closureInfo {
    rootPaths = lib.attrValues prebuiltVMs;
  };
in
{
  inherit prebuiltVMs;

  # Utility to include in test derivations
  withPrebuiltVMs =
    testDerivation:
    pkgs.runCommand "${testDerivation.name}-with-cache"
      {
        inherit (testDerivation) meta;
        nativeBuildInputs = [ pkgs.nix ];
      }
      ''
        # Copy pre-built VMs into test environment
        cp -r ${vmClosureInfo}/register-closure $out/
        ${pkgs.nix}/bin/nix-store --load-db < $out/register-closure

        # Run tests with pre-built VMs available
        ${testDerivation}/bin/test-script
        touch $out
      '';
}
