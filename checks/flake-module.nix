{ pkgs, inputs, ... }:
{
  # NixOS VM tests for Arda
  # These tests run actual NixOS VMs to test system integration and CLI functionality
  perSystem =
    { system, ... }:
    let
      inherit (pkgs) lib;
      testers = pkgs.testers;
      # Import the module configuration and build it with runNixOSTest
      arda-cli-vm = testers.runNixOSTest (import ./arda-cli-vm);

      # Get the arda-cli package
      arda-cli = pkgs.callPackage ../tests/nixos/arda-cli.nix { };

      # CLI VM Tests - Test arda CLI commands in isolated VMs
      # The test modules are functions that take config parameters
      test-help-module = import ../tests/nixos/cli/help/test-help-output.nix;
      test-help-config = test-help-module {
        config = { };
        inherit pkgs lib;
      };
      # Prepend arda to PATH in testScript
      test-help-config-with-cli = test-help-config // {
        testScript = ''
          ${testHelpScriptPreamble arda-cli}
          ${test-help-config.testScript}
        '';
      };
      arda-cli-vm-help = testers.runNixOSTest test-help-config-with-cli;

      test-config-operations-module = import ../tests/nixos/cli/config/test-config-operations.nix;
      test-config-operations-config = test-config-operations-module {
        config = { };
        inherit pkgs lib;
      };
      test-config-operations-config-with-cli = test-config-operations-config // {
        testScript = ''
          ${testHelpScriptPreamble arda-cli}
          ${test-config-operations-config.testScript}
        '';
      };
      arda-cli-vm-config-operations = testers.runNixOSTest test-config-operations-config-with-cli;

      test-config-priority-module = import ../tests/nixos/cli/config/test-config-priority.nix;
      test-config-priority-config = test-config-priority-module {
        config = { };
        inherit pkgs lib;
      };
      test-config-priority-config-with-cli = test-config-priority-config // {
        testScript = ''
          ${testHelpScriptPreamble arda-cli}
          ${test-config-priority-config.testScript}
        '';
      };
      arda-cli-vm-config-priority = testers.runNixOSTest test-config-priority-config-with-cli;

      test-theme-commands-module = import ../tests/nixos/cli/themes/test-theme-commands.nix;
      test-theme-commands-config = test-theme-commands-module {
        config = { };
        inherit pkgs lib;
      };
      test-theme-commands-config-with-cli = test-theme-commands-config // {
        testScript = ''
          ${testHelpScriptPreamble arda-cli}
          ${test-theme-commands-config.testScript}
        '';
      };
      arda-cli-vm-theme-commands = testers.runNixOSTest test-theme-commands-config-with-cli;

      testHelpScriptPreamble = arda-cli: ''
        # Make arda-cli available
        machine.succeed("mkdir -p /tmp/arda-test")
        machine.succeed("cp ${arda-cli}/bin/arda /tmp/arda-test/arda")
        machine.succeed("chmod +x /tmp/arda-test/arda")
      '';
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
