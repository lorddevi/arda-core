{
  config,
  pkgs,
  lib,
  ...
}:
{
  name = "arda-cli-vm-help";

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

    # Test 1: Main arda --help command
    print("=== Testing: arda --help ===")
    result = machine.succeed("/tmp/arda-test/arda --help")
    assert "Arda - minimal infrastructure management" in result
    assert "config" in result
    assert "host" in result
    assert "roles" in result
    assert "secrets" in result
    assert "templates" in result
    assert "theme" in result
    print("✅ arda --help displays correctly")

    # Test 2: arda config --help
    print("\n=== Testing: arda config --help ===")
    result = machine.succeed("/tmp/arda-test/arda config --help")
    # More flexible assertions to handle rich formatting
    assert "config" in result.lower()
    assert "init" in result.lower()
    assert "set" in result.lower()
    assert "view" in result.lower()
    assert "--global" in result.lower() or "global" in result.lower()
    assert "--local" in result.lower() or "local" in result.lower()
    print("✅ arda config --help displays correctly")

    # Test 3: arda theme --help
    print("\n=== Testing: arda theme --help ===")
    result = machine.succeed("/tmp/arda-test/arda theme --help")
    assert "theme" in result.lower()
    assert "list" in result.lower()
    print("✅ arda theme --help displays correctly")

    # Test 4: arda host --help
    print("\n=== Testing: arda host --help ===")
    result = machine.succeed("/tmp/arda-test/arda host --help")
    assert "host" in result.lower()
    print("✅ arda host --help displays correctly")

    # Test 5: arda roles --help
    print("\n=== Testing: arda roles --help ===")
    result = machine.succeed("/tmp/arda-test/arda roles --help")
    assert "role" in result.lower()
    print("✅ arda roles --help displays correctly")

    # Test 6: arda secrets --help
    print("\n=== Testing: arda secrets --help ===")
    result = machine.succeed("/tmp/arda-test/arda secrets --help")
    assert "secret" in result.lower()
    print("✅ arda secrets --help displays correctly")

    # Test 7: arda templates --help
    print("\n=== Testing: arda templates --help ===")
    result = machine.succeed("/tmp/arda-test/arda templates --help")
    assert "template" in result.lower()
    print("✅ arda templates --help displays correctly")

    # Test 8: Verify Active configuration line appears
    print("\n=== Testing: Active configuration line ===")
    result = machine.succeed("/tmp/arda-test/arda --help")
    assert "Active configuration:" in result
    print("✅ Active configuration line appears in help")

    # Test 9: Help with theme option
    print("\n=== Testing: arda --help with theme option ===")
    result = machine.succeed("/tmp/arda-test/arda --theme dracula --help")
    assert "Arda - minimal infrastructure management" in result
    print("✅ arda --theme dracula --help works")

    # Test 10: Help with verbose option
    print("\n=== Testing: arda --help with verbose option ===")
    result = machine.succeed("/tmp/arda-test/arda --verbose --help")
    assert "Arda - minimal infrastructure management" in result
    print("✅ arda --verbose --help works")

    print("\n" + "="*60)
    print("✅ All help output tests PASSED")
    print("="*60)
  '';

  meta.maintainers = [ "Lord Devi" ];
}
