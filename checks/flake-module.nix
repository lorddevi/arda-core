{ pkgs, inputs, ... }:
{
  # NixOS VM tests for Arda
  # These tests run actual NixOS VMs to test system integration
  perSystem =
    { system, lib, ... }:
    let
      testers = pkgs.testers;
      # Import the module configuration and build it with runNixOSTest
      arda-cli-vm = testers.runNixOSTest (import ./arda-cli-vm);
    in
    {
      # VM test configurations
      checks = {
        inherit arda-cli-vm;
      };
    };
}
