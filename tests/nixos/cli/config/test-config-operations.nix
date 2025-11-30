{
  config,
  pkgs,
  lib,
  ...
}:
{
  name = "arda-cli-vm-config-operations";

  nodes.machine =
    {
      config,
      pkgs,
      lib,
      ...
    }:
    {
      # arda-cli will be added by flake-module.nix via machine.systemPackages
      environment.systemPackages = [
      ];
    };

  testScript = ''
    # Start the VM
    machine.start()
    machine.wait_for_unit("default.target")

    # Debug: Check if arda binary exists and is executable
    print("=== Debug: Check arda binary ===")
    machine.succeed("ls -la /tmp/arda-test/arda")
    print("✅ arda binary exists and is executable")

    # Test 1: View default config (should work even with no config file)
    print("\n=== Testing: arda config view (no config file) ===")
    result = machine.succeed("/tmp/arda-test/arda config view")
    print(result)
    assert "Arda" in result or "theme" in result.lower() or "configuration" in result.lower()
    print("✅ arda config view works with no config file")

    # Test 2: Initialize a config file
    print("\n=== Testing: arda config init ===")
    print("Current directory:", machine.succeed("pwd"))
    # Use --force to avoid interactive prompt since config view already created a file
    machine.succeed("/tmp/arda-test/arda config --local init --force")
    print("Config init command completed")
    machine.succeed("ls -la etc/arda.toml 2>&1")
    print("✅ arda config init creates config file")

    # Test 3: Set theme in local config
    print("\n=== Testing: arda config set theme nord ===")
    machine.succeed("/tmp/arda-test/arda config --local set theme nord")
    result = machine.succeed("cat etc/arda.toml")
    assert "nord" in result
    print("✅ arda config set theme nord works")
    print(f"Config content:\n{result}")

    # Test 4: View config to see the set value
    print("\n=== Testing: arda config view (with config) ===")
    result = machine.succeed("/tmp/arda-test/arda config --local view")
    assert "nord" in result
    print("✅ arda config view shows updated theme")

    # Test 5: Set another config value
    print("\n=== Testing: arda config set output.verbose true ===")
    machine.succeed("/tmp/arda-test/arda config --local set output.verbose true")
    result = machine.succeed("cat etc/arda.toml")
    assert "verbose" in result
    assert "true" in result
    print("✅ arda config set output.verbose true works")

    # Test 6: Set timestamp config value
    print("\n=== Testing: arda config set output.timestamp false ===")
    machine.succeed("/tmp/arda-test/arda config --local set output.timestamp false")
    result = machine.succeed("cat etc/arda.toml")
    assert "timestamp" in result
    assert "false" in result
    print("✅ arda config set output.timestamp false works")

    # Test 7: Verify final config file content
    print("\n=== Testing: Full config file verification ===")
    result = machine.succeed("cat etc/arda.toml")
    assert "nord" in result
    assert "verbose" in result
    assert "timestamp" in result
    print("✅ Config file contains all set values")
    print(f"Final config:\n{result}")

    # Test 8: Test config command help
    print("\n=== Testing: arda config --help ===")
    result = machine.succeed("/tmp/arda-test/arda config --help")
    assert "init" in result
    assert "set" in result
    assert "view" in result
    assert "--local" in result
    assert "--global" in result
    print("✅ arda config --help shows all subcommands")

    print("\n" + "="*60)
    print("✅ All config operations tests PASSED")
    print("="*60)
  '';

  meta.maintainers = [ "Lord Devi" ];
}
