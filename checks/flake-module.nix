{ pkgs, inputs, ... }:
{
  # NixOS VM tests for Arda
  # These tests run actual NixOS VMs to test system integration and CLI functionality
  perSystem =
    { system, lib, ... }:
    let
      testers = pkgs.testers;
      # Import the module configuration and build it with runNixOSTest
      arda-cli-vm = testers.runNixOSTest (import ./arda-cli-vm);

      # CLI VM Tests - Test arda CLI commands in isolated VMs
      arda-cli-vm-help = testers.runNixOSTest (import ../tests/nixos/cli/help/test-help-output.nix);
      arda-cli-vm-config-operations = testers.runNixOSTest (
        import ../tests/nixos/cli/config/test-config-operations.nix
      );
      arda-cli-vm-config-priority = testers.runNixOSTest (
        import ../tests/nixos/cli/config/test-config-priority.nix
      );
      arda-cli-vm-theme-commands = testers.runNixOSTest (
        import ../tests/nixos/cli/themes/test-theme-commands.nix
      );
    in
    {
      # VM test configurations
      checks = {
        inherit
          arda-cli-vm
          arda-cli-vm-help
          arda-cli-vm-config-operations
          arda-cli-vm-config-priority
          arda-cli-vm-theme-commands
          ;
      };
    };
}
